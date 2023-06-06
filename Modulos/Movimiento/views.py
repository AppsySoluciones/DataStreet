from Modulos.CentroCostos.models import CentroCosto,SubCentroCosto
from Modulos.Movimiento.models import Comentario, Movimiento,get_estado_caja, get_movimientos_usuario,get_estado_caja_admin,get_movimientos,export_to_excel,convert_xlsx_to_pdf
from Modulos.UnidadProductiva.models import UnidadProductiva
from django.contrib.auth.decorators import login_required
from Modulos.UnidadNegocio.models import UnidadNegocio
from django.shortcuts import get_object_or_404
from django.shortcuts import render,redirect
from botocore.exceptions import ClientError
from Modulos.Usuario.models import Usuario
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum
from django.conf import settings
from django.db.models import Q
from datetime import datetime
from Modulos.Movimiento.utils import render_to_pdf,area_chart_data,pie_chart_data,mayor_ingreso_uproductiva,mayor_egreso_uproductiva, centro_costos_uprod
import locale
import boto3
import json
from django.http import JsonResponse
from django.views.generic import View
from django.http import HttpResponse


URL_SERVER = settings.URL_SERVER
AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME



from django.contrib.auth.decorators import user_passes_test

def grupo_requerido(grupo_nombres):
    def chequear_grupo(usuario):
        return usuario.groups.filter(name__in=grupo_nombres).exists() and usuario.groups.all().count() == len(grupo_nombres)

    return user_passes_test(chequear_grupo)

# Create your views here.
@login_required(login_url=reverse_lazy('login'))
def home(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)


    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso,disponible_ba,ingreso_ba,egreso_ba = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    
    if usuario.groups.filter(name__in=['Auditor']).exists():
        filters = Q(tipo_ingreso='OUT')|(Q(ingreso_bancario=True) & (Q(tipo_ingreso='IN') | Q(tipo_ingreso='OUT')))
        movimientos = get_movimientos_usuario(usuario).filter(filters)

    else:
        movimientos = get_movimientos_usuario(usuario).filter(ingreso_bancario=False)


    context = {'server_url':URL_SERVER,
        'disponible':disponible,
        'egresos':egreso,
        'ingresos':ingreso,
        'request': request
        }
    
    context['disponible_ba'] = disponible_ba
    context['ingresos_ba'] = ingreso_ba
    context['egresos_ba'] = egreso_ba
        

    if usuario.groups.filter(name='Auditor').exists():
        movimientos = movimientos.filter(tipo_ingreso='OUT')

    unidades_productivas = UnidadProductiva.objects.filter(usuarioRegistro=usuario).all()

    context['fechas'],context['ingresos_chart'],context['egresos_chart'] = area_chart_data(movimientos)
    context['pie_ingresos'],context['pie_egresos'] = pie_chart_data(movimientos)
    context['top_3_ingresos'] = mayor_ingreso_uproductiva(movimientos)
    context['top_3_egresos'] = mayor_egreso_uproductiva(movimientos)
    context['pie_centrocostos'] = centro_costos_uprod(movimientos)

    context['unidades_productivas'] = unidades_productivas

    return render(request,"charts.html",context) 

def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]


#@login_required(login_url=reverse_lazy('login'))
#@grupo_requerido(['Administrador','Comun'])
def egresos(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    centro_costos = CentroCosto.objects.all().order_by('nombre')
    disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    
    data_centros = {
        }
    data_centros_id= {
    }
    for centro in centro_costos:
        data_centros[centro.nombre] = list(centro.subcentro.all().order_by('nombre').values_list('nombre',flat=True))
        data_centros_id[centro.pk] = list(centro.subcentro.all().order_by('nombre').values_list('id',flat=True))
    
    unidades_productivas = UnidadProductiva.objects.filter(usuarioRegistro=usuario).all()
    context = {
        'server_url':URL_SERVER,
        'centros':data_centros,
        'centros_id':data_centros_id,
        'disponible':disponible,
        'egresos':egreso,
        'ingresos':ingreso,
        'request': request,
        'unidades_productivas':unidades_productivas,
        }

    context['disponible_ba'] = disponible_ba
    context['ingresos_ba'] = ingreso_ba
    context['egresos_ba'] = egreso_ba
    
    return render(request,"egreso.html",context)

#@login_required(login_url='/login/')
#@grupo_requerido(['Administrador', 'Auditor'])
def ingresos(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    if usuario.groups.filter(name='Administrador').exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_movimientos(usuario)
    unidad_negocio = UnidadNegocio.objects.filter(admin=usuario).all()
    usuarios_comun =[]
    usuarios_comun_id =[]
    for unidad in unidad_negocio:
        for unidad_productiva in unidad.unidades_productivas.all():
            if unidad_productiva.usuarioRegistro != None:
                if unidad_productiva.usuarioRegistro.pk not in usuarios_comun_id:
                    usuarios_comun_id.append(unidad_productiva.usuarioRegistro.pk)
                    usuarios_comun.append(unidad_productiva.usuarioRegistro)

    context = {
        'server_url':URL_SERVER,
        'usuarios_comun':usuarios_comun,
        'disponible':disponible,
        'ingresos':ingreso, 
        'egresos':egreso,
        'request': request
        }
    context['disponible_ba'] = disponible_ba
    context['ingresos_ba'] = ingreso_ba
    context['egresos_ba'] = egreso_ba
    return render(request,"ingreso.html",context)


def ingresos_ba(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    if usuario.groups.filter(name='Administrador').exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_movimientos(usuario)
    
    if usuario.groups.filter(name__in=['Comun']).exists():
        unidades_productivas = UnidadProductiva.objects.filter(usuarioRegistro=usuario).all()
        unidad_negocio_nombres = []
        unidad_negocio_id = []
    else:
        unidad_negocio = UnidadNegocio.objects.filter(admin=usuario).all() 
        unidad_negocio_nombres = {
        }
        unidad_negocio_id= {
        }
        for unidad in unidad_negocio:
            unidad_negocio_nombres[unidad.nombre] = list(unidad.unidades_productivas.all().values_list('nombre',flat=True))
            unidad_negocio_id[unidad.nombre] = list(unidad.unidades_productivas.all().values_list('id',flat=True))
        unidades_productivas = []

    context = {
        'server_url':URL_SERVER,
        'centros':unidad_negocio_nombres,
        'centros_id':unidad_negocio_id,
        'disponible':disponible,
        'ingresos':ingreso,
        'egresos':egreso,
        'request': request,
        'unidades_productivas':unidades_productivas,
        }
    context['disponible_ba'] = disponible_ba
    context['ingresos_ba'] = ingreso_ba
    context['egresos_ba'] = egreso_ba
    
    return render(request,"ingresos_ba.html",context)

def egresos_ba(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    centro_costos = CentroCosto.objects.all().order_by('nombre')
    disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    if usuario.groups.filter(name='Administrador').exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_movimientos(usuario)
    data_centros = {
    }
    data_centros_id= {
    }
    for centro in centro_costos:
        data_centros[centro.nombre] = list(centro.subcentro.all().order_by('nombre').values_list('nombre',flat=True))
        data_centros_id[centro.pk] = list(centro.subcentro.all().order_by('nombre').values_list('id',flat=True))

    context = {'server_url':URL_SERVER,
        'centros':data_centros,
        'centros_id':data_centros_id,
        'disponible':disponible,
        'egresos':egreso,
        'ingresos':ingreso,
        'request': request
        }
    context['disponible_ba'] = disponible_ba
    context['ingresos_ba'] = ingreso_ba
    context['egresos_ba'] = egreso_ba
    return render(request,"egresos_ba.html",context)

#@login_required(login_url=reverse_lazy('/usuario/login/'))
#@grupo_requerido('Administrador')
def registrarIngreso(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first() 
        
    
    costo_valor = request.POST['costo_valor']
    concepto = request.POST['concepto']
    
    
        
    if request.POST['ingreso_bancario'] == 'False':
        ingreso_bancario = False
        accion = request.POST['accion']

        if request.POST['accion'] == 'Reducción de Caja':
        _,ingreso,_,_,_,_ = get_movimientos(usuario)
        ingreso = ingreso.strip("$")
        ingreso = ingreso.replace(",", "" )
        ingreso = float(ingreso.replace(",", "." ))
        if float(costo_valor) > ingreso:
            messages.error(request, f'¡La reducción de caja {concepto} no se registró correctamente! El valor supera el disponible en caja.')
            return redirect(f'{URL_SERVER}ingreso/')
        costo_valor = -1*float(costo_valor)
    else:
        ingreso_bancario = True

    
    

    if request.POST['ingreso_bancario'] == 'False':
        ingreso_bancario = False
    else:
        ingreso_bancario = True

    if ingreso_bancario == True:
        accion = request.POST['opciones']
        tipo_ventas = request.POST['selectVentas']
        if tipo_ventas != '':
            accion = request.POST['opciones']+" "+accion
        else:
            accion = request.POST['opciones']
        
        if usuario.groups.filter(name='Administrador').exists():
            unidad_productiva_id = request.POST['sub_centro_costo']
            unidad_productiva = UnidadProductiva.objects.filter(nombre=unidad_productiva_id).first()
        else:
            unidad_productiva_id = request.POST['unidad_productiva']
            unidad_productiva = get_object_or_404(UnidadProductiva, pk=unidad_productiva_id)  
        ingreso = Movimiento.objects.create(
            fecha_registro = datetime.now(),
            unidad_productiva=unidad_productiva,
            accion=accion,
            valor=costo_valor,
            concepto=concepto,
            estado='En Proceso',
            ingreso_bancario=ingreso_bancario,
            tipo_ingreso='IN',
        )
        ingreso.save()
        messages.success(request, f'¡El Ingreso Bancario {concepto} se registró correctamente!')
        return redirect(f'{URL_SERVER}ingreso_ba/')
    else:
        usuario_presupuesto = request.POST['usuario_comun']
        usuario_presupuesto = get_object_or_404(Usuario, pk=usuario_presupuesto)
        if request.POST['accion'] == 'Reducción de Caja':
            usuario_presupuesto.presupuesto = usuario_presupuesto.presupuesto - float(costo_valor)
        else:
            usuario_presupuesto.presupuesto = usuario_presupuesto.presupuesto + float(costo_valor)
        
        ingreso = Movimiento.objects.create(
            fecha_registro = datetime.now(),
            accion=accion,
            valor=costo_valor,
            concepto=concepto,
            estado='En Proceso',
            ingreso_bancario=ingreso_bancario,
            tipo_ingreso='IN',
            usuario_presupuesto=usuario_presupuesto,
            usuario_admin_ingreso = usuario

        )
        ingreso.save()
        usuario_comun = get_object_or_404(Usuario, pk=request.POST['usuario_comun'])
        if usuario_comun.groups.filter(name__in=['Comun']).exists():
            if accion == 'Reducción de Caja':
                usuario_comun.presupuesto = usuario_comun.presupuesto - float(costo_valor)
            else:
                usuario_comun.presupuesto = usuario_comun.presupuesto + float(costo_valor)
            usuario_comun.save() 
        
    messages.success(request, f'¡El Ingreso {concepto} se registró correctamente!')
    return redirect(f'{URL_SERVER}ingreso/')

#@grupo_requerido('Comun')
def registrarEgreso(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    centro_costo=request.POST['centro_costo']
    sub_centro_costo_id=request.POST['sub_centro_costo']
    nom_provedor = request.POST['nom_provedor']
    tipo_doc = request.POST['tipo_doc']
    num_doc = request.POST['num_doc']
    factura_check = request.POST['factura_check']
    concepto = request.POST['concepto']
    costo_valor = request.POST['costo_valor']
    
    if request.POST['ingreso_bancario'] == 'False':
        ingreso_bancario = False
    else:
        ingreso_bancario = True

    
    sub_centro_costo= SubCentroCosto.objects.filter(pk=sub_centro_costo_id).first()
    
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name='Administrador').exists():
        unidad_productiva = UnidadProductiva.objects.filter(nombre='Administración').first()
    else:
        unidad_productiva = request.POST['unidad_productiva']
        unidad_productiva = get_object_or_404(UnidadProductiva, pk=unidad_productiva)
    
    fecha_registro = datetime.now()

    if factura_check == 'true':
        num_factura = request.POST['num_factura']
        comprobante_factura = request.FILES['soporte']
        egreso = Movimiento.objects.create(
        sub_centro_costo=sub_centro_costo,
        fecha_registro=fecha_registro,
        nombre_proveedor=nom_provedor,
        tipo_documento=tipo_doc,
        numero_documento=num_doc,
        numero_factura=num_factura,
        concepto = concepto,
        estado='En proceso',
        tipo_ingreso='OUT',
        valor=costo_valor,
        unidad_productiva=unidad_productiva,
        comprobante_factura=comprobante_factura,
        ingreso_bancario=ingreso_bancario,
        )
        egreso.save()
    
    else:
        egreso = Movimiento.objects.create(
            sub_centro_costo=sub_centro_costo,
            fecha_registro=fecha_registro,
            nombre_proveedor=nom_provedor,
            tipo_documento=tipo_doc,
            numero_documento=num_doc,
            concepto = concepto,
            estado='En proceso',
            tipo_ingreso='OUT',
            valor=costo_valor,
            unidad_productiva=unidad_productiva,
            ingreso_bancario=ingreso_bancario,
        )
        egreso.save()

    messages.success(request, f'¡El Egreso {concepto} se registró correctamente!')
    return redirect(f'{URL_SERVER}egreso/')

def tablas_ingresos(request,pdf=None):
    try:
        
        usuario = get_object_or_404(Usuario, pk=request.user.id)
        

        
        if usuario.groups.filter(name__in=['Auditor']).exists():
            movimientos = get_movimientos_usuario(usuario)

        else:
            movimientos = get_movimientos_usuario(usuario)
        

        context = {'server_url':URL_SERVER,
            'data_movimientos':movimientos,
            'request': request
            }

        
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
        if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
            disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_movimientos(usuario)
        context['disponible_ba'] = disponible_ba
        context['ingresos_ba'] = ingreso_ba
        context['egresos_ba'] = egreso_ba
        context['ingresos'] = ingreso
        context['egresos'] = egreso
        context['disponible'] = disponible

        if usuario.groups.filter(name__in=['Administrador','Auditor','Comun']).exists():
            #diccionario[clave] = valor
            elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
            unique_elementos = set(elementos)
            context['unidades_productivas'] = unique_elementos

        # if usuario.groups.filter(name='Auditor').exists():
            
        #context['data_movimientos'] = movimientos.filter(tipo_ingreso='OUT')
        # for movimiento in movimientos:
        #     unidad_productiva = movimiento.unidad_productiva
        #     unidad_negocio = UnidadNegocio.objects.filter(unidades_productivas=unidad_productiva).first()
        #     movimiento.unidad_negocio = unidad_negocio.nombre

        return render(request,"tables_ingresos.html",context)

    except Exception as e:
        messages.error(request, f'¡Error! {e}')
        return redirect(f'{URL_SERVER}ingreso/')
def tablas_egresos(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name='Administrador').exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba =get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    movimientos = get_movimientos_usuario(usuario).filter(tipo_ingreso='OUT')
    context = {'server_url':URL_SERVER,
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    context['disponible_ba'] = disponible_ba
    context['ingresos_ba'] = ingreso_ba
    context['egresos_ba'] = egreso_ba
    return render(request,"tables_egresos.html",context)


def tablas_ingresos_ba(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    filtros = Q(ingreso_bancario=True)
    movimientos = get_movimientos_usuario(usuario).filter(filtros)
    

    context = {'server_url':URL_SERVER,
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    
    context['disponible_ba'] = disponible_ba
    context['ingresos_ba'] = ingreso_ba
    context['egresos_ba'] = egreso_ba
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        #diccionario[clave] = valor
        elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
        unique_elementos = set(elementos)
        context['unidades_productivas'] = unique_elementos

    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        context['data_movimientos'] = movimientos.filter(tipo_ingreso='IN')

    return render(request,"tables_ingresos_ba.html",context)

def tablas_egresos_ba(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    filtros = Q(ingreso_bancario=True)
    movimientos = get_movimientos_usuario(usuario).filter(filtros)
    

    context = {'server_url':URL_SERVER,
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        #diccionario[clave] = valor
        elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
        unique_elementos = set(elementos)
        context['unidades_productivas'] = unique_elementos
        context['disponible_ba'] = disponible_ba
        context['ingresos_ba'] = ingreso_ba
        context['egresos_ba'] = egreso_ba

    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        context['data_movimientos'] = movimientos.filter(tipo_ingreso='OUT')
    
    return render(request,"tables_egresos_ba.html",context)

def detalle(request,pk):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    movimientos = get_object_or_404(Movimiento,pk=pk)
    comentarios = Comentario.objects.filter(movimiento=movimientos)
    unidad_negocio = UnidadNegocio.objects.filter(unidades_productivas=movimientos.unidad_productiva).first()
    centro_costo = CentroCosto.objects.filter(subcentro=movimientos.sub_centro_costo).first()
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    valor_f = locale.currency(movimientos.valor, symbol=True, grouping=True)
    context = {'server_url':URL_SERVER,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request,
        'movimiento':movimientos,
        'estado':'En proceso',
        'unidad_negocio':unidad_negocio,
        'centro_costo':centro_costo,
        'valor_f':valor_f,
        'id_url_detalle':pk,
        'comentarios':comentarios,

        }
    context['disponible_ba'] = disponible_ba
    context['ingresos_ba'] = ingreso_ba
    context['egresos_ba'] = egreso_ba
    return render(request,"detalle_mov.html",context)

def edicion_mov(request,pk):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    movimientos = get_object_or_404(Movimiento,pk=pk)
    unidad_negocio = UnidadNegocio.objects.filter(unidades_productivas=movimientos.unidad_productiva).first()
    centro_costo = CentroCosto.objects.filter(subcentro=movimientos.sub_centro_costo).first()

    centro_costos = CentroCosto.objects.all()
    data_centros = {
    }
    data_centros_id= {
    }
    for centro in centro_costos:
        data_centros[centro.nombre] = list(centro.subcentro.all().values_list('nombre',flat=True))
        data_centros_id[centro.pk] = list(centro.subcentro.all().values_list('id',flat=True))
    
    context = {'server_url':URL_SERVER,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request,
        'movimiento':movimientos,
        'centros':data_centros,
        'centros_id':data_centros_id,
        'estado':'En proceso',
        'unidad_negocio':unidad_negocio,
        'centro_costo':centro_costo

        }
    return render(request,"editar_mov.html",context)


def agregar_comentario(request,pk):
    comentario = request.POST['comentario']
    movimiento = get_object_or_404(Movimiento,pk=pk)
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    comentario = Comentario.objects.create(
        movimiento=movimiento,
        usuario=usuario,
        comentario=comentario
        )
    comentario.save()
    messages.success(request, f'¡Comentario Agregado Correctamente!')
    return redirect(f'{URL_SERVER}movimiento/detalle/'+str(pk)+'/') 

def edicion_form(request,pk):
    movimiento = get_object_or_404(Movimiento,pk=pk)
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    centro_costo=request.POST['centro_costo']
    sub_centro_costo_id=request.POST['sub_centro_costo']
    nom_provedor = request.POST['nom_provedor']
    tipo_doc = request.POST['tipo_doc']
    num_doc = request.POST['num_doc']
    factura_check = request.POST['factura_check']
    concepto = request.POST['concepto']
    
    costo_valor =request.POST['costo_valor']
    costo_valor = float(costo_valor.replace(",", "." ))
    
    sub_centro_costo= SubCentroCosto.objects.filter(pk=sub_centro_costo_id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    fecha_registro = datetime.now()

    if factura_check == 'true':
        num_factura = request.POST['num_factura']
        comprobante_factura = request.FILES['soporte']
        egreso = Movimiento.objects.filter(pk=pk).update(
        sub_centro_costo=sub_centro_costo,
        fecha_registro=fecha_registro,
        nombre_proveedor=nom_provedor,
        tipo_documento=tipo_doc,
        numero_documento=num_doc,
        numero_factura=num_factura,
        concepto = concepto,
        estado='En proceso',
        tipo_ingreso='OUT',
        valor=costo_valor,
        unidad_productiva=unidad_productiva,
        comprobante_factura=comprobante_factura
        )
    
    else:
        egreso = Movimiento.objects.filter(pk=pk).update(
            fecha_registro=fecha_registro,
            nombre_proveedor=nom_provedor,
            tipo_documento=tipo_doc,
            numero_documento=num_doc,
            concepto = concepto,
            estado='En proceso',
            tipo_ingreso='OUT',
            valor=costo_valor,
            unidad_productiva=unidad_productiva,
        )
    return redirect(f'{URL_SERVER}movimiento/editar/{movimiento.pk}/')

def select_unidad_prod(request):
    usuario = get_object_or_404(Usuario,pk=request.user.id)
    if request.POST['unidad_productiva'] == 'None':
        usuario.last_productiva = None
    else:
        usuario.last_productiva = request.POST['unidad_productiva']
    usuario.save()
    return redirect(f'{URL_SERVER}')

def comprobante(request,pk):
    movimiento = get_object_or_404(Movimiento,pk=pk)
    s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': AWS_STORAGE_BUCKET_NAME,
                'Key': movimiento.comprobante_factura.name
            },
            ExpiresIn=360
        )
        return redirect(f'{response}')
    except ClientError as e:
        # Manejar cualquier error de generación de URL firmada

        return redirect('/')

def aprobar_mov(request,pk):
    movimiento = get_object_or_404(Movimiento,pk=pk)
    movimiento.estado = 'Aprobado'
    movimiento.save()
    
    unidad_prod = movimiento.unidad_productiva
    if unidad_prod.usuarioRegistro is not None:
        usuario = unidad_prod.usuarioRegistro
        if movimiento.tipo_ingreso == 'IN':
            usuario.send_email('Ingreso Aprobado ',f'¡El Ingreso {movimiento.concepto} fué marcado como APROBADO!')
            messages.success(request, f'¡El Ingreso {movimiento.concepto} fué marcado como APROBADO!')
        elif movimiento.tipo_ingreso == 'OUT':
            usuario.send_email('Egreso Rechazado',f'¡El Egreso {movimiento.concepto} fué marcado como APROBADO!')
            messages.success(request, f'¡El Egreso {movimiento.concepto} fué marcado como APROBADO!')
    
    return redirect(f'{URL_SERVER}tablaing/')
def rechazar_mov(request,pk):
    movimiento = get_object_or_404(Movimiento,pk=pk)
    movimiento.estado = 'Rechazado'
    movimiento.save()
    messages.success(request, f'¡El Movimiento {movimiento.concepto} fué marcado como RECHAZADO!')
    unidad_prod = movimiento.unidad_productiva
    if unidad_prod.usuarioRegistro is not None:
        usuario = unidad_prod.usuarioRegistro.first()
        if movimiento.tipo_ingreso == 'IN':
            usuario.send_email('Ingreso Rechazado ',f'¡El Ingreso {movimiento.concepto} fué marcado como RECHAZADO!')
            messages.success(request, f'¡El Ingreso {movimiento.concepto} fué marcado como RECHAZADO!')
        elif movimiento.tipo_ingreso == 'OUT':
            usuario.send_email('Egreso Rechazado',f'¡El Egreso {movimiento.concepto} fué marcado como RECHAZADO!')
            messages.success(request, f'¡El Egreso {movimiento.concepto} fué marcado como RECHAZADO!')
    return redirect(f'{URL_SERVER}tablaing/')

def generar_excel_ingresos(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba  = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    
    if usuario.groups.filter(name__in=['Auditor']).exists():
        movimientos = get_movimientos_usuario(usuario)

    else:
        movimientos = get_movimientos_usuario(usuario).filter(ingreso_bancario=False)
    

    context = {'server_url':URL_SERVER,
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        #diccionario[clave] = valor
        elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
        unique_elementos = set(elementos)
        context['unidades_productivas'] = unique_elementos

    # if usuario.groups.filter(name='Auditor').exists():
        
    #     context['data_movimientos'] = movimientos.filter(tipo_ingreso='OUT')
    for movimiento in movimientos:
        unidad_productiva = movimiento.unidad_productiva
        unidad_negocio = UnidadNegocio.objects.filter(unidades_productivas=unidad_productiva).first()
        if unidad_negocio != None:
            movimiento.unidad_negocio = unidad_negocio.nombre
        else:
            movimiento.unidad_negocio = 'N/A'
        
    excel_generado = export_to_excel(movimientos)
    messages.success(request, f'¡El excel se generó corretamente!')

    return excel_generado 



def generar_excel_egresos(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba  = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    filtros = Q(ingreso_bancario=True)
    movimientos = get_movimientos_usuario(usuario).filter(filtros)
    

    context = {'server_url':URL_SERVER,
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        #diccionario[clave] = valor
        elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
        unique_elementos = set(elementos)
        context['unidades_productivas'] = unique_elementos

    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        context['data_movimientos'] = movimientos.filter(tipo_ingreso='OUT')
        
    excel_generado = export_to_excel(movimientos)
    messages.success(request, f'¡El excel se generó corretamente!')

    return excel_generado 


def generar_excel_ingresos_ba(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba  = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
    filtros = Q(ingreso_bancario=True)
    movimientos = get_movimientos_usuario(usuario).filter(filtros)
    

    context = {'server_url':URL_SERVER,
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        #diccionario[clave] = valor
        elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
        unique_elementos = set(elementos)
        context['unidades_productivas'] = unique_elementos 

    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        context['data_movimientos'] = movimientos.filter(tipo_ingreso='IN')
        
    excel_generado = export_to_excel(movimientos)
    messages.success(request, f'¡El excel se generó corretamente!')

    return excel_generado 

def select_u_productiva(request):
    try:
        usuario = get_object_or_404(Usuario, pk=request.user.id)
        unidad_prod = get_object_or_404(UnidadProductiva, pk=request.POST['uprodselectid'])
        if UnidadProductiva.objects.filter(usuarioRegistro=usuario).exists():
            usuario.last_productiva = unidad_prod.pk
        else:
            usuario.last_productiva = None
        
        messages.success(request, f'¡Seleccionaste la unidad productiva {unidad_prod.nombre}!')
        return redirect('/')
    except:
        messages.success(request, f'¡Upss hubo un error!')
        return redirect('/')


class Pdf_ingresos (View):
    def get(self, request, *args, **kwargs):
        try:
            usuario = get_object_or_404(Usuario, pk=request.user.id)
            if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
                disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba  = get_movimientos(usuario)
            else:
                unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
                disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
            
            if usuario.groups.filter(name__in=['Auditor']).exists():
                filters = Q(tipo_ingreso='OUT')|(Q(ingreso_bancario=True) & (Q(tipo_ingreso='IN') | Q(tipo_ingreso='OUT')))
                movimientos = get_movimientos_usuario(usuario).filter(filters)

            else:
                movimientos = get_movimientos_usuario(usuario).filter(ingreso_bancario=False)
            

            context = {'server_url':URL_SERVER,
                'data_movimientos':movimientos,
                'ingresos':ingreso,
                'egresos':egreso,
                'disponible':disponible,
                'request': request
                }
            if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
                #diccionario[clave] = valor
                elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
                unique_elementos = set(elementos)
                context['unidades_productivas'] = unique_elementos

            if usuario.groups.filter(name='Auditor').exists():
                
                context['data_movimientos'] = movimientos.filter(tipo_ingreso='OUT')
            excel_generado = render_to_pdf('pdf/pdf_tables_ingresos.html', context)
            messages.success(request, f'¡El pdf se generó corretamente!')
            return excel_generado
            #return render(request,"pdf/pdf_tables_ingresos.html",context)
        except Exception as e:
            messages.error(request, f'¡Error al generar el pdf!')

            return redirect(f'{URL_SERVER}tablaing/')
        
class Pdf_ingresos_ba (View):
    def get(self, request, *args, **kwargs):
        try:
            usuario = get_object_or_404(Usuario, pk=request.user.id)
            if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
                disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba  = get_movimientos(usuario)
            else:
                unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
                disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
            filtros = Q(ingreso_bancario=True)
            movimientos = get_movimientos_usuario(usuario).filter(filtros)
            

            context = {'server_url':URL_SERVER,
                'data_movimientos':movimientos,
                'ingresos':ingreso,
                'egresos':egreso,
                'disponible':disponible,
                'request': request
                }
            if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
                #diccionario[clave] = valor
                elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
                unique_elementos = set(elementos)
                context['unidades_productivas'] = unique_elementos

            if usuario.groups.filter(name='Auditor').exists():
                context['data_movimientos'] = movimientos.filter(tipo_ingreso='OUT')
            excel_generado = render_to_pdf('pdf/pdf_tables_ingresos_ba.html', context)
            messages.success(request, f'¡El pdf se generó corretamente!')
            return excel_generado

        except Exception as e:
            messages.error(request, f'¡Error al generar el pdf!')

            return redirect(f'{URL_SERVER}tablaingba/')

class Pdf_egresos_ba (View):
    def get(self, request, *args, **kwargs):
        try:
            usuario = get_object_or_404(Usuario, pk=request.user.id)
            if usuario.groups.filter(name='Administrador').exists():
                disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba  = get_movimientos(usuario)
            else:
                unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
                disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
            filtros = Q(ingreso_bancario=True) & Q(tipo_ingreso='OUT')
            movimientos = get_movimientos_usuario(usuario).filter(filtros).order_by('fecha_registro')
            context = {'server_url':URL_SERVER,
                'data_movimientos':movimientos,
                'ingresos':ingreso,
                'egresos':egreso,
                'disponible':disponible,
                'request': request
                }
            excel_generado = render_to_pdf('pdf/pdf_tables_egresos_ba.html', context)
            messages.success(request, f'¡El pdf se generó corretamente!')
            return excel_generado
        except Exception as e:
            messages.error(request, f'¡Error al generar el pdf!')

            return redirect(f'{URL_SERVER}tablaegreba/')

def dispo_caja_egresos(request):
    id = request.GET['opcion']
    unidad_prod = get_object_or_404(UnidadProductiva, pk=id)
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    egresos_caja = Movimiento.objects.filter(Q(ingreso_bancario=False) & Q(tipo_ingreso='OUT') & Q(unidad_productiva=unidad_prod)).all().aggregate(Sum('valor'))    
    egresos_bancarios = Movimiento.objects.filter(Q(ingreso_bancario=True) & Q(tipo_ingreso='OUT') & Q(unidad_productiva=unidad_prod)).all().aggregate(Sum('valor'))
    ingresos_bancarios = Movimiento.objects.filter(Q(ingreso_bancario=True) & Q(tipo_ingreso='IN') & Q(unidad_productiva=unidad_prod)).all().aggregate(Sum('valor'))
    if ingresos_bancarios['valor__sum'] == None:
        ingresos_bancarios = 0
    else:
        ingresos_bancarios = ingresos_bancarios['valor__sum']

    if egresos_bancarios['valor__sum'] == None:
        egresos_bancarios = 0
    else:
        egresos_bancarios = egresos_bancarios['valor__sum']

    if egresos_caja['valor__sum'] == None:
        egresos_caja = 0
    saldo_bancario = ingresos_bancarios - egresos_bancarios
    data = {
        'Egresos_caja':locale.currency(egresos_caja['valor__sum'], symbol=True, grouping=True),
        'Disponible_caja': '-',
        'Ingresos_caja': '-',
        'Egresos_bancarios':locale.currency(egresos_bancarios, symbol=True, grouping=True),
        'Ingresos_bancarios':locale.currency(ingresos_bancarios, symbol=True, grouping=True),
        'Saldo_bancario':locale.currency(saldo_bancario, symbol=True, grouping=True),
        }
    return JsonResponse(data)

def ventas(request): 
    unidad_prod = request.GET['opcion']
    
    if unidad_prod == 'AGRICULTURA':
        opciones_ventas = [
            {'value': 'Agucate', 'label': 'Agucate'},
            {'value': 'Limon', 'label': 'Limon'},
            {'value': 'Platano', 'label': 'Platano'},
            {'value': 'Naranja', 'label': 'Naranja'},
            {'value': 'Sili', 'label': 'Sili'},
            {'value': 'Café', 'label': 'Café'},
            {'value': 'Heno', 'label': 'Heno'},
        ]
    elif unidad_prod == 'GANADERIA':
        opciones_ventas = [
            {'value': 'Ganado', 'label': 'Ganado'},
            {'value': 'Leche', 'label': 'Leche'},
            {'value': 'Embriones', 'label': 'Embriones'},
            {'value': 'Terneros', 'label': 'Terneros'},
            {'value': 'Aspiraciones', 'label': 'Aspiraciones'},
        ]
    else:
        opciones_ventas = [
            {'value': '', 'label': ''}]

    return JsonResponse(opciones_ventas, safe=False)    
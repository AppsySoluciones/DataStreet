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
from django.views.generic import View


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
    disponible,ingreso,egreso = get_movimientos(usuario)

    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    
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
    

    if usuario.groups.filter(name='Auditor').exists():
        movimientos = movimientos.filter(tipo_ingreso='OUT')

    context['fechas'],context['ingresos_chart'],context['egresos_chart'] = area_chart_data(movimientos)
    context['pie_ingresos'],context['pie_egresos'] = pie_chart_data(movimientos)
    context['top_3_ingresos'] = mayor_ingreso_uproductiva(movimientos)
    context['top_3_egresos'] = mayor_egreso_uproductiva(movimientos)
    context['pie_centrocostos'] = centro_costos_uprod(movimientos)

    return render(request,"charts.html",context) 

def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]


#@login_required(login_url=reverse_lazy('login'))
#@grupo_requerido(['Administrador','Comun'])
def egresos(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    centro_costos = CentroCosto.objects.all()
    disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    data_centros = {
    }
    data_centros_id= {
    }
    for centro in centro_costos:
        data_centros[centro.nombre] = list(centro.subcentro.all().values_list('nombre',flat=True))
        data_centros_id[centro.pk] = list(centro.subcentro.all().values_list('id',flat=True))
    print(data_centros)
    print(data_centros_id)
    context = {
        'server_url':URL_SERVER,
        'centros':data_centros,
        'centros_id':data_centros_id,
        'disponible':disponible,
        'egresos':egreso,
        'ingresos':ingreso,
        'request': request
        }
    
    return render(request,"egreso.html",context)

#@login_required(login_url='/login/')
#@grupo_requerido(['Administrador', 'Auditor'])
def ingresos(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    disponible,ingreso,egreso = get_movimientos(usuario)
    unidad_negocio = UnidadNegocio.objects.filter(admin=usuario).all()
    unidad_negocio_nombres = {
    }
    unidad_negocio_id= {
    }
    for unidad in unidad_negocio:
        unidad_negocio_nombres[unidad.nombre] = list(unidad.unidades_productivas.all().values_list('nombre',flat=True))
        unidad_negocio_id[unidad.nombre] = list(unidad.unidades_productivas.all().values_list('id',flat=True))
    print(unidad_negocio_nombres)
    print(unidad_negocio_id)
    context = {
        'server_url':URL_SERVER,
        'centros':unidad_negocio_nombres,
        'centros_id':unidad_negocio_id,
        'disponible':disponible,
        'ingresos':ingreso,
        'egresos':egreso,
        'request': request
        }
    
    return render(request,"ingreso.html",context)


def ingresos_ba(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    disponible,ingreso,egreso = get_movimientos(usuario)
    unidad_negocio = UnidadNegocio.objects.filter(admin=usuario).all()
    unidad_negocio_nombres = {
    }
    unidad_negocio_id= {
    }
    for unidad in unidad_negocio:
        unidad_negocio_nombres[unidad.nombre] = list(unidad.unidades_productivas.all().values_list('nombre',flat=True))
        unidad_negocio_id[unidad.nombre] = list(unidad.unidades_productivas.all().values_list('id',flat=True))
    print(unidad_negocio_nombres)
    print(unidad_negocio_id)
    context = {
        'server_url':URL_SERVER,
        'centros':unidad_negocio_nombres,
        'centros_id':unidad_negocio_id,
        'disponible':disponible,
        'ingresos':ingreso,
        'egresos':egreso,
        'request': request
        }
    
    return render(request,"ingresos_ba.html",context)

def egresos_ba(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    centro_costos = CentroCosto.objects.all()
    disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    data_centros = {
    }
    data_centros_id= {
    }
    for centro in centro_costos:
        data_centros[centro.nombre] = list(centro.subcentro.all().values_list('nombre',flat=True))
        data_centros_id[centro.pk] = list(centro.subcentro.all().values_list('id',flat=True))
    print(data_centros)
    print(data_centros_id)
    context = {'server_url':URL_SERVER,
        'centros':data_centros,
        'centros_id':data_centros_id,
        'disponible':disponible,
        'egresos':egreso,
        'ingresos':ingreso,
        'request': request
        }
    return render(request,"egresos_ba.html",context)

#@login_required(login_url=reverse_lazy('/usuario/login/'))
#@grupo_requerido('Administrador')
def registrarIngreso(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidadm=request.POST['centro_costo']
    unidad_productiva_id=request.POST['sub_centro_costo']
    
    accion = request.POST['accion']
    costo_valor = request.POST['costo_valor']
    concepto = request.POST['concepto']
    unidadm = UnidadNegocio.objects.filter(nombre=unidadm).first()
    unidad_productiva = get_object_or_404(UnidadProductiva, nombre=unidad_productiva_id)
        
    if request.POST['ingreso_bancario'] == 'False':
        ingreso_bancario = False
    else:
        ingreso_bancario = True

    if request.POST['accion'] == 'Reducción de Caja':
        _,ingreso,_ = get_movimientos(usuario)
        ingreso = ingreso.strip("$")
        ingreso = ingreso.replace(",", "" )
        ingreso = float(ingreso.replace(",", "." ))
        if float(costo_valor) > ingreso:
            messages.error(request, f'¡La reducción de caja {concepto} no se registró correctamente! El valor supera el disponible en caja.')
            return redirect(f'{URL_SERVER}ingreso/')
        costo_valor = -1*float(costo_valor)
        
    ingreso = Movimiento.objects.create(
        fecha_registro = datetime.now(),
        unidad_productiva=unidad_productiva,
        accion=accion,
        valor=costo_valor,
        concepto=concepto,
        estado='Aprobado',
        ingreso_bancario=ingreso_bancario,
        tipo_ingreso='IN',
    )
    ingreso.save()
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
    
    sub_centro_costo= SubCentroCosto.objects.filter(pk=sub_centro_costo_id).first()
    
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name='Administrador').exists():
        unidad_productiva = UnidadProductiva.objects.filter(nombre='Administración').first()
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()

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
        comprobante_factura=comprobante_factura
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
        )
        egreso.save()

    messages.success(request, f'¡El Egreso {concepto} se registró correctamente!')
    return redirect(f'{URL_SERVER}egreso/')

def tablas_ingresos(request,pdf=None):
    try:
        usuario = get_object_or_404(Usuario, pk=request.user.id)
        if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
            disponible,ingreso,egreso = get_movimientos(usuario)
        else:
            unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
            disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
        
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

        return render(request,"tables_ingresos.html",context)

    except Exception as e:
        messages.error(request, f'¡Error! {e}')
        return redirect(f'{URL_SERVER}ingreso/')
def tablas_egresos(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name='Administrador').exists():
        disponible,ingreso,egreso = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    movimientos = get_movimientos_usuario(usuario).filter(tipo_ingreso='OUT')
    context = {'server_url':URL_SERVER,
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    return render(request,"tables_egresos.html",context)


def tablas_ingresos_ba(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
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

    return render(request,"tables_ingresos_ba.html",context)

def tablas_egresos_ba(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
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
    
    return render(request,"tables_egresos_ba.html",context)

def detalle(request,pk):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso = get_movimientos(usuario)
    else:
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
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
    return render(request,"detalle_mov.html",context)

def edicion_mov(request,pk):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
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
        print(e)
        return redirect('/')

def aprobar_mov(request,pk):
    movimiento = get_object_or_404(Movimiento,pk=pk)
    movimiento.estado = 'Aprobado'
    movimiento.save()
    messages.success(request, f'¡El Movimiento {movimiento.concepto} fué marcado como APROBADO!')
    unidad_prod = movimiento.unidad_productiva
    if unidad_prod.usuarioRegistro is not None:
        usuario = unidad_prod.usuarioRegistro.first()
        usuario.send_email('Movimiento Rechazado',f'¡El Movimiento {movimiento.concepto} fué marcado como APROBADO!')
    return redirect(f'{URL_SERVER}tablaing/')
def rechazar_mov(request,pk):
    movimiento = get_object_or_404(Movimiento,pk=pk)
    movimiento.estado = 'Rechazado'
    movimiento.save()
    messages.success(request, f'¡El Movimiento {movimiento.concepto} fué marcado como RECHAZADO!')
    unidad_prod = movimiento.unidad_productiva
    if unidad_prod.usuarioRegistro is not None:
        usuario = unidad_prod.usuarioRegistro.first()
        usuario.send_email('Movimiento Rechazado', f'¡El Movimiento {movimiento.concepto} fué marcado como RECHAZADO!')
    return redirect(f'{URL_SERVER}tablaing/')

def generar_excel_ingresos(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    movimientos = get_movimientos_usuario(usuario).filter(ingreso_bancario=False)
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        #diccionario[clave] = valor
        if usuario.groups.filter(name='Auditor').exists():
            movimientos = movimientos.filter(tipo_ingreso='OUT')
        elementos = movimientos.values_list('unidad_productiva__nombre', flat=True).distinct()
        unique_elementos = set(elementos)
        movimientos = unique_elementos
        
    excel_generado = export_to_excel(movimientos)
    messages.success(request, f'¡El excel se generó corretamente!')

    return excel_generado 
    


class Pdf_ingresos (View):
    def get(self, request, *args, **kwargs):
        try:
            usuario = get_object_or_404(Usuario, pk=request.user.id)
            if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
                disponible,ingreso,egreso = get_movimientos(usuario)
            else:
                unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
                disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
            
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
            print(e)
            return redirect(f'{URL_SERVER}tablaing/')
        
class Pdf_ingresos_ba (View):
    def get(self, request, *args, **kwargs):
        try:
            usuario = get_object_or_404(Usuario, pk=request.user.id)
            if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
                disponible,ingreso,egreso = get_movimientos(usuario)
            else:
                unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
                disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
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
            print(e)
            return redirect(f'{URL_SERVER}tablaingba/')

class Pdf_egresos_ba (View):
    def get(self, request, *args, **kwargs):
        try:
            usuario = get_object_or_404(Usuario, pk=request.user.id)
            if usuario.groups.filter(name='Administrador').exists():
                disponible,ingreso,egreso = get_movimientos(usuario)
            else:
                unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
                disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
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
            print(e)
            return redirect(f'{URL_SERVER}tablaegreba/')
from Modulos.CentroCostos.models import CentroCosto,SubCentroCosto
from Modulos.Movimiento.models import Comentario, Movimiento,get_estado_caja, get_movimientos_usuario,get_estado_caja_admin,get_movimientos
from Modulos.UnidadProductiva.models import UnidadProductiva
from django.contrib.auth.decorators import login_required
from Modulos.UnidadNegocio.models import UnidadNegocio
from django.shortcuts import render,redirect
from Modulos.Usuario.models import Usuario
from django.urls import reverse_lazy
from django.db.models import Sum
from django.shortcuts import get_object_or_404

import locale

import json



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
    context = {
        'disponible':disponible,
        'egresos':egreso,
        'ingresos':ingreso,
        'request': request
        }
    if usuario.groups.filter(name='Administrador').exists():
        unidades_productivas_admin = UnidadProductiva.objects.filter(usuarioRegistro=usuario).all()
        context['unidades_productivas_admin'] = unidades_productivas_admin
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
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    disponible,ingreso,egreso = get_movimientos(usuario)
    unidad_negocio = UnidadNegocio.objects.all()
    unidad_negocio_nombres = {
    }
    unidad_negocio_id= {
    }
    for unidad in unidad_negocio:
        unidad_negocio_nombres[unidad.nombre] = list(unidad.unidades_productivas.all().values_list('nombre',flat=True))
        unidad_negocio_id[unidad.pk] = list(unidad.unidades_productivas.all().values_list('id',flat=True))
    return render(request,"ingreso.html",{'centros':unidad_negocio_nombres,'centros_id':unidad_negocio_id,'disponible':disponible,'ingresos':ingreso,'egresos':egreso,'request': request})


def ingresos_ba(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    centro_costos = CentroCosto.objects.all()
    data_centros = {}
    for centro in centro_costos:
        data_centros[centro.nombre] = list(centro.subcentro.all().values_list('nombre',flat=True))
    return render(request,"ingresos_ba.html",{'centros':data_centros,'ingresos':ingreso,'disponible':disponible,'egresos':egreso,'request': request})

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
    context = {
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
    unidadm=request.POST['unidad_negocio']
    unidad_productiva_id=request.POST['unidad_productiva']
    fecha_registro = request.POST['fecha_registro']
    accion = request.POST['accion']
    costo_valor = request.POST['costo_valor']
    concepto = request.POST['concepto']
    unidadm = UnidadNegocio.objects.filter(nombre=unidadm).first()
    unidad_negocio = UnidadNegocio.objects.filter(pk=unidad_productiva_id).first()
    unidad_productiva = UnidadProductiva.objects.first()
    
    ingreso = Movimiento.objects.create(
        unidad_productiva=unidad_productiva,
        fecha_registro=fecha_registro,
        accion=accion,
        valor=costo_valor,
        concepto=concepto,
        estado='En proceso',
        tipo_ingreso='IN'
    )
    ingreso.save()
    return redirect('/')

#@grupo_requerido('Comun')
def registrarEgreso(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    centro_costo=request.POST['centro_costo']
    sub_centro_costo_id=request.POST['sub_centro_costo']
    fecha_registro = request.POST['fecha_registro']
    nom_provedor = request.POST['nom_provedor']
    tipo_doc = request.POST['tipo_doc']
    num_doc = request.POST['num_doc']
    factura_check = request.POST['factura_check']
    concepto = request.POST['concepto']
    costo_valor = request.POST['costo_valor']
    
    sub_centro_costo= SubCentroCosto.objects.filter(pk=sub_centro_costo_id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()

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
        
    )
    else:
        egreso = Movimiento.objects.create(
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
    return redirect('/')



def tablas_ingresos(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    movimientos = get_movimientos_usuario(usuario).filter(tipo_ingreso='IN')
    context = {
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    return render(request,"tables_ingresos.html",context)

def tablas_egresos(request):
    usuario = Usuario.objects.filter(pk=request.user.id).first()
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    movimientos = get_movimientos_usuario(usuario).filter(tipo_ingreso='OUT')
    context = {
        'data_movimientos':movimientos,
        'ingresos':ingreso,
        'egresos':egreso,
        'disponible':disponible,
        'request': request
        }
    return render(request,"tables_egresos.html",context)


def detalle(request,pk):
    usuario = get_object_or_404(Usuario,pk=request.user.id)
    unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
    disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    movimientos = get_object_or_404(Movimiento,pk=pk)
    comentarios = Comentario.objects.filter(movimiento=movimientos)
    unidad_negocio = UnidadNegocio.objects.filter(unidades_productivas=movimientos.unidad_productiva).first()
    centro_costo = CentroCosto.objects.filter(subcentro=movimientos.sub_centro_costo).first()
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    valor_f = locale.currency(movimientos.valor, symbol=True, grouping=True)
    context = {
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
    
    context = {
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
    return redirect('http://127.0.0.1:8000/movimiento/detalle/'+str(pk)+'/') 

def edicion_form(request):
    return None

def select_unidad_prod(request):
    usuario = get_object_or_404(Usuario,pk=request.user.id)
    if request.POST['unidad_productiva'] == 'None':
        usuario.last_productiva = None
    else:
        usuario.last_productiva = request.POST['unidad_productiva']
    usuario.save()
    return redirect('http://127.0.0.1:8000/')
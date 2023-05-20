from Modulos.UnidadProductiva.models import UnidadProductiva
from Modulos.UnidadNegocio.models import UnidadNegocio
from Modulos.CentroCostos.models import SubCentroCosto
from Modulos.Usuario.models import Usuario
from django.db.models import Sum
from django.db.models import Q
from django.db import models
import locale
import uuid
# Create your models here.

class TipoMovimiento(models.TextChoices):
    INGRESO = 'IN', 'Ingreso-s'
    EGRESO = 'OUT', 'Egreso-s'

class Movimiento(models.Model):
    unidad_productiva = models.ForeignKey(UnidadProductiva, on_delete=models.CASCADE,null=True,blank=True)
    numero_documento = models.CharField(max_length=50,null=True,blank=True)
    nombre_proveedor = models.CharField(max_length=50,null=True,blank=True)
    sub_centro_costo = models.ForeignKey(SubCentroCosto, on_delete=models.CASCADE,null=True,blank=True)
    numero_factura = models.CharField(max_length=50,null=True,blank=True)
    tipo_documento = models.CharField(max_length=50,null=True,blank=True)
    factura = models.BooleanField(default=False,null=True,blank=True)
    estado = models.CharField(max_length=10,null=True,blank=True)
    accion = models.CharField(max_length=20,null=True,blank=True)
    uuid = models.SlugField(blank=True,unique=True)
    fecha_registro = models.DateField(auto_created=True,null=True,blank=True)
    concepto = models.CharField(max_length=200,null=True,blank=True)
    valor = models.FloatField(default=0)
    comprobante_factura = models.FileField(upload_to='comprobantes/',null=True,blank=True)

    tipo_ingreso = models.CharField(
        default=TipoMovimiento.INGRESO,
        max_length=50,
    )
    



    def __str__(self):
        return f"{self.tipo_ingreso} - {self.concepto} - {self.valor}"
    
    def gen_uid(self):
        self.uid = uuid.uuid4()
        self.save()

    

def get_estado_caja(user,unidad_productiva):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    ingresos = Movimiento.objects.filter(Q(tipo_ingreso='IN')&Q(unidad_productiva=unidad_productiva)).aggregate(Sum('valor'))['valor__sum']
    egresos = Movimiento.objects.filter(Q(tipo_ingreso='OUT')&Q(unidad_productiva=unidad_productiva)).aggregate(Sum('valor'))['valor__sum']
    if ingresos == None:
        ingresos = 0
    if egresos == None:
        egresos = 0
    ingresos_f = locale.currency(ingresos, symbol=True, grouping=True)
    egresos_f = locale.currency(egresos, symbol=True, grouping=True)
    diferencia = ingresos - egresos
    diferencia_f = locale.currency(diferencia, symbol=True, grouping=True)
    return diferencia_f, ingresos_f, egresos_f

def get_estado_caja_admin(user,unidad_productiva=None):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    if unidad_productiva:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        unidad_productiva=UnidadProductiva.objects.get(id=user.last_productiva)
        ingresos = Movimiento.objects.filter(Q(tipo_ingreso='IN')&Q(unidad_productiva=unidad_productiva)).aggregate(Sum('valor'))['valor__sum']
        egresos = Movimiento.objects.filter(Q(tipo_ingreso='OUT')&Q(unidad_productiva=unidad_productiva)).aggregate(Sum('valor'))['valor__sum']
        
    elif user.last_productiva:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        unidad_productiva=UnidadProductiva.objects.get(id=user.last_productiva)
        ingresos = Movimiento.objects.filter(Q(tipo_ingreso='IN')&Q(unidad_productiva=unidad_productiva)).aggregate(Sum('valor'))['valor__sum']
        egresos = Movimiento.objects.filter(Q(tipo_ingreso='OUT')&Q(unidad_productiva=unidad_productiva)).aggregate(Sum('valor'))['valor__sum']

    else:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        ingresos = Movimiento.objects.filter(tipo_ingreso='IN').aggregate(Sum('valor'))['valor__sum']
        egresos = Movimiento.objects.filter(tipo_ingreso='OUT').aggregate(Sum('valor'))['valor__sum']

    if ingresos == None:
        ingresos = 0
    if egresos == None:
        egresos = 0
    ingresos_f = locale.currency(ingresos, symbol=True, grouping=True)
    egresos_f = locale.currency(egresos, symbol=True, grouping=True)
    diferencia = ingresos - egresos
    diferencia_f = locale.currency(diferencia, symbol=True, grouping=True)

    return diferencia_f, ingresos_f, egresos_f



def get_movimientos_usuario(user):
    return Movimiento.objects.filter(unidad_productiva__usuarioRegistro=user).all()

def get_movimientos(usuario,unidad_productiva=None):
    if usuario.groups.filter(name='Administrador').exists():
        disponible,ingreso,egreso = get_estado_caja_admin(usuario,unidad_productiva)
    elif usuario.groups.filter(name='Comun').exists():
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso = get_estado_caja(usuario,unidad_productiva)
    else:
        disponible,ingreso,egreso = get_estado_caja_admin(usuario)
    return disponible,ingreso,egreso


class Comentario(models.Model):
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE,null=True,blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE,null=True,blank=True)
    comentario = models.CharField(max_length=200,null=True,blank=True)
    fecha_registro = models.DateField(auto_created=True,null=True,blank=True)
    def __str__(self):
        return f"{self.usuario} - {self.comentario}"
    
from Modulos.UnidadProductiva.models import UnidadProductiva
from Modulos.UnidadNegocio.models import UnidadNegocio
from Modulos.CentroCostos.models import SubCentroCosto
from Modulos.Usuario.models import Usuario
from django.db.models import Sum
from django.db.models import Q
from django.db import models
from django.conf import settings
from openpyxl import load_workbook
import locale
import uuid
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl import Workbook
from django.http import HttpResponse
import pyexcel as pe
from fpdf import FPDF
from django.http import FileResponse
from fpdf import FPDF



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
    accion = models.CharField(max_length=200,null=True,blank=True)
    uuid = models.SlugField(blank=True)
    fecha_registro = models.DateTimeField(auto_now=True,null=True,blank=True)
    fecha_modificacion = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    concepto = models.CharField(max_length=200,null=True,blank=True)
    valor = models.FloatField(default=0)
    comprobante_factura = models.FileField(upload_to='comprobantes/',null=True,blank=True)
    ingreso_bancario = models.BooleanField(default=False,null=True,blank=True)
    negociacion = models.CharField(max_length=255,null=True,blank=True)

    tipo_ingreso = models.CharField(
        default=TipoMovimiento.INGRESO,
        max_length=50,
    )
    



    def __str__(self):
        return f"{self.tipo_ingreso} - {self.concepto} - {self.valor}"
    
    def gen_uid(self):
        self.uid = uuid.uuid4()
        self.save()


def export_to_excel(queryset,to_pdf=False):
    # Obtener los objetos de Django
    #queryset = Movimiento.objects.all()

    # Crear el libro de trabajo de Excel y la hoja de cálculo
    workbook = Workbook()
    workbook.iso_dates = True
    worksheet = workbook.active

    # Escribir los encabezados de las columnas
    headers = ['Fecha de Registro', 'Fecha Aprobado', 'Tipo de Ingreso', 'Unidad Productiva', 'Concepto', 'Valor', 'SubCentro Costo', 'Numero de Factura', 'Tipo de Documento', 'Factura', 'Estado', 'Accion', 'Comprobante Factura']
    for col_num, header in enumerate(headers, 1):
        worksheet.cell(row=1, column=col_num, value=header)

    # Escribir los datos del objeto
    for row_num, obj in enumerate(queryset, 2):
        if not obj.unidad_productiva:
            unidad_productiva_nombre = 'N/A'
        else:
            unidad_productiva_nombre =  obj.unidad_productiva.nombre
        if obj.tipo_ingreso=='IN':
            if obj.ingreso_bancario:
                tipo_ingreso = 'Ingreso Bancario'
            else:
                tipo_ingreso = 'Ingreso de caja'
            if obj.accion == 'Reducción de Caja':
                tipo_ingreso = 'Reducción de Caja'
        elif obj.tipo_ingreso=='OUT':
            if obj.ingreso_bancario:
                tipo_ingreso = 'Egreso Bancario'
            else:
                tipo_ingreso = 'Egreso de caja'
        else:
            tipo_ingreso = 'N/A'

        if not obj.sub_centro_costo:
            sub_centro_costo_nombre = 'N/A'
        else:
            sub_centro_costo_nombre = obj.sub_centro_costo.nombre
            
        worksheet.cell(row=row_num, column=1, value=obj.fecha_registro.strftime('%d/%m/%Y %H:%M'))
        worksheet.cell(row=row_num, column=2, value=obj.fecha_modificacion.strftime('%d/%m/%Y %H:%M'))
        worksheet.cell(row=row_num, column=3, value=tipo_ingreso)
        worksheet.cell(row=row_num, column=4, value=unidad_productiva_nombre)
        worksheet.cell(row=row_num, column=5, value=obj.concepto)
        worksheet.cell(row=row_num, column=6, value=obj.valor)
        worksheet.cell(row=row_num, column=7, value=sub_centro_costo_nombre)
        worksheet.cell(row=row_num, column=8, value=obj.numero_factura)
        worksheet.cell(row=row_num, column=9, value=obj.tipo_documento)
        worksheet.cell(row=row_num, column=10, value=obj.factura)
        worksheet.cell(row=row_num, column=11, value=obj.estado)
        worksheet.cell(row=row_num, column=12, value=obj.accion)
    
    if to_pdf:
        workbook.save('archivo_excel.xlsx')
        return convert_xlsx_to_pdf('archivo_excel.xlsx', 'pdf_file.pdf')
    else:
        # Crear la respuesta del archivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=archivo.xlsx'
        workbook.save(response)
        return response




def convert_xlsx_to_pdf(xlsx_file, pdf_file):
    # Load the XLSX file
    workbook = load_workbook(xlsx_file)

    # Select the active worksheet
    worksheet = workbook.active

    # Create the PDF object
    pdf = FPDF()

    # Add a page to the PDF
    pdf.add_page()

    # Iterate over the rows of the XLSX and add them to the PDF
    for row in worksheet.iter_rows(values_only=True):
        line = '\t'.join(str(cell) for cell in row)
        pdf.cell(0, 10, txt=line, ln=True)

    # Guardar el archivo PDF
    pdf.output(pdf_file)
     # Crear una instancia de FileResponse con el archivo PDF
    response = FileResponse(open(pdf_file, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="archivo.pdf"'

    return response


    

def get_estado_caja(user):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    filtros_in = Q(tipo_ingreso='IN')&Q(unidad_productiva__usuarioRegistro=user)&Q(ingreso_bancario=False)
    filtros_out = Q(tipo_ingreso='OUT')&Q(estado='Aprobado')&Q(unidad_productiva__usuarioRegistro=user)&Q(ingreso_bancario=False)
    filtros_in_ba = Q(tipo_ingreso='IN')&Q(unidad_productiva__usuarioRegistro=user)&Q(ingreso_bancario=True)
    filtros_out_ba = Q(tipo_ingreso='OUT')&Q(estado='Aprobado')&Q(unidad_productiva__usuarioRegistro=user)&Q(ingreso_bancario=True)

    ingresos = Movimiento.objects.filter(filtros_in).aggregate(Sum('valor'))['valor__sum']
    egresos = Movimiento.objects.filter(filtros_out).aggregate(Sum('valor'))['valor__sum']
    ingresos_ba = Movimiento.objects.filter(filtros_in_ba).aggregate(Sum('valor'))['valor__sum']
    egresos_ba = Movimiento.objects.filter(filtros_out_ba).aggregate(Sum('valor'))['valor__sum']

    if ingresos == None:
        ingresos = 0
    if egresos == None:
        egresos = 0

    ingresos_f = locale.currency(ingresos, symbol=True, grouping=True)
    egresos_f = locale.currency(egresos, symbol=True, grouping=True)
    diferencia = ingresos - egresos
    diferencia_f = locale.currency(diferencia, symbol=True, grouping=True)

    if ingresos_ba == None:
        ingresos_ba = 0
    if egresos_ba == None:
        egresos_ba = 0
    ingresos_ba_f = locale.currency(ingresos_ba, symbol=True, grouping=True)
    egresos_ba_f = locale.currency(egresos_ba, symbol=True, grouping=True)
    diferencia_ba = ingresos_ba - egresos_ba
    diferencia_ba_f = locale.currency(diferencia_ba, symbol=True, grouping=True)

    return diferencia_f, ingresos_f, egresos_f, diferencia_ba_f, ingresos_ba_f, egresos_ba_f

def get_estado_caja_admin(user,unidad_productiva=None):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    
    unidades_negocio = UnidadNegocio.objects.filter(admin=user).all()
    merged_queryset = None

    querysets = []
    unidades_negocio = UnidadNegocio.objects.filter(admin=user).all()
    # Inicializa un objeto Q vacío
    union_query = Q()
    for unidad_negocio in unidades_negocio:
        condicion = Q(unidad_productiva__in=unidad_negocio.unidades_productivas.all()) 
        union_query |= condicion


    filtros_in = Q(tipo_ingreso='IN')&union_query&Q(ingreso_bancario=False)
    filtros_out = Q(tipo_ingreso='OUT')&Q(estado='Aprobado')&union_query&Q(ingreso_bancario=False)
    filtros_in_ba = Q(tipo_ingreso='IN')&union_query&Q(ingreso_bancario=True)
    filtros_out_ba = Q(tipo_ingreso='OUT')&Q(estado='Aprobado')&union_query&Q(ingreso_bancario=True)

    ingresos = Movimiento.objects.filter(filtros_in).aggregate(Sum('valor'))['valor__sum']
    egresos = Movimiento.objects.filter(filtros_out).aggregate(Sum('valor'))['valor__sum']
    ingresos_ba = Movimiento.objects.filter(filtros_in_ba).aggregate(Sum('valor'))['valor__sum']
    egresos_ba = Movimiento.objects.filter(filtros_out_ba).aggregate(Sum('valor'))['valor__sum']

    if ingresos == None:
        ingresos = 0
    if egresos == None:
        egresos = 0

    ingresos_f = locale.currency(ingresos, symbol=True, grouping=True)
    egresos_f = locale.currency(egresos, symbol=True, grouping=True)
    diferencia = ingresos - egresos
    diferencia_f = locale.currency(diferencia, symbol=True, grouping=True)

    if ingresos_ba == None:
        ingresos_ba = 0
    if egresos_ba == None:
        egresos_ba = 0
    ingresos_ba_f = locale.currency(ingresos_ba, symbol=True, grouping=True)
    egresos_ba_f = locale.currency(egresos_ba, symbol=True, grouping=True)
    diferencia_ba = ingresos_ba - egresos_ba
    diferencia_ba_f = locale.currency(diferencia_ba, symbol=True, grouping=True)

    return diferencia_f, ingresos_f, egresos_f, diferencia_ba_f, ingresos_ba_f, egresos_ba_f



def get_movimientos_usuario(usuario):
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        querysets = []
        unidades_negocio = UnidadNegocio.objects.filter(admin=usuario).all()
        # Inicializa un objeto Q vacío
        union_query = Q()
        for unidad_negocio in unidades_negocio:
            condicion = Q(unidad_productiva__in=unidad_negocio.unidades_productivas.all()) 
            union_query |= condicion
        return  Movimiento.objects.filter(union_query).all()
    else:
        return Movimiento.objects.filter(unidad_productiva__usuarioRegistro=usuario).all()

def get_movimientos(usuario,unidad_productiva=None):
    if usuario.groups.filter(name__in=['Administrador','Auditor']).exists():
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja_admin(usuario,unidad_productiva)
        return  disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba
    elif usuario.groups.filter(name='Comun').exists():
        unidad_productiva = UnidadProductiva.objects.filter(usuarioRegistro=usuario).first()
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja(usuario)
        return disponible,ingreso,egreso,disponible_ba,ingreso_ba,egreso_ba
    else:
        disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba = get_estado_caja_admin(usuario)
        return disponible,ingreso,egreso, disponible_ba,ingreso_ba,egreso_ba
   












class Comentario(models.Model):
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE,null=True,blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE,null=True,blank=True)
    comentario = models.CharField(max_length=200,null=True,blank=True)
    fecha_registro = models.DateField(auto_created=True,null=True,blank=True)
    def __str__(self):
        return f"{self.usuario} - {self.comentario}"
    


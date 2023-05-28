import locale
from django.db.models import Q
from django.db.models import Sum
from io import BytesIO # nos ayuda a convertir un html en pdf
from django.http import HttpResponse
from django.template.loader import get_template
from Modulos.Movimiento.models import Movimiento
from Modulos.UnidadProductiva.models import UnidadProductiva

from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def area_chart_data(movimientos):
    fechas = []
    ingresos = []
    egresos = []
    acumulado_ingresos = 0
    acumulado_egresos = 0
    for movimiento in movimientos:
        if not movimiento.fecha_registro:
            fechas.append("Sin fecha")
        else:
            fechas.append(movimiento.fecha_registro.strftime("%d/%m/%Y"))
        
        if movimiento.tipo_ingreso == "IN":
            acumulado_egresos = acumulado_egresos+0
            acumulado_ingresos = acumulado_ingresos+int(movimiento.valor)
        elif movimiento.tipo_ingreso == "OUT" and movimiento.estado == "Aprobado":
            acumulado_egresos = acumulado_egresos+int(movimiento.valor)
            acumulado_ingresos = acumulado_ingresos+0
        else:
            acumulado_egresos = acumulado_egresos+0
            acumulado_ingresos = acumulado_ingresos+0
        ingresos.append(acumulado_ingresos)
        egresos.append(acumulado_egresos) 
    
    return fechas, ingresos, egresos

def pie_chart_data(movimientos):
    filter = Q(tipo_ingreso="OUT") & Q(estado="Aprobado")
    ingresos = movimientos.filter(tipo_ingreso="IN").aggregate(Sum('valor'))['valor__sum']
    egresos = movimientos.filter(filter).aggregate(Sum('valor'))['valor__sum']
    if ingresos is None:
        ingresos = 0
    if egresos is None:
        egresos = 0 
    disponible = ingresos + egresos
    ingresos = int(round((ingresos/disponible)*100, 2))
    egresos = int(round((egresos/disponible)*100, 2))

    return ingresos, egresos


def mayor_ingreso_uproductiva(movimientos):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        # Filtrar los 3 tipos de ingresos y obtener la suma mayor
        list_unidad_productiva = []

        # Obtener las unidades productivas y sus sumas de movimientos
        unidades_productivas = UnidadProductiva.objects.all()
        suma_unidades_productivas = []

        for unidad_productiva in unidades_productivas:
            filter = Q(tipo_ingreso="IN") & Q(unidad_productiva=unidad_productiva)
            suma = movimientos.filter(filter).aggregate(Sum('valor'))['valor__sum']
            suma_unidades_productivas.append({
                'unidad_productiva': unidad_productiva.nombre,
                'suma': suma if suma else 0
            })

        # Ordenar por la suma en orden descendente
        suma_unidades_productivas = sorted(suma_unidades_productivas, key=lambda x: x['suma'], reverse=True)

        width = [94,82,70]
        i = 0

        if suma_unidades_productivas:
            if len(suma_unidades_productivas)>3:
                suma_unidades_productivas = suma_unidades_productivas[:3]
            else:
                suma_unidades_productivas = suma_unidades_productivas[:len(suma_unidades_productivas)]
            for suma_unidad_productiva in suma_unidades_productivas:
                suma_unidad_productiva['with'] = width[i]
                suma_unidad_productiva['suma'] = locale.currency(suma_unidad_productiva['suma'], symbol=True, grouping=True)
                i +=1
            return suma_unidades_productivas
        else:
            return [],[]
        

def mayor_egreso_uproductiva(movimientos):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        # Obtener las unidades productivas y sus sumas de movimientos
        unidades_productivas = UnidadProductiva.objects.all()
        suma_unidades_productivas = []

        for unidad_productiva in unidades_productivas:
            filter = Q(tipo_ingreso="OUT") & Q(unidad_productiva=unidad_productiva) & Q(estado="Aprobado")
            suma = movimientos.filter(filter).aggregate(Sum('valor'))['valor__sum']
            suma_unidades_productivas.append({
                'unidad_productiva': unidad_productiva.nombre,
                'suma': suma if suma else 0
            })

        # Ordenar por la suma en orden descendente
        suma_unidades_productivas = sorted(suma_unidades_productivas, key=lambda x: x['suma'], reverse=True)

        width = [94,82,70]
        i = 0

        if suma_unidades_productivas:
            if len(suma_unidades_productivas)>3:
                suma_unidades_productivas = suma_unidades_productivas[:3]
            else:
                suma_unidades_productivas = suma_unidades_productivas[:len(suma_unidades_productivas)]
            for suma_unidad_productiva in suma_unidades_productivas:
                suma_unidad_productiva['with'] = width[i]
                suma_unidad_productiva['suma'] = locale.currency(suma_unidad_productiva['suma'], symbol=True, grouping=True)
                i +=1
            return suma_unidades_productivas
        else:
            return [],[]
        
def centro_costos_uprod(movimientos):
    resultados = movimientos.values('sub_centro_costo__nombre').annotate(suma_valor=Sum('valor'))
    lista_resultados = []
    for resultado in resultados:
        sub_centro_costo = resultado['sub_centro_costo__nombre']
        suma_valor = int(resultado['suma_valor'])
        lista_resultados.append({'sub_centro_costo': sub_centro_costo, 'suma_valor': suma_valor})
    
    return lista_resultados

from django.db.models import Q
from django.db.models import Sum
from io import BytesIO # nos ayuda a convertir un html en pdf
from django.http import HttpResponse
from django.template.loader import get_template

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
    disponible = ingresos - egresos
    ingresos = int(round((ingresos/disponible)*100, 2))
    egresos = int(round((egresos/disponible)*100, 2))

    return ingresos, egresos

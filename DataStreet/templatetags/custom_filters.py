from django import template
import datetime
import re

register = template.Library()

@register.filter
def custom_date_format(value):
    months = {
        'Enero': 1,
        'Febrero': 2,
        'Marzo': 3,
        'Abril': 4,
        'Mayo': 5,
        'Junio': 6,
        'Julio': 7,
        'Agosto': 8,
        'Septiembre': 9,
        'Octubre': 10,
        'Noviembre': 11,
        'Diciembre': 12
    }

    try:
        match = re.search(r'(\d{1,2}) de (\w+) de (\d{4}) a las (\d{1,2}):(\d{2})', value)
        day, month, year, hour, minute = match.groups()

        month_number = months.get(month, 0)

        date_obj = datetime.datetime(int(year), month_number, int(day), int(hour), int(minute))
        
        return date_obj.strftime('%d/%m/%Y - %H:%M')

    except:
        return value


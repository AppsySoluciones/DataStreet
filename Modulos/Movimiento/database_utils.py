from Modulos.UnidadProductiva.models import UnidadProductiva
from Modulos.UnidadNegocio.models import UnidadNegocio
from Modulos.CentroCostos.models import CentroCosto,SubCentroCosto

import pandas as pd

filepath = 'CentroCostoDB.xlsx'

df = pd.read_excel(filepath, sheet_name='Hoja1')



UnidadesNegocio = UnidadNegocio.objects.all()
CentroCosto_lista = CentroCosto.objects.all()
SubCentroCosto_lista = SubCentroCosto.objects.all()


for i in range(len(df)):
    unegocio = df.iloc[i]['Unidad de Negocio']
    ccosto = df.iloc[i]['Centro de Costo']
    subccosto = df.iloc[i]['Subcentro de Costo']
    print(unegocio,ccosto,subccosto)

    if UnidadesNegocio.filter(nombre=unegocio).exists():
        unegocio = UnidadesNegocio.filter(nombre=unegocio).first()
    else:
        unegocio = UnidadNegocio.objects.create(nombre=unegocio,descripcion=unegocio)
        unegocio.save()
    
    if not CentroCosto_lista.filter(nombre=ccosto).exists():
        centro = CentroCosto.objects.create(nombre=ccosto)
        subcentro = SubCentroCosto.objects.create(nombre=subccosto)
        subcentro.save()
        centro.subcentro.add(subcentro)
        centro.save()
    else:
        centro = CentroCosto_lista.filter(nombre=ccosto).get()
        if centro.subcentro.filter(nombre=subccosto).exists():
            continue
        else:
            subcentro = SubCentroCosto.objects.create(nombre=subccosto)
            centro.subcentro.add(subcentro)
            centro.save()
        
        centro.save()





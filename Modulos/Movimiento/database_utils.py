from Modulos.UnidadProductiva.models import UnidadProductiva
from Modulos.UnidadNegocio.models import UnidadNegocio
from Modulos.CentroCostos.models import CentroCosto,SubCentroCosto
from django.db.models import Q

import pandas as pd

filepath = 'CentroCostoDB.xlsx'

df = pd.read_excel(filepath, sheet_name='Hoja1')



UnidadesNegocio = UnidadNegocio.objects.all()
CentroCosto_lista = CentroCosto.objects.all()
SubCentroCosto_lista = SubCentroCosto.objects.all()

# Eliminar los duplicados de la columna "columna_a"
#df_sin_duplicados = df['Unidad de Negocio'].drop_duplicates().to_list()

#print(df_sin_duplicados)

columnas_uprod = df['Unidad de Negocio'].unique()
columnas_uprod = columnas_uprod.tolist()


for unidad_negocio in columnas_uprod:
    df_unidad_negocio = df[df['Unidad de Negocio'] == unidad_negocio]
    for i in range(len(df_unidad_negocio)):
        unegocio = df_unidad_negocio.iloc[i]['Unidad de Negocio']
        ccosto = df_unidad_negocio.iloc[i]['Centro de Costo']
        subccosto = df_unidad_negocio.iloc[i]['Subcentro de Costo']
        
        print(unegocio,ccosto,subccosto)

        if UnidadesNegocio.filter(nombre=unegocio).exists():
            unegocio = UnidadesNegocio.filter(nombre=unegocio).first()
        else:
            unegocio = UnidadNegocio.objects.create(nombre=unegocio,descripcion=unegocio)
            unegocio.save()

        filtro_ccosto = Q(nombre=ccosto) & Q(unegocio=unegocio)
        if not CentroCosto_lista.filter(filtro_ccosto).exists():
            centro = CentroCosto.objects.create(nombre=ccosto)
            subcentro = SubCentroCosto.objects.create(nombre=subccosto)
            subcentro.save()
            centro.unegocio.add(unegocio)
            centro.subcentro.add(subcentro)
            centro.save()
        else:
            centro = CentroCosto_lista.filter(filtro_ccosto).get()
            if centro.subcentro.filter(nombre=subccosto).exists():
                continue
            else:
                subcentro = SubCentroCosto.objects.create(nombre=subccosto)
                centro.subcentro.add(subcentro)
                centro.unegocio.add(unegocio)
                centro.save()
            
            centro.save()

'''diccionario = {}
for _, row in df.iterrows():
    unidad_negocio = row['Unidad de Negocio']
    centro_costo = row['Centro de Costo']
    subcentro_costo = row['Subcentro de Costo']
    
    if unidad_negocio not in diccionario:
        diccionario[unidad_negocio] = []
    
    centro_costo_encontrado = False
    for cc in diccionario[unidad_negocio]:
        if cc['Nombre'] == centro_costo:
            cc['Subcentros'].append(subcentro_costo)
            centro_costo_encontrado = True
            break
    
    if not centro_costo_encontrado:
        diccionario[unidad_negocio].append({
            'Nombre': centro_costo,
            'Subcentros': [subcentro_costo]
        })
print(diccionario['Administrativa'])

columnas_uprod = df['Unidad de Negocio'].unique()
columnas_uprod = columnas_uprod.tolist()'''
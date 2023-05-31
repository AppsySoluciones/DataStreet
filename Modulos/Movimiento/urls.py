from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('ingreso/',views.ingresos,name='ingreso'),
    path('egreso/',views.egresos),
    path('ingreso_ba/',views.ingresos_ba),
    path('egreso_ba/',views.egresos_ba),
    path('registraringreso/',views.registrarIngreso),
    path('registraregreso/',views.registrarEgreso),
    path('tablaing/',views.tablas_ingresos),
    path('tablaegre/',views.tablas_egresos),
    path('tablaingba/',views.tablas_ingresos_ba),
    path('tablaegreba/',views.tablas_egresos_ba),
    path('movimiento/detalle/<int:pk>/',views.detalle),
    path('movimiento/editar/<int:pk>/',views.edicion_mov),
    path('movimiento/editar/<int:pk>/edit',views.edicion_form),
    path('movimiento/addnote/<int:pk>/',views.agregar_comentario),
    path('selectunidad/',views.select_unidad_prod),
    path('movimiento/comprobante/<int:pk>/',views.comprobante),
    path('movimiento/aprob/<int:pk>/',views.aprobar_mov),
    path('movimiento/rechazar/<int:pk>/',views.rechazar_mov),
    path('generarxlsing/',views.generar_excel_ingresos),
    path('generarxlsegre/',views.generar_excel_egresos),
    path('generarpdfing/',views.Pdf_ingresos.as_view()),
    path('generarpdfingba/',views.Pdf_ingresos_ba.as_view()),
    path('generarpdfegre/',views.Pdf_egresos_ba.as_view()),
    ]
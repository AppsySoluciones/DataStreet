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
    path('movimiento/detalle/<int:pk>/',views.detalle),
    path('movimiento/editar/<int:pk>/',views.edicion_mov),
    path('movimiento/editar/<int:pk>/edit',views.edicion_form),
    path('movimiento/addnote/<int:pk>/',views.agregar_comentario),
    path('selectunidad/',views.select_unidad_prod),
    ]
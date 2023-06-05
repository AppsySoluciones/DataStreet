from django.urls import path
from . import views

urlpatterns = [
    path('testemail/',views.send_correoe),
    ]
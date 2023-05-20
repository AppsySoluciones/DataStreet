from django.db import models
from Modulos.UnidadNegocio.models import UnidadNegocio

class SubCentroCosto(models.Model):
    nombre = models.CharField(max_length=50,unique=True)
    descripcion = models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return "Sub. "+self.nombre

# Create your models here.
class CentroCosto(models.Model):
    nombre = models.CharField(max_length=50,unique=True)
    descripcion = models.CharField(max_length=200,null=True,blank=True)
    unegocio = models.ManyToManyField(UnidadNegocio,related_name='ccosto_unegocio',blank=True)
    subcentro = models.ManyToManyField(SubCentroCosto,blank=True)
    
    def __str__(self):
        return self.nombre + " "
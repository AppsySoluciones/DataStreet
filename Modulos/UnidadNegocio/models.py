from django.db import models
from Modulos.Usuario.models import Usuario
from Modulos.UnidadProductiva.models import UnidadProductiva
# Create your models here.
class UnidadNegocio(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200,null=True,blank=True)
    telefono = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(max_length=254,null=True,blank=True)
    admin = models.ForeignKey(Usuario, on_delete=models.CASCADE,null=True,blank=True)
    unidades_productivas = models.ManyToManyField(UnidadProductiva,blank=True)


    def __str__(self):
        return self.nombre + " " + str(self.descripcion)
    

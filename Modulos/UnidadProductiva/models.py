from django.db import models
from Modulos.Usuario.models import Usuario
# Create your models here.
class UnidadProductiva(models.Model):
    nombre = models.CharField(max_length=50,null=True,blank=True)
    descripcion = models.CharField(max_length=200,null=True,blank=True)
    ubcacion = models.CharField(max_length=300,null=True,blank=True)
    telefono = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(max_length=254,null=True,blank=True)
    usuarioRegistro = models.ManyToManyField(Usuario,related_name='user_asocited',blank=True) 
    usuarioAuditor = models.ManyToManyField(Usuario,related_name='user_auditor',blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.descripcion}"
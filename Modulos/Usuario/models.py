from django.db import models
from django.core.mail import send_mail
from django.shortcuts import render

import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.decorators import user_passes_test
from django.db.models.signals import pre_save
from django.dispatch import receiver


# Create your models here.

class UserManager(BaseUserManager):
    def _create_user(self, email, nombre, apellido, password, is_staff, is_superuser, **extra_fields):
        user = self.model(
            email=email,
            nombre=nombre,
            apellido=apellido,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, nombre, apellido, password=None, **extra_fields):
        return self._create_user(email, nombre, apellido, password, False, False, **extra_fields)

    def create_superuser(self, email, nombre, apellido, password=None, **extra_fields):
        return self._create_user(email, nombre, apellido, password, True, True, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254,null=True,blank=True, unique=True)
    nombre = models.CharField(max_length=50,null=True,blank=True)
    telefono = models.CharField(max_length=50,null=True,blank=True)
    cedula = models.CharField(max_length=20,null=True,blank=True)
    apellido = models.CharField(max_length=50,null=True,blank=True)
    last_productiva = models.IntegerField(null=True,blank=True)
    presupuesto = models.FloatField(null=True,blank=True,default=0)


    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    
    

    def grupo_requerido(self,grupo_nombre):
        def chequear_grupo(self):
            return self.groups.filter(name=grupo_nombre).exists()

        return user_passes_test(chequear_grupo)
    
    def send_email(self,subject, message):
        # Enviar notificación por correo electrónico
        subject = 'Notificación'
        from_email = 'noreply@grovity.co'
        recipient_list = [str(self.email)]
        send_mail(subject, message, from_email, recipient_list)
        
        return None
    


# Generated by Django 4.2 on 2023-04-27 20:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Usuario', '0001_initial'),
        ('UnidadNegocio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnidadProductiva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=200)),
                ('direccion', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('unidadNegocio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UnidadNegocio.unidadnegocio')),
                ('usuarioRegistro', models.ManyToManyField(blank=True, related_name='user_asocited', to='Usuario.usuario')),
            ],
        ),
    ]

# Generated by Django 3.1.2 on 2023-05-04 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UnidadNegocio', '0002_remove_unidadnegocio_direccion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidadnegocio',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='unidadnegocio',
            name='nombre',
            field=models.CharField(max_length=50),
        ),
    ]

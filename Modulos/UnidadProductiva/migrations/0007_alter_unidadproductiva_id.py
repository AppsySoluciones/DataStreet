# Generated by Django 4.2 on 2023-05-09 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UnidadProductiva', '0006_remove_unidadproductiva_unidadnegocio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidadproductiva',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

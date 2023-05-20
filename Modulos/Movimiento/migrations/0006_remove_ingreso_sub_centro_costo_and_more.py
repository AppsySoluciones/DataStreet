# Generated by Django 4.2 on 2023-05-05 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CentroCostos', '0004_alter_centrocosto_id_alter_subcentrocosto_id'),
        ('Movimiento', '0005_ingreso_sub_centro_costo_alter_egreso_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingreso',
            name='sub_centro_costo',
        ),
        migrations.AddField(
            model_name='ingreso',
            name='sub_centro_costo',
            field=models.ManyToManyField(blank=True, null=True, to='CentroCostos.subcentrocosto'),
        ),
    ]
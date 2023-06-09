# Generated by Django 4.2 on 2023-05-10 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UnidadProductiva', '0007_alter_unidadproductiva_id'),
        ('Movimiento', '0012_alter_movimiento_concepto_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movimiento',
            name='comprobante_factura',
        ),
        migrations.RemoveField(
            model_name='movimiento',
            name='uuid',
        ),
        migrations.AlterField(
            model_name='movimiento',
            name='unidad_productiva',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='UnidadProductiva.unidadproductiva'),
        ),
    ]

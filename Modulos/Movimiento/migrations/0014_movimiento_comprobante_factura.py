# Generated by Django 4.2 on 2023-05-10 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Movimiento', '0013_remove_movimiento_comprobante_factura_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='comprobante_factura',
            field=models.FileField(blank=True, null=True, upload_to='comprobantes/'),
        ),
    ]

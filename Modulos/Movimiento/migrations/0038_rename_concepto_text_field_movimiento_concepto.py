# Generated by Django 4.2.1 on 2024-02-20 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Movimiento', '0037_remove_movimiento_concepto'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movimiento',
            old_name='concepto_text_field',
            new_name='concepto',
        ),
    ]

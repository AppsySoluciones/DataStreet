# Generated by Django 4.2.1 on 2023-05-21 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Movimiento', '0017_comentario'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='ingreso_bancario',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]

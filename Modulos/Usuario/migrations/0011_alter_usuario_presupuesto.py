# Generated by Django 4.2.1 on 2023-06-02 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuario', '0010_usuario_presupuesto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='presupuesto',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]

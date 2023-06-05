# Generated by Django 4.2.1 on 2023-06-05 21:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Movimiento', '0027_movimiento_usuario_presupuesto'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='usuario_admin_ingreso',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuario_admin_ingreso', to=settings.AUTH_USER_MODEL),
        ),
    ]

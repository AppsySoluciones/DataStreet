# Generated by Django 3.1.2 on 2023-05-07 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuario', '0004_alter_usuario_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

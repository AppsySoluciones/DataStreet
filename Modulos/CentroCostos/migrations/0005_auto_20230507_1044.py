# Generated by Django 3.1.2 on 2023-05-07 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CentroCostos', '0004_alter_centrocosto_id_alter_subcentrocosto_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centrocosto',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='subcentrocosto',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

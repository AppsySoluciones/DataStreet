# Generated by Django 4.2 on 2023-05-05 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CentroCostos', '0003_auto_20230504_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centrocosto',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='subcentrocosto',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

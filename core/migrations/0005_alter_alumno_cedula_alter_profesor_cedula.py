# Generated by Django 5.2.3 on 2025-06-28 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_alumno_cedula_alter_profesor_cedula'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='cedula',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='profesor',
            name='cedula',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]

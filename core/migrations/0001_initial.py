# Generated by Django 5.2.3 on 2025-06-26 19:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Corte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Materia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Profesor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('cedula', models.CharField(max_length=20, unique=True)),
                ('is_coor', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('cedula', models.CharField(max_length=20, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Asignatura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('fecha_de_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_de_entrega', models.DateTimeField()),
                ('id_coorte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaturas', to='core.corte')),
            ],
        ),
        migrations.CreateModel(
            name='Inscripcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inscripciones', to=settings.AUTH_USER_MODEL)),
                ('id_materia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inscripciones', to='core.materia')),
            ],
        ),
        migrations.AddField(
            model_name='corte',
            name='id_materia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cortes', to='core.materia'),
        ),
        migrations.AddField(
            model_name='materia',
            name='id_profesor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='materias_asignadas', to='core.profesor'),
        ),
        migrations.CreateModel(
            name='Carrera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('id_coor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carreras_coordinadas', to='core.profesor')),
            ],
        ),
        migrations.CreateModel(
            name='Semestre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField()),
                ('id_carrera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semestres', to='core.carrera')),
            ],
        ),
        migrations.AddField(
            model_name='materia',
            name='id_semestre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materias', to='core.semestre'),
        ),
    ]

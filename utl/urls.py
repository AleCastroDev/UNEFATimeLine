from django.contrib import admin
from django.urls import path, include
from core.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', welcome, name='welcome'),
    path('registro/', registro, name='registro'),
    path('login/', login_view, name='login'),
    path('login_prof/', login_prof_view, name='login_prof'),

    path('logout/', custom_logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile_prof/', profile_prof_view, name='profile_prof'),

    path('eliminar-inscripcion/<int:id_materia>/', eliminar_inscripcion, name='eliminar_inscripcion'),
    path('api/semestres/<int:carrera_id>/', obtener_semestres_por_carrera, name='obtener_semestres'),
    path('api/materias/<int:semestre_id>/', obtener_materias_por_semestre, name='obtener_materias'),
    path('api/inscribir/', inscribir_materia, name='inscribir_materia'),

    path('calendario/', calendario, name='calendario'),
    path('api/tareas/', tareas_usuario_json, name='tareas_usuario_json'),

    path('inicio/', home, name='inicio'),
    path('semana/', home_semana, name='semana'),
    path('mes/', home_mes, name='mes'),

    path('asignatura/crear/<int:materia_id>/', crear_asignatura_view, name='crear_asignatura'),

    path('eliminar-asignatura/<int:id_asigantura>/', eliminar_asignatura, name='eliminar_asignatura'),
    path('asignatura/editar/<int:id_asignatura>/', editar_asignatura, name='editar_asignatura'),

    path('calendario_prof/', calendario_prof, name='calendario_prof'),
    path('api/tareas_prof/', tareas_prof_json, name='tareas_prof_json'),

    path('inicio_prof/', home_prof, name='inicio_prof'),
    path('semana_prof/', home_semana_prof, name='semana_prof'),
    path('mes_prof/', home_mes_prof, name='mes_prof'),
]

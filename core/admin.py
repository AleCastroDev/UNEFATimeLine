from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from .models import *

admin.site.register(Alumno)
admin.site.register(Inscripcion)
admin.site.register(Materia)
admin.site.register(Semestre)
admin.site.register(Carrera)
admin.site.register(Profesor)
admin.site.register(Asignatura)

class CedulaUserAdmin(UserAdmin):
    model = Alumno
    list_display = ('cedula', 'is_staff', 'is_superuser')
    ordering = ('cedula',)
    search_fields = ('cedula',)

    fieldsets = (
        (None, {'fields': ('cedula', 'password')}),
        (_('Permisos'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('cedula', 'password1', 'password2'),
        }),
    )
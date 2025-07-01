from django import forms
from .models import *

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'cedula']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre:'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula:'}),
        }


class LoginForm(forms.Form):
    cedula = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Cédula:'
        })
    )

    password = forms.CharField(
        widget=forms.HiddenInput(),
        initial='123'            
    )

class ProfesorLoginForm(forms.Form):
    cedula = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cédula:'
        })
    )
    
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña:'
        })
    )

class UpdateNameForm(forms.Form):
    nombre = forms.CharField(max_length=50, label='')


class UpdateCedulaForm(forms.Form):
    cedula = forms.CharField(max_length=20, label='')

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['tipo_evaluacion', 'fecha_de_entrega', 'tema_general', 'descripcion']
        widgets = {
            'tipo_evaluacion': forms.TextInput(attrs={
                'placeholder': 'Tipo de evaluación'
            },
            ),
            'fecha_de_entrega': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'placeholder': 'Fecha de entrega'
            },
            format='%Y-%m-%dT%H:%M',
            ),
            'tema_general': forms.TextInput(attrs={
                'placeholder': 'Tema general (opcional)'
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Descripción (opcional)',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'fecha_de_entrega':
                field.label = ''
        
        if self.instance and self.instance.fecha_de_entrega:
            self.initial['fecha_de_entrega'] = self.instance.fecha_de_entrega.strftime('%Y-%m-%dT%H:%M')
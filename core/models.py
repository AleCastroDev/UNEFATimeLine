from django.db import models
from django.contrib.auth.models import AbstractBaseUser,  PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password, is_password_usable

# ─── Usuario Personalizado ───────────────────────────────────────────────

class AlumnoManager(BaseUserManager):
    def create_user(self, cedula, nombre, password=None, **extra_fields):
        if not cedula:
            raise ValueError("El usuario debe tener una cédula")
        if not nombre:
            raise ValueError("El usuario debe tener un nombre")

        user = self.model(cedula=cedula, nombre=nombre, **extra_fields)
        user.set_password(password or "123")  # ⚠️ Establece contraseña por defecto aquí
        user.save()
        return user
    def create_superuser(self, cedula, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(cedula, nombre, password, **extra_fields)

class Alumno(AbstractBaseUser, PermissionsMixin):
    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100) 

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)

    USERNAME_FIELD = 'cedula'
    REQUIRED_FIELDS = ['nombre']  # ← también aquí

    objects = AlumnoManager()

    def __str__(self):
        return f"{self.nombre} - {self.cedula}"

# ─── Modelos Académicos ─────────────────────────────────────────────────

class Profesor(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    is_coor = models.BooleanField(default=False)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
    # Evita doble hasheo: solo hashea si no comienza con 'pbkdf2_' u otro marcador de hash
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.cedula} {'(Coordinador)' if self.is_coor else ''}"

class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    id_coor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, related_name='carreras_coordinadas')
    svg_icono = models.TextField(help_text="Pega aquí el código SVG del icono")

    def __str__(self):
        return self.nombre

class Semestre(models.Model):
    numero = models.IntegerField()
    id_carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='semestres')

    def __str__(self):
        return f"Semestre {self.numero} - {self.id_carrera.nombre}"

class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    id_semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, related_name='materias')
    id_profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, blank=True, related_name='materias_asignadas')
    svg_icono = models.TextField(help_text="Pega aquí el código SVG del icono")

    def __str__(self):
        return self.nombre

class Inscripcion(models.Model):
    id_alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='inscripciones')
    id_materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='inscripciones')

    def __str__(self):
        return f"{self.id_alumno.cedula} en {self.id_materia.nombre}"

class Asignatura(models.Model):
    tipo_evaluacion = models.CharField(max_length=15)
    id_materia = models.ForeignKey('Materia', on_delete=models.CASCADE, related_name='asignaturas')
    fecha_de_creacion = models.DateTimeField(auto_now_add=True)
    fecha_de_entrega = models.DateTimeField()
    tema_general = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.id_materia} - {self.tipo_evaluacion}'
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import *
from .models import * 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from collections import defaultdict
from django.utils import timezone
from django.db.models import DateField
from django.db.models.functions import Cast
from babel.dates import format_datetime
from calendar import monthrange
from django.contrib.auth.hashers import check_password

def get_first_name(full_name):
        return full_name.split()[0] if full_name else ''

def welcome(request):
    if request.user.is_authenticated:
        return redirect('inicio') 
    return render(request, 'index.html')

def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
                cedula = form.cleaned_data['cedula']
                nombre = form.cleaned_data['nombre']
                
                if Alumno.objects.filter(cedula=cedula).exists():
                    messages.error(request, "Esta cédula ya está registrada.")

                elif len(cedula) < 6 or len(cedula) > 8:
                    messages.error(request, "La cédula debe tener entre 6 y 8 dígitos.")
                
                elif not cedula.isdigit():
                    messages.error(request, "La cédula solo puede contener números.")

                elif any(char.isdigit() for char in nombre):
                    messages.error(request, "El nombre no puede contener números.")

                elif len(nombre.strip()) < 7:
                    messages.error(request, "El nombre debe tener al menos 7 caracteres.")

                else:
                    usuario = Alumno.objects.create_user(cedula=cedula, nombre=nombre)
                    login(request, usuario)
                    return redirect('profile')
    else:
        form = AlumnoForm()
    return render(request, 'account/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['cedula']
            password = form.cleaned_data['password']
            user = authenticate(request, cedula=cedula, password=password)
            if user:
                login(request, user)
                return redirect('inicio')
            else:
                messages.error(request, 'Cédula no registrada')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

def login_prof_view(request):
    if request.method == 'POST':
        form = ProfesorLoginForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['cedula']
            password = form.cleaned_data['password']
            try:
                profesor = Profesor.objects.get(cedula=cedula)
                if check_password(password, profesor.password):
                    request.session['profesor_id'] = profesor.id
                    return redirect('inicio_prof')
                else:
                    messages.error(request, 'Contraseña incorrecta.')
            except Profesor.DoesNotExist:
                messages.error(request, 'Cédula no registrada.')
    else:
        form = ProfesorLoginForm()

    return render(request, 'account/login_prof.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user

    nombre_completo = user.nombre
    cedula = getattr(user, 'cedula')  # ajusta si se llama distinto

    name_form = UpdateNameForm(initial={'nombre': getattr(user, 'nombre', '')})
    cedula_form = UpdateCedulaForm(initial={'cedula': getattr(user, 'cedula', '')})
    
    if request.method == 'POST':
        if 'update_name' in request.POST:
            name_form = UpdateNameForm(request.POST)
            if name_form.is_valid():
                user.nombre = name_form.cleaned_data['nombre']

                if any(char.isdigit() for char in user.nombre):
                    messages.error(request, "El nombre no puede contener números.", extra_tags='name')

                elif len(user.nombre.strip()) < 7:
                    messages.error(request, "El nombre debe tener al menos 7 caracteres.", extra_tags='name')

                else:
                    user.save()
                    return redirect('profile')
        
        if 'update_cedula' in request.POST:
            cedula_form = UpdateCedulaForm(request.POST)
            if cedula_form.is_valid():
                user.cedula = cedula_form.cleaned_data['cedula']

                if Alumno.objects.filter(cedula=cedula).exists():
                    messages.error(request, "Esta cédula ya está registrada.", extra_tags='cedula')

                elif len(cedula) < 6 or len(cedula) > 8:
                    messages.error(request, "La cédula debe tener entre 6 y 8 dígitos.", extra_tags='cedula')
                
                elif not cedula.isdigit():
                    messages.error(request, "La cédula solo puede contener números.", extra_tags='cedula')

                else:
                    user.save()
                    return redirect('profile')

    materias_inscritas = Materia.objects.filter(inscripciones__id_alumno=user).order_by('nombre')
    carreras = Carrera.objects.all().order_by('nombre')

    contexto = {
        'nombre_completo': nombre_completo,
        'cedula': cedula,
        'primer_nombre': get_first_name(nombre_completo),
        'name_form': name_form,
        'cedula_form': cedula_form,
        'materias': materias_inscritas,
        'carreras': carreras,
    }

    return render(request, 'profile.html', contexto)

def profile_prof_view(request):
    # if not request.session.get('profesor_id'):
    #     return redirect('login_prof')
    profesor = Profesor.objects.get(id=request.session['profesor_id'])

    nombre_completo = profesor.nombre
    cedula = profesor.cedula

    name_form = UpdateNameForm(initial={'nombre': profesor.nombre})
    asignaturas = Asignatura.objects.filter(id_materia__id_profesor=profesor).select_related('id_materia').order_by('fecha_de_entrega')
    cedula_form = UpdateCedulaForm(initial={'cedula': profesor.cedula})
    
    if request.method == 'POST':
        if 'update_name' in request.POST:
            name_form = UpdateNameForm(request.POST)
            if name_form.is_valid():
                nuevo_nombre = name_form.cleaned_data['nombre']
                if any(char.isdigit() for char in nuevo_nombre):
                    messages.error(request, "El nombre no puede contener números.", extra_tags='name')
                elif len(nuevo_nombre.strip()) < 7:
                    messages.error(request, "El nombre debe tener al menos 7 caracteres.", extra_tags='name')
                else:
                    profesor.nombre = nuevo_nombre
                    profesor.save()
                    return redirect('profile_prof')

        if 'update_cedula' in request.POST:
            cedula_form = UpdateCedulaForm(request.POST)
            if cedula_form.is_valid():
                nueva_cedula = cedula_form.cleaned_data['cedula']
                if Profesor.objects.filter(cedula=nueva_cedula).exclude(id=profesor.id).exists():
                    messages.error(request, "Esta cédula ya está registrada.", extra_tags='cedula')
                elif len(nueva_cedula) < 6 or len(nueva_cedula) > 8:
                    messages.error(request, "La cédula debe tener entre 6 y 8 dígitos.", extra_tags='cedula')
                elif not nueva_cedula.isdigit():
                    messages.error(request, "La cédula solo puede contener números.", extra_tags='cedula')
                else:
                    profesor.cedula = nueva_cedula
                    profesor.save()
                    return redirect('profile_prof')

    materias = Materia.objects.filter(id_profesor__cedula=profesor.cedula).order_by('nombre')
    carreras = Carrera.objects.filter(semestres__materias__id_profesor__cedula=profesor.cedula).distinct().order_by('nombre')

    contexto = {
        'nombre_completo': nombre_completo,
        'cedula': cedula,
        'primer_nombre': get_first_name(nombre_completo),
        'name_form': name_form,
        'cedula_form': cedula_form,
        'materias': materias,
        'carreras': carreras,
        'asignaturas': asignaturas,
    }

    return render(request, 'profile_prof.html', contexto)

@login_required
def eliminar_inscripcion(request, id_materia):
    inscripcion = get_object_or_404(
        Inscripcion,
        id_alumno=request.user,
        id_materia__id=id_materia
    )
    inscripcion.delete()
    return redirect('profile')

@login_required
def custom_logout_view(request):
    logout(request) 
    return redirect('welcome') 

@login_required
def obtener_semestres_por_carrera(request, carrera_id):
    semestres = Semestre.objects.filter(id_carrera_id=carrera_id).order_by('numero')
    datos = [
        {
            'id': s.id,
            'numero': s.numero,
            'materias_count': s.materias.count()  # ← Conteo de materias
        }
        for s in semestres
    ]
    return JsonResponse({'semestres': datos})

@login_required
def obtener_materias_por_semestre(request, semestre_id):
    materias = Materia.objects.filter(id_semestre_id=semestre_id).order_by('nombre')
    datos = [
        {
            'id': m.id,
            'nombre': m.nombre,
            'profesor': m.id_profesor.nombre if m.id_profesor else "Sin asignar",
            'svg_icono': m.svg_icono
        }
        for m in materias
    ]
    return JsonResponse({'materias': datos})

@login_required
@require_POST
def inscribir_materia(request):
    materia_id = request.POST.get('materia_id')
    if not materia_id:
        return JsonResponse({'error': 'ID de materia no proporcionado'}, status=400)

    try:
        materia = Materia.objects.get(id=materia_id)
        Inscripcion.objects.get_or_create(id_alumno=request.user, id_materia=materia)
        return JsonResponse({'ok': True})
    except Materia.DoesNotExist:
        return JsonResponse({'error': 'Materia no encontrada'}, status=404)
    
@login_required
def calendario(request):
    contexto = {
        'primer_nombre': get_first_name(request.user.nombre),
    }
    return render(request, 'calendario.html', contexto)

@login_required
def tareas_usuario_json(request):
    try:
        alumno = request.user

        # Obtener materias del alumno
        materias_ids = Inscripcion.objects.filter(id_alumno=alumno).values_list('id_materia_id', flat=True)

        # Asignaturas asociadas a esas materias
        asignaturas = Asignatura.objects.filter(id_materia__in=materias_ids)

        # Filtrar por rango de fechas si se reciben desde FullCalendar
        start = request.GET.get('start')
        end = request.GET.get('end')
        if start and end:
            start = datetime.fromisoformat(start)
            end = datetime.fromisoformat(end)
            asignaturas = asignaturas.filter(fecha_de_entrega__range=(start, end))

        # Agrupar tareas por fecha
        conteo_por_fecha = defaultdict(int)
        tareas_detalladas = defaultdict(list)

        for asignatura in asignaturas:
            if asignatura.fecha_de_entrega:
                fecha = asignatura.fecha_de_entrega.date().isoformat()
                conteo_por_fecha[fecha] += 1

                tareas_detalladas[fecha].append({
                    "tipo_evaluacion": asignatura.tipo_evaluacion,
                    "descripcion": asignatura.descripcion,
                    "materia": asignatura.id_materia.nombre,
                    "fecha_de_entrega": asignatura.fecha_de_entrega,
                    "tema_general": asignatura.tema_general,
                    "descripcion": asignatura.descripcion,
                })

        # Formato para el calendario (solo números por día)
        eventos = [
            {
                "title": str(cantidad),
                "start": fecha,
                "allDay": True
            }
            for fecha, cantidad in conteo_por_fecha.items()
        ]

        # Respuesta combinada
        return JsonResponse({
            "eventos": eventos,
            "tareas_por_dia": tareas_detalladas,
        })

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500) 

@login_required
def home(request):
    hoy = timezone.localtime(timezone.now())
    materias_usuario = Inscripcion.objects.filter(id_alumno=request.user).values_list('id_materia', flat=True)
    tareas_hoy = Asignatura.objects.annotate(
        fecha=Cast('fecha_de_entrega', output_field=DateField())
    ).filter(
        fecha=hoy,
        id_materia__in=materias_usuario
    )

    materias_dict = defaultdict(lambda: {
        'svg_icono': '',
        'nombre': '',
        'profesor': '',
        'cantidad': 0,
        'tareas': []
    })

    for tarea in tareas_hoy:
        materia_id = tarea.id_materia.id
        materia_info = materias_dict[materia_id]
        materia_info['svg_icono'] = tarea.id_materia.svg_icono
        materia_info['nombre'] = tarea.id_materia.nombre
        materia_info['profesor'] = tarea.id_materia.id_profesor.nombre
        materia_info['cantidad'] += 1
        materia_info['tareas'].append({
            'titulo': tarea.tipo_evaluacion,
            'tema_general': tarea.tema_general,
            'descripcion': tarea.descripcion,
            'hora': tarea.fecha_de_entrega.strftime('%I:%M%p') if tarea.fecha_de_entrega else '',
        })
        materia_info['tareas'].sort(key=lambda t: (t['hora']))

    contexto = {
        'primer_nombre': get_first_name(request.user.nombre),
        'total_tareas_hoy': tareas_hoy.count(),
        'materias_con_tareas': materias_dict.values()
    }

    return render(request, 'home.html', contexto)

@login_required
def home_semana(request):
    hoy = timezone.localtime(timezone.now())
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    # Obtener materias del usuario
    materias_usuario = Inscripcion.objects.filter(
        id_alumno=request.user
    ).values_list('id_materia', flat=True)

    # Tareas solo de materias en las que el usuario está inscrito
    tareas = Asignatura.objects.annotate(
        fecha=Cast('fecha_de_entrega', output_field=DateField())
    ).filter(
        fecha__range=(inicio_semana, fin_semana),
        id_materia__in=materias_usuario
    )

    materias_dict = defaultdict(lambda: {
        'svg_icono': '',
        'nombre': '',
        'profesor': '',
        'cantidad': 0,
        'tareas': []
    })

    for tarea in tareas:
        materia = tarea.id_materia
        materia_info = materias_dict[materia.id]
        materia_info['svg_icono'] = materia.svg_icono
        materia_info['nombre'] = materia.nombre
        materia_info['profesor'] = materia.id_profesor.nombre
        materia_info['cantidad'] += 1
        materia_info['tareas'].append({
            'titulo': tarea.tipo_evaluacion,
            'tema_general': tarea.tema_general,
            'descripcion': tarea.descripcion,
            'hora': tarea.fecha_de_entrega.strftime('%I:%M%p') if tarea.fecha_de_entrega else '',
            'fecha': format_datetime(tarea.fecha_de_entrega, "EEEE d", locale='es') if tarea.fecha_de_entrega else '',
            'fecha_de_entrega': tarea.fecha_de_entrega.date() if tarea.fecha_de_entrega else None,
        })

        materia_info['tareas'].sort(key=lambda t: (t['fecha_de_entrega'], t['hora']))

    contexto = {
        'primer_nombre': get_first_name(request.user.nombre),
        'total_tareas_hoy': tareas.count(),
        'materias_con_tareas': materias_dict.values(),
        'hoy': hoy.date(),
    }

    return render(request, 'home_semana.html', contexto)

@login_required
def home_mes(request):
    hoy = timezone.localtime(timezone.now())
    primer_dia_mes = hoy.replace(day=1)
    ultimo_dia_mes = hoy.replace(day=monthrange(hoy.year, hoy.month)[1])

    # Materias en las que el alumno está inscrito
    materias_usuario = Inscripcion.objects.filter(
        id_alumno=request.user
    ).values_list('id_materia', flat=True)

    # Tareas solo de esas materias
    tareas = Asignatura.objects.annotate(
        fecha=Cast('fecha_de_entrega', output_field=DateField())
    ).filter(
        fecha__range=(primer_dia_mes, ultimo_dia_mes),
        id_materia__in=materias_usuario
    )

    materias_dict = defaultdict(lambda: {
        'svg_icono': '',
        'nombre': '',
        'profesor': '',
        'cantidad': 0,
        'tareas': []
    })

    for tarea in tareas:
        materia = tarea.id_materia
        materia_info = materias_dict[materia.id]
        materia_info['svg_icono'] = materia.svg_icono
        materia_info['nombre'] = materia.nombre
        materia_info['profesor'] = materia.id_profesor.nombre
        materia_info['cantidad'] += 1
        materia_info['tareas'].append({
            'titulo': tarea.tipo_evaluacion,
            'tema_general': tarea.tema_general,
            'descripcion': tarea.descripcion,
            'hora': tarea.fecha_de_entrega.strftime('%I:%M%p') if tarea.fecha_de_entrega else '',
            'fecha': format_datetime(tarea.fecha_de_entrega, "EEEE d", locale='es') if tarea.fecha_de_entrega else '',
            'fecha_de_entrega': tarea.fecha_de_entrega.date() if tarea.fecha_de_entrega else None,
        })
        materia_info['tareas'].sort(key=lambda t: (t['fecha_de_entrega'], t['hora']))

    contexto = {
        'primer_nombre': get_first_name(request.user.nombre),
        'total_tareas_hoy': tareas.count(),
        'materias_con_tareas': materias_dict.values(),
        'hoy': hoy.date(),
    }

    return render(request, 'home_mes.html', contexto)

def eliminar_asignatura(request, id_asigantura):
    profesor_id = request.session.get('profesor_id')
    if not profesor_id:
        return redirect('login_prof')

    asignatura = get_object_or_404(
        Asignatura,
        id=id_asigantura,
        id_materia__id_profesor=profesor_id
    )
    asignatura.delete()
    return redirect('profile_prof') 

def editar_asignatura(request, id_asignatura):
    asignatura = get_object_or_404(Asignatura, id=id_asignatura)
    materia = asignatura.id_materia 

    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            return redirect('profile_prof')  # o donde quieras redirigir
    else:
        form = AsignaturaForm(instance=asignatura)

    return render(request, 'asignaturas/crear_asignatura.html', {
        'form': form,
        'modo': 'editar',
        'materia': materia,
        'asignatura': asignatura
    })

def crear_asignatura_view(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)

    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            asignatura = form.save(commit=False)
            asignatura.id_materia = materia
            asignatura.save()
            return redirect('profile_prof')  # Cambia esto si deseas otra página
    else:
        form = AsignaturaForm()

    return render(request, 'asignaturas/crear_asignatura.html', {
        'form': form,
        'materia': materia,
        'primer_nombre': get_first_name(request.user.nombre),
    })

def calendario_prof(request):
    contexto = {
        'primer_nombre': get_first_name(Profesor.objects.get(id=request.session['profesor_id']).nombre),
    }
    return render(request, 'calendario_prof.html', contexto)

def tareas_prof_json(request):
    try:
        profesor_id = request.session.get('profesor_id')
        profesor = Profesor.objects.get(id=profesor_id)
        asignaturas = Asignatura.objects.filter(id_materia__id_profesor=profesor)

        # Filtrar por rango de fechas si se reciben desde FullCalendar
        start = request.GET.get('start')
        end = request.GET.get('end')
        if start and end:
            start = datetime.fromisoformat(start)
            end = datetime.fromisoformat(end)
            asignaturas = asignaturas.filter(fecha_de_entrega__range=(start, end))

        # Agrupar tareas por fecha
        conteo_por_fecha = defaultdict(int)
        tareas_detalladas = defaultdict(list)

        for asignatura in asignaturas:
            if asignatura.fecha_de_entrega:
                fecha = asignatura.fecha_de_entrega.date().isoformat()
                conteo_por_fecha[fecha] += 1

                tareas_detalladas[fecha].append({
                    "tipo_evaluacion": asignatura.tipo_evaluacion,
                    "descripcion": asignatura.descripcion,
                    "materia": asignatura.id_materia.nombre,
                    "fecha_de_entrega": asignatura.fecha_de_entrega.isoformat(),
                    "tema_general": asignatura.tema_general,
                })

        # Formato para el calendario (solo números por día)
        eventos = [
            {
                "title": str(cantidad),
                "start": fecha,
                "allDay": True
            }
            for fecha, cantidad in conteo_por_fecha.items()
        ]

        return JsonResponse({
            "eventos": eventos,
            "tareas_por_dia": tareas_detalladas,
        })

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)

def home_prof(request):
    if not request.session.get('profesor_id'):
        return redirect('login_prof')
    
    hoy = timezone.localtime(timezone.now())
    profesor = Profesor.objects.get(id=request.session['profesor_id'])

    materias_profesor = Materia.objects.filter(id_profesor=profesor)

    tareas_hoy = Asignatura.objects.annotate(
        fecha=Cast('fecha_de_entrega', output_field=DateField())
    ).filter(
        fecha=hoy,
        id_materia__in=materias_profesor
    )

    materias_dict = defaultdict(lambda: {
        'svg_icono': '',
        'nombre': '',
        'profesor': '',
        'semestre': '',
        'carrera': '',
        'cantidad': 0,
        'tareas': []
    })

    for tarea in tareas_hoy:
        materia = tarea.id_materia
        semestre = materia.id_semestre
        carrera = semestre.id_carrera

        materia_info = materias_dict[materia.id]
        materia_info['svg_icono'] = materia.svg_icono
        materia_info['nombre'] = materia.nombre
        materia_info['profesor'] = materia.id_profesor.nombre
        materia_info['semestre'] = semestre.numero
        materia_info['carrera'] = carrera.nombre
        materia_info['cantidad'] += 1
        materia_info['tareas'].append({
            'titulo': tarea.tipo_evaluacion,
            'tema_general': tarea.tema_general,
            'descripcion': tarea.descripcion,
            'hora': tarea.fecha_de_entrega.strftime('%I:%M %p') if tarea.fecha_de_entrega else '',
        })
        materia_info['tareas'].sort(key=lambda t: (t['hora']))

    contexto = {
        'primer_nombre': get_first_name(Profesor.objects.get(id=request.session['profesor_id']).nombre),
        'total_tareas_hoy': tareas_hoy.count(),
        'materias_con_tareas': materias_dict.values()
    }

    return render(request, 'home_prof.html', contexto)

def home_semana_prof(request):
    hoy = timezone.localtime(timezone.now())
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    # Obtener materias del usuario
    if request.session.get('profesor_id'):
        profesor = Profesor.objects.get(id=request.session['profesor_id'])
        materias_usuario = Materia.objects.filter(id_profesor=profesor)

    # Tareas solo de materias en las que el usuario está inscrito
    tareas = Asignatura.objects.annotate(
        fecha=Cast('fecha_de_entrega', output_field=DateField())
    ).filter(
        fecha__range=(inicio_semana, fin_semana),
        id_materia__in=materias_usuario
    )

    materias_dict = defaultdict(lambda: {
        'svg_icono': '',
        'nombre': '',
        'profesor': '',
        'semestre': '',
        'carrera': '',
        'cantidad': 0,
        'tareas': []
    })

    for tarea in tareas:
        materia = tarea.id_materia
        semestre = materia.id_semestre
        carrera = semestre.id_carrera

        materia_info = materias_dict[materia.id]
        materia_info['svg_icono'] = materia.svg_icono
        materia_info['nombre'] = materia.nombre
        materia_info['profesor'] = materia.id_profesor.nombre
        materia_info['semestre'] = semestre.numero
        materia_info['carrera'] = carrera.nombre
        materia_info['cantidad'] += 1
        materia_info['tareas'].append({
            'titulo': tarea.tipo_evaluacion,
            'tema_general': tarea.tema_general,
            'descripcion': tarea.descripcion,
            'hora': tarea.fecha_de_entrega.strftime('%I:%M %p') if tarea.fecha_de_entrega else '',
            'fecha': format_datetime(tarea.fecha_de_entrega, "EEEE d", locale='es') if tarea.fecha_de_entrega else '',
            'fecha_de_entrega': tarea.fecha_de_entrega.date() if tarea.fecha_de_entrega else None,
        })
        materia_info['tareas'].sort(key=lambda t: (t['fecha_de_entrega'], t['hora']))

    contexto = {
        'primer_nombre': get_first_name(Profesor.objects.get(id=request.session['profesor_id']).nombre),
        'total_tareas_hoy': tareas.count(),
        'materias_con_tareas': materias_dict.values(),
        'hoy': hoy.date(),
    }

    return render(request, 'home_semana_prof.html', contexto)

def home_mes_prof(request):
    hoy = timezone.localtime(timezone.now())
    primer_dia_mes = hoy.replace(day=1)
    ultimo_dia_mes = hoy.replace(day=monthrange(hoy.year, hoy.month)[1])

    # Determinar si es profesor o alumno
    if request.session.get('profesor_id'):
        profesor = Profesor.objects.get(id=request.session['profesor_id'])
        materias_usuario = Materia.objects.filter(id_profesor=profesor)

    tareas = Asignatura.objects.annotate(
        fecha=Cast('fecha_de_entrega', output_field=DateField())
    ).filter(
        fecha__range=(primer_dia_mes, ultimo_dia_mes),
        id_materia__in=materias_usuario
    )

    materias_dict = defaultdict(lambda: {
        'svg_icono': '',
        'nombre': '',
        'profesor': '',
        'semestre': '',
        'carrera': '',
        'cantidad': 0,
        'tareas': []
    })

    for tarea in tareas:
        materia = tarea.id_materia
        semestre = materia.id_semestre
        carrera = semestre.id_carrera

        materia_info = materias_dict[materia.id]
        materia_info['svg_icono'] = materia.svg_icono
        materia_info['nombre'] = materia.nombre
        materia_info['profesor'] = materia.id_profesor.nombre
        materia_info['semestre'] = semestre.numero
        materia_info['carrera'] = carrera.nombre
        materia_info['cantidad'] += 1
        materia_info['tareas'].append({
            'titulo': tarea.tipo_evaluacion,
            'tema_general': tarea.tema_general,
            'descripcion': tarea.descripcion,
            'hora': tarea.fecha_de_entrega.strftime('%I:%M %p') if tarea.fecha_de_entrega else '',
            'fecha': format_datetime(tarea.fecha_de_entrega, "EEEE d", locale='es') if tarea.fecha_de_entrega else '',
            'fecha_de_entrega': tarea.fecha_de_entrega.date() if tarea.fecha_de_entrega else None,
        })
        materia_info['tareas'].sort(key=lambda t: (t['fecha_de_entrega'], t['hora']))

    contexto = {
        'primer_nombre': get_first_name(Profesor.objects.get(id=request.session['profesor_id']).nombre),
        'total_tareas_hoy': tareas.count(),
        'materias_con_tareas': materias_dict.values(),
        'hoy': hoy.date(),
    }

    return render(request, 'home_mes_prof.html', contexto)
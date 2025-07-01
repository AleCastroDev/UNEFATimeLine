document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    const tareasEl = document.getElementById('task_container'); // <-- contenedor donde mostrarás las tareas

    if (calendarEl) {
        const calendar = new window.FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            buttonText: {
                today: 'Hoy'
            },
            headerToolbar: {
                left: 'title',
                center: '',
                right: 'today prev,next'
            },
            titleFormat: {
                year: 'numeric',
                month: 'short'
            },
            events: function (fetchInfo, successCallback, failureCallback) {
                fetch(`/api/tareas/?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`)
                    .then(res => res.json())
                    .then(data => {
                        // Renderizar tareas detalladas abajo
                        
                        if (data.tareas_por_dia) {
                            renderizarListaDetallada(data.tareas_por_dia);
                        }
                        successCallback(data.eventos);
                    })
                    .catch(err => {
                        console.error("Error cargando eventos:", err);
                        failureCallback(err);
                    });
            },
            eventContent: function (arg) {
                return {
                    domNodes: [customEventElement(arg)]
                };
            },
        });

        window.addEventListener('load', () => {
            calendar.render();
        });
    } 
    
    // Personalizar cómo se muestra el número de tareas en el calendario
    function customEventElement(arg) {
        const div = document.createElement('div');
        div.innerText = arg.event.title;
        div.classList.add('evento-tarea-cantidad');
        return div;
    }

    // Mostrar las tareas detalladas agrupadas por día
    function renderizarListaDetallada(tareasPorDia) {
        if (!tareasEl) {
            return;
        }

        tareasEl.innerHTML = ''; // Limpiar contenido anterior

        const titulo = document.querySelector('.fc-toolbar-title');
        if (!titulo) {
            return;
        }

        const partes = titulo.textContent.trim().toLowerCase().replace('.', '').split(' ').filter(p => p !== 'de');
        const mesVisible = partes[0];
        const añoVisible = parseInt(partes[1]);

        const nombresMes = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

        const indiceMesVisible = nombresMes.indexOf(mesVisible);

        if (indiceMesVisible === -1 || isNaN(añoVisible)) {
            return;
        }

        function closeModal() {
            document.getElementById('modal').classList.remove('active');
            document.querySelector('.shadow').classList.remove('active');
            document.querySelector('body').classList.remove('no-scroll');
        }

        Object.keys(tareasPorDia).sort().forEach(fecha => {
            const [year, month, day] = fecha.split('-');
            const fechaObj = new Date(year, month - 1, day);

            if (fechaObj.getFullYear() === añoVisible && fechaObj.getMonth() === indiceMesVisible) {

                const tareas = tareasPorDia[fecha];

                const nombreDia = fechaObj.toLocaleDateString('es-ES', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long'
                });

                const hoy = new Date();
                hoy.setHours(0, 0, 0, 0);
                const todasPasadas = tareas.every(t => new Date(t.fecha_de_entrega) < hoy);

                const h3 = document.createElement('h3');
                h3.innerHTML = `${nombreDia.charAt(0).toUpperCase() + nombreDia.slice(1)} <span class="badge">${tareas.length}</span>`;
                if (todasPasadas) {
                    h3.classList.add('tarea-pasada');
                }
                tareasEl.appendChild(h3);

                tareas.forEach(t => {
                    const div = document.createElement('div');
                    div.classList.add('tarea-card');

                    // Evaluar si es una tarea pasada
                    const fechaEntrega = new Date(t.fecha_de_entrega);
                    const hoy = new Date();
                    hoy.setHours(0, 0, 0, 0); // Eliminar hora para comparar solo fecha

                    if (fechaEntrega < hoy) {
                        div.classList.add('tarea-pasada'); // Le das opacidad
                    }

                    div.innerHTML = `
                        <strong>${t.tipo_evaluacion}</strong>
                        <p>${t.materia}</p>
                        <small>
                            ${new Date(t.fecha_de_entrega).toLocaleTimeString('es-ES', {
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: true
                            })}
                         </small>
                    `;

                    if ((t.descripcion && t.descripcion.trim() !== '') || (t.tema_general && t.tema_general.trim() !== '')) {
                        const extraInfo = document.createElement('div');
                        extraInfo.classList.add('info-extra');
                        extraInfo.innerHTML = `
                            <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" viewBox="0 0 512 512" data-tema="${t.tema || ''}" data-descripcion="${t.descripcion || ''}">  <!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/></svg>
                        `;

                        const svg = extraInfo.querySelector('.info-icon');
                        svg.addEventListener('click', () => {
                            // Siempre se muestra el título del tipo de evaluación
                            document.getElementById('modal-titulo').textContent = t.tipo_evaluacion;
                            document.getElementById('modal-tema').innerHTML = '';
                            document.getElementById('modal-descripcion').innerHTML = '';
                            if (t.tema_general && t.tema_general.trim() !== '') {
                                document.getElementById('modal-tema').innerHTML = `<span>Tema general:</span> ${t.tema_general}`;
                            }
                            if (t.descripcion && t.descripcion.trim() !== '') {
                                document.getElementById('modal-descripcion').innerHTML = `<span>Descripción:</span> ${t.descripcion}`;
                            }
                            document.getElementById('modal').classList.add('active');
                            document.querySelector('.shadow').classList.add('active');
                            document.body.classList.add('no-scroll');
                            document.querySelector('.shadow').addEventListener('click', closeModal, { once: true });
                        });

                        div.appendChild(extraInfo);
                    }
                    tareasEl.appendChild(div);
                });
            }
        });
    }
});

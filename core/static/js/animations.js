document.addEventListener('DOMContentLoaded', () => {
    const shadow = document.getElementById('shadow');
    const body = document.body;
    let activeModal = null;

    // Abre cualquier modal desde botones con data-target
    document.querySelectorAll('[data-target]').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const targetSelector = trigger.getAttribute('data-target');
            const modal = document.querySelector(targetSelector);

            if (targetSelector === '#deleteModal') {
                const materiaId = trigger.getAttribute('data-id');
                const form = document.getElementById('deleteForm');
                if (form && materiaId) {
                    form.action = `/eliminar-inscripcion/${materiaId}/`;
                }
            }
            
            if (modal) {
                modal.classList.add('active');
                shadow.classList.add('active');
                body.classList.add('no-scroll');
                activeModal = modal;
            }
        });
    });

    // Función para cerrar el modal
    function closeModal() {
        if (activeModal) {
            activeModal.classList.remove('active');
            shadow.classList.remove('active');
            body.classList.remove('no-scroll');
            activeModal = null;
        }
    }

    // Cerrar al hacer click en la sombra o en botones de cancelar
    shadow.addEventListener('click', closeModal);

    document.querySelectorAll('.btn-cancel, .btn-secondary').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal();
        });
    });

    document.querySelectorAll('.open-semestres').forEach(btn => {
        btn.addEventListener('click', () => {
            const carreraId = btn.getAttribute('data-id');
            const modal = document.querySelector('#semestreModal');
            const container = document.getElementById('semestreContainer');

            const modalCarreras = document.querySelector('#carrerasModal');
            if (modalCarreras.classList.contains('active')) {
                modalCarreras.classList.remove('active');
            }

            // Limpiar contenido anterior
            container.innerHTML = '<p>Cargando semestres...</p>';

            // Hacer solicitud AJAX a Django
            fetch(`/api/semestres/${carreraId}/`)
                .then(res => res.json())
                .then(data => {
                    container.innerHTML = ''; // Limpiar después de recibir respuesta
                    data.semestres.forEach(semestre => {
                        const card = document.createElement('div');
                        card.classList.add('semestre_card');
                        card.setAttribute('data-target', '#materiaModal');
                        card.setAttribute('data-id', semestre.id);
                        card.innerHTML = `<div class="txt"><h3>${semestre.numero}</h3><p>${semestre.materias_count} mat.</p></div>`;
                        container.appendChild(card);
                    });
                })
                .catch(err => {
                    container.innerHTML = '<p>Error al cargar semestres.</p>';
                    console.error(err);
                });
        });
    });
    

    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.semestre_card');
        if (!btn) return;

        const semestreId = btn.getAttribute('data-id');
        const modal = document.querySelector('#materiasModal');
        const container = document.getElementById('materiasContainer');

        // Cerrar el modal de semestres si está abierto
        const modalSemestres = document.querySelector('#semestreModal');
        if (modalSemestres.classList.contains('active')) {
            modalSemestres.classList.remove('active');
        }

        // Mostrar el modal de materias
        modal.classList.add('active');
        shadow.classList.add('active');
        body.classList.add('no-scroll');
        activeModal = modal;

        // Limpiar contenido anterior
        container.innerHTML = '<p>Cargando materias...</p>';

        // Hacer solicitud AJAX
        fetch(`/api/materias/${semestreId}/`)
            .then(res => res.json())
            .then(data => {
                container.innerHTML = '';
                if (data.materias.length === 0) {
                    container.innerHTML = '<p>No hay materias disponibles.</p>';
                } else {
                    data.materias.forEach(materia => {
                        const card = document.createElement('div');
                        card.classList.add('materias_modal_card');

                        card.innerHTML = `
                            <div class="icon">
                                ${materia.svg_icono}
                            </div>
                            <div class="txt">
                                <h3>${materia.nombre}</h3>
                                <p><span>Profesor: </span>${materia.profesor}</p>
                            </div>
                            <div class="add">
                                <svg data-target="#semestreModal" data-id="${materia.id}" class="open-materias"
                                    xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                                    <path d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 144L48 224c-17.7 0-32 14.3-32 32s14.3 32 
                                    32 32l144 0 0 144c0 17.7 14.3 32 32 32s32-14.3 32-32l0-144 144 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-144 
                                    0 0-144z"/>
                                </svg>
                            </div>
                        `;

                        container.appendChild(card);
                    });
                }
            })
            .catch(err => {
                container.innerHTML = '<p>Error al cargar materias.</p>';
                console.error(err);
            });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // ¿La cookie comienza con el nombre que queremos?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.querySelector('#materiasModal').addEventListener('click', function (e) {
        const svg = e.target.closest('.add svg');
        if (!svg) return;

        const materiaId = svg.getAttribute('data-id');
        if (!materiaId) return;

        fetch('/api/inscribir/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `materia_id=${materiaId}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                window.location.href = '/profile'; // Redirige a la misma página
            } else {
                alert('Error al inscribirse: ' + (data.error || 'Desconocido'));
            }
        })
        .catch(err => {
            console.error('Error al inscribir:', err);
            alert('Ocurrió un error al inscribirse');
        });
    });
});

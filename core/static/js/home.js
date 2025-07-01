document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.info-extra').forEach(el => {
        el.addEventListener('click', () => {
            const titulo = el.getAttribute('data-titulo');
            const tema = el.getAttribute('data-tema');
            const descripcion = el.getAttribute('data-descripcion');

            document.getElementById('modal-titulo').textContent = titulo;
            document.getElementById('modal-tema').innerHTML = '';
            document.getElementById('modal-descripcion').innerHTML = '';

            if (tema && tema.trim() !== '') {
                document.getElementById('modal-tema').innerHTML = `<span>Tema general:</span> ${tema}`;
            }
            if (descripcion && descripcion.trim() !== '') {
                document.getElementById('modal-descripcion').innerHTML = `<span>Descripción:</span> ${descripcion}`;
            }

            document.getElementById('modal').classList.add('active');
            document.querySelector('.shadow').classList.add('active');
            document.body.classList.add('no-scroll');

            document.querySelector('.shadow').addEventListener('click', closeModal, { once: true });
        });
    });
});

function closeModal() {
    document.getElementById('modal').classList.remove('active');
    document.querySelector('.shadow').classList.remove('active');
    document.body.classList.remove('no-scroll');
}
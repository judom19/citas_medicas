document.addEventListener('DOMContentLoaded', function() {
    // Espera a que la página se cargue completamente
    setTimeout(function() {
        var contentContainer = document.querySelector('.container-transition');
        contentContainer.classList.add('show'); // Agrega la clase "show" para activar la transición
    }, 75); // Agrega un retraso de 100 ms para asegurarse de que se aplique después de la carga completa
});

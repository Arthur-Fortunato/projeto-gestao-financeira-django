document.addEventListener("DOMContentLoaded", function () {
    const reveals = document.querySelectorAll(".reveal");

    const observador = new IntersectionObserver((entradas) => {
        entradas.forEach(entrada => {
            if (entrada.isIntersecting) {
                entrada.target.classList.add("active");
            }
        });
    }, {
        threshold: 0.2
    });

    reveals.forEach(reveal => {
        observador.observe(reveal);
    });
});
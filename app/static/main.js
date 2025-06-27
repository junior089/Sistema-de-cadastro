// main.js - JS global para Mutirão Mulher Rural
// Exemplo: fechar mensagens flash automaticamente
window.addEventListener("DOMContentLoaded", function () {
  setTimeout(function () {
    document.querySelectorAll(".flash-message").forEach(function (el) {
      el.style.display = "none";
    });
  }, 4000);
});

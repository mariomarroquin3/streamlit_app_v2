/**
 * app.js
 * Comportamiento compartido entre todas las páginas: modo oscuro persistente
 * y menú de navegación móvil. No depende de ningún framework.
 */
(function () {
  "use strict";

  const root = document.documentElement;
  const toggle = document.getElementById("themeToggle");
  const STORAGE_KEY = "retinovision-theme";

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (toggle) {
      toggle.setAttribute("aria-pressed", String(theme === "dark"));
      toggle.setAttribute(
        "aria-label",
        theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"
      );
    }
  }

  function initTheme() {
    let stored = null;
    try {
      stored = localStorage.getItem(STORAGE_KEY);
    } catch (err) {
      /* almacenamiento no disponible: se ignora silenciosamente */
    }
    if (stored === "light" || stored === "dark") {
      applyTheme(stored);
      return;
    }
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(prefersDark ? "dark" : "light");
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      try {
        localStorage.setItem(STORAGE_KEY, next);
      } catch (err) {
        /* almacenamiento no disponible: se ignora silenciosamente */
      }
    });
  }

  initTheme();

  // --- Menú móvil ---
  const burger = document.getElementById("navBurger");
  const mobileNav = document.getElementById("mobileNav");
  if (burger && mobileNav) {
    burger.addEventListener("click", function () {
      const isOpen = mobileNav.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", String(isOpen));
      burger.classList.toggle("is-open", isOpen);
    });
    mobileNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        mobileNav.classList.remove("is-open");
        burger.setAttribute("aria-expanded", "false");
      });
    });
  }
})();

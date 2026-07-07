document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const toggleBtn = document.getElementById("sidebarToggle");

  function openSidebar() {
    sidebar && sidebar.classList.add("open");
    overlay && overlay.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function closeSidebar() {
    sidebar && sidebar.classList.remove("open");
    overlay && overlay.classList.remove("open");
    document.body.style.overflow = "";
  }

  if (toggleBtn && sidebar && overlay) {
    toggleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      sidebar.classList.contains("open") ? closeSidebar() : openSidebar();
    });
    overlay.addEventListener("click", closeSidebar);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && sidebar.classList.contains("open")) closeSidebar();
    });
  }

  document.querySelectorAll(".table-wrap table").forEach(table => {
    const headers = [];
    table.querySelectorAll("thead th").forEach(th => headers.push(th.textContent.trim()));
    if (!headers.length) return;
    table.querySelectorAll("tbody tr").forEach(row => {
      row.querySelectorAll("td").forEach((td, i) => {
        if (i < headers.length) td.setAttribute("data-label", headers[i]);
      });
    });
  });

  const progressFills = document.querySelectorAll(".progress-fill");
  setTimeout(() => {
    progressFills.forEach(fill => {
      const w = fill.getAttribute("data-fill-width");
      if (w) {
        let pct = parseFloat(w);
        if (isNaN(pct) || pct < 0) pct = 0;
        if (pct > 100) pct = 100;
        fill.style.width = pct + "%";
      }
    });
  }, 150);

  const flashBanner = document.querySelector(".flash-banner");
  if (flashBanner) {
    setTimeout(() => {
      flashBanner.style.transition = "opacity 600ms ease, transform 600ms ease";
      flashBanner.style.opacity = "0";
      flashBanner.style.transform = "translateY(-10px)";
      setTimeout(() => flashBanner.remove(), 600);
    }, 3000);
  }

  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", (e) => {
      const inputs = form.querySelectorAll("input[required], select[required], textarea[required]");
      let valid = true;
      inputs.forEach(input => {
        input.style.borderColor = "";
        if (!input.value.trim()) {
          input.style.borderColor = "var(--danger)";
          valid = false;
        }
      });
      if (!valid) {
        e.preventDefault();
        const first = form.querySelector("[style*='border-color']");
        if (first) first.focus();
      }
    });
  });

  const currentPath = window.location.pathname;
  document.querySelectorAll("[data-nav]").forEach(link => {
    const href = link.getAttribute("href");
    if (href && href !== "#" && currentPath.startsWith(href)) link.classList.add("active");
  });

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    });
  }

  let deferredPrompt = null;
  const installBtn = document.getElementById("installApp");
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) installBtn.hidden = false;
  });
  if (installBtn) {
    installBtn.addEventListener("click", async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      installBtn.hidden = true;
    });
  }
  window.addEventListener("appinstalled", () => {
    deferredPrompt = null;
    if (installBtn) installBtn.hidden = true;
  });

  if ("ontouchstart" in window) document.body.classList.add("touch-device");

  const themeToggle = document.getElementById("themeToggle");
  const themeIcon = document.getElementById("themeIcon");
  const themeLabel = document.getElementById("themeLabel");
  const themeColorMeta = document.getElementById("themeColorMeta");

  function getTheme() { return localStorage.getItem("theme") || "dark"; }

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    if (themeIcon) themeIcon.textContent = theme === "dark" ? "\u2600" : "\u263E";
    if (themeLabel) themeLabel.textContent = theme === "dark" ? "Light" : "Dark";
    if (themeColorMeta) themeColorMeta.content = theme === "dark" ? "#06060e" : "#f4f4f9";
  }

  setTheme(getTheme());

  document.querySelectorAll("[data-theme-toggle]").forEach(btn => {
    btn.addEventListener("click", () => {
      setTheme(getTheme() === "dark" ? "light" : "dark");
    });
  });

  const logoutForm = document.getElementById("logoutForm");
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutForm && logoutBtn) {
    logoutBtn.addEventListener("click", function (e) {
      const exitIntent = sessionStorage.getItem("exitIntent");
      if (exitIntent) {
        sessionStorage.removeItem("exitIntent");
        logoutForm.submit();
        return;
      }
      e.preventDefault();
      sessionStorage.setItem("exitIntent", "true");
      if (location.pathname !== "/dashboard") {
        location.href = "/dashboard";
      } else {
        logoutBtn.innerHTML = '<span class="nav-icon">&#10149;</span> Confirm?';
        setTimeout(() => { logoutBtn.innerHTML = '<span class="nav-icon">&#10149;</span> Sign Out'; }, 3000);
      }
    });
  }
});

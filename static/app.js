document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const toggleBtn = document.getElementById("sidebarToggle");

    function openSidebar() {
        sidebar.classList.add("open");
        overlay.classList.add("open");
        toggleBtn.classList.add("open");
        document.body.style.overflow = "hidden";
    }

    function closeSidebar() {
        sidebar.classList.remove("open");
        overlay.classList.remove("open");
        toggleBtn.classList.remove("open");
        document.body.style.overflow = "";
    }

    if (toggleBtn && sidebar && overlay) {
        toggleBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (sidebar.classList.contains("open")) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
        overlay.addEventListener("click", closeSidebar);
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && sidebar.classList.contains("open")) {
                closeSidebar();
            }
        });
    }

    document.querySelectorAll(".table-container table").forEach(table => {
        const headers = [];
        table.querySelectorAll("thead th").forEach(th => {
            headers.push(th.textContent.trim());
        });
        if (headers.length === 0) return;
        const rows = table.querySelectorAll("tbody tr");
        rows.forEach(row => {
            const cells = row.querySelectorAll("td");
            cells.forEach((td, idx) => {
                if (idx < headers.length) {
                    td.setAttribute("data-label", headers[idx]);
                }
            });
        });
    });

    const flashBanner = document.querySelector(".alert");
    if (flashBanner) {
        setTimeout(() => {
            flashBanner.style.transition = "opacity 600ms ease, transform 600ms ease";
            flashBanner.style.opacity = "0";
            flashBanner.style.transform = "translateY(-10px)";
            setTimeout(() => { flashBanner.remove(); }, 600);
        }, 3000);
    }

    document.querySelectorAll("form").forEach(form => {
        const inputs = form.querySelectorAll("input[required], select[required], textarea[required]");
        if (inputs.length === 0) return;
        form.addEventListener("submit", (e) => {
            let valid = true;
            inputs.forEach(input => {
                input.style.borderColor = "";
                if (!input.value.trim()) {
                    input.style.borderColor = "var(--danger, #b91c1c)";
                    valid = false;
                }
            });
            if (!valid) {
                e.preventDefault();
                const firstInvalid = form.querySelector("[style*='border-color']");
                if (firstInvalid) firstInvalid.focus();
            }
        });
    });

    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker.register("/sw.js").catch(() => {});
        });
    }

    if ("ontouchstart" in window) {
        document.body.classList.add("touch-device");
    }

    const themeIcon = document.getElementById("themeIcon");
    const themeLabel = document.getElementById("themeLabel");

    const sunSvg = '<svg viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg>';
    const moonSvg = '<svg viewBox="0 0 24 24"><path d="M20 8.69V4h-4.69L12 .69 8.69 4H4v4.69L.69 12 4 15.31V20h4.69L12 23.31 15.31 20H20v-4.69L23.31 12 20 8.69zM12 18V6c3.31 0 6 2.69 6 6s-2.69 6-6 6z"/></svg>';

    function getTheme() {
        return localStorage.getItem("theme") || "dark";
    }

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("theme", theme);
        if (themeIcon) themeIcon.innerHTML = theme === "dark" ? sunSvg : moonSvg;
        if (themeLabel) themeLabel.textContent = theme === "dark" ? "Light" : "Dark";
        const meta = document.getElementById("themeColorMeta");
        if (meta) meta.content = theme === "dark" ? "#000000" : "#f0f4f8";
    }

    setTheme(getTheme());

    document.querySelectorAll("[data-theme-toggle]").forEach(btn => {
        btn.addEventListener("click", () => {
            const current = getTheme();
            setTheme(current === "dark" ? "light" : "dark");
        });
    });

    const exitForm = document.querySelector("form.logout-form");
    if (exitForm) {
        const exitBtn = exitForm.querySelector("button[data-exit]");
        if (exitBtn) {
            exitBtn.addEventListener("click", function (e) {
                const exitIntent = sessionStorage.getItem("exitIntent");
                if (exitIntent) {
                    sessionStorage.removeItem("exitIntent");
                    exitForm.submit();
                    return;
                }
                e.preventDefault();
                sessionStorage.setItem("exitIntent", "true");
                if (location.pathname !== "/dashboard") {
                    location.href = "/dashboard";
                } else {
                    const labelSpan = exitBtn.querySelector("span:last-child");
                    labelSpan.textContent = "Confirm Sign Out?";
                    setTimeout(() => { labelSpan.textContent = "Sign Out"; }, 3000);
                }
            });
        }
    }
});

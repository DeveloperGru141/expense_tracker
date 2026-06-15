document.addEventListener("DOMContentLoaded", () => {
    // 1. Sidebar toggle for tablet/mobile
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const toggleBtn = document.getElementById("sidebarToggle");

    function openSidebar() {
        sidebar.classList.add("open");
        overlay.classList.add("open");
        document.body.style.overflow = "hidden";
    }

    function closeSidebar() {
        sidebar.classList.remove("open");
        overlay.classList.remove("open");
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

    // 2. Set data-label attributes on table cells for mobile card layout
    document.querySelectorAll(".table-wrap table").forEach(table => {
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

    // 3. Animate progress bars on load
    const progressFills = document.querySelectorAll(".progress-fill");
    setTimeout(() => {
        progressFills.forEach(fill => {
            const fillWidth = fill.getAttribute("data-fill-width");
            if (fillWidth) {
                let pct = parseFloat(fillWidth);
                if (isNaN(pct)) pct = 0;
                if (pct < 0) pct = 0;
                if (pct > 100) pct = 100;
                fill.style.width = `${pct}%`;
            }
        });
    }, 150);

    // 4. Auto-fade settings save flash banner
    const flashBanner = document.querySelector(".flash-banner");
    if (flashBanner) {
        setTimeout(() => {
            flashBanner.style.transition = "opacity 600ms ease, transform 600ms ease, margin 600ms ease";
            flashBanner.style.opacity = "0";
            flashBanner.style.transform = "translateY(-10px)";
            setTimeout(() => {
                flashBanner.remove();
            }, 600);
        }, 3000);
    }

    // 5. Form validation
    document.querySelectorAll("form.expense-form, form.filter-form").forEach(form => {
        form.addEventListener("submit", (e) => {
            const inputs = form.querySelectorAll("input[required], select[required], textarea[required]");
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

    // 6. Confirm before delete (skip forms with existing onsubmit)
    document.querySelectorAll("form:not([onsubmit])").forEach(form => {
        const deleteBtn = form.querySelector(".delete-button");
        if (deleteBtn) {
            form.addEventListener("submit", (e) => {
                if (!confirm("Are you sure you want to delete this item? This cannot be undone.")) {
                    e.preventDefault();
                }
            });
        }
    });

    // 7. Active nav link -- highlight current page
    const currentPath = window.location.pathname;
    document.querySelectorAll(".nav-link").forEach(link => {
        const href = link.getAttribute("href");
        if (href && href !== "#" && currentPath.startsWith(href)) {
            link.classList.add("active");
        }
    });

    // 8. Chart responsiveness - resize canvas on orientation change
    let resizeTimer;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            document.querySelectorAll("canvas").forEach(canvas => {
                const parent = canvas.parentElement;
                if (parent) {
                    const rect = parent.getBoundingClientRect();
                    canvas.style.width = rect.width + "px";
                    canvas.style.height = "auto";
                }
            });
        }, 250);
    });

    // 9. Register service worker for PWA
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker.register("/sw.js").catch(() => {});
        });
    }

    // 10. PWA install prompt
    let deferredPrompt = null;
    const installBtns = [document.getElementById("installApp"), document.getElementById("installAppMobile")].filter(Boolean);

    window.addEventListener("beforeinstallprompt", (e) => {
        e.preventDefault();
        deferredPrompt = e;
        installBtns.forEach(btn => btn.hidden = false);
    });

    installBtns.forEach(btn => {
        btn.addEventListener("click", async () => {
            if (!deferredPrompt) return;
            deferredPrompt.prompt();
            const result = await deferredPrompt.userChoice;
            deferredPrompt = null;
            installBtns.forEach(b => b.hidden = true);
        });
    });

    window.addEventListener("appinstalled", () => {
        deferredPrompt = null;
        installBtns.forEach(btn => btn.hidden = true);
    });

    // 11. Add touch class for mobile hover fix
    if ("ontouchstart" in window) {
        document.body.classList.add("touch-device");
    }

    // 12. Theme toggle
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const themeLabel = document.getElementById("themeLabel");
    const themeColorMeta = document.getElementById("themeColorMeta");

    function getTheme() {
        return localStorage.getItem("theme") || "dark";
    }

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("theme", theme);
        if (themeIcon) themeIcon.textContent = theme === "dark" ? "\u2600" : "\u263E";
        if (themeLabel) themeLabel.textContent = theme === "dark" ? "Light" : "Dark";
        if (themeColorMeta) themeColorMeta.content = theme === "dark" ? "#06101a" : "#f0f4f8";
    }

    setTheme(getTheme());

    document.querySelectorAll("[data-theme-toggle]").forEach(btn => {
        btn.addEventListener("click", () => {
            const current = getTheme();
            setTheme(current === "dark" ? "light" : "dark");
        });
    });

    // 13. Two-step exit confirmation
    document.querySelectorAll("button[data-exit]").forEach(btn => {
        btn.addEventListener("click", function () {
            const exitIntent = sessionStorage.getItem("exitIntent");
            if (exitIntent) {
                sessionStorage.removeItem("exitIntent");
                const form = this.closest("form[data-exit]");
                if (form) form.submit();
            } else {
                sessionStorage.setItem("exitIntent", "true");
                if (location.pathname !== "/dashboard") {
                    location.href = "/dashboard";
                }
            }
        });
    });
});

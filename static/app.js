document.addEventListener("DOMContentLoaded", () => {
    // 1. Animate progress bars on load
    const progressFills = document.querySelectorAll(".progress-fill");
    
    // We add a tiny delay to ensure smooth transition trigger after mounting
    setTimeout(() => {
        progressFills.forEach(fill => {
            const fillWidth = fill.getAttribute("data-fill-width");
            if (fillWidth) {
                // Safely convert to float and constrain to [0, 100]
                let pct = parseFloat(fillWidth);
                if (isNaN(pct)) pct = 0;
                if (pct < 0) pct = 0;
                if (pct > 100) pct = 100;
                
                fill.style.width = `${pct}%`;
            }
        });
    }, 150);

    // 2. Auto-fade settings save flash banner alert
    const flashBanner = document.querySelector(".flash-banner");
    if (flashBanner) {
        setTimeout(() => {
            flashBanner.style.transition = "opacity 600ms ease, transform 600ms ease, margin 600ms ease";
            flashBanner.style.opacity = "0";
            flashBanner.style.transform = "translateY(-10px)";
            
            // Remove from layout after fade finishes
            setTimeout(() => {
                flashBanner.remove();
            }, 600);
        }, 3000);
    }

    // 3. Register service worker for PWA behavior
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker.register("/sw.js").catch(() => {
                // Keep silent in UI; the app should work even when registration fails.
            });
        });
    }
});

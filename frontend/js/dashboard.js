document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;
    const user = getUser();
    const hour = new Date().getHours();
    const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
    const el = document.getElementById("greeting");
    if (el) el.textContent = `${greeting}, ${user?.name || "User"}`;

    const searchInput = document.getElementById("dashboardSearch");
    if (searchInput) {
        searchInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                window.location.href = `claim.html?q=${encodeURIComponent(searchInput.value)}`;
            }
        });
    }

    try {
        const claims = await apiFetch("/claims/");
        const recentList = document.getElementById("recentClaims");
        if (recentList && claims) {
            recentList.innerHTML = claims.slice(0, 3).map(c => `
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border-glass);">
                    <div>
                        <div style="font-weight:500;font-size:13px;">${c.claim_type || "Claim"} #${c.id}</div>
                        <div style="font-size:11px;color:var(--text-muted);">${c.created_at?.split("T")[0]}</div>
                    </div>
                    <span class="badge badge-${c.status}">${c.status}</span>
                </div>
            `).join("") || '<div style="color:var(--text-muted);font-size:13px;">No claims yet</div>';
        }
    } catch (e) { console.log("No recent claims"); }
});

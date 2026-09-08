document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth() || !requireAdmin()) return;

    try {
        const stats = await apiFetch("/admin/stats");
        document.getElementById("statUsers").textContent = stats.total_users;
        document.getElementById("statClaims").textContent = stats.total_claims;
        document.getElementById("statPending").textContent = stats.pending;
        document.getElementById("statRisk").textContent = stats.high_risk;

        const claims = await apiFetch("/claims/all");
        const tbody = document.getElementById("claimsTableBody");
        if (tbody) {
            tbody.innerHTML = claims.map(c => `
                <tr>
                    <td>#${c.id}</td>
                    <td>${c.user_name || c.user_id}</td>
                    <td>${c.claim_type}</td>
                    <td>${c.estimated_amount || "-"}</td>
                    <td><span class="badge badge-fraud-${c.fraud_label}">${c.fraud_label}</span></td>
                    <td><span class="badge badge-${c.status}">${c.status}</span></td>
                    <td>${c.created_at?.split("T")[0]}</td>
                    <td>
                        <select onchange="updateStatus(${c.id}, this.value)" style="background:var(--bg-base);color:var(--text-primary);border:1px solid var(--border-glass);border-radius:6px;padding:4px 8px;font-size:12px;">
                            <option value="pending" ${c.status==="pending"?"selected":""}>Pending</option>
                            <option value="approved" ${c.status==="approved"?"selected":""}>Approved</option>
                            <option value="rejected" ${c.status==="rejected"?"selected":""}>Rejected</option>
                            <option value="investigating" ${c.status==="investigating"?"selected":""}>Investigating</option>
                        </select>
                    </td>
                </tr>
            `).join("");
        }

        const users = await apiFetch("/admin/users");
        const utbody = document.getElementById("usersTableBody");
        if (utbody) {
            utbody.innerHTML = users.map(u => `
                <tr>
                    <td>${u.name}</td>
                    <td>${u.email}</td>
                    <td>${u.country || "-"}</td>
                    <td>${u.role}</td>
                    <td>${u.created_at?.split("T")[0]}</td>
                    <td>
                        <select onchange="updateRole(${u.id}, this.value)" style="background:var(--bg-base);color:var(--text-primary);border:1px solid var(--border-glass);border-radius:6px;padding:4px 8px;font-size:12px;">
                            <option value="user" ${u.role==="user"?"selected":""}>User</option>
                            <option value="admin" ${u.role==="admin"?"selected":""}>Admin</option>
                        </select>
                    </td>
                </tr>
            `).join("");
        }

        if (typeof Chart !== "undefined") {
            new Chart(document.getElementById("typeChart"), {
                type: "bar",
                data: {
                    labels: (stats.claims_by_type || []).map(x => x.claim_type),
                    datasets: [{ label: "Claims", data: (stats.claims_by_type || []).map(x => x.count), backgroundColor: "#8B5CF6", borderRadius: 6 }]
                },
                options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: "#6B6B80" } }, y: { ticks: { color: "#6B6B80" } } } }
            });
            new Chart(document.getElementById("fraudChart"), {
                type: "doughnut",
                data: {
                    labels: (stats.fraud_distribution || []).map(x => x.fraud_label),
                    datasets: [{ data: (stats.fraud_distribution || []).map(x => x.count), backgroundColor: ["#22C55E", "#F59E0B", "#EF4444"], borderWidth: 0 }]
                },
                options: { responsive: true, plugins: { legend: { position: "bottom", labels: { color: "#6B6B80" } } } }
            });
        }
    } catch (e) { console.error(e); showToast("Failed to load admin data", "error"); }
});

async function updateStatus(id, status) {
    try {
        await apiFetch(`/claims/${id}/status`, { method: "PUT", body: new URLSearchParams({ status }) });
        showToast("Status updated");
    } catch (err) { showToast(err.message, "error"); }
}

async function updateRole(id, role) {
    try {
        await apiFetch(`/admin/users/${id}/role?role=${role}`, { method: "PUT" });
        showToast("Role updated");
    } catch (err) { showToast(err.message, "error"); }
}

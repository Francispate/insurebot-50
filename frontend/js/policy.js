document.addEventListener("DOMContentLoaded", () => {
    if (!requireAuth()) return;

    const tabs = document.querySelectorAll(".policy-tab");
    const panels = document.querySelectorAll(".policy-panel");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            panels.forEach(p => p.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById(tab.dataset.target).classList.add("active");
        });
    });

    const policyDropzone = document.getElementById("policyDropzone");
    const policyFile = document.getElementById("policyFile");
    let uploadedPolicy = null;

    if (policyDropzone) {
        policyDropzone.addEventListener("click", () => policyFile?.click());
        policyDropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length) handlePolicy(e.dataTransfer.files[0]);
        });
        policyDropzone.addEventListener("dragover", (e) => e.preventDefault());
    }
    if (policyFile) policyFile.addEventListener("change", (e) => {
        if (e.target.files.length) handlePolicy(e.target.files[0]);
    });

    function handlePolicy(file) {
        uploadedPolicy = file;
        policyDropzone.innerHTML = `<div style="font-size:32px;">📄</div><div style="font-weight:500;">${file.name}</div>`;
    }

    document.getElementById("analyzePolicyBtn")?.addEventListener("click", async () => {
        if (!uploadedPolicy) { showToast("Upload a policy PDF first", "error"); return; }
        const btn = document.getElementById("analyzePolicyBtn");
        btn.disabled = true; btn.textContent = "Analyzing...";
        const formData = new FormData();
        formData.append("file", uploadedPolicy);
        try {
            const res = await fetch(`${BASE_URL}/policies/analyze`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${getToken()}` },
                body: formData
            });
            const data = await res.json();
            showPolicyResult(data);
        } catch (err) { showToast(err.message, "error"); }
        finally { btn.disabled = false; btn.textContent = "Analyze Policy"; }
    });

    function showPolicyResult(data) {
        const el = document.getElementById("policyResult");
        if (!el) return;
        el.style.display = "block";
        el.innerHTML = `
            <h3 style="margin-bottom:16px;">Policy Analysis</h3>
            <div class="glass-card" style="margin-bottom:12px;">
                <div style="font-size:12px;color:var(--text-muted);">Summary</div>
                <div style="margin-top:4px;">${data.policy_summary}</div>
            </div>
            <div class="glass-card" style="margin-bottom:12px;">
                <div style="font-size:12px;color:var(--text-muted);">Covered</div>
                <ul style="margin-top:4px;padding-left:16px;font-size:13px;">
                    ${(data.what_is_covered || []).map(i => `<li>${i}</li>`).join("")}
                </ul>
            </div>
            <div class="glass-card" style="margin-bottom:12px;">
                <div style="font-size:12px;color:var(--text-muted);">Not Covered</div>
                <ul style="margin-top:4px;padding-left:16px;font-size:13px;">
                    ${(data.what_is_NOT_covered || []).map(i => `<li>${i}</li>`).join("")}
                </ul>
            </div>
            <div class="glass-card" style="margin-bottom:12px;">
                <div style="font-size:12px;color:var(--text-muted);">Hidden Benefits</div>
                <ul style="margin-top:4px;padding-left:16px;font-size:13px;">
                    ${(data.hidden_benefits || []).map(i => `<li>${i}</li>`).join("")}
                </ul>
            </div>
            <div class="glass-card">
                <div style="font-size:12px;color:var(--text-muted);">Dangerous Clauses</div>
                <ul style="margin-top:4px;padding-left:16px;font-size:13px;">
                    ${(data.dangerous_clauses || []).map(i => `<li>${i}</li>`).join("")}
                </ul>
            </div>
        `;
    }

    document.getElementById("getAdviceBtn")?.addEventListener("click", async () => {
        const type = document.getElementById("adviceType").value;
        const desc = document.getElementById("adviceDesc").value;
        const btn = document.getElementById("getAdviceBtn");
        btn.disabled = true; btn.textContent = "Getting advice...";
        try {
            const res = await apiFetch("/policies/advice", {
                method: "POST",
                body: JSON.stringify({ claim_type: type, description: desc })
            });
            const el = document.getElementById("adviceResult");
            if (el) {
                el.style.display = "block";
                el.innerHTML = `<div class="glass-card"><div style="white-space:pre-wrap;font-size:14px;line-height:1.6;">${res.advice}</div></div>`;
            }
        } catch (err) { showToast(err.message, "error"); }
        finally { btn.disabled = false; btn.textContent = "Get Advice"; }
    });
});

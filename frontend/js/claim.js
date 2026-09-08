document.addEventListener("DOMContentLoaded", () => {
    if (!requireAuth()) return;

    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    let uploadedFile = null;

    if (dropzone) {
        dropzone.addEventListener("click", () => fileInput?.click());
        dropzone.addEventListener("dragover", (e) => { e.preventDefault(); dropzone.classList.add("dragover"); });
        dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files.length) handleFile(e.target.files[0]);
        });
    }

    function handleFile(file) {
        uploadedFile = file;
        if (dropzone) dropzone.innerHTML = `<div style="font-size:32px;margin-bottom:8px;">📄</div><div style="font-weight:500;">${file.name}</div><div style="font-size:12px;color:var(--text-muted);">Click to change</div>`;
    }

    const analyzeBtn = document.getElementById("analyzeBtn");
    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", async () => {
            if (!uploadedFile) { showToast("Please upload an image first", "error"); return; }
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> Analyzing...';

            const formData = new FormData();
            formData.append("image", uploadedFile);

            try {
                const res = await fetch(`${BASE_URL}/claims/analyze`, {
                    method: "POST",
                    body: formData
                });
                const data = await res.json();
                showResult(data);
            } catch (err) {
                showToast(err.message, "error");
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = "Analyze Claim";
            }
        });
    }

    function showResult(data) {
        const resultCard = document.getElementById("resultCard");
        if (!resultCard) return;
        resultCard.style.display = "block";
        resultCard.innerHTML = `
            <h3 style="margin-bottom:16px;font-size:18px;">Analysis Result</h3>
            <div style="display:grid;gap:12px;">
                <div class="glass-card" style="padding:16px;">
                    <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px;">Damage Severity</div>
                    <span class="badge badge-${data.damage_severity === 'minor' ? 'approved' : data.damage_severity === 'severe' ? 'rejected' : 'pending'}">${data.damage_severity}</span>
                </div>
                <div class="glass-card" style="padding:16px;">
                    <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px;">Estimated Amount</div>
                    <div style="font-size:20px;font-weight:700;">${data.estimated_amount}</div>
                </div>
                <div class="glass-card" style="padding:16px;">
                    <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px;">Fraud Risk</div>
                    <span class="badge badge-fraud-${data.fraud_label}">${data.fraud_label} (${data.fraud_risk_score}%)</span>
                </div>
                <div class="glass-card" style="padding:16px;">
                    <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px;">Affected Parts</div>
                    <div style="font-size:13px;">${(data.affected_parts || []).join(", ")}</div>
                </div>
                <div class="glass-card" style="padding:16px;">
                    <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px;">Documents Needed</div>
                    <div style="font-size:13px;">${(data.documentation_needed || []).join(", ")}</div>
                </div>
            </div>
            <button class="btn btn-primary" style="width:100%;margin-top:16px;" id="saveClaimBtn">Save Claim</button>
        `;

        document.getElementById("saveClaimBtn").addEventListener("click", async () => {
            const claimData = {
                claim_type: data.claim_type || "car",
                description: document.getElementById("claimDesc")?.value || "",
                damage_severity: data.damage_severity,
                estimated_amount: data.estimated_amount,
                affected_parts: JSON.stringify(data.affected_parts || []),
                documentation_needed: JSON.stringify(data.documentation_needed || []),
                rejection_risks: JSON.stringify(data.rejection_risks || []),
                fraud_risk_score: data.fraud_risk_score,
                fraud_label: data.fraud_label,
                predicted_settlement: data.predicted_settlement,
                settlement_confidence: data.settlement_confidence,
                requires_investigation: data.requires_investigation ? 1 : 0
            };
            try {
                await apiFetch("/claims/", { method: "POST", body: JSON.stringify(claimData) });
                showToast("Claim saved successfully!");
                setTimeout(() => window.location.href = "dashboard.html", 1000);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }
});

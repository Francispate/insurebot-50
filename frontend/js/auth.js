function requireAuth() {
    if (!getToken()) {
        window.location.href = "login.html";
        return false;
    }
    return true;
}

function requireAdmin() {
    const user = getUser();
    if (!user || user.role !== "admin") {
        window.location.href = "dashboard.html";
        return false;
    }
    return true;
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "login.html";
}

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const loginTab = document.getElementById("loginTab");
    const registerTab = document.getElementById("registerTab");

    if (loginTab && registerTab) {
        loginTab.addEventListener("click", () => {
            loginTab.classList.add("active");
            registerTab.classList.remove("active");
            document.getElementById("loginForm").classList.add("active");
            document.getElementById("registerForm").classList.remove("active");
        });
        registerTab.addEventListener("click", () => {
            registerTab.classList.add("active");
            loginTab.classList.remove("active");
            document.getElementById("registerForm").classList.add("active");
            document.getElementById("loginForm").classList.remove("active");
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("loginEmail").value;
            const password = document.getElementById("loginPassword").value;
            try {
                const res = await apiFetch("/auth/login", {
                    method: "POST",
                    body: JSON.stringify({ email, password })
                });
                localStorage.setItem("token", res.token);
                localStorage.setItem("user", JSON.stringify(res.user));
                window.location.href = "dashboard.html";
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("regName").value;
            const email = document.getElementById("regEmail").value;
            const password = document.getElementById("regPassword").value;
            const country = document.getElementById("regCountry").value;
            try {
                const res = await apiFetch("/auth/register", {
                    method: "POST",
                    body: JSON.stringify({ name, email, password, country })
                });
                localStorage.setItem("token", res.token);
                localStorage.setItem("user", JSON.stringify(res.user));
                window.location.href = "dashboard.html";
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }
});

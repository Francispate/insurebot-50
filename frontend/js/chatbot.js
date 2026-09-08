document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("chatbotToggle");
    const panel = document.getElementById("chatbotPanel");
    const input = document.getElementById("chatInput");
    const sendBtn = document.getElementById("chatSend");
    const messages = document.getElementById("chatMessages");

    if (!toggle) return;

    toggle.addEventListener("click", () => panel.classList.toggle("open"));

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;
        if (!requireAuth()) { showToast("Please login first", "error"); return; }

        appendMessage("user", text);
        input.value = "";
        showTyping();

        try {
            const history = [];
            const res = await apiFetch("/chat/message", {
                method: "POST",
                body: JSON.stringify({ messages: [...history, { role: "user", content: text }], session_id: "" })
            });
            hideTyping();
            appendMessage("bot", res.response);
        } catch (err) {
            hideTyping();
            appendMessage("bot", "Sorry, I'm having trouble connecting. Please try again.");
        }
    }

    sendBtn?.addEventListener("click", sendMessage);
    input?.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });

    function appendMessage(role, text) {
        const div = document.createElement("div");
        div.className = `chat-message ${role}`;
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    function showTyping() {
        const div = document.createElement("div");
        div.className = "chat-message bot typing";
        div.id = "typingIndicator";
        div.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    function hideTyping() {
        document.getElementById("typingIndicator")?.remove();
    }
});

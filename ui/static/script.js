/* ── Chat UI ─────────────────────────────────────────── */

function sendMessage() {
    const input   = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const message = input.value.trim();
    if (!message) return;

    addMessage("You", message, "user");
    input.value = "";
    sendBtn.disabled = true;

    const loadingId = addMessage("Agent", "Thinking…", "loading");

    fetch("/chat", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ question: message }),
    })
    .then(r => r.json())
    .then(data => {
        removeMessage(loadingId);
        addMessage("Agent", data.answer || data.error, "agent");
    })
    .catch(err => {
        removeMessage(loadingId);
        addMessage("Agent", "Error: " + err.message, "agent");
    })
    .finally(() => { sendBtn.disabled = false; input.focus(); });
}

function addMessage(sender, text, type) {
    const chatBox = document.getElementById("chat-box");
    const id      = "msg-" + Date.now();
    const div     = document.createElement("div");
    div.className = `message ${type}`;
    div.id        = id;
    div.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Send on Enter key
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    if (input) {
        input.addEventListener("keydown", e => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
        });
    }
});

/* ── Registration Form ───────────────────────────────── */

const regForm = document.getElementById("register-form");
if (regForm) {
    regForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const f = regForm;
        const payload = {
            name:        f.name.value,
            description: f.description.value,
            endpoint:    f.endpoint.value,
            method:      f.method.value,
            parameters:  f.parameters.value ? f.parameters.value.split(",").map(p => p.trim()).filter(Boolean) : [],
            owner_team:  f.owner_team.value,
            auth_type:   f.auth_type.value,
            dependencies: [],
        };

        const resp   = await fetch("/registry/register", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(payload),
        });
        const result = await resp.json();
        const status = document.getElementById("status-message");

        if (resp.ok) {
            status.innerHTML = `<p style="color:green">✓ Registered! ID: <strong>${result.api_id}</strong></p>`;
            f.reset();
        } else {
            status.innerHTML = `<p style="color:red">✗ Failed: ${JSON.stringify(result)}</p>`;
        }
    });
}

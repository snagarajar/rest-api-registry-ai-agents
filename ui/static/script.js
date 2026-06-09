/* ── Chat UI ─────────────────────────────────────────── */

function ask(question) {
    document.getElementById("user-input").value = question;
    sendMessage();
}

function sendMessage() {
    const input   = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const message = input.value.trim();
    if (!message) return;

    // Hide suggestion chips after first real message
    const suggestions = document.querySelector(".suggestions");
    if (suggestions) suggestions.style.display = "none";

    addUserMessage(message);
    input.value = "";
    sendBtn.disabled = true;

    const loadingId = addLoadingMessage();

    fetch("/chat", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ question: message }),
    })
    .then(r => r.json())
    .then(data => {
        removeMessage(loadingId);
        addAgentMessage(data.answer || data.error || "No response.");
    })
    .catch(err => {
        removeMessage(loadingId);
        addAgentMessage("⚠️ Error: " + err.message);
    })
    .finally(() => { sendBtn.disabled = false; input.focus(); });
}

function addUserMessage(text) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = "message user";
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addAgentMessage(markdown) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = "message agent";
    div.innerHTML = `<div class="msg-label">Agent</div><div class="msg-body">${marked.parse(markdown)}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addLoadingMessage() {
    const chatBox = document.getElementById("chat-box");
    const id = "msg-loading-" + Date.now();
    const div = document.createElement("div");
    div.className = "message loading";
    div.id = id;
    div.innerHTML = `Thinking <span class="dots"><span></span><span></span><span></span></span>`;
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

const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const profileEl = document.getElementById("profile");

function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function showProfile(profile) {
  const filled = Object.entries(profile || {}).filter(([, v]) => v && v.length !== 0);
  profileEl.textContent = filled.length
    ? "Saved preferences: " + filled.map(([k, v]) => k + ": " + v).join(" | ")
    : "Saved preferences: none yet";
}

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;
  addMessage(text, "user");
  inputEl.value = "";
  sendBtn.disabled = true;
  const typing = addMessage("Typing...", "bot");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    typing.textContent = data.reply;
    showProfile(data.profile);
  } catch (err) {
    typing.textContent = "Error: could not reach the server.";
  }
  sendBtn.disabled = false;
  inputEl.focus();
}

async function resetPrefs() {
  await fetch("/reset", { method: "POST" });
  showProfile({});
  addMessage("All preferences have been cleared!", "bot");
}

sendBtn.addEventListener("click", sendMessage);
inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });
document.getElementById("reset-btn").addEventListener("click", resetPrefs);

fetch("/profile").then((r) => r.json()).then(showProfile);
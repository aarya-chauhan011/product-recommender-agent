const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const profileEl = document.getElementById("profile");
const productsEl = document.getElementById("products");

function esc(value) {
  const d = document.createElement("div");
  d.textContent = value == null ? "" : String(value);
  return d.innerHTML;
}

function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function addTyping() {
  const div = document.createElement("div");
  div.className = "msg bot typing";
  div.innerHTML = "<span></span><span></span><span></span>";
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function showProfile(p) {
  p = p || {};
  const chips = [];
  if (p.category) chips.push(["Category", p.category]);
  if (p.max_budget) chips.push(["Budget", "up to ₹" + Number(p.max_budget).toLocaleString("en-IN")]);
  (p.liked_brands || []).forEach((b) => chips.push(["Likes", b]));
  (p.disliked_brands || []).forEach((b) => chips.push(["Avoids", b]));
  (p.liked_features || []).forEach((f) => chips.push(["Feature", f]));
  profileEl.innerHTML = chips.length
    ? chips.map(([k, v]) => `<span class="chip">${esc(k)}: <b>${esc(v)}</b></span>`).join("")
    : '<span class="chip-empty">No saved preferences yet</span>';
}

function icon(category) {
  const c = String(category || "").toLowerCase();
  if (c.includes("jewel")) return "💍";
  if (c.includes("decor")) return "🏺";
  return "🛍️";
}

function showProducts(products) {
  if (!products || !products.length) {
    productsEl.innerHTML = '<p class="empty">No matching products yet. Try changing your budget or category.</p>';
    return;
  }
  productsEl.innerHTML = products.map((p, i) => {
    const price = isNaN(Number(p.price)) ? esc(p.price) : "₹" + Number(p.price).toLocaleString("en-IN");
    const thumb = p.image
      ? `<img src="${esc(p.image)}" alt="${esc(p.name)}">`
      : icon(p.category);
    const badge = i === 0 ? '<span class="badge">Top pick</span>' : "";
    return `
      <div class="product" style="animation-delay:${i * 0.12}s">
        <div class="thumb">${thumb}</div>
        <div class="info">
          <h4>${esc(p.name)}${badge}</h4>
          <div class="brand">${esc(p.brand)} · ${esc(p.category)}</div>
          <div class="desc">${esc(p.description)}</div>
          <div class="price">${price}</div>
        </div>
      </div>`;
  }).join("");
}

async function sendMessage(text) {
  text = (text || inputEl.value).trim();
  if (!text) return;
  addMessage(text, "user");
  inputEl.value = "";
  sendBtn.disabled = true;
  const typing = addTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    if (!res.ok) throw new Error("Server error " + res.status);
    const data = await res.json();
    typing.remove();
    addMessage(data.reply, "bot");
    showProfile(data.profile);
    showProducts(data.products);
  } catch (err) {
    typing.remove();
    addMessage("Sorry, I could not reach the server. Please try again.", "bot");
  }
  sendBtn.disabled = false;
  inputEl.focus();
}

async function resetPrefs() {
  await fetch("/reset", { method: "POST" });
  showProfile({});
  productsEl.innerHTML = '<p class="empty">Your recommendations will appear here.</p>';
  addMessage("All preferences have been cleared!", "bot");
}

sendBtn.addEventListener("click", () => sendMessage());
inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });
document.getElementById("reset-btn").addEventListener("click", resetPrefs);
document.querySelectorAll(".quick button").forEach((b) =>
  b.addEventListener("click", () => sendMessage(b.dataset.q))
);

// Scroll-reveal animation
const observer = new IntersectionObserver((entries) => {
  entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("show"); });
}, { threshold: 0.15 });
document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

fetch("/profile").then((r) => r.json()).then(showProfile);
const API_BASE = "http://localhost:3000";
const WS_URL = "ws://localhost:3000/ws";
const ws = new WebSocket(WS_URL);
const messagesDiv = document.getElementById("messages");
const sendBtn = document.getElementById("sendBtn");

// WebSocket: receive new messages
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  updateOrAddMessage(msg);
};

// Load existing messages on startup
async function loadMessages() {
  try {
    const res = await fetch(`${API_BASE}/messages`);
    const data = await res.json();
    data.forEach(updateOrAddMessage);
  } catch (err) {
    console.error("Error loading messages:", err);
  }
}
loadMessages();

// Send message via HTTP POST
sendBtn.addEventListener("click", sendMessage);

async function sendMessage() {
  const input = document.getElementById("msgInput");
  const text = input.value.trim();
  if (!text) return;

  try {
    await fetch(`${API_BASE}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    input.value = "";
  } catch (err) {
    console.error("Error sending message:", err);
  }
}

// Like or dislike message
async function react(timestamp, action) {
  try {
    await fetch(`${API_BASE}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ timestamp }),
    });
  } catch (err) {
    console.error(`Error reacting with ${action}:`, err);
  }
}

// Display or update message safely (no innerHTML)
function updateOrAddMessage(msg) {
  let el = document.getElementById(msg.timestamp);
  if (!el) {
    el = document.createElement("div");
    el.className = "message";
    el.id = msg.timestamp;
    messagesDiv.prepend(el);
  }

  // Clear and rebuild safely
  el.textContent = "";

  const textEl = document.createElement("b");
  textEl.textContent = msg.text;
  el.appendChild(textEl);
  el.appendChild(document.createElement("br"));

  const likesText = document.createTextNode(`👍 ${msg.likes} `);
  const dislikesText = document.createTextNode(`👎 ${msg.dislikes} `);
  el.appendChild(likesText);
  el.appendChild(dislikesText);

  const likeBtn = document.createElement("button");
  likeBtn.textContent = "Like";
  likeBtn.onclick = () => react(msg.timestamp, "like");
  el.appendChild(likeBtn);

  const dislikeBtn = document.createElement("button");
  dislikeBtn.textContent = "Dislike";
  dislikeBtn.onclick = () => react(msg.timestamp, "dislike");
  el.appendChild(dislikeBtn);
}

const socket = io();
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const chat = document.getElementById("chat");
const promptInput = document.getElementById("promptInput");
const sendBtn = document.getElementById("sendBtn");
const agentSelect = document.getElementById("agentSelect");

let gameState = { agents: {}, canvasObjects: [] };

socket.emit("joinRoom", { roomId: "room1" });

// Receive state updates
socket.on("agentMessage", ({ from, payload, gameState: newState }) => {
  if (newState) gameState = newState;

  addChat(`${payload.role}: ${payload.text}`);
  redrawCanvas();
});

socket.on("log", ({ from, prompt }) => {
  addChat(`👉 ${from} prompt: ${prompt}`);
});

function addChat(msg) {
  const div = document.createElement("div");
  div.textContent = msg;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

sendBtn.onclick = () => {
  const prompt = promptInput.value.trim();
  const agentId = agentSelect.value;
  if (!prompt) return;
  socket.emit("agentSpeak", {
    roomId: "room1",
    agentId,
    prompt,
    context: { agents: ["A", "B"] },
  });
  promptInput.value = "";
};

function redrawCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw all canvas objects
  for (const obj of gameState.canvasObjects) {
    drawObject(obj);
  }
}

function drawObject(obj) {
  if (!obj || !obj.cmd) return;

  switch (obj.cmd) {
    case "circle":
      ctx.beginPath();
      ctx.arc(obj.x, obj.y, obj.w || 20, 0, Math.PI * 2);
      ctx.fillStyle = obj.color || "black";
      ctx.fill();
      break;
    case "rect":
      ctx.fillStyle = obj.color || "black";
      ctx.fillRect(obj.x, obj.y, obj.w || 50, obj.h || 50);
      break;
    case "text":
      ctx.fillStyle = obj.color || "black";
      ctx.fillText(obj.payload || "?", obj.x, obj.y);
      break;
  }
}

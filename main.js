import express from "express";
import http from "http";
import { Server } from "socket.io";
import cors from "cors";
import dotenv from "dotenv";
import { GoogleGenAI, Type } from "@google/genai";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

app.use(express.static(path.join(__dirname, "public")));

const genai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// === Game state ===
const gameState = {
  agents: {
    A: { id: "A", name: "Alice", x: 1, y: 1, lastMessage: "", task: null, inventory: [] },
    B: { id: "B", name: "Bob", x: 3, y: 1, lastMessage: "", task: null, inventory: [] }
  },
  environment: {
    fridge: { x: 2, y: 2 },
    table: { x: 5, y: 3 },
    oven: { x: 8, y: 2 }
  }
};

// Pizza steps
const pizzaSteps = [
  { action: "get ingredients", location: "fridge" },
  { action: "prepare pizza", location: "table" },
  { action: "bake pizza", location: "oven" }
];

// === Helper: apply movement commands ===
function applyCommands(commands) {
  if (!Array.isArray(commands)) return;
  for (const cmd of commands) {
    if (cmd.type === "move" && gameState.agents[cmd.agent]) {
      gameState.agents[cmd.agent].x = cmd.x;
      gameState.agents[cmd.agent].y = cmd.y;
    }
  }
}

// === Gemini schema ===
const moveCommandSchema = {
  type: Type.OBJECT,
  properties: {
    type: { type: Type.STRING, enum: ["move"] },
    agent: { type: Type.STRING },
    x: { type: Type.NUMBER },
    y: { type: Type.NUMBER }
  },
  required: ["type", "agent", "x", "y"],
  propertyOrdering: ["type", "agent", "x", "y"]
};

const responseSchema = {
  type: Type.OBJECT,
  properties: {
    role: { type: Type.STRING },
    intent: { type: Type.STRING },
    text: { type: Type.STRING },
    drawCommands: {
      type: Type.ARRAY,
      items: moveCommandSchema
    }
  },
  required: ["role", "intent", "text", "drawCommands"],
  propertyOrdering: ["role", "intent", "text", "drawCommands"]
};

// Assign tasks if missing
function assignTasks() {
  Object.values(gameState.agents).forEach((agent, i) => {
    if (!agent.task) {
      agent.task = { ...pizzaSteps[i % pizzaSteps.length], step: i % pizzaSteps.length };
    }
  });
}

// Move agent one step towards target
function moveTowards(agent, target) {
  if (agent.x < target.x) agent.x++;
  else if (agent.x > target.x) agent.x--;
  if (agent.y < target.y) agent.y++;
  else if (agent.y > target.y) agent.y--;
}

// === Generate agent response using Gemini ===
async function agentRespond(roomId, agentId, contextText) {
  const agent = gameState.agents[agentId];
  const otherId = agentId === "A" ? "B" : "A";

  const instructionText = `
You are ${agent.name}, a persona in a 2D grid kitchen simulation.
You can:
1. Talk with ${gameState.agents[otherId].name}.
2. Move on the grid to complete your pizza task.

Rules:
- Always reply with JSON using the schema.
- If you move, include a command like:
  { "type": "move", "agent": "${agentId}", "x": 2, "y": 2 }
- Tasks: pick ingredients (fridge), prepare (table), bake (oven).
- Keep x between 0–10, y between 0–5.
- Do not invent fields, follow schema.
- Be natural in conversation.

Context: Last thing ${gameState.agents[otherId].name} said: "${gameState.agents[otherId].lastMessage || "Nothing"}"
Current task: "${agent.task ? agent.task.action : "none"}"
`;

  const response = await genai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: instructionText,
    config: { responseMimeType: "application/json", responseSchema }
  });

  let structured;
  try {
    structured = JSON.parse(response.text);
  } catch (err) {
    console.error("Parse error:", err);
    structured = { role: agentId, intent: "error", text: "Parsing failed", drawCommands: [] };
  }

  // Update agent
  agent.lastMessage = structured.text || "";
  applyCommands(structured.drawCommands);

  // Auto-step toward task if not yet at target
  if (agent.task) {
    const target = gameState.environment[agent.task.location];
    if (target && (agent.x !== target.x || agent.y !== target.y)) {
      moveTowards(agent, target);
    } else {
      agent.inventory.push(agent.task.action);
      console.log(`${agent.name} completed task: ${agent.task.action}`);
      agent.task = null;
    }
  }

  io.to(roomId).emit("agentMessage", { from: agentId, payload: structured, gameState });
  return structured.text;
}

// === Socket.IO ===
io.on("connection", (socket) => {
  console.log("Socket connected:", socket.id);

  socket.on("joinRoom", ({ roomId }) => {
    socket.join(roomId);

    socket.emit("agentMessage", {
      from: "server",
      payload: { role: "system", intent: "sync", text: "Welcome!" },
      gameState
    });

    // Conversation + task loop
    let lastSpeaker = "B"; // alternate
    setInterval(async () => {
      const nextSpeaker = lastSpeaker === "A" ? "B" : "A";
      const context = `Last message from ${gameState.agents[lastSpeaker].name}: "${gameState.agents[lastSpeaker].lastMessage}"`;
      await agentRespond(roomId, nextSpeaker, context);
      assignTasks();
      lastSpeaker = nextSpeaker;
    }, 5000); // every 5 sec
  });
});

server.listen(3000, () => console.log("✅ Server running on 3000"));

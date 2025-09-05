
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

const genai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY
});

// === Game state ===
const gameState = {
  agents: {
    A: { id: "A", name: "Alice", x: 100, y: 200, lastMessage: "" },
    B: { id: "B", name: "Bob", x: 400, y: 200, lastMessage: "" }
  }
};

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

// === Schema for Gemini structured output ===
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

// === Generate agent response ===
async function agentRespond(roomId, agentId, contextText) {
  const agent = gameState.agents[agentId];
  const otherId = agentId === "A" ? "B" : "A";

  const instructionText = `
You are ${agent.name}, a persona in a 2D canvas simulation.
You can:
1. Talk with the other agent.
2. Move yourself on the canvas.

Rules:
- Always reply with JSON only.
- If you want to move, include a command like:
  { "type": "move", "agent": "${agentId}", "x": 250, "y": 180 }
- Keep x between 50–550, y between 50–350.
- Never invent fields, only use schema.
- Be natural in conversation with ${gameState.agents[otherId].name}.

Context: The last thing ${gameState.agents[otherId].name} said was:
"${gameState.agents[otherId].lastMessage || "Nothing yet"}"
`;

  const response = await genai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: instructionText,
    config: {
      responseMimeType: "application/json",
      responseSchema
    }
  });

  console.log(`Raw Gemini (${agentId}):`, response.text);

  let structured;
  try {
    structured = JSON.parse(response.text);
  } catch (err) {
    console.error("Parse error:", err);
    structured = {
      role: agentId,
      intent: "error",
      text: "Parsing failed",
      drawCommands: []
    };
  }

  // Update game state
  gameState.agents[agentId].lastMessage = structured.text || "";
  applyCommands(structured.drawCommands);

  // Broadcast to clients
  io.to(roomId).emit("agentMessage", {
    from: agentId,
    payload: structured,
    gameState
  });

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

    // Conversation loop
    let lastSpeaker = "B"; // alternate
    setInterval(async () => {
      const nextSpeaker = lastSpeaker === "A" ? "B" : "A";
      const context = `Last message from ${gameState.agents[lastSpeaker].name}: "${gameState.agents[lastSpeaker].lastMessage}"`;
      await agentRespond(roomId, nextSpeaker, context);
      lastSpeaker = nextSpeaker;
    }, 10000); // every 10 sec
  });
});

server.listen(3000, () => console.log("✅ Server running on 3000"));

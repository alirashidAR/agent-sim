# 🧠 AgentMemory Framework

A modular, plug-and-play framework for creating AI agents with persistent memory and communication capabilities.

## ✨ Features

- 🔌 **Plug-and-Play**: Easy integration into any project
- 🧠 **Persistent Memory**: Multiple memory backends (Mem0, local storage)
- 🤖 **Multiple AI Providers**: Gemini, OpenAI, mock (for testing)
- 💬 **Agent Communication**: Built-in communication hub
- 🎭 **Extensible**: Easy to create custom agent types
- ⚙️ **Configurable**: Environment-based or programmatic configuration
- 🔧 **Developer Friendly**: Full debugging and diagnostic tools

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Basic installation
pip install mem0ai google-generativeai python-dotenv

# Or use the setup utility
python framework_setup.py --install
```

### 2. Configure Environment

```bash
# Create environment template
python framework_setup.py --create-env

# Edit .env file with your API keys
GEMINI_API_KEY=your_gemini_api_key
MEM0_API_KEY=your_mem0_api_key
```

### 3. Basic Usage

```python
import asyncio
from framework import BaseAgent, FrameworkConfig

async def main():
    # Create agent with default config (loads from .env)
    config = FrameworkConfig.from_env()
    agent = BaseAgent("MyBot", config, "I'm a helpful assistant")
    
    # Add memory
    await agent.add_memory("I love helping users with questions")
    
    # Generate response with memory context
    response = await agent.think("What do you like to do?")
    print(response)

asyncio.run(main())
```

## 📖 Framework Structure

```
framework/
├── __init__.py              # Main imports
├── config.py               # Configuration management
├── memory_manager.py       # Memory system
├── ai_providers.py         # AI provider implementations  
├── base_agent.py           # Base agent class
└── communication.py        # Communication hub

examples/
├── basic_usage.py          # Basic usage example
├── custom_agents.py        # Custom agent types
└── plugin_example.py       # Different provider configs
```

## 🔧 Configuration Options

### Environment Variables

```bash
# AI Provider
AI_PROVIDER=gemini          # gemini, openai, mock
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
AI_MODEL=gemini-2.0-flash-exp

# Memory Provider  
MEMORY_PROVIDER=mem0        # mem0, local
MEM0_API_KEY=your_key

# Framework Settings
DEBUG_MODE=true
MAX_MEMORY_RETRIEVAL=10
```

### Programmatic Configuration

```python
from framework import FrameworkConfig

# Custom configuration
config = FrameworkConfig(
    ai_provider="gemini",
    ai_api_key="your-key",
    memory_provider="local",  # Use local storage
    debug_mode=True
)

# From dictionary
config = FrameworkConfig.from_dict({
    "ai_provider": "openai",
    "memory_provider": "mem0"
})
```

## 🎭 Creating Custom Agents

```python
from framework import BaseAgent

class TherapistAgent(BaseAgent):
    def __init__(self, name: str, config: FrameworkConfig):
        super().__init__(
            name=name,
            config=config,
            personality="Empathetic and supportive therapist",
            system_prompt="You are a professional therapist..."
        )
    
    async def start_session(self, client_message: str) -> str:
        # Custom therapy session logic
        await self.add_memory(f"Session started: {client_message}")
        return await self.think(client_message)

# Usage
therapist = TherapistAgent("Dr. Smith", config)
response = await therapist.start_session("I'm feeling anxious")
```

## 💬 Agent Communication

```python
from framework import CommunicationHub

# Create communication hub
hub = CommunicationHub(config)
hub.add_agent(agent1)
hub.add_agent(agent2)

# Facilitate conversation
conversation = await hub.facilitate_conversation(
    "Agent1", "Agent2", 
    "Hello! How are you?", 
    max_exchanges=5
)

# Group discussion
discussion = await hub.group_discussion(
    "What's the future of AI?",
    ["Agent1", "Agent2", "Agent3"],
    rounds=3
)
```

## 🔌 Supported Providers

### AI Providers

| Provider | Package Required | Models |
|----------|------------------|--------|
| Gemini | `google-generativeai` | `gemini-2.0-flash-exp`, `gemini-pro` |
| OpenAI | `openai` | `gpt-4`, `gpt-3.5-turbo` |
| Mock | None | For testing |

### Memory Providers

| Provider | Package Required | Description |
|----------|------------------|-------------|
| Mem0 | `mem0ai` | Cloud-based semantic memory |
| Local | None | File-based storage for testing |

## 🛠 Development Tools

### Diagnostics

```bash
# Run complete diagnostics
python framework_setup.py --diagnostics

# Interactive setup
python framework_setup.py --quick-start
```

### Event Handling

```python
# Add event handlers to communication hub
def on_conversation(event_type, data):
    print(f"Conversation event: {data['speaker']} -> {data['listener']}")

hub.add_event_handler("conversation_exchange", on_conversation)
```

## 📋 Examples

### Basic Agent Communication

```python
# examples/basic_usage.py
import asyncio
from framework import BaseAgent, FrameworkConfig

async def main():
    config = FrameworkConfig.from_env()
    
    alice = BaseAgent("Alice", config, "Curious researcher")
    bob = BaseAgent("Bob", config, "Creative problem solver")
    
    response = await alice.communicate_with(bob, "What's your approach to creativity?")
    print(response)

asyncio.run(main())
```

### Custom Agent Types

```python
# examples/custom_agents.py - Shows TherapistAgent, ScientistAgent, CreativeAgent
```

### Different Providers

```python
# examples/plugin_example.py - Shows Gemini, OpenAI, Mock configurations
```

## 🔍 API Reference

### BaseAgent

```python
class BaseAgent:
    async def add_memory(content: str, metadata: dict = None) -> str
    async def search_memories(query: str, limit: int = None) -> List[dict]
    async def think(input_text: str, context: str = None) -> str
    async def communicate_with(other_agent: BaseAgent, message: str) -> str
    async def receive_message(sender: BaseAgent, message: str, context: str = None) -> str
```

### CommunicationHub

```python
class CommunicationHub:
    def add_agent(agent: BaseAgent) -> None
    async def facilitate_conversation(agent1: str, agent2: str, message: str, max_exchanges: int = 5) -> List[dict]
    async def group_discussion(topic: str, agents: List[str], rounds: int = 3) -> List[dict]
    async def broadcast_message(sender: str, message: str, recipients: List[str] = None) -> dict
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing API Keys**
   ```bash
   python framework_setup.py --diagnostics
   ```

2. **Import Errors**
   ```bash
   pip install mem0ai google-generativeai python-dotenv
   ```

3. **Memory Issues**
   - Use `memory_provider="local"` for testing
   - Check Mem0 API key and quota

4. **AI Provider Issues**
   - Verify API keys are correct
   - Check model names match provider requirements

## 🤝 Integration Examples

### Into Existing Projects

```python
# your_project.py
from framework import BaseAgent, FrameworkConfig

class YourCustomBot(BaseAgent):
    def __init__(self):
        config = FrameworkConfig(
            ai_provider="gemini",
            ai_api_key="your-key",
            memory_provider="local"  # Simple setup
        )
        super().__init__("YourBot", config)
    
    async def handle_user_input(self, user_input: str) -> str:
        # Your custom logic here
        await self.add_memory(f"User said: {user_input}")
        return await self.think(user_input)
```

### Web Framework Integration

```python
# flask_example.py
from flask import Flask, request, jsonify
from framework import BaseAgent, FrameworkConfig
import asyncio

app = Flask(__name__)
bot = BaseAgent("WebBot", FrameworkConfig.from_env())

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    response = asyncio.run(bot.think(user_message))
    return jsonify({'response': response})
```

## 📄 License

MIT License - feel free to use in your projects!

## 🆘 Support

- Check `examples/` directory for usage patterns
- Run `python framework_setup.py --diagnostics` for issues
- Review configuration options in `framework/config.py`



# 🚀 How to Use the AgentMemory Framework

This guide shows you exactly how to integrate the AgentMemory Framework into your projects.

## 🎯 What You Get

✅ **Plug-and-Play Memory**: Agents remember conversations across sessions  
✅ **Multiple AI Providers**: Switch between Gemini, OpenAI, or mock AI  
✅ **Easy Integration**: Drop into any Python project  
✅ **Custom Agent Types**: Create specialized agents for your use case  
✅ **Communication System**: Agents can talk to each other  

## 🏃‍♂️ Quick Integration

### 1. Copy the Framework

```bash
# Copy the entire framework directory to your project
cp -r framework/ /path/to/your/project/
```

### 2. Install Dependencies

```bash
# For Gemini + Mem0 (recommended)
pip install mem0ai google-generativeai python-dotenv

# For OpenAI + Mem0
pip install mem0ai openai python-dotenv

# For testing (no API keys needed)
pip install python-dotenv
```

### 3. Set Up Environment

```bash
# Create .env file
echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
echo "MEM0_API_KEY=your_mem0_key_here" >> .env
```

### 4. Use in Your Code

```python
# your_app.py
from framework import BaseAgent, FrameworkConfig
import asyncio

async def main():
    # Simple setup
    agent = BaseAgent("MyBot", FrameworkConfig.from_env())
    
    # Agent remembers this
    await agent.add_memory("User prefers concise answers")
    
    # Generate response with memory context
    response = await agent.think("How should I respond to users?")
    print(response)

asyncio.run(main())
```

## 🎭 Real-World Use Cases

### 1. Customer Support Bot

```python
from framework import BaseAgent, FrameworkConfig

class SupportBot(BaseAgent):
    def __init__(self):
        config = FrameworkConfig.from_env()
        super().__init__(
            "SupportBot", 
            config,
            personality="Helpful and professional customer support agent",
            system_prompt="You are a customer support agent. Be helpful, professional, and remember customer preferences."
        )
    
    async def handle_customer_query(self, customer_id: str, query: str) -> str:
        # Remember this customer interaction
        await self.add_memory(f"Customer {customer_id}: {query}", {"customer_id": customer_id})
        
        # Get relevant past interactions
        past_context = await self.get_memory_context(f"Customer {customer_id}")
        
        # Generate response with context
        response = await self.think(query, past_context)
        
        # Remember our response
        await self.add_memory(f"I responded to {customer_id}: {response}", {"customer_id": customer_id})
        
        return response

# Usage
bot = SupportBot()
response = await bot.handle_customer_query("user123", "I'm having trouble with my order")
```

### 2. Learning Companion

```python
class TutorBot(BaseAgent):
    def __init__(self, subject: str):
        config = FrameworkConfig.from_env()
        super().__init__(
            f"{subject}Tutor",
            config,
            personality=f"Patient and encouraging {subject} tutor",
            system_prompt=f"You are a {subject} tutor. Adapt to the student's learning pace and remember their progress."
        )
        self.subject = subject
    
    async def teach_concept(self, student_id: str, concept: str, student_question: str) -> str:
        # Check what student already knows
        knowledge_context = await self.get_memory_context(f"student {student_id} knows")
        
        # Remember this learning session
        await self.add_memory(
            f"Student {student_id} learning {concept}: {student_question}",
            {"student_id": student_id, "concept": concept}
        )
        
        # Generate teaching response
        prompt = f"Teach {concept} to student. Their question: {student_question}"
        response = await self.think(prompt, knowledge_context)
        
        return response

# Usage
math_tutor = TutorBot("Math")
explanation = await math_tutor.teach_concept("student1", "calculus", "What is a derivative?")
```

### 3. Creative Writing Assistant

```python
class WritingAssistant(BaseAgent):
    def __init__(self):
        config = FrameworkConfig.from_env()
        super().__init__(
            "WritingAssistant",
            config,
            personality="Creative and supportive writing coach",
            system_prompt="You help writers develop their stories and characters. Remember their writing style and preferences."
        )
        self.projects = {}
    
    async def help_with_story(self, writer_id: str, project_name: str, request: str) -> str:
        # Remember this project
        project_key = f"{writer_id}_{project_name}"
        
        # Get project context
        project_context = await self.get_memory_context(f"project {project_name}")
        
        # Add this interaction to memory
        await self.add_memory(
            f"Writer {writer_id} working on {project_name}: {request}",
            {"writer_id": writer_id, "project": project_name}
        )
        
        # Generate helpful response
        response = await self.think(request, project_context)
        
        return response

# Usage
assistant = WritingAssistant()
help_text = await assistant.help_with_story("writer1", "SciFiNovel", "I need help developing my main character")
```

## 🔧 Integration Patterns

### Web Framework Integration

#### Flask Example

```python
from flask import Flask, request, jsonify
from framework import BaseAgent, FrameworkConfig
import asyncio

app = Flask(__name__)

# Initialize bot once
config = FrameworkConfig.from_env()
bot = BaseAgent("WebBot", config, "Helpful web assistant")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    message = data.get('message')
    
    # Run async function in sync context
    response = asyncio.run(handle_chat(user_id, message))
    return jsonify({'response': response})

async def handle_chat(user_id: str, message: str) -> str:
    # Add user context to memory
    await bot.add_memory(f"User {user_id}: {message}", {"user_id": user_id})
    
    # Get response with memory context
    return await bot.think(message)

if __name__ == '__main__':
    app.run()
```

#### FastAPI Example

```python
from fastapi import FastAPI
from pydantic import BaseModel
from framework import BaseAgent, FrameworkConfig

app = FastAPI()
bot = BaseAgent("APIBot", FrameworkConfig.from_env())

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # Remember user interaction
    await bot.add_memory(f"User {request.user_id}: {request.message}")
    
    # Generate response
    response = await bot.think(request.message)
    
    return {"response": response}
```

### Discord Bot Integration

```python
import discord
from framework import BaseAgent, FrameworkConfig

class DiscordBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.agent = BaseAgent("DiscordBot", FrameworkConfig.from_env())
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # Remember conversation
        await self.agent.add_memory(
            f"{message.author.name}: {message.content}",
            {"user_id": str(message.author.id), "channel": str(message.channel.id)}
        )
        
        # Generate response
        response = await self.agent.think(message.content)
        await message.channel.send(response)

# Usage
bot = DiscordBot()
bot.run('your_discord_token')
```

## 🛠 Configuration Options

### Environment-Based Setup

```bash
# .env file
AI_PROVIDER=gemini                    # or openai, mock
GEMINI_API_KEY=your_key
MEM0_API_KEY=your_key
MEMORY_PROVIDER=mem0                  # or local
DEBUG_MODE=true
MAX_MEMORY_RETRIEVAL=10
```

### Programmatic Setup

```python
from framework import FrameworkConfig, BaseAgent

# Custom configuration
config = FrameworkConfig(
    ai_provider="gemini",
    ai_api_key="your-key",
    memory_provider="local",  # For testing
    debug_mode=True,
    max_memory_retrieval=15
)

agent = BaseAgent("CustomBot", config)
```

### Multiple Configurations

```python
# Different configs for different agents
production_config = FrameworkConfig(
    ai_provider="gemini",
    memory_provider="mem0",
    debug_mode=False
)

test_config = FrameworkConfig(
    ai_provider="mock",
    memory_provider="local",
    debug_mode=True
)

prod_bot = BaseAgent("ProdBot", production_config)
test_bot = BaseAgent("TestBot", test_config)
```

## 🚨 Common Issues & Solutions

### 1. Missing API Keys
```python
# Check configuration
from framework import FrameworkConfig
config = FrameworkConfig.from_env()
try:
    config.validate()
    print("Configuration is valid!")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### 2. Memory Not Persisting
```python
# For testing, use local memory
config = FrameworkConfig(
    memory_provider="local",
    ai_provider="mock"  # No API key needed
)
```

### 3. Import Errors
```bash
# Install required packages
pip install mem0ai google-generativeai python-dotenv
```

### 4. Debugging
```python
# Enable debug mode
config = FrameworkConfig.from_env()
config.debug_mode = True

# Or in .env file
DEBUG_MODE=true
```

## 📈 Performance Tips

### 1. Memory Management
```python
# Limit memory retrieval for faster responses
config.max_memory_retrieval = 5

# Use metadata for better memory organization
await agent.add_memory("Important info", {"priority": "high", "category": "user_preference"})
```

### 2. Async Best Practices
```python
# Batch operations when possible
memories = await asyncio.gather(
    agent1.search_memories("topic"),
    agent2.search_memories("topic"),
    agent3.search_memories("topic")
)
```

### 3. Configuration Caching
```python
# Create config once, reuse for multiple agents
config = FrameworkConfig.from_env()

agents = [
    BaseAgent(f"Agent{i}", config) 
    for i in range(5)
]
```

## 🎯 Next Steps

1. **Try the Examples**: Run the files in `examples/` directory
2. **Create Custom Agents**: Extend `BaseAgent` for your specific needs  
3. **Set Up Communication**: Use `CommunicationHub` for multi-agent systems
4. **Add Event Handling**: Monitor agent interactions with event handlers
5. **Scale Up**: Use production-ready providers (Gemini + Mem0)

## 📚 Additional Resources

- **Framework Documentation**: See `FRAMEWORK_README.md`
- **Setup Utility**: Run `python framework_setup.py --help`
- **Examples Directory**: Check `examples/` for more patterns
- **Diagnostics**: Run `python framework_setup.py --diagnostics`

---

**Ready to build something amazing? Start with the basic example and customize from there! 🚀**



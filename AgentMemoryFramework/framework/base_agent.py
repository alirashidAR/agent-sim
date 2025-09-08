"""
Base agent class for the AgentMemory Framework
Provides core functionality that can be extended for specific use cases
"""
import uuid
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from .config import FrameworkConfig
from .memory_manager import MemoryManager
from .ai_providers import create_ai_provider, AIProvider

class BaseAgent:
    """
    Base agent class with memory and AI capabilities
    
    This class provides core functionality and can be extended for specific use cases.
    """
    
    def __init__(self, 
                 name: str,
                 config: Optional[FrameworkConfig] = None,
                 personality: str = "",
                 system_prompt: str = "",
                 agent_id: Optional[str] = None):
        """
        Initialize a base agent
        
        Args:
            name: Agent's name
            config: Framework configuration (if None, loads from environment)
            personality: Agent's personality description
            system_prompt: System prompt for the AI
            agent_id: Optional custom agent ID
        """
        self.name = name
        self.agent_id = agent_id or str(uuid.uuid4())
        self.personality = personality
        self.system_prompt = system_prompt or f"You are {name}, an AI agent."
        
        # Initialize configuration
        self.config = config or FrameworkConfig.from_env()
        self.config.validate()
        
        # Initialize memory and AI
        self.memory_manager = MemoryManager(self.config)
        self.ai_provider = create_ai_provider(self.config)
        
        # Agent state
        self.conversation_history: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
        if self.config.debug_mode:
            print(f"🤖 Agent '{self.name}' initialized with ID: {self.agent_id}")
    
    async def add_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a memory to the agent's persistent storage"""
        if metadata is None:
            metadata = {}
        
        # Add agent-specific metadata
        full_metadata = {
            "agent_name": self.name,
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            **metadata
        }
        
        memory_id = await self.memory_manager.add_memory(
            user_id=self.agent_id,
            content=content,
            metadata=full_metadata
        )
        
        if self.config.debug_mode:
            print(f"💾 {self.name} stored memory: {content[:50]}...")
        
        return memory_id
    
    async def search_memories(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for relevant memories"""
        return await self.memory_manager.search_memories(
            user_id=self.agent_id,
            query=query,
            limit=limit
        )
    
    async def get_all_memories(self) -> List[Dict[str, Any]]:
        """Get all memories for this agent"""
        return await self.memory_manager.get_all_memories(self.agent_id)
    
    async def get_memory_context(self, topic: str) -> str:
        """Get formatted memory context for a topic"""
        return await self.memory_manager.get_memory_context(self.agent_id, topic)
    
    async def think(self, input_text: str, context: Optional[str] = None) -> str:
        """
        Generate a response using AI with memory context
        
        Args:
            input_text: The input to respond to
            context: Additional context (optional)
        
        Returns:
            AI-generated response
        """
        # Get relevant memories
        memory_context = await self.get_memory_context(input_text)
        
        # Build full context
        full_context = ""
        if self.system_prompt:
            full_context += f"{self.system_prompt}\n\n"
        
        if self.personality:
            full_context += f"Personality: {self.personality}\n\n"
        
        if memory_context:
            full_context += memory_context + "\n"
        
        if context:
            full_context += f"Additional context: {context}\n\n"
        
        # Generate response
        response = await self.ai_provider.generate_response(input_text, full_context)
        return response
    
    async def communicate_with(self, other_agent: 'BaseAgent', message: str) -> str:
        """
        Send a message to another agent and get their response
        
        Args:
            other_agent: The agent to communicate with
            message: The message to send
        
        Returns:
            The other agent's response
        """
        if self.config.debug_mode:
            print(f"💬 {self.name} → {other_agent.name}: {message}")
        
        # Store outgoing message
        await self.add_memory(f"I said to {other_agent.name}: {message}")
        
        # Log conversation
        conversation_entry = {
            "from": self.name,
            "to": other_agent.name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(conversation_entry)
        
        # Get response from other agent
        context = f"This message is from {self.name}: {message}"
        response = await other_agent.receive_message(self, message, context)
        
        # Store received response
        await self.add_memory(f"{other_agent.name} replied: {response}")
        
        return response
    
    async def receive_message(self, sender: 'BaseAgent', message: str, context: Optional[str] = None) -> str:
        """
        Receive and respond to a message from another agent
        
        Args:
            sender: The agent who sent the message
            message: The message received
            context: Additional context
        
        Returns:
            This agent's response
        """
        # Store incoming message
        await self.add_memory(f"{sender.name} said to me: {message}")
        
        # Generate response
        response = await self.think(message, context)
        
        if self.config.debug_mode:
            print(f"💬 {sender.name} → {self.name}: {message}")
            print(f"💭 {self.name} → {sender.name}: {response}")
        
        # Log conversation
        conversation_entry = {
            "from": sender.name,
            "to": self.name,
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(conversation_entry)
        
        return response
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the agent"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata for the agent"""
        return self.metadata.get(key, default)
    
    async def reset_memory(self) -> bool:
        """Clear all memories (use with caution)"""
        memories = await self.get_all_memories()
        success = True
        
        for memory in memories:
            memory_id = memory.get("id")
            if memory_id:
                result = await self.memory_manager.delete_memory(self.agent_id, memory_id)
                success = success and result
        
        return success
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history for this agent"""
        return self.conversation_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "personality": self.personality,
            "conversations": len(self.conversation_history),
            "config": self.config.to_dict()
        }
    
    def __str__(self) -> str:
        return f"Agent(name='{self.name}', id='{self.agent_id[:8]}...')"
    
    def __repr__(self) -> str:
        return self.__str__()



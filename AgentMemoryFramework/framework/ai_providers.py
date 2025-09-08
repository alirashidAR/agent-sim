"""
AI provider implementations for the AgentMemory Framework
Supports multiple AI providers (Gemini, OpenAI, etc.)
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .config import FrameworkConfig

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response from the AI"""
        pass
    
    @abstractmethod
    async def generate_with_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Generate response with conversation history"""
        pass

class GeminiProvider(AIProvider):
    """Google Gemini AI provider"""
    
    def __init__(self, config: FrameworkConfig):
        super().__init__(config)
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.ai_api_key)
            self.model = genai.GenerativeModel(config.ai_model)
            self.genai = genai
        except ImportError:
            raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using Gemini"""
        full_prompt = prompt
        if context:
            full_prompt = f"{context}\n\n{prompt}"
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, full_prompt)
            return response.text
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error generating Gemini response: {e}")
            return f"I'm having trouble thinking right now. Error: {str(e)}"
    
    async def generate_with_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Generate response with conversation history"""
        # Convert messages to a single prompt for Gemini
        conversation_text = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                conversation_text += f"Human: {content}\n"
            elif role == "assistant":
                conversation_text += f"Assistant: {content}\n"
        
        conversation_text += "Assistant: "
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, conversation_text)
            return response.text
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error generating Gemini conversation response: {e}")
            return f"I'm having trouble responding right now. Error: {str(e)}"

class OpenAIProvider(AIProvider):
    """OpenAI provider (GPT models)"""
    
    def __init__(self, config: FrameworkConfig):
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=config.ai_api_key)
            self.model_name = config.ai_model if config.ai_model.startswith("gpt") else "gpt-4"
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using OpenAI"""
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error generating OpenAI response: {e}")
            return f"I'm having trouble thinking right now. Error: {str(e)}"
    
    async def generate_with_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Generate response with conversation history"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error generating OpenAI conversation response: {e}")
            return f"I'm having trouble responding right now. Error: {str(e)}"

class MockAIProvider(AIProvider):
    """Mock AI provider for testing"""
    
    def __init__(self, config: FrameworkConfig):
        super().__init__(config)
        self.response_templates = [
            "That's an interesting point about {topic}.",
            "I understand your perspective on {topic}.",
            "Let me think about {topic} for a moment...",
            "Thanks for sharing your thoughts on {topic}.",
            "I have some ideas about {topic} as well."
        ]
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate mock response"""
        import random
        topic = prompt.split()[:3]  # Use first 3 words as topic
        topic_str = " ".join(topic)
        
        template = random.choice(self.response_templates)
        return template.format(topic=topic_str)
    
    async def generate_with_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Generate mock conversation response"""
        if messages:
            last_message = messages[-1].get("content", "conversation")
            return await self.generate_response(last_message)
        return "Hello! How can I help you today?"

def create_ai_provider(config: FrameworkConfig) -> AIProvider:
    """Factory function to create AI provider based on config"""
    if config.ai_provider == "gemini":
        return GeminiProvider(config)
    elif config.ai_provider == "openai":
        return OpenAIProvider(config)
    elif config.ai_provider == "mock":
        return MockAIProvider(config)
    else:
        raise ValueError(f"Unsupported AI provider: {config.ai_provider}")



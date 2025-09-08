"""
Configuration management for the AgentMemory Framework
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class FrameworkConfig:
    """Configuration class for the AgentMemory Framework"""
    
    # Memory settings
    memory_provider: str = "mem0"  # mem0, local, redis, etc.
    memory_api_key: Optional[str] = None
    
    # AI Provider settings  
    ai_provider: str = "gemini"  # gemini, openai, anthropic, etc.
    ai_api_key: Optional[str] = None
    ai_model: str = "gemini-2.0-flash-exp"
    
    # General settings
    debug_mode: bool = False
    max_memory_retrieval: int = 10
    memory_similarity_threshold: float = 0.7
    
    # Communication settings
    max_conversation_turns: int = 10
    conversation_timeout: int = 30  # seconds
    
    @classmethod
    def from_env(cls, env_file: str = ".env") -> "FrameworkConfig":
        """Load configuration from environment variables"""
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        return cls(
            memory_provider=os.getenv("MEMORY_PROVIDER", "mem0"),
            memory_api_key=os.getenv("MEM0_API_KEY") or os.getenv("MEMORY_API_KEY"),
            ai_provider=os.getenv("AI_PROVIDER", "gemini"),
            ai_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("AI_API_KEY"),
            ai_model=os.getenv("AI_MODEL", "gemini-2.0-flash-exp"),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            max_memory_retrieval=int(os.getenv("MAX_MEMORY_RETRIEVAL", "10")),
            memory_similarity_threshold=float(os.getenv("MEMORY_SIMILARITY_THRESHOLD", "0.7")),
            max_conversation_turns=int(os.getenv("MAX_CONVERSATION_TURNS", "10")),
            conversation_timeout=int(os.getenv("CONVERSATION_TIMEOUT", "30"))
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "FrameworkConfig":
        """Create configuration from dictionary"""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "memory_provider": self.memory_provider,
            "memory_api_key": self.memory_api_key,
            "ai_provider": self.ai_provider,
            "ai_api_key": self.ai_api_key,
            "ai_model": self.ai_model,
            "debug_mode": self.debug_mode,
            "max_memory_retrieval": self.max_memory_retrieval,
            "memory_similarity_threshold": self.memory_similarity_threshold,
            "max_conversation_turns": self.max_conversation_turns,
            "conversation_timeout": self.conversation_timeout
        }
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.ai_api_key:
            raise ValueError(f"AI API key is required for provider: {self.ai_provider}")
        
        if self.memory_provider == "mem0" and not self.memory_api_key:
            raise ValueError("Mem0 API key is required when using mem0 provider")
        
        return True



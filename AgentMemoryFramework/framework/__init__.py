# AgentMemory Framework
# A plug-and-play memory system for AI agents

from .memory_manager import MemoryManager
from .base_agent import BaseAgent
from .ai_providers import GeminiProvider, OpenAIProvider
from .communication import CommunicationHub
from .config import FrameworkConfig

__version__ = "1.0.0"
__all__ = [
    "MemoryManager",
    "BaseAgent", 
    "GeminiProvider",
    "OpenAIProvider",
    "CommunicationHub",
    "FrameworkConfig"
]



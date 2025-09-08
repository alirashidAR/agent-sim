"""
Memory management system for AI agents
Supports multiple memory providers (Mem0, local storage, etc.)
"""
import uuid
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from .config import FrameworkConfig

class MemoryProvider(ABC):
    """Abstract base class for memory providers"""
    
    @abstractmethod
    async def add_memory(self, user_id: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add a memory and return memory ID"""
        pass
    
    @abstractmethod
    async def search_memories(self, user_id: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search for relevant memories"""
        pass
    
    @abstractmethod
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all memories for a user"""
        pass
    
    @abstractmethod
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a specific memory"""
        pass

class Mem0Provider(MemoryProvider):
    """Mem0 memory provider implementation"""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
        try:
            from mem0 import MemoryClient
            self.client = MemoryClient()
        except ImportError:
            raise ImportError("mem0ai package is required for Mem0Provider. Install with: pip install mem0ai")
    
    async def add_memory(self, user_id: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add memory to Mem0"""
        messages = [
            {"role": "user", "content": content},
            {"role": "assistant", "content": "I remember this information."}
        ]
        
        full_metadata = {
            "timestamp": datetime.now().isoformat(),
            **metadata
        }
        
        try:
            result = self.client.add(messages, user_id=user_id, metadata=full_metadata)
            return str(result) if result else str(uuid.uuid4())
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error adding memory: {e}")
            return str(uuid.uuid4())
    
    async def search_memories(self, user_id: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search memories in Mem0"""
        try:
            results = self.client.search(query=query, user_id=user_id, limit=limit)
            if isinstance(results, list):
                return results
            return results.get('results', [])
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error searching memories: {e}")
            return []
    
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all memories from Mem0"""
        try:
            results = self.client.get_all(user_id=user_id)
            if isinstance(results, list):
                return results
            return results.get('results', [])
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error getting all memories: {e}")
            return []
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete memory from Mem0"""
        try:
            self.client.delete(memory_id)
            return True
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error deleting memory: {e}")
            return False

class LocalMemoryProvider(MemoryProvider):
    """Local file-based memory provider for testing/development"""
    
    def __init__(self, config: FrameworkConfig, storage_path: str = "local_memories.json"):
        self.config = config
        self.storage_path = storage_path
        self.memories = self._load_memories()
    
    def _load_memories(self) -> Dict[str, List[Dict]]:
        """Load memories from local file"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_memories(self):
        """Save memories to local file"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    async def add_memory(self, user_id: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add memory locally"""
        memory_id = str(uuid.uuid4())
        memory = {
            "id": memory_id,
            "content": content,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        }
        
        if user_id not in self.memories:
            self.memories[user_id] = []
        
        self.memories[user_id].append(memory)
        self._save_memories()
        return memory_id
    
    async def search_memories(self, user_id: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search memories locally (simple text matching)"""
        if user_id not in self.memories:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for memory in self.memories[user_id]:
            if query_lower in memory["content"].lower():
                matches.append({
                    "memory": memory["content"],
                    "metadata": memory["metadata"],
                    "id": memory["id"]
                })
        
        return matches[:limit]
    
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all memories locally"""
        if user_id not in self.memories:
            return []
        
        return [
            {
                "memory": memory["content"],
                "metadata": memory["metadata"],
                "id": memory["id"]
            }
            for memory in self.memories[user_id]
        ]
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete memory locally"""
        if user_id not in self.memories:
            return False
        
        original_count = len(self.memories[user_id])
        self.memories[user_id] = [m for m in self.memories[user_id] if m["id"] != memory_id]
        
        if len(self.memories[user_id]) < original_count:
            self._save_memories()
            return True
        return False

class MemoryManager:
    """Main memory manager that handles different providers"""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
        self.provider = self._create_provider()
    
    def _create_provider(self) -> MemoryProvider:
        """Create the appropriate memory provider"""
        if self.config.memory_provider == "mem0":
            return Mem0Provider(self.config)
        elif self.config.memory_provider == "local":
            return LocalMemoryProvider(self.config)
        else:
            raise ValueError(f"Unsupported memory provider: {self.config.memory_provider}")
    
    async def add_memory(self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a memory"""
        if metadata is None:
            metadata = {}
        
        return await self.provider.add_memory(user_id, content, metadata)
    
    async def search_memories(self, user_id: str, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for relevant memories"""
        limit = limit or self.config.max_memory_retrieval
        return await self.provider.search_memories(user_id, query, limit)
    
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all memories for a user"""
        return await self.provider.get_all_memories(user_id)
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a specific memory"""
        return await self.provider.delete_memory(user_id, memory_id)
    
    async def get_memory_context(self, user_id: str, topic: str) -> str:
        """Get formatted memory context for a topic"""
        memories = await self.search_memories(user_id, topic)
        
        if not memories:
            return ""
        
        context = f"\n--- Relevant memories ---\n"
        for memory in memories:
            context += f"- {memory.get('memory', '')}\n"
        context += "--- End of memories ---\n"
        
        return context



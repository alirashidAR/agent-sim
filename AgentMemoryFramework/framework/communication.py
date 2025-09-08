"""
Communication hub for managing agent interactions
"""
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from .base_agent import BaseAgent
from .config import FrameworkConfig

class CommunicationHub:
    """
    Hub for managing communication between multiple agents
    """
    
    def __init__(self, config: Optional[FrameworkConfig] = None):
        self.config = config or FrameworkConfig.from_env()
        self.agents: Dict[str, BaseAgent] = {}
        self.global_conversation_log: List[Dict[str, Any]] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def add_agent(self, agent: BaseAgent) -> None:
        """Add an agent to the communication hub"""
        self.agents[agent.name] = agent
        if self.config.debug_mode:
            print(f"🔗 Added agent '{agent.name}' to communication hub")
    
    def remove_agent(self, agent_name: str) -> bool:
        """Remove an agent from the communication hub"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            if self.config.debug_mode:
                print(f"🔌 Removed agent '{agent_name}' from communication hub")
            return True
        return False
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """Get list of all agent names"""
        return list(self.agents.keys())
    
    async def facilitate_conversation(self, 
                                    agent1_name: str, 
                                    agent2_name: str,
                                    initial_message: str, 
                                    max_exchanges: int = 5) -> List[Dict[str, Any]]:
        """
        Facilitate a conversation between two agents
        
        Args:
            agent1_name: Name of the first agent (initiator)
            agent2_name: Name of the second agent (responder)
            initial_message: Message to start the conversation
            max_exchanges: Maximum number of exchanges
        
        Returns:
            List of conversation exchanges
        """
        agent1 = self.agents.get(agent1_name)
        agent2 = self.agents.get(agent2_name)
        
        if not agent1 or not agent2:
            raise ValueError(f"One or both agents not found: {agent1_name}, {agent2_name}")
        
        conversation_log = []
        current_message = initial_message
        current_speaker = agent1
        current_listener = agent2
        
        if self.config.debug_mode:
            print(f"🎭 Starting conversation between {agent1_name} and {agent2_name}")
            print(f"📝 Initial message: {initial_message}")
            print("=" * 60)
        
        for exchange in range(max_exchanges):
            # Send message and get response
            response = await current_speaker.communicate_with(current_listener, current_message)
            
            # Log the exchange
            exchange_log = {
                "exchange": exchange + 1,
                "speaker": current_speaker.name,
                "listener": current_listener.name,
                "message": current_message,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            conversation_log.append(exchange_log)
            self.global_conversation_log.append(exchange_log)
            
            # Emit event
            await self._emit_event("conversation_exchange", exchange_log)
            
            # Swap roles for next exchange
            current_speaker, current_listener = current_listener, current_speaker
            current_message = response
            
            if self.config.debug_mode:
                print("-" * 40)
        
        if self.config.debug_mode:
            print("=" * 60)
            print(f"✅ Conversation completed after {max_exchanges} exchanges")
        
        await self._emit_event("conversation_completed", {
            "participants": [agent1_name, agent2_name],
            "exchanges": len(conversation_log),
            "conversation_log": conversation_log
        })
        
        return conversation_log
    
    async def group_discussion(self, 
                             topic: str, 
                             agent_names: List[str], 
                             rounds: int = 3) -> List[Dict[str, Any]]:
        """
        Facilitate a group discussion among multiple agents
        
        Args:
            topic: Discussion topic
            agent_names: List of participating agent names
            rounds: Number of discussion rounds
        
        Returns:
            List of all contributions
        """
        if len(agent_names) < 2:
            raise ValueError("At least 2 agents required for group discussion")
        
        agents = []
        for name in agent_names:
            agent = self.agents.get(name)
            if not agent:
                raise ValueError(f"Agent '{name}' not found")
            agents.append(agent)
        
        discussion_log = []
        
        if self.config.debug_mode:
            print(f"🎪 Starting group discussion on: {topic}")
            print(f"👥 Participants: {', '.join(agent_names)}")
            print("=" * 60)
        
        for round_num in range(rounds):
            if self.config.debug_mode:
                print(f"🔄 Round {round_num + 1}")
            
            for agent in agents:
                # Get context from previous contributions
                context = ""
                if discussion_log:
                    recent_contributions = [
                        log for log in discussion_log 
                        if log.get("round") == round_num + 1
                    ]
                    if recent_contributions:
                        context = "Previous contributions in this round:\n"
                        for contrib in recent_contributions:
                            context += f"- {contrib['agent']}: {contrib['contribution']}\n"
                
                # Agent contributes
                prompt = f"Topic: {topic}\n\n{context}\n\nPlease share your thoughts on this topic."
                contribution = await agent.think(prompt)
                
                # Store contribution in memory
                await agent.add_memory(f"I contributed to a group discussion on '{topic}': {contribution}")
                
                # Log contribution
                contribution_log = {
                    "round": round_num + 1,
                    "agent": agent.name,
                    "topic": topic,
                    "contribution": contribution,
                    "timestamp": datetime.now().isoformat()
                }
                
                discussion_log.append(contribution_log)
                self.global_conversation_log.append(contribution_log)
                
                await self._emit_event("group_contribution", contribution_log)
                
                if self.config.debug_mode:
                    print(f"💭 {agent.name}: {contribution}")
                    print("-" * 40)
        
        if self.config.debug_mode:
            print("=" * 60)
            print(f"✅ Group discussion completed after {rounds} rounds")
        
        await self._emit_event("group_discussion_completed", {
            "topic": topic,
            "participants": agent_names,
            "rounds": rounds,
            "contributions": len(discussion_log),
            "discussion_log": discussion_log
        })
        
        return discussion_log
    
    async def broadcast_message(self, 
                              sender_name: str, 
                              message: str, 
                              recipient_names: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Broadcast a message to multiple agents
        
        Args:
            sender_name: Name of the sending agent
            message: Message to broadcast
            recipient_names: List of recipient names (if None, sends to all)
        
        Returns:
            Dictionary mapping agent names to their responses
        """
        sender = self.agents.get(sender_name)
        if not sender:
            raise ValueError(f"Sender agent '{sender_name}' not found")
        
        if recipient_names is None:
            recipient_names = [name for name in self.agents.keys() if name != sender_name]
        
        responses = {}
        
        for recipient_name in recipient_names:
            recipient = self.agents.get(recipient_name)
            if recipient:
                response = await sender.communicate_with(recipient, message)
                responses[recipient_name] = response
        
        await self._emit_event("broadcast_completed", {
            "sender": sender_name,
            "message": message,
            "recipients": recipient_names,
            "responses": responses
        })
        
        return responses
    
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _emit_event(self, event_type: str, data: Any) -> None:
        """Emit an event to all registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_type, data)
                    else:
                        handler(event_type, data)
                except Exception as e:
                    if self.config.debug_mode:
                        print(f"Error in event handler: {e}")
    
    def get_global_conversation_log(self) -> List[Dict[str, Any]]:
        """Get the complete conversation log"""
        return self.global_conversation_log.copy()
    
    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all agents"""
        stats = {}
        for name, agent in self.agents.items():
            stats[name] = agent.get_stats()
        return stats
    
    def print_system_status(self) -> None:
        """Print current system status"""
        print("\n🔍 Communication Hub Status")
        print("=" * 50)
        print(f"📊 Total agents: {len(self.agents)}")
        print(f"📝 Total conversations logged: {len(self.global_conversation_log)}")
        
        print("\n👥 Agents:")
        for name, agent in self.agents.items():
            print(f"  • {name} (ID: {agent.agent_id[:8]}...)")
            print(f"    - Personality: {agent.personality or 'None'}")
            print(f"    - Conversations: {len(agent.conversation_history)}")
        print("=" * 50)



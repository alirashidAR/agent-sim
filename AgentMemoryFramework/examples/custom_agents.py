#!/usr/bin/env python3
"""
Example showing how to create custom agent types using the framework
"""
import asyncio
import sys
import os
from typing import List, Dict, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework import BaseAgent, CommunicationHub, FrameworkConfig

class TherapistAgent(BaseAgent):
    """Custom agent specialized in therapeutic conversations"""
    
    def __init__(self, name: str, config: FrameworkConfig, specialization: str = "general"):
        super().__init__(
            name=name,
            config=config,
            personality=f"Empathetic and supportive therapist specializing in {specialization}",
            system_prompt=f"You are {name}, a professional therapist specializing in {specialization}. "
                         f"You provide supportive, non-judgmental responses and help people process their emotions."
        )
        self.specialization = specialization
        self.session_count = 0
    
    async def start_session(self, client_message: str) -> str:
        """Start a therapy session"""
        self.session_count += 1
        await self.add_memory(f"Started therapy session #{self.session_count}")
        
        context = f"This is the start of therapy session #{self.session_count}. " \
                 f"The client said: {client_message}"
        
        response = await self.think(client_message, context)
        await self.add_memory(f"Session #{self.session_count} - Client: {client_message}, My response: {response}")
        
        return response

class ScientistAgent(BaseAgent):
    """Custom agent specialized in scientific research and analysis"""
    
    def __init__(self, name: str, config: FrameworkConfig, field: str = "general science"):
        super().__init__(
            name=name,
            config=config,
            personality=f"Methodical scientist specializing in {field}",
            system_prompt=f"You are {name}, a scientist specializing in {field}. "
                         f"You approach problems methodically, ask probing questions, "
                         f"and base conclusions on evidence and data."
        )
        self.field = field
        self.experiments = []
    
    async def propose_experiment(self, hypothesis: str) -> str:
        """Propose an experiment to test a hypothesis"""
        await self.add_memory(f"Considering hypothesis: {hypothesis}")
        
        context = f"As a {self.field} scientist, please propose an experiment to test this hypothesis: {hypothesis}"
        experiment_proposal = await self.think(hypothesis, context)
        
        self.experiments.append({
            "hypothesis": hypothesis,
            "experiment": experiment_proposal,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        await self.add_memory(f"Proposed experiment for hypothesis '{hypothesis}': {experiment_proposal}")
        return experiment_proposal
    
    def get_experiments(self) -> List[Dict[str, Any]]:
        """Get all proposed experiments"""
        return self.experiments.copy()

class CreativeAgent(BaseAgent):
    """Custom agent specialized in creative tasks"""
    
    def __init__(self, name: str, config: FrameworkConfig, medium: str = "writing"):
        super().__init__(
            name=name,
            config=config,
            personality=f"Creative artist specializing in {medium}",
            system_prompt=f"You are {name}, a creative artist specializing in {medium}. "
                         f"You think outside the box, make unexpected connections, "
                         f"and approach problems with creativity and imagination."
        )
        self.medium = medium
        self.creations = []
    
    async def create_something(self, prompt: str, style: str = "original") -> str:
        """Create something based on a prompt"""
        await self.add_memory(f"Creating {self.medium} piece with prompt: {prompt}")
        
        context = f"As a {self.medium} artist, create something {style} based on this prompt: {prompt}"
        creation = await self.think(prompt, context)
        
        self.creations.append({
            "prompt": prompt,
            "style": style,
            "creation": creation,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        await self.add_memory(f"Created {self.medium} piece: {creation[:100]}...")
        return creation
    
    def get_creations(self) -> List[Dict[str, Any]]:
        """Get all creations"""
        return self.creations.copy()

async def custom_agents_example():
    """Example showing custom agent types in action"""
    print("🎭 Custom Agent Types Example")
    print("=" * 50)
    
    # Create config (using local storage for this example)
    config = FrameworkConfig.from_env()
    config.memory_provider = "local"  # Use local storage
    config.debug_mode = True
    
    # Create custom agents
    therapist = TherapistAgent("Dr. Sarah", config, "anxiety and stress")
    scientist = ScientistAgent("Prof. Chen", config, "psychology")
    artist = CreativeAgent("Maya", config, "poetry")
    
    # Set up communication hub
    hub = CommunicationHub(config)
    hub.add_agent(therapist)
    hub.add_agent(scientist)
    hub.add_agent(artist)
    
    print("\n🧠 Therapist Session:")
    session_response = await therapist.start_session("I've been feeling really overwhelmed at work lately.")
    print(f"Therapist response: {session_response[:150]}...")
    
    print("\n🔬 Scientist Experiment Proposal:")
    experiment = await scientist.propose_experiment("People who practice mindfulness have lower stress levels")
    print(f"Experiment proposal: {experiment[:150]}...")
    
    print("\n🎨 Artist Creation:")
    poem = await artist.create_something("Write about finding peace in chaos", "contemplative")
    print(f"Poem: {poem[:150]}...")
    
    print("\n💬 Inter-agent Collaboration:")
    # Have the scientist and therapist discuss the stress research
    conversation = await hub.facilitate_conversation(
        "Prof. Chen", "Dr. Sarah",
        "I've been researching stress and mindfulness. What's your clinical experience with these techniques?",
        max_exchanges=2
    )
    
    # Have the artist create something based on the scientific discussion
    memories = await scientist.search_memories("mindfulness stress")
    if memories:
        scientific_context = memories[0].get('memory', '')
        artistic_response = await artist.create_something(
            f"Create a piece inspired by this scientific insight: {scientific_context}",
            "inspirational"
        )
        print(f"\nArtist's inspired creation: {artistic_response[:150]}...")
    
    print("\n📊 Agent Statistics:")
    print(f"Therapist sessions: {therapist.session_count}")
    print(f"Scientist experiments: {len(scientist.get_experiments())}")
    print(f"Artist creations: {len(artist.get_creations())}")
    
    print("\n✅ Custom agents example completed!")

if __name__ == "__main__":
    asyncio.run(custom_agents_example())



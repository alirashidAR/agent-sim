#!/usr/bin/env python3
"""
Basic usage example of the AgentMemory Framework
Shows how to create agents and have them communicate
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import the framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework import BaseAgent, CommunicationHub, FrameworkConfig

async def basic_example():
    """Basic example showing agent creation and communication"""
    print("🚀 Basic AgentMemory Framework Example")
    print("=" * 50)
    
    # Option 1: Use default config (loads from environment)
    config = FrameworkConfig.from_env()
    
    # Option 2: Create custom config
    # config = FrameworkConfig(
    #     ai_provider="gemini",
    #     ai_api_key="your-key-here",
    #     memory_provider="local",  # Use local storage for testing
    #     debug_mode=True
    # )
    
    # Create agents
    alice = BaseAgent(
        name="Alice",
        config=config,
        personality="Curious and analytical researcher",
        system_prompt="You are Alice, a researcher who loves asking questions and analyzing data."
    )
    
    bob = BaseAgent(
        name="Bob",
        config=config,
        personality="Creative problem solver",
        system_prompt="You are Bob, a creative thinker who enjoys brainstorming solutions."
    )
    
    # Basic communication
    print("\n💬 Basic Communication:")
    response = await alice.communicate_with(bob, "Hi Bob! What's your approach to solving complex problems?")
    print(f"Bob's response: {response[:100]}...")
    
    # Add some memories manually
    print("\n🧠 Adding memories:")
    await alice.add_memory("I enjoy collaborative problem-solving sessions")
    await bob.add_memory("I like to think outside the box when approaching challenges")
    
    # Test memory retrieval
    print("\n🔍 Testing memory retrieval:")
    alice_memories = await alice.search_memories("problem solving")
    print(f"Alice found {len(alice_memories)} relevant memories")
    
    # Another conversation with memory context
    print("\n💬 Second conversation (with memory context):")
    response2 = await bob.communicate_with(alice, "What have we discussed about problem-solving before?")
    print(f"Alice's response: {response2[:100]}...")
    
    print("\n✅ Basic example completed!")

if __name__ == "__main__":
    asyncio.run(basic_example())



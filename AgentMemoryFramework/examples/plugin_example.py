#!/usr/bin/env python3
"""
Example showing how to use different AI providers and memory backends
"""
import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework import BaseAgent, FrameworkConfig

async def plugin_example():
    """Example showing different provider configurations"""
    print("🔌 Plugin System Example")
    print("=" * 50)
    
    # Example 1: Gemini + Mem0 (production setup)
    print("\n1️⃣ Gemini + Mem0 Configuration:")
    try:
        gemini_config = FrameworkConfig(
            ai_provider="gemini",
            ai_api_key=os.getenv("GEMINI_API_KEY"),
            memory_provider="mem0",
            memory_api_key=os.getenv("MEM0_API_KEY"),
            debug_mode=True
        )
        
        if gemini_config.ai_api_key:
            gemini_agent = BaseAgent("GeminiBot", gemini_config, "I use Gemini AI with Mem0 memory")
            response = await gemini_agent.think("Tell me about yourself")
            print(f"Gemini agent: {response[:100]}...")
        else:
            print("Gemini API key not found, skipping...")
    
    except Exception as e:
        print(f"Gemini setup failed: {e}")
    
    # Example 2: OpenAI + Local memory (alternative setup)
    print("\n2️⃣ OpenAI + Local Memory Configuration:")
    try:
        openai_config = FrameworkConfig(
            ai_provider="openai",
            ai_api_key=os.getenv("OPENAI_API_KEY"),
            ai_model="gpt-4",
            memory_provider="local",
            debug_mode=True
        )
        
        if openai_config.ai_api_key:
            openai_agent = BaseAgent("GPTBot", openai_config, "I use OpenAI GPT with local memory")
            response = await openai_agent.think("Tell me about yourself")
            print(f"OpenAI agent: {response[:100]}...")
        else:
            print("OpenAI API key not found, skipping...")
    
    except Exception as e:
        print(f"OpenAI setup failed: {e}")
    
    # Example 3: Mock AI + Local memory (testing setup)
    print("\n3️⃣ Mock AI + Local Memory Configuration (for testing):")
    try:
        mock_config = FrameworkConfig(
            ai_provider="mock",
            ai_api_key="not-needed-for-mock",
            memory_provider="local",
            debug_mode=True
        )
        
        mock_agent = BaseAgent("MockBot", mock_config, "I use mock AI for testing")
        
        # Add some memories
        await mock_agent.add_memory("I am a test agent")
        await mock_agent.add_memory("I help with testing the framework")
        
        # Test memory retrieval
        memories = await mock_agent.search_memories("test")
        print(f"Mock agent found {len(memories)} memories about 'test'")
        
        # Generate response
        response = await mock_agent.think("Tell me about testing")
        print(f"Mock agent: {response}")
        
    except Exception as e:
        print(f"Mock setup failed: {e}")
    
    # Example 4: Configuration from dictionary
    print("\n4️⃣ Configuration from Dictionary:")
    config_dict = {
        "ai_provider": "mock",
        "ai_api_key": "test-key",
        "memory_provider": "local",
        "debug_mode": True,
        "max_memory_retrieval": 5
    }
    
    dict_config = FrameworkConfig.from_dict(config_dict)
    dict_agent = BaseAgent("DictBot", dict_config, "I was configured from a dictionary")
    
    response = await dict_agent.think("How were you configured?")
    print(f"Dictionary-configured agent: {response}")
    
    print("\n✅ Plugin example completed!")

if __name__ == "__main__":
    asyncio.run(plugin_example())



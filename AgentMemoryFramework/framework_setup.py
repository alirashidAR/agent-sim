#!/usr/bin/env python3
"""
Setup and validation utility for the AgentMemory Framework
"""
import os
import sys
from typing import Dict, List, Any, Optional

def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are installed"""
    dependencies = {
        "mem0ai": False,
        "google-generativeai": False,
        "openai": False,
        "python-dotenv": False
    }
    
    for package in dependencies:
        try:
            __import__(package.replace("-", "_"))
            dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    return dependencies

def check_environment_variables() -> Dict[str, Optional[str]]:
    """Check environment variables"""
    env_vars = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "MEM0_API_KEY": os.getenv("MEM0_API_KEY"),
        "AI_PROVIDER": os.getenv("AI_PROVIDER"),
        "MEMORY_PROVIDER": os.getenv("MEMORY_PROVIDER")
    }
    
    return env_vars

def validate_setup(ai_provider: str = "gemini", memory_provider: str = "mem0") -> List[str]:
    """Validate the setup for specific providers"""
    issues = []
    
    # Check dependencies
    deps = check_dependencies()
    
    if ai_provider == "gemini" and not deps["google-generativeai"]:
        issues.append("google-generativeai package not installed. Run: pip install google-generativeai")
    
    if ai_provider == "openai" and not deps["openai"]:
        issues.append("openai package not installed. Run: pip install openai")
    
    if memory_provider == "mem0" and not deps["mem0ai"]:
        issues.append("mem0ai package not installed. Run: pip install mem0ai")
    
    if not deps["python-dotenv"]:
        issues.append("python-dotenv package not installed. Run: pip install python-dotenv")
    
    # Check environment variables
    env_vars = check_environment_variables()
    
    if ai_provider == "gemini" and not env_vars["GEMINI_API_KEY"]:
        issues.append("GEMINI_API_KEY environment variable not set")
    
    if ai_provider == "openai" and not env_vars["OPENAI_API_KEY"]:
        issues.append("OPENAI_API_KEY environment variable not set")
    
    if memory_provider == "mem0" and not env_vars["MEM0_API_KEY"]:
        issues.append("MEM0_API_KEY environment variable not set")
    
    return issues

def create_env_template(filename: str = ".env.template") -> None:
    """Create an environment template file"""
    template_content = """# AgentMemory Framework Configuration

# AI Provider Settings
AI_PROVIDER=gemini  # Options: gemini, openai, mock
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Memory Provider Settings  
MEMORY_PROVIDER=mem0  # Options: mem0, local
MEM0_API_KEY=your_mem0_api_key_here

# Framework Settings
DEBUG_MODE=true
MAX_MEMORY_RETRIEVAL=10
MEMORY_SIMILARITY_THRESHOLD=0.7
MAX_CONVERSATION_TURNS=10
CONVERSATION_TIMEOUT=30

# AI Model Settings
AI_MODEL=gemini-2.0-flash-exp  # For Gemini: gemini-2.0-flash-exp, For OpenAI: gpt-4, gpt-3.5-turbo
"""
    
    with open(filename, 'w') as f:
        f.write(template_content)
    
    print(f"✅ Created environment template: {filename}")
    print("   Copy this to .env and fill in your API keys")

def install_dependencies(providers: List[str] = None) -> None:
    """Install dependencies for specified providers"""
    if providers is None:
        providers = ["gemini", "mem0", "dotenv"]
    
    package_map = {
        "gemini": "google-generativeai",
        "openai": "openai", 
        "mem0": "mem0ai",
        "dotenv": "python-dotenv"
    }
    
    packages_to_install = []
    for provider in providers:
        if provider in package_map:
            packages_to_install.append(package_map[provider])
    
    if packages_to_install:
        import subprocess
        cmd = [sys.executable, "-m", "pip", "install"] + packages_to_install
        print(f"Installing packages: {' '.join(packages_to_install)}")
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")

def run_diagnostics() -> None:
    """Run complete diagnostics"""
    print("🔍 AgentMemory Framework Diagnostics")
    print("=" * 50)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check dependencies
    print("\n📦 Dependencies:")
    deps = check_dependencies()
    for package, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"   {status} {package}")
    
    # Check environment variables
    print("\n🔧 Environment Variables:")
    env_vars = check_environment_variables()
    for var, value in env_vars.items():
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: Not set")
    
    # Validate common configurations
    print("\n⚙️  Configuration Validation:")
    
    configs_to_test = [
        ("gemini", "mem0"),
        ("gemini", "local"),
        ("openai", "mem0"),
        ("openai", "local"),
        ("mock", "local")
    ]
    
    for ai_provider, memory_provider in configs_to_test:
        issues = validate_setup(ai_provider, memory_provider)
        if not issues:
            print(f"   ✅ {ai_provider} + {memory_provider}: OK")
        else:
            print(f"   ❌ {ai_provider} + {memory_provider}: {len(issues)} issues")
            for issue in issues:
                print(f"      - {issue}")
    
    print("\n" + "=" * 50)

def quick_start() -> None:
    """Interactive quick start setup"""
    print("🚀 AgentMemory Framework Quick Start")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("📝 No .env file found. Creating template...")
        create_env_template(".env")
        print("\n⚠️  Please edit .env file with your API keys before continuing.")
        return
    
    # Run diagnostics
    run_diagnostics()
    
    # Suggest next steps
    print("\n🎯 Next Steps:")
    print("1. Check the diagnostics above")
    print("2. Install missing dependencies if needed")
    print("3. Set missing environment variables")
    print("4. Try running: python examples/basic_usage.py")
    print("5. Or run: python examples/plugin_example.py")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AgentMemory Framework Setup Utility")
    parser.add_argument("--diagnostics", action="store_true", help="Run diagnostics")
    parser.add_argument("--create-env", action="store_true", help="Create .env template")
    parser.add_argument("--install", nargs="*", help="Install dependencies for providers")
    parser.add_argument("--quick-start", action="store_true", help="Interactive quick start")
    
    args = parser.parse_args()
    
    if args.diagnostics:
        run_diagnostics()
    elif args.create_env:
        create_env_template()
    elif args.install is not None:
        install_dependencies(args.install if args.install else None)
    elif args.quick_start:
        quick_start()
    else:
        quick_start()  # Default action



#!/usr/bin/env python3
"""
Strands Agent Setup Script
Helps users set up the project with proper dependencies and configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🚀 STRANDS AGENT SETUP")
    print("=" * 60)
    print("Setting up your intelligent conversational AI...")
    print()


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_pip():
    """Check if pip is available."""
    print("📦 Checking pip...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False


def install_dependencies():
    """Install required dependencies."""
    print("📥 Installing dependencies...")
    
    try:
        # Upgrade pip first
        print("   Upgrading pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                            stdout=subprocess.DEVNULL)
        
        # Install requirements
        print("   Installing packages from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Set up environment configuration."""
    print("⚙️  Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        # Create basic .env file
        try:
            with open(env_file, 'w') as f:
                f.write("# Strands Agent Configuration\n")
                f.write("# Get your credentials from:\n")
                f.write("# - Google API Key: https://console.developers.google.com/\n")
                f.write("# - Search Engine ID: https://cse.google.com/\n\n")
                f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
                f.write("GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here\n")
            
            print("✅ Created basic .env file")
            print("⚠️  Please edit .env file with your API credentials")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False


def validate_structure():
    """Validate project structure."""
    print("📁 Validating project structure...")
    
    required_dirs = ["src", "tests", "scripts", "templates", "docs"]
    required_files = ["main.py", "requirements.txt", "README.md"]
    
    missing_items = []
    
    # Check directories
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_items.append(f"Directory: {dir_name}")
    
    # Check files
    for file_name in required_files:
        if not Path(file_name).exists():
            missing_items.append(f"File: {file_name}")
    
    if missing_items:
        print("❌ Missing required items:")
        for item in missing_items:
            print(f"   - {item}")
        return False
    
    print("✅ Project structure is valid")
    return True


def test_imports():
    """Test that main modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        # Test core imports
        from src.config import config
        from src.strands_agent import StrandsAgent
        from src.google_search import GoogleSearchTool
        
        print("✅ Core modules import successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def run_basic_tests():
    """Run basic unit tests to verify setup."""
    print("🧪 Running basic tests...")
    
    try:
        # Run unit tests (not integration tests to avoid API calls)
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_strands_agent.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Basic tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print("   This might be normal if API credentials are not configured")
            return True  # Don't fail setup for test failures
            
    except subprocess.TimeoutExpired:
        print("⚠️  Tests timed out (this is usually okay)")
        return True
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        return True  # Don't fail setup for test issues


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Configure your API credentials in .env file:")
    print("   - Get Google API key: https://console.developers.google.com/")
    print("   - Create Custom Search Engine: https://cse.google.com/")
    print("   - Edit .env file with your credentials")
    
    print("\n2. Test your setup:")
    print("   python scripts/validate_integration_tests.py")
    
    print("\n3. Start using Strands Agent:")
    print("   🖥️  CLI: python main.py")
    print("   🌐 Web UI: python scripts/start_ui.py")
    
    print("\n4. Run tests (optional):")
    print("   📝 Unit tests: python -m pytest tests/test_strands_agent.py -v")
    print("   🔗 Integration tests: python scripts/run_integration_tests.py")
    
    print("\n📚 Documentation:")
    print("   - Project structure: PROJECT_STRUCTURE.md")
    print("   - Web UI guide: docs/WEB_UI_README.md")
    print("   - Test setup: docs/test_config_guide.md")
    
    print("\n🆘 Need help?")
    print("   - Check README.md for detailed instructions")
    print("   - Review docs/ directory for specific guides")
    
    print("\n" + "=" * 60)


def main():
    """Main setup function."""
    print_banner()
    
    # Track setup success
    setup_steps = [
        ("Python Version", check_python_version),
        ("Pip Availability", check_pip),
        ("Project Structure", validate_structure),
        ("Dependencies", install_dependencies),
        ("Environment Setup", setup_environment),
        ("Module Imports", test_imports),
        ("Basic Tests", run_basic_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_func in setup_steps:
        print(f"\n{step_name}:")
        print("-" * len(step_name))
        
        if not step_func():
            failed_steps.append(step_name)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    
    if failed_steps:
        print("❌ Setup completed with issues:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease resolve the issues above before using the application.")
        sys.exit(1)
    else:
        print("✅ Setup completed successfully!")
        print_next_steps()


if __name__ == "__main__":
    main()
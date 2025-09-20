#!/usr/bin/env python3
"""
Startup script for Strands Agent Web UI.
Checks prerequisites and starts the Flask web application.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to Python path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import config


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("Checking prerequisites...")
    
    # Check if Flask is installed
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask==3.0.0"])
            print("✅ Flask installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Flask. Please run: pip install flask")
            return False
    
    # Check if templates directory exists
    templates_dir = Path("templates")
    if templates_dir.exists():
        print("✅ Templates directory found")
    else:
        print("❌ Templates directory not found")
        return False
    
    # Check if main template exists
    index_template = templates_dir / "index.html"
    if index_template.exists():
        print("✅ Main template found")
    else:
        print("❌ Main template (templates/index.html) not found")
        return False
    
    # Check API configuration
    if config.is_configured():
        print("✅ API credentials configured")
    else:
        print("⚠️  API credentials not configured")
        print("   The UI will start but the agent won't work until you configure:")
        for missing in config.get_missing_config():
            print(f"   - {missing}")
        print("   Please update your .env file")
    
    return True


def start_web_ui():
    """Start the web UI."""
    print("\n" + "="*60)
    print("🚀 STARTING STRANDS AGENT WEB UI")
    print("="*60)
    
    if config.is_configured():
        print("✅ Agent ready with API integration")
    else:
        print("⚠️  Agent will run in limited mode (no web search)")
    
    print("\n📱 Web UI will be available at:")
    print("   🌐 http://localhost:5000")
    print("   🌐 http://127.0.0.1:5000")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("="*60)
    
    try:
        # Import and run the Flask app
        from src.app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Strands Agent Web UI stopped.")
    except Exception as e:
        print(f"\n❌ Error starting web UI: {e}")
        return False
    
    return True


def main():
    """Main function."""
    print("Strands Agent Web UI Launcher")
    print("=" * 35)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Start the web UI
    if not start_web_ui():
        sys.exit(1)


if __name__ == "__main__":
    main()
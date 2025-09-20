#!/usr/bin/env python3
"""
Simple web UI launcher for Strands Agent.
Runs the Flask application from the correct directory with proper imports.
"""

import os
import sys
from pathlib import Path

def main():
    """Launch the web UI."""
    print("🚀 Starting Strands Agent Web UI...")
    
    # Change to src directory for proper imports
    src_dir = Path(__file__).parent / 'src'
    os.chdir(src_dir)
    
    # Add src to Python path
    sys.path.insert(0, str(src_dir))
    
    try:
        # Import and run the Flask app
        from app import app
        
        print("🌐 Web UI available at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop")
        
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Web UI stopped.")
    except Exception as e:
        print(f"❌ Error starting web UI: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
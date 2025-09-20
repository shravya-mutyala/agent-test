#!/usr/bin/env python3
"""
Standalone Flask web application for Strands Agent UI.
Simple, self-contained web interface that works from the project root.
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
import logging

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    from strands_agent import StrandsAgent
    from google_search import GoogleSearchError, RateLimitError
    from config import config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the project root directory.")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Flask app
app = Flask(__name__, template_folder='templates')
app.secret_key = 'strands-agent-secret-key-change-in-production'

# Initialize the agent
agent = None
try:
    if config.is_configured():
        agent = StrandsAgent(config.google_api_key, config.search_engine_id)
        logger.info("Strands Agent initialized successfully")
    else:
        logger.warning("API credentials not configured - agent will not be available")
except Exception as e:
    logger.error(f"Failed to initialize Strands Agent: {e}")


@app.route('/')
def index():
    """Main chat interface page."""
    # Initialize session if needed
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle user questions and return agent responses."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Please enter a question.'
            })
        
        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not available. Please check API configuration.'
            })
        
        # Get response from agent
        logger.info(f"Processing question: {question[:100]}...")
        response = agent.ask(question)
        
        # Store in session history
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'question': question,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 exchanges to prevent session bloat
        if len(session['chat_history']) > 20:
            session['chat_history'] = session['chat_history'][-20:]
        
        session.modified = True
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({
            'success': False,
            'error': 'Sorry, I encountered an error processing your question. Please try again.'
        })


@app.route('/clear', methods=['POST'])
def clear_chat():
    """Clear chat history."""
    session['chat_history'] = []
    session.modified = True
    return jsonify({'success': True})


@app.route('/status')
def status():
    """Check agent status."""
    return jsonify({
        'agent_available': agent is not None,
        'api_configured': config.is_configured(),
        'missing_config': config.get_missing_config() if not config.is_configured() else []
    })


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please check the console for details.'
    }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Page not found.'
    }), 404


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("Checking web UI prerequisites...")
    
    # Check templates directory
    templates_dir = Path("templates")
    if not templates_dir.exists():
        print("❌ Templates directory not found")
        return False
    
    # Check main template
    index_template = templates_dir / "index.html"
    if not index_template.exists():
        print("❌ Main template (templates/index.html) not found")
        return False
    
    print("✅ Templates found")
    
    # Check API configuration
    if config.is_configured():
        print("✅ API credentials configured")
    else:
        print("⚠️  API credentials not configured")
        print("   The UI will start but the agent won't work until you configure:")
        for missing in config.get_missing_config():
            print(f"   - {missing}")
    
    return True


def main():
    """Main function to start the web UI."""
    print("=" * 60)
    print("🌐 STRANDS AGENT WEB UI")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    print("\n🚀 Starting web server...")
    
    if agent:
        print("✅ Agent ready with API integration")
    else:
        print("⚠️  Agent will run in limited mode (no web search)")
    
    print("\n📱 Web UI will be available at:")
    print("   🌐 http://localhost:5000")
    print("   🌐 http://127.0.0.1:5000")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Strands Agent Web UI stopped.")
    except Exception as e:
        print(f"\n❌ Error starting web UI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
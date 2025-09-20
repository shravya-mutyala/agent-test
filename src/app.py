"""
Flask web application for Strands Agent UI.
Provides a simple chat interface for interacting with the agent.
"""

from flask import Flask, render_template, request, jsonify, session
import uuid
from datetime import datetime
from strands_agent import StrandsAgent
from config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os

# Configure Flask to look for templates in the correct directory
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'strands-agent-secret-key-change-in-production'

# Initialize the agent
try:
    if config.is_configured():
        agent = StrandsAgent(config.google_api_key, config.search_engine_id)
        logger.info("Strands Agent initialized successfully")
    else:
        agent = None
        logger.warning("API credentials not configured - agent will not be available")
except Exception as e:
    agent = None
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


if __name__ == '__main__':
    print("Starting Strands Agent Web UI...")
    print("=" * 50)
    
    if not config.is_configured():
        print("⚠️  WARNING: API credentials not configured!")
        print("The web interface will start but the agent won't work.")
        print("Please configure your .env file with:")
        for missing in config.get_missing_config():
            print(f"  - {missing}")
        print()
    
    if agent:
        print("✅ Strands Agent ready!")
    else:
        print("❌ Strands Agent not available")
    
    print("🌐 Starting web server...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
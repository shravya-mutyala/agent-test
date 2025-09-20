#!/usr/bin/env python3
"""
Strands Agent CLI Interface
A simple command-line interface for testing the Strands Agent functionality.
"""

import sys
import os
import argparse
from typing import Optional

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import config
from strands_agent import StrandsAgent
from google_search import GoogleSearchError, RateLimitError


def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("🔍 STRANDS AGENT - Real-time Information Assistant")
    print("=" * 60)
    print("Ask questions and get answers with current information!")
    print()


def print_help():
    """Print detailed help information"""
    print("USAGE:")
    print("  python main.py                    # Start interactive mode")
    print("  python main.py --question 'text' # Ask a single question")
    print("  python main.py --help            # Show this help")
    print()
    print("EXAMPLES:")
    print("  python main.py --question 'What are the latest AWS certification discounts?'")
    print("  python main.py --question 'Current Azure pricing for virtual machines'")
    print("  python main.py --question 'Tell me about cloud computing'")
    print()
    print("CONFIGURATION:")
    print("  Set up your .env file with:")
    print("  - GOOGLE_API_KEY=your_api_key")
    print("  - GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id")
    print()
    print("INTERACTIVE MODE COMMANDS:")
    print("  help     - Show help information")
    print("  config   - Show configuration status")
    print("  clear    - Clear the screen")
    print("  quit     - Exit the application")
    print("  exit     - Exit the application")
    print()


def check_configuration() -> bool:
    """
    Check if the application is properly configured
    
    Returns:
        True if configured, False otherwise
    """
    if config.is_configured():
        print("✅ Configuration: All required settings found")
        return True
    else:
        print("❌ Configuration: Missing required settings")
        missing = config.get_missing_config()
        print(f"   Missing: {', '.join(missing)}")
        print()
        print("📝 Setup Instructions:")
        print("   1. Copy .env.example to .env")
        print("   2. Get a Google API key from: https://console.developers.google.com/")
        print("   3. Create a Custom Search Engine at: https://cse.google.com/")
        print("   4. Add your credentials to the .env file")
        print()
        return False


def show_config_status():
    """Display current configuration status"""
    print("\n📋 Configuration Status:")
    print("-" * 30)
    
    if config.google_api_key:
        # Show partial API key for security
        masked_key = config.google_api_key[:8] + "..." + config.google_api_key[-4:] if len(config.google_api_key) > 12 else "***"
        print(f"Google API Key: {masked_key}")
    else:
        print("Google API Key: ❌ Not set")
    
    if config.search_engine_id:
        # Show partial search engine ID
        masked_id = config.search_engine_id[:6] + "..." + config.search_engine_id[-4:] if len(config.search_engine_id) > 10 else "***"
        print(f"Search Engine ID: {masked_id}")
    else:
        print("Search Engine ID: ❌ Not set")
    
    print(f"Status: {'✅ Ready' if config.is_configured() else '❌ Incomplete'}")
    print()


def ask_question(agent: StrandsAgent, question: str) -> None:
    """
    Ask a question to the agent and display the response
    
    Args:
        agent: The StrandsAgent instance
        question: The question to ask
    """
    if not question.strip():
        print("❌ Please provide a non-empty question.")
        return
    
    print(f"\n🤔 Question: {question}")
    print("\n🔍 Processing...")
    
    try:
        response = agent.ask(question)
        print(f"\n💡 Answer:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
    except (GoogleSearchError, RateLimitError) as e:
        print(f"\n❌ Search Error: {e}")
        print("💡 Try asking a different question or check your API configuration.")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print("💡 Please try again or contact support if the issue persists.")


def interactive_mode(agent: StrandsAgent) -> None:
    """
    Run the agent in interactive mode
    
    Args:
        agent: The StrandsAgent instance
    """
    print("🎯 Interactive Mode - Type your questions below")
    print("💡 Type 'help' for commands, 'quit' or 'exit' to leave")
    print()
    
    while True:
        try:
            # Get user input
            question = input("❓ Your question: ").strip()
            
            # Handle empty input
            if not question:
                continue
            
            # Handle special commands
            if question.lower() in ['quit', 'exit']:
                print("\n👋 Goodbye! Thanks for using Strands Agent!")
                break
                
            elif question.lower() == 'help':
                print_help()
                continue
                
            elif question.lower() == 'config':
                show_config_status()
                continue
                
            elif question.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                print_banner()
                continue
            
            # Process the question
            ask_question(agent, question)
            print()  # Add spacing between questions
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using Strands Agent!")
            break
            
        except EOFError:
            print("\n\n👋 Goodbye! Thanks for using Strands Agent!")
            break


def single_question_mode(agent: StrandsAgent, question: str) -> None:
    """
    Ask a single question and exit
    
    Args:
        agent: The StrandsAgent instance
        question: The question to ask
    """
    ask_question(agent, question)


def create_agent() -> Optional[StrandsAgent]:
    """
    Create and initialize the StrandsAgent
    
    Returns:
        StrandsAgent instance if successful, None otherwise
    """
    try:
        print("🚀 Initializing Strands Agent...")
        
        # Create agent with credential validation
        agent = StrandsAgent(
            google_api_key=config.google_api_key,
            search_engine_id=config.search_engine_id,
            validate_credentials=True  # Test credentials during initialization
        )
        
        print("✅ Agent initialized successfully!")
        return agent
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Please check your .env file and API credentials.")
        return None
        
    except GoogleSearchError as e:
        print(f"❌ API Error: {e}")
        print("💡 Please verify your Google API key and search engine ID.")
        return None
        
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        print("💡 Please check your configuration and try again.")
        return None


def main():
    """Main application entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Strands Agent - Real-time Information Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --question "What are the latest AWS certification discounts?"
  python main.py --question "Current Azure pricing"

Configuration:
  Create a .env file with your Google API credentials:
  GOOGLE_API_KEY=your_api_key
  GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
        """
    )
    
    parser.add_argument(
        '--question', '-q',
        type=str,
        help='Ask a single question and exit'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Skip the banner display'
    )
    
    args = parser.parse_args()
    
    # Show banner unless suppressed
    if not args.no_banner:
        print_banner()
    
    # Check configuration
    if not check_configuration():
        print("❌ Cannot start without proper configuration.")
        sys.exit(1)
    
    # Create agent
    agent = create_agent()
    if not agent:
        print("❌ Failed to initialize agent.")
        sys.exit(1)
    
    # Run in appropriate mode
    if args.question:
        # Single question mode
        single_question_mode(agent, args.question)
    else:
        # Interactive mode
        interactive_mode(agent)


if __name__ == "__main__":
    main()
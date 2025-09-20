"""
Strands Agent - Intelligent conversational AI with real-time web search capabilities.

This package provides a conversational AI agent that combines static knowledge
with real-time web search using Google Custom Search API.
"""

__version__ = "1.0.0"
__author__ = "Strands Agent Team"
__description__ = "Intelligent conversational AI with real-time web search"

# Import with proper error handling for different execution contexts
try:
    from .strands_agent import StrandsAgent
    from .google_search import GoogleSearchTool, GoogleSearchError, RateLimitError
    from .config import config
except ImportError:
    # Fallback for when running from src directory
    from strands_agent import StrandsAgent
    from google_search import GoogleSearchTool, GoogleSearchError, RateLimitError
    from config import config

__all__ = [
    'StrandsAgent',
    'GoogleSearchTool', 
    'GoogleSearchError',
    'RateLimitError',
    'config'
]
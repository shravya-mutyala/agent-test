"""
Strands Agent - A conversational AI that combines static knowledge with real-time web search.
Intelligently routes queries to Google Search when current information is needed.
"""

from typing import Optional
import logging
from google_search import GoogleSearchTool, GoogleSearchError, RateLimitError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrandsAgent:
    """
    Main agent class that handles user questions by determining whether to use
    static knowledge or perform web searches for current information.
    """
    
    def __init__(self, google_api_key: str, search_engine_id: str, validate_credentials: bool = False):
        """
        Initialize the Strands Agent with comprehensive validation.
        
        Args:
            google_api_key: Google API key for Custom Search API
            search_engine_id: Custom Search Engine ID
            validate_credentials: Whether to test API credentials during initialization
            
        Raises:
            ValueError: If API credentials are invalid or missing
            GoogleSearchError: If credential validation fails
        """
        if not google_api_key or not search_engine_id:
            raise ValueError("Google API key and search engine ID are required")
            
        try:
            self.google_search = GoogleSearchTool(google_api_key, search_engine_id)
            
            # Optionally validate credentials during initialization
            if validate_credentials:
                logger.info("Validating API credentials...")
                if not self.google_search.test_connection():
                    raise GoogleSearchError("API credential validation failed. Please check your Google API key and search engine ID.")
                logger.info("API credentials validated successfully")
            
            logger.info("Strands Agent initialized successfully")
            
        except ValueError as e:
            logger.error(f"Initialization failed due to invalid parameters: {e}")
            raise
        except GoogleSearchError as e:
            logger.error(f"Initialization failed due to API issues: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {e}")
            raise ValueError(f"Failed to initialize Strands Agent: {str(e)}")
    
    def ask(self, question: str) -> str:
        """
        Main user interface method. Processes a user question and returns an answer.
        Includes comprehensive input validation and error handling.
        
        Args:
            question: User's question as a string
            
        Returns:
            String response to the user's question
        """
        # Enhanced input validation
        if question is None:
            return "I didn't receive a question. Could you please ask me something?"
            
        if not isinstance(question, str):
            return "I can only process text questions. Please provide your question as text."
            
        if not question.strip():
            return "Your question appears to be empty. Could you please ask me something specific?"
            
        question = question.strip()
        
        # Check for extremely long questions
        if len(question) > 1000:
            return "Your question is quite long. Could you please make it more concise (under 1000 characters)?"
            
        # Check for very short questions that might not be meaningful
        if len(question) < 3:
            return "Your question seems very short. Could you provide more details so I can help you better?"
            
        logger.info(f"Processing question: {question[:100]}{'...' if len(question) > 100 else ''}")
        
        try:
            # Determine if the question needs current information
            if self._needs_search(question):
                logger.info("Question requires web search for current information")
                return self._search_and_answer(question)
            else:
                logger.info("Question can be answered with static knowledge")
                return self._static_answer(question)
                
        except ValueError as e:
            logger.warning(f"Validation error processing question: {e}")
            return f"I noticed an issue with your question: {str(e)}. Could you please rephrase it?"
            
        except (GoogleSearchError, RateLimitError) as e:
            logger.error(f"Search service error: {e}")
            return self._fallback_response(question, "search_error")
            
        except Exception as e:
            logger.error(f"Unexpected error processing question: {e}")
            return self._fallback_response(question, "unexpected_error")
    
    def _needs_search(self, question: str) -> bool:
        """
        Determines if a question requires real-time web search based on keyword detection.
        
        Args:
            question: User's question as a string
            
        Returns:
            True if the question likely needs current information, False otherwise
        """
        # Keywords that strongly indicate need for current/real-time information
        search_keywords = [
            'latest', 'current', 'recent', 'today', 'this month', 'this year',
            'now', 'discount', 'price', 'pricing', 'cost', 'deal', 'deals',
            'new', 'updated', 'announcement', 'news', 'breaking', 'just',
            'voucher', 'promotion', 'sale', 'availability', 'available', 
            'release', 'launched', 'upcoming'
        ]
        
        question_lower = question.lower()
        
        # Check if any search keywords are present
        has_search_keywords = any(keyword in question_lower for keyword in search_keywords)
        
        # If question has search keywords, definitely search
        if has_search_keywords:
            return True
            
        # Additional patterns that suggest need for current info when combined with pricing/time questions
        pricing_patterns = ['how much', 'what does it cost', 'what is the cost']
        time_patterns = ['when is', 'when will', 'when can']
        
        has_pricing_patterns = any(pattern in question_lower for pattern in pricing_patterns)
        has_time_patterns = any(pattern in question_lower for pattern in time_patterns)
        
        # If question asks about pricing or timing, likely needs current info
        if has_pricing_patterns or has_time_patterns:
            return True
        
        # For general "tell me about" or "what is" questions, use static knowledge
        general_patterns = ['tell me about', 'what is', 'what are', 'explain', 'describe']
        if any(pattern in question_lower for pattern in general_patterns):
            # Only search if it also has time-sensitive keywords
            return False
        
        return False
    
    def _static_answer(self, question: str) -> str:
        """
        Provides answers using static knowledge for questions that don't require current information.
        
        Args:
            question: User's question as a string
            
        Returns:
            Static response based on general knowledge
        """
        question_lower = question.lower()
        
        # Basic static responses for common question patterns
        if any(word in question_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm the Strands Agent. I can help you with questions about technology, certifications, and current information. What would you like to know?"
        
        if any(word in question_lower for word in ['help', 'what can you do']):
            return "I can help you with questions about technology topics, especially when you need current information. I can search the web for the latest pricing, deals, certification information, and more. Just ask me anything!"
        
        if 'aws' in question_lower and 'certification' in question_lower:
            return "AWS offers various certification paths including Cloud Practitioner, Solutions Architect, Developer, and SysOps Administrator at the Associate level, plus Professional and Specialty certifications. For current pricing and exam details, I'd need to search for the latest information."
        
        if 'azure' in question_lower and 'certification' in question_lower:
            return "Microsoft Azure certifications include Fundamentals, Associate, and Expert levels covering roles like Administrator, Developer, Solutions Architect, and more. For current exam information and pricing, I can search for the latest details."
        
        if 'google cloud' in question_lower and 'certification' in question_lower:
            return "Google Cloud offers certifications for Cloud Engineer, Cloud Architect, Data Engineer, and other specialized roles. For current exam information and pricing, I can search for the latest details."
        
        # Generic response for questions that don't match patterns
        return "I can help with that, but I might need to search for current information to give you the most accurate answer. Could you be more specific about what you're looking for?"
    
    def _search_and_answer(self, question: str) -> str:
        """
        Performs web search and generates answer for questions requiring current information.
        Implements comprehensive error handling with fallback to static knowledge.
        
        Args:
            question: User's question as a string
            
        Returns:
            Summarized answer based on search results with source citations, or fallback response
        """
        try:
            # Validate search query before attempting search
            if not question or len(question.strip()) < 3:
                return "Your question seems too short. Could you please provide more details so I can search for better information?"
            
            # Perform the search
            logger.info(f"Searching for current information about: {question}")
            search_results = self.google_search.search(question, num_results=5)
            
            # Validate search results
            if not search_results:
                logger.warning("No search results found, attempting fallback response")
                return self._fallback_response(question, "no_results")
            
            # Validate that we have meaningful results
            valid_results = [r for r in search_results if r.snippet and r.snippet.strip() and r.snippet != 'No description available']
            if not valid_results:
                logger.warning("No meaningful search results found, attempting fallback response")
                return self._fallback_response(question, "no_meaningful_results")
            
            # Generate summary from search results
            summary = self.google_search.summarize_results(valid_results, question)
            
            # Validate generated summary
            if not summary or len(summary.strip()) < 10:
                logger.warning("Generated summary is too short, attempting fallback response")
                return self._fallback_response(question, "poor_summary")
            
            logger.info("Successfully generated answer from search results")
            return summary
            
        except RateLimitError as e:
            logger.warning(f"Rate limit error: {e}")
            return self._fallback_response(question, "rate_limit")
            
        except GoogleSearchError as e:
            logger.error(f"Search error: {e}")
            return self._fallback_response(question, "search_error")
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return f"I noticed an issue with your question: {str(e)}. Could you please rephrase it?"
            
        except Exception as e:
            logger.error(f"Unexpected error in search and answer: {e}")
            return self._fallback_response(question, "unexpected_error")
    
    def _fallback_response(self, question: str, error_type: str) -> str:
        """
        Provides fallback responses when search fails, attempting to use static knowledge.
        
        Args:
            question: Original user question
            error_type: Type of error that triggered the fallback
            
        Returns:
            Fallback response with helpful information
        """
        logger.info(f"Providing fallback response for error type: {error_type}")
        
        # Try to provide static knowledge first
        try:
            static_response = self._static_answer(question)
            
            # If static response is generic, enhance it with error context
            if "I can help with that" in static_response or "Could you be more specific" in static_response:
                # Provide error-specific fallback messages
                if error_type == "rate_limit":
                    return "I'm currently experiencing high demand and can't search for the latest information right now. However, I can share some general knowledge: " + static_response
                elif error_type == "no_results":
                    return "I couldn't find current information about that specific topic, but here's what I can tell you: " + static_response
                elif error_type == "no_meaningful_results":
                    return "The search results weren't very helpful, but I can provide some general information: " + static_response
                elif error_type == "search_error":
                    return "I'm having trouble accessing current information right now, but here's what I know: " + static_response
                else:
                    return "I encountered an issue searching for current information, but let me share what I can: " + static_response
            else:
                # Static response is meaningful, just add a note about the search issue
                if error_type == "rate_limit":
                    return static_response + "\n\nNote: I'm currently unable to search for the very latest information due to high demand, but the above should still be helpful."
                elif error_type in ["no_results", "no_meaningful_results"]:
                    return static_response + "\n\nNote: I couldn't find current information about your specific question, but this general information should help."
                else:
                    return static_response + "\n\nNote: I'm currently unable to search for the latest information, but this should give you a good starting point."
                    
        except Exception as e:
            logger.error(f"Error in fallback response generation: {e}")
            
            # Final fallback messages based on error type
            fallback_messages = {
                "rate_limit": "I'm experiencing high demand right now and need to wait before searching. Please try again in a few moments, or feel free to ask a different question.",
                "no_results": "I couldn't find any current information about that topic. You might want to try rephrasing your question or checking official sources directly.",
                "no_meaningful_results": "I found some results but couldn't extract useful information from them. Could you try rephrasing your question or being more specific?",
                "search_error": "I'm having trouble accessing search services right now. Please try again later, or feel free to ask about something else.",
                "poor_summary": "I found some information but had trouble summarizing it clearly. You might want to try a more specific question or check the sources directly.",
                "unexpected_error": "I encountered an unexpected issue while processing your question. Please try again or rephrase your question."
            }
            
            return fallback_messages.get(error_type, "I'm having trouble processing your question right now. Please try again later or rephrase your question.")
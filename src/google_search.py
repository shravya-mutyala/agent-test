"""
Google Search API integration for the Strands Agent.
Provides search functionality using Google Custom Search API.
"""

import requests
import time
from dataclasses import dataclass
from typing import List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Structured representation of a search result."""
    title: str
    snippet: str
    url: str


class GoogleSearchError(Exception):
    """Custom exception for Google Search API errors."""
    pass


class RateLimitError(GoogleSearchError):
    """Exception raised when API rate limits are exceeded."""
    pass


class GoogleSearchTool:
    """
    Google Custom Search API integration tool.
    Handles search requests, rate limiting, and error handling.
    """
    
    def __init__(self, api_key: str, search_engine_id: str):
        """
        Initialize the Google Search Tool with comprehensive validation.
        
        Args:
            api_key: Google API key for Custom Search API
            search_engine_id: Custom Search Engine ID
            
        Raises:
            ValueError: If credentials are invalid or missing
        """
        # Enhanced credential validation
        if not api_key:
            raise ValueError("Google API key is required and cannot be empty")
            
        if not isinstance(api_key, str):
            raise ValueError("Google API key must be a string")
            
        if not search_engine_id:
            raise ValueError("Search engine ID is required and cannot be empty")
            
        if not isinstance(search_engine_id, str):
            raise ValueError("Search engine ID must be a string")
            
        # Basic format validation for API key (Google API keys typically start with 'AIza')
        if len(api_key.strip()) < 20:
            raise ValueError("Google API key appears to be too short (minimum 20 characters expected)")
            
        # Basic format validation for search engine ID
        search_engine_id = search_engine_id.strip()
        if len(search_engine_id) < 10:
            raise ValueError("Search engine ID appears to be too short (minimum 10 characters expected)")
            
        self.api_key = api_key.strip()
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum 100ms between requests
        
        logger.info("Google Search Tool initialized with validated credentials")
    
    def test_connection(self) -> bool:
        """
        Test the API connection with a simple search to validate credentials.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Perform a simple test search
            test_results = self.search("test", num_results=1)
            logger.info("API connection test successful")
            return True
        except (GoogleSearchError, RateLimitError) as e:
            logger.warning(f"API connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False
        
    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """
        Search Google using Custom Search API.
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 10)
            
        Returns:
            List of SearchResult objects
            
        Raises:
            GoogleSearchError: For API errors
            RateLimitError: When rate limits are exceeded
            ValueError: For invalid parameters
        """
        # Enhanced input validation
        if not query:
            raise ValueError("Search query cannot be None")
            
        if not isinstance(query, str):
            raise ValueError("Search query must be a string")
            
        query = query.strip()
        if not query:
            raise ValueError("Search query cannot be empty or only whitespace")
            
        if len(query) < 2:
            raise ValueError("Search query must be at least 2 characters long")
            
        if len(query) > 500:
            raise ValueError("Search query is too long (maximum 500 characters)")
            
        # Check for potentially problematic characters
        if any(char in query for char in ['<', '>', '{', '}', '[', ']']):
            logger.warning(f"Query contains potentially problematic characters: {query}")
            
        if not isinstance(num_results, int):
            raise ValueError("Number of results must be an integer")
            
        if num_results < 1 or num_results > 10:
            raise ValueError("Number of results must be between 1 and 10")
            
        # Rate limiting - ensure minimum interval between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
            
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query.strip(),
                'num': num_results
            }
            
            logger.info(f"Searching for: {query}")
            response = requests.get(self.base_url, params=params, timeout=10)
            self.last_request_time = time.time()
            
            # Handle different HTTP status codes with detailed error messages
            if response.status_code == 429:
                raise RateLimitError("Search API rate limit exceeded. Please wait a moment before trying again.")
            elif response.status_code == 403:
                try:
                    error_data = response.json() if response.content else {}
                    error_reason = error_data.get('error', {}).get('errors', [{}])[0].get('reason', 'unknown')
                    
                    if 'quota' in error_reason.lower() or 'limit' in error_reason.lower():
                        raise RateLimitError("Daily search quota exceeded. Please try again tomorrow or check your API usage limits.")
                    elif 'credentials' in error_reason.lower() or 'key' in error_reason.lower():
                        raise GoogleSearchError("Invalid API credentials. Please check your Google API key and search engine ID.")
                    elif 'disabled' in error_reason.lower():
                        raise GoogleSearchError("Search API is disabled for this project. Please enable the Custom Search API in Google Cloud Console.")
                    else:
                        raise GoogleSearchError(f"Access forbidden: {error_reason}. Please check your API configuration.")
                except (ValueError, KeyError):
                    raise GoogleSearchError("Access forbidden. Please verify your API credentials and permissions.")
            elif response.status_code == 400:
                try:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get('error', {}).get('message', 'Invalid request')
                    raise GoogleSearchError(f"Invalid search request: {error_message}")
                except (ValueError, KeyError):
                    raise GoogleSearchError("Invalid search request. Please check your search parameters.")
            elif response.status_code == 404:
                raise GoogleSearchError("Search service not found. Please verify your search engine ID.")
            elif response.status_code >= 500:
                raise GoogleSearchError("Google Search service is temporarily unavailable. Please try again later.")
            elif response.status_code != 200:
                raise GoogleSearchError(f"Search request failed with status {response.status_code}. Please try again.")
                
            data = response.json()
            
            # Check for API errors in response
            if 'error' in data:
                error_info = data['error']
                error_message = error_info.get('message', 'Unknown API error')
                raise GoogleSearchError(f"API error: {error_message}")
                
            # Extract search results
            results = []
            items = data.get('items', [])
            
            if not items:
                logger.warning(f"No search results found for query: {query}")
                return results
                
            for item in items:
                try:
                    result = SearchResult(
                        title=item.get('title', 'No title'),
                        snippet=item.get('snippet', 'No description available'),
                        url=item.get('link', '')
                    )
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Error parsing search result item: {e}")
                    continue
                    
            logger.info(f"Retrieved {len(results)} search results")
            return results
            
        except requests.exceptions.Timeout:
            raise GoogleSearchError("Search request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            raise GoogleSearchError("Network connection error. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise GoogleSearchError(f"Request failed: {str(e)}")
        except Exception as e:
            if isinstance(e, (GoogleSearchError, RateLimitError, ValueError)):
                raise
            raise GoogleSearchError(f"Unexpected error during search: {str(e)}")
    
    def summarize_results(self, results: List[SearchResult], original_question: str) -> str:
        """
        Create a summary answer from search results by combining and synthesizing information.
        Includes comprehensive validation and error handling for result processing.
        
        Args:
            results: List of SearchResult objects
            original_question: The original user question for context
            
        Returns:
            Summarized answer with source citations
            
        Raises:
            ValueError: If results are invalid or cannot be processed
        """
        # Validate inputs
        if not results:
            raise ValueError("No search results provided for summarization")
            
        if not original_question or not original_question.strip():
            raise ValueError("Original question is required for context")
            
        # Process snippets and sources with enhanced validation
        processed_info = []
        sources = []
        processing_errors = []
        
        for i, result in enumerate(results):
            try:
                # Validate result structure
                if not hasattr(result, 'snippet') or not hasattr(result, 'url') or not hasattr(result, 'title'):
                    processing_errors.append(f"Result {i+1}: Invalid result structure")
                    continue
                
                # Validate snippet content
                if not result.snippet or result.snippet.strip() == '' or result.snippet == 'No description available':
                    processing_errors.append(f"Result {i+1}: No useful snippet content")
                    continue
                
                # Clean up snippet (remove extra whitespace, normalize)
                clean_snippet = ' '.join(result.snippet.split())
                
                # Validate snippet length and content quality
                if len(clean_snippet) < 10:
                    processing_errors.append(f"Result {i+1}: Snippet too short")
                    continue
                
                # Check for common low-quality snippet indicators
                low_quality_indicators = ['...', 'click here', 'read more', 'sign up', 'login required']
                if any(indicator in clean_snippet.lower() for indicator in low_quality_indicators) and len(clean_snippet) < 50:
                    processing_errors.append(f"Result {i+1}: Low quality snippet detected")
                    continue
                
                # Extract domain name for cleaner source citation
                try:
                    if result.url and result.url.strip():
                        domain = result.url.split('/')[2] if '/' in result.url else result.url
                        # Remove www. prefix for cleaner display
                        if domain.startswith('www.'):
                            domain = domain[4:]
                        # Validate domain format
                        if '.' not in domain or len(domain) < 3:
                            domain = 'Unknown source'
                    else:
                        domain = 'Unknown source'
                except (IndexError, AttributeError, ValueError):
                    domain = 'Unknown source'
                
                processed_info.append({
                    'snippet': clean_snippet,
                    'source': domain,
                    'url': result.url or '',
                    'title': result.title or 'Untitled'
                })
                sources.append(domain)
                
            except Exception as e:
                processing_errors.append(f"Result {i+1}: Processing error - {str(e)}")
                logger.warning(f"Error processing search result {i+1}: {e}")
                continue
        
        # Log processing errors for debugging
        if processing_errors:
            logger.warning(f"Search result processing issues: {'; '.join(processing_errors)}")
        
        # Validate that we have usable processed information
        if not processed_info:
            if processing_errors:
                raise ValueError(f"Could not process any search results: {'; '.join(processing_errors[:3])}")
            else:
                raise ValueError("No usable information found in search results")
        
        try:
            # Synthesize information from multiple sources with error handling
            summary_parts = []
            
            # Look for common themes and information across sources
            # Use up to 3 most relevant snippets to create comprehensive answer
            for i, info in enumerate(processed_info[:3]):
                try:
                    snippet = info['snippet']
                    
                    # Validate snippet before processing
                    if not snippet or len(snippet.strip()) < 5:
                        continue
                    
                    # Truncate very long snippets but preserve key information
                    if len(snippet) > 250:
                        # Try to find a good breaking point (sentence end)
                        truncate_pos = snippet.rfind('.', 0, 250)
                        if truncate_pos > 100:  # Only use sentence break if it's not too early
                            snippet = snippet[:truncate_pos + 1]
                        else:
                            # Look for other good breaking points
                            for punct in [';', '!', '?']:
                                punct_pos = snippet.rfind(punct, 0, 250)
                                if punct_pos > 100:
                                    snippet = snippet[:punct_pos + 1]
                                    break
                            else:
                                # No good breaking point found, truncate with ellipsis
                                snippet = snippet[:247] + "..."
                    
                    summary_parts.append(snippet)
                    
                except Exception as e:
                    logger.warning(f"Error processing snippet {i+1}: {e}")
                    continue
            
            # Validate that we have summary parts
            if not summary_parts:
                raise ValueError("Could not create summary from any of the search results")
            
            # Combine information into coherent response with error handling
            try:
                if len(summary_parts) == 1:
                    summary = summary_parts[0]
                elif len(summary_parts) == 2:
                    # For two sources, connect them naturally
                    second_part = summary_parts[1]
                    # Ensure second part starts with lowercase if it's a continuation
                    if second_part and second_part[0].isupper() and not second_part.startswith(('The ', 'This ', 'That ', 'These ', 'Those ')):
                        second_part = second_part[0].lower() + second_part[1:]
                    summary = f"{summary_parts[0]} Additionally, {second_part}"
                else:
                    # For multiple sources, create structured summary
                    primary_info = summary_parts[0]
                    additional_parts = []
                    
                    for part in summary_parts[1:]:
                        if part and part.strip():
                            # Clean up the part for combination
                            clean_part = part.strip()
                            if clean_part.endswith('.'):
                                clean_part = clean_part[:-1]
                            additional_parts.append(clean_part)
                    
                    if additional_parts:
                        additional_info = ". ".join(additional_parts)
                        summary = f"{primary_info} {additional_info}."
                    else:
                        summary = primary_info
                
                # Validate final summary
                if not summary or len(summary.strip()) < 10:
                    raise ValueError("Generated summary is too short or empty")
                
            except Exception as e:
                logger.error(f"Error combining summary parts: {e}")
                # Fallback: just use the first valid snippet
                summary = summary_parts[0] if summary_parts else "Unable to create summary"
            
            # Check for potential conflicting information indicators
            conflict_indicators = ['however', 'but', 'although', 'while', 'different', 'varies', 'depends', 'conflicting']
            has_potential_conflicts = any(indicator in summary.lower() for indicator in conflict_indicators)
            
            if has_potential_conflicts and len(processed_info) > 1:
                summary += " (Note: Information may vary between sources - please verify with official sources for the most accurate details.)"
            
            # Add source citations with unique sources
            try:
                unique_sources = list(dict.fromkeys(sources[:3]))  # Remove duplicates, preserve order
                valid_sources = [s for s in unique_sources if s and s != 'Unknown source']
                
                if valid_sources:
                    if len(valid_sources) == 1:
                        source_text = valid_sources[0]
                    else:
                        source_text = ", ".join(valid_sources)
                    
                    summary += f"\n\nSources: {source_text}"
                elif unique_sources:  # Has sources but they're all 'Unknown source'
                    summary += f"\n\nSources: {len(unique_sources)} web source{'s' if len(unique_sources) > 1 else ''}"
                    
            except Exception as e:
                logger.warning(f"Error adding source citations: {e}")
                # Continue without source citations rather than failing
            
            return summary
            
        except Exception as e:
            logger.error(f"Critical error in summary generation: {e}")
            # Final fallback - return basic information from first result
            if processed_info:
                first_result = processed_info[0]
                fallback_summary = first_result['snippet'][:200]
                if len(first_result['snippet']) > 200:
                    fallback_summary += "..."
                return f"{fallback_summary}\n\nSource: {first_result['source']}"
            else:
                raise ValueError("Unable to generate summary from search results")
"""
Unit tests for Strands Agent core functionality.
Tests search keyword detection, API integration, response generation, and error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from src.strands_agent import StrandsAgent
from src.google_search import GoogleSearchTool, SearchResult, GoogleSearchError, RateLimitError


class TestStrandsAgent(unittest.TestCase):
    """Test cases for the main StrandsAgent class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key_12345678901234567890"
        self.search_engine_id = "test_search_engine_id_123"
        
        # Mock the GoogleSearchTool to avoid actual API calls during initialization
        with patch('strands_agent.GoogleSearchTool'):
            self.agent = StrandsAgent(self.api_key, self.search_engine_id)
    
    def test_initialization_valid_credentials(self):
        """Test successful initialization with valid credentials."""
        with patch('strands_agent.GoogleSearchTool') as mock_tool:
            agent = StrandsAgent(self.api_key, self.search_engine_id)
            self.assertIsNotNone(agent)
            mock_tool.assert_called_once_with(self.api_key, self.search_engine_id)
    
    def test_initialization_invalid_credentials(self):
        """Test initialization failure with invalid credentials."""
        # Test empty API key
        with self.assertRaises(ValueError) as context:
            StrandsAgent("", self.search_engine_id)
        self.assertIn("Google API key and search engine ID are required", str(context.exception))
        
        # Test empty search engine ID
        with self.assertRaises(ValueError) as context:
            StrandsAgent(self.api_key, "")
        self.assertIn("Google API key and search engine ID are required", str(context.exception))
        
        # Test None values
        with self.assertRaises(ValueError) as context:
            StrandsAgent(None, self.search_engine_id)
        self.assertIn("Google API key and search engine ID are required", str(context.exception))


class TestSearchKeywordDetection(unittest.TestCase):
    """Test cases for search keyword detection logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('strands_agent.GoogleSearchTool'):
            self.agent = StrandsAgent("test_key_12345678901234567890", "test_engine_123")
    
    def test_needs_search_with_time_keywords(self):
        """Test detection of questions requiring current information based on time keywords."""
        time_questions = [
            "What are the latest AWS certification discounts?",
            "What is the current price of Azure certification?",
            "Tell me about recent Google Cloud updates",
            "What deals are available today?",
            "What's new this month in cloud certifications?",
            "What is happening now with AWS pricing?"
        ]
        
        for question in time_questions:
            with self.subTest(question=question):
                self.assertTrue(self.agent._needs_search(question), 
                              f"Should detect search need for: {question}")
    
    def test_needs_search_with_pricing_keywords(self):
        """Test detection of questions about pricing and deals."""
        pricing_questions = [
            "What's the discount on AWS certification?",
            "How much does Azure certification cost?",
            "What are the current pricing deals?",
            "Tell me about certification vouchers",
            "What promotions are available?",
            "Is there a sale on cloud certifications?"
        ]
        
        for question in pricing_questions:
            with self.subTest(question=question):
                self.assertTrue(self.agent._needs_search(question),
                              f"Should detect search need for: {question}")
    
    def test_needs_search_with_availability_keywords(self):
        """Test detection of questions about availability and releases."""
        availability_questions = [
            "What certifications are available now?",
            "When will the new AWS exam be released?",
            "What's the availability of certification slots?",
            "Tell me about upcoming certification launches"
        ]
        
        for question in availability_questions:
            with self.subTest(question=question):
                self.assertTrue(self.agent._needs_search(question),
                              f"Should detect search need for: {question}")
    
    def test_no_search_needed_for_general_questions(self):
        """Test that general knowledge questions don't trigger search."""
        general_questions = [
            "What is AWS certification?",
            "Tell me about cloud computing",
            "What are the benefits of Azure?",
            "Explain Google Cloud services",
            "Describe the certification process",
            "What is the difference between AWS and Azure?"
        ]
        
        for question in general_questions:
            with self.subTest(question=question):
                self.assertFalse(self.agent._needs_search(question),
                               f"Should NOT detect search need for: {question}")
    
    def test_needs_search_edge_cases(self):
        """Test edge cases for search detection."""
        # Questions with pricing patterns should trigger search
        self.assertTrue(self.agent._needs_search("How much does it cost to get certified?"))
        self.assertTrue(self.agent._needs_search("What does it cost for AWS certification?"))
        
        # Questions with time patterns should trigger search
        self.assertTrue(self.agent._needs_search("When is the next certification exam?"))
        self.assertTrue(self.agent._needs_search("When will AWS release new certifications?"))
        
        # Mixed questions should be handled correctly
        self.assertFalse(self.agent._needs_search("Tell me about AWS certification benefits"))
        self.assertTrue(self.agent._needs_search("Tell me about the latest AWS certification benefits"))


class TestInputValidation(unittest.TestCase):
    """Test cases for input validation in the ask method."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('strands_agent.GoogleSearchTool'):
            self.agent = StrandsAgent("test_key_12345678901234567890", "test_engine_123")
    
    def test_ask_with_none_input(self):
        """Test handling of None input."""
        response = self.agent.ask(None)
        self.assertIn("didn't receive a question", response.lower())
    
    def test_ask_with_non_string_input(self):
        """Test handling of non-string input."""
        response = self.agent.ask(123)
        self.assertIn("can only process text questions", response.lower())
        
        response = self.agent.ask([])
        self.assertIn("can only process text questions", response.lower())
    
    def test_ask_with_empty_string(self):
        """Test handling of empty or whitespace-only strings."""
        response = self.agent.ask("")
        self.assertIn("appears to be empty", response.lower())
        
        response = self.agent.ask("   ")
        self.assertIn("appears to be empty", response.lower())
        
        response = self.agent.ask("\n\t  ")
        self.assertIn("appears to be empty", response.lower())
    
    def test_ask_with_very_long_question(self):
        """Test handling of extremely long questions."""
        long_question = "What is AWS certification? " * 100  # Over 1000 characters
        response = self.agent.ask(long_question)
        self.assertIn("quite long", response.lower())
        self.assertIn("more concise", response.lower())
    
    def test_ask_with_very_short_question(self):
        """Test handling of very short questions."""
        # "Hi" is actually treated as very short (2 chars) by the implementation
        response = self.agent.ask("Hi")
        self.assertIn("seems very short", response.lower())
        
        response = self.agent.ask("A?")
        self.assertIn("seems very short", response.lower())


class TestStaticAnswers(unittest.TestCase):
    """Test cases for static answer generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('strands_agent.GoogleSearchTool'):
            self.agent = StrandsAgent("test_key_12345678901234567890", "test_engine_123")
    
    def test_greeting_responses(self):
        """Test responses to greeting messages."""
        # Use longer greetings that won't trigger the "very short" validation
        greetings = ["Hello there", "Hey there", "hello agent", "Hi, how are you?"]
        
        for greeting in greetings:
            with self.subTest(greeting=greeting):
                response = self.agent.ask(greeting)
                self.assertIn("Hello", response)
                self.assertIn("Strands Agent", response)
    
    def test_help_responses(self):
        """Test responses to help requests."""
        help_requests = ["Help", "What can you do?", "help me", "WHAT CAN YOU DO"]
        
        for help_request in help_requests:
            with self.subTest(help_request=help_request):
                response = self.agent.ask(help_request)
                self.assertIn("help", response.lower())
                self.assertIn("search", response.lower())
    
    def test_certification_knowledge(self):
        """Test static knowledge about certifications."""
        # AWS certification question
        response = self.agent.ask("What is AWS certification?")
        self.assertIn("AWS", response)
        self.assertIn("certification", response.lower())
        
        # Azure certification question
        response = self.agent.ask("Tell me about Azure certifications")
        self.assertIn("Azure", response)
        self.assertIn("Microsoft", response)
        
        # Google Cloud certification question
        response = self.agent.ask("What are Google Cloud certifications?")
        self.assertIn("Google Cloud", response)
        self.assertIn("certification", response.lower())


class TestGoogleSearchToolMocking(unittest.TestCase):
    """Test cases for mocking Google Search API responses."""
    
    def setUp(self):
        """Set up test fixtures with mocked search tool."""
        self.api_key = "test_key_12345678901234567890"
        self.search_engine_id = "test_engine_123"
        
        # Create mock search results
        self.mock_results = [
            SearchResult(
                title="AWS Certification Discount - 50% Off",
                snippet="AWS is offering 50% discount on certification exams this month through re:Invent promotion.",
                url="https://aws.amazon.com/certification/discount"
            ),
            SearchResult(
                title="Latest AWS Exam Vouchers Available",
                snippet="Get your AWS certification vouchers with special pricing. Limited time offer for cloud professionals.",
                url="https://aws.amazon.com/training/vouchers"
            )
        ]
        
        # Mock the GoogleSearchTool
        self.mock_search_tool = Mock(spec=GoogleSearchTool)
        
        with patch('strands_agent.GoogleSearchTool', return_value=self.mock_search_tool):
            self.agent = StrandsAgent(self.api_key, self.search_engine_id)
    
    def test_successful_search_and_answer(self):
        """Test successful search and answer generation with mocked results."""
        # Configure mock to return test results
        self.mock_search_tool.search.return_value = self.mock_results
        self.mock_search_tool.summarize_results.return_value = (
            "AWS is offering 50% discount on certification exams this month through re:Invent promotion. "
            "Get your AWS certification vouchers with special pricing.\n\nSources: aws.amazon.com"
        )
        
        response = self.agent.ask("What are the latest AWS certification discounts?")
        
        # Verify search was called
        self.mock_search_tool.search.assert_called_once()
        self.mock_search_tool.summarize_results.assert_called_once()
        
        # Verify response content
        self.assertIn("50% discount", response)
        self.assertIn("aws.amazon.com", response.lower())
    
    def test_search_with_no_results(self):
        """Test handling when search returns no results."""
        # Configure mock to return empty results
        self.mock_search_tool.search.return_value = []
        
        response = self.agent.ask("What are the latest certification deals?")
        
        # Should get fallback response
        self.assertIn("couldn't find current information", response.lower())
    
    def test_search_with_invalid_results(self):
        """Test handling when search returns results with no meaningful content."""
        # Create results with empty snippets
        invalid_results = [
            SearchResult(title="Test", snippet="", url="https://example.com"),
            SearchResult(title="Test 2", snippet="No description available", url="https://example2.com")
        ]
        
        self.mock_search_tool.search.return_value = invalid_results
        
        response = self.agent.ask("What are the current cloud certification prices?")
        
        # Should get fallback response - check for the actual fallback message
        self.assertIn("weren't very helpful", response.lower())


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_key_12345678901234567890"
        self.search_engine_id = "test_engine_123"
        
        self.mock_search_tool = Mock(spec=GoogleSearchTool)
        
        with patch('strands_agent.GoogleSearchTool', return_value=self.mock_search_tool):
            self.agent = StrandsAgent(self.api_key, self.search_engine_id)
    
    def test_google_search_error_handling(self):
        """Test handling of GoogleSearchError."""
        # Configure mock to raise GoogleSearchError
        self.mock_search_tool.search.side_effect = GoogleSearchError("API key invalid")
        
        response = self.agent.ask("What are the latest AWS certification prices?")
        
        # Should get fallback response - check for the actual fallback message
        self.assertIn("unable to search for the latest information", response.lower())
    
    def test_rate_limit_error_handling(self):
        """Test handling of RateLimitError."""
        # Configure mock to raise RateLimitError
        self.mock_search_tool.search.side_effect = RateLimitError("Rate limit exceeded")
        
        response = self.agent.ask("What are current certification deals?")
        
        # Should get rate limit specific fallback
        self.assertIn("high demand", response.lower())
    
    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors during search."""
        # Configure mock to raise unexpected error
        self.mock_search_tool.search.side_effect = Exception("Unexpected network error")
        
        response = self.agent.ask("What are the latest cloud certification updates?")
        
        # Should get generic fallback response
        self.assertIn("encountered an issue searching", response.lower())
    
    def test_summarization_error_handling(self):
        """Test handling of errors during result summarization."""
        # Configure search to succeed but summarization to fail
        mock_results = [
            SearchResult(title="Test", snippet="Test content", url="https://example.com")
        ]
        self.mock_search_tool.search.return_value = mock_results
        self.mock_search_tool.summarize_results.side_effect = ValueError("Summarization failed")
        
        response = self.agent.ask("What are the current AWS certification costs?")
        
        # Should get fallback response
        self.assertIn("issue with your question", response.lower())


class TestGoogleSearchTool(unittest.TestCase):
    """Test cases for GoogleSearchTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_12345678901234567890"
        self.search_engine_id = "test_search_engine_id_123"
    
    def test_initialization_valid_params(self):
        """Test successful initialization with valid parameters."""
        tool = GoogleSearchTool(self.api_key, self.search_engine_id)
        self.assertEqual(tool.api_key, self.api_key)
        self.assertEqual(tool.search_engine_id, self.search_engine_id)
    
    def test_initialization_invalid_params(self):
        """Test initialization with invalid parameters."""
        # Test empty API key
        with self.assertRaises(ValueError) as context:
            GoogleSearchTool("", self.search_engine_id)
        self.assertIn("API key is required", str(context.exception))
        
        # Test short API key
        with self.assertRaises(ValueError) as context:
            GoogleSearchTool("short", self.search_engine_id)
        self.assertIn("too short", str(context.exception))
        
        # Test empty search engine ID
        with self.assertRaises(ValueError) as context:
            GoogleSearchTool(self.api_key, "")
        self.assertIn("Search engine ID is required", str(context.exception))
        
        # Test non-string parameters
        with self.assertRaises(ValueError) as context:
            GoogleSearchTool(123, self.search_engine_id)
        self.assertIn("must be a string", str(context.exception))
    
    @patch('google_search.requests.get')
    def test_search_input_validation(self, mock_get):
        """Test search method input validation."""
        tool = GoogleSearchTool(self.api_key, self.search_engine_id)
        
        # Test empty query
        with self.assertRaises(ValueError) as context:
            tool.search("")
        self.assertIn("cannot be None", str(context.exception))
        
        # Test whitespace-only query
        with self.assertRaises(ValueError) as context:
            tool.search("   ")
        self.assertIn("cannot be empty or only whitespace", str(context.exception))
        
        # Test None query
        with self.assertRaises(ValueError) as context:
            tool.search(None)
        self.assertIn("cannot be None", str(context.exception))
        
        # Test very short query
        with self.assertRaises(ValueError) as context:
            tool.search("a")
        self.assertIn("at least 2 characters", str(context.exception))
        
        # Test very long query
        long_query = "a" * 501
        with self.assertRaises(ValueError) as context:
            tool.search(long_query)
        self.assertIn("too long", str(context.exception))
        
        # Test invalid num_results
        with self.assertRaises(ValueError) as context:
            tool.search("test query", num_results=0)
        self.assertIn("between 1 and 10", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            tool.search("test query", num_results=11)
        self.assertIn("between 1 and 10", str(context.exception))
    
    @patch('google_search.requests.get')
    def test_search_http_error_handling(self, mock_get):
        """Test handling of various HTTP error responses."""
        tool = GoogleSearchTool(self.api_key, self.search_engine_id)
        
        # Test 429 Rate Limit
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with self.assertRaises(RateLimitError) as context:
            tool.search("test query")
        self.assertIn("rate limit exceeded", str(context.exception).lower())
        
        # Test 403 Forbidden
        mock_response.status_code = 403
        mock_response.content = b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}'
        mock_response.json.return_value = {"error": {"errors": [{"reason": "quotaExceeded"}]}}
        
        with self.assertRaises(RateLimitError) as context:
            tool.search("test query")
        self.assertIn("quota exceeded", str(context.exception).lower())
        
        # Test 400 Bad Request
        mock_response.status_code = 400
        mock_response.content = b'{"error": {"message": "Invalid request"}}'
        mock_response.json.return_value = {"error": {"message": "Invalid request"}}
        
        with self.assertRaises(GoogleSearchError) as context:
            tool.search("test query")
        self.assertIn("Invalid request", str(context.exception))
    
    @patch('google_search.requests.get')
    def test_successful_search_response_parsing(self, mock_get):
        """Test parsing of successful search responses."""
        tool = GoogleSearchTool(self.api_key, self.search_engine_id)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Test Title 1",
                    "snippet": "Test snippet 1 with useful information",
                    "link": "https://example.com/1"
                },
                {
                    "title": "Test Title 2", 
                    "snippet": "Test snippet 2 with more information",
                    "link": "https://example.com/2"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        results = tool.search("test query")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "Test Title 1")
        self.assertEqual(results[0].snippet, "Test snippet 1 with useful information")
        self.assertEqual(results[0].url, "https://example.com/1")
    
    def test_summarize_results_input_validation(self):
        """Test summarize_results method input validation."""
        tool = GoogleSearchTool(self.api_key, self.search_engine_id)
        
        # Test empty results
        with self.assertRaises(ValueError) as context:
            tool.summarize_results([], "test question")
        self.assertIn("No search results provided", str(context.exception))
        
        # Test empty question
        results = [SearchResult("Title", "Snippet", "URL")]
        with self.assertRaises(ValueError) as context:
            tool.summarize_results(results, "")
        self.assertIn("Original question is required", str(context.exception))
    
    def test_summarize_results_processing(self):
        """Test result processing and summarization."""
        tool = GoogleSearchTool(self.api_key, self.search_engine_id)
        
        # Test with valid results
        results = [
            SearchResult(
                title="AWS Certification Discount",
                snippet="AWS offers 50% discount on certification exams through December 2024.",
                url="https://aws.amazon.com/certification"
            ),
            SearchResult(
                title="Azure Certification Deals",
                snippet="Microsoft Azure certifications are available with special pricing this month.",
                url="https://docs.microsoft.com/azure"
            )
        ]
        
        summary = tool.summarize_results(results, "What are current certification discounts?")
        
        # Verify summary contains key information
        self.assertIn("50% discount", summary)
        self.assertIn("AWS", summary)
        self.assertIn("Sources:", summary)
        self.assertIn("aws.amazon.com", summary)
    
    def test_summarize_results_with_poor_quality_snippets(self):
        """Test handling of poor quality or empty snippets."""
        tool = GoogleSearchTool(self.api_key, self.search_engine_id)
        
        # Test with empty and low-quality snippets
        results = [
            SearchResult("Title 1", "", "https://example.com"),
            SearchResult("Title 2", "No description available", "https://example2.com"),
            SearchResult("Title 3", "Click here for more...", "https://example3.com"),
            SearchResult("Title 4", "This is a good quality snippet with useful information about the topic.", "https://example4.com")
        ]
        
        summary = tool.summarize_results(results, "test question")
        
        # Should only use the good quality snippet
        self.assertIn("good quality snippet", summary)
        self.assertIn("example4.com", summary)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
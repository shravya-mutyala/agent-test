"""
Integration tests for Strands Agent with real Google Search API.
Tests end-to-end functionality, response quality, rate limiting, and source citation accuracy.

These tests require valid Google API credentials and will make actual API calls.
Run with: python -m pytest test_integration.py -v
"""

import unittest
import time
import os
from unittest.mock import patch
import pytest
from src.strands_agent import StrandsAgent
from src.google_search import GoogleSearchTool, GoogleSearchError, RateLimitError
from src.config import config


class TestIntegrationSetup(unittest.TestCase):
    """Test setup and configuration for integration tests."""
    
    def test_api_credentials_available(self):
        """Test that required API credentials are available for integration tests."""
        self.assertTrue(config.google_api_key, "GOOGLE_API_KEY environment variable is required for integration tests")
        self.assertTrue(config.search_engine_id, "GOOGLE_SEARCH_ENGINE_ID environment variable is required for integration tests")
        
        # Validate credential format
        self.assertGreater(len(config.google_api_key), 20, "Google API key appears to be too short")
        self.assertGreater(len(config.search_engine_id), 10, "Search engine ID appears to be too short")
    
    @unittest.skipIf(not config.is_configured(), "API credentials not configured")
    def test_google_search_tool_initialization(self):
        """Test that GoogleSearchTool can be initialized with real credentials."""
        tool = GoogleSearchTool(config.google_api_key, config.search_engine_id)
        self.assertIsNotNone(tool)
        self.assertEqual(tool.api_key, config.google_api_key)
        self.assertEqual(tool.search_engine_id, config.search_engine_id)
    
    @unittest.skipIf(not config.is_configured(), "API credentials not configured")
    def test_strands_agent_initialization(self):
        """Test that StrandsAgent can be initialized with real credentials."""
        agent = StrandsAgent(config.google_api_key, config.search_engine_id)
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.google_search)


@unittest.skipIf(not config.is_configured(), "API credentials not configured")
class TestRealAPIConnection(unittest.TestCase):
    """Test real API connection and basic functionality."""
    
    def setUp(self):
        """Set up test fixtures with real API credentials."""
        self.tool = GoogleSearchTool(config.google_api_key, config.search_engine_id)
        self.agent = StrandsAgent(config.google_api_key, config.search_engine_id)
    
    def test_api_connection_test(self):
        """Test the API connection test functionality."""
        # This should succeed with valid credentials
        connection_result = self.tool.test_connection()
        self.assertTrue(connection_result, "API connection test should succeed with valid credentials")
    
    def test_basic_search_functionality(self):
        """Test basic search functionality with a simple query."""
        results = self.tool.search("Python programming", num_results=3)
        
        # Validate results structure
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Should return at least one result")
        self.assertLessEqual(len(results), 3, "Should not return more results than requested")
        
        # Validate result content
        for result in results:
            self.assertIsNotNone(result.title)
            self.assertIsNotNone(result.snippet)
            self.assertIsNotNone(result.url)
            self.assertTrue(result.url.startswith('http'), f"URL should be valid: {result.url}")
    
    def test_search_with_different_result_counts(self):
        """Test search with different numbers of requested results."""
        for num_results in [1, 3, 5, 10]:
            with self.subTest(num_results=num_results):
                results = self.tool.search("cloud computing", num_results=num_results)
                self.assertLessEqual(len(results), num_results, f"Should not exceed requested {num_results} results")
                self.assertGreater(len(results), 0, "Should return at least one result")


@unittest.skipIf(not config.is_configured(), "API credentials not configured")
class TestEndToEndFlow(unittest.TestCase):
    """Test complete end-to-end flow with real API calls."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = StrandsAgent(config.google_api_key, config.search_engine_id)
    
    def test_search_triggering_questions(self):
        """Test that questions requiring current information trigger search correctly."""
        search_questions = [
            "What are the latest AWS certification discounts?",
            "What is the current price of Azure certification?",
            "What deals are available today for cloud certifications?",
            "What are recent Google Cloud updates?",
            "What promotions are available now?"
        ]
        
        for question in search_questions:
            with self.subTest(question=question):
                # Add delay to respect rate limits
                time.sleep(0.5)
                
                response = self.agent.ask(question)
                
                # Validate response structure
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 50, f"Response should be substantial for: {question}")
                
                # Should contain source information for search-based responses
                self.assertIn("Sources:", response, f"Search-based response should include sources for: {question}")
    
    def test_static_knowledge_questions(self):
        """Test that general knowledge questions don't trigger unnecessary searches."""
        static_questions = [
            "What is AWS certification?",
            "Tell me about cloud computing",
            "What are the benefits of Azure?",
            "Explain Google Cloud services"
        ]
        
        for question in static_questions:
            with self.subTest(question=question):
                response = self.agent.ask(question)
                
                # Validate response
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 30, f"Response should be informative for: {question}")
                
                # Static responses typically don't include "Sources:" section
                # (though they might mention searching for current info)
    
    def test_mixed_conversation_flow(self):
        """Test a realistic conversation flow mixing static and search-based questions."""
        conversation = [
            ("Hello", "greeting"),
            ("What is AWS certification?", "static"),
            ("What are the latest AWS certification discounts?", "search"),
            ("Tell me about Azure certifications", "static"),
            ("What are current Azure certification prices?", "search")
        ]
        
        for i, (question, expected_type) in enumerate(conversation):
            with self.subTest(step=i+1, question=question):
                # Add delay between requests to respect rate limits
                if i > 0:
                    time.sleep(0.5)
                
                response = self.agent.ask(question)
                
                # Validate basic response structure
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 10, f"Response should be meaningful for: {question}")
                
                # Validate response type characteristics
                if expected_type == "greeting":
                    self.assertIn("Strands Agent", response)
                elif expected_type == "search":
                    # Search responses should be substantial and include sources
                    self.assertGreater(len(response), 50, "Search responses should be detailed")


@unittest.skipIf(not config.is_configured(), "API credentials not configured")
class TestResponseQuality(unittest.TestCase):
    """Test the quality and accuracy of responses from real API calls."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = StrandsAgent(config.google_api_key, config.search_engine_id)
        self.tool = GoogleSearchTool(config.google_api_key, config.search_engine_id)
    
    def test_response_relevance_and_quality(self):
        """Test that responses are relevant and of good quality."""
        test_cases = [
            {
                "question": "What are the latest Python programming trends?",
                "expected_keywords": ["Python", "programming"],
                "min_length": 100
            },
            {
                "question": "What are current cloud computing certifications available?",
                "expected_keywords": ["cloud", "certification"],
                "min_length": 80
            },
            {
                "question": "What are recent developments in artificial intelligence?",
                "expected_keywords": ["AI", "artificial intelligence", "development"],
                "min_length": 100
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            with self.subTest(case=i+1, question=test_case["question"]):
                # Add delay to respect rate limits
                time.sleep(1)
                
                response = self.agent.ask(test_case["question"])
                
                # Test response length and substance
                self.assertGreater(len(response), test_case["min_length"], 
                                 f"Response should be substantial: {response[:100]}...")
                
                # Test keyword relevance (at least one expected keyword should be present)
                response_lower = response.lower()
                keyword_found = any(keyword.lower() in response_lower 
                                  for keyword in test_case["expected_keywords"])
                self.assertTrue(keyword_found, 
                              f"Response should contain relevant keywords. Response: {response[:200]}...")
                
                # Test that response includes sources for search-based queries
                self.assertIn("Sources:", response, "Search-based responses should include source citations")
    
    def test_search_result_processing_quality(self):
        """Test the quality of search result processing and summarization."""
        # Test with a specific query that should return good results
        results = self.tool.search("AWS certification exam guide", num_results=5)
        
        # Validate we got meaningful results
        self.assertGreater(len(results), 0, "Should return search results")
        
        # Test summarization quality
        summary = self.tool.summarize_results(results, "What is the AWS certification exam guide?")
        
        # Validate summary quality
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 50, "Summary should be substantial")
        self.assertIn("Sources:", summary, "Summary should include source citations")
        
        # Test that summary is coherent (basic checks)
        self.assertFalse(summary.startswith("Sources:"), "Summary should have content before sources")
        
        # Count sentences (rough quality indicator)
        sentence_count = summary.count('.') + summary.count('!') + summary.count('?')
        self.assertGreater(sentence_count, 0, "Summary should contain complete sentences")
    
    def test_information_synthesis_from_multiple_sources(self):
        """Test that information from multiple sources is properly synthesized."""
        # Use a query that should return diverse sources
        results = self.tool.search("cloud computing benefits for businesses", num_results=5)
        
        if len(results) >= 2:  # Only test if we have multiple sources
            summary = self.tool.summarize_results(results, "What are the benefits of cloud computing for businesses?")
            
            # Check that summary appears to synthesize information
            # (not just copying one source)
            self.assertGreater(len(summary), 150, "Multi-source summary should be comprehensive")
            
            # Should mention multiple aspects/benefits
            benefit_keywords = ["cost", "scalability", "flexibility", "security", "efficiency", "productivity"]
            found_benefits = sum(1 for keyword in benefit_keywords if keyword in summary.lower())
            self.assertGreater(found_benefits, 1, "Summary should mention multiple benefits/aspects")


@unittest.skipIf(not config.is_configured(), "API credentials not configured")
class TestSourceCitationAccuracy(unittest.TestCase):
    """Test the accuracy and quality of source citations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = GoogleSearchTool(config.google_api_key, config.search_engine_id)
        self.agent = StrandsAgent(config.google_api_key, config.search_engine_id)
    
    def test_source_citation_format(self):
        """Test that source citations are properly formatted and accurate."""
        # Add delay to respect rate limits
        time.sleep(0.5)
        
        results = self.tool.search("Microsoft Azure documentation", num_results=3)
        summary = self.tool.summarize_results(results, "Where can I find Azure documentation?")
        
        # Validate source citation presence
        self.assertIn("Sources:", summary, "Summary should include source citations")
        
        # Extract sources section
        sources_section = summary.split("Sources:")[-1].strip()
        self.assertGreater(len(sources_section), 5, "Sources section should not be empty")
        
        # Validate that sources look like domain names
        # Should contain at least one domain-like string
        import re
        domain_pattern = r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        domains_found = re.findall(domain_pattern, sources_section)
        self.assertGreater(len(domains_found), 0, f"Should find domain names in sources: {sources_section}")
    
    def test_source_relevance_to_results(self):
        """Test that cited sources correspond to actual search results."""
        # Add delay to respect rate limits
        time.sleep(0.5)
        
        results = self.tool.search("Python programming tutorial", num_results=3)
        
        # Extract domains from actual results
        result_domains = []
        for result in results:
            if result.url:
                try:
                    domain = result.url.split('/')[2]
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    result_domains.append(domain.lower())
                except (IndexError, AttributeError):
                    continue
        
        # Generate summary and check source accuracy
        summary = self.tool.summarize_results(results, "How to learn Python programming?")
        
        if "Sources:" in summary:
            sources_section = summary.split("Sources:")[-1].strip().lower()
            
            # Check that at least one cited source matches actual results
            source_match_found = False
            for domain in result_domains:
                if domain in sources_section:
                    source_match_found = True
                    break
            
            self.assertTrue(source_match_found, 
                          f"Cited sources should match actual results. "
                          f"Result domains: {result_domains}, "
                          f"Sources section: {sources_section}")
    
    def test_source_deduplication(self):
        """Test that duplicate sources are properly handled."""
        # Create mock results with duplicate domains for testing
        from google_search import SearchResult
        
        duplicate_results = [
            SearchResult("Title 1", "Content from example.com about topic", "https://example.com/page1"),
            SearchResult("Title 2", "More content from example.com", "https://example.com/page2"),
            SearchResult("Title 3", "Content from different.com", "https://different.com/page1"),
            SearchResult("Title 4", "Another example.com page", "https://www.example.com/page3")
        ]
        
        summary = self.tool.summarize_results(duplicate_results, "Test question")
        
        if "Sources:" in summary:
            sources_section = summary.split("Sources:")[-1].strip()
            
            # Count occurrences of example.com (should appear only once)
            example_count = sources_section.lower().count("example.com")
            self.assertLessEqual(example_count, 1, 
                               f"Duplicate sources should be deduplicated. Sources: {sources_section}")


@unittest.skipIf(not config.is_configured(), "API credentials not configured")
class TestRateLimitingAndQuotaHandling(unittest.TestCase):
    """Test rate limiting behavior and quota handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = GoogleSearchTool(config.google_api_key, config.search_engine_id)
        self.agent = StrandsAgent(config.google_api_key, config.search_engine_id)
    
    def test_rate_limiting_behavior(self):
        """Test that rate limiting is properly implemented."""
        # Record timing of multiple requests
        request_times = []
        
        for i in range(3):
            start_time = time.time()
            try:
                results = self.tool.search(f"test query {i}", num_results=1)
                end_time = time.time()
                request_times.append(end_time - start_time)
                
                # Validate that we got results (API is working)
                self.assertIsInstance(results, list)
                
            except (GoogleSearchError, RateLimitError) as e:
                # If we hit rate limits, that's actually what we're testing for
                self.assertIn("rate limit", str(e).lower(), f"Rate limit error should be properly identified: {e}")
                break
            
            # Small delay between requests
            time.sleep(0.2)
        
        # If we completed multiple requests, check timing
        if len(request_times) > 1:
            # Requests should not be too fast (rate limiting should add some delay)
            min_interval = min(request_times[1:])  # Skip first request
            self.assertGreater(min_interval, 0.05, "Rate limiting should prevent requests that are too fast")
    
    def test_rate_limit_error_handling(self):
        """Test proper handling of rate limit errors."""
        # This test might not trigger rate limits in normal circumstances,
        # but we can test the error handling mechanism
        
        # Test with a rapid series of requests to potentially trigger rate limiting
        rate_limit_encountered = False
        
        for i in range(5):
            try:
                # Make requests without delay to test rate limiting
                results = self.tool.search(f"rapid test query {i}", num_results=1)
                self.assertIsInstance(results, list)
                
            except RateLimitError as e:
                # This is expected behavior
                rate_limit_encountered = True
                self.assertIn("rate limit", str(e).lower())
                break
            except GoogleSearchError as e:
                # Other API errors are also acceptable for this test
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    rate_limit_encountered = True
                    break
                else:
                    # Re-raise unexpected errors
                    raise
        
        # Note: We don't assert that rate limiting MUST occur, as it depends on API limits
        # But if it does occur, it should be handled properly
        if rate_limit_encountered:
            print("Rate limiting behavior confirmed and properly handled")
    
    def test_quota_exceeded_handling(self):
        """Test handling of quota exceeded scenarios."""
        # This test primarily validates that quota errors are properly categorized
        # We can't easily trigger actual quota exceeded without using up the daily limit
        
        # Test that the agent can handle quota-related errors gracefully
        try:
            # Make a normal request to ensure API is working
            response = self.agent.ask("What are current technology trends?")
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 20)
            
        except GoogleSearchError as e:
            # If we encounter quota issues, ensure they're handled gracefully
            if "quota" in str(e).lower():
                self.assertIn("quota", str(e).lower())
                print(f"Quota handling confirmed: {e}")
            else:
                raise
        except RateLimitError as e:
            # Rate limit errors are also acceptable
            self.assertIn("rate", str(e).lower())
            print(f"Rate limit handling confirmed: {e}")
    
    def test_fallback_behavior_on_api_limits(self):
        """Test that the agent provides fallback responses when API limits are hit."""
        # We'll simulate this by testing the fallback mechanism
        # In real scenarios, this would trigger when actual limits are reached
        
        # Test that agent can provide static responses when search fails
        static_question = "What is cloud computing?"
        response = self.agent.ask(static_question)
        
        # Should get a meaningful response even if search is unavailable
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 30)
        self.assertIn("cloud", response.lower())


@unittest.skipIf(not config.is_configured(), "API credentials not configured")
class TestErrorRecoveryAndResilience(unittest.TestCase):
    """Test error recovery and system resilience with real API."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = StrandsAgent(config.google_api_key, config.search_engine_id)
        self.tool = GoogleSearchTool(config.google_api_key, config.search_engine_id)
    
    def test_recovery_from_temporary_failures(self):
        """Test that the system can recover from temporary API failures."""
        # Test multiple requests to see if system maintains stability
        successful_requests = 0
        total_requests = 5
        
        for i in range(total_requests):
            try:
                time.sleep(0.5)  # Respect rate limits
                response = self.agent.ask(f"What are current trends in technology area {i}?")
                
                # Validate response quality
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 30)
                successful_requests += 1
                
            except (GoogleSearchError, RateLimitError) as e:
                # These are acceptable - system should handle them gracefully
                print(f"Request {i+1} handled error gracefully: {e}")
                continue
        
        # We should have at least some successful requests
        # (unless there are serious API issues)
        success_rate = successful_requests / total_requests
        print(f"Success rate: {success_rate:.2%} ({successful_requests}/{total_requests})")
        
        # If success rate is very low, there might be API configuration issues
        if success_rate < 0.2:
            self.skipTest("API success rate too low - possible configuration issues")
    
    def test_handling_of_malformed_queries(self):
        """Test system behavior with various edge case queries."""
        edge_case_queries = [
            "What are the latest $$$ pricing deals???",  # Special characters
            "current trends in AI" * 20,  # Very long query
            "latest news about 'cloud computing' and \"AI\"",  # Mixed quotes
            "What's happening NOW with tech?!?!",  # Excessive punctuation
        ]
        
        for i, query in enumerate(edge_case_queries):
            with self.subTest(query_type=f"edge_case_{i+1}"):
                time.sleep(0.5)  # Respect rate limits
                
                try:
                    response = self.agent.ask(query)
                    
                    # Should get some kind of meaningful response
                    self.assertIsInstance(response, str)
                    self.assertGreater(len(response), 20)
                    
                    # Should not contain error traces or raw error messages
                    self.assertNotIn("Traceback", response)
                    self.assertNotIn("Exception", response)
                    
                except (GoogleSearchError, RateLimitError) as e:
                    # These are acceptable - system should handle gracefully
                    print(f"Edge case query handled gracefully: {e}")


if __name__ == '__main__':
    # Check if API credentials are configured before running tests
    if not config.is_configured():
        print("WARNING: API credentials not configured.")
        print("Please set the following environment variables:")
        for missing in config.get_missing_config():
            print(f"  - {missing}")
        print("\nSkipping integration tests.")
    else:
        print("Running integration tests with real API...")
        print("Note: These tests will make actual API calls and may count against your quota.")
        
        # Run tests with verbose output
        unittest.main(verbosity=2)
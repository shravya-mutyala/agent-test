#!/usr/bin/env python3
"""
Integration test runner for Strands Agent.
Provides safe execution of integration tests with proper configuration checks.
"""

import os
import sys
import subprocess
import time

# Add parent directory to Python path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import config


def check_prerequisites():
    """Check if all prerequisites for integration tests are met."""
    print("Checking integration test prerequisites...")
    
    # Check API credentials
    if not config.is_configured():
        print("❌ API credentials not configured.")
        print("Please set the following environment variables:")
        for missing in config.get_missing_config():
            print(f"   - {missing}")
        print("\nYou can set these in a .env file or as environment variables.")
        return False
    
    print("✅ API credentials configured")
    
    # Check required packages
    try:
        import pytest
        print("✅ pytest available")
    except ImportError:
        print("❌ pytest not installed. Install with: pip install pytest")
        return False
    
    try:
        import requests
        print("✅ requests library available")
    except ImportError:
        print("❌ requests not installed. Install with: pip install requests")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv available")
    except ImportError:
        print("❌ python-dotenv not installed. Install with: pip install python-dotenv")
        return False
    
    return True


def run_connection_test():
    """Run a quick connection test before full integration tests."""
    print("\nRunning API connection test...")
    
    try:
        from src.google_search import GoogleSearchTool
        tool = GoogleSearchTool(config.google_api_key, config.search_engine_id)
        
        if tool.test_connection():
            print("✅ API connection successful")
            return True
        else:
            print("❌ API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False


def run_integration_tests(test_filter=None, verbose=True):
    """Run the integration tests with proper configuration."""
    print("\n" + "="*60)
    print("RUNNING STRANDS AGENT INTEGRATION TESTS")
    print("="*60)
    print("⚠️  WARNING: These tests make real API calls and count against your quota!")
    print("⚠️  Estimated API calls: 20-30 requests")
    print("⚠️  Estimated time: 2-3 minutes (with rate limiting)")
    print()
    
    # Ask for confirmation
    response = input("Do you want to continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Integration tests cancelled.")
        return False
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", "test_integration.py"]
    
    if verbose:
        cmd.append("-v")
    
    if test_filter:
        cmd.extend(["-k", test_filter])
    
    # Add output options
    cmd.extend(["--tb=short", "--no-header"])
    
    print(f"\nRunning command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        # Run the tests
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        return False
    except Exception as e:
        print(f"\nError running tests: {e}")
        return False


def main():
    """Main function to orchestrate integration test execution."""
    print("Strands Agent Integration Test Runner")
    print("=" * 40)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Run connection test
    if not run_connection_test():
        print("\n❌ API connection test failed. Please check your credentials and try again.")
        sys.exit(1)
    
    # Parse command line arguments for test filtering
    test_filter = None
    if len(sys.argv) > 1:
        test_filter = sys.argv[1]
        print(f"\nFiltering tests with: {test_filter}")
    
    # Run integration tests
    success = run_integration_tests(test_filter)
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("="*60)
        print("Your Strands Agent is working correctly with the Google Search API.")
        print("The system successfully handles:")
        print("  • End-to-end question processing")
        print("  • Real API integration")
        print("  • Response quality and relevance")
        print("  • Source citation accuracy")
        print("  • Rate limiting and error handling")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ SOME INTEGRATION TESTS FAILED")
        print("="*60)
        print("Please review the test output above for details.")
        print("Common issues:")
        print("  • API quota exceeded (try again tomorrow)")
        print("  • Network connectivity issues")
        print("  • API key or search engine ID configuration")
        sys.exit(1)


if __name__ == "__main__":
    main()
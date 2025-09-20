#!/usr/bin/env python3
"""
Test runner script for Strands Agent unit tests.
Provides easy way to run all tests with proper output formatting.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all unit tests for the Strands Agent."""
    print("Running Strands Agent Unit Tests...")
    print("=" * 50)
    
    # Change to the directory containing the tests
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_strands_agent.py", 
            "-v",
            "--tb=short"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ All tests passed successfully!")
            print("The Strands Agent core functionality is working correctly.")
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed. Please check the output above.")
            return False
            
    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install it with:")
        print("pip install pytest pytest-mock")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
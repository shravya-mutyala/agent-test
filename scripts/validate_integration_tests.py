#!/usr/bin/env python3
"""
Validation script for integration tests.
Verifies that integration tests are properly structured and ready to run.
"""

import sys
import importlib.util
from pathlib import Path


def validate_test_structure():
    """Validate that integration test file is properly structured."""
    print("Validating integration test structure...")
    
    try:
        import test_integration
        print("✅ Integration test module imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import integration test module: {e}")
        return False
    
    # Check for required test classes
    required_classes = [
        'TestIntegrationSetup',
        'TestRealAPIConnection', 
        'TestEndToEndFlow',
        'TestResponseQuality',
        'TestSourceCitationAccuracy',
        'TestRateLimitingAndQuotaHandling',
        'TestErrorRecoveryAndResilience'
    ]
    
    for class_name in required_classes:
        if hasattr(test_integration, class_name):
            print(f"✅ Found test class: {class_name}")
        else:
            print(f"❌ Missing test class: {class_name}")
            return False
    
    return True


def validate_dependencies():
    """Validate that all required dependencies are available."""
    print("\nValidating dependencies...")
    
    required_modules = [
        ('unittest', 'Python standard library'),
        ('pytest', 'Testing framework'),
        ('requests', 'HTTP library'),
        ('google_search', 'Custom Google Search module'),
        ('strands_agent', 'Main agent module'),
        ('config', 'Configuration module')
    ]
    
    all_available = True
    
    for module_name, description in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} ({description})")
        except ImportError:
            print(f"❌ {module_name} ({description}) - Not available")
            all_available = False
    
    return all_available


def validate_test_files():
    """Validate that all test-related files exist."""
    print("\nValidating test files...")
    
    required_files = [
        ('test_integration.py', 'Main integration test file'),
        ('run_integration_tests.py', 'Integration test runner'),
        ('test_config_guide.md', 'Configuration guide'),
        ('test_strands_agent.py', 'Unit tests'),
        ('requirements.txt', 'Dependencies file')
    ]
    
    all_exist = True
    
    for filename, description in required_files:
        file_path = Path(filename)
        if file_path.exists():
            print(f"✅ {filename} ({description})")
        else:
            print(f"❌ {filename} ({description}) - Missing")
            all_exist = False
    
    return all_exist


def count_test_methods():
    """Count the number of test methods in integration tests."""
    print("\nCounting test methods...")
    
    try:
        import test_integration
        import inspect
        
        total_tests = 0
        
        for name in dir(test_integration):
            obj = getattr(test_integration, name)
            if inspect.isclass(obj) and name.startswith('Test'):
                class_tests = len([method for method in dir(obj) if method.startswith('test_')])
                print(f"  {name}: {class_tests} tests")
                total_tests += class_tests
        
        print(f"\n✅ Total integration tests: {total_tests}")
        return total_tests
        
    except Exception as e:
        print(f"❌ Error counting tests: {e}")
        return 0


def validate_test_coverage():
    """Validate that tests cover all required functionality."""
    print("\nValidating test coverage...")
    
    # Check that tests cover all task requirements
    required_coverage = [
        "end-to-end flow with actual Google Search API",
        "response quality with sample questions", 
        "rate limiting and quota handling",
        "source citation accuracy"
    ]
    
    try:
        with open('test_integration.py', 'r') as f:
            test_content = f.read().lower()
        
        coverage_found = []
        
        # Check for end-to-end flow tests
        if 'end_to_end' in test_content or 'testendtoendflow' in test_content:
            coverage_found.append("✅ End-to-end flow testing")
        else:
            coverage_found.append("❌ End-to-end flow testing")
        
        # Check for response quality tests
        if 'response_quality' in test_content or 'testresponsequality' in test_content:
            coverage_found.append("✅ Response quality testing")
        else:
            coverage_found.append("❌ Response quality testing")
        
        # Check for rate limiting tests
        if 'rate_limit' in test_content or 'testratelimiting' in test_content:
            coverage_found.append("✅ Rate limiting testing")
        else:
            coverage_found.append("❌ Rate limiting testing")
        
        # Check for source citation tests
        if 'source_citation' in test_content or 'testsourcecitation' in test_content:
            coverage_found.append("✅ Source citation testing")
        else:
            coverage_found.append("❌ Source citation testing")
        
        for item in coverage_found:
            print(f"  {item}")
        
        return all("✅" in item for item in coverage_found)
        
    except Exception as e:
        print(f"❌ Error validating coverage: {e}")
        return False


def main():
    """Main validation function."""
    print("Integration Test Validation")
    print("=" * 40)
    
    validations = [
        ("Test Structure", validate_test_structure),
        ("Dependencies", validate_dependencies), 
        ("Test Files", validate_test_files),
        ("Test Coverage", validate_test_coverage)
    ]
    
    all_passed = True
    
    for name, validator in validations:
        print(f"\n{name}:")
        print("-" * len(name))
        if not validator():
            all_passed = False
    
    # Count tests
    test_count = count_test_methods()
    
    print("\n" + "=" * 60)
    if all_passed and test_count > 0:
        print("✅ ALL VALIDATIONS PASSED!")
        print("=" * 60)
        print("Integration tests are properly structured and ready to run.")
        print(f"Total test methods: {test_count}")
        print("\nTo run integration tests:")
        print("1. Configure API credentials in .env file")
        print("2. Run: python run_integration_tests.py")
        print("3. Or run specific tests: python -m pytest test_integration.py -v")
        print("\nSee test_config_guide.md for detailed setup instructions.")
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("=" * 60)
        print("Please fix the issues above before running integration tests.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
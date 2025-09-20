# Integration Test Configuration Guide

This guide helps you set up and run integration tests for the Strands Agent with real Google Search API.

## Prerequisites

### 1. Google Cloud Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Custom Search API**
   - In the Google Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Custom Search API"
   - Click on it and press "Enable"

3. **Create API Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the generated API key
   - (Optional) Restrict the key to Custom Search API for security

### 2. Custom Search Engine Setup

1. **Create Custom Search Engine**
   - Go to [Google Custom Search Engine](https://cse.google.com/cse/)
   - Click "Add" to create a new search engine
   - Enter a site to search (you can use `*.com` to search the entire web)
   - Click "Create"

2. **Get Search Engine ID**
   - In your Custom Search Engine control panel
   - Click on your search engine
   - In the "Setup" tab, find "Search engine ID"
   - Copy this ID

3. **Configure for Web Search**
   - In the "Setup" tab, under "Sites to search"
   - Remove any specific sites and add `*` to search the entire web
   - Turn on "Image search" and "Safe search" as needed

### 3. Environment Configuration

Create a `.env` file in your project root with your credentials:

```bash
# Google Search API Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

**Security Note**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

### 4. Install Dependencies

Make sure you have all required packages:

```bash
pip install -r requirements.txt
pip install pytest  # If not already installed
```

## Running Integration Tests

### Quick Start

1. **Run all integration tests:**
   ```bash
   python run_integration_tests.py
   ```

2. **Run specific test categories:**
   ```bash
   python run_integration_tests.py "TestEndToEndFlow"
   python run_integration_tests.py "TestResponseQuality"
   python run_integration_tests.py "TestRateLimitingAndQuotaHandling"
   ```

3. **Run with pytest directly:**
   ```bash
   python -m pytest test_integration.py -v
   ```

### Test Categories

The integration tests are organized into several categories:

1. **TestIntegrationSetup**
   - Validates API credentials and basic setup
   - Tests tool initialization

2. **TestRealAPIConnection**
   - Tests basic API connectivity
   - Validates search functionality with real API

3. **TestEndToEndFlow**
   - Tests complete question-to-answer flow
   - Validates search triggering logic
   - Tests mixed conversation scenarios

4. **TestResponseQuality**
   - Validates response relevance and quality
   - Tests information synthesis from multiple sources
   - Checks response comprehensiveness

5. **TestSourceCitationAccuracy**
   - Validates source citation format
   - Tests source relevance to results
   - Checks source deduplication

6. **TestRateLimitingAndQuotaHandling**
   - Tests rate limiting behavior
   - Validates quota handling
   - Tests fallback mechanisms

7. **TestErrorRecoveryAndResilience**
   - Tests recovery from temporary failures
   - Validates handling of edge cases
   - Tests system stability

## Understanding Test Results

### Success Indicators

✅ **All tests pass**: Your Strands Agent is fully functional with the Google Search API

✅ **Most tests pass with some rate limiting**: Normal behavior, indicates proper rate limit handling

### Common Issues and Solutions

❌ **API credentials not configured**
- Solution: Check your `.env` file and ensure variables are set correctly

❌ **API connection test failed**
- Check your API key is valid and not expired
- Ensure Custom Search API is enabled in Google Cloud Console
- Verify your search engine ID is correct

❌ **Rate limit exceeded**
- Normal if running tests multiple times quickly
- Wait a few minutes and try again
- Consider reducing test frequency

❌ **Quota exceeded**
- You've hit your daily API quota
- Wait until tomorrow or upgrade your Google Cloud plan
- Check your usage in Google Cloud Console

❌ **403 Forbidden errors**
- API key might be restricted
- Check API key restrictions in Google Cloud Console
- Ensure Custom Search API is enabled

## API Usage and Costs

### Free Tier Limits
- Google Custom Search API provides 100 free queries per day
- Integration tests use approximately 20-30 queries per full run
- You can run tests 3-4 times per day within free limits

### Monitoring Usage
- Check usage in Google Cloud Console > APIs & Services > Custom Search API
- Set up billing alerts to avoid unexpected charges
- Consider upgrading if you need more queries for development

### Cost Optimization
- Run specific test categories instead of full suite during development
- Use unit tests (with mocked API) for frequent testing
- Reserve integration tests for final validation

## Troubleshooting

### Network Issues
```bash
# Test basic connectivity
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_SEARCH_ENGINE_ID&q=test"
```

### Credential Validation
```python
# Quick credential test
python -c "from config import config; print('Configured:', config.is_configured())"
```

### Verbose Test Output
```bash
# Run with maximum verbosity
python -m pytest test_integration.py -v -s --tb=long
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Run integration tests sparingly** - Use unit tests for frequent development
2. **Monitor API usage** - Keep track of your daily quota
3. **Test in stages** - Run connection tests before full integration tests
4. **Use test filters** - Focus on specific functionality when debugging
5. **Keep credentials secure** - Never commit API keys to version control

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your Google Cloud and Custom Search Engine setup
3. Review the test output for specific error messages
4. Check Google Cloud Console for API usage and errors
5. Ensure all dependencies are installed correctly

The integration tests are designed to be comprehensive and realistic, testing all aspects of the Strands Agent's functionality with real API calls.
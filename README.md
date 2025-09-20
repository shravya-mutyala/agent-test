# 🤖 Strands Agent

An intelligent conversational AI that combines static knowledge with real-time web search capabilities using Google Custom Search API. Features both CLI and beautiful web interfaces.

## ✨ Features

- **🧠 Intelligent Question Routing**: Automatically determines when to use static knowledge vs. real-time search
- **🔍 Real-time Web Search**: Integrates with Google Custom Search API for current information
- **📚 Source Citations**: Provides proper attribution for web-sourced information
- **🌐 Beautiful Web UI**: Modern, responsive chat interface with peaceful design
- **💻 CLI Interface**: Full-featured command-line interface for power users
- **🛡️ Comprehensive Error Handling**: Graceful fallbacks and user-friendly error messages
- **⚡ Rate Limiting**: Built-in protection against API rate limits
- **🧪 Extensive Testing**: Unit tests and integration tests with real API calls

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd strands-agent

# Run automated setup
python setup.py
```

The setup script will:
- ✅ Check Python version compatibility
- ✅ Install all dependencies
- ✅ Create configuration files
- ✅ Validate project structure
- ✅ Run basic tests

### Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Google API credentials
   ```

3. **Validate setup**
   ```bash
   python scripts/validate_integration_tests.py
   ```

## 🎯 Usage

### 🌐 Web Interface (Recommended)
```bash
python scripts/start_ui.py
```
Then open: **http://localhost:5000**

### 💻 Command Line Interface
```bash
# Interactive mode
python main.py

# Single question
python main.py --question "What are the latest AWS certification discounts?"
```

### 📱 Example Questions

**Questions that trigger web search:**
- "What are the latest AWS certification discounts?"
- "Current Azure pricing for virtual machines"
- "What deals are available today for cloud certifications?"
- "Recent developments in artificial intelligence"

**Questions answered with static knowledge:**
- "What is cloud computing?"
- "Tell me about AWS certifications"
- "Explain the benefits of Azure"
- "What are Google Cloud services?"

## 📁 Project Structure

```
strands-agent/
├── 📁 src/                    # Source code
│   ├── strands_agent.py       # Main agent class
│   ├── google_search.py       # Google Search API integration
│   ├── config.py              # Configuration management
│   └── app.py                 # Flask web application
├── 📁 tests/                  # Test suite
├── 📁 scripts/                # Utility scripts
├── 📁 templates/              # Web UI templates
├── 📁 docs/                   # Documentation
├── 📄 main.py                 # CLI interface
└── 📄 setup.py                # Automated setup script
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure documentation.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your Google API credentials:

```bash
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### Getting API Credentials

1. **Google API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Custom Search API
   - Create credentials (API Key)
   - Restrict to Custom Search API for security

2. **Custom Search Engine ID**:
   - Go to [Google Custom Search](https://cse.google.com/cse/)
   - Create a new search engine
   - Configure it to search the entire web (`*`)
   - Copy the Search Engine ID

📖 **Detailed Setup Guide**: [docs/test_config_guide.md](docs/test_config_guide.md)

## 🧪 Testing

### Quick Validation
```bash
python scripts/validate_integration_tests.py
```

### Unit Tests
```bash
python -m pytest tests/test_strands_agent.py -v
```

### Integration Tests (Real API)
```bash
python scripts/run_integration_tests.py
```

**⚠️ Note**: Integration tests make real API calls and count against your quota.

### All Tests
```bash
python scripts/run_tests.py
```

## 🌐 Web UI Features

- **🎨 Beautiful Design**: Modern gradient background with peaceful theme
- **📱 Responsive**: Works perfectly on desktop, tablet, and mobile
- **💬 Real-time Chat**: Instant responses with typing indicators
- **📚 Source Citations**: Clear attribution for web-sourced information
- **🔄 Auto-scroll**: Smooth conversation flow
- **⌨️ Keyboard Shortcuts**: Enter to send, Shift+Enter for new line
- **🗑️ Clear Chat**: Easy conversation reset

📖 **Web UI Guide**: [docs/WEB_UI_README.md](docs/WEB_UI_README.md)

## 🏗️ Architecture

### Core Components

- **StrandsAgent**: Main conversation logic and question routing
- **GoogleSearchTool**: Google Custom Search API integration with error handling
- **Config**: Environment variable and configuration management
- **Flask App**: Web interface with session management

### Key Features

- **🎯 Smart Routing**: Keyword-based detection for search necessity
- **🔄 Error Recovery**: Multiple fallback strategies for API failures
- **⚡ Rate Limiting**: Automatic request throttling and retry logic
- **📊 Response Quality**: Multi-source information synthesis with citations
- **🔒 Security**: Secure credential management and input validation

## 📊 API Usage & Costs

- **🆓 Free Tier**: 100 queries per day
- **💰 Paid Tier**: $5 per 1000 queries after free limit
- **📈 Monitoring**: Track usage in Google Cloud Console
- **⚡ Rate Limits**: Built-in throttling respects API limits

## 🛡️ Security Features

- ✅ Environment variables for sensitive data
- ✅ API key validation and error handling
- ✅ No logging of sensitive information
- ✅ Secure credential management
- ✅ Input validation and sanitization
- ✅ Comprehensive .gitignore for sensitive files

## 📚 Documentation

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project organization
- **[docs/WEB_UI_README.md](docs/WEB_UI_README.md)** - Complete web UI guide
- **[docs/test_config_guide.md](docs/test_config_guide.md)** - API setup and testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python scripts/run_tests.py`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Submit a pull request

## 🆘 Troubleshooting

### Common Issues

**"Agent not available"**
- Check your `.env` file configuration
- Verify API credentials are correct
- Ensure Google Custom Search API is enabled

**"Rate limit exceeded"**
- Normal behavior - wait a few minutes
- Check your daily quota in Google Cloud Console

**Web UI not loading**
- Ensure Flask is installed: `pip install flask`
- Check that templates/index.html exists
- Verify no port conflicts on 5000

### Getting Help

1. Run validation: `python scripts/validate_integration_tests.py`
2. Check logs in console output
3. Review documentation in `docs/` directory
4. Create an issue with detailed error information

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Enjoy Your Strands Agent!

Your intelligent conversational AI is ready to help with questions, research, and real-time information. The beautiful web interface and powerful CLI provide flexible ways to interact with your agent.

**Happy chatting!** 🤖✨
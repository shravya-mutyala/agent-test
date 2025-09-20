# 📁 Strands Agent - Project Structure

This document describes the organized project structure and explains the purpose of each directory and file.

## 🏗️ Directory Structure

```
strands-agent/
├── 📁 src/                          # Source code
│   ├── __init__.py                  # Package initialization
│   ├── strands_agent.py             # Main agent class
│   ├── google_search.py             # Google Search API integration
│   ├── config.py                    # Configuration management
│   └── app.py                       # Flask web application
│
├── 📁 tests/                        # Test files
│   ├── test_strands_agent.py        # Unit tests for main agent
│   └── test_integration.py          # Integration tests with real API
│
├── 📁 scripts/                      # Utility scripts
│   ├── run_integration_tests.py     # Integration test runner
│   ├── run_tests.py                 # General test runner
│   ├── start_ui.py                  # Web UI launcher
│   └── validate_integration_tests.py # Test validation script
│
├── 📁 templates/                    # Web UI templates
│   └── index.html                   # Main chat interface
│
├── 📁 docs/                         # Documentation
│   ├── WEB_UI_README.md            # Web UI documentation
│   └── test_config_guide.md        # Test configuration guide
│
├── 📁 .kiro/                        # Kiro IDE configuration
│   └── specs/                       # Feature specifications
│       └── strands-agent/
│           ├── requirements.md      # Project requirements
│           ├── design.md           # System design
│           └── tasks.md            # Implementation tasks
│
├── 📄 main.py                       # CLI interface
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment variables template
├── 📄 .gitignore                    # Git ignore rules
├── 📄 README.md                     # Main project documentation
└── 📄 PROJECT_STRUCTURE.md         # This file
```

## 📂 Directory Descriptions

### `/src/` - Source Code
Contains all the main application source code organized as a Python package.

- **`__init__.py`** - Makes src a Python package and defines public API
- **`strands_agent.py`** - Core agent class with conversation logic
- **`google_search.py`** - Google Custom Search API integration
- **`config.py`** - Configuration management and environment variables
- **`app.py`** - Flask web application for the chat UI

### `/tests/` - Test Suite
Comprehensive test coverage for all functionality.

- **`test_strands_agent.py`** - Unit tests with mocked dependencies
- **`test_integration.py`** - Integration tests with real API calls

### `/scripts/` - Utility Scripts
Helper scripts for development, testing, and deployment.

- **`run_integration_tests.py`** - Safe integration test execution
- **`run_tests.py`** - General test runner for all tests
- **`start_ui.py`** - Web UI launcher with prerequisite checks
- **`validate_integration_tests.py`** - Test structure validation

### `/templates/` - Web Templates
HTML templates for the Flask web application.

- **`index.html`** - Main chat interface with responsive design

### `/docs/` - Documentation
Project documentation and guides.

- **`WEB_UI_README.md`** - Complete web UI documentation
- **`test_config_guide.md`** - API setup and testing guide

### `/.kiro/` - IDE Configuration
Kiro IDE specific files including feature specifications.

## 🚀 Usage Instructions

### Running the Application

**CLI Interface:**
```bash
python main.py
```

**Web UI:**
```bash
python scripts/start_ui.py
```

**Direct Flask:**
```bash
cd src && python app.py
```

### Running Tests

**Unit Tests:**
```bash
python -m pytest tests/test_strands_agent.py -v
```

**Integration Tests:**
```bash
python scripts/run_integration_tests.py
```

**All Tests:**
```bash
python scripts/run_tests.py
```

### Development Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

3. **Validate Setup:**
   ```bash
   python scripts/validate_integration_tests.py
   ```

## 📦 Package Structure

The `src/` directory is organized as a proper Python package:

```python
# Import the main classes
from src import StrandsAgent, GoogleSearchTool, config

# Or import specific components
from src.strands_agent import StrandsAgent
from src.google_search import GoogleSearchTool, GoogleSearchError
from src.config import config
```

## 🔧 Configuration Files

### `.env` - Environment Variables
```bash
GOOGLE_API_KEY=your_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### `requirements.txt` - Dependencies
- Core dependencies for the application
- Testing frameworks
- Web framework (Flask)

### `.gitignore` - Version Control
- Excludes sensitive files (.env, API keys)
- Ignores build artifacts and cache files
- Prevents committing temporary files

## 🛡️ Security Considerations

### Protected Files
The following files are protected by `.gitignore`:
- `.env` - Contains API keys and secrets
- `__pycache__/` - Python bytecode cache
- `*.log` - Log files that may contain sensitive data
- `venv/` - Virtual environment files

### Safe to Commit
- `.env.example` - Template without real credentials
- All source code in `src/`
- All tests in `tests/`
- Documentation in `docs/`
- Configuration templates

## 🔄 Development Workflow

1. **Make Changes** in `src/` directory
2. **Run Unit Tests** to verify functionality
3. **Run Integration Tests** before major releases
4. **Update Documentation** as needed
5. **Commit Changes** (sensitive files are automatically excluded)

## 📈 Scalability

This structure supports:
- **Easy Testing** - Separated test files with clear organization
- **Modular Development** - Each component in its own file
- **Documentation** - Centralized docs with specific guides
- **Deployment** - Clear separation of source and utilities
- **Collaboration** - Organized structure for team development

The organized structure makes the project maintainable, scalable, and professional while ensuring security best practices are followed.
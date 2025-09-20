# 🌐 Strands Agent Web UI

A beautiful, responsive web interface for the Strands Agent that provides an intuitive chat experience with real-time web search capabilities.

## ✨ Features

- **Beautiful Chat Interface**: Clean, modern design with peaceful gradient background
- **Real-time Responses**: Instant communication with the Strands Agent
- **Smart Search Integration**: Automatically searches the web when current information is needed
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Source Citations**: Displays sources for web-searched information
- **Chat History**: Maintains conversation history during your session
- **Error Handling**: Graceful error messages and fallback responses
- **Loading Indicators**: Visual feedback during processing

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install flask==3.0.0
# or
pip install -r requirements.txt
```

### 2. Configure API Credentials
Make sure your `.env` file is configured with:
```bash
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### 3. Start the Web UI
```bash
# Easy way - use the launcher
python start_ui.py

# Or run Flask directly
python app.py
```

### 4. Open Your Browser
Navigate to: **http://localhost:5000**

## 🎨 UI Features

### Header Section
- **Title**: "Ask Me Anything!" with robot icon
- **Subtitle**: Brief description of capabilities
- **Gradient Design**: Beautiful purple gradient background

### Chat Interface
- **Message Bubbles**: Distinct styling for user (purple gradient) and agent (light gray) messages
- **Timestamps**: Shows time for each message
- **Auto-scroll**: Automatically scrolls to latest messages
- **Welcome Message**: Friendly introduction when chat is empty

### Input Section
- **Auto-resize Textarea**: Expands as you type longer messages
- **Send Button**: Animated send button with paper plane icon
- **Keyboard Shortcuts**: 
  - `Enter` to send message
  - `Shift+Enter` for new line

### Additional Features
- **Clear Chat Button**: Remove all chat history
- **Loading Animation**: Spinner with "Thinking and searching..." message
- **Error Messages**: Clear error notifications with icons
- **Responsive Design**: Adapts to different screen sizes

## 🛠️ Technical Details

### Backend (Flask)
- **Framework**: Flask 3.0.0
- **Session Management**: Maintains chat history per session
- **API Integration**: Direct integration with Strands Agent
- **Error Handling**: Comprehensive error catching and user-friendly messages
- **Status Endpoint**: Check agent availability and configuration

### Frontend (HTML/CSS/JavaScript)
- **Styling**: Pure CSS with modern design principles
- **Fonts**: Inter font family for clean typography
- **Icons**: Font Awesome for consistent iconography
- **Animations**: Smooth transitions and loading animations
- **Responsive**: Mobile-first responsive design

### Key Endpoints
- `GET /` - Main chat interface
- `POST /ask` - Send question to agent
- `POST /clear` - Clear chat history
- `GET /status` - Check agent status

## 🎯 Usage Examples

### Sample Questions to Try
- "What are the latest AWS certification discounts?"
- "Tell me about cloud computing"
- "What are current Python programming trends?"
- "What is artificial intelligence?"
- "What deals are available today for tech certifications?"

### Expected Behavior
- **Static Questions**: Answered immediately with built-in knowledge
- **Current Info Questions**: Triggers web search and provides sourced answers
- **Error Scenarios**: Graceful fallback with helpful error messages

## 🔧 Customization

### Styling
Edit `templates/index.html` to customize:
- **Colors**: Modify CSS gradient and color variables
- **Layout**: Adjust container sizes and spacing
- **Typography**: Change fonts and text styling
- **Background**: Update gradient or add background images

### Functionality
Edit `app.py` to customize:
- **Session Management**: Modify chat history handling
- **Error Messages**: Customize error responses
- **Logging**: Adjust logging levels and formats
- **Security**: Add authentication or rate limiting

## 🐛 Troubleshooting

### Common Issues

**"Agent not available"**
- Check your `.env` file configuration
- Verify API credentials are correct
- Ensure Google Custom Search API is enabled

**"Network error"**
- Check internet connection
- Verify Flask server is running
- Check browser console for JavaScript errors

**UI not loading properly**
- Clear browser cache
- Check browser console for errors
- Verify templates/index.html exists

**Slow responses**
- Normal for web search queries (2-5 seconds)
- Check API quota limits
- Monitor network connectivity

### Debug Mode
To enable debug mode, edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Logs
Check console output for:
- Agent initialization status
- Request processing logs
- Error messages and stack traces

## 🔒 Security Notes

### Production Deployment
- Change the Flask secret key in `app.py`
- Use environment variables for sensitive configuration
- Enable HTTPS in production
- Add rate limiting and authentication as needed

### API Security
- Restrict Google API key to Custom Search API only
- Monitor API usage and set quotas
- Keep API credentials secure and never commit to version control

## 📱 Mobile Experience

The web UI is fully responsive and provides an excellent mobile experience:
- **Touch-friendly**: Large buttons and touch targets
- **Responsive Layout**: Adapts to different screen sizes
- **Mobile Keyboard**: Optimized input handling
- **Smooth Scrolling**: Natural chat experience on mobile

## 🎉 Enjoy Your Strands Agent!

The web UI provides an intuitive and beautiful way to interact with your intelligent agent. The peaceful design and smooth animations create a pleasant user experience while the powerful backend ensures accurate and up-to-date responses.

Happy chatting! 🤖✨
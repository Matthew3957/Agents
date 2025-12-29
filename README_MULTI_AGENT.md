# Multi-Agent Ollama Assistant

An advanced Python-based system tray application featuring **intelligent agent routing** with specialized AI agents for different tasks. A lightweight router agent (using Gemma2 2B) automatically delegates queries to the right specialized agent, each with access to specific tools and capabilities.

## 🌟 Key Features

### **Intelligent Agent Routing**
- **Router Agent** (Gemma2 2B) automatically analyzes queries and routes to the best specialized agent
- Manual agent selection available if you want to force a specific agent
- Seamless switching between agents based on task requirements

### **Specialized Agents**

1. **General Agent** - Casual conversation and general questions
2. **File Manager Agent** - File operations, document saving, directory management
3. **Calendar Agent** - Google Calendar integration for scheduling and event management
4. **Web Search Agent** - Internet search and current information retrieval
5. **Document Analyst Agent** - PDF/DOCX reading, analysis, and summarization
6. **Code Helper Agent** - Code writing, debugging, and Python script execution

### **Powerful Tool System**

Each agent has access to specialized tools:
- **File Operations**: read, write, list, create directories, delete files
- **Document Processing**: Extract text from PDF, DOCX, analyze documents
- **Web Capabilities**: Search the internet, fetch URLs
- **Calendar Management**: Create events, list upcoming events, delete events
- **Code Execution**: Run Python scripts safely with timeout protection

### **Enhanced UI**
- Shows which agent is handling each request
- Displays tools used during execution
- Manual agent selector for forcing specific agents
- Agent information panel
- Conversation history with agent attribution

### **System Tray Integration**
- Global hotkey (Ctrl+Shift+A) for instant access
- Runs quietly in background
- Cross-platform support (Linux, macOS, Windows)

## 📋 Prerequisites

1. **Python 3.7+**
2. **Ollama** installed and running
3. **Required Models**:
   ```bash
   ollama pull gemma2:2b      # Router agent (fast, lightweight)
   ollama pull ministral:3b   # Specialized agents (efficient)
   ```

## 🚀 Installation

### Step 1: Install Dependencies

```bash
# Core dependencies (required)
pip install pystray Pillow keyboard ollama PyYAML requests

# Optional: For document processing
pip install PyPDF2 python-docx

# Optional: For Google Calendar integration
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Pull Ollama Models

```bash
# Router model (lightweight, fast routing decisions)
ollama pull gemma2:2b

# Agent model (balanced performance)
ollama pull ministral:3b
```

### Step 3: Configure (Optional)

The application works out-of-the-box with default settings. To customize:

```bash
# Edit config.yaml to:
# - Change models for specific agents
# - Adjust agent descriptions for better routing
# - Modify temperature settings
# - Add custom agents
nano config.yaml
```

### Step 4: Setup Google Calendar (Optional)

If you want calendar integration:

1. Follow the Google Calendar API setup guide:
   - Go to https://console.cloud.google.com/
   - Create/select a project
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials JSON

2. Save credentials:
   ```bash
   mv ~/Downloads/credentials.json ~/.ollama_calendar_credentials.json
   ```

3. Run setup script:
   ```bash
   python3 setup_google_calendar.py
   ```

   This will open a browser for OAuth authorization.

### Step 5: Run the Application

```bash
python3 ollama_multi_agent_tray.py
```

Or make it executable:
```bash
chmod +x ollama_multi_agent_tray.py
./ollama_multi_agent_tray.py
```

## 📖 Usage Guide

### Quick Start

1. **Launch**: Run `python3 ollama_multi_agent_tray.py`
2. **Access**: Press `Ctrl+Shift+A` to show the window
3. **Query**: Type your question and press `Ctrl+Enter`
4. **Watch**: The router automatically selects the best agent

### Example Queries

**File Management**
```
"Save this text to a file called notes.txt: Meeting with John tomorrow"
"List all files in my documents"
"Create a directory called ProjectX"
"Read the contents of report.txt"
```

**Calendar Management**
```
"Create a meeting tomorrow at 2pm called Team Sync"
"What events do I have this week?"
"Schedule a dentist appointment for Friday at 10am"
```

**Web Search**
```
"Search for the latest Python 3.12 features"
"What's the current weather in San Francisco?"
"Find information about quantum computing"
```

**Document Analysis**
```
"Analyze the document at ~/Documents/report.pdf"
"Extract text from contract.docx and summarize it"
"What are the key points in research_paper.pdf?"
```

**Code Help**
```
"Write a Python function to calculate Fibonacci numbers"
"Debug this code: [paste code]"
"Run this Python script: print('Hello World')"
```

**General Conversation**
```
"What is machine learning?"
"Explain quantum computing simply"
"Tell me a joke"
```

### Agent Selection

**Automatic (Recommended)**
- Leave agent selector on "auto"
- Router agent analyzes your query
- Best suited agent is automatically selected

**Manual**
- Select specific agent from dropdown
- Useful when you know exactly which agent you need
- Forces routing to that agent regardless of query

### UI Features

**Conversation History**
- Shows all queries and responses
- Color-coded: Blue (you), Green (assistant)
- Agent name displayed for each response
- Tools used shown in purple

**Buttons**
- **Send**: Submit query (or use Ctrl+Enter)
- **Save Response**: Save last response with metadata
- **Clear History**: Reset conversation
- **View Saved**: Browse all saved responses
- **Agents Info**: View available agents and capabilities
- **Hide**: Minimize to system tray

**Status Bar**
- Shows current status (Ready/Processing)
- Displays last agent used

## 🛠️ Configuration

### config.yaml Structure

```yaml
router:
  model: "gemma2:2b"      # Fast model for routing
  temperature: 0.3         # Lower = more consistent routing

agents:
  agent_name:
    model: "ministral:3b"
    description: "What this agent does"
    temperature: 0.7       # Lower = focused, Higher = creative
    tools:                 # Available tools for this agent
      - tool_name_1
      - tool_name_2
```

### Customization Options

**Change Models**
```yaml
# Use different models per agent
code_helper:
  model: "llama3.2:3b"  # Better for code

document_analyst:
  model: "phi3:mini"    # Good for analysis
```

**Adjust Routing Behavior**
```yaml
# Modify agent descriptions for better routing
web_search:
  description: "Current events, news, real-time info, latest updates"
```

**Add Custom Agent**
```yaml
agents:
  data_scientist:
    model: "ministral:3b"
    description: "Data analysis, statistics, visualization"
    temperature: 0.5
    tools:
      - execute_code
      - read_file
      - write_file
```

### Tool Capabilities

**File Operations**
- `read_file(file_path)` - Read file contents
- `write_file(file_path, content, append=False)` - Write to file
- `list_directory(dir_path)` - List directory contents
- `create_directory(dir_path)` - Create directory
- `delete_file(file_path)` - Delete file

**Document Processing**
- `extract_text(file_path)` - Extract text from PDF/DOCX/TXT
- `analyze_document(file_path)` - Get metadata + content analysis

**Web Operations**
- `web_search(query, num_results=5)` - Search using DuckDuckGo
- `fetch_url(url)` - Fetch content from URL

**Calendar** (requires setup)
- `create_event(summary, start_time, end_time, description)` - Create calendar event
- `list_events(max_results=10, time_min=None)` - List upcoming events
- `delete_event(event_id)` - Delete event

**Code Execution**
- `execute_code(code, language="python")` - Run Python code safely

## 🗂️ File Locations

### User Files
- **Conversation History**: `~/.ollama_multi_agent_history.json`
- **Saved Responses**: `~/.ollama_multi_agent_saved.json`
- **Workspace Directory**: `~/OllamaAssistant/` (for file operations)

### Configuration
- **Main Config**: `config.yaml` (in app directory)
- **Calendar Credentials**: `~/.ollama_calendar_credentials.json`
- **Calendar Token**: `~/.ollama_calendar_token.pickle`

## 🔧 Advanced Features

### How Agent Routing Works

1. **Query Analysis**: Router agent (Gemma2 2B) analyzes your query
2. **Agent Selection**: Compares query against agent descriptions
3. **Execution**: Selected agent processes query with available tools
4. **Tool Usage**: Agent can call tools in JSON format
5. **Response**: Agent synthesizes tool results into natural language

### Tool Calling Format

Agents use tools by outputting JSON blocks:

```
```tool
{"tool": "write_file", "params": {"file_path": "notes.txt", "content": "Hello"}}
```
```

The system:
1. Detects tool calls in agent response
2. Executes tools with provided parameters
3. Feeds results back to agent
4. Agent creates final natural language response

### Adding Custom Tools

Edit `agent_system/tools.py`:

```python
def my_custom_tool(self, param1, param2):
    """Description of what this tool does"""
    try:
        # Tool implementation
        result = do_something(param1, param2)

        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

Register in `__init__`:
```python
self.tools["my_custom_tool"] = self.my_custom_tool
```

Add to agent config:
```yaml
agents:
  my_agent:
    tools:
      - my_custom_tool
```

## 🐛 Troubleshooting

### Router Not Working Properly

**Symptoms**: Wrong agents being selected

**Solutions**:
- Refine agent descriptions in `config.yaml`
- Make descriptions more distinct
- Add more keywords to descriptions
- Use manual agent selection temporarily

### Agent Can't Use Tool

**Symptoms**: "Tool not available to this agent"

**Solutions**:
- Check if tool is listed in agent's `tools` array in `config.yaml`
- Verify tool exists in `agent_system/tools.py`
- Check tool name spelling matches exactly

### Calendar Not Working

**Symptoms**: "Google Calendar not configured"

**Solutions**:
1. Verify credentials file exists: `~/.ollama_calendar_credentials.json`
2. Run setup: `python3 setup_google_calendar.py`
3. Check OAuth authorization was completed
4. Test: `python3 setup_google_calendar.py test`

### Document Processing Fails

**Symptoms**: "PyPDF2 not installed" or "python-docx not installed"

**Solutions**:
```bash
pip install PyPDF2 python-docx
```

### Model Not Found

**Symptoms**: "Model 'X' not found"

**Solutions**:
```bash
# Check available models
ollama list

# Pull missing model
ollama pull gemma2:2b
ollama pull ministral:3b
```

### Performance Issues

**Symptoms**: Slow responses

**Solutions**:
- Use smaller models: Change router to `gemma2:2b` (already default)
- Reduce conversation history context (edit `agent_manager.py`, line with `[-10:]`)
- Close other Ollama instances
- Ensure sufficient RAM

## 💡 Tips & Best Practices

### Effective Prompting

**Be Specific About Actions**
- ❌ "Do something with files"
- ✅ "Save this content to project_notes.txt"

**Provide Context**
- ❌ "Analyze it"
- ✅ "Analyze the PDF at ~/Documents/report.pdf"

**Clear Time References for Calendar**
- ❌ "Meeting sometime next week"
- ✅ "Create a meeting on Monday at 3pm"

### Workspace Organization

The app uses `~/OllamaAssistant/` as workspace:
- Relative paths are resolved here
- Keeps files organized
- Use absolute paths for files elsewhere

### Security Considerations

**Code Execution**
- Code runs with your user permissions
- 10-second timeout for safety
- Review code before executing

**File Operations**
- Files created in workspace by default
- Absolute paths work but use cautiously
- No files deleted without explicit request

**Calendar Access**
- OAuth tokens stored locally
- Only you have access
- Revoke access anytime in Google Account settings

### Performance Optimization

**Model Selection**
- Router: Use fastest small model (gemma2:2b)
- Agents: Balance speed vs capability (ministral:3b is good middle ground)
- Specialized tasks: Consider larger models if needed

**Temperature Tuning**
- 0.1-0.3: Factual tasks, routing, file operations
- 0.4-0.6: Analysis, code, research
- 0.7-0.9: Creative writing, brainstorming

## 🎯 Use Cases

### Personal Assistant
- Calendar management
- Note-taking and organization
- Web research
- Document reading

### Developer Tool
- Quick code snippets
- Documentation lookup
- Script execution
- File management

### Research Assistant
- Document analysis
- Information gathering
- Summarization
- Web search

### Productivity Hub
- Task tracking (save responses as tasks)
- Meeting scheduling
- Quick calculations
- Information lookup

## 🔄 Updating

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Update Models
```bash
ollama pull gemma2:2b
ollama pull ministral:3b
```

### Update Application
```bash
git pull  # If using git
# Or download latest version
```

## 📚 Architecture

```
ollama_multi_agent_tray.py          # Main application + UI
├── agent_system/
│   ├── __init__.py                 # Package initialization
│   ├── agent_manager.py            # Agent management + routing
│   │   ├── Agent                   # Base agent class
│   │   ├── RouterAgent             # Query routing
│   │   └── AgentManager            # Orchestration
│   └── tools.py                    # Tool implementations
│       └── ToolRegistry            # Tool management
├── config.yaml                     # Agent configuration
└── setup_google_calendar.py        # Calendar setup utility
```

## 🤝 Contributing Ideas

Enhancement ideas:
- Add more specialized agents (translator, writer, analyst)
- Integrate more APIs (email, Slack, GitHub)
- Add voice input/output
- Create plugin system
- Add multi-modal support (image analysis)
- Database integration
- Task scheduling/automation

## 📄 License

This application is provided as-is for personal and educational use.

## 🙏 Acknowledgments

- **Ollama** for local AI inference
- **Gemma2** for efficient routing
- **Ministral** for capable agent responses
- **DuckDuckGo** for web search
- **Google Calendar API** for calendar integration

## 📞 Support

### For Issues With:

**Ollama**: https://ollama.ai or https://github.com/ollama/ollama

**Google Calendar API**: https://developers.google.com/calendar

**Python Packages**: Check respective package documentation

**This Application**: Review troubleshooting section above

## 🎉 Quick Reference

### Keyboard Shortcuts
- `Ctrl+Shift+A` - Show/hide window (global)
- `Ctrl+Enter` - Send query

### Command Examples
```bash
# Start application
python3 ollama_multi_agent_tray.py

# Setup calendar
python3 setup_google_calendar.py

# Test calendar
python3 setup_google_calendar.py test

# Check Ollama models
ollama list

# Pull model
ollama pull gemma2:2b
```

### File Paths
- Config: `config.yaml`
- History: `~/.ollama_multi_agent_history.json`
- Saved: `~/.ollama_multi_agent_saved.json`
- Workspace: `~/OllamaAssistant/`

---

**Ready to get started?** Run `python3 ollama_multi_agent_tray.py` and press `Ctrl+Shift+A` to access your multi-agent AI assistant!

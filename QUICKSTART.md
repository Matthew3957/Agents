# Quick Start Guide - Multi-Agent Ollama Assistant

Get up and running in 5 minutes!

## 1️⃣ Install Ollama

```bash
# Download from https://ollama.ai
# Or on Linux:
curl -fsSL https://ollama.com/install.sh | sh
```

## 2️⃣ Pull Required Models

```bash
ollama pull gemma2:2b       # Fast router (~1.6GB)
ollama pull ministral:3b    # Agent model (~2.2GB)
```

## 3️⃣ Install Python Dependencies

```bash
# Core dependencies only (no optional features)
pip install pystray Pillow keyboard ollama PyYAML requests

# OR install everything including optional features
pip install -r requirements.txt
```

## 4️⃣ Run the Application

```bash
python3 ollama_multi_agent_tray.py
```

## 5️⃣ Use It!

1. Press **Ctrl+Shift+A** to show the window
2. Type a query and press **Ctrl+Enter**
3. Watch the router select the right agent automatically!

## 🎯 Try These Examples

### File Management
```
"Save this text to notes.txt: Remember to buy milk"
"List files in my directory"
```

### Web Search
```
"Search for Python 3.12 new features"
"What's the weather in Tokyo?"
```

### Code Help
```
"Write a function to reverse a string in Python"
"Run this: print('Hello, World!')"
```

### Document Analysis
```
"Extract text from ~/Documents/report.pdf"
```

### General Questions
```
"What is quantum computing?"
"Explain Docker in simple terms"
```

## ⚙️ Optional Setup

### Google Calendar (Optional)

Only if you want calendar integration:

1. Get credentials from https://console.cloud.google.com/
2. Save as `~/.ollama_calendar_credentials.json`
3. Run: `python3 setup_google_calendar.py`

### Document Processing (Optional)

For PDF/DOCX support:
```bash
pip install PyPDF2 python-docx
```

## 🎨 Customize

Edit `config.yaml` to:
- Change models
- Adjust agent behavior
- Add custom agents
- Modify tool assignments

## 📋 System Requirements

- **Python**: 3.7+
- **RAM**: 4GB+ (for Ollama models)
- **Disk**: ~4GB for models
- **OS**: Linux, macOS, or Windows

## 🚀 Next Steps

Once running:
- Press `Ctrl+Shift+A` to toggle window
- Click "Agents Info" to see available agents
- Use "auto" mode to let the router decide
- Or manually select an agent from the dropdown

## ❓ Troubleshooting

**Can't connect to Ollama?**
```bash
ollama serve  # Start Ollama service
```

**Model not found?**
```bash
ollama list   # Check installed models
ollama pull gemma2:2b  # Pull missing model
```

**Import errors?**
```bash
pip install -r requirements.txt
```

**Hotkey not working?**
- Check if another app uses Ctrl+Shift+A
- Try clicking the system tray icon instead

---

**That's it!** You're ready to use your multi-agent AI assistant. Read the full [README_MULTI_AGENT.md](README_MULTI_AGENT.md) for advanced features.

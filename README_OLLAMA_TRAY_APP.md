# Ollama System Tray Assistant

A lightweight Python-based system tray application that provides quick access to AI assistance using Ministral 3B via Ollama. Access it instantly with a global hotkey for quick queries without interrupting your workflow.

## Features

- **System Tray Integration**: Runs quietly in the background, accessible from your system tray
- **Global Hotkey**: Press `Ctrl+Shift+A` to instantly show/hide the assistant window
- **Conversation History**: Maintains context across queries in the same session
- **Save Responses**: Save useful AI responses for later reference
- **Persistent History**: Conversation history is automatically saved and restored between sessions
- **Clean UI**: Simple, distraction-free interface built with Tkinter
- **Lightweight**: Uses Ministral 3B for fast responses with minimal resource usage

## Screenshots

The application provides:
- A clean conversation interface showing query/response history
- Text input area for your queries
- Quick actions to save responses, clear history, and view saved items
- System tray icon for easy access

## Prerequisites

1. **Python 3.7 or higher**
   ```bash
   python3 --version
   ```

2. **Ollama installed and running**
   - Download from: https://ollama.ai
   - Verify it's running: `ollama list`

3. **Ministral 3B model**
   ```bash
   ollama pull ministral:3b
   ```

## Installation

### Step 1: Clone or Download the Repository

```bash
cd /path/to/your/directory
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pystray Pillow keyboard ollama
```

### Step 3: Verify Ollama is Running

Make sure Ollama is running and the Ministral model is available:

```bash
# Check Ollama is running
ollama list

# If Ministral is not in the list, pull it
ollama pull ministral:3b
```

### Step 4: Run the Application

```bash
python3 ollama_tray_app.py
```

Or make it executable:
```bash
chmod +x ollama_tray_app.py
./ollama_tray_app.py
```

## Usage

### Starting the Application

1. Run the application:
   ```bash
   python3 ollama_tray_app.py
   ```

2. Look for the "AI" icon in your system tray (notification area)

3. The application will print:
   ```
   Ollama Assistant started!
   Press Ctrl+Shift+A to show/hide the window
   Right-click the system tray icon for options
   ```

### Using the Assistant

#### Quick Access with Hotkey
- Press `Ctrl+Shift+A` anywhere to show/hide the assistant window
- The window appears on top of other windows for quick access

#### Sending Queries
- Type your question in the input box
- Press `Ctrl+Enter` or click "Send" to submit
- The AI response appears in the conversation history

#### Saving Useful Responses
- Click "Save Last Response" to save the most recent AI answer
- Saved responses are stored with timestamps and original queries
- Access saved responses anytime with "View Saved"

#### Managing History
- Conversation history is maintained during your session
- History is automatically saved when you close the window
- Previous conversations are restored when you reopen the app
- Click "Clear History" to start fresh

#### Closing/Hiding
- Click "Hide" or press `Ctrl+Shift+A` to hide the window
- The app continues running in the system tray
- Right-click the tray icon and select "Quit" to fully exit

## File Locations

The application stores data in your home directory:

- **Conversation History**: `~/.ollama_assistant_history.json`
- **Saved Responses**: `~/.ollama_assistant_saved.json`

## Configuration

### Changing the AI Model

Edit `ollama_tray_app.py` and change the model parameter:

```python
# Line 46
def __init__(self, model="ministral:3b"):
```

Other compatible models:
- `llama3.2:3b` - Llama 3.2 3B
- `phi3:mini` - Microsoft Phi-3 Mini
- `gemma2:2b` - Google Gemma 2 2B

### Changing the Global Hotkey

Edit `ollama_tray_app.py` and modify the hotkey:

```python
# Line 387
keyboard.add_hotkey('ctrl+shift+a', self.toggle_window)
```

Examples:
- `'ctrl+alt+o'` - Ctrl+Alt+O
- `'ctrl+space'` - Ctrl+Space
- `'alt+a'` - Alt+A

### Customizing the Icon

The system tray icon is generated in the `create_image()` method. You can:
- Change the background color (default: `'#2196F3'`)
- Replace with a custom image file
- Modify the "AI" text

## Troubleshooting

### Application Won't Start

**Error: Cannot connect to Ollama**
- Ensure Ollama is running: `ollama serve`
- Check if you can run: `ollama list`
- On Linux, make sure the Ollama service is started

**Error: ministral model not found**
- Pull the model: `ollama pull ministral:3b`
- Or choose to continue with another model

### Hotkey Not Working

**Ctrl+Shift+A doesn't respond**
- Check if another application is using the same hotkey
- Try changing to a different hotkey combination
- On Linux, you might need to run with sudo (not recommended for security)
- Some desktop environments may intercept certain key combinations

### Permission Issues (Linux)

**keyboard module requires root**
- The `keyboard` library requires elevated permissions on Linux
- Alternative: Use without global hotkey by accessing from system tray only
- Or use an alternative like `pynput` (requires code modification)

### Module Import Errors

```bash
# Install missing dependencies
pip install pystray Pillow keyboard ollama
```

### Window Not Appearing

- Check if the window is hidden behind other windows
- Try pressing `Ctrl+Shift+A` twice
- Right-click the tray icon and select "Show/Hide"

## Running on Startup

### Linux (systemd)

Create a service file: `~/.config/systemd/user/ollama-assistant.service`

```ini
[Unit]
Description=Ollama System Tray Assistant
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/ollama_tray_app.py
Restart=on-failure

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable ollama-assistant
systemctl --user start ollama-assistant
```

### Linux (Desktop Entry)

Create: `~/.config/autostart/ollama-assistant.desktop`

```ini
[Desktop Entry]
Type=Application
Name=Ollama Assistant
Exec=/usr/bin/python3 /path/to/ollama_tray_app.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

### macOS

Add to Login Items:
1. System Preferences → Users & Groups
2. Login Items tab
3. Click "+" and add the script

Or use launchd:
Create: `~/Library/LaunchAgents/com.ollama.assistant.plist`

### Windows

1. Press `Win+R` and type `shell:startup`
2. Create a shortcut to `ollama_tray_app.py`
3. Or create a batch file:

```batch
@echo off
python "C:\path\to\ollama_tray_app.py"
```

## Advanced Usage

### Keyboard Shortcuts

- `Ctrl+Shift+A` - Show/hide window (global)
- `Ctrl+Enter` - Send query (in window)

### Tips

1. **Quick Questions**: Use for quick lookups without opening a browser
2. **Code Snippets**: Ask for code examples and save useful ones
3. **Definitions**: Get quick explanations of technical terms
4. **Brainstorming**: Keep conversation history for ongoing ideation
5. **Documentation**: Save important responses as reference material

## Uninstalling

1. Stop the application (right-click tray icon → Quit)
2. Remove the application files
3. Optionally remove data files:
   ```bash
   rm ~/.ollama_assistant_history.json
   rm ~/.ollama_assistant_saved.json
   ```
4. Uninstall Python packages (if not used elsewhere):
   ```bash
   pip uninstall pystray Pillow keyboard ollama
   ```

## Security Considerations

- The application stores conversation history locally in JSON files
- Saved responses are stored in plain text
- No data is sent anywhere except to your local Ollama instance
- Be cautious about saving sensitive information in responses
- File permissions are set to user-only by default

## Performance

- **Memory**: ~50-100MB (Python + Tkinter)
- **CPU**: Minimal when idle, depends on Ollama during queries
- **Startup Time**: <1 second
- **Response Time**: Depends on Ollama and model (typically 1-3 seconds for Ministral 3B)

## Customization Ideas

1. **Add Multiple Models**: Create a dropdown to switch between models
2. **Temperature Control**: Add slider for response creativity
3. **System Prompts**: Predefined prompts for common tasks
4. **Export History**: Export conversations to markdown or PDF
5. **Themes**: Add dark mode or custom color schemes
6. **Plugins**: Integrate with other tools or services

## Dependencies

- **pystray**: System tray integration
- **Pillow (PIL)**: Image handling for tray icon
- **keyboard**: Global hotkey support
- **ollama**: Python client for Ollama API
- **tkinter**: GUI framework (included with Python)

## License

This application is provided as-is for personal and educational use.

## Contributing

Feel free to modify and enhance the application for your needs. Suggested improvements:
- Better error handling
- More keyboard shortcuts
- Custom themes
- Plugin system
- Multi-language support

## Support

For issues with:
- **Ollama**: Visit https://ollama.ai or https://github.com/ollama/ollama
- **Python packages**: Check respective package documentation
- **This application**: Review the troubleshooting section above

## Changelog

### Version 1.0
- Initial release
- System tray integration
- Global hotkey support (Ctrl+Shift+A)
- Conversation history
- Save responses feature
- Persistent storage
- Ministral 3B integration

## Acknowledgments

- Built with Ollama for local AI inference
- Uses Ministral 3B for efficient, fast responses
- UI built with Python Tkinter for cross-platform compatibility

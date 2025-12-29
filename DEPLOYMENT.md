# Deployment Guide - Running Without Terminal

This guide covers various methods to run the Ollama Multi-Agent Assistant in the background without keeping a terminal or PowerShell window open.

## 📋 Prerequisites

Before deploying, ensure you have:
1. **Ollama installed and running**
2. **Required models pulled**:
   ```bash
   ollama pull gemma3:1b    # Simple tasks (~1GB)
   ollama pull gemma2:2b    # Medium tasks (~1.6GB)
   ollama pull gemma3:4b    # Complex tasks (~2.5GB)
   ```
3. **Python dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🐧 Linux Deployment

### Option 1: systemd Service (Recommended)

**Best for**: Automatic startup on boot, system-wide deployment

**Setup**:

1. Edit the service file to match your paths:
   ```bash
   nano ollama-assistant.service
   ```

   Update these lines:
   ```ini
   WorkingDirectory=/home/YOUR_USERNAME/path/to/Agents
   ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/path/to/Agents/ollama_multi_agent_tray.py
   ```

2. Install the service:
   ```bash
   # For user service (recommended)
   mkdir -p ~/.config/systemd/user/
   cp ollama-assistant.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable ollama-assistant.service
   systemctl --user start ollama-assistant.service
   ```

   Or for system-wide service:
   ```bash
   sudo cp ollama-assistant.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable ollama-assistant.service
   sudo systemctl start ollama-assistant.service
   ```

3. Check status:
   ```bash
   systemctl --user status ollama-assistant.service
   ```

4. View logs:
   ```bash
   journalctl --user -u ollama-assistant.service -f
   ```

**Control commands**:
```bash
# Start
systemctl --user start ollama-assistant

# Stop
systemctl --user stop ollama-assistant

# Restart
systemctl --user restart ollama-assistant

# Disable auto-start
systemctl --user disable ollama-assistant
```

### Option 2: Background Script

**Best for**: Simple deployment, easy control

**Setup**:

1. Make the script executable:
   ```bash
   chmod +x run_background.sh
   ```

2. Start the assistant:
   ```bash
   ./run_background.sh start
   ```

**Commands**:
```bash
# Start in background
./run_background.sh start

# Stop
./run_background.sh stop

# Restart
./run_background.sh restart

# Check status
./run_background.sh status

# View logs (live)
./run_background.sh logs
```

### Option 3: Docker (Linux with X11)

**Best for**: Isolated environment, easy updates

**Requirements**:
- Docker and Docker Compose installed
- X11 forwarding enabled

**Setup**:

1. Enable X11 forwarding:
   ```bash
   xhost +local:docker
   ```

2. Build and start:
   ```bash
   docker-compose up -d --build
   ```

3. View logs:
   ```bash
   docker-compose logs -f
   ```

**Commands**:
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up -d --build
```

**Notes**:
- The container needs access to X11 for the GUI
- Hotkey functionality may be limited in container
- Best for Linux hosts only

---

## 🪟 Windows Deployment

### Option 1: Windows Service with NSSM (Recommended)

**Best for**: Automatic startup, runs in background

**Prerequisites**:
Install NSSM (Non-Sucking Service Manager):
```powershell
# Using Chocolatey
choco install nssm

# Or download from https://nssm.cc/
```

**Setup**:

1. Right-click `install_windows_service.bat`
2. Select "Run as administrator"
3. Follow the prompts

The script will:
- Install the assistant as a Windows service
- Configure it to start automatically
- Start the service immediately

**Manual NSSM setup**:
```powershell
# Install service
nssm install OllamaAssistant "C:\Python311\python.exe" "C:\path\to\ollama_multi_agent_tray.py"
nssm set OllamaAssistant AppDirectory "C:\path\to\Agents"
nssm set OllamaAssistant DisplayName "Ollama Multi-Agent Assistant"
nssm set OllamaAssistant Start SERVICE_AUTO_START

# Start service
nssm start OllamaAssistant
```

**Control**:
```powershell
# Start
nssm start OllamaAssistant

# Stop
nssm stop OllamaAssistant

# Restart
nssm restart OllamaAssistant

# Remove service
nssm remove OllamaAssistant confirm
```

### Option 2: Task Scheduler

**Best for**: Scheduled startup, no admin rights needed

**Setup**:

1. Open Task Scheduler
2. Create Basic Task
3. Configure:
   - **Name**: Ollama Assistant
   - **Trigger**: At log on
   - **Action**: Start a program
   - **Program**: `pythonw.exe` (not python.exe!)
   - **Arguments**: `"C:\path\to\ollama_multi_agent_tray.py"`
   - **Start in**: `C:\path\to\Agents`
4. Additional settings:
   - ✓ Run whether user is logged on or not
   - ✓ Run with highest privileges
   - ✓ Hidden

### Option 3: Startup Folder

**Best for**: Simple, user-level startup

**Setup**:

1. Press `Win+R`, type: `shell:startup`, press Enter
2. Create a batch file: `start_ollama_assistant.bat`
   ```batch
   @echo off
   cd /d "C:\path\to\Agents"
   start /min pythonw.exe ollama_multi_agent_tray.py
   ```
3. Save in the Startup folder

**Note**: Uses `pythonw.exe` (not `python.exe`) to run without console window.

---

## 🍎 macOS Deployment

### Option 1: launchd Service (Recommended)

**Best for**: Automatic startup, system integration

**Setup**:

1. Create plist file:
   ```bash
   nano ~/Library/LaunchAgents/com.ollama.assistant.plist
   ```

2. Add this content:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.ollama.assistant</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/local/bin/python3</string>
           <string>/Users/YOUR_USERNAME/path/to/Agents/ollama_multi_agent_tray.py</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/Users/YOUR_USERNAME/path/to/Agents</string>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/tmp/ollama-assistant.log</string>
       <key>StandardErrorPath</key>
       <string>/tmp/ollama-assistant-error.log</string>
   </dict>
   </plist>
   ```

3. Update paths in the plist file

4. Load the service:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.ollama.assistant.plist
   ```

**Control**:
```bash
# Start
launchctl start com.ollama.assistant

# Stop
launchctl stop com.ollama.assistant

# Unload (disable auto-start)
launchctl unload ~/Library/LaunchAgents/com.ollama.assistant.plist

# View logs
tail -f /tmp/ollama-assistant.log
```

### Option 2: Login Items

**Best for**: Simple user-level startup

**Setup**:

1. System Preferences → Users & Groups
2. Select your user → Login Items
3. Click "+" and add `ollama_multi_agent_tray.py`
4. Or use a wrapper script for better control

### Option 3: Background Script

Use the same `run_background.sh` as Linux:

```bash
chmod +x run_background.sh
./run_background.sh start
```

---

## 🔧 Environment Configuration

### Setting Ollama Host

If Ollama is not running on localhost:

**Linux/macOS**:
```bash
export OLLAMA_HOST=http://192.168.1.100:11434
```

**Windows**:
```powershell
setx OLLAMA_HOST "http://192.168.1.100:11434"
```

**Docker**:
Edit `docker-compose.yml`:
```yaml
environment:
  - OLLAMA_HOST=http://192.168.1.100:11434
```

---

## 🐛 Troubleshooting

### Service Won't Start

**Check Ollama is running**:
```bash
curl http://localhost:11434/api/tags
```

**Check models are available**:
```bash
ollama list
```

**View logs**:
- **Linux systemd**: `journalctl --user -u ollama-assistant -f`
- **Windows NSSM**: Check Event Viewer → Application logs
- **macOS launchd**: `tail -f /tmp/ollama-assistant.log`
- **Background script**: `./run_background.sh logs`

### GUI Not Showing

**Linux**: Check DISPLAY variable and X11 access
```bash
echo $DISPLAY
xhost +local:
```

**Windows**: Ensure running as the logged-in user, not SYSTEM

**macOS**: Check permissions in System Preferences → Security & Privacy

### Hotkey Not Working

**Linux**:
- Service needs to run as your user (not root)
- Check keyboard library has permissions

**Windows**:
- Service must run as logged-in user
- May need "Run with highest privileges"

**macOS**:
- Grant accessibility permissions to Python
- System Preferences → Security & Privacy → Accessibility

### High CPU/Memory Usage

**Check which models are loaded**:
```bash
curl http://localhost:11434/api/ps
```

**Reduce model count**: Edit `config.yaml` to use fewer models

**Restart service**: Reload models
```bash
# Linux
systemctl --user restart ollama-assistant

# Windows
nssm restart OllamaAssistant

# macOS
launchctl stop com.ollama.assistant
launchctl start com.ollama.assistant
```

---

## 📊 Monitoring

### Check Service Status

**Linux**:
```bash
systemctl --user status ollama-assistant
# or
./run_background.sh status
```

**Windows**:
```powershell
nssm status OllamaAssistant
# or
Get-Service OllamaAssistant
```

**macOS**:
```bash
launchctl list | grep ollama
```

### View Logs

**Linux systemd**:
```bash
journalctl --user -u ollama-assistant -f --since "10 minutes ago"
```

**Linux background script**:
```bash
./run_background.sh logs
```

**Windows**:
```powershell
# Event Viewer
eventvwr.msc

# Or check NSSM logs
nssm dump OllamaAssistant
```

**macOS**:
```bash
tail -f /tmp/ollama-assistant.log
```

**Docker**:
```bash
docker-compose logs -f --tail=100
```

---

## 🔄 Updating

### Update Application

1. **Stop the service**
2. **Pull latest changes** (if using git)
3. **Update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```
4. **Pull new models** (if needed):
   ```bash
   ollama pull gemma3:1b
   ollama pull gemma2:2b
   ollama pull gemma3:4b
   ```
5. **Restart the service**

### Update Models Only

```bash
# Update all models
ollama pull gemma3:1b
ollama pull gemma2:2b
ollama pull gemma3:4b

# Restart to use new models
# (service command depends on your platform)
```

---

## 🎯 Best Practices

1. **Use systemd/NSSM** for production deployments
2. **Monitor logs** regularly for errors
3. **Keep models updated** for best performance
4. **Configure auto-restart** in case of crashes
5. **Use background script** for development/testing
6. **Set resource limits** if running on shared systems
7. **Back up configuration** before major changes

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs for error messages
2. Verify Ollama is accessible
3. Ensure all models are pulled
4. Test running manually first: `python3 ollama_multi_agent_tray.py`
5. Check firewall/permissions

---

## 📝 Quick Reference

### Start Commands by Platform

**Linux systemd**:
```bash
systemctl --user start ollama-assistant
```

**Linux background**:
```bash
./run_background.sh start
```

**Windows service**:
```powershell
nssm start OllamaAssistant
```

**macOS launchd**:
```bash
launchctl start com.ollama.assistant
```

**Docker**:
```bash
docker-compose up -d
```

### Stop Commands

Replace `start` with `stop` in the commands above.

### View Logs

**Linux systemd**:
```bash
journalctl --user -u ollama-assistant -f
```

**Background script**:
```bash
./run_background.sh logs
```

**Docker**:
```bash
docker-compose logs -f
```

---

**Recommendation**: For most users, use the systemd service (Linux), NSSM service (Windows), or launchd (macOS) for the best experience.

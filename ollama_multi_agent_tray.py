#!/usr/bin/env python3
"""
Ollama Multi-Agent System Tray Application
A system tray app with intelligent agent routing for various tasks
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
from datetime import datetime
from pathlib import Path
import sys
import yaml
import re

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
except ImportError:
    print("Error: pystray or PIL not installed. Run: pip install pystray Pillow")
    sys.exit(1)

try:
    import keyboard
except ImportError:
    print("Error: keyboard not installed. Run: pip install keyboard")
    sys.exit(1)

try:
    import ollama
except ImportError:
    print("Error: ollama not installed. Run: pip install ollama")
    sys.exit(1)

# Import agent system
from agent_system.agent_manager import AgentManager
from agent_system.tools import ToolRegistry


class MultiAgentAssistant:
    """Main assistant coordinating multiple specialized agents"""

    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.tool_registry = ToolRegistry()
        self.agent_manager = AgentManager(self.config, self.tool_registry)
        self.conversation_history = []

    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        if not os.path.exists(config_path):
            # Return default config
            return {
                "router": {
                    "model": "gemma2:2b",
                    "temperature": 0.3
                },
                "agents": {
                    "general": {
                        "model": "ministral:3b",
                        "description": "General conversation and questions",
                        "temperature": 0.7
                    },
                    "file_manager": {
                        "model": "ministral:3b",
                        "description": "File operations, saving documents, managing files",
                        "temperature": 0.3,
                        "tools": ["read_file", "write_file", "list_directory", "create_directory"]
                    },
                    "calendar": {
                        "model": "ministral:3b",
                        "description": "Calendar management, scheduling, events",
                        "temperature": 0.3,
                        "tools": ["create_event", "list_events", "delete_event"]
                    },
                    "web_search": {
                        "model": "ministral:3b",
                        "description": "Internet search, current information, web queries",
                        "temperature": 0.5,
                        "tools": ["web_search", "fetch_url"]
                    },
                    "document_analyst": {
                        "model": "ministral:3b",
                        "description": "Document reading, analysis, summarization",
                        "temperature": 0.4,
                        "tools": ["read_file", "analyze_document", "extract_text"]
                    },
                    "code_helper": {
                        "model": "ministral:3b",
                        "description": "Code writing, debugging, technical questions",
                        "temperature": 0.6,
                        "tools": ["read_file", "write_file", "execute_code"]
                    }
                }
            }

        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def query(self, prompt, use_history=True):
        """Process query through the agent system"""
        try:
            # Add user message to history
            if use_history:
                self.conversation_history.append({
                    "role": "user",
                    "content": prompt,
                    "timestamp": datetime.now().isoformat()
                })

            # Let agent manager route and execute
            result = self.agent_manager.process_query(
                prompt,
                self.conversation_history if use_history else []
            )

            # Add response to history
            if use_history:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": result["response"],
                    "agent": result["agent_used"],
                    "tools_used": result.get("tools_used", []),
                    "timestamp": datetime.now().isoformat()
                })

            return result

        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "agent_used": "error",
                "tools_used": [],
                "error": str(e)
            }

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self):
        """Get conversation history"""
        return self.conversation_history.copy()

    def get_available_agents(self):
        """Get list of available agents"""
        return self.agent_manager.get_agent_list()


class MultiAgentWindow:
    """Enhanced UI window for multi-agent assistant"""

    def __init__(self, assistant, saved_responses_file):
        self.assistant = assistant
        self.saved_responses_file = saved_responses_file
        self.window = None
        self.is_visible = False

    def create_window(self):
        """Create the main window"""
        if self.window:
            self.show()
            return

        self.window = tk.Tk()
        self.window.title("Multi-Agent Ollama Assistant")
        self.window.geometry("900x700")

        # Make window appear on top
        self.window.attributes('-topmost', True)

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

        # Create UI elements
        self._create_widgets()

        self.is_visible = True
        self.window.mainloop()

    def _create_widgets(self):
        """Create all UI widgets"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Header frame
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(header_frame, text="Multi-Agent AI Assistant",
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Agent info label
        self.agent_info_label = ttk.Label(header_frame, text="Ready",
                                         font=('Arial', 9), foreground='#666')
        self.agent_info_label.grid(row=0, column=1, sticky=tk.E)

        # Agent selector
        agent_frame = ttk.Frame(main_frame)
        agent_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(agent_frame, text="Force Agent:").grid(row=0, column=0, padx=(0, 5))

        self.agent_var = tk.StringVar(value="auto")
        agents = ["auto"] + list(self.assistant.get_available_agents().keys())
        self.agent_combo = ttk.Combobox(agent_frame, textvariable=self.agent_var,
                                       values=agents, state='readonly', width=20)
        self.agent_combo.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(agent_frame, text="(Auto = Router decides)",
                 foreground='#666').grid(row=0, column=2)

        # Conversation history display
        history_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD,
                                                      width=100, height=20)
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_text.config(state=tk.DISABLED)

        # Configure tags for styling
        self.history_text.tag_config("user", foreground="#0066cc", font=('Arial', 10, 'bold'))
        self.history_text.tag_config("assistant", foreground="#009900", font=('Arial', 10, 'bold'))
        self.history_text.tag_config("agent_info", foreground="#ff6600", font=('Arial', 9, 'italic'))
        self.history_text.tag_config("tool_info", foreground="#9933cc", font=('Arial', 9, 'italic'))
        self.history_text.tag_config("message", foreground="#000000")

        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        ttk.Label(input_frame, text="Your Query:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.input_text = tk.Text(input_frame, wrap=tk.WORD, width=100, height=3)
        self.input_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.input_text.bind('<Control-Return>', lambda e: self.send_query())

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.send_button = ttk.Button(button_frame, text="Send (Ctrl+Enter)",
                                      command=self.send_query)
        self.send_button.grid(row=0, column=0, padx=(0, 5))

        ttk.Button(button_frame, text="Save Response",
                  command=self.save_last_response).grid(row=0, column=1, padx=(0, 5))

        ttk.Button(button_frame, text="Clear History",
                  command=self.clear_history).grid(row=0, column=2, padx=(0, 5))

        ttk.Button(button_frame, text="View Saved",
                  command=self.view_saved_responses).grid(row=0, column=3, padx=(0, 5))

        ttk.Button(button_frame, text="Agents Info",
                  command=self.show_agents_info).grid(row=0, column=4, padx=(0, 5))

        ttk.Button(button_frame, text="Hide",
                  command=self.hide).grid(row=0, column=5)

        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # Load previous conversation if exists
        self._load_conversation()

    def _append_to_history(self, role, message, agent_used=None, tools_used=None):
        """Append a message to the history display"""
        self.history_text.config(state=tk.NORMAL)

        if self.history_text.get("1.0", tk.END).strip():
            self.history_text.insert(tk.END, "\n\n")

        # Add role label
        timestamp = datetime.now().strftime("%H:%M:%S")
        if role == "user":
            self.history_text.insert(tk.END, f"[{timestamp}] You: ", "user")
        else:
            self.history_text.insert(tk.END, f"[{timestamp}] Assistant: ", "assistant")

        # Add agent and tool info if available
        if agent_used:
            self.history_text.insert(tk.END, f"\n  [Agent: {agent_used}", "agent_info")
            if tools_used:
                self.history_text.insert(tk.END, f" | Tools: {', '.join(tools_used)}", "tool_info")
            self.history_text.insert(tk.END, "]\n", "agent_info")

        self.history_text.insert(tk.END, message, "message")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)

    def send_query(self):
        """Send query to the multi-agent system"""
        query = self.input_text.get("1.0", tk.END).strip()
        if not query:
            return

        # Check if forcing a specific agent
        force_agent = None if self.agent_var.get() == "auto" else self.agent_var.get()

        # Disable send button
        self.send_button.config(state=tk.DISABLED)
        self.status_label.config(text="Processing...")
        self.agent_info_label.config(text="Routing query...")

        # Clear input
        self.input_text.delete("1.0", tk.END)

        # Add query to history display
        self._append_to_history("user", query)

        # Process in background thread
        def process():
            if force_agent:
                # Directly use specified agent
                result = self.assistant.agent_manager.execute_with_agent(
                    force_agent, query, self.assistant.conversation_history
                )
            else:
                # Let router decide
                result = self.assistant.query(query)

            self.window.after(0, lambda: self._handle_response(result))

        threading.Thread(target=process, daemon=True).start()

    def _handle_response(self, result):
        """Handle the response from the agent system"""
        response = result.get("response", "No response")
        agent_used = result.get("agent_used", "unknown")
        tools_used = result.get("tools_used", [])

        self._append_to_history("assistant", response, agent_used, tools_used)
        self.send_button.config(state=tk.NORMAL)
        self.status_label.config(text="Ready")
        self.agent_info_label.config(text=f"Last: {agent_used}")
        self._save_conversation()

    def show_agents_info(self):
        """Show information about available agents"""
        agents = self.assistant.get_available_agents()

        info_window = tk.Toplevel(self.window)
        info_window.title("Available Agents")
        info_window.geometry("700x500")

        text_widget = scrolledtext.ScrolledText(info_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget.insert(tk.END, "═══ AVAILABLE AGENTS ═══\n\n", "header")

        for agent_name, agent_info in agents.items():
            text_widget.insert(tk.END, f"🤖 {agent_name.upper()}\n", "bold")
            text_widget.insert(tk.END, f"Description: {agent_info['description']}\n")
            text_widget.insert(tk.END, f"Model: {agent_info['model']}\n")
            if agent_info.get('tools'):
                text_widget.insert(tk.END, f"Tools: {', '.join(agent_info['tools'])}\n")
            text_widget.insert(tk.END, "\n" + "─" * 70 + "\n\n")

        text_widget.config(state=tk.DISABLED)

    def save_last_response(self):
        """Save the last assistant response to file"""
        history = self.assistant.get_history()
        if not history:
            messagebox.showinfo("No History", "No responses to save yet.")
            return

        # Find last assistant message
        last_response = None
        last_query = None
        agent_used = None
        tools_used = []

        for i in range(len(history) - 1, -1, -1):
            if history[i]["role"] == "assistant" and last_response is None:
                last_response = history[i]["content"]
                agent_used = history[i].get("agent", "unknown")
                tools_used = history[i].get("tools_used", [])
                # Find corresponding query
                if i > 0 and history[i-1]["role"] == "user":
                    last_query = history[i-1]["content"]
                break

        if not last_response:
            messagebox.showinfo("No Response", "No assistant response found.")
            return

        # Load existing saved responses
        saved = []
        if os.path.exists(self.saved_responses_file):
            try:
                with open(self.saved_responses_file, 'r') as f:
                    saved = json.load(f)
            except:
                saved = []

        # Add new response
        saved.append({
            "timestamp": datetime.now().isoformat(),
            "query": last_query,
            "response": last_response,
            "agent": agent_used,
            "tools_used": tools_used
        })

        # Save to file
        with open(self.saved_responses_file, 'w') as f:
            json.dump(saved, f, indent=2)

        messagebox.showinfo("Saved", f"Response saved! (Agent: {agent_used})")

    def view_saved_responses(self):
        """View all saved responses"""
        if not os.path.exists(self.saved_responses_file):
            messagebox.showinfo("No Saved Responses", "No saved responses yet.")
            return

        try:
            with open(self.saved_responses_file, 'r') as f:
                saved = json.load(f)
        except:
            messagebox.showerror("Error", "Could not load saved responses.")
            return

        if not saved:
            messagebox.showinfo("No Saved Responses", "No saved responses yet.")
            return

        # Create new window
        view_window = tk.Toplevel(self.window)
        view_window.title("Saved Responses")
        view_window.geometry("800x600")

        # Create text widget
        text_widget = scrolledtext.ScrolledText(view_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add saved responses
        for i, item in enumerate(saved, 1):
            timestamp = datetime.fromisoformat(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            text_widget.insert(tk.END, f"═══ Saved Response #{i} ═══\n", "header")
            text_widget.insert(tk.END, f"Time: {timestamp}\n")
            text_widget.insert(tk.END, f"Agent: {item.get('agent', 'unknown')}\n")
            if item.get("tools_used"):
                text_widget.insert(tk.END, f"Tools: {', '.join(item['tools_used'])}\n")
            text_widget.insert(tk.END, "\n")
            if item.get("query"):
                text_widget.insert(tk.END, "Query:\n", "bold")
                text_widget.insert(tk.END, f"{item['query']}\n\n")
            text_widget.insert(tk.END, "Response:\n", "bold")
            text_widget.insert(tk.END, f"{item['response']}\n\n")
            text_widget.insert(tk.END, "─" * 80 + "\n\n")

        text_widget.config(state=tk.DISABLED)

    def clear_history(self):
        """Clear conversation history"""
        if messagebox.askyesno("Clear History", "Clear conversation history?"):
            self.assistant.clear_history()
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete("1.0", tk.END)
            self.history_text.config(state=tk.DISABLED)
            self._save_conversation()
            self.status_label.config(text="History cleared")
            self.agent_info_label.config(text="Ready")

    def _save_conversation(self):
        """Save conversation to file"""
        history_file = Path.home() / ".ollama_multi_agent_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.assistant.get_history(), f, indent=2)
        except Exception as e:
            print(f"Could not save conversation: {e}")

    def _load_conversation(self):
        """Load conversation from file"""
        history_file = Path.home() / ".ollama_multi_agent_history.json"
        if not history_file.exists():
            return

        try:
            with open(history_file, 'r') as f:
                history = json.load(f)

            self.assistant.conversation_history = history

            # Display in UI
            for msg in history:
                agent = msg.get("agent") if msg["role"] == "assistant" else None
                tools = msg.get("tools_used", []) if msg["role"] == "assistant" else None
                self._append_to_history(msg["role"], msg["content"], agent, tools)
        except Exception as e:
            print(f"Could not load conversation: {e}")

    def show(self):
        """Show the window"""
        if self.window:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            self.is_visible = True

    def hide(self):
        """Hide the window"""
        if self.window:
            self.window.withdraw()
            self.is_visible = False

    def toggle(self):
        """Toggle window visibility"""
        if self.is_visible:
            self.hide()
        else:
            self.show()


class TrayApp:
    """System tray application for multi-agent assistant"""

    def __init__(self):
        self.assistant = MultiAgentAssistant()
        self.saved_responses_file = Path.home() / ".ollama_multi_agent_saved.json"
        self.window = MultiAgentWindow(self.assistant, self.saved_responses_file)
        self.icon = None
        self.hotkey_registered = False

    def create_image(self):
        """Create system tray icon"""
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='#FF6600')
        dc = ImageDraw.Draw(image)

        # Draw multi-agent symbol
        dc.ellipse([10, 10, 25, 25], fill='white')
        dc.ellipse([39, 10, 54, 25], fill='white')
        dc.ellipse([25, 39, 40, 54], fill='white')

        return image

    def setup_hotkey(self):
        """Setup global hotkey"""
        try:
            keyboard.add_hotkey('ctrl+shift+a', self.toggle_window)
            self.hotkey_registered = True
            print("Hotkey registered: Ctrl+Shift+A")
        except Exception as e:
            print(f"Could not register hotkey: {e}")

    def toggle_window(self):
        """Toggle window visibility"""
        if not self.window.window:
            threading.Thread(target=self.window.create_window, daemon=True).start()
        else:
            self.window.toggle()

    def show_window(self, icon, item):
        """Show window from tray menu"""
        self.toggle_window()

    def quit_app(self, icon, item):
        """Quit the application"""
        if self.hotkey_registered:
            keyboard.unhook_all()
        icon.stop()
        if self.window.window:
            self.window.window.quit()

    def run(self):
        """Run the application"""
        self.setup_hotkey()

        menu = (
            item('Show/Hide (Ctrl+Shift+A)', self.show_window, default=True),
            item('Quit', self.quit_app)
        )

        self.icon = pystray.Icon(
            "ollama_multi_agent",
            self.create_image(),
            "Multi-Agent Ollama Assistant",
            menu
        )

        print("Multi-Agent Ollama Assistant started!")
        print("Press Ctrl+Shift+A to show/hide the window")
        print(f"Available agents: {', '.join(self.assistant.get_available_agents().keys())}")

        self.icon.run()


def main():
    """Main entry point"""
    # Check if Ollama is accessible
    try:
        ollama.list()
    except Exception as e:
        print(f"Error: Cannot connect to Ollama. Make sure Ollama is running.")
        print(f"Details: {e}")
        sys.exit(1)

    app = TrayApp()
    app.run()


if __name__ == "__main__":
    main()

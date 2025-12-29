#!/usr/bin/env python3
"""
Ollama System Tray Application
A system tray app for quick AI queries using Ministral 3B via Ollama
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
from datetime import datetime
from pathlib import Path
import sys

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


class OllamaAssistant:
    """Handles communication with Ollama API"""

    def __init__(self, model="ministral:3b"):
        self.model = model
        self.conversation_history = []

    def query(self, prompt, use_history=True):
        """Send a query to Ollama and get response"""
        try:
            if use_history:
                messages = self.conversation_history + [{"role": "user", "content": prompt}]
            else:
                messages = [{"role": "user", "content": prompt}]

            response = ollama.chat(
                model=self.model,
                messages=messages
            )

            assistant_message = response['message']['content']

            # Add to history
            if use_history:
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self):
        """Get conversation history"""
        return self.conversation_history.copy()


class AssistantWindow:
    """Main UI window for the assistant"""

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
        self.window.title("Ollama Assistant - Ministral 3B")
        self.window.geometry("700x600")

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
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Ollama Quick Assistant",
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        # Conversation history display
        history_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        history_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD,
                                                      width=80, height=20)
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_text.config(state=tk.DISABLED)

        # Configure tags for styling
        self.history_text.tag_config("user", foreground="#0066cc", font=('Arial', 10, 'bold'))
        self.history_text.tag_config("assistant", foreground="#009900", font=('Arial', 10, 'bold'))
        self.history_text.tag_config("message", foreground="#000000")

        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        ttk.Label(input_frame, text="Your Query:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.input_text = tk.Text(input_frame, wrap=tk.WORD, width=80, height=3)
        self.input_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.input_text.bind('<Control-Return>', lambda e: self.send_query())

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.send_button = ttk.Button(button_frame, text="Send (Ctrl+Enter)",
                                      command=self.send_query)
        self.send_button.grid(row=0, column=0, padx=(0, 5))

        ttk.Button(button_frame, text="Save Last Response",
                  command=self.save_last_response).grid(row=0, column=1, padx=(0, 5))

        ttk.Button(button_frame, text="Clear History",
                  command=self.clear_history).grid(row=0, column=2, padx=(0, 5))

        ttk.Button(button_frame, text="View Saved",
                  command=self.view_saved_responses).grid(row=0, column=3, padx=(0, 5))

        ttk.Button(button_frame, text="Hide (Ctrl+Shift+A)",
                  command=self.hide).grid(row=0, column=4)

        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # Load previous conversation if exists
        self._load_conversation()

    def _append_to_history(self, role, message):
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

        self.history_text.insert(tk.END, message, "message")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)

    def send_query(self):
        """Send query to Ollama"""
        query = self.input_text.get("1.0", tk.END).strip()
        if not query:
            return

        # Disable send button
        self.send_button.config(state=tk.DISABLED)
        self.status_label.config(text="Processing...")

        # Clear input
        self.input_text.delete("1.0", tk.END)

        # Add query to history display
        self._append_to_history("user", query)

        # Process in background thread
        def process():
            response = self.assistant.query(query)
            self.window.after(0, lambda: self._handle_response(response))

        threading.Thread(target=process, daemon=True).start()

    def _handle_response(self, response):
        """Handle the response from Ollama"""
        self._append_to_history("assistant", response)
        self.send_button.config(state=tk.NORMAL)
        self.status_label.config(text="Ready")
        self._save_conversation()

    def save_last_response(self):
        """Save the last assistant response to file"""
        history = self.assistant.get_history()
        if not history:
            messagebox.showinfo("No History", "No responses to save yet.")
            return

        # Find last assistant message
        last_response = None
        last_query = None
        for i in range(len(history) - 1, -1, -1):
            if history[i]["role"] == "assistant" and last_response is None:
                last_response = history[i]["content"]
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
            "response": last_response
        })

        # Save to file
        with open(self.saved_responses_file, 'w') as f:
            json.dump(saved, f, indent=2)

        messagebox.showinfo("Saved", "Response saved successfully!")

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
        view_window.geometry("700x500")

        # Create text widget
        text_widget = scrolledtext.ScrolledText(view_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add saved responses
        for i, item in enumerate(saved, 1):
            timestamp = datetime.fromisoformat(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            text_widget.insert(tk.END, f"═══ Saved Response #{i} ═══\n", "header")
            text_widget.insert(tk.END, f"Time: {timestamp}\n\n")
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

    def _save_conversation(self):
        """Save conversation to file"""
        history_file = Path.home() / ".ollama_assistant_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.assistant.get_history(), f, indent=2)
        except Exception as e:
            print(f"Could not save conversation: {e}")

    def _load_conversation(self):
        """Load conversation from file"""
        history_file = Path.home() / ".ollama_assistant_history.json"
        if not history_file.exists():
            return

        try:
            with open(history_file, 'r') as f:
                history = json.load(f)

            self.assistant.conversation_history = history

            # Display in UI
            for msg in history:
                self._append_to_history(msg["role"], msg["content"])
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
    """System tray application"""

    def __init__(self):
        self.assistant = OllamaAssistant()
        self.saved_responses_file = Path.home() / ".ollama_assistant_saved.json"
        self.window = AssistantWindow(self.assistant, self.saved_responses_file)
        self.icon = None
        self.hotkey_registered = False

    def create_image(self):
        """Create system tray icon"""
        # Create a simple icon
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='#2196F3')
        dc = ImageDraw.Draw(image)

        # Draw "AI" text
        dc.text((10, 20), "AI", fill='white')

        return image

    def setup_hotkey(self):
        """Setup global hotkey"""
        try:
            # Register Ctrl+Shift+A
            keyboard.add_hotkey('ctrl+shift+a', self.toggle_window)
            self.hotkey_registered = True
            print("Hotkey registered: Ctrl+Shift+A")
        except Exception as e:
            print(f"Could not register hotkey: {e}")

    def toggle_window(self):
        """Toggle window visibility"""
        if not self.window.window:
            # Create window in separate thread
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
        # Setup hotkey
        self.setup_hotkey()

        # Create tray icon
        menu = (
            item('Show/Hide (Ctrl+Shift+A)', self.show_window, default=True),
            item('Quit', self.quit_app)
        )

        self.icon = pystray.Icon(
            "ollama_assistant",
            self.create_image(),
            "Ollama Assistant",
            menu
        )

        print("Ollama Assistant started!")
        print("Press Ctrl+Shift+A to show/hide the window")
        print("Right-click the system tray icon for options")

        # Run in tray
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

    # Check if ministral model is available
    try:
        models = ollama.list()
        model_names = [m['name'] for m in models.get('models', [])]
        if not any('ministral' in name.lower() for name in model_names):
            print("Warning: Ministral model not found.")
            print("Run: ollama pull ministral:3b")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
    except Exception as e:
        print(f"Warning: Could not check models: {e}")

    app = TrayApp()
    app.run()


if __name__ == "__main__":
    main()

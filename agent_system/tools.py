"""
Tool implementations for the multi-agent system
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import mimetypes

# Optional imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class ToolRegistry:
    """Registry of available tools for agents"""

    def __init__(self):
        self.tools = {
            # File operations
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_directory": self.list_directory,
            "create_directory": self.create_directory,
            "delete_file": self.delete_file,

            # Document operations
            "analyze_document": self.analyze_document,
            "extract_text": self.extract_text,

            # Web operations
            "web_search": self.web_search,
            "fetch_url": self.fetch_url,

            # Calendar operations
            "create_event": self.create_event,
            "list_events": self.list_events,
            "delete_event": self.delete_event,

            # Code execution
            "execute_code": self.execute_code,
        }

        self.google_calendar_service = None
        self._workspace_dir = Path.home() / "OllamaAssistant"
        self._workspace_dir.mkdir(exist_ok=True)

    def get_tool(self, tool_name):
        """Get a tool by name"""
        return self.tools.get(tool_name)

    def has_tool(self, tool_name):
        """Check if a tool exists"""
        return tool_name in self.tools

    # ===== FILE OPERATIONS =====

    def read_file(self, file_path):
        """Read content from a file"""
        try:
            # Resolve path relative to workspace if not absolute
            if not os.path.isabs(file_path):
                file_path = self._workspace_dir / file_path

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "path": str(file_path),
                "size": len(content)
            }
        except FileNotFoundError:
            return {"success": False, "error": f"File not found: {file_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, file_path, content, append=False):
        """Write content to a file"""
        try:
            # Resolve path relative to workspace if not absolute
            if not os.path.isabs(file_path):
                file_path = self._workspace_dir / file_path

            # Create parent directories if needed
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "path": str(file_path),
                "bytes_written": len(content),
                "mode": "appended" if append else "written"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, dir_path=None):
        """List contents of a directory"""
        try:
            if dir_path is None:
                dir_path = self._workspace_dir
            elif not os.path.isabs(dir_path):
                dir_path = self._workspace_dir / dir_path

            items = []
            for item in os.listdir(dir_path):
                item_path = Path(dir_path) / item
                items.append({
                    "name": item,
                    "type": "directory" if item_path.is_dir() else "file",
                    "size": item_path.stat().st_size if item_path.is_file() else None
                })

            return {
                "success": True,
                "path": str(dir_path),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_directory(self, dir_path):
        """Create a directory"""
        try:
            if not os.path.isabs(dir_path):
                dir_path = self._workspace_dir / dir_path

            Path(dir_path).mkdir(parents=True, exist_ok=True)

            return {
                "success": True,
                "path": str(dir_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, file_path):
        """Delete a file"""
        try:
            if not os.path.isabs(file_path):
                file_path = self._workspace_dir / file_path

            if os.path.isfile(file_path):
                os.remove(file_path)
                return {"success": True, "path": str(file_path)}
            else:
                return {"success": False, "error": "Not a file or doesn't exist"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== DOCUMENT OPERATIONS =====

    def extract_text(self, file_path):
        """Extract text from various document formats"""
        try:
            if not os.path.isabs(file_path):
                file_path = self._workspace_dir / file_path

            file_path = Path(file_path)
            ext = file_path.suffix.lower()

            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

            elif ext == '.pdf':
                if not PDF_AVAILABLE:
                    return {"success": False, "error": "PyPDF2 not installed"}

                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"

            elif ext in ['.docx', '.doc']:
                if not DOCX_AVAILABLE:
                    return {"success": False, "error": "python-docx not installed"}

                doc = DocxDocument(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

            else:
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()

            return {
                "success": True,
                "text": text,
                "path": str(file_path),
                "length": len(text),
                "format": ext
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_document(self, file_path):
        """Analyze a document and return metadata + content"""
        try:
            if not os.path.isabs(file_path):
                file_path = self._workspace_dir / file_path

            file_path = Path(file_path)

            # Extract text
            extraction = self.extract_text(str(file_path))
            if not extraction["success"]:
                return extraction

            # Get file stats
            stats = file_path.stat()

            return {
                "success": True,
                "path": str(file_path),
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "format": file_path.suffix,
                "text": extraction["text"],
                "word_count": len(extraction["text"].split()),
                "line_count": len(extraction["text"].split('\n'))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== WEB OPERATIONS =====

    def web_search(self, query, num_results=5):
        """Search the web using DuckDuckGo"""
        try:
            # Using DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            results = []

            # Abstract
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", ""),
                    "snippet": data.get("Abstract", ""),
                    "url": data.get("AbstractURL", "")
                })

            # Related topics
            for topic in data.get("RelatedTopics", [])[:num_results-1]:
                if "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "snippet": topic.get("Text", ""),
                        "url": topic.get("FirstURL", "")
                    })

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fetch_url(self, url):
        """Fetch content from a URL"""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            return {
                "success": True,
                "url": url,
                "content": response.text,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', '')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== CALENDAR OPERATIONS =====

    def _get_calendar_service(self):
        """Get or create Google Calendar service"""
        if not GOOGLE_AVAILABLE:
            return None

        if self.google_calendar_service:
            return self.google_calendar_service

        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        token_file = Path.home() / '.ollama_calendar_token.pickle'
        credentials_file = Path.home() / '.ollama_calendar_credentials.json'

        # Load existing credentials
        if token_file.exists():
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_file.exists():
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.google_calendar_service = build('calendar', 'v3', credentials=creds)
        return self.google_calendar_service

    def create_event(self, summary, start_time, end_time=None, description=""):
        """Create a Google Calendar event"""
        try:
            service = self._get_calendar_service()
            if not service:
                return {"success": False, "error": "Google Calendar not configured"}

            # Parse times if strings
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if end_time is None:
                end_time = start_time + timedelta(hours=1)
            elif isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            created_event = service.events().insert(calendarId='primary', body=event).execute()

            return {
                "success": True,
                "event_id": created_event['id'],
                "summary": summary,
                "start": start_time.isoformat(),
                "link": created_event.get('htmlLink', '')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_events(self, max_results=10, time_min=None):
        """List upcoming Google Calendar events"""
        try:
            service = self._get_calendar_service()
            if not service:
                return {"success": False, "error": "Google Calendar not configured"}

            if time_min is None:
                time_min = datetime.utcnow().isoformat() + 'Z'

            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            event_list = []
            for event in events:
                event_list.append({
                    "id": event['id'],
                    "summary": event.get('summary', 'No title'),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "description": event.get('description', '')
                })

            return {
                "success": True,
                "events": event_list,
                "count": len(event_list)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_event(self, event_id):
        """Delete a Google Calendar event"""
        try:
            service = self._get_calendar_service()
            if not service:
                return {"success": False, "error": "Google Calendar not configured"}

            service.events().delete(calendarId='primary', eventId=event_id).execute()

            return {
                "success": True,
                "event_id": event_id,
                "message": "Event deleted"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== CODE EXECUTION =====

    def execute_code(self, code, language="python"):
        """Execute code safely (Python only for now)"""
        try:
            if language != "python":
                return {"success": False, "error": f"Language {language} not supported"}

            # Create a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Execute with timeout
                result = subprocess.run(
                    ['python3', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                return {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            finally:
                # Clean up
                os.unlink(temp_file)

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Code execution timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

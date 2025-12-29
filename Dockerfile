FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    x11-apps \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ollama_multi_agent_tray.py .
COPY config.yaml .
COPY setup_google_calendar.py .
COPY agent_system/ ./agent_system/

# Create directories for persistent data
RUN mkdir -p /root/OllamaAssistant

# Environment variables
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1

# Note: This requires X11 forwarding to work with GUI
# For headless operation, consider creating a separate API-only version

CMD ["python3", "ollama_multi_agent_tray.py"]

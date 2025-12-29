#!/bin/bash
# Background runner for Ollama Multi-Agent Assistant
# This script runs the assistant in the background without keeping terminal open

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_SCRIPT="$SCRIPT_DIR/ollama_multi_agent_tray.py"
PID_FILE="$HOME/.ollama_assistant.pid"
LOG_FILE="$HOME/.ollama_assistant.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "Ollama Assistant is already running (PID: $PID)"
                exit 1
            fi
        fi

        echo "Starting Ollama Multi-Agent Assistant..."

        # Start in background
        nohup python3 "$APP_SCRIPT" > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"

        echo "Started with PID: $(cat $PID_FILE)"
        echo "Log file: $LOG_FILE"
        echo "Press Ctrl+Shift+A to access the assistant"
        ;;

    stop)
        if [ ! -f "$PID_FILE" ]; then
            echo "PID file not found. Is the assistant running?"
            exit 1
        fi

        PID=$(cat "$PID_FILE")
        echo "Stopping Ollama Assistant (PID: $PID)..."

        kill $PID 2>/dev/null

        # Wait for process to stop
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                break
            fi
            sleep 0.5
        done

        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "Force killing..."
            kill -9 $PID 2>/dev/null
        fi

        rm -f "$PID_FILE"
        echo "Stopped"
        ;;

    restart)
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        if [ ! -f "$PID_FILE" ]; then
            echo "Ollama Assistant is not running"
            exit 1
        fi

        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Ollama Assistant is running (PID: $PID)"
            echo "Log file: $LOG_FILE"
        else
            echo "PID file exists but process is not running"
            rm -f "$PID_FILE"
            exit 1
        fi
        ;;

    logs)
        if [ ! -f "$LOG_FILE" ]; then
            echo "Log file not found: $LOG_FILE"
            exit 1
        fi

        tail -f "$LOG_FILE"
        ;;

    *)
        echo "Ollama Multi-Agent Assistant - Background Runner"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the assistant in background"
        echo "  stop    - Stop the assistant"
        echo "  restart - Restart the assistant"
        echo "  status  - Check if assistant is running"
        echo "  logs    - View log output (Ctrl+C to exit)"
        echo ""
        echo "After starting, press Ctrl+Shift+A to access the interface"
        exit 1
        ;;
esac

exit 0

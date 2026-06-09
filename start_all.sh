#!/usr/bin/env bash
# start_all.sh — launch all services
#
# Usage:
#   ./start_all.sh              — start all services, logs to terminal
#   ./start_all.sh --cli        — start all services + open CLI
#   ./start_all.sh --log        — start all services, logs to /tmp/api-registry-*.log
#   ./start_all.sh --cli --log  — both

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/venv/bin/python3"

if [ ! -f "$PYTHON" ]; then
    echo "ERROR: venv not found — run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

OPEN_CLI=false
LOG_TO_FILE=false
for arg in "$@"; do
    case $arg in
        --cli) OPEN_CLI=true ;;
        --log) LOG_TO_FILE=true ;;
    esac
done

# ── Kill any processes already on these ports ─────────────────────────────────
PORTS=(9000 8001 8002 8003 8004 8500)
echo "=== Stopping any existing services ==="
for port in "${PORTS[@]}"; do
    pid=$(lsof -ti ":$port" 2>/dev/null)
    if [ -n "$pid" ]; then
        kill -9 $pid 2>/dev/null && echo "  Killed PID $pid on :$port"
    fi
done
sleep 1

# ── Helper to start a service ─────────────────────────────────────────────────
start_svc() {
    local name=$1; local module=$2; local port=$3
    if [ "$LOG_TO_FILE" = true ]; then
        local logfile="/tmp/api-registry-${name}.log"
        "$PYTHON" -m uvicorn "$module" --port "$port" --log-level warning > "$logfile" 2>&1 &
        echo "  $name :$port  (log → $logfile)"
    else
        "$PYTHON" -m uvicorn "$module" --port "$port" --log-level warning &
        echo "  $name :$port"
    fi
}

echo ""
echo "=== Starting API Registry services ==="
start_svc "registry"      "registry.main:app"                  9000; sleep 2
start_svc "lims"          "mock_apis.lims_api:app"             8001; sleep 1
start_svc "erp"           "mock_apis.erp_api:app"              8002; sleep 1
start_svc "genomics"      "mock_apis.genomics_api:app"         8003; sleep 1
start_svc "manufacturing" "mock_apis.manufacturing_api:app"    8004; sleep 1
start_svc "lab_app"       "lab_app.main:app"                   8500; sleep 2

echo ""
echo "All services running."
echo "  Chat UI   → http://localhost:9000/chat-ui"
echo "  Register  → http://localhost:9000/registry-ui"
echo "  Browse    → http://localhost:9000/browse-ui"
echo ""

if [ "$OPEN_CLI" = true ]; then
    echo "Starting CLI... (Ctrl+C to quit)"
    echo ""
    "$PYTHON" ui/cli.py
else
    echo "Tip: run  ./start_all.sh --cli  to also open the CLI."
    echo "     run  ./start_all.sh --log  to redirect logs to /tmp/api-registry-*.log"
    echo ""
    echo "Press Ctrl+C to stop all services."
    wait
fi

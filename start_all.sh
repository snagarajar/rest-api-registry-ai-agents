#!/usr/bin/env bash
# start_all.sh — launch all services and open the CLI agent
set -e

echo "=== Starting API Registry services ==="

# Start registry
python -m uvicorn registry.main:app --port 9000 --log-level warning &
REGISTRY_PID=$!
echo "Registry started (PID $REGISTRY_PID)"
sleep 2

# Start mock APIs
python -m uvicorn mock_apis.lims_api:app --port 8001 --log-level warning &
sleep 1
python -m uvicorn mock_apis.erp_api:app --port 8002 --log-level warning &
sleep 1
python -m uvicorn mock_apis.genomics_api:app --port 8003 --log-level warning &
sleep 1
python -m uvicorn mock_apis.manufacturing_api:app --port 8004 --log-level warning &
sleep 2

echo ""
echo "All services running."
echo "  Registry  → http://localhost:9000"
echo "  LIMS      → http://localhost:8001"
echo "  ERP       → http://localhost:8002"
echo "  Genomics  → http://localhost:8003"
echo "  Mfg       → http://localhost:8004"
echo ""
echo "Web UI → http://localhost:9000/chat-ui"
echo "Reg UI → http://localhost:9000/register-ui"
echo ""
echo "Starting CLI... (Ctrl+C to quit)"
echo ""

python ui/cli.py

# Cleanup on exit
kill $REGISTRY_PID 2>/dev/null || true
wait

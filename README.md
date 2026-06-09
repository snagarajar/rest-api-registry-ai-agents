# REST API Registry for AI Agents 🤖

> **Illumina AI Hackathon** — Demonstrate AI agent autonomy through API discovery and invocation

## What This Is

A central registry where teams **self-register** their REST APIs, and a Claude-powered AI agent **autonomously discovers and invokes** them to answer natural-language questions — no manual coordination needed.

```
User: "Can we fulfill work order WO-1234?"
  → Agent queries registry → finds LIMS + ERP APIs
  → Calls both endpoints → synthesizes answer
Agent: "Yes. WO-1234 needs 500 units; 800 are in inventory."
```

## Quick Start

```bash
# 1. Set up environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure AWS credentials (us-west-2, Bedrock access required)
cp .env.example .env
aws configure

# 3. Test Bedrock connectivity
python test_bedrock.py

# 4. Launch everything + CLI
chmod +x start_all.sh && ./start_all.sh
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Registry | 9000 | Central API metadata store |
| LIMS API | 8001 | Work orders & bead pools |
| ERP API  | 8002 | Inventory & procurement |
| Genomics | 8003 | Quality checks & assays |
| Manufacturing | 8004 | Instruments & fab capacity |

## Interfaces

| Interface | How to open |
|-----------|-------------|
| CLI Agent | `python ui/cli.py` |
| Web Chat  | http://localhost:9000/chat-ui |
| Register API | http://localhost:9000/register-ui |
| API Docs | http://localhost:9000/docs |

## Sample Questions

```
Can we fulfill work order WO-1234?
What's the inventory level for BeadChip?
What's the quality grade for BeadChip?
Is instrument Watson available?
What's the capacity at fab-sd?
```

## Project Structure

```
api-registry-hackathon/
├── registry/          # FastAPI registry service (port 9000)
├── mock_apis/         # 4 simulated team APIs (ports 8001–8004)
├── orchestrator/      # Claude agent via AWS Bedrock
├── ui/                # CLI + web chat + registration form
├── tests/             # Pytest tests for registry
├── test_bedrock.py    # Verify AWS connectivity
└── start_all.sh       # One-shot launcher
```

## Run Tests

```bash
pytest tests/ -v
```

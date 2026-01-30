#!/bin/bash
# Start all agent servers

echo "Starting all support agents..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start agents in background
echo "Starting Ingestion Agent (port 10001)..."
python -m agents.ingestion_agent.__main__ &
INGESTION_PID=$!

echo "Starting Planner Agent (port 10002)..."
python -m agents.planner_agent.__main__ &
PLANNER_PID=$!

echo "Starting Intent Agent (port 10003)..."
python -m agents.intent_agent.__main__ &
INTENT_PID=$!

echo "Starting RAG Agent (port 10004)..."
python -m agents.rag_agent.__main__ &
RAG_PID=$!

echo "Starting Memory Agent (port 10005)..."
python -m agents.memory_agent.__main__ &
MEMORY_PID=$!

echo "Starting Reasoning Agent (port 10006)..."
python -m agents.reasoning_agent.__main__ &
REASONING_PID=$!

echo "Starting Response Agent (port 10007)..."
python -m agents.response_agent.__main__ &
RESPONSE_PID=$!

echo "Starting Guardrails Agent (port 10008)..."
python -m agents.guardrails_agent.__main__ &
GUARDRAILS_PID=$!

echo "Starting Host Agent (port 8083)..."
python -m agents.host_agent.__main__ &
HOST_PID=$!

echo ""
echo "All agents started!"
echo "PIDs:"
echo "  Ingestion: $INGESTION_PID"
echo "  Planner: $PLANNER_PID"
echo "  Intent: $INTENT_PID"
echo "  RAG: $RAG_PID"
echo "  Memory: $MEMORY_PID"
echo "  Reasoning: $REASONING_PID"
echo "  Response: $RESPONSE_PID"
echo "  Guardrails: $GUARDRAILS_PID"
echo "  Host: $HOST_PID"
echo ""
echo "To stop all agents, run: pkill -f '__main__'"

# Wait for all processes
wait

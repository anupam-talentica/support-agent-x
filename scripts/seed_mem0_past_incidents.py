#!/usr/bin/env python3
"""Seed mem0 (Memory Agent's store) from past-resolved-incidents.json.

This enables Test Case 3: when RAG cannot satisfy, Memory Agent can return
a similar past incident (e.g. INC-2025-001 duplicate charge) so the response
is driven by Memory resolution.

Run from support_agents root (with .env loaded, ChromaDB and OPENAI_API_KEY available):
    python scripts/seed_mem0_past_incidents.py

For Docker: run once with ChromaDB and OpenAI reachable (e.g. from host with
CHROMA_HOST=localhost, or in a one-off container with same env as memory_agent).
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Load .env so OPENAI_API_KEY, CHROMA_HOST, etc. are set
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, '.env'))
except Exception:
    pass


def main() -> None:
    json_path = os.path.join(ROOT, 'training-docs', 'memory-agent-scenarios', 'past-resolved-incidents.json')
    if not os.path.isfile(json_path):
        print(f'ERROR: JSON not found: {json_path}')
        sys.exit(1)

    if not os.getenv('OPENAI_API_KEY'):
        print('ERROR: OPENAI_API_KEY not set. Set it in .env or environment.')
        sys.exit(1)

    with open(json_path, 'r') as f:
        incidents = json.load(f)

    from agents.memory_agent.memory_agent import Mem0MemoryAgent
    agent = Mem0MemoryAgent()

    # Seed with user_id="all_users" so invoke_rag_and_memory_parallel(ticket_query, "all_users") finds them
    user_id = "all_users"
    for inc in incidents:
        incident_id = inc.get('incident_id', 'unknown')
        query_text = inc.get('query_text', '')
        resolution = inc.get('resolution', '')
        message = (
            f"Past incident {incident_id}: {query_text} "
            f"Resolution: {resolution}"
        )
        metadata = {
            "ticket_id": incident_id,
            "type": "past_resolved_incident",
            "outcome": inc.get('outcome', 'resolved'),
        }
        try:
            result = agent.add_memory(message, user_id=user_id, metadata=metadata)
            if "error" in result:
                print(f'Skip {incident_id}: {result["error"]}')
            else:
                print(f'Added to mem0: {incident_id}')
        except Exception as e:
            print(f'Skip {incident_id}: {e}')

    print(f'Seeded mem0 with {len(incidents)} past-resolved incidents. Test Case 3 (Memory solves) can now return INC-2025-001 for duplicate-charge queries.')


if __name__ == '__main__':
    main()

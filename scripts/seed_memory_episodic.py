#!/usr/bin/env python3
"""Seed Episodic Memory from training-docs/memory-agent-scenarios/past-resolved-incidents.json.

Run from support_agents root:
    python scripts/seed_memory_episodic.py

Requires: MEMORY_DB_PATH (default ./data/memory.db), and memory DB initialized.
"""

import json
import os
import sys

# Add support_agents root to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents.memory_agent.memory_db import get_memory_db
from agents.memory_agent.memory_schema import EpisodicMemory


def main() -> None:
    json_path = os.path.join(ROOT, 'training-docs', 'memory-agent-scenarios', 'past-resolved-incidents.json')
    if not os.path.isfile(json_path):
        print(f'ERROR: JSON not found: {json_path}')
        sys.exit(1)

    with open(json_path, 'r') as f:
        incidents = json.load(f)

    with get_memory_db() as db:
        for inc in incidents:
            existing = db.query(EpisodicMemory).filter(EpisodicMemory.incident_id == inc['incident_id']).first()
            if existing:
                print(f'Skip (exists): {inc["incident_id"]}')
                continue
            record = EpisodicMemory(
                incident_id=inc['incident_id'],
                query_text=inc['query_text'],
                resolution=inc.get('resolution'),
                outcome=inc.get('outcome', 'resolved'),
                tags=inc.get('tags'),
                user_id=inc.get('user_id'),
                metadata=inc.get('metadata'),
            )
            db.add(record)
            print(f'Added: {inc["incident_id"]}')

    print(f'Seeded {len(incidents)} episodic memory entries.')


if __name__ == '__main__':
    main()

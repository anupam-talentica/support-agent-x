#!/usr/bin/env python3
"""Initialize Memory Agent's database with schema."""

import os
import sys

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.memory_agent.memory_db import drop_memory_database, init_memory_database


def main() -> None:
    """Main initialization function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Memory Agent database')
    parser.add_argument(
        '--drop', action='store_true', help='Drop all tables before creating (WARNING: deletes all data)'
    )
    args = parser.parse_args()
    
    if args.drop:
        print('Dropping existing memory database...')
        drop_memory_database()
    
    print('Initializing memory database schema...')
    init_memory_database()
    
    print('Memory database initialization complete!')


if __name__ == '__main__':
    main()

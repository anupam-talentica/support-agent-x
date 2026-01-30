#!/usr/bin/env python3
"""Initialize application database with schema and optional seed data."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_database, get_db
from database.models import User
from database.services import UserService


def seed_test_data() -> None:
    """Seed database with test data."""
    print('Seeding test data...')
    
    with get_db() as db:
        # Create test users
        test_users = [
            {
                'user_id': 'test_user_001',
                'email': 'analyst@example.com',
                'role': 'support_analyst',
            },
            {
                'user_id': 'test_user_002',
                'email': 'customer@example.com',
                'role': 'customer',
            },
            {
                'user_id': 'test_user_003',
                'email': 'admin@example.com',
                'role': 'admin',
            },
        ]
        
        for user_data in test_users:
            existing = UserService.get_user(db, user_data['user_id'])
            if not existing:
                UserService.create_user(db, **user_data)
                print(f"  Created user: {user_data['email']}")
            else:
                print(f"  User already exists: {user_data['email']}")
    
    print('Test data seeded successfully!')


def main() -> None:
    """Main initialization function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize application database')
    parser.add_argument(
        '--seed', action='store_true', help='Seed database with test data'
    )
    parser.add_argument(
        '--drop', action='store_true', help='Drop all tables before creating (WARNING: deletes all data)'
    )
    args = parser.parse_args()
    
    if args.drop:
        from database.connection import drop_database
        print('Dropping existing database...')
        drop_database()
    
    print('Initializing database schema...')
    init_database()
    
    if args.seed:
        seed_test_data()
    
    print('Database initialization complete!')


if __name__ == '__main__':
    main()

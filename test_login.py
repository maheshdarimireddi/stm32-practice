"""
Test script for login application
Pre-populates database with test users
"""

import sqlite3
import hashlib


def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_test_users():
    """Create test users in database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    test_users = [
        ('demo', 'demo@example.com', 'Demo123'),
        ('testuser', 'test@example.com', 'Test123'),
        ('admin', 'admin@example.com', 'Admin123'),
    ]
    
    try:
        for username, email, password in test_users:
            hashed = hash_password(password)
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed)
            )
            print(f"✓ Created user: {username}")
        
        conn.commit()
        print("\n✓ Test users created successfully!")
        print("\nTest Accounts:")
        print("-" * 40)
        for username, email, password in test_users:
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Email: {email}")
            print("-" * 40)
    
    except sqlite3.IntegrityError as e:
        print(f"Note: {str(e)}")
        print("Test users may already exist in database")
    
    finally:
        conn.close()


def view_all_users():
    """View all users in database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, email, created_at FROM users')
    users = cursor.fetchall()
    
    print("\nAll Users in Database:")
    print("-" * 60)
    for username, email, created_at in users:
        print(f"Username: {username:15} | Email: {email:25} | Created: {created_at}")
    print("-" * 60)
    
    conn.close()


def reset_database():
    """Reset database (delete users.db)"""
    import os
    if os.path.exists('users.db'):
        os.remove('users.db')
        print("✓ Database reset successfully")


if __name__ == "__main__":
    print("Login System - Test Script")
    print("=" * 40)
    
    choice = input("\nSelect option:\n1. Create test users\n2. View all users\n3. Reset database\n\nChoice (1-3): ").strip()
    
    if choice == '1':
        create_test_users()
    elif choice == '2':
        view_all_users()
    elif choice == '3':
        confirm = input("Are you sure? This will delete all users (y/n): ").strip().lower()
        if confirm == 'y':
            reset_database()
    else:
        print("Invalid choice")

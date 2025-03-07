import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash

def test_database_connection():
    """Test basic database connection and file existence"""
    print("\n===== TESTING DATABASE CONNECTION =====")
    
    # Check if database file exists
    db_path = 'nutrilogic.db'
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        print(f"✓ Database file exists at {os.path.abspath(db_path)}")
        print(f"✓ File size: {file_size} bytes")
    else:
        print(f"✗ Database file does not exist at {os.path.abspath(db_path)}")
        return False
    
    # Test connection
    try:
        conn = sqlite3.connect(db_path)
        print("✓ Successfully connected to database")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        return False

def check_schema():
    """Check database schema"""
    print("\n===== CHECKING DATABASE SCHEMA =====")
    
    try:
        conn = sqlite3.connect('nutrilogic.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables in database: {', '.join([t[0] for t in tables])}")
        
        # Check if users table exists
        if ('users',) in tables:
            print("✓ users table exists")
            
            # Check columns in users table
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("\nColumns in users table:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check for required columns
            required_columns = {
                'id': 'INTEGER', 
                'username': 'TEXT', 
                'email': 'TEXT',
                'password_hash': 'TEXT',
                'name': 'TEXT',
                'height': 'REAL',
                'weight': 'REAL',
                'pre_pregnancy_weight': 'REAL',
                'age': 'INTEGER',
                'trimester': 'INTEGER',
                'multiple_pregnancies': 'BOOLEAN'
            }
            
            existing_columns = {col[1]: col[2] for col in columns}
            missing_columns = []
            
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    missing_columns.append(col_name)
                elif not existing_columns[col_name].startswith(col_type):
                    print(f"✗ Column {col_name} has wrong type: {existing_columns[col_name]} (expected {col_type})")
            
            if missing_columns:
                print(f"✗ Missing required columns: {', '.join(missing_columns)}")
            else:
                print("✓ All required columns exist")
                
        else:
            print("✗ users table does not exist")
        
        conn.close()
    except Exception as e:
        print(f"✗ Error checking schema: {e}")

def test_insert_user():
    """Test inserting a user into the database"""
    print("\n===== TESTING USER INSERTION =====")
    
    # Generate a unique test user
    import random
    import string
    import datetime
    
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    test_user = {
        'username': f'testuser_{random_suffix}',
        'email': f'test_{random_suffix}@example.com',
        'password': 'Test1234!',
        'name': 'Test User',
        'height': 170.0,
        'weight': 65.0,
        'pre_pregnancy_weight': 60.0,
        'age': 30,
        'trimester': 2,
        'multiple_pregnancies': False,
        'medical_conditions': 'none',
        'diet_type': 'vegetarian',
        'allergies': 'none'
    }
    
    conn = None
    try:
        # Connect to database
        conn = sqlite3.connect('nutrilogic.db')
        cursor = conn.cursor()
        
        # Insert test user
        cursor.execute('''
            INSERT INTO users (
                username, email, password_hash, name, height, weight,
                pre_pregnancy_weight, age, trimester, multiple_pregnancies,
                medical_conditions, diet_type, allergies
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_user['username'],
            test_user['email'],
            generate_password_hash(test_user['password']),
            test_user['name'],
            test_user['height'],
            test_user['weight'],
            test_user['pre_pregnancy_weight'],
            test_user['age'],
            test_user['trimester'],
            test_user['multiple_pregnancies'],
            test_user['medical_conditions'],
            test_user['diet_type'],
            test_user['allergies']
        ))
        
        # Commit changes
        conn.commit()
        
        # Verify user was inserted
        cursor.execute("SELECT id, username, email FROM users WHERE username = ?", (test_user['username'],))
        user = cursor.fetchone()
        
        if user:
            print(f"✓ Successfully inserted test user")
            print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        else:
            print("✗ Failed to verify inserted user")
        
    except Exception as e:
        print(f"✗ Error inserting test user: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def check_permissions():
    """Check file permissions"""
    print("\n===== CHECKING FILE PERMISSIONS =====")
    
    db_path = 'nutrilogic.db'
    
    if os.path.exists(db_path):
        # Check if file is readable
        if os.access(db_path, os.R_OK):
            print(f"✓ Database file is readable")
        else:
            print(f"✗ Database file is not readable")
        
        # Check if file is writable
        if os.access(db_path, os.W_OK):
            print(f"✓ Database file is writable")
        else:
            print(f"✗ Database file is not writable")
            
        # Try write test
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA user_version = user_version + 1")
            conn.commit()
            
            cursor.execute("PRAGMA user_version")
            version = cursor.fetchone()[0]
            
            print(f"✓ Successfully wrote to database (user_version = {version})")
            conn.close()
        except Exception as e:
            print(f"✗ Failed to write to database: {e}")
    else:
        print(f"✗ Database file does not exist at {os.path.abspath(db_path)}")

def main():
    """Run all database troubleshooting tests"""
    print("=" * 50)
    print("DATABASE TROUBLESHOOTING")
    print("=" * 50)
    
    # Run tests
    if not test_database_connection():
        print("\n✗ Database connection failed. Cannot continue tests.")
        return
    
    check_schema()
    check_permissions()
    test_insert_user()
    
    print("\n" + "=" * 50)
    print("TROUBLESHOOTING COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main() 
import sqlite3

def check_database():
    conn = sqlite3.connect('nutrilogic.db')
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Check users table if it exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if cursor.fetchone():
        # Get column information
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nColumns in users table:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Get user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\nNumber of users: {user_count}")
        
        # List all users
        if user_count > 0:
            cursor.execute("SELECT id, username, email, name FROM users")
            users = cursor.fetchall()
            print("\nUser list:")
            for user in users:
                print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Name: {user[3]}")
                
            # Get one full user record as an example
            if user_count > 0:
                cursor.execute("SELECT * FROM users LIMIT 1")
                user_data = cursor.fetchone()
                cursor.execute("PRAGMA table_info(users)")
                column_names = [column[1] for column in cursor.fetchall()]
                
                print("\nSample user data:")
                for i, col in enumerate(column_names):
                    if i < len(user_data):
                        print(f"{col}: {user_data[i]}")
    
    conn.close()

if __name__ == "__main__":
    check_database() 
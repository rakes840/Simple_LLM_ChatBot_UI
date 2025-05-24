import sqlite3

def add_profile_updated_at_column(db_path='test.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the column already exists
    cursor.execute("PRAGMA table_info(users);")
    columns = [info[1] for info in cursor.fetchall()]
    if 'profile_updated_at' in columns:
        print("Column 'profile_updated_at' already exists.")
    else:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_updated_at DATETIME;")
            conn.commit()
            print("Column 'profile_updated_at' added successfully.")
        except sqlite3.OperationalError as e:
            print(f"Error adding column: {e}")

    conn.close()

if __name__ == "__main__":
    add_profile_updated_at_column()

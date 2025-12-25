import sqlite3
import os

def init_database(db_path='db/trends.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    schema_path = os.path.join(os.path.dirname(db_path), 'schema.sql')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    init_database()

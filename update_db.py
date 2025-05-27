import sqlite3

def add_approval_status():
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/mydb.db')
        cursor = conn.cursor()
        
        # Add approval_status column to venue table
        cursor.execute('''ALTER TABLE venue ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending';''')
        
        # Add approval_status column to other service provider tables if they don't have it
        cursor.execute('''ALTER TABLE makeupartist ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending';''')
        cursor.execute('''ALTER TABLE hairdresser ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending';''')
        cursor.execute('''ALTER TABLE weddingplanner ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending';''')
        
        # Commit the changes
        conn.commit()
        print("Successfully added approval_status column to all service provider tables")
        
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("Column already exists:", e)
        else:
            print("Error:", e)
    finally:
        conn.close()

if __name__ == '__main__':
    add_approval_status() 
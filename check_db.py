import sqlite3

conn = sqlite3.connect('ged.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("Tables:", tables)

for (table_name,) in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
    print(f"  - {table_name}: {count} ligne(s)")

conn.close()
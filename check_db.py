import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%user%'")
print(c.fetchall())
conn.close()
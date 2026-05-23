import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
try:
    c.execute('ALTER TABLE users ADD COLUMN reminder_time TEXT')
    print('reminder_time OK')
except:
    print('reminder_time allaqachon bor')
try:
    c.execute('ALTER TABLE users ADD COLUMN notes TEXT')
    print('notes OK')
except:
    print('notes allaqachon bor')
conn.commit()
conn.close()
print('Tayyor!')
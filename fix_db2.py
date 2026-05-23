import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

cols = [
    'ALTER TABLE users ADD COLUMN streak_days INTEGER DEFAULT 0',
    'ALTER TABLE users ADD COLUMN last_active_date TEXT',
    'ALTER TABLE users ADD COLUMN weekly_xp INTEGER DEFAULT 0',
    'ALTER TABLE users ADD COLUMN referred_by_id INTEGER',
]

for sql in cols:
    try:
        c.execute(sql)
        print('OK:', sql.split('COLUMN')[1].split()[0])
    except Exception as e:
        print('Skip:', e)

conn.commit()
conn.close()
print('Tayyor!')
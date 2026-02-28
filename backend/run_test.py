import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from db import init_db, get_db

print('cwd', os.getcwd())
init_db()
conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM job")
print('jobs count', cursor.fetchone()[0])
cursor.execute("SELECT * FROM job LIMIT 3")
for row in cursor.fetchall():
    print(dict(row))
conn.close()

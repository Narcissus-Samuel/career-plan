from db import get_db

conn = get_db()
cursor = conn.cursor()
cursor.execute("DELETE FROM job_relations")
conn.commit()
conn.close()
print("✅ job_relations 表已清空")
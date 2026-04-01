import sqlite3
import os

# 数据库文件路径（相对于脚本所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'career.db')

def main():
    if not os.path.exists(DB_PATH):
        print(f"错误：数据库文件不存在 {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 删除不合理的路径：实施工程师 -> 统计员
    print("1. 删除实施工程师 -> 统计员 的换岗路径...")
    delete_sql = """
        DELETE FROM job_relations
        WHERE from_job = '实施工程师'
          AND to_job = '统计员'
          AND relation_type = 'transition'
    """
    cursor.execute(delete_sql)
    rows_deleted = cursor.rowcount
    print(f"   已删除 {rows_deleted} 条记录")

    # 2. 更新售后客服 -> 统计员的描述
    print("2. 更新售后客服 -> 统计员的描述...")
    new_desc = "【售后客服】可换岗至【统计员】；需补充技能：电话沟通与客户服务、数据统计与报表编制、办公软件操作、、Excel数据处理；需提升软能力：细致严谨、协作能力、执行力；建议证书：人力资源管理师（四级/三级）、计算机等级考试证书（二级MS Office）"
    update_sql = """
        UPDATE job_relations
        SET description = ?
        WHERE from_job = '售后客服'
          AND to_job = '统计员'
          AND relation_type = 'transition'
    """
    cursor.execute(update_sql, (new_desc,))
    rows_updated = cursor.rowcount
    print(f"   已更新 {rows_updated} 条记录")

    # 3. 提交更改并关闭连接
    conn.commit()
    conn.close()

    print("操作完成。")

if __name__ == '__main__':
    main()
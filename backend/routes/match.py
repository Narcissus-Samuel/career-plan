# 匹配结果路由
# routes/match.py
from flask import Blueprint, request, jsonify
from db import get_db

match_bp = Blueprint('match', __name__, url_prefix='/api')

@match_bp.route('/match', methods=['GET'])
def get_match():
    """获取人岗匹配结果。从 match_history 表中读取指定学生的记录。"""
    try:
        student_id = request.args.get('studentId')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT job_name, match_score, details, created_at FROM match_history WHERE student_id = ? ORDER BY match_score DESC",
            (student_id,)
        )
        rows = cursor.fetchall()
        matches = [dict(row) for row in rows]
        conn.close()
        return jsonify({"studentId": student_id, "matches": matches})
    except Exception as e:
        # log the full traceback to console for debugging
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
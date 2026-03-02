from flask import Blueprint, request, jsonify
from services import llm_service
from db import get_db
from .auth import token_required

llm_bp = Blueprint('llm', __name__, url_prefix='/api/llm')


@llm_bp.route('/recommend', methods=['POST'])
@token_required
def recommend():
    data = request.json or {}
    student = data.get('student')
    top_n = int(data.get('top_n', 5))
    # load jobs from db
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM job')
    jobs = [dict(r) for r in cur.fetchall()]
    conn.close()
    recs = llm_service.intelligent_recommendation(student or {}, jobs, top_n)
    return jsonify({'results': recs})


@llm_bp.route('/generate_plan', methods=['POST'])
@token_required
def generate_plan():
    data = request.json or {}
    student = data.get('student')
    job_name = data.get('job_name')
    text = llm_service.generate_plan_suggestion(student or {}, job_name or '')
    return jsonify({'plan': text})


@llm_bp.route('/qa', methods=['POST'])
def qa():
    data = request.json or {}
    q = data.get('question', '')
    context = data.get('context', '')
    ans = llm_service.chat_qa(q, context)
    return jsonify({'answer': ans})

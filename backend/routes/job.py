from flask import Blueprint, request, jsonify
from db import get_db
import json
from services.llm_service import generate_dynamic_job_profile

job_bp = Blueprint('job', __name__, url_prefix='/api/jobs')

# ---------- 原有接口（全部保留）----------

@job_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有岗位大类"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, icon, description, skills, certificates, soft_abilities
        FROM job_categories
        ORDER BY id
    ''')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'id': row['id'],
            'name': row['name'],
            'icon': row['icon'],
            'description': row['description'],
            'skills': json.loads(row['skills']) if row['skills'] else [],
            'certificates': json.loads(row['certificates']) if row['certificates'] else [],
            'soft_abilities': json.loads(row['soft_abilities']) if row['soft_abilities'] else {}
        })
    conn.close()
    return jsonify(result)

@job_bp.route('/<int:job_id>', methods=['GET'])
def get_job_detail(job_id):
    """根据岗位ID返回完整详情"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rowid as id,
               job_name, location, salary_range, company, industry,
               company_size, company_type, job_code, job_description,
               updated_at, company_info, source_url
        FROM job
        WHERE rowid = ?
    ''', (job_id,))
    job = cursor.fetchone()
    conn.close()
    if not job:
        return jsonify({'error': '岗位不存在'}), 404
    return jsonify(dict(job))

@job_bp.route('/profile/<string:job_name>', methods=['GET'])
def get_job_profile_by_name(job_name):
    """通过岗位名称获取详情（兼容旧版）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rowid as id,
               job_name, location, salary_range, company, industry,
               company_size, company_type, job_code, job_description,
               updated_at, company_info, source_url, category_id
        FROM job
        WHERE job_name = ?
        LIMIT 1
    ''', (job_name,))
    job = cursor.fetchone()
    if not job:
        conn.close()
        return jsonify({'error': '岗位不存在'}), 404
    job_dict = dict(job)

    # 获取所属大类画像（可选）
    if job_dict.get('category_id'):
        cursor.execute('''
            SELECT name, skills, certificates, soft_abilities
            FROM job_categories
            WHERE id = ?
        ''', (job_dict['category_id'],))
        category = cursor.fetchone()
        if category:
            job_dict['category_profile'] = {
                'name': category['name'],
                'skills': json.loads(category['skills']) if category['skills'] else [],
                'certificates': json.loads(category['certificates']) if category['certificates'] else [],
                'soft_abilities': json.loads(category['soft_abilities']) if category['soft_abilities'] else {}
            }
        else:
            job_dict['category_profile'] = {}
    else:
        job_dict['category_profile'] = {}

    conn.close()
    return jsonify(job_dict)

@job_bp.route('/graph', methods=['GET'])
def get_job_graph():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT from_job, to_job, relation_type, description FROM job_relations')
    edges = cursor.fetchall()
    nodes_set = set()
    for e in edges:
        nodes_set.add(e['from_job'])
        nodes_set.add(e['to_job'])
    nodes = [{'id': n, 'label': n} for n in nodes_set]
    conn.close()
    return jsonify({'nodes': nodes, 'edges': [dict(e) for e in edges]})

@job_bp.route('/industries', methods=['GET'])
def get_industries():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT industry FROM job WHERE industry IS NOT NULL AND industry != "" ORDER BY industry')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([row['industry'] for row in rows])

@job_bp.route('/search', methods=['GET'])
def search_jobs():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    industry = request.args.get('industry', '', type=str)
    company_size = request.args.get('company_size', '', type=str)
    order = request.args.get('order', 'asc')

    if page < 1 or size < 1:
        return jsonify({'error': '分页参数无效'}), 400

    order_sql = 'ASC' if order.lower() == 'asc' else 'DESC'

    conn = get_db()
    cursor = conn.cursor()

    conditions = []
    params = []
    if keyword:
        conditions.append("(job_name LIKE ? OR company LIKE ?)")
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if industry:
        conditions.append("industry = ?")
        params.append(industry)
    if company_size:
        conditions.append("company_size = ?")
        params.append(company_size)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    count_sql = f"SELECT COUNT(*) as total FROM job {where_clause}"
    cursor.execute(count_sql, params)
    total = cursor.fetchone()['total']

    sql = f"""
        SELECT rowid as id,
               job_name, location, salary_range, company,
               industry, company_size, company_type
        FROM job {where_clause}
        ORDER BY rowid {order_sql}
        LIMIT ? OFFSET ?
    """
    offset = (page - 1) * size
    cursor.execute(sql, params + [size, offset])
    rows = cursor.fetchall()
    conn.close()

    items = [dict(row) for row in rows]
    return jsonify({'total': total, 'page': page, 'size': size, 'items': items})

@job_bp.route('/simple_search', methods=['GET'])
def simple_search():
    keyword = request.args.get('keyword', '', type=str)
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    offset = (page - 1) * size

    conn = get_db()
    cursor = conn.cursor()
    if keyword:
        cursor.execute('''
            SELECT rowid as id, job_name, company, salary_range, location
            FROM job
            WHERE job_name LIKE ? OR company LIKE ?
            ORDER BY rowid
            LIMIT ? OFFSET ?
        ''', (f'%{keyword}%', f'%{keyword}%', size, offset))
    else:
        cursor.execute('''
            SELECT rowid as id, job_name, company, salary_range, location
            FROM job
            ORDER BY rowid
            LIMIT ? OFFSET ?
        ''', (size, offset))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ========== 新增接口：获取岗位画像（按优先级） ==========

@job_bp.route('/<int:job_id>/profile', methods=['GET'])
def get_job_profile(job_id):
    """
    获取岗位画像，优先级：
    1. job_profile 表中是否有该岗位名称的单独画像
    2. 如果有分类（category_id），返回大类画像
    3. 否则动态生成并存入 job_profile 表
    """
    conn = get_db()
    cursor = conn.cursor()

    # 获取岗位基本信息
    cursor.execute('''
        SELECT rowid as id, job_name, job_description, category_id
        FROM job
        WHERE rowid = ?
    ''', (job_id,))
    job = cursor.fetchone()
    if not job:
        conn.close()
        return jsonify({'error': '岗位不存在'}), 404

    job_name = job['job_name']
    job_desc = job['job_description']
    category_id = job['category_id']

    # 1. 检查 job_profile 表中是否有该岗位的单独画像
    cursor.execute('''
        SELECT skills, certificates, soft_abilities
        FROM job_profile
        WHERE job_name = ?
    ''', (job_name,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify({
            'job_name': job_name,
            'skills': json.loads(existing['skills']) if existing['skills'] else [],
            'certificates': json.loads(existing['certificates']) if existing['certificates'] else [],
            'soft_abilities': json.loads(existing['soft_abilities']) if existing['soft_abilities'] else {},
            'source': 'job_profile'
        })

    # 2. 如果有分类，从 job_categories 获取大类画像
    if category_id:
        cursor.execute('''
            SELECT name, skills, certificates, soft_abilities
            FROM job_categories
            WHERE id = ?
        ''', (category_id,))
        cat = cursor.fetchone()
        if cat and cat['skills']:
            conn.close()
            return jsonify({
                'job_name': job_name,
                'skills': json.loads(cat['skills']),
                'certificates': json.loads(cat['certificates']) if cat['certificates'] else [],
                'soft_abilities': json.loads(cat['soft_abilities']) if cat['soft_abilities'] else {},
                'source': 'category',
                'category_name': cat['name']
            })

    # 3. 动态生成画像（长尾岗位）
    dynamic = generate_dynamic_job_profile(job_name)
    if dynamic:
        cursor.execute('''
            INSERT INTO job_profile (job_name, skills, certificates, soft_abilities)
            VALUES (?, ?, ?, ?)
        ''', (
            job_name,
            json.dumps(dynamic.get('skills', [])),
            json.dumps(dynamic.get('certificates', [])),
            json.dumps(dynamic.get('soft_abilities', {}))
        ))
        conn.commit()
        conn.close()
        return jsonify({
            'job_name': job_name,
            'skills': dynamic.get('skills', []),
            'certificates': dynamic.get('certificates', []),
            'soft_abilities': dynamic.get('soft_abilities', {}),
            'source': 'dynamic'
        })
    else:
        conn.close()
        return jsonify({'error': '无法生成画像'}), 404
# 添加单个岗位的路径查询接口
@job_bp.route('/<job_name>/vertical', methods=['GET'])
def get_vertical_path(job_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT to_job, description FROM job_relations WHERE from_job = ? AND relation_type = 'promotion'",
        (job_name,)
    )
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@job_bp.route('/<job_name>/lateral', methods=['GET'])
def get_lateral_path(job_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT to_job, description FROM job_relations WHERE from_job = ? AND relation_type = 'transition'",
        (job_name,)
    )
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
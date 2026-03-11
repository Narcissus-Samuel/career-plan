# routes/job.py
from flask import Blueprint, request, jsonify
from db import get_db
import json

job_bp = Blueprint('job', __name__, url_prefix='/api/jobs')

# ---------- 岗位分类接口（不变）----------
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

# ---------- 新增：通过岗位ID获取完整详情 ----------
@job_bp.route('/<int:job_id>', methods=['GET'])
def get_job_detail(job_id):
    """根据岗位ID返回完整详情（包含职位描述、公司信息等）"""
    conn = get_db()
    cursor = conn.cursor()
    # 使用 rowid 作为唯一标识
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

# ---------- 可选：通过岗位名称获取详情（如果存在同名岗位，返回第一个）----------
@job_bp.route('/profile/<string:job_name>', methods=['GET'])
def get_job_profile(job_name):
    """通过岗位名称获取详情（建议改用ID接口，此处保留兼容）"""
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

# ---------- 岗位图谱（不变）----------
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

# ---------- 获取行业列表（不变）----------
@job_bp.route('/industries', methods=['GET'])
def get_industries():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT industry FROM job WHERE industry IS NOT NULL AND industry != "" ORDER BY industry')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([row['industry'] for row in rows])

# ---------- 岗位搜索（返回列表，包含id）----------
@job_bp.route('/search', methods=['GET'])
def search_jobs():
    """
    搜索参数同之前，返回列表包含 id (rowid)
    """
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

    # 总数
    count_sql = f"SELECT COUNT(*) as total FROM job {where_clause}"
    cursor.execute(count_sql, params)
    total = cursor.fetchone()['total']

    # 列表查询，返回基本字段 + id
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

# ---------- 简单搜索（兼容旧版，同样返回id）----------
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
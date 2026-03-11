# routes/job.py
from flask import Blueprint, request, jsonify
from db import get_db
import json

job_bp = Blueprint('job', __name__, url_prefix='/api/jobs')

@job_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有岗位大类（用于前端选择）"""
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

@job_bp.route('/profile/<string:job_name>', methods=['GET'])
def get_job_profile(job_name):
    """获取单个岗位的详细画像（融合大类+具体标签）"""
    conn = get_db()
    cursor = conn.cursor()

    # 获取岗位基本信息
    cursor.execute('''
        SELECT j.rowid as id, j.job_name, j.company, j.industry, j.salary_range, j.location,
               j.job_description, j.company_size, j.company_type, j.category_id
        FROM job j
        WHERE j.job_name = ?
    ''', (job_name,))
    job = cursor.fetchone()
    if not job:
        conn.close()
        return jsonify({'error': '岗位不存在'}), 404

    job_dict = dict(job)

    # 获取所属大类画像
    if job['category_id']:
        cursor.execute('''
            SELECT name, skills, certificates, soft_abilities
            FROM job_categories
            WHERE id = ?
        ''', (job['category_id'],))
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

    # 获取该大类的细分标签
    if job['category_id']:
        cursor.execute('''
            SELECT tag_name, frequency, description
            FROM job_tags
            WHERE category_id = ?
            ORDER BY frequency DESC
        ''', (job['category_id'],))
        tags = cursor.fetchall()
        job_dict['tags'] = [dict(t) for t in tags]
    else:
        job_dict['tags'] = []

    conn.close()
    return jsonify(job_dict)

@job_bp.route('/graph', methods=['GET'])
def get_job_graph():
    """获取岗位图谱数据（用于前端可视化）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT from_job, to_job, relation_type, description
        FROM job_relations
    ''')
    edges = cursor.fetchall()
    # 收集所有节点
    nodes_set = set()
    for e in edges:
        nodes_set.add(e['from_job'])
        nodes_set.add(e['to_job'])
    nodes = [{'id': n, 'label': n} for n in nodes_set]
    conn.close()
    return jsonify({
        'nodes': nodes,
        'edges': [dict(e) for e in edges]
    })

@job_bp.route('/industries', methods=['GET'])
def get_industries():
    """获取所有行业列表（用于前端筛选）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT industry FROM job WHERE industry IS NOT NULL AND industry != "" ORDER BY industry')
    rows = cursor.fetchall()
    conn.close()
    industries = [row['industry'] for row in rows]
    return jsonify(industries)

@job_bp.route('/search', methods=['GET'])
def search_jobs():
    """
    岗位搜索接口（支持关键词、行业、公司规模、分页）
    参数：
        keyword: 搜索关键词（匹配岗位名称或公司）
        industry: 行业（精确匹配）
        company_size: 公司规模（如“20-99人”）
        page: 页码，默认1
        size: 每页条数，默认10
        sort_by: 排序字段（保留参数但暂时无效）
        order: asc/desc
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    industry = request.args.get('industry', '', type=str)
    company_size = request.args.get('company_size', '', type=str)
    order = request.args.get('order', 'asc')

    if page < 1 or size < 1:
        return jsonify({'error': '分页参数无效'}), 400

    # 使用 rowid 作为默认排序，避免无 id 列的问题
    order_sql = 'ASC' if order.lower() == 'asc' else 'DESC'

    conn = get_db()
    cursor = conn.cursor()

    # 构建查询条件
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

    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM job {where_clause}"
    cursor.execute(count_sql, params)
    total = cursor.fetchone()['total']

    # 查询数据，使用 rowid 作为 id 返回
    sql = f"""
        SELECT rowid as id, job_name, location, salary_range, company, industry, company_size, company_type
        FROM job {where_clause}
        ORDER BY rowid {order_sql}
        LIMIT ? OFFSET ?
    """
    offset = (page - 1) * size
    cursor.execute(sql, params + [size, offset])
    rows = cursor.fetchall()
    conn.close()

    jobs = [dict(row) for row in rows]
    return jsonify({
        'total': total,
        'page': page,
        'size': size,
        'items': jobs
    })

@job_bp.route('/simple_search', methods=['GET'])
def simple_search():
    """简单关键词搜索（仅匹配岗位名称和公司）"""
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
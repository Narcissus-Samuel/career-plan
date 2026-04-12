from flask import Blueprint, request, jsonify
from db import get_db
import json
import re
import time
from services.llm_service import generate_dynamic_job_profile, call_llm
from services.llm_service import get_job_skills, get_job_category

job_bp = Blueprint('job', __name__, url_prefix='/api/jobs')


# ========== 岗位名称标准化函数 ==========
def _normalize_job_name(job_name):
    """标准化岗位名称，用于数据库查询（不区分大小写）"""
    if not job_name:
        return job_name
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT job_name FROM job WHERE LOWER(job_name) = LOWER(?) LIMIT 1", (job_name,))
        row = cursor.fetchone()
        if row:
            return row['job_name']
        
        cursor.execute("SELECT job_name FROM job WHERE LOWER(job_name) LIKE LOWER(?) LIMIT 1", (f'%{job_name}%',))
        row = cursor.fetchone()
        if row:
            return row['job_name']
        
        return job_name
    except Exception as e:
        print(f"标准化岗位名称失败: {e}")
        return job_name
    finally:
        if conn:
            conn.close()


# ========== 原有接口 ==========
@job_bp.route('/categories', methods=['GET'])
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, icon, description, skills, certificates, soft_abilities
        FROM job_categories ORDER BY id
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
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rowid as id, job_name, location, salary_range, company, industry,
               company_size, company_type, job_code, job_description,
               updated_at, company_info, source_url
        FROM job WHERE rowid = ?
    ''', (job_id,))
    job = cursor.fetchone()
    conn.close()
    if not job:
        return jsonify({'error': '岗位不存在'}), 404
    return jsonify(dict(job))


@job_bp.route('/profile/<path:job_name>', methods=['GET'])
def get_job_profile_by_name(job_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rowid as id, job_name, location, salary_range, company, industry,
               company_size, company_type, job_code, job_description,
               updated_at, company_info, source_url, category_id
        FROM job WHERE job_name = ? LIMIT 1
    ''', (job_name,))
    job = cursor.fetchone()
    if not job:
        conn.close()
        return jsonify({'error': '岗位不存在'}), 404
    job_dict = dict(job)

    if job_dict.get('category_id'):
        cursor.execute('''
            SELECT name, skills, certificates, soft_abilities
            FROM job_categories WHERE id = ?
        ''', (job_dict['category_id'],))
        category = cursor.fetchone()
        if category:
            job_dict['category_profile'] = {
                'name': category['name'],
                'skills': json.loads(category['skills']) if category['skills'] else [],
                'certificates': json.loads(category['certificates']) if category['certificates'] else [],
                'soft_abilities': json.loads(category['soft_abilities']) if category['soft_abilities'] else {}
            }
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
        SELECT rowid as id, job_name, location, salary_range, company,
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
            FROM job WHERE job_name LIKE ? OR company LIKE ?
            ORDER BY rowid LIMIT ? OFFSET ?
        ''', (f'%{keyword}%', f'%{keyword}%', size, offset))
    else:
        cursor.execute('''
            SELECT rowid as id, job_name, company, salary_range, location
            FROM job ORDER BY rowid LIMIT ? OFFSET ?
        ''', (size, offset))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ========== 获取岗位画像 ==========
@job_bp.route('/<int:job_id>/profile', methods=['GET'])
def get_job_profile(job_id):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rowid as id, job_name, job_description, category_id
            FROM job WHERE rowid = ?
        ''', (job_id,))
        job = cursor.fetchone()
        if not job:
            return jsonify({'error': '岗位不存在'}), 404

        job_name = job['job_name']
        category_id = job['category_id']

        cursor.execute('''
            SELECT skills, certificates, soft_abilities
            FROM job_profile WHERE job_name = ?
        ''', (job_name,))
        existing = cursor.fetchone()
        
        if existing:
            profile = {
                'job_name': job_name,
                'skills': json.loads(existing['skills']) if existing['skills'] else [],
                'certificates': json.loads(existing['certificates']) if existing['certificates'] else [],
                'soft_abilities': json.loads(existing['soft_abilities']) if existing['soft_abilities'] else {},
                'source': 'job_profile'
            }
        else:
            dynamic = generate_dynamic_job_profile(job_name)
            if not dynamic:
                return jsonify({'error': '无法生成画像'}), 404
            
            cursor.execute('''
                INSERT OR REPLACE INTO job_profile (job_name, skills, certificates, soft_abilities)
                VALUES (?, ?, ?, ?)
            ''', (
                job_name,
                json.dumps(dynamic.get('skills', [])),
                json.dumps(dynamic.get('certificates', [])),
                json.dumps(dynamic.get('soft_abilities', {}))
            ))
            conn.commit()
            profile = {
                'job_name': job_name,
                'skills': dynamic.get('skills', []),
                'certificates': dynamic.get('certificates', []),
                'soft_abilities': dynamic.get('soft_abilities', {}),
                'source': 'dynamic'
            }

        if category_id:
            cursor.execute('''
                SELECT name, skills, certificates, soft_abilities
                FROM job_categories WHERE id = ?
            ''', (category_id,))
            cat = cursor.fetchone()
            if cat:
                profile['category_reference'] = {
                    'category_name': cat['name'],
                    'skills': json.loads(cat['skills']) if cat['skills'] else [],
                    'certificates': json.loads(cat['certificates']) if cat['certificates'] else [],
                    'soft_abilities': json.loads(cat['soft_abilities']) if cat['soft_abilities'] else {}
                }
        return jsonify(profile)
        
    except Exception as e:
        print(f"获取岗位画像失败: {e}")
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ========== 垂直发展路径 ==========
def _get_career_path_internal(job_name):
    """内部函数：获取完整垂直发展路径"""
    normalized_name = _normalize_job_name(job_name)
    
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        chain = []
        current = normalized_name
        visited = set()
        
        while current and current not in visited:
            visited.add(current)
            cursor.execute('''
                SELECT to_job, description FROM job_relations 
                WHERE from_job = ? AND relation_type = 'promotion' LIMIT 1
            ''', (current,))
            row = cursor.fetchone()
            if not row:
                break
            chain.append({
                'from_job': current,
                'to_job': row['to_job'],
                'description': row['description']
            })
            current = row['to_job']
        
        if chain:
            return {'success': True, 'source': 'database', 'job_name': normalized_name, 'path': chain}
        
        print(f"🤖 正在为岗位 [{normalized_name}] 动态生成垂直晋升路径...")
        
        prompt = f"""
你是一位资深的职业规划专家。请为【{normalized_name}】岗位生成一条完整的、连续的晋升发展路径。

要求：
1. 输出一个JSON数组，包含从当前岗位开始的连续晋升路径
2. 每个元素包含：job_name（岗位名称）、description（该岗位的简要描述）
3. 路径长度：3-5个节点（包含当前岗位）
4. 必须是真实存在、行业通用的岗位名称

只返回JSON数组，不要其他文字。
"""
        
        result = call_llm(prompt, temperature=0.3, max_tokens=1500)
        if not result:
            raise ValueError("AI 返回空结果")
        
        json_match = re.search(r'\[[\s\S]*\]', result)
        if json_match:
            result = json_match.group(0)
        
        path_data = json.loads(result)
        
        if not isinstance(path_data, list) or len(path_data) < 2:
            raise ValueError("返回格式不正确")
        
        formatted_path = []
        current = normalized_name
        for i, item in enumerate(path_data):
            if i == 0:
                continue
            formatted_path.append({
                'from_job': current,
                'to_job': item['job_name'],
                'description': item.get('description', '')
            })
            current = item['job_name']
        
        conn2 = None
        cursor2 = None
        try:
            conn2 = get_db()
            cursor2 = conn2.cursor()
            for item in formatted_path:
                cursor2.execute('''
                    INSERT OR REPLACE INTO job_relations (from_job, to_job, relation_type, description)
                    VALUES (?, ?, ?, ?)
                ''', (item['from_job'], item['to_job'], 'promotion', item['description']))
            conn2.commit()
        finally:
            if cursor2:
                cursor2.close()
            if conn2:
                conn2.close()
        
        return {'success': True, 'source': 'ai_generated', 'job_name': normalized_name, 'path': formatted_path}
        
    except Exception as e:
        print(f"❌ 生成垂直路径失败: {e}")
        default_path = [
            {'from_job': normalized_name, 'to_job': f'高级{normalized_name}', 'description': f'从{normalized_name}晋升至高级{normalized_name}'},
            {'from_job': f'高级{normalized_name}', 'to_job': f'{normalized_name}专家', 'description': f'从高级{normalized_name}晋升至{normalized_name}专家'}
        ]
        return {'success': True, 'source': 'default', 'job_name': normalized_name, 'path': default_path}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ========== 横向发展路径 ==========
def _get_lateral_path_internal(job_name):
    """内部函数：获取横向发展路径，确保至少2条"""
    normalized_name = _normalize_job_name(job_name)
    
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT to_job, description FROM job_relations 
            WHERE from_job = ? AND relation_type = 'transition'
            ORDER BY id
        ''', (normalized_name,))
        existing = cursor.fetchall()
        
        # 构建已有路径列表
        existing_paths = []
        for row in existing:
            existing_paths.append({
                'job_name': row['to_job'],
                'description': row['description']
            })
        
        # 如果已有路径 >= 2 条，直接返回
        if len(existing_paths) >= 2:
            return {'success': True, 'source': 'database', 'job_name': normalized_name, 'lateral_paths': existing_paths}
        
        print(f"🤖 正在为岗位 [{normalized_name}] 动态生成横向发展路径（已有{len(existing_paths)}条）...")
        
        try:
            current_skills = get_job_skills(normalized_name)
            skills_str = '、'.join(current_skills[:10]) if current_skills else '未知'
        except:
            skills_str = '未知'
        
        prompt = f"""
你是一位资深的职业规划专家。请为【{normalized_name}】岗位推荐3-5个相关的横向发展（换岗/转型）方向。

当前岗位的核心技能：{skills_str}

要求：
1. 输出一个JSON数组，每个元素包含：job_name（目标岗位名称）、description（转型需要的条件和建议）
2. 推荐的岗位必须是同一行业/领域内，技能可迁移的岗位

只返回JSON数组，不要其他文字。
"""
        
        result = call_llm(prompt, temperature=0.3, max_tokens=1200)
        if not result:
            raise ValueError("AI 返回空结果")
        
        json_match = re.search(r'\[[\s\S]*\]', result)
        if json_match:
            result = json_match.group(0)
        
        new_paths = json.loads(result)
        
        if not isinstance(new_paths, list):
            raise ValueError("返回格式不正确")
        
        # 保存到数据库
        conn2 = None
        cursor2 = None
        try:
            conn2 = get_db()
            cursor2 = conn2.cursor()
            for item in new_paths:
                to_job = item.get('job_name', '')
                description = item.get('description', '')
                if to_job:
                    cursor2.execute('''
                        INSERT OR IGNORE INTO job_relations (from_job, to_job, relation_type, description)
                        VALUES (?, ?, ?, ?)
                    ''', (normalized_name, to_job, 'transition', description))
            conn2.commit()
            
            # 【关键】等待一下确保数据写入完成
            time.sleep(0.2)
            
            # 【关键】重新读取数据库，确保返回最新数据
            cursor2.execute('''
                SELECT to_job, description FROM job_relations 
                WHERE from_job = ? AND relation_type = 'transition'
                ORDER BY id
            ''', (normalized_name,))
            fresh_rows = cursor2.fetchall()
            all_paths = []
            for row in fresh_rows:
                all_paths.append({
                    'job_name': row['to_job'],
                    'description': row['description']
                })
            
            print(f"✅ 横向路径生成完成，共 {len(all_paths)} 条: {[p['job_name'] for p in all_paths]}")
            
        finally:
            if cursor2:
                cursor2.close()
            if conn2:
                conn2.close()
        
        return {'success': True, 'source': 'ai_generated', 'job_name': normalized_name, 'lateral_paths': all_paths}
        
    except Exception as e:
        print(f"❌ 生成横向路径失败: {e}")
        import traceback
        traceback.print_exc()
        default_paths = existing_paths.copy() if 'existing_paths' in locals() else []
        if len(default_paths) < 2:
            default_paths.append({"job_name": f"高级{job_name}", "description": f"在{job_name}岗位上深耕，提升专业深度"})
        if len(default_paths) < 3:
            default_paths.append({"job_name": f"{job_name}顾问", "description": f"从{job_name}转型为顾问方向"})
        return {'success': True, 'source': 'default', 'job_name': job_name, 'lateral_paths': default_paths[:3]}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ========== 获取完整的职业发展图谱 ==========
@job_bp.route('/<job_name>/full-path', methods=['GET'])
def get_full_career_path(job_name):
    """获取岗位的完整发展路径（垂直+横向）"""
    normalized_name = _normalize_job_name(job_name)
    
    # 获取垂直路径
    vertical_result = _get_career_path_internal(normalized_name)
    vertical_path = vertical_result.get('path', []) if vertical_result.get('success') else []
    
    # 获取横向路径（确保返回完整数据）
    lateral_result = _get_lateral_path_internal(normalized_name)
    lateral_paths = lateral_result.get('lateral_paths', []) if lateral_result.get('success') else []
    
    # 格式化垂直路径
    formatted_vertical = []
    for item in vertical_path:
        formatted_vertical.append({
            'from_job': item.get('from_job', normalized_name),
            'to_job': item.get('to_job', ''),
            'description': item.get('description', '')
        })
    
    # 格式化横向路径
    formatted_lateral = []
    for item in lateral_paths:
        formatted_lateral.append({
            'job_name': item.get('job_name', ''),
            'description': item.get('description', '')
        })
    
    print(f"📊 返回数据: 垂直路径 {len(formatted_vertical)} 条, 横向路径 {len(formatted_lateral)} 条")
    
    return jsonify({
        'success': True,
        'job_name': normalized_name,
        'vertical_path': formatted_vertical,
        'lateral_paths': formatted_lateral
    })

# ========== 简单路径查询接口 ==========
@job_bp.route('/<job_name>/vertical', methods=['GET'])
def get_vertical_path_simple(job_name):
    normalized_name = _normalize_job_name(job_name)
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        chain = []
        current = normalized_name
        visited = set()
        while current and current not in visited:
            visited.add(current)
            cursor.execute(
                "SELECT to_job, description FROM job_relations WHERE from_job = ? AND relation_type = 'promotion' LIMIT 1",
                (current,)
            )
            row = cursor.fetchone()
            if not row:
                break
            chain.append({
                'from_job': current,
                'to_job': row['to_job'],
                'description': row['description']
            })
            current = row['to_job']
        return jsonify(chain)
    finally:
        if conn:
            conn.close()


@job_bp.route('/<job_name>/lateral', methods=['GET'])
def get_lateral_path_simple(job_name):
    normalized_name = _normalize_job_name(job_name)
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT to_job, description FROM job_relations WHERE from_job = ? AND relation_type = 'transition'",
            (normalized_name,)
        )
        rows = cursor.fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        if conn:
            conn.close()


@job_bp.route('/names', methods=['GET'])
def get_all_job_names():
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT job_name FROM job WHERE job_name IS NOT NULL AND job_name != '' ORDER BY job_name")
        rows = cursor.fetchall()
        job_names = [row['job_name'] for row in rows]
        return jsonify(job_names)
    finally:
        if conn:
            conn.close()
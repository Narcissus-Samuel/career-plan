# routes/report.py
from flask import Blueprint, request, jsonify, send_file
from db import get_db
from .auth import token_required, verify_token
import io
import json
from datetime import datetime

report_bp = Blueprint('report', __name__, url_prefix='/api')

# ========== 增强版报告生成接口（完全基于数据库） ==========
@report_bp.route('/report', methods=['POST'])
def generate_report():
    """
    生成个性化职业规划报告（HTML格式）
    数据来源：用户资料、能力评估、职业规划等（数据库）
    未来可无缝对接大模型：只需替换 report_builder 中的静态规则为模型调用
    """
    data = request.json
    student_id = data.get('studentId')
    job_name = data.get('jobName', '目标岗位')

    user = None
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
        user = verify_token(token)
    if not user and student_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM student WHERE id = ?', (student_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row['user_id']:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (row['user_id'],))
            user = cursor.fetchone()
            conn.close()

    if not user:
        return jsonify({
            "content": """
            <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; text-align: center;">
                <h2 style="color: #666;">请先登录后查看个性化报告</h2>
                <p>登录后，我们将根据你的资料生成专属职业规划。</p>
                <button onclick="location.href='/login'" style="padding:10px 20px; background:#409EFF; color:white; border:none; border-radius:4px;">立即登录</button>
            </div>
            """
        })

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, gender, grade, major, target
        FROM user_profiles WHERE user_id = ?
    ''', (user['id'],))
    profile = cursor.fetchone()

    cursor.execute('''
        SELECT ad.name, ad.code, aa.score
        FROM ability_assessments aa
        JOIN ability_dimensions ad ON aa.dimension_id = ad.id
        WHERE aa.user_id = ?
        ORDER BY ad.sort_order
    ''', (user['id'],))
    abilities = cursor.fetchall()

    cursor.execute('''
        SELECT target, title FROM user_plans
        WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
    ''', (user['id'],))
    plan = cursor.fetchone()

    conn.close()

    report_html = _build_report_html(
        user=user,
        profile=profile,
        abilities=abilities,
        plan=plan,
        job_name=job_name
    )

    return jsonify({"content": report_html})

def _build_report_html(user, profile, abilities, plan, job_name):
    """根据用户数据生成HTML报告（当前为静态规则，日后可替换为模型生成）"""
    name = profile['name'] if profile and profile['name'] else user['username']
    grade = profile['grade'] if profile and profile['grade'] else '未知年级'
    major = profile['major'] if profile and profile['major'] else '未知专业'
    target = profile['target'] if profile and profile['target'] else (plan['target'] if plan else '未设定')

    if abilities and len(abilities) > 0:
        avg_score = sum(a['score'] for a in abilities) / len(abilities)
        strength = max(abilities, key=lambda x: x['score'])
        weakness = min(abilities, key=lambda x: x['score'])
        strength_name = strength['name']
        weakness_name = weakness['name']
        match_score = round(avg_score * 20)
    else:
        strength_name = '学习能力'
        weakness_name = '创新能力'
        match_score = 75

    html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
        <h1 style="color: #409EFF;">{name} 的{job_name}职业规划报告</h1>
        <p>亲爱的{name}，根据你的资料和能力评估，我们为你量身定制了以下规划：</p>

        <h2>一、个人分析</h2>
        <p>你的专业是 <strong>{major}</strong>，目前 <strong>{grade}</strong>，职业目标为 <strong>{target}</strong>。</p>
        <p>你的核心优势是 <strong>{strength_name}</strong>，有待提升的是 <strong>{weakness_name}</strong>。</p>

        <h2>二、人岗匹配</h2>
        <p>与 <strong>{job_name}</strong> 的匹配度为 <strong>{match_score}%</strong>，建议加强实战经验。</p>

        <h2>三、发展建议</h2>
        <ul>
            <li><strong>短期（3个月）</strong>：学习{job_name}相关技能，完成1个实战项目。</li>
            <li><strong>中期（1年）</strong>：积累实习经验，考取相关证书（如{job_name}认证）。</li>
            <li><strong>长期（3年）</strong>：成为团队骨干，向{target}方向发展。</li>
        </ul>
    """

    if plan:
        html += f"""
        <h2>四、当前规划概要</h2>
        <p>你的规划标题：{plan['title'] or '未命名'}</p>
        """

    html += """
        <p style="color: #666; margin-top:30px;">本报告根据你的资料生成，仅供参考。请结合自身情况调整。</p>
    </div>
    """
    return html

# ========== 原有导出接口（保持不变）==========
@report_bp.route('/report/export', methods=['POST'])
def export_report():
    """导出报告文件（模拟Word/PPT）"""
    data = request.json
    format_type = data.get('format', 'word')
    content = data.get('content', '默认内容')

    file_data = io.BytesIO()
    file_data.write(content.encode('utf-8'))
    file_data.seek(0)

    return send_file(
        file_data,
        as_attachment=True,
        download_name=f"report.{format_type}",
        mimetype='application/octet-stream'
    )

# ========== 新增报告管理接口（增强版，生成美观HTML）==========
REPORT_TYPES = [
    {'id': 1, 'name': '综合职业规划报告', 'description': '包含测评结果、能力分析、发展路径的完整报告', 'icon': '📊', 'color': '#1890ff'},
    {'id': 2, 'name': '能力短板分析报告', 'description': '聚焦能力短板，提供详细的提升建议和学习资源', 'icon': '🎯', 'color': '#faad14'},
    {'id': 3, 'name': '发展路径规划报告', 'description': '详细的分阶段发展路径，包含里程碑和目标设置', 'icon': '🗺️', 'color': '#52c41a'},
    {'id': 4, 'name': '职业测评结果报告', 'description': '仅包含职业兴趣测评的原始数据和基础分析', 'icon': '📈', 'color': '#ff7a45'},
]

REPORT_TEMPLATES = {
    1: {
        'name': '综合职业规划报告',
        'modules': [
            {'key': 'basicInfo', 'name': '基础信息', 'default': True},
            {'key': 'careerPlan', 'name': '职业规划', 'default': True},
            {'key': 'abilityScore', 'name': '能力测评分析', 'default': True},
            {'key': 'careerSuggest', 'name': '职业适配建议', 'default': True},
            {'key': 'summary', 'name': '总结与建议', 'default': True},
        ]
    },
    2: {
        'name': '能力短板分析报告',
        'modules': [
            {'key': 'basicInfo', 'name': '基础信息', 'default': True},
            {'key': 'abilityScore', 'name': '能力测评分析', 'default': True},
            {'key': 'careerSuggest', 'name': '职业适配建议', 'default': True},
            {'key': 'summary', 'name': '总结与建议', 'default': True},
        ]
    },
    3: {
        'name': '发展路径规划报告',
        'modules': [
            {'key': 'basicInfo', 'name': '基础信息', 'default': True},
            {'key': 'careerPlan', 'name': '职业规划', 'default': True},
            {'key': 'careerSuggest', 'name': '职业适配建议', 'default': True},
        ]
    },
    4: {
        'name': '职业测评结果报告',
        'modules': [
            {'key': 'basicInfo', 'name': '基础信息', 'default': True},
            {'key': 'abilityScore', 'name': '能力测评分析', 'default': True},
        ]
    },
}

@report_bp.route('/report/types', methods=['GET'])
def get_report_types():
    return jsonify(REPORT_TYPES)

@report_bp.route('/report/templates/<int:type_id>', methods=['GET'])
def get_report_template(type_id):
    template = REPORT_TEMPLATES.get(type_id)
    if not template:
        return jsonify({'error': '报告类型不存在'}), 404
    return jsonify(template)

# ---------- 安全构建 HTML 报告（将所有 Row 转换为字典，使用 .get 访问）----------
def _build_html_report_safe(user, profile, abilities, student_info, interests, plan, report_type, modules):
    """
    根据用户数据生成美观的 HTML 报告（安全版，兼容数据缺失）
    参数说明：
        user: users 表记录 (Row)
        profile: user_profiles 记录 (Row 或 None)
        abilities: 能力评估记录列表 (Row 列表)
        student_info: student 表记录 (Row 或 None)
        interests: 兴趣名称列表 (list)
        plan: user_plans 记录 (Row 或 None)
        report_type: 报告类型ID
        modules: 选中的模块列表 (list)
    """
    # 将所有 Row 对象转换为字典，方便安全访问
    user_dict = dict(user) if user else {}
    profile_dict = dict(profile) if profile else {}
    student_dict = dict(student_info) if student_info else {}
    plan_dict = dict(plan) if plan else {}

    # 将 abilities 转换为字典列表
    abilities_list = []
    if abilities:
        for row in abilities:
            abilities_list.append(dict(row))

    # 基础信息（使用字典的 .get 方法提供默认值）
    name = profile_dict.get('name') or user_dict.get('username', '未知用户')
    gender = profile_dict.get('gender', '未填写')
    grade = profile_dict.get('grade', '未知年级')
    major = profile_dict.get('major', '未知专业')
    target = profile_dict.get('target') or plan_dict.get('target', '未设定')

    # 兴趣
    interest_str = '、'.join(interests) if interests else '未填写'

    # 技能（处理可能为空的 JSON）
    skills_str = '暂无'
    if student_dict.get('skills'):
        try:
            skills = json.loads(student_dict['skills'])
            skills_str = '、'.join(skills) if skills else '暂无'
        except:
            skills_str = student_dict['skills']  # 如果不是 JSON 则直接使用字符串

    # 证书
    certs_str = '暂无'
    if student_dict.get('certificates'):
        try:
            certs = json.loads(student_dict['certificates'])
            certs_str = '、'.join(certs) if certs else '暂无'
        except:
            certs_str = student_dict['certificates']

    # 实习经历
    internship_str = student_dict.get('internships', '暂无实习经历')

    # 完整度与竞争力
    completeness = student_dict.get('completeness', 0)
    competitiveness = student_dict.get('competitiveness', 0)

    # 能力评估数据
    ability_rows = ''
    strength = None
    weakness = None
    match_score = 0
    if abilities_list:
        scores = [a.get('score', 0) for a in abilities_list]
        if scores:
            avg_score = sum(scores) / len(scores)
            match_score = round(avg_score * 20)
            strength = max(abilities_list, key=lambda x: x.get('score', 0))
            weakness = min(abilities_list, key=lambda x: x.get('score', 0))
        for a in abilities_list:
            ability_rows += f'<tr><td>{a.get("name", "未知")}</td><td>{a.get("score", 0)}星</td></tr>'

    # 开始构建 HTML
    html = f'''
    <div class="report-inner" style="font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; padding: 30px; background: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
        <h1 style="text-align: center; font-size: 28px; font-weight: 600; color: #2c3e50; margin-bottom: 25px; border-bottom: 2px solid #409EFF; padding-bottom: 15px;">
            {name} 的个性化职业生涯发展报告
        </h1>
        <div style="text-align: right; color: #7f8c8d; margin-bottom: 30px; font-size: 14px; border-bottom: 1px dashed #dcdfe6; padding-bottom: 15px;">
            <p>报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>适用年级：{grade} | 所属专业：{major}</p>
            <p>能力画像完整度：{completeness}% | 就业竞争力：{competitiveness}%</p>
            <p>生成引擎：静态规则（可替换为大模型）</p>
        </div>
    '''

    # 一、基础信息
    if 'basicInfo' in modules:
        html += f'''
        <div style="margin-bottom: 40px;">
            <h2 style="font-size: 22px; font-weight: 600; color: #409EFF; border-left: 6px solid #409EFF; padding-left: 15px; margin-bottom: 20px;">一、个人基础信息</h2>
            <table style="width: 100%; border-collapse: collapse; background: #fafafa; border-radius: 8px; overflow: hidden;">
                <tr style="background: #f0f2f5;">
                    <td style="padding: 12px 15px; font-weight: 600; width: 20%;">姓名</td>
                    <td style="padding: 12px 15px;">{name}</td>
                    <td style="padding: 12px 15px; font-weight: 600; width: 20%;">性别</td>
                    <td style="padding: 12px 15px;">{gender}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 15px; font-weight: 600;">年级</td>
                    <td style="padding: 12px 15px;">{grade}</td>
                    <td style="padding: 12px 15px; font-weight: 600;">专业</td>
                    <td style="padding: 12px 15px;">{major}</td>
                </tr>
                <tr style="background: #f0f2f5;">
                    <td style="padding: 12px 15px; font-weight: 600;">目标方向</td>
                    <td style="padding: 12px 15px;">{target}</td>
                    <td style="padding: 12px 15px; font-weight: 600;">职业兴趣</td>
                    <td style="padding: 12px 15px;">{interest_str}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 15px; font-weight: 600;">掌握技能</td>
                    <td style="padding: 12px 15px;" colspan="3">{skills_str}</td>
                </tr>
                <tr style="background: #f0f2f5;">
                    <td style="padding: 12px 15px; font-weight: 600;">持有证书</td>
                    <td style="padding: 12px 15px;" colspan="3">{certs_str}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 15px; font-weight: 600;">实习经历</td>
                    <td style="padding: 12px 15px;" colspan="3">{internship_str}</td>
                </tr>
            </table>
        </div>
        '''

    # 二、能力测评分析
    if 'abilityScore' in modules and abilities_list and strength and weakness:
        html += f'''
        <div style="margin-bottom: 40px;">
            <h2 style="font-size: 22px; font-weight: 600; color: #409EFF; border-left: 6px solid #409EFF; padding-left: 15px; margin-bottom: 20px;">二、能力测评分析</h2>
            <div style="background: #ecf8ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <p style="font-size: 16px; margin-bottom: 10px;"><strong>核心优势：</strong>{strength.get("name", "未知")}（{strength.get("score", 0)}星）</p>
                <p style="margin-bottom: 10px;"><strong>待提升短板：</strong>{weakness.get("name", "未知")}（{weakness.get("score", 0)}星）</p>
                <p><strong>综合匹配度：</strong>{match_score}%</p>
            </div>
            <table style="width: 100%; border-collapse: collapse; background: #fafafa; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #409EFF; color: white;">
                        <th style="padding: 10px;">能力维度</th>
                        <th style="padding: 10px;">得分（1-5星）</th>
                    </tr>
                </thead>
                <tbody>
                    {ability_rows}
                </tbody>
            </table>
        </div>
        '''

    # 三、职业规划
    if 'careerPlan' in modules:
        plan_content = plan_dict.get('title') if plan_dict else None
        if not plan_content:
            grade_defaults = {
                '大一': '夯实专业基础，参加社团，了解行业',
                '大二': '考取证书，参与实习/项目，明确方向',
                '大三': '针对性提升能力，准备实习/备考',
                '大四': '冲刺目标，完成求职/考研/留学流程'
            }
            plan_content = grade_defaults.get(grade, '暂无规划数据')
        html += f'''
        <div style="margin-bottom: 40px;">
            <h2 style="font-size: 22px; font-weight: 600; color: #409EFF; border-left: 6px solid #409EFF; padding-left: 15px; margin-bottom: 20px;">三、职业规划</h2>
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
                {plan_content}
            </div>
        </div>
        '''

    # 四、职业适配建议
    if 'careerSuggest' in modules and strength and weakness:
        suggest = f"根据你的能力特点，建议优先选择需要{strength.get('name', '该能力')}的岗位，如数据分析师、产品经理等。同时针对性提升{weakness.get('name', '该能力')}，可通过课程学习、项目实践等方式。"
        html += f'''
        <div style="margin-bottom: 40px;">
            <h2 style="font-size: 22px; font-weight: 600; color: #409EFF; border-left: 6px solid #409EFF; padding-left: 15px; margin-bottom: 20px;">四、职业适配建议</h2>
            <div style="background: #f0f9eb; padding: 15px; border-radius: 8px;">
                {suggest}
            </div>
        </div>
        '''

    # 五、总结与建议
    if 'summary' in modules:
        summary = "整体来看，你的能力基础扎实，职业目标明确。建议按照规划分阶段实施，保持学习动力，积极参与实践，不断调整优化。"
        html += f'''
        <div style="margin-bottom: 40px;">
            <h2 style="font-size: 22px; font-weight: 600; color: #409EFF; border-left: 6px solid #409EFF; padding-left: 15px; margin-bottom: 20px;">五、总结与建议</h2>
            <div style="background: #fdf6ec; padding: 15px; border-radius: 8px;">
                {summary}
            </div>
        </div>
        '''

    html += '''
        <div style="text-align: center; color: #909399; font-size: 13px; margin-top: 50px; border-top: 1px solid #e4e7ed; padding-top: 20px;">
            <p>本报告由大学生职业规划系统生成，数据仅供参考，请结合个人实际情况调整。</p>
            <p>如有疑问，请联系系统管理员。</p>
        </div>
    </div>
    '''
    return html

@report_bp.route('/report/generate', methods=['POST'])
@token_required
def generate_report_saved():
    """生成报告并保存到数据库（根据format决定生成纯文本或HTML）"""
    user = request.user
    data = request.json
    title = data.get('title')
    report_type = data.get('type')
    format_type = data.get('format', 'html')
    modules = data.get('modules', [])

    if not title or not report_type:
        return jsonify({'error': '缺少必要参数'}), 400

    # 从数据库获取所有必要数据
    conn = get_db()
    cursor = conn.cursor()

    # 基础信息
    cursor.execute('''
        SELECT name, gender, grade, major, target
        FROM user_profiles WHERE user_id = ?
    ''', (user['id'],))
    profile = cursor.fetchone()

    # 能力评估
    cursor.execute('''
        SELECT ad.name, ad.code, aa.score
        FROM ability_assessments aa
        JOIN ability_dimensions ad ON aa.dimension_id = ad.id
        WHERE aa.user_id = ?
        ORDER BY ad.sort_order
    ''', (user['id'],))
    abilities = cursor.fetchall()

    # 学生信息（技能、证书、实习、完整度、竞争力）
    cursor.execute('''
        SELECT skills, certificates, internships, completeness, competitiveness
        FROM student
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    ''', (user['id'],))
    student_info = cursor.fetchone()

    # 职业兴趣
    cursor.execute('''
        SELECT i.name
        FROM user_interests ui
        JOIN interests i ON ui.interest_id = i.id
        WHERE ui.user_id = ?
    ''', (user['id'],))
    interest_rows = cursor.fetchall()
    interests = [row['name'] for row in interest_rows]

    # 用户规划（最新一条）
    cursor.execute('''
        SELECT target, title FROM user_plans
        WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
    ''', (user['id'],))
    plan = cursor.fetchone()

    conn.close()

    # 只要不是纯文本，就生成 HTML 报告（包括 pdf/word 等）
    if format_type != 'txt':
        content = _build_html_report_safe(
            user=user,
            profile=profile,
            abilities=abilities,
            student_info=student_info,
            interests=interests,
            plan=plan,
            report_type=report_type,
            modules=modules
        )
    else:
        # 纯文本格式（原有逻辑）
        content = f"报告标题：{title}\n"
        content += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"用户ID：{user['id']}\n"
        if 'basicInfo' in modules and profile:
            content += f"\n【基础信息】\n姓名：{profile['name'] or '未填写'}\n性别：{profile['gender'] or '未填写'}\n年级：{profile['grade'] or '未填写'}\n专业：{profile['major'] or '未填写'}\n目标方向：{profile['target'] or '未填写'}\n"
        if 'abilityScore' in modules and abilities:
            content += "\n【能力测评】\n"
            for ab in abilities:
                content += f"{ab['name']}：{ab['score']}分\n"
        if 'summary' in modules:
            content += "\n【总结建议】\n根据您的职业目标和能力现状，建议您：\n1. 夯实专业基础\n2. 积累实践经验\n3. 持续提升软技能\n"

    # 保存到 reports 表
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reports (user_id, title, type, format, content)
        VALUES (?, ?, ?, ?, ?)
    ''', (user['id'], title, report_type, format_type, content))
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'id': report_id, 'message': '报告生成成功', 'content': content})

# ========== 历史记录与下载接口 ==========
@report_bp.route('/report/history', methods=['GET'])
@token_required
def get_report_history():
    user = request.user
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, type, format, created_at
        FROM reports
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user['id'],))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@report_bp.route('/report/<int:report_id>', methods=['GET'])
@token_required
def get_report_detail(report_id):
    user = request.user
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, type, format, content, created_at
        FROM reports
        WHERE id = ? AND user_id = ?
    ''', (report_id, user['id']))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': '报告不存在'}), 404
    return jsonify(dict(row))

@report_bp.route('/report/<int:report_id>/download', methods=['GET'])
@token_required
def download_report(report_id):
    user = request.user
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, format, content
        FROM reports
        WHERE id = ? AND user_id = ?
    ''', (report_id, user['id']))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': '报告不存在'}), 404

    filename = f"report_{report_id}.{row['format']}"
    file_data = io.BytesIO()
    file_data.write(row['content'].encode('utf-8'))
    file_data.seek(0)

    return send_file(
        file_data,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream'
    )
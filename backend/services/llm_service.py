"""
services/llm_service.py

提供与职业规划相关的"大模型"接口实现（本地启发式 + 可选调用外部 API 的包装）

函数：
- parse_resume(file_path) -> dict
- intelligent_recommendation(student_dict, jobs_list)
- generate_plan_suggestion(student_dict, job_name)
- chat_qa(question, context)

说明：若配置了环境变量 DEEPSEEK_API_KEY，会尝试使用 DeepSeek；
否则使用本地启发式模板生成文本，便于离线演示。
"""
import os
import json
from typing import Dict, Any, List
from algorithms import recommend_jobs, compute_match_score

# 高级算法类（若存在则优先使用）
try:
    from career_ml import CareerRecommend
except Exception:
    CareerRecommend = None


def _get_deepseek_key():
    """✅ 动态获取 API Key，确保 load_dotenv 后生效"""
    return os.environ.get('DEEPSEEK_API_KEY')


def _call_deepseek(prompt: str) -> str:
    """调用 DeepSeek HTTP 接口（兼容 OpenAI-style chat completion）"""
    api_key = _get_deepseek_key()
    if not api_key:
        print('⚠️ DEEPSEEK_API_KEY 未配置，使用本地模板')
        return ''
    try:
        import requests
        url = 'https://api.siliconflow.cn/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'deepseek-ai/DeepSeek-V3',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 600
        }
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        j = r.json()
        # 兼容多种返回结构
        if 'choices' in j and len(j['choices']) > 0:
            c = j['choices'][0]
            if isinstance(c.get('message'), dict) and 'content' in c['message']:
                return c['message']['content']
            if 'text' in c:
                return c['text']
        return j.get('result') or ''
    except Exception as e:
        print(f'❌ DeepSeek 调用失败：{e}')
        return ''


def parse_resume(file_path: str) -> Dict[str, Any]:
    """解析简历（演示版）"""
    try:
        _, ext = os.path.splitext(file_path.lower())
        if ext in ('.txt', '.md'):
            with open(file_path, 'r', encoding='utf-8') as f:
                txt = f.read()
            skills = []
            for line in txt.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    if k.strip().lower() in ('skills', '技能'):
                        skills = [s.strip() for s in v.split(',') if s.strip()]
            return {
                'name': None,
                'major': None,
                'grade': None,
                'skills': skills or ['Python'],
                'certificates': [],
                'internships': None,
                'interests': [],
                'completeness': 70,
                'competitiveness': 60
            }
    except Exception:
        pass

    return {
        'name': '测试学生',
        'major': '计算机',
        'grade': '大三',
        'skills': ['Python', 'SQL'],
        'certificates': [],
        'internships': None,
        'interests': ['数据分析'],
        'completeness': 80,
        'competitiveness': 70
    }


def intelligent_recommendation(student: Dict[str, Any], jobs: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """返回推荐岗位列表以及每个岗位的匹配详情"""
    if CareerRecommend is not None:
        try:
            cr = CareerRecommend()
            recs_raw = cr.get_match_list(student, jobs, top_k=top_n)
            out = []
            for r in recs_raw:
                out.append({'job': r['job'], 'match': {'overall_score': r['score'], 'skill_score': r.get('skill_score')}})
            return out
        except Exception:
            pass

    recs = recommend_jobs(student, jobs, top_n)
    out = []
    for job, detail in recs:
        item = {'job': job, 'match': detail}
        out.append(item)
    return out


def generate_plan_suggestion(student: Dict[str, Any], job_name: str) -> str:
    """基于学生信息生成规划建议文本（模板 + 可选大模型增强）"""
    template = []
    template.append(f"目标岗位：{job_name}")
    template.append("总体建议：")
    template.append("1. 技能提升：根据岗位需求补齐关键技能，例如掌握相关框架与工具。")
    template.append("2. 项目经验：建议完成至少 1-2 个相关项目，展示端到端能力。")
    template.append("3. 简历优化：将关键技能与项目成果量化展示，突出业绩与指标。")
    template.append("4. 面试准备：整理常见技术问题与行为问题的回答要点。")

    prompt = '\n'.join(template) + '\n\n学生信息：' + json.dumps(student, ensure_ascii=False)
    
    print('🔍 正在调用 DeepSeek 生成规划建议...')
    ai = _call_deepseek(prompt)
    if ai:
        print('✅ DeepSeek 调用成功')
        return ai
    print('⚠️ DeepSeek 调用失败，使用本地模板')
    return '\n'.join(template)


def chat_qa(question: str, context: str = '') -> str:
    """简洁的问答接口"""
    api_key = _get_deepseek_key()
    if api_key:
        print('🔍 正在调用 DeepSeek 回答问答...')
        out = _call_deepseek(f"Q: {question}\n上下文：{context}")
        if out:
            print('✅ DeepSeek 问答成功')
            return out

    q = question.lower()
    if '如何' in q or '怎样' in q:
        return '要提升核心技能，建议系统学习相关课程、实践项目并通过线上平台参与挑战。'
    if '工资' in q or '薪资' in q:
        return '薪资受地区、公司规模、经验影响，建议参考同行业招聘信息并结合自身技能评估。'
    return '这是一个很好的问题，建议您提供更多背景（例如兴趣、技能、期望行业），我可以给出更具体建议。'

# ==================== 以下是你新增的智谱 API 相关函数（已替换为阿里云百炼）====================
import json
import re
import time
from typing import Optional, Dict, Any, List, Tuple

# 阿里云百炼 SDK
import dashscope
from config import ALIYUN_API_KEY  # 需要在 config.py 中添加 ALIYUN_API_KEY

# 设置阿里云 API Key（全局设置）
dashscope.api_key = ALIYUN_API_KEY

def _call_zhipu(prompt: str, temperature=0.3, max_tokens=2000, thinking=False, max_retries=3) -> str:
    """
    调用阿里云百炼 qwen-plus 模型（已替换智谱）。
    内置重试机制，遇到速率限制时自动等待后重试。
    """
    for attempt in range(max_retries):
        try:
            # 阿里云百炼的生成调用
            response = dashscope.Generation.call(
                model='qwen-plus',          # 使用 qwen-plus，免费额度充足
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.7,
            )
            if response.status_code == 200:
                return response.output.text
            else:
                print(f"❌ 阿里云调用失败：{response.code} - {response.message}")
                # 如果是限流错误（429），等待后重试
                if "429" in str(response) or "throttling" in str(response).lower():
                    wait_time = (attempt + 1) * 5
                    print(f"⚠️ 触发限流，等待 {wait_time} 秒后重试 (尝试 {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    return ""
        except Exception as e:
            print(f"❌ 阿里云调用异常：{e}")
            if "429" in str(e) or "rate" in str(e).lower():
                wait_time = (attempt + 1) * 5
                print(f"⚠️ 触发限流，等待 {wait_time} 秒后重试 (尝试 {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                return ""
    print("❌ 阿里云调用重试耗尽，返回空字符串")
    return ""

# 如果你以后想切换回智谱，可以将上面的 _call_zhipu 替换为以下注释掉的代码：
# from zhipuai import ZhipuAI
# _zhipu_client = None
# def _get_zhipu_client():
#     global _zhipu_client
#     if _zhipu_client is None:
#         _zhipu_client = ZhipuAI(api_key=ZHIPU_API_KEY)
#     return _zhipu_client
# def _call_zhipu(prompt: str, temperature=0.3, max_tokens=2000, thinking=False, max_retries=3) -> str:
#     for attempt in range(max_retries):
#         try:
#             client = _get_zhipu_client()
#             params = {
#                 "model": "glm-4-flash",
#                 "messages": [{"role": "user", "content": prompt}],
#                 "temperature": temperature,
#                 "max_tokens": max_tokens,
#                 "top_p": 0.7,
#             }
#             if thinking:
#                 params["thinking"] = {"type": "enabled"}
#             response = client.chat.completions.create(**params)
#             return response.choices[0].message.content
#         except Exception as e:
#             error_str = str(e)
#             if "429" in error_str or "rate limit" in error_str.lower():
#                 wait_time = (attempt + 1) * 5
#                 print(f"⚠️ 智谱速率限制，等待 {wait_time} 秒后重试 (尝试 {attempt+1}/{max_retries})...")
#                 time.sleep(wait_time)
#             else:
#                 print(f"❌ 智谱 API 调用失败（非限流错误）：{e}")
#                 return ""
#     print("❌ 智谱 API 调用重试耗尽，返回空字符串")
#     return ""

# ---------- 分词相似度相关（用于分类） ----------
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("⚠️ 警告: jieba 未安装，将使用简单的子串匹配进行岗位分类，准确性可能较低。建议安装 jieba: pip install jieba")

def _calc_text_similarity(text1: str, text2: str) -> float:
    """计算两个文本的分词相似度（Jaccard相似度），若jieba不可用则回退到子串包含判断"""
    if not JIEBA_AVAILABLE:
        return 1.0 if text1 in text2 or text2 in text1 else 0.0
    words1 = set(jieba.cut(text1))
    words2 = set(jieba.cut(text2))
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)

# ---------- 技能合并辅助函数 ----------
def _merge_skills(skills_list: List[str]) -> List[str]:
    """
    对技能列表进行去重、合并同义词，返回标准化后的列表。
    同义词映射可根据实际数据扩展。
    """
    skill_alias = {
        "HTML5": "HTML",
        "CSS3": "CSS",
        "Vue3.0": "Vue",
        "Vue2": "Vue",
        "React.js": "React",
        "AngularJS": "Angular",
        "Angular2": "Angular",
        "Angular 2+": "Angular",
        "TypeScript": "TS",
        "Javascript": "JavaScript",
        "ES6": "JavaScript（ES6）",
        "ES2015": "JavaScript（ES6）",
        "Node.js": "NodeJS",
        "Express.js": "Express",
        "Mysql": "MySQL",
        "Sql Server": "SQL Server",
        "Photoshop": "PS",
        "Illustrator": "AI",
        "Figma": "Figma",
        "Sketch": "Sketch",
        "Axure RP": "Axure",
        # 可以继续添加
    }
    cleaned = []
    seen = set()
    for skill in skills_list:
        # 去除前后空格
        skill = skill.strip()
        if not skill:
            continue
        # 标准化
        normalized = skill_alias.get(skill, skill)
        # 去重
        if normalized not in seen:
            seen.add(normalized)
            cleaned.append(normalized)
    return cleaned

# ========== 第一步：自动聚类，生成大类（优化版） ==========
def cluster_categories_with_zhipu(sample_size: int = 500) -> List[Dict[str, Any]]:
    """
    从数据库中随机抽取 sample_size 条岗位数据（默认500），调用大模型分析，
    返回10-15个大类，每个大类包含名称和该大类下的职位名称列表。
    """
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT job_name, job_description FROM job
        WHERE job_description IS NOT NULL AND job_description != ''
        ORDER BY RANDOM() LIMIT ?
    """, (sample_size,))
    samples = cursor.fetchall()
    conn.close()

    if not samples:
        return []

    sample_text = ""
    for i, row in enumerate(samples, 1):
        desc = row['job_description'][:200] if row['job_description'] else "无描述"
        sample_text += f"{i}. 岗位名称：{row['job_name']}\n   岗位描述：{desc}...\n\n"

    prompt = f"""
你是一个职业分类专家。下面有{sample_size}条岗位数据样本（包含岗位名称和部分描述）。请根据这些岗位的核心技能和要求，将它们归纳为10-15个主要大类。
要求：
- 每个大类应有一个概括性的名称，例如“后端开发类”、“前端开发类”、“数据科学类”等。
- 每个大类下列出该大类包含的典型职位名称（从样本中观察到的，或归纳出的职位名称），列表应尽量完整，覆盖常见岗位变体。
- 返回严格的JSON格式，是一个数组，每个元素包含：
  {{
    "category_name": "大类名称",
    "job_titles": ["职位名称1", "职位名称2", ...]
  }}
- 确保大类数量在10-15之间。
- 只返回JSON，不要其他文字。

样本数据：
{sample_text}
"""
    for attempt in range(2):
        result = _call_zhipu(prompt, temperature=0.2, max_tokens=4000)
        if not result:
            continue
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        try:
            categories = json.loads(result)
            if isinstance(categories, list):
                return categories
            else:
                print(f"返回的JSON不是数组，尝试重试...")
        except Exception as e:
            print(f"解析聚类结果失败（尝试 {attempt+1}）：{e}")
    return []

# ========== 第二步：为每个岗位分配大类（基于分词相似度） ==========
def assign_categories_by_keywords(category_job_titles_map: Dict[str, List[str]], similarity_threshold: float = 0.3):
    """
    根据聚类得到的大类-职位名称映射，为job表中的每个岗位分配category_id。
    使用分词相似度计算岗位名称与职位标题的匹配程度，选择相似度最高的类别。
    如果没有匹配（最高相似度 < threshold），则category_id保持NULL。
    """
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()

    # 获取所有大类ID和名称
    cursor.execute("SELECT id, name FROM job_categories")
    cat_id_map = {row['name']: row['id'] for row in cursor.fetchall()}

    # 获取所有未分类的岗位
    cursor.execute("SELECT rowid, job_name FROM job WHERE category_id IS NULL")
    jobs = cursor.fetchall()
    count = 0
    for job in jobs:
        job_id = job['rowid']
        job_name = job['job_name']
        best_cat_id = None
        best_score = 0.0
        for cat_name, titles in category_job_titles_map.items():
            for title in titles:
                if not title:
                    continue
                score = _calc_text_similarity(job_name, title)
                if score > best_score:
                    best_score = score
                    best_cat_id = cat_id_map.get(cat_name)
        if best_score >= similarity_threshold and best_cat_id:
            cursor.execute("UPDATE job SET category_id = ? WHERE rowid = ?", (best_cat_id, job_id))
            conn.commit()
            count += 1
    conn.close()
    return count

# ========== 第三步：为每个大类生成通用画像（优化版） ==========
# ========== 第三步：为每个大类生成通用画像（优化版） ==========
def generate_category_profile_with_zhipu(category_id: int) -> bool:
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM job_categories WHERE id = ?", (category_id,))
    cat = cursor.fetchone()
    if not cat:
        conn.close()
        return False
    category_name = cat['name']

    # 随机抽取50条描述（提高代表性）
    cursor.execute(
        "SELECT job_description FROM job WHERE category_id = ? AND job_description IS NOT NULL ORDER BY RANDOM() LIMIT 50",
        (category_id,)
    )
    descs = [row['job_description'] for row in cursor.fetchall() if row['job_description']]
    if not descs:
        conn.close()
        return False

    combined = "\n---\n".join(descs)
    prompt = f"""
你是一个职业分析师。请根据以下属于"{category_name}"的多个岗位描述，提炼该大类岗位的通用画像。
要求返回严格的JSON格式，包含：
- skills：技能列表，**请合并相似技能**（例如 HTML 和 HTML5 合并为 HTML，Vue 和 Vue3.0 合并为 Vue），并按重要性或出现频率排序。如果可能，请按类别组织技能（例如基础技术、框架与库、工具与工程化、数据库等），但最终仍以字符串列表形式返回（可在技能名称后加括号注明分类，如“HTML（基础技术）”），或者直接返回列表即可。
- certificates：常见证书要求（字符串数组）。
- soft_abilities：软实力要求，对象形式，键为软能力名称，值为包含 `score`（1-5分）和 `description`（详细描述该能力在岗位中的具体体现）的对象。
  请根据岗位描述提炼出最相关的软能力，至少应包含创新能力、学习能力、抗压能力、沟通能力、实习能力（如果这些能力在描述中有体现，请给出评分和描述；如果某个能力完全未提及，可给出默认值，但鼓励根据上下文推断）。你也可以补充其他你认为重要的软能力。
  例如：{{"沟通能力": {{"score": 4, "description": "需要与产品、开发、测试等多方沟通，协调需求和进度，因此要求较强的沟通协作能力。"}}}}

注意：技能列表应聚焦于本大类核心岗位的常见要求，避免包含明显无关领域的技能（如后端数据库、GIS开发等，除非描述中反复强调）。

岗位描述：
{combined}

只返回JSON，不要其他文字。
"""
    for attempt in range(2):
        result = _call_zhipu(prompt, temperature=0.3, max_tokens=4000)
        if not result:
            continue
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        try:
            data = json.loads(result)
            # 处理技能列表：合并去重
            if "skills" in data and isinstance(data["skills"], list):
                data["skills"] = _merge_skills(data["skills"])
            # 处理证书列表：去重
            if "certificates" in data and isinstance(data["certificates"], list):
                data["certificates"] = list(dict.fromkeys(data["certificates"]))
            # 确保 soft_abilities 是字典
            if "soft_abilities" not in data or not isinstance(data["soft_abilities"], dict):
                data["soft_abilities"] = {}
            required = ["创新能力", "学习能力", "抗压能力", "沟通能力", "实习能力"]
            for dim in required:
                if dim not in data["soft_abilities"]:
                    data["soft_abilities"][dim] = {
                        "score": 3,
                        "description": f"根据岗位描述，{dim}是该类岗位常见要求，但未明确提及，给予中等评分。"
                    }
                else:
                    val = data["soft_abilities"][dim]
                    if isinstance(val, (int, float)):
                        data["soft_abilities"][dim] = {
                            "score": int(val),
                            "description": f"{dim}是岗位重要能力。"
                        }
                    elif isinstance(val, dict) and "score" not in val:
                        data["soft_abilities"][dim] = {
                            "score": 3,
                            "description": str(val) if val else f"{dim}是岗位重要能力。"
                        }
            # 保存到数据库
            skills = json.dumps(data.get('skills', []), ensure_ascii=False)
            certificates = json.dumps(data.get('certificates', []), ensure_ascii=False)
            soft_abilities = json.dumps(data.get('soft_abilities', {}), ensure_ascii=False)

            cursor.execute("""
                UPDATE job_categories
                SET skills = ?, certificates = ?, soft_abilities = ?
                WHERE id = ?
            """, (skills, certificates, soft_abilities, category_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"生成大类画像JSON解析失败（尝试 {attempt+1}）：{e}")
    conn.close()
    return False

# ========== 第四步：动态生成长尾岗位画像（优化版） ==========
def generate_dynamic_job_profile(job_name: str) -> Optional[Dict[str, Any]]:
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. 检查是否已存在该岗位的单独画像
    cursor.execute("SELECT job_name FROM job_profile WHERE job_name = ?", (job_name,))
    if cursor.fetchone():
        print(f"⚠️ {job_name} 已有单独画像，跳过")
        conn.close()
        return None  # 已存在，不再生成
    
    # 2. 随机抽取10条描述
    cursor.execute(
        "SELECT job_description FROM job WHERE job_name LIKE ? AND job_description IS NOT NULL ORDER BY RANDOM() LIMIT 10",
        (f'%{job_name}%',)
    )
    descs = [row['job_description'] for row in cursor.fetchall() if row['job_description']]
    if not descs:
        print(f"❌ {job_name} 无相关描述，无法生成画像")
        conn.close()
        return None

    # 3. 构造提示词，调用大模型
    combined = "\n---\n".join(descs)
    prompt = f"""
你是一个职业分析师。请根据以下岗位名称和描述，为该岗位生成画像。
岗位名称：{job_name}
描述：
{combined}

要求返回严格的JSON格式，包含：
- skills：必备技能列表，**请合并相似技能**（例如 HTML 和 HTML5 合并为 HTML，Vue 和 Vue3.0 合并为 Vue），并按重要性或出现频率排序。
- certificates：常见证书列表（字符串数组）。
- soft_abilities：软实力要求，对象形式，键为软能力名称，值为包含 `score`（1-5分）和 `description`（详细描述该能力在岗位中的具体体现）的对象。
  请根据描述提炼出最相关的软能力，至少应包含创新能力、学习能力、抗压能力、沟通能力、实习能力（如果这些能力在描述中有体现，请给出评分和描述；如果某个能力完全未提及，可给出默认值，但鼓励根据上下文推断）。你也可以补充其他你认为重要的软能力。
  例如：{{"沟通能力": {{"score": 4, "description": "需要与产品、开发、测试等多方沟通，协调需求和进度，因此要求较强的沟通协作能力。"}}}}

只返回JSON，不要其他文字。
"""
    for attempt in range(2):
        result = _call_zhipu(prompt, temperature=0.3, max_tokens=3000)
        if not result:
            continue
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        try:
            data = json.loads(result)
            # 处理技能列表：合并去重
            if "skills" in data and isinstance(data["skills"], list):
                data["skills"] = _merge_skills(data["skills"])
            # 处理证书列表：去重
            if "certificates" in data and isinstance(data["certificates"], list):
                data["certificates"] = list(dict.fromkeys(data["certificates"]))
            # 确保 soft_abilities 是字典
            if "soft_abilities" not in data or not isinstance(data["soft_abilities"], dict):
                data["soft_abilities"] = {}
            required = ["创新能力", "学习能力", "抗压能力", "沟通能力", "实习能力"]
            for dim in required:
                if dim not in data["soft_abilities"]:
                    data["soft_abilities"][dim] = {
                        "score": 3,
                        "description": f"根据岗位描述，{dim}是该岗位常见要求，但未明确提及，给予中等评分。"
                    }
                else:
                    val = data["soft_abilities"][dim]
                    if isinstance(val, (int, float)):
                        data["soft_abilities"][dim] = {
                            "score": int(val),
                            "description": f"{dim}是岗位重要能力。"
                        }
                    elif isinstance(val, dict) and "score" not in val:
                        data["soft_abilities"][dim] = {
                            "score": 3,
                            "description": str(val) if val else f"{dim}是岗位重要能力。"
                        }
            # ========== 插入数据库 ==========
            cursor.execute('''
                INSERT INTO job_profile (job_name, skills, certificates, soft_abilities)
                VALUES (?, ?, ?, ?)
            ''', (
                job_name,
                json.dumps(data.get('skills', []), ensure_ascii=False),
                json.dumps(data.get('certificates', []), ensure_ascii=False),
                json.dumps(data.get('soft_abilities', {}), ensure_ascii=False)
            ))
            conn.commit()
            print(f"✅ {job_name} 画像已存入数据库")
            conn.close()
            return data
        except Exception as e:
            print(f"动态画像生成JSON解析失败（尝试 {attempt+1}）：{e}")
    conn.close()
    return None

# ========== 岗位图谱构建相关（修改部分以满足要求） ==========
import re
from collections import defaultdict
from typing import List, Tuple

# 级别关键词及顺序（值越大级别越高）
LEVEL_KEYWORDS = {
    "实习": 0,
    "初级": 1,
    "中级": 2,
    "高级": 3,
    "资深": 4,
    "专家": 5,
    "架构师": 6,
    "经理": 7,
    "总监": 8,
    "首席": 9,
}

def extract_level(job_title: str) -> int:
    """从岗位名称中提取级别分数，返回最高匹配级别（0表示无级别）"""
    title_lower = job_title.lower()
    max_level = 0
    for kw, level in LEVEL_KEYWORDS.items():
        if kw in title_lower:
            if level > max_level:
                max_level = level
    return max_level

def extract_base_job(job_title: str) -> str:
    """去除岗位名称中的级别关键词，返回基础职位名（用于分组）"""
    base = job_title
    for kw in LEVEL_KEYWORDS.keys():
        base = base.replace(kw, "").strip()
    # 去除多余空格
    base = re.sub(r'\s+', ' ', base).strip()
    return base

def get_skill_similarity(job1: str, job2: str) -> float:
    """
    计算两个岗位的技能相似度（基于 job_profile 或 job_categories 中的技能列表）
    返回 0-1 之间的分数
    """
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    
    # 尝试从 job_profile 获取技能（更精确）
    cursor.execute("SELECT skills FROM job_profile WHERE job_name = ?", (job1,))
    row1 = cursor.fetchone()
    cursor.execute("SELECT skills FROM job_profile WHERE job_name = ?", (job2,))
    row2 = cursor.fetchone()
    
    # 如果都没有单独画像，尝试从所属大类获取技能
    if not row1 or not row2:
        # 获取岗位的 category_id
        cursor.execute("SELECT category_id FROM job WHERE job_name = ? LIMIT 1", (job1,))
        cat1 = cursor.fetchone()
        cursor.execute("SELECT category_id FROM job WHERE job_name = ? LIMIT 1", (job2,))
        cat2 = cursor.fetchone()
        if cat1 and cat1['category_id'] and cat2 and cat2['category_id']:
            cursor.execute("SELECT skills FROM job_categories WHERE id = ?", (cat1['category_id'],))
            row1 = cursor.fetchone()
            cursor.execute("SELECT skills FROM job_categories WHERE id = ?", (cat2['category_id'],))
            row2 = cursor.fetchone()
    
    conn.close()
    
    if not row1 or not row2:
        return 0.0
    
    try:
        skills1 = set(json.loads(row1['skills']) if row1['skills'] else [])
        skills2 = set(json.loads(row2['skills']) if row2['skills'] else [])
    except:
        return 0.0
    
    if not skills1 or not skills2:
        return 0.0
    
    intersection = skills1 & skills2
    union = skills1 | skills2
    return len(intersection) / len(union)

def get_job_skills(job_name: str) -> List[str]:
    """
    根据岗位名称获取技能列表（优先从 job_profile 获取，若没有则从所属大类获取）
    """
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    
    # 尝试从 job_profile 获取
    cursor.execute("SELECT skills FROM job_profile WHERE job_name = ?", (job_name,))
    row = cursor.fetchone()
    if row and row['skills']:
        try:
            skills = json.loads(row['skills'])
            conn.close()
            return skills if isinstance(skills, list) else []
        except:
            pass
    
    # 如果没有单独画像，获取所属大类
    cursor.execute("SELECT category_id FROM job WHERE job_name = ? LIMIT 1", (job_name,))
    cat_row = cursor.fetchone()
    if cat_row and cat_row['category_id']:
        cursor.execute("SELECT skills FROM job_categories WHERE id = ?", (cat_row['category_id'],))
        cat_skills = cursor.fetchone()
        if cat_skills and cat_skills['skills']:
            try:
                skills = json.loads(cat_skills['skills'])
                conn.close()
                return skills if isinstance(skills, list) else []
            except:
                pass
    conn.close()
    return []

# ---------- 垂直路径生成（基于级别分组，并添加具体技能描述） ----------
def build_vertical_paths() -> List[Tuple[str, str, str, str]]:
    """
    构建垂直晋升路径（基于岗位名称中的级别关键词），每个路径描述包含目标岗位所需技能。
    """
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT job_name FROM job")
    rows = cursor.fetchall()
    all_jobs = [row['job_name'] for row in rows]
    
    groups = defaultdict(list)
    for job in all_jobs:
        base = extract_base_job(job)
        level = extract_level(job)
        groups[base].append((job, level))
    
    relations = []
    for base, jobs_with_level in groups.items():
        if len(jobs_with_level) < 2:
            continue
        sorted_jobs = sorted(jobs_with_level, key=lambda x: x[1])
        for i in range(len(sorted_jobs)-1):
            from_job = sorted_jobs[i][0]
            to_job = sorted_jobs[i+1][0]
            if sorted_jobs[i][1] == sorted_jobs[i+1][1]:
                continue
            # 获取目标岗位技能
            skills = get_job_skills(to_job)
            skills_desc = "、".join(skills[:5]) if skills else ""
            if skills_desc:
                desc = f"晋升路径：从 {from_job} 到 {to_job}，需要掌握 {skills_desc} 等核心技能。"
            else:
                desc = f"晋升路径：从 {from_job} 到 {to_job}，需要提升技术深度和管理能力。"
            relations.append((from_job, to_job, 'promotion', desc))
    
    conn.close()
    return relations

# ---------- 垂直路径生成（使用大模型，并添加具体技能描述） ----------
def build_vertical_paths_using_llm() -> List[Tuple[str, str, str, str]]:
    """
    使用大模型为部分核心岗位生成晋升路径，每条路径描述包含目标岗位所需技能。
    """
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT job_name, COUNT(*) as cnt FROM job 
        GROUP BY job_name 
        ORDER BY cnt DESC 
        LIMIT 15
    """)
    core_jobs = [row['job_name'] for row in cursor.fetchall()]
    conn.close()

    relations = []
    for job in core_jobs:
        prompt = f"请根据行业常识，列举{job}可能的职业晋升路径（直接上级岗位名称），最多3个，以JSON数组形式返回，如['高级{job}', '{job}经理', '技术总监']。只返回数组，不要其他文字。"
        result = _call_zhipu(prompt, temperature=0.3, max_tokens=200)
        if not result:
            continue
        try:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)
            targets = json.loads(result)
            if isinstance(targets, list):
                for target in targets:
                    # 获取目标岗位技能
                    skills = get_job_skills(target)
                    skills_desc = "、".join(skills[:5]) if skills else ""
                    if skills_desc:
                        desc = f"晋升路径：从 {job} 到 {target}，需要掌握 {skills_desc} 等核心技能。"
                    else:
                        desc = f"晋升路径：从 {job} 到 {target}，需要提升技术深度和管理能力。"
                    relations.append((job, target, 'promotion', desc))
        except Exception as e:
            print(f"解析晋升路径失败 for {job}: {e}")
    return relations

# ---------- 横向路径生成（基于技能相似度，描述包含需要补充的技能） ----------
def build_lateral_paths(top_n: int = 25, min_paths: int = 2, similarity_threshold: float = 0.15) -> List[Tuple[str, str, str, str]]:
    """
    构建横向换岗路径：
    - 只考虑相似度 >= similarity_threshold 的岗位。
    - 为每个核心岗位选取相似度最高的 min_paths 条路径（如果不足则只返回实际数量）。
    - 路径描述中列出需要补充的具体技能（目标岗位有而源岗位没有的技能）。
    """
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT job_name, COUNT(*) as cnt FROM job 
        GROUP BY job_name 
        ORDER BY cnt DESC 
        LIMIT ?
    """, (top_n,))
    core_jobs = [row['job_name'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT job_name FROM job")
    all_jobs = [row['job_name'] for row in cursor.fetchall()]
    conn.close()
    
    relations = []
    for job in core_jobs:
        similarities = []
        for other in all_jobs:
            if other == job:
                continue
            sim = get_skill_similarity(job, other)
            if sim >= similarity_threshold:
                similarities.append((other, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        selected = similarities[:min_paths]
        
        for to_job, sim in selected:
            # 获取源岗位和目标岗位的技能集合
            from_skills = set(get_job_skills(job))
            to_skills = set(get_job_skills(to_job))
            
            # 需要补充的技能 = 目标岗位有而源岗位没有
            need_skills = to_skills - from_skills
            
            if need_skills:
                skills_list = list(need_skills)[:5]
                skills_desc = "、".join(skills_list)
                if len(need_skills) > 5:
                    skills_desc += "等"
                desc = f"可考虑换岗至 {to_job}，需补充 {skills_desc} 技能。"
            else:
                desc = f"可考虑换岗至 {to_job}，技能匹配度高，建议深入了解岗位实际需求。"
            
            relations.append((job, to_job, 'transition', desc))
    
    return relations

# ---------- 重建岗位图谱 ----------
def rebuild_job_graph() -> Tuple[int, int]:
    """
    重建岗位图谱：清空 job_relations，然后重新插入垂直晋升和横向换岗路径。
    返回 (垂直路径数量, 横向路径数量)
    """
    from db import get_db
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM job_relations")
    
    # 使用大模型生成垂直路径（也可以使用基于级别的 build_vertical_paths，但大模型更灵活）
    vertical = build_vertical_paths_using_llm()
    for rel in vertical:
        cursor.execute("""
            INSERT INTO job_relations (from_job, to_job, relation_type, description)
            VALUES (?, ?, ?, ?)
        """, rel)
    
    # 构建横向路径：阈值0.3，确保每个核心岗位至少2条（如果不足则只取实际数量）
    lateral = build_lateral_paths(top_n=25, min_paths=2, similarity_threshold=0.15)
    for rel in lateral:
        cursor.execute("""
            INSERT INTO job_relations (from_job, to_job, relation_type, description)
            VALUES (?, ?, ?, ?)
        """, rel)
    
    conn.commit()
    conn.close()
    return len(vertical), len(lateral)
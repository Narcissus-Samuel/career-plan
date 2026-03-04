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
from backend.algorithms import recommend_jobs, compute_match_score

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
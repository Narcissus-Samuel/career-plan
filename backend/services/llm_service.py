"""
services/llm_service.py

提供与职业规划相关的“大模型”接口实现（本地启发式 + 可选调用外部 API 的包装）

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

# 改成 DeepSeek 的 key
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_API_KEY')

def _call_deepseek(prompt: str) -> str:
    """如果配置了 DEEPSEEK_API_KEY，则调用 DeepSeek API，否则返回空字符串。"""
    if not DEEPSEEK_KEY:
        return ''
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=DEEPSEEK_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        resp = client.chat.completions.create(
            model='deepseek-chat',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=600
        )
        return resp.choices[0].message.content
    except Exception as e:
        print('deepseek call failed', e)
        return ''


def parse_resume(file_path: str) -> Dict[str, Any]:
    """解析简历（演示版）：
    - 支持 txt/简单文本或返回模拟结构
    返回结构化学生信息字典，包含 skills, certificates, internships, interests, completeness, competitiveness
    """
    try:
        _, ext = os.path.splitext(file_path.lower())
        if ext in ('.txt', '.md'):
            with open(file_path, 'r', encoding='utf-8') as f:
                txt = f.read()
            # 简单关键词抽取：查找技能行（以 Skills: 开头）
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

    # fallback mock
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
    """返回推荐岗位列表以及每个岗位的匹配详情。"""
    recs = recommend_jobs(student, jobs, top_n)
    # 转换为可序列化结构
    out = []
    for job, detail in recs:
        item = {
            'job': job,
            'match': detail
        }
        out.append(item)
    return out


def generate_plan_suggestion(student: Dict[str, Any], job_name: str) -> str:
    """基于学生信息生成规划建议文本（模板 + 可选大模型增强）"""
    template = []
    template.append(f"目标岗位：{job_name}")
    template.append("总体建议：")
    template.append("1. 技能提升：根据岗位需求补齐关键技能，例如掌握相关框架与工具。")
    template.append("2. 项目经验：建议完成至少1-2个相关项目，展示端到端能力。")
    template.append("3. 简历优化：将关键技能与项目成果量化展示，突出业绩与指标。")
    template.append("4. 面试准备：整理常见技术问题与行为问题的回答要点。")

    prompt = '\n'.join(template) + '\n\n学生信息：' + json.dumps(student, ensure_ascii=False)
    ai = _call_deepseek(prompt)
    if ai:
        return ai
    return '\n'.join(template)


def chat_qa(question: str, context: str = '') -> str:
    """简洁的问答接口：若配置大模型，调用之；否则用规则回复。"""
    if DEEPSEEK_KEY:
        out = _call_deepseek(f"Q: {question}\n上下文：{context}")
        if out:
            return out

    # 简单规则示例
    q = question.lower()
    if '如何' in q or '怎样' in q:
        return '要提升核心技能，建议系统学习相关课程、实践项目并通过线上平台参与挑战。'
    if '工资' in q or '薪资' in q:
        return '薪资受地区、公司规模、经验影响，建议参考同行业招聘信息并结合自身技能评估。'
    return '这是一个很好的问题，建议您提供更多背景（例如兴趣、技能、期望行业），我可以给出更具体建议。'
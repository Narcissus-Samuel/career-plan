"""
算法模块：职业匹配、推荐与评分

实现说明：
- 基于技能重叠度和兴趣匹配的简单启发式算法
- 提供可单元测试的函数：compute_match_score, recommend_jobs, score_student_competitiveness
"""
from typing import List, Dict, Any, Tuple
import math
import json


def _list_from_json(maybe_json):
    if maybe_json is None:
        return []
    if isinstance(maybe_json, list):
        return maybe_json
    try:
        return json.loads(maybe_json)
    except Exception:
        # assume comma-separated
        return [s.strip() for s in str(maybe_json).split(',') if s.strip()]


def compute_match_score(student: Dict[str, Any], job_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算学生与岗位画像的匹配分：
    - 技能匹配（权重0.6）：学生技能与岗位技能交集比
    - 兴趣匹配（权重0.2）：学生兴趣与岗位名称/行业包含的相关关键词
    - 软技能匹配（权重0.2）：基于岗位画像中 soft_abilities 与学生 competitiveness
    返回字典包含 overall_score 与各维度分数。
    """
    stu_skills = set([s.lower() for s in _list_from_json(student.get('skills'))])
    job_skills = set([s.lower() for s in _list_from_json(job_profile.get('skills'))])

    skill_overlap = len(stu_skills & job_skills)
    skill_score = 0.0
    if job_skills:
        skill_score = skill_overlap / max(len(job_skills), 1)

    # interest match（关键词包含）
    interests = [i.lower() for i in _list_from_json(student.get('interests'))]
    interest_score = 0.0
    if interests:
        name = (job_profile.get('job_name') or '').lower()
        industry = (job_profile.get('industry') or '') if isinstance(job_profile.get('industry'), str) else ''
        text = name + ' ' + industry
        match_count = sum(1 for it in interests if it in text)
        interest_score = min(1.0, match_count / len(interests))

    # soft abilities vs competitiveness
    soft = job_profile.get('soft_abilities') or {}
    if isinstance(soft, str):
        try:
            soft = json.loads(soft)
        except Exception:
            soft = {}
    avg_soft_req = 0.0
    if soft:
        vals = [v for v in soft.values() if isinstance(v, (int, float))]
        if vals:
            avg_soft_req = sum(vals) / (len(vals) * 100.0)  # 归一化到0-1

    competitiveness = (student.get('competitiveness') or 50) / 100.0
    soft_score = 1.0 - abs(competitiveness - avg_soft_req)
    soft_score = max(0.0, min(1.0, soft_score))

    w_skill = 0.6
    w_interest = 0.2
    w_soft = 0.2
    overall = skill_score * w_skill + interest_score * w_interest + soft_score * w_soft

    return {
        'overall_score': round(overall, 4),
        'skill_score': round(skill_score, 4),
        'interest_score': round(interest_score, 4),
        'soft_score': round(soft_score, 4),
        'skill_overlap': list(stu_skills & job_skills),
    }


def recommend_jobs(student: Dict[str, Any], jobs: List[Dict[str, Any]], top_n: int = 5) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    给定学生信息和岗位列表，返回按匹配分排序的前 top_n 个岗位及匹配详情
    返回列表元素为 (job, match_detail)
    """
    scored = []
    for job in jobs:
        # job_profile may be merged; ensure fields exist
        job_profile = {
            'job_name': job.get('job_name') or job.get('jobName') or '',
            'skills': job.get('skills') or job.get('required_skills') or [],
            'industry': job.get('industry') or job.get('company') or '',
            'soft_abilities': job.get('soft_abilities') or {}
        }
        score = compute_match_score(student, job_profile)
        scored.append((job, score))
    scored.sort(key=lambda t: t[1]['overall_score'], reverse=True)
    return scored[:top_n]


def score_student_competitiveness(student: Dict[str, Any]) -> int:
    """
    根据简历信息给出一个 0-100 的竞争力评分（启发式）：
    - 技能数量、证书、实习经验数量、完整度都参与计算
    """
    skills = _list_from_json(student.get('skills'))
    certs = _list_from_json(student.get('certificates'))
    internships = student.get('internships')
    completeness = student.get('completeness') or 50

    score = 40.0
    score += min(30, len(skills) * 3)
    score += min(15, len(certs) * 2)
    if internships:
        score += 10
    score += (completeness / 100.0) * 5

    score = max(0, min(100, int(score)))
    return score


if __name__ == '__main__':
    # 简单自测
    student = {'skills': ['python', 'django'], 'interests': ['后端'], 'competitiveness': 70}
    jobs = [{'job_name': '后端开发工程师', 'skills': ['python', 'flask'], 'industry': '软件'}]
    print(recommend_jobs(student, jobs))

"""
深度学习模型模块
包含岗位匹配度预测模型和岗位向量化模型
"""

from .matching_model import SiameseMatchingNet, TextProcessor, MatchingPredictor
from .job2vec_model import Job2Vec, JobPathRecommender

__all__ = [
    'SiameseMatchingNet',
    'TextProcessor', 
    'MatchingPredictor',
    'Job2Vec',
    'JobPathRecommender'
]
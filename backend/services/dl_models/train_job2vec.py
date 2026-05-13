"""
训练岗位向量化模型（Word2Vec）
从数据库中的学生工作经历提取职位序列
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

from db import get_db
from services.dl_models.job2vec_model import Job2Vec

def extract_job_sequences_from_db():
    """从 student 表的 work_json 字段提取职位序列"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT work_json FROM student WHERE work_json IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    
    sequences = []
    for row in rows:
        try:
            work_json = json.loads(row['work_json'])
            if isinstance(work_json, list):
                for exp in work_json:
                    if isinstance(exp, dict) and 'position' in exp:
                        # 一个学生可能有多段经历，每段是一个序列元素
                        # 为了训练序列关系，我们将同一学生的职位按时间顺序排列
                        pass
                # 更合理的：按时间顺序提取该学生的所有职位
                positions = []
                for exp in sorted(work_json, key=lambda x: x.get('date_range', '')):
                    pos = exp.get('position', '')
                    if pos:
                        positions.append(pos)
                if len(positions) >= 2:
                    sequences.append(positions)
        except:
            continue
    
    # 也可以从 job_relations 表中提取路径作为辅助训练数据
    cursor = get_db().cursor()
    cursor.execute("SELECT from_job, to_job, relation_type FROM job_relations")
    relations = cursor.fetchall()
    for rel in relations:
        sequences.append([rel['from_job'], rel['to_job']])
    
    print(f"✅ 提取到 {len(sequences)} 条职位序列")
    return sequences

def train():
    os.makedirs('data/models', exist_ok=True)
    os.makedirs('data/plots', exist_ok=True)
    
    # 1. 提取序列
    sequences = extract_job_sequences_from_db()
    if not sequences:
        print("⚠️ 没有足够的职位序列数据，使用模拟数据演示")
        # 模拟数据
        sequences = [
            ['实习工程师', '初级工程师', '中级工程师', '高级工程师'],
            ['初级工程师', '中级工程师', '高级工程师', '技术专家'],
            ['产品助理', '产品经理', '高级产品经理', '产品总监'],
            ['UI设计师', '高级UI设计师', '设计主管'],
            ['测试工程师', '高级测试工程师', '测试经理'],
            ['前端开发', '全栈开发', '技术经理'],
            ['后端开发', '架构师', '技术总监'],
            ['销售代表', '销售经理', '区域总监'],
            ['人力资源助理', 'HRBP', '人力资源总监'],
        ]
    
    # 2. 训练模型
    model = Job2Vec(embedding_dim=128, window_size=3, learning_rate=0.01)
    model.train(sequences, epochs=50, batch_size=16)
    
    # 3. 保存模型
    model.save('data/models/job2vec_model.pkl')
    print("✅ 模型保存至 data/models/job2vec_model.pkl")
    
    # 4. 可视化 t-SNE
    job_names = list(model.job2id.keys())[:50]  # 取前50个
    embeddings = np.array([model.embeddings[model.job2id[job]] for job in job_names])
    
    tsne = TSNE(n_components=2, random_state=42, perplexity=15)
    embeddings_2d = tsne.fit_transform(embeddings)
    
    plt.figure(figsize=(12, 8))
    for i, job in enumerate(job_names):
        plt.scatter(embeddings_2d[i, 0], embeddings_2d[i, 1], alpha=0.7)
        plt.annotate(job, (embeddings_2d[i, 0], embeddings_2d[i, 1]), fontsize=8)
    plt.title('Job Embeddings Visualization (t-SNE)', fontsize=14)
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.tight_layout()
    plt.savefig('data/plots/job_tsne.png', dpi=300)
    plt.close()
    print("✅ t-SNE图保存至 data/plots/job_tsne.png")
    
    # 5. 测试类比
    if '高级工程师' in model.job2id and '中级工程师' in model.job2id and '产品经理' in model.job2id:
        analogies = model.analogy('中级工程师', '高级工程师', '产品经理')
        print(f"  中级工程师 → 高级工程师 : 产品经理 → {analogies}")

if __name__ == '__main__':
    train()
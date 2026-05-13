"""
训练岗位-简历匹配度预测模型
从数据库提取数据，训练Siamese网络，生成图表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
import jieba
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import seaborn as sns
from datetime import datetime

from db import get_db
from services.dl_models.matching_model import SiameseMatchingNet, TextProcessor

# ==================== 数据准备 ====================
class MatchDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = texts
        self.labels = labels
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return {
            'resume': torch.tensor(self.texts[idx][0], dtype=torch.long),
            'job': torch.tensor(self.texts[idx][1], dtype=torch.long),
            'label': torch.tensor(self.labels[idx], dtype=torch.float32)
        }

def load_data_from_db():
    """从数据库加载正负样本"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. 正样本：从 match_history 中取匹配度高的记录
    cursor.execute("""
        SELECT m.job_name, m.match_score, s.skills, s.certificates, s.work_json, s.project_json, s.education_text
        FROM match_history m
        JOIN student s ON m.student_id = s.id
        WHERE m.match_score >= 80
        LIMIT 5000
    """)
    positive = cursor.fetchall()
    
    # 2. 负样本：随机组合（学生 + 不匹配的岗位）
    # 获取所有学生和岗位
    cursor.execute("SELECT id, skills, certificates, work_json, project_json, education_text FROM student")
    students = cursor.fetchall()
    cursor.execute("SELECT job_name, job_description FROM job LIMIT 2000")
    jobs = cursor.fetchall()
    
    import random
    negative = []
    for _ in range(len(positive)):
        stu = random.choice(students)
        job = random.choice(jobs)
        # 简单避免偶然正样本（可选）
        negative.append((stu, job))
    
    conn.close()
    
    # 构建文本
    positive_texts = []
    positive_labels = []
    for row in positive:
        resume_text = build_resume_text(row)
        job_text = row['job_name'] + " " + (row.get('job_description') or '')
        positive_texts.append((resume_text, job_text))
        positive_labels.append(1.0)
    
    negative_texts = []
    negative_labels = []
    for stu, job in negative:
        resume_text = build_resume_text(stu)
        job_text = job['job_name'] + " " + (job.get('job_description') or '')
        negative_texts.append((resume_text, job_text))
        negative_labels.append(0.0)
    
    all_texts = positive_texts + negative_texts
    all_labels = positive_labels + negative_labels
    
    print(f"✅ 数据加载完成：正样本 {len(positive_texts)}，负样本 {len(negative_texts)}")
    return all_texts, all_labels

def build_resume_text(row):
    """构建学生简历文本"""
    parts = []
    if row.get('skills'):
        parts.append(f"技能：{row['skills']}")
    if row.get('certificates'):
        parts.append(f"证书：{row['certificates']}")
    if row.get('work_json'):
        try:
            work = json.loads(row['work_json']) if isinstance(row['work_json'], str) else row['work_json']
            for exp in work[:3]:
                parts.append(f"工作经历：{exp.get('company','')} {exp.get('position','')} {exp.get('achievements','')}")
        except:
            pass
    if row.get('project_json'):
        try:
            proj = json.loads(row['project_json']) if isinstance(row['project_json'], str) else row['project_json']
            for p in proj[:3]:
                parts.append(f"项目：{p.get('project_name','')} {p.get('description','')}")
        except:
            pass
    if row.get('education_text'):
        parts.append(f"教育：{row['education_text']}")
    return " ".join(parts)

# ==================== 训练函数 ====================
def train():
    # 创建保存目录
    os.makedirs('data/models', exist_ok=True)
    os.makedirs('data/plots', exist_ok=True)
    os.makedirs('data/logs', exist_ok=True)
    
    # 1. 加载数据
    all_texts, all_labels = load_data_from_db()
    
    # 2. 构建词表
    processor = TextProcessor(vocab_size=10000, max_len=256)
    all_raw_texts = [t[0] + " " + t[1] for t in all_texts]
    processor.build_vocab(all_raw_texts)
    processor.save('data/models/text_processor.pkl')
    
    # 3. 转换为序列
    resume_seqs = []
    job_seqs = []
    for resume_text, job_text in all_texts:
        resume_seqs.append(processor.text_to_sequence(resume_text))
        job_seqs.append(processor.text_to_sequence(job_text))
    
    # 4. 划分训练/验证集
    from sklearn.model_selection import train_test_split
    X = list(zip(resume_seqs, job_seqs))
    X_train, X_val, y_train, y_val = train_test_split(X, all_labels, test_size=0.2, random_state=42)
    
    train_dataset = MatchDataset(X_train, y_train)
    val_dataset = MatchDataset(X_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)
    
    # 5. 模型、优化器、损失
    model = SiameseMatchingNet(vocab_size=len(processor.word2idx), embed_dim=128, hidden_dim=256)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    criterion = nn.MSELoss()  # 回归任务
    
    # 6. 训练循环
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': [], 'lr': []}
    best_val_loss = float('inf')
    
    for epoch in range(50):
        # 训练
        model.train()
        train_loss = 0
        train_preds, train_trues = [], []
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1} Train"):
            resume = batch['resume'].to(device)
            job = batch['job'].to(device)
            label = batch['label'].to(device).view(-1, 1)
            
            optimizer.zero_grad()
            pred = model(resume, job) / 100.0  # 归一化到0-1
            loss = criterion(pred, label)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            train_preds.extend((pred * 100).cpu().detach().numpy().flatten())
            train_trues.extend((label * 100).cpu().numpy().flatten())
        
        # 验证
        model.eval()
        val_loss = 0
        val_preds, val_trues = [], []
        with torch.no_grad():
            for batch in val_loader:
                resume = batch['resume'].to(device)
                job = batch['job'].to(device)
                label = batch['label'].to(device).view(-1, 1)
                pred = model(resume, job) / 100.0
                loss = criterion(pred, label)
                val_loss += loss.item()
                val_preds.extend((pred * 100).cpu().numpy().flatten())
                val_trues.extend((label * 100).cpu().numpy().flatten())
        
        # 计算准确率（误差<10分算正确）
        train_acc = np.mean([abs(p-t) < 10 for p,t in zip(train_preds, train_trues)]) * 100
        val_acc = np.mean([abs(p-t) < 10 for p,t in zip(val_preds, val_trues)]) * 100
        
        history['train_loss'].append(train_loss/len(train_loader))
        history['val_loss'].append(val_loss/len(val_loader))
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        history['lr'].append(optimizer.param_groups[0]['lr'])
        
        print(f"Epoch {epoch+1:3d} | Loss: {train_loss/len(train_loader):.4f}/{val_loss/len(val_loader):.4f} | Acc: {train_acc:.2f}%/{val_acc:.2f}%")
        
        scheduler.step(history['val_loss'][-1])
        
        # 保存最佳模型
        if history['val_loss'][-1] < best_val_loss:
            best_val_loss = history['val_loss'][-1]
            torch.save(model.state_dict(), 'data/models/matching_model_best.pth')
            print(f"  ✅ 保存最佳模型，验证Loss: {best_val_loss:.4f}")
    
    # 7. 生成图表（调用visualize模块）
    from services.dl_models.visualize import plot_training_history, plot_confusion_matrix_from_preds
    plot_training_history(history, save_path='data/plots/training_history.png')
    
    # 在验证集上绘制混淆矩阵
    plot_confusion_matrix_from_preds(val_trues, val_preds, threshold=70, save_path='data/plots/confusion_matrix.png')
    
    print("✅ 训练完成！模型保存在 data/models/matching_model_best.pth")
    print("✅ 图表保存在 data/plots/")

if __name__ == '__main__':
    train()
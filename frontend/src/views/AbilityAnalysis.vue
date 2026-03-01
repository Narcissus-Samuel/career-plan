<template>
  <div class="ability-analysis">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">能力短板分析</h1>
      <p class="page-desc">基于你的测评数据，精准识别职业能力短板，提供个性化提升方案</p>
      <div class="header-actions">
        <button class="btn-refresh" @click="refreshAnalysis">🔄 重新分析</button>
        <button class="btn-export" @click="exportReport">📤 导出分析报告</button>
      </div>
    </div>

    <!-- 数据概览卡片 -->
    <div class="overview-cards">
      <div class="overview-card">
        <div class="card-icon">📊</div>
        <div class="card-content">
          <div class="card-title">综合能力评分</div>
          <div class="card-value">{{ totalScore }}/100</div>
          <div class="card-desc">
            <span class="score-tag" :class="getScoreLevel(totalScore)">{{ getScoreLevelText(totalScore) }}</span>
          </div>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon">⚠️</div>
        <div class="card-content">
          <div class="card-title">核心短板数量</div>
          <div class="card-value">{{ shortageCount }}</div>
          <div class="card-desc">需重点提升的能力维度</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon">🎯</div>
        <div class="card-content">
          <div class="card-title">目标岗位匹配度</div>
          <div class="card-value">{{ matchRate }}%</div>
          <div class="card-desc">当前能力与目标岗位的匹配程度</div>
        </div>
      </div>
    </div>

    <!-- 能力维度雷达图 -->
    <div class="chart-section">
      <div class="chart-card">
        <h3 class="chart-title">能力维度雷达图</h3>
        <div class="chart-container">
          <canvas id="abilityRadarChart"></canvas>
        </div>
        <div class="chart-legend">
          <div class="legend-item">
            <span class="legend-color your-score"></span>
            <span class="legend-text">你的得分</span>
          </div>
          <div class="legend-item">
            <span class="legend-color target-score"></span>
            <span class="legend-text">目标岗位要求</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 短板详情列表 -->
    <div class="shortage-section">
      <h3 class="section-title">核心短板详情</h3>
      <div class="shortage-list">
        <div class="shortage-item" v-for="(item, index) in shortageList" :key="index">
          <div class="shortage-header">
            <div class="shortage-icon" :style="{ backgroundColor: item.color }">{{ item.icon }}</div>
            <div class="shortage-title">
              <h4>{{ item.name }}</h4>
              <span class="shortage-score">{{ item.score }}/100</span>
            </div>
          </div>
          <div class="shortage-desc">
            {{ item.description }}
          </div>
          <div class="shortage-suggestion">
            <h5>提升建议：</h5>
            <ul>
              <li v-for="(suggest, i) in item.suggestions" :key="i">{{ suggest }}</li>
            </ul>
          </div>
          <div class="shortage-actions">
            <button class="btn-learn" @click="goToLearning(item.name)">📚 立即学习</button>
            <button class="btn-plan" @click="createImprovePlan(item.name)">📋 制定提升计划</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 提升路径规划 -->
    <div class="improve-section">
      <h3 class="section-title">个性化提升路径</h3>
      <div class="improve-timeline">
        <div class="timeline-item" v-for="(item, index) in improveTimeline" :key="index">
          <div class="timeline-dot" :style="{ backgroundColor: item.color }"></div>
          <div class="timeline-content">
            <div class="timeline-period">{{ item.period }}</div>
            <div class="timeline-title">{{ item.title }}</div>
            <div class="timeline-tasks">
              <span class="task-tag" v-for="task in item.tasks" :key="task">{{ task }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 相关学习资源 -->
    <div class="resource-section">
      <h3 class="section-title">推荐学习资源</h3>
      <div class="resource-list">
        <div class="resource-card" v-for="(item, index) in resourceList" :key="index">
          <div class="resource-type" :style="{ backgroundColor: item.color }">{{ item.type }}</div>
          <div class="resource-content">
            <h4 class="resource-title">{{ item.title }}</h4>
            <p class="resource-desc">{{ item.description }}</p>
            <div class="resource-meta">
              <span class="meta-item">🕒 {{ item.duration }}</span>
              <span class="meta-item">⭐ {{ item.rating }}分</span>
            </div>
          </div>
          <button class="resource-btn" @click="goToResource(item.id)">查看详情</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto' // 引入Chart.js

// 初始化路由实例
const router = useRouter()

// 页面核心数据
const totalScore = ref(75) // 综合能力总分
const shortageCount = ref(3) // 核心短板数量
const matchRate = ref(78) // 目标岗位匹配度

// 能力维度数据（雷达图）
const abilityDimensions = ref([
  { name: '专业技能', yourScore: 80, targetScore: 90 },
  { name: '沟通表达', yourScore: 65, targetScore: 85 },
  { name: '逻辑思维', yourScore: 75, targetScore: 80 },
  { name: '团队协作', yourScore: 70, targetScore: 85 },
  { name: '学习能力', yourScore: 85, targetScore: 80 },
  { name: '抗压能力', yourScore: 60, targetScore: 80 },
  { name: '创新能力', yourScore: 70, targetScore: 85 }
])

// 核心短板列表
const shortageList = ref([
  {
    icon: '🗣️',
    name: '沟通表达能力',
    score: 65,
    color: '#ff7a45',
    description: '在团队协作和对外沟通场景中，表达不够清晰、简洁，难以快速传递核心信息，影响工作效率和协作效果。',
    suggestions: [
      '参加线下沟通技巧培训课程，每周进行1次模拟演讲练习',
      '阅读《非暴力沟通》《金字塔原理》等书籍，学习结构化表达',
      '主动承担团队汇报、跨部门沟通的任务，积累实战经验',
      '录制自己的沟通场景视频，复盘并优化表达逻辑'
    ]
  },
  {
    icon: '💪',
    name: '抗压能力',
    score: 60,
    color: '#faad14',
    description: '面对紧急任务、多任务并行或负面反馈时，容易产生焦虑情绪，影响决策效率和执行质量。',
    suggestions: [
      '学习时间管理方法（如番茄工作法），合理拆分任务降低压力',
      '培养运动、冥想等放松习惯，每周至少3次，每次30分钟以上',
      '建立情绪日记，记录压力来源并分析应对策略',
      '主动挑战有难度的任务，逐步提升心理承受能力'
    ]
  },
  {
    icon: '✨',
    name: '创新能力',
    score: 70,
    color: '#52c41a',
    description: '在解决问题时倾向于使用传统方法，缺乏多角度思考和创新解决方案，难以在竞争中形成差异化优势。',
    suggestions: [
      '定期浏览行业前沿资讯，每周学习1个新的思维模型（如六顶思考帽）',
      '参加创新工作坊或头脑风暴活动，锻炼发散思维',
      '尝试用跨界思维解决现有问题，记录创新想法并落地验证',
      '学习设计思维，从用户需求出发重构解决方案'
    ]
  }
])

// 提升路径时间线
const improveTimeline = ref([
  {
    period: '1-2个月',
    title: '基础能力提升',
    color: '#1890ff',
    tasks: ['沟通技巧入门', '压力管理基础', '创新思维启蒙']
  },
  {
    period: '3-4个月',
    title: '实战应用阶段',
    color: '#52c41a',
    tasks: ['团队沟通实战', '高压场景模拟', '创新方案落地']
  },
  {
    period: '5-6个月',
    title: '能力固化阶段',
    color: '#faad14',
    tasks: ['沟通习惯养成', '抗压能力强化', '创新思维内化']
  },
  {
    period: '7-8个月',
    title: '能力突破阶段',
    color: '#ff7a45',
    tasks: ['高阶沟通技巧', '极端压力应对', '创新方法论构建']
  }
])

// 推荐学习资源
const resourceList = ref([
  {
    id: 1,
    type: '课程',
    color: '#1890ff',
    title: '高效沟通表达实战课',
    description: '从表达逻辑、肢体语言、倾听技巧等维度，全面提升沟通能力，适合职场新人。',
    duration: '12小时',
    rating: 4.8
  },
  {
    id: 2,
    type: '书籍',
    color: '#52c41a',
    title: '抗压能力：从焦虑到从容',
    description: '结合心理学和实战案例，教你如何识别压力源、调整心态、提升心理韧性。',
    duration: '3小时/章',
    rating: 4.7
  },
  {
    id: 3,
    type: '训练营',
    color: '#faad14',
    title: '创新思维30天训练营',
    description: '通过每日打卡、实战任务、导师点评，系统培养创新思维和解决问题的能力。',
    duration: '30天',
    rating: 4.9
  },
  {
    id: 4,
    type: '直播',
    color: '#ff7a45',
    title: '职场沟通与压力管理专场',
    description: '行业大咖分享实战经验，实时解答沟通和抗压相关问题。',
    duration: '2小时',
    rating: 4.6
  }
])

// 获取分数等级
const getScoreLevel = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'normal'
  if (score >= 60) return 'poor'
  return 'very-poor'
}

// 获取分数等级文本
const getScoreLevelText = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '待提升'
  return '急需提升'
}

// 初始化雷达图
const initRadarChart = () => {
  const ctx = document.getElementById('abilityRadarChart').getContext('2d')
  
  // 提取雷达图数据
  const labels = abilityDimensions.value.map(item => item.name)
  const yourScores = abilityDimensions.value.map(item => item.yourScore)
  const targetScores = abilityDimensions.value.map(item => item.targetScore)

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: '你的得分',
          data: yourScores,
          backgroundColor: 'rgba(24, 144, 255, 0.2)',
          borderColor: 'rgba(24, 144, 255, 1)',
          pointBackgroundColor: 'rgba(24, 144, 255, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(24, 144, 255, 1)'
        },
        {
          label: '目标岗位要求',
          data: targetScores,
          backgroundColor: 'rgba(82, 196, 26, 0.2)',
          borderColor: 'rgba(82, 196, 26, 1)',
          pointBackgroundColor: 'rgba(82, 196, 26, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(82, 196, 26, 1)'
        }
      ]
    },
    options: {
      elements: {
        line: {
          borderWidth: 2
        }
      },
      scales: {
        r: {
          angleLines: {
            display: true
          },
          suggestedMin: 0,
          suggestedMax: 100
        }
      }
    }
  })
}

// 重新分析
const refreshAnalysis = () => {
  // 模拟重新分析（实际项目中可调用后端接口）
  alert('正在重新分析你的能力数据，请稍候...')
  // 随机更新部分数据（仅演示）
  totalScore.value = Math.floor(Math.random() * 20) + 70
  matchRate.value = Math.floor(Math.random() * 15) + 70
}

// 导出报告
const exportReport = () => {
  alert('能力短板分析报告正在导出为PDF格式，请稍候...')
  // 实际项目中可调用导出接口或前端生成PDF
}

// 跳转到学习页面
const goToLearning = (abilityName) => {
  router.push({ 
    path: '/resource-library', 
    query: { keyword: abilityName } 
  })
}

// 制定提升计划
const createImprovePlan = (abilityName) => {
  router.push({
    path: '/career-planning',
    query: { focus: abilityName }
  })
}

// 跳转到资源详情
const goToResource = (id) => {
  router.push({
    path: `/detail/${id}`,
    query: { type: 'resource' }
  })
}

// 页面挂载时初始化图表
onMounted(() => {
  initRadarChart()
})
</script>

<style scoped>
/* 全局样式 */
.ability-analysis {
  width: 1200px;
  margin: 0 auto;
  padding: 20px 0 50px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
}

/* 页面头部 */
.page-header {
  margin-bottom: 30px;
}
.page-title {
  font-size: 28px;
  margin: 0 0 8px 0;
  color: #2f54eb;
}
.page-desc {
  font-size: 16px;
  color: #666;
  margin: 0 0 15px 0;
}
.header-actions {
  display: flex;
  gap: 10px;
}
.btn-refresh, .btn-export {
  padding: 8px 15px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
.btn-refresh {
  background: #f5f7fa;
  color: #2f54eb;
}
.btn-export {
  background: #2f54eb;
  color: #fff;
}

/* 概览卡片 */
.overview-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
}
.overview-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}
.card-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  border-radius: 8px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card-content {
  flex: 1;
}
.card-title {
  font-size: 14px;
  color: #666;
  margin: 0 0 5px 0;
}
.card-value {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 5px 0;
}
.card-desc {
  font-size: 12px;
  color: #999;
}
.score-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.score-tag.excellent {
  background: #f6ffed;
  color: #52c41a;
}
.score-tag.good {
  background: #e6f7ff;
  color: #1890ff;
}
.score-tag.normal {
  background: #fffbe6;
  color: #faad14;
}
.score-tag.poor {
  background: #fff2e8;
  color: #ff7a45;
}
.score-tag.very-poor {
  background: #fff1f0;
  color: #ff4d4f;
}

/* 图表区域 */
.chart-section {
  margin-bottom: 40px;
}
.chart-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
}
.chart-title {
  font-size: 18px;
  margin: 0 0 15px 0;
  color: #333;
}
.chart-container {
  height: 400px;
  margin-bottom: 15px;
}
.chart-legend {
  display: flex;
  gap: 20px;
  justify-content: center;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}
.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 4px;
  display: inline-block;
}
.legend-color.your-score {
  background: rgba(24, 144, 255, 0.7);
}
.legend-color.target-score {
  background: rgba(82, 196, 26, 0.7);
}

/* 短板详情 */
.shortage-section {
  margin-bottom: 40px;
}
.section-title {
  font-size: 20px;
  margin: 0 0 20px 0;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
}
.shortage-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.shortage-item {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
}
.shortage-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}
.shortage-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}
.shortage-title {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.shortage-title h4 {
  font-size: 18px;
  margin: 0;
}
.shortage-score {
  font-size: 14px;
  color: #ff7a45;
  font-weight: bold;
}
.shortage-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}
.shortage-suggestion h5 {
  font-size: 14px;
  margin: 0 0 8px 0;
  color: #333;
}
.shortage-suggestion ul {
  margin: 0;
  padding-left: 20px;
  font-size: 14px;
  color: #666;
  line-height: 1.8;
}
.shortage-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}
.btn-learn, .btn-plan {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
}
.btn-learn {
  background: #e6f7ff;
  color: #1890ff;
}
.btn-plan {
  background: #f6ffed;
  color: #52c41a;
}

/* 提升路径 */
.improve-section {
  margin-bottom: 40px;
}
.improve-timeline {
  position: relative;
  padding-left: 30px;
  border-left: 2px solid #e8e8e8;
  margin-left: 10px;
}
.timeline-item {
  position: relative;
  margin-bottom: 25px;
}
.timeline-dot {
  position: absolute;
  left: -38px;
  top: 0;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid #fff;
}
.timeline-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 15px;
}
.timeline-period {
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
}
.timeline-title {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 8px 0;
}
.timeline-tasks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.task-tag {
  padding: 2px 8px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

/* 学习资源 */
.resource-section {
  margin-bottom: 20px;
}
.resource-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}
.resource-card {
  width: calc(25% - 15px);
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.resource-type {
  padding: 8px 0;
  text-align: center;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
}
.resource-content {
  padding: 15px;
  flex: 1;
}
.resource-title {
  font-size: 16px;
  margin: 0 0 8px 0;
}
.resource-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.6;
  margin: 0 0 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.resource-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #999;
}
.resource-btn {
  width: 100%;
  padding: 8px 0;
  background: #f5f7fa;
  color: #2f54eb;
  border: none;
  border-top: 1px solid #e8e8e8;
  cursor: pointer;
  font-size: 14px;
}
.resource-btn:hover {
  background: #e6f7ff;
}
</style>
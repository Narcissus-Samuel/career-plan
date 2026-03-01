<template>
  <div class="development-path">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">发展路径规划</h1>
      <p class="page-desc">根据你的职业目标和能力现状，定制个性化的成长路径，清晰规划每一步</p>
      <div class="header-actions">
        <button class="btn-new" @click="createNewPath">➕ 新建规划路径</button>
        <button class="btn-save" @click="savePath">💾 保存当前规划</button>
        <button class="btn-share" @click="sharePath">📤 分享规划路径</button>
      </div>
    </div>

    <!-- 路径选择区 -->
    <div class="path-select-section">
      <div class="select-header">
        <h3 class="section-subtitle">选择职业发展方向</h3>
        <button class="btn-edit" @click="editPathType">✏️ 编辑</button>
      </div>
      <div class="path-type-cards">
        <div 
          class="path-type-card" 
          v-for="(item, index) in pathTypes" 
          :key="index"
          :class="{ active: item.id === activePathId }"
          @click="selectPathType(item.id)"
        >
          <div class="card-icon" :style="{ backgroundColor: item.color }">{{ item.icon }}</div>
          <div class="card-content">
            <h4 class="card-title">{{ item.name }}</h4>
            <p class="card-desc">{{ item.description }}</p>
            <div class="card-progress" v-if="item.progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${item.progress}%` }"></div>
              </div>
              <span class="progress-text">{{ item.progress }}% 完成</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心规划区 -->
    <div class="core-plan-section" v-if="activePath">
      <!-- 路径基本信息 -->
      <div class="path-info-card">
        <div class="info-header">
          <h3 class="info-title">{{ activePath.name }} - 规划详情</h3>
          <div class="info-meta">
            <span class="meta-item">创建时间：{{ activePath.createTime }}</span>
            <span class="meta-item">目标达成时间：{{ activePath.targetTime }}</span>
          </div>
        </div>
        <div class="info-content">
          <div class="info-item">
            <label class="info-label">核心目标：</label>
            <p class="info-value">{{ activePath.coreGoal }}</p>
          </div>
          <div class="info-item">
            <label class="info-label">能力基础：</label>
            <p class="info-value">{{ activePath.abilityBase }}</p>
          </div>
          <div class="info-item">
            <label class="info-label">关键挑战：</label>
            <p class="info-value">{{ activePath.challenges }}</p>
          </div>
        </div>
      </div>

      <!-- 阶段规划时间线 -->
      <div class="timeline-section">
        <h3 class="section-subtitle">分阶段规划（{{ activePath.stages.length }}个阶段）</h3>
        <div class="timeline-container">
          <div class="timeline-track"></div>
          <div 
            class="timeline-item" 
            v-for="(stage, index) in activePath.stages" 
            :key="index"
            :class="{ current: index === currentStage }"
          >
            <div class="timeline-dot" :style="{ backgroundColor: getStageColor(stage.status) }">
              <span class="dot-icon">{{ getStageIcon(stage.status) }}</span>
            </div>
            <div class="timeline-content">
              <div class="stage-header">
                <h4 class="stage-title">{{ stage.name }} <span class="stage-period">({{ stage.period }})</span></h4>
                <span class="stage-status" :style="{ backgroundColor: getStageColor(stage.status) }">
                  {{ getStageStatusText(stage.status) }}
                </span>
              </div>
              <div class="stage-goals">
                <h5 class="goals-title">核心目标：</h5>
                <ul class="goals-list">
                  <li v-for="(goal, i) in stage.goals" :key="i">
                    <input type="checkbox" :id="`goal-${index}-${i}`" v-model="goal.completed">
                    <label :for="`goal-${index}-${i}`" :class="{ completed: goal.completed }">{{ goal.content }}</label>
                  </li>
                </ul>
              </div>
              <div class="stage-milestones">
                <h5 class="milestones-title">关键里程碑：</h5>
                <div class="milestones-list">
                  <div class="milestone-item" v-for="(milestone, i) in stage.milestones" :key="i">
                    <span class="milestone-icon">📍</span>
                    <div class="milestone-content">
                      <span class="milestone-name">{{ milestone.name }}</span>
                      <span class="milestone-date">{{ milestone.date }}</span>
                    </div>
                    <button class="milestone-btn" @click="editMilestone(index, i)">✏️</button>
                  </div>
                </div>
              </div>
              <div class="stage-actions">
                <button class="btn-start" @click="startStage(index)" v-if="stage.status === 'pending'">开始阶段</button>
                <button class="btn-complete" @click="completeStage(index)" v-if="stage.status === 'ongoing'">完成阶段</button>
                <button class="btn-detail" @click="viewStageDetail(index)">查看详情</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 资源与支持 -->
      <div class="resource-support-section">
        <h3 class="section-subtitle">配套资源与支持</h3>
        <div class="support-tabs">
          <span class="tab-item active" @click="switchTab('learning')">学习资源</span>
          <span class="tab-item" @click="switchTab('mentor')">导师指导</span>
          <span class="tab-item" @click="switchTab('practice')">实践机会</span>
        </div>
        <div class="support-content">
          <!-- 学习资源 -->
          <div class="learning-resource" v-if="activeTab === 'learning'">
            <div class="resource-item" v-for="(item, index) in learningResources" :key="index">
              <div class="resource-icon" :style="{ backgroundColor: item.color }">{{ item.icon }}</div>
              <div class="resource-info">
                <h4 class="resource-title">{{ item.title }}</h4>
                <p class="resource-desc">{{ item.description }}</p>
                <div class="resource-meta">
                  <span class="meta-item">预计耗时：{{ item.duration }}</span>
                  <span class="meta-item">优先级：{{ item.priority }}</span>
                </div>
              </div>
              <button class="resource-action" @click="accessResource(item.id)">立即学习</button>
            </div>
          </div>

          <!-- 导师指导 -->
          <div class="mentor-support" v-if="activeTab === 'mentor'">
            <div class="mentor-item" v-for="(item, index) in mentorList" :key="index">
              <img :src="item.avatar" alt="导师头像" class="mentor-avatar">
              <div class="mentor-info">
                <h4 class="mentor-name">{{ item.name }} <span class="mentor-title">{{ item.title }}</span></h4>
                <p class="mentor-field">擅长领域：{{ item.field }}</p>
                <p class="mentor-intro">{{ item.introduction }}</p>
                <div class="mentor-service">
                  <span class="service-tag" v-for="tag in item.services" :key="tag">{{ tag }}</span>
                </div>
              </div>
              <button class="mentor-action" @click="consultMentor(item.id)">预约咨询</button>
            </div>
          </div>

          <!-- 实践机会 -->
          <div class="practice-opportunity" v-if="activeTab === 'practice'">
            <div class="practice-item" v-for="(item, index) in practiceList" :key="index">
              <div class="practice-tag" :style="{ backgroundColor: item.color }">{{ item.type }}</div>
              <div class="practice-info">
                <h4 class="practice-title">{{ item.title }}</h4>
                <p class="practice-desc">{{ item.description }}</p>
                <div class="practice-requirement">
                  <label>能力要求：</label>
                  <span class="requirement-tag" v-for="req in item.requirements" :key="req">{{ req }}</span>
                </div>
              </div>
              <button class="practice-action" @click="applyPractice(item.id)">立即申请</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 进度跟踪 -->
      <div class="progress-tracking-section">
        <h3 class="section-subtitle">整体进度跟踪</h3>
        <div class="progress-overview">
          <div class="progress-chart">
            <canvas id="progressChart"></canvas>
          </div>
          <div class="progress-stats">
            <div class="stat-item">
              <div class="stat-value">{{ completedStages }}/{{ totalStages }}</div>
              <div class="stat-label">已完成阶段</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ completedGoals }}/{{ totalGoals }}</div>
              <div class="stat-label">已完成目标</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ delayedMilestones }}</div>
              <div class="stat-label">逾期里程碑</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ overallProgress }}%</div>
              <div class="stat-label">整体完成度</div>
            </div>
          </div>
        </div>
        <div class="progress-tips">
          <span class="tips-icon">💡</span>
          <span class="tips-content">你的{{ activePath.name }}路径整体进度正常，建议加快「{{ delayedMilestoneName }}」的推进，避免影响后续阶段。</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'

// 初始化路由实例
const router = useRouter()

// 页面核心数据
const pathTypes = ref([
  {
    id: 1,
    icon: '👨💼',
    name: '互联网产品经理',
    description: '从产品助理到资深产品经理的完整成长路径',
    color: '#1890ff',
    progress: 35,
    createTime: '2026-01-15',
    targetTime: '2028-01-15'
  },
  {
    id: 2,
    icon: '🎓',
    name: '计算机考研深造',
    description: '从基础复习到复试录取的全流程规划',
    color: '#52c41a',
    progress: 60,
    createTime: '2026-02-01',
    targetTime: '2027-12-31'
  },
  {
    id: 3,
    icon: '💼',
    name: '国企行政岗',
    description: '从校招准备到职场晋升的发展规划',
    color: '#faad14',
    progress: 15,
    createTime: '2026-02-10',
    targetTime: '2029-02-10'
  }
])

// 激活的路径ID和详情
const activePathId = ref(1)
const activePath = ref(pathTypes.value[0])

// 阶段数据（以产品经理路径为例）
const stageData = ref([
  {
    name: '基础积累期',
    period: '2026.01-2026.06',
    status: 'completed', // pending/ongoing/completed
    goals: [
      { content: '掌握产品经理基础理论知识', completed: true },
      { content: '学习Axure、Figma等产品工具', completed: true },
      { content: '完成2个产品原型设计练习', completed: false },
      { content: '阅读5本产品经理经典书籍', completed: true }
    ],
    milestones: [
      { name: '产品工具认证考试', date: '2026-03-15' },
      { name: '完成第一个完整产品原型', date: '2026-05-20' }
    ]
  },
  {
    name: '实践提升期',
    period: '2026.07-2027.01',
    status: 'ongoing',
    goals: [
      { content: '找到产品助理实习岗位', completed: true },
      { content: '参与1个完整的产品迭代周期', completed: false },
      { content: '独立完成1个小功能的需求文档', completed: false },
      { content: '积累10个用户访谈经验', completed: false }
    ],
    milestones: [
      { name: '转正为正式产品助理', date: '2026-10-01' },
      { name: '完成首次独立需求交付', date: '2026-12-15' }
    ]
  },
  {
    name: '能力进阶期',
    period: '2027.02-2027.08',
    status: 'pending',
    goals: [
      { content: '负责1个核心模块的产品规划', completed: false },
      { content: '主导1次产品版本迭代', completed: false },
      { content: '建立产品数据监控体系', completed: false },
      { content: '考取PMP项目管理证书', completed: false }
    ],
    milestones: [
      { name: '晋升为初级产品经理', date: '2027-05-01' },
      { name: 'PMP证书考试通过', date: '2027-07-20' }
    ]
  },
  {
    name: '资深发展期',
    period: '2027.09-2028.01',
    status: 'pending',
    goals: [
      { content: '独立负责1个产品线', completed: false },
      { content: '制定产品年度规划', completed: false },
      { content: '搭建产品团队协作体系', completed: false },
      { content: '形成个人产品方法论', completed: false }
    ],
    milestones: [
      { name: '晋升为资深产品经理', date: '2028-01-01' },
      { name: '完成年度产品目标', date: '2028-01-15' }
    ]
  }
])

// 初始化激活路径的阶段数据
activePath.value.stages = stageData.value

// 当前阶段索引
const currentStage = ref(1)

// 标签页切换
const activeTab = ref('learning')

// 学习资源数据
const learningResources = ref([
  {
    id: 1,
    icon: '📚',
    color: '#1890ff',
    title: '产品经理入门到精通',
    description: '系统学习产品经理核心技能，包含需求分析、原型设计、项目管理等',
    duration: '3个月',
    priority: '高'
  },
  {
    id: 2,
    icon: '🎥',
    color: '#52c41a',
    title: 'Axure原型设计实战课',
    description: '从零基础到独立完成复杂产品原型，包含交互设计、组件复用等技巧',
    duration: '1个月',
    priority: '高'
  },
  {
    id: 3,
    icon: '📝',
    color: '#faad14',
    title: 'PRD需求文档写作指南',
    description: '学习专业的需求文档撰写规范，提升需求表达和沟通效率',
    duration: '2周',
    priority: '中'
  },
  {
    id: 4,
    icon: '📊',
    color: '#ff7a45',
    title: '产品数据分析实战',
    description: '掌握产品数据监控、分析方法，用数据驱动产品决策',
    duration: '1.5个月',
    priority: '中'
  }
])

// 导师列表数据
const mentorList = ref([
  {
    id: 1,
    avatar: 'https://picsum.photos/seed/mentor1/64/64',
    name: '张经理',
    title: '资深产品经理',
    field: '互联网产品、电商产品、用户增长',
    introduction: '10年产品经理经验，曾主导多个千万级用户产品的规划与落地',
    services: ['1v1咨询', '简历指导', '模拟面试', '职业规划']
  },
  {
    id: 2,
    avatar: 'https://picsum.photos/seed/mentor2/64/64',
    name: '李总监',
    title: '产品总监',
    field: 'ToB产品、企业服务、SaaS产品',
    introduction: '8年ToB产品经验，擅长产品商业化和生态搭建',
    services: ['1v1咨询', '项目指导', '行业分析', '资源对接']
  }
])

// 实践机会数据
const practiceList = ref([
  {
    id: 1,
    type: '实习',
    color: '#1890ff',
    title: '互联网大厂产品助理实习',
    description: '参与电商产品的需求分析、原型设计和用户调研工作，有导师带教',
    requirements: ['产品基础', 'Axure', '沟通能力', '每周4天']
  },
  {
    id: 2,
    type: '项目',
    color: '#52c41a',
    title: '校园产品创新大赛',
    description: '组队参与产品创新大赛，从0到1设计一款校园产品，有行业评委点评',
    requirements: ['创新思维', '团队协作', '原型设计', '路演能力']
  },
  {
    id: 3,
    type: '兼职',
    color: '#faad14',
    title: '初创公司产品顾问',
    description: '为初创公司提供产品规划建议，参与产品需求评审和迭代决策',
    requirements: ['产品思维', '行业认知', '独立思考', '时间灵活']
  }
])

// 进度统计数据
const completedStages = ref(1)
const totalStages = ref(4)
const completedGoals = ref(3)
const totalGoals = ref(16)
const delayedMilestones = ref(1)
const overallProgress = ref(35)
const delayedMilestoneName = ref('完成第一个完整产品原型')

// 选择发展路径
const selectPathType = (id) => {
  activePathId.value = id
  const selectedPath = pathTypes.value.find(item => item.id === id)
  activePath.value = selectedPath
  
  // 模拟不同路径的阶段数据（实际项目中可从接口获取）
  if (id === 2) {
    activePath.value.stages = [
      {
        name: '基础复习期',
        period: '2026.02-2026.06',
        status: 'completed',
        goals: [{ content: '完成数学一轮复习', completed: true }, { content: '英语单词背诵完毕', completed: true }],
        milestones: [{ name: '基础阶段测试', date: '2026-06-30' }]
      },
      {
        name: '强化提升期',
        period: '2026.07-2026.10',
        status: 'ongoing',
        goals: [{ content: '专业课一轮复习', completed: false }, { content: '真题刷题训练', completed: false }],
        milestones: [{ name: '强化阶段模考', date: '2026-10-31' }]
      },
      {
        name: '冲刺备考期',
        period: '2026.11-2026.12',
        status: 'pending',
        goals: [{ content: '全真模拟考试', completed: false }, { content: '查漏补缺', completed: false }],
        milestones: [{ name: '考研初试', date: '2026-12-24' }]
      },
      {
        name: '复试准备期',
        period: '2027.02-2027.03',
        status: 'pending',
        goals: [{ content: '复试专业课复习', completed: false }, { content: '面试模拟训练', completed: false }],
        milestones: [{ name: '考研复试', date: '2027-03-15' }]
      }
    ]
  } else if (id === 3) {
    activePath.value.stages = [
      {
        name: '备考准备期',
        period: '2026.02-2026.06',
        status: 'pending',
        goals: [{ content: '了解考公政策和岗位', completed: false }, { content: '购买备考资料', completed: true }],
        milestones: [{ name: '确定报考岗位', date: '2026-06-30' }]
      },
      {
        name: '基础学习期',
        period: '2026.07-2026.10',
        status: 'pending',
        goals: [{ content: '行测基础学习', completed: false }, { content: '申论基础学习', completed: false }],
        milestones: [{ name: '基础阶段测试', date: '2026-10-31' }]
      },
      {
        name: '强化刷题期',
        period: '2026.11-2027.02',
        status: 'pending',
        goals: [{ content: '行测真题刷题', completed: false }, { content: '申论写作训练', completed: false }],
        milestones: [{ name: '强化阶段模考', date: '2027-02-28' }]
      },
      {
        name: '冲刺备考期',
        period: '2027.03-2027.11',
        status: 'pending',
        goals: [{ content: '全真模拟考试', completed: false }, { content: '查漏补缺', completed: false }],
        milestones: [{ name: '公务员考试', date: '2027-11-26' }]
      }
    ]
  } else {
    activePath.value.stages = stageData.value
  }
  
  // 更新进度数据
  updateProgressStats()
}

// 更新进度统计
const updateProgressStats = () => {
  let completed = 0
  let total = 0
  let goalCompleted = 0
  let goalTotal = 0
  
  activePath.value.stages.forEach(stage => {
    if (stage.status === 'completed') completed++
    total++
    
    stage.goals.forEach(goal => {
      if (goal.completed) goalCompleted++
      goalTotal++
    })
  })
  
  completedStages.value = completed
  totalStages.value = total
  completedGoals.value = goalCompleted
  totalGoals.value = goalTotal
  overallProgress.value = Math.round((completed / total) * 100)
  
  // 重新初始化进度图表
  initProgressChart()
}

// 获取阶段状态颜色
const getStageColor = (status) => {
  switch(status) {
    case 'completed': return '#52c41a'
    case 'ongoing': return '#1890ff'
    case 'pending': return '#d9d9d9'
    default: return '#d9d9d9'
  }
}

// 获取阶段状态图标
const getStageIcon = (status) => {
  switch(status) {
    case 'completed': return '✓'
    case 'ongoing': return '▶'
    case 'pending': return '○'
    default: return '○'
  }
}

// 获取阶段状态文本
const getStageStatusText = (status) => {
  switch(status) {
    case 'completed': return '已完成'
    case 'ongoing': return '进行中'
    case 'pending': return '未开始'
    default: return '未开始'
  }
}

// 切换标签页
const switchTab = (tab) => {
  activeTab.value = tab
}

// 开始阶段
const startStage = (index) => {
  activePath.value.stages[index].status = 'ongoing'
  currentStage.value = index
  updateProgressStats()
  alert(`已开始「${activePath.value.stages[index].name}」阶段！`)
}

// 完成阶段
const completeStage = (index) => {
  activePath.value.stages[index].status = 'completed'
  updateProgressStats()
  alert(`已完成「${activePath.value.stages[index].name}」阶段！`)
  
  // 自动切换到下一个未开始的阶段
  const nextStage = activePath.value.stages.findIndex((stage, i) => i > index && stage.status === 'pending')
  if (nextStage > -1) {
    currentStage.value = nextStage
  }
}

// 查看阶段详情
const viewStageDetail = (index) => {
  router.push({
    path: '/detail',
    query: { 
      type: 'stage',
      pathId: activePathId.value,
      stageIndex: index
    }
  })
}

// 编辑里程碑
const editMilestone = (stageIndex, milestoneIndex) => {
  const newDate = prompt('请输入新的里程碑日期（格式：YYYY-MM-DD）：', activePath.value.stages[stageIndex].milestones[milestoneIndex].date)
  if (newDate) {
    activePath.value.stages[stageIndex].milestones[milestoneIndex].date = newDate
    alert('里程碑日期已更新！')
  }
}

// 访问学习资源
const accessResource = (id) => {
  router.push({
    path: '/resource-library',
    query: { id, type: 'learning' }
  })
}

// 咨询导师
const consultMentor = (id) => {
  router.push({
    path: '/detail',
    query: { id, type: 'mentor' }
  })
}

// 申请实践机会
const applyPractice = (id) => {
  router.push({
    path: '/detail',
    query: { id, type: 'practice' }
  })
}

// 新建规划路径
const createNewPath = () => {
  const pathName = prompt('请输入新的发展路径名称：')
  if (pathName) {
    const newId = pathTypes.value.length + 1
    pathTypes.value.push({
      id: newId,
      icon: '🎯',
      name: pathName,
      description: '自定义的职业发展路径',
      color: '#722ed1',
      progress: 0,
      createTime: new Date().toISOString().split('T')[0],
      targetTime: new Date(new Date().setFullYear(new Date().getFullYear() + 2)).toISOString().split('T')[0]
    })
    selectPathType(newId)
    alert(`已创建新的发展路径「${pathName}」！`)
  }
}

// 保存规划路径
const savePath = () => {
  // 模拟保存到后端
  alert(`「${activePath.value.name}」路径规划已保存成功！`)
}

// 分享规划路径
const sharePath = () => {
  const shareType = prompt('请选择分享方式：1-链接 2-图片 3-PDF', '1')
  switch(shareType) {
    case '1':
      alert(`分享链接：https://career-plan.com/share/${activePathId.value}`)
      break
    case '2':
    case '3':
      alert(`正在生成${shareType === '2' ? '图片' : 'PDF'}格式的规划路径，稍后发送到你的邮箱！`)
      break
    default:
      alert('分享方式选择错误！')
  }
}

// 编辑路径类型
const editPathType = () => {
  const newName = prompt('请输入新的路径名称：', activePath.value.name)
  if (newName) {
    activePath.value.name = newName
    const index = pathTypes.value.findIndex(item => item.id === activePathId.value)
    pathTypes.value[index].name = newName
    alert('路径名称已更新！')
  }
}

// 初始化进度图表
const initProgressChart = () => {
  const ctx = document.getElementById('progressChart')
  if (ctx) {
    // 销毁已存在的图表
    if (window.progressChartInstance) {
      window.progressChartInstance.destroy()
    }
    
    // 提取阶段数据
    const labels = activePath.value.stages.map(stage => stage.name)
    const completedGoals = activePath.value.stages.map(stage => {
      return stage.goals.filter(goal => goal.completed).length
    })
    const totalGoals = activePath.value.stages.map(stage => stage.goals.length)
    
    // 创建图表
    window.progressChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: '已完成目标',
            data: completedGoals,
            backgroundColor: 'rgba(82, 196, 26, 0.7)',
            borderColor: 'rgba(82, 196, 26, 1)',
            borderWidth: 1
          },
          {
            label: '总目标数',
            data: totalGoals,
            backgroundColor: 'rgba(201, 203, 207, 0.7)',
            borderColor: 'rgba(201, 203, 207, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '目标数量'
            }
          }
        }
      }
    })
  }
}

// 页面挂载时初始化图表
onMounted(() => {
  updateProgressStats()
  initProgressChart()
})
</script>

<style scoped>
/* 全局样式 */
.development-path {
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
.btn-new, .btn-save, .btn-share, .btn-edit {
  padding: 8px 15px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
.btn-new {
  background: #2f54eb;
  color: #fff;
}
.btn-save {
  background: #52c41a;
  color: #fff;
}
.btn-share {
  background: #faad14;
  color: #fff;
}
.btn-edit {
  background: #f5f7fa;
  color: #2f54eb;
  padding: 4px 8px;
  font-size: 12px;
}

/* 路径选择区 */
.path-select-section {
  margin-bottom: 40px;
}
.select-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.section-subtitle {
  font-size: 20px;
  margin: 0;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
}
.path-type-cards {
  display: flex;
  gap: 20px;
}
.path-type-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}
.path-type-card.active {
  border-color: #2f54eb;
  box-shadow: 0 4px 12px rgba(47,84,235,0.1);
}
.path-type-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  margin-bottom: 15px;
}
.card-title {
  font-size: 18px;
  margin: 0 0 8px 0;
}
.card-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 10px 0;
  line-height: 1.6;
}
.card-progress {
  width: 100%;
}
.progress-bar {
  height: 6px;
  background: #f5f7fa;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 5px;
}
.progress-fill {
  height: 100%;
  background: #52c41a;
  border-radius: 3px;
  transition: width 0.3s;
}
.progress-text {
  font-size: 12px;
  color: #999;
}

/* 核心规划区 */
.core-plan-section {
  margin-bottom: 40px;
}
.path-info-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
  margin-bottom: 20px;
}
.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.info-title {
  font-size: 18px;
  margin: 0;
  color: #2f54eb;
}
.info-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 15px;
}
.info-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.info-item {
  display: flex;
  gap: 10px;
}
.info-label {
  font-weight: bold;
  min-width: 80px;
  color: #333;
}
.info-value {
  flex: 1;
  margin: 0;
  color: #666;
  line-height: 1.6;
}

/* 时间线样式 */
.timeline-section {
  margin-bottom: 40px;
}
.timeline-container {
  position: relative;
  padding-left: 40px;
}
.timeline-track {
  position: absolute;
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e8e8e8;
}
.timeline-item {
  position: relative;
  margin-bottom: 30px;
}
.timeline-dot {
  position: absolute;
  left: -40px;
  top: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  z-index: 1;
}
.timeline-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
  border-left: 3px solid #1890ff;
}
.timeline-item.current .timeline-content {
  border-left-color: #2f54eb;
  box-shadow: 0 4px 12px rgba(47,84,235,0.1);
}
.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.stage-title {
  font-size: 18px;
  margin: 0;
}
.stage-period {
  font-size: 14px;
  color: #999;
  font-weight: normal;
  margin-left: 10px;
}
.stage-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
}
.stage-goals, .stage-milestones {
  margin-bottom: 15px;
}
.goals-title, .milestones-title {
  font-size: 14px;
  margin: 0 0 8px 0;
  color: #333;
}
.goals-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.goals-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 5px;
}
.goals-list li input {
  margin-top: 4px;
}
.goals-list li label {
  flex: 1;
  font-size: 14px;
  color: #666;
  cursor: pointer;
}
.goals-list li label.completed {
  text-decoration: line-through;
  color: #999;
}
.milestones-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.milestone-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}
.milestone-icon {
  color: #faad14;
}
.milestone-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
}
.milestone-name {
  color: #333;
}
.milestone-date {
  color: #999;
  font-size: 12px;
}
.milestone-btn {
  background: transparent;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 5px;
}
.milestone-btn:hover {
  color: #2f54eb;
}
.stage-actions {
  display: flex;
  gap: 10px;
}
.btn-start, .btn-complete, .btn-detail {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
}
.btn-start {
  background: #e6f7ff;
  color: #1890ff;
}
.btn-complete {
  background: #f6ffed;
  color: #52c41a;
}
.btn-detail {
  background: #f5f7fa;
  color: #666;
}

/* 资源与支持 */
.resource-support-section {
  margin-bottom: 40px;
}
.support-tabs {
  display: flex;
  gap: 0;
  background: #f5f7fa;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  margin-bottom: 0;
}
.tab-item {
  padding: 10px 20px;
  font-size: 14px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
.tab-item.active {
  background: #fff;
  color: #2f54eb;
  border-bottom-color: #2f54eb;
}
.support-content {
  background: #fff;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
}

/* 学习资源样式 */
.learning-resource {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.resource-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}
.resource-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}
.resource-info {
  flex: 1;
}
.resource-title {
  font-size: 16px;
  margin: 0 0 5px 0;
}
.resource-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 5px 0;
  line-height: 1.6;
}
.resource-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}
.resource-action, .mentor-action, .practice-action {
  padding: 8px 15px;
  border-radius: 4px;
  border: none;
  background: #2f54eb;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}

/* 导师指导样式 */
.mentor-support {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.mentor-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}
.mentor-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}
.mentor-info {
  flex: 1;
}
.mentor-name {
  font-size: 16px;
  margin: 0 0 5px 0;
}
.mentor-title {
  font-size: 12px;
  color: #999;
  font-weight: normal;
  margin-left: 8px;
}
.mentor-field {
  font-size: 14px;
  color: #666;
  margin: 0 0 5px 0;
}
.mentor-intro {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
  line-height: 1.6;
}
.mentor-service {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.service-tag {
  padding: 2px 8px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 12px;
}

/* 实践机会样式 */
.practice-opportunity {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.practice-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}
.practice-tag {
  align-self: flex-start;
  padding: 2px 8px;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
}
.practice-info {
  flex: 1;
}
.practice-title {
  font-size: 16px;
  margin: 0 0 5px 0;
}
.practice-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
  line-height: 1.6;
}
.practice-requirement {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.practice-requirement label {
  font-size: 14px;
  color: #333;
  font-weight: bold;
}
.requirement-tag {
  padding: 2px 8px;
  background: #fffbe6;
  color: #faad14;
  border-radius: 4px;
  font-size: 12px;
}

/* 进度跟踪 */
.progress-tracking-section {
  margin-bottom: 20px;
}
.progress-overview {
  display: flex;
  gap: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
}
.progress-chart {
  flex: 2;
  height: 250px;
}
.progress-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 20px;
}
.stat-item {
  text-align: center;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #2f54eb;
  margin: 0 0 5px 0;
}
.stat-label {
  font-size: 14px;
  color: #666;
  margin: 0;
}
.progress-tips {
  margin-top: 15px;
  padding: 10px 15px;
  background: #fffbe6;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.tips-icon {
  font-size: 16px;
}
.tips-content {
  font-size: 14px;
  color: #faad14;
  line-height: 1.6;
}
</style>
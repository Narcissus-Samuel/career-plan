<template>
  <div class="job-match-page">
    <!-- 统一样式的顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item active" @click="$router.push('/match-result')">人岗匹配</li>
            <li class="menu-item" @click="$router.push('/student-ability')">能力画像</li>
            <li class="menu-item" @click="$router.push('/resource-library')">资源库</li>
            <li class="menu-item" @click="$router.push('/about-us')">关于我们</li>
            <li class="menu-item dropdown">
              核心功能 ▼
              <ul class="dropdown-menu">
                <li class="dropdown-item" @click="goToFeature('测评')">
                  <span class="color-dot red"></span> 职业兴趣测评
                </li>
                <li class="dropdown-item" @click="goToFeature('分析')">
                  <span class="color-dot orange"></span> 能力短板分析
                </li>
                <li class="dropdown-item" @click="goToFeature('规划')">
                  <span class="color-dot green"></span> 发展路径规划
                </li>
                <li class="dropdown-item" @click="goToFeature('导出')">
                  <span class="color-dot blue"></span> 匹配报告导出
                </li>
              </ul>
            </li>
          </ul>
        </div>
        <div class="nav-right">
          <div class="nav-search-wrap">
            <input type="text" class="nav-search-input" placeholder="搜索目标岗位..." @keyup.enter="handleSearch" />
            <button class="nav-search-btn" @click="handleSearch">搜索</button>
          </div>
          <button class="btn-toggle-theme" @click="toggleTheme">🌙</button>
          <button class="btn-login" @click="$router.push('/login')" v-if="!isLogin">登录</button>
          <button class="btn-register" @click="$router.push('/register')" v-if="!isLogin">注册</button>
          <div class="user-profile" v-if="isLogin">
            <img :src="userAvatar || 'https://picsum.photos/seed/avatar/40/40'" alt="头像" class="avatar" @click="toggleUserMenu" />
            <div class="user-menu" v-show="isUserMenuOpen">
              <div class="menu-item" @click="$router.push('/profile')">个人中心</div>
              <div class="menu-item" @click="$router.push('/settings')">账号设置</div>
              <div class="menu-item logout" @click="handleLogout">退出登录</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 核心内容区域 -->
    <div class="match-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>人岗匹配分析</h1>
        <p>基于你的就业能力画像，智能分析与目标岗位的契合度与差距</p>
      </div>

      <!-- 岗位推荐与选择区域 -->
      <div class="job-selection-section glass-panel">
        <h2 class="section-title">🎯 目标岗位选择</h2>
        
        <!-- 岗位推荐卡片 -->
        <div class="job-recommendation">
          <h3>为你推荐的匹配岗位</h3>
          <div class="job-card-list">
            <div 
              class="job-card" 
              v-for="job in recommendedJobs" 
              :key="job.id"
              :class="{ active: selectedJob.id === job.id }"
              @click="selectJob(job)"
            >
              <div class="job-icon">{{ job.icon }}</div>
              <div class="job-info">
                <h4 class="job-name">{{ job.name }}</h4>
                <p class="job-desc">{{ job.desc }}</p>
                <div class="job-tags">
                  <span class="tag" v-for="tag in job.tags" :key="tag">{{ tag }}</span>
                </div>
              </div>
              <div class="match-prediction">
                <span>预估匹配度</span>
                <span class="score">{{ job.predictedMatch }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 自定义岗位选择 -->
        <div class="custom-job-selection">
          <h3>或选择其他岗位</h3>
          <el-select 
            v-model="selectedJobId" 
            placeholder="请选择目标岗位" 
            filterable 
            class="job-selector"
            @change="onJobChange"
          >
            <el-option 
              v-for="job in allJobs" 
              :key="job.id" 
              :label="job.name" 
              :value="job.id"
            ></el-option>
          </el-select>
        </div>

        <!-- 匹配按钮 - 核心修改点 -->
        <div class="match-action">
          <el-button 
            type="primary" 
            @click="handleMatchButtonClick"
            :loading="matching"
            :disabled="matching"
            class="match-btn"
          >
            {{ matching ? '匹配分析中...' : '开始人岗匹配分析' }}
          </el-button>
          <span v-if="!hasAbilityProfile" class="tips">
            👉 请先完成<a @click="goToAbilityProfile" class="link">能力画像</a>生成
          </span>
        </div>
      </div>

      <!-- 匹配结果展示区域 -->
      <div v-if="matchResultVisible" class="match-result-section glass-panel">
        <h2 class="section-title">📊 人岗匹配分析结果</h2>
        
        <!-- 总体匹配度 -->
        <div class="overall-match">
          <div class="match-score-card">
            <span class="score-label">总体匹配度</span>
            <span class="total-score">{{ matchResult.overallScore }}%</span>
            <div class="score-bar">
              <div class="bar-fill" :style="{ width: matchResult.overallScore + '%', background: getScoreColor(matchResult.overallScore) }"></div>
            </div>
            <span class="match-level" :style="{ color: getScoreColor(matchResult.overallScore) }">
              {{ getMatchLevelText(matchResult.overallScore) }}
            </span>
          </div>
        </div>

        <!-- 维度对比分析 -->
        <div class="dimension-analysis">
          <h3>多维度契合度对比</h3>
          <div class="dimension-grid">
            <!-- 专业技能维度 -->
            <div class="dimension-item">
              <h4 class="dimension-name">专业技能</h4>
              <div class="dimension-compare">
                <div class="compare-item">
                  <span class="label">你的能力</span>
                  <div class="score-bar">
                    <div class="bar-fill self" :style="{ width: matchResult.dimensions.professionalSkill.self + '%' }"></div>
                  </div>
                  <span class="score">{{ matchResult.dimensions.professionalSkill.self }}%</span>
                </div>
                <div class="compare-item">
                  <span class="label">岗位要求</span>
                  <div class="score-bar">
                    <div class="bar-fill job" :style="{ width: matchResult.dimensions.professionalSkill.job + '%' }"></div>
                  </div>
                  <span class="score">{{ matchResult.dimensions.professionalSkill.job }}%</span>
                </div>
              </div>
              <div class="gap-analysis">
                <span class="gap-label">差距分析：</span>
                <span class="gap-text">{{ matchResult.dimensions.professionalSkill.gap }}</span>
              </div>
            </div>

            <!-- 通用素质维度 -->
            <div class="dimension-item">
              <h4 class="dimension-name">通用素质</h4>
              <div class="dimension-compare">
                <div class="compare-item">
                  <span class="label">你的能力</span>
                  <div class="score-bar">
                    <div class="bar-fill self" :style="{ width: matchResult.dimensions.generalQuality.self + '%' }"></div>
                  </div>
                  <span class="score">{{ matchResult.dimensions.generalQuality.self }}%</span>
                </div>
                <div class="compare-item">
                  <span class="label">岗位要求</span>
                  <div class="score-bar">
                    <div class="bar-fill job" :style="{ width: matchResult.dimensions.generalQuality.job + '%' }"></div>
                  </div>
                  <span class="score">{{ matchResult.dimensions.generalQuality.job }}%</span>
                </div>
              </div>
              <div class="gap-analysis">
                <span class="gap-label">差距分析：</span>
                <span class="gap-text">{{ matchResult.dimensions.generalQuality.gap }}</span>
              </div>
            </div>

            <!-- 实践经验维度 -->
            <div class="dimension-item">
              <h4 class="dimension-name">实践经验</h4>
              <div class="dimension-compare">
                <div class="compare-item">
                  <span class="label">你的能力</span>
                  <div class="score-bar">
                    <div class="bar-fill self" :style="{ width: matchResult.dimensions.practicalExperience.self + '%' }"></div>
                  </div>
                  <span class="score">{{ matchResult.dimensions.practicalExperience.self }}%</span>
                </div>
                <div class="compare-item">
                  <span class="label">岗位要求</span>
                  <div class="score-bar">
                    <div class="bar-fill job" :style="{ width: matchResult.dimensions.practicalExperience.job + '%' }"></div>
                  </div>
                  <span class="score">{{ matchResult.dimensions.practicalExperience.job }}%</span>
                </div>
              </div>
              <div class="gap-analysis">
                <span class="gap-label">差距分析：</span>
                <span class="gap-text">{{ matchResult.dimensions.practicalExperience.gap }}</span>
              </div>
            </div>

            <!-- 发展潜力维度 -->
            <div class="dimension-item">
              <h4 class="dimension-name">发展潜力</h4>
              <div class="dimension-compare">
                <div class="compare-item">
                  <span class="label">你的能力</span>
                  <div class="score-bar">
                    <div class="bar-fill self" :style="{ width: matchResult.dimensions.developmentPotential.self + '%' }"></div>
                  </div>
                  <span class="score">{{ matchResult.dimensions.developmentPotential.self }}%</span>
                </div>
                <div class="compare-item">
                  <span class="label">岗位要求</span>
                  <div class="score-bar">
                    <div class="bar-fill job" :style="{ width: matchResult.dimensions.developmentPotential.job + '%' }"></div>
                  </div>
                  <span class="score">{{ matchResult.dimensions.developmentPotential.job }}%</span>
                </div>
              </div>
              <div class="gap-analysis">
                <span class="gap-label">差距分析：</span>
                <span class="gap-text">{{ matchResult.dimensions.developmentPotential.gap }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 详细差距分析与提升建议 -->
        <div class="detailed-analysis">
          <h3>差距分析与提升建议</h3>
          <el-collapse accordion>
            <el-collapse-item title="核心短板分析">
              <div class="collapse-content">
                {{ matchResult.detailedAnalysis.shortcomings }}
              </div>
            </el-collapse-item>
            <el-collapse-item title="能力提升建议">
              <div class="collapse-content">
                {{ matchResult.detailedAnalysis.suggestions }}
              </div>
            </el-collapse-item>
            <el-collapse-item title="求职策略建议">
              <div class="collapse-content">
                {{ matchResult.detailedAnalysis.strategy }}
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 操作按钮 -->
        <div class="result-actions">
          <el-button @click="resetMatch">重新选择岗位</el-button>
          <el-button type="primary" @click="exportMatchReport">导出匹配报告</el-button>
          <el-button type="success" @click="generateCareerPlan">生成职业规划</el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!matchResultVisible && hasAbilityProfile" class="empty-state glass-panel">
        <div class="empty-icon">📋</div>
        <p class="empty-text">请选择目标岗位，点击匹配按钮生成分析结果</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

// 路由实例
const router = useRouter()
const route = useRoute()

// ========== 导航栏相关 ==========
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')

// 导航栏方法
const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const handleLogout = () => {
  localStorage.clear()
  isLogin.value = false
  router.push('/')
  ElMessage.success('退出登录成功')
}

const toggleTheme = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  ElMessage.info('已切换为' + (darkMode.value ? '暗黑' : '亮色') + '模式')
}

const goToFeature = (type) => {
  const map = {
    '测评': '/interest-test',
    '分析': '/ability-analysis',
    '规划': '/development-path',
    '导出': '/report-export'
  }
  router.push(map[type] || '/')
}

const handleSearch = () => {
  const input = document.querySelector('.nav-search-input')
  if (input.value.trim()) {
    // 岗位搜索逻辑
    const keyword = input.value.trim()
    const matchedJob = allJobs.value.find(job => 
      job.name.includes(keyword) || job.tags.some(tag => tag.includes(keyword))
    )
    if (matchedJob) {
      selectJob(matchedJob)
      ElMessage.success('找到匹配岗位：' + matchedJob.name)
    } else {
      ElMessage.warning('未找到包含"' + keyword + '"的岗位')
    }
    input.value = ''
  }
}

// ========== 核心业务逻辑 ==========
// 检查是否有能力画像数据（增加兜底逻辑）
const hasAbilityProfile = ref(false)

// 所有岗位数据
const allJobs = ref([
  { id: 1, name: 'Java开发工程师', icon: '☕', desc: '负责后端系统设计与开发，构建高可用分布式系统', tags: ['后端', 'Java', 'SpringBoot', '分布式'], predictedMatch: 85 },
  { id: 2, name: 'Python开发工程师', icon: '🐍', desc: '专注于数据处理、AI算法实现或后端开发', tags: ['Python', '数据分析', 'AI', '爬虫'], predictedMatch: 88 },
  { id: 3, name: 'Web前端开发工程师', icon: '🌐', desc: '负责用户界面开发，实现优质的交互体验', tags: ['前端', 'Vue', 'React', 'JavaScript'], predictedMatch: 75 },
  { id: 4, name: '全栈开发工程师', icon: '🔧', desc: '兼具前后端开发能力，独立完成完整项目开发', tags: ['全栈', '前后端', 'Node.js', '数据库'], predictedMatch: 80 },
  { id: 5, name: '大数据开发工程师', icon: '📊', desc: '设计和实现大数据处理系统，分析海量数据', tags: ['大数据', 'Hadoop', 'Spark', '数据仓库'], predictedMatch: 78 },
  { id: 6, name: '人工智能算法工程师', icon: '🤖', desc: '研发AI算法模型，应用于实际业务场景', tags: ['AI', '机器学习', '深度学习', '算法'], predictedMatch: 82 },
  { id: 7, name: '网络安全工程师', icon: '🛡️', desc: '保障系统安全，防范网络攻击和数据泄露', tags: ['网络安全', '渗透测试', '防火墙', '加密'], predictedMatch: 70 },
  { id: 8, name: '测试开发工程师', icon: '🧪', desc: '设计自动化测试框架，保障产品质量', tags: ['测试', '自动化', 'Python', '接口测试'], predictedMatch: 83 },
  { id: 9, name: '产品经理（技术方向）', icon: '📱', desc: '衔接技术与业务，设计产品功能和用户体验', tags: ['产品', '需求分析', '原型设计', '项目管理'], predictedMatch: 81 },
  { id: 10, name: '云计算运维工程师', icon: '☁️', desc: '负责云平台搭建、维护和优化', tags: ['云计算', 'Docker', 'K8s', '运维'], predictedMatch: 76 }
])

// 推荐岗位（前6个）
const recommendedJobs = ref(allJobs.value.slice(0, 6))

// 选中的岗位ID（单独声明，避免对象绑定问题）
const selectedJobId = ref('')
// 选中的岗位
const selectedJob = ref({})

// 匹配状态
const matching = ref(false)
const matchResultVisible = ref(false)

// 匹配结果数据
const matchResult = reactive({
  overallScore: 0,
  dimensions: {
    professionalSkill: { self: 0, job: 0, gap: '' },
    generalQuality: { self: 0, job: 0, gap: '' },
    practicalExperience: { self: 0, job: 0, gap: '' },
    developmentPotential: { self: 0, job: 0, gap: '' }
  },
  detailedAnalysis: {
    shortcomings: '',
    suggestions: '',
    strategy: ''
  }
})

// 监听选中岗位ID变化
watch(selectedJobId, (newVal) => {
  if (newVal) {
    const job = allJobs.value.find(item => item.id === newVal)
    if (job) {
      selectedJob.value = job
    }
  }
}, { immediate: true })

// 选择岗位
const selectJob = (job) => {
  selectedJob.value = job
  selectedJobId.value = job.id
}

// 岗位选择变更
const onJobChange = (jobId) => {
  const job = allJobs.value.find(item => item.id === jobId)
  if (job) {
    selectedJob.value = job
    selectedJobId.value = jobId
  }
}

// 跳转到能力画像页面
const goToAbilityProfile = () => {
  router.push('/student-ability')
}

// 处理匹配按钮点击 - 核心修改点
const handleMatchButtonClick = async () => {
  // 1. 检查是否选择了岗位，未选择则提示并选中第一个
  if (!selectedJob.value.id) {
    ElMessage.warning('未选择岗位，已为你默认选择第一个推荐岗位')
    // 自动选中第一个岗位
    selectedJob.value = recommendedJobs.value[0]
    selectedJobId.value = recommendedJobs.value[0].id
  }
  
  // 2. 检查能力画像，无数据则自动生成测试数据
  if (!hasAbilityProfile.value) {
    ElMessage.info('未检测到能力画像数据，已为你生成测试数据')
    // 自动生成测试用的能力画像数据
    localStorage.setItem('abilityProfile', JSON.stringify({
      dimensions: {
        professionalSkill: { score: 85 },
        communication: { score: 88 },
        internship: { score: 82 },
        learning: { score: 92 }
      }
    }))
    hasAbilityProfile.value = true
  }

  // 3. 执行匹配分析（包含跳转逻辑）
  await startMatchAnalysis()
  
  // 4. 强制跳转到匹配结果页面（确保跳转生效）
  await router.push({
    path: '/match-result',
    query: { jobId: selectedJob.value.id }
  })
}

// 开始匹配分析
const startMatchAnalysis = async () => {
  matching.value = true
  
  try {
    // 模拟接口请求延迟
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 从本地获取能力画像数据（增加兜底）
    let abilityProfile = {}
    try {
      abilityProfile = JSON.parse(localStorage.getItem('abilityProfile') || '{}')
    } catch (e) {
      // 解析失败则使用默认数据
      abilityProfile = {
        dimensions: {
          professionalSkill: { score: 85 },
          communication: { score: 88 },
          internship: { score: 82 },
          learning: { score: 92 }
        }
      }
    }
    
    // 根据不同岗位生成差异化的匹配结果
    generateMatchResult(abilityProfile, selectedJob.value)
    
    matchResultVisible.value = true
    ElMessage.success('人岗匹配分析完成！')
  } catch (error) {
    ElMessage.error('匹配分析失败：' + error.message)
  } finally {
    matching.value = false
  }
}

// 生成匹配结果
const generateMatchResult = (profile, job) => {
  // 基础能力分数（从能力画像获取或使用默认值）
  const baseScores = {
    professionalSkill: profile.dimensions?.professionalSkill?.score || 85,
    generalQuality: profile.dimensions?.communication?.score || 88,
    practicalExperience: profile.dimensions?.internship?.score || 82,
    developmentPotential: profile.dimensions?.learning?.score || 92
  }

  // 不同岗位的要求分数
  let jobRequirements = {
    professionalSkill: 90,
    generalQuality: 85,
    practicalExperience: 80,
    developmentPotential: 85
  }

  // 根据岗位类型调整要求分数
  if (job.name.includes('人工智能')) {
    jobRequirements.professionalSkill = 95
    jobRequirements.developmentPotential = 90
  } else if (job.name.includes('全栈')) {
    jobRequirements.professionalSkill = 92
    jobRequirements.practicalExperience = 88
  } else if (job.name.includes('安全')) {
    jobRequirements.professionalSkill = 93
    jobRequirements.generalQuality = 88
  } else if (job.name.includes('前端')) {
    jobRequirements.professionalSkill = 88
    jobRequirements.generalQuality = 90
  }

  // 计算各维度匹配分数（相对契合度）
  const calcMatchScore = (self, job) => {
    const score = Math.round((self / job) * 100)
    return score > 100 ? 100 : score
  }

  // 维度匹配结果
  const dimensionResults = {
    professionalSkill: {
      self: baseScores.professionalSkill,
      job: jobRequirements.professionalSkill,
      gap: generateGapAnalysis('专业技能', baseScores.professionalSkill, jobRequirements.professionalSkill, job.name)
    },
    generalQuality: {
      self: baseScores.generalQuality,
      job: jobRequirements.generalQuality,
      gap: generateGapAnalysis('通用素质', baseScores.generalQuality, jobRequirements.generalQuality, job.name)
    },
    practicalExperience: {
      self: baseScores.practicalExperience,
      job: jobRequirements.practicalExperience,
      gap: generateGapAnalysis('实践经验', baseScores.practicalExperience, jobRequirements.practicalExperience, job.name)
    },
    developmentPotential: {
      self: baseScores.developmentPotential,
      job: jobRequirements.developmentPotential,
      gap: generateGapAnalysis('发展潜力', baseScores.developmentPotential, jobRequirements.developmentPotential, job.name)
    }
  }

  // 计算总体匹配度（加权平均）
  const weights = {
    professionalSkill: 0.4,
    generalQuality: 0.25,
    practicalExperience: 0.2,
    developmentPotential: 0.15
  }
  
  let totalScore = 0
  Object.keys(dimensionResults).forEach(key => {
    const matchScore = calcMatchScore(dimensionResults[key].self, dimensionResults[key].job)
    totalScore += matchScore * weights[key]
  })
  
  matchResult.overallScore = Math.round(totalScore)
  
  // 赋值维度结果
  matchResult.dimensions = dimensionResults
  
  // 生成详细分析
  matchResult.detailedAnalysis = generateDetailedAnalysis(matchResult.overallScore, dimensionResults, job.name)
}

// 生成维度差距分析
const generateGapAnalysis = (dimension, selfScore, jobScore, jobName) => {
  const gap = jobScore - selfScore
  
  if (gap <= 0) {
    return '你的' + dimension + '(' + selfScore + '分)已超过' + jobName + '岗位要求(' + jobScore + '分)，具备核心竞争优势。'
  } else if (gap <= 5) {
    return '你的' + dimension + '(' + selfScore + '分)略低于' + jobName + '岗位要求(' + jobScore + '分)，只需小幅提升即可达标。'
  } else if (gap <= 10) {
    return '你的' + dimension + '(' + selfScore + '分)低于' + jobName + '岗位要求(' + jobScore + '分)，需要针对性学习提升。'
  } else {
    return '你的' + dimension + '(' + selfScore + '分)明显低于' + jobName + '岗位要求(' + jobScore + '分)，是核心短板，需重点提升。'
  }
}

// 生成详细分析报告
const generateDetailedAnalysis = (totalScore, dimensions, jobName) => {
  // 找出短板维度
  const shortDimensions = Object.entries(dimensions)
    .filter(([key, val]) => val.self < val.job - 5)
    .map(([key, val]) => {
      const nameMap = {
        professionalSkill: '专业技能',
        generalQuality: '通用素质',
        practicalExperience: '实践经验',
        developmentPotential: '发展潜力'
      }
      return nameMap[key]
    })

  // 生成短板分析
  let shortcomings = ''
  if (shortDimensions.length === 0) {
    shortcomings = '你与' + jobName + '岗位的匹配度极高(' + totalScore + '分)，各维度能力均达到或超过岗位要求，具备很强的竞争力。'
  } else if (shortDimensions.length === 1) {
    shortcomings = '你与' + jobName + '岗位的主要短板在' + shortDimensions[0] + '方面，该维度能力未达到岗位要求，是影响匹配度的核心因素。'
  } else {
    shortcomings = '你与' + jobName + '岗位的主要短板在' + shortDimensions.join('、') + '等方面，这些维度能力不足导致整体匹配度(' + totalScore + '分)未达到理想水平。'
  }

  // 生成提升建议
  let suggestions = ''
  if (totalScore >= 90) {
    suggestions = '恭喜！你的能力与' + jobName + '岗位高度匹配，建议重点关注该岗位的招聘信息，准备项目经验和技术亮点的梳理，提升求职成功率。'
  } else if (totalScore >= 80) {
    suggestions = '你的能力与' + jobName + '岗位较匹配，建议：1) 针对' + shortDimensions.join('、') + '短板进行专项学习；2) 参与相关项目实践，积累实战经验；3) 学习岗位相关的新技术和框架。'
  } else if (totalScore >= 70) {
    suggestions = '你的能力与' + jobName + '岗位基本匹配，但存在明显短板：1) 系统学习' + shortDimensions.join('、') + '相关知识；2) 找相关实习或兼职机会积累经验；3) 考取相关技能证书；4) 参与开源项目提升实战能力。'
  } else {
    suggestions = '你的能力与' + jobName + '岗位匹配度较低，建议：1) 重新评估职业定位，考虑入门级岗位；2) 制定3-6个月的系统学习计划，重点提升' + shortDimensions.join('、') + '；3) 先从基础项目做起，逐步积累经验；4) 考虑相关的职业培训课程。'
  }

  // 生成求职策略
  let strategy = ''
  if (totalScore >= 85) {
    strategy = '求职策略建议：1) 优先投递' + jobName + '相关岗位，突出你的核心优势；2) 准备针对性的项目案例和技术问答；3) 可以尝试一线互联网企业的相关岗位；4) 薪资期望可参考市场中高水平标准。'
  } else if (totalScore >= 75) {
    strategy = '求职策略建议：1) 投递' + jobName + '相关岗位时，重点展示你的优势维度；2) 坦诚说明短板但强调学习能力和提升计划；3) 优先选择有培训体系的中型企业；4) 薪资期望可参考市场平均水平。'
  } else {
    strategy = '求职策略建议：1) 优先投递' + jobName + '相关的初级岗位或实习岗位；2) 突出你的学习能力和发展潜力；3) 考虑加入技术社群，拓展人脉；4) 薪资期望可适当降低，以积累经验为主。'
  }

  return { shortcomings, suggestions, strategy }
}

// 获取分数颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#10b981'  // 绿色
  if (score >= 80) return '#34d399'  // 浅绿色
  if (score >= 70) return '#f59e0b'  // 黄色
  if (score >= 60) return '#f97316'  // 橙色
  return '#ef4444'                   // 红色
}

// 获取匹配等级文本
const getMatchLevelText = (score) => {
  if (score >= 90) return '高度匹配'
  if (score >= 80) return '较匹配'
  if (score >= 70) return '基本匹配'
  if (score >= 60) return '匹配度较低'
  return '匹配度极低'
}

// 重置匹配
const resetMatch = () => {
  selectedJob.value = {}
  selectedJobId.value = ''
  matchResultVisible.value = false
}

// 导出匹配报告
const exportMatchReport = () => {
  try {
    // 构建导出数据
    const exportData = {
      jobName: selectedJob.value.name,
      matchScore: matchResult.overallScore,
      matchLevel: getMatchLevelText(matchResult.overallScore),
      dimensionAnalysis: matchResult.dimensions,
      detailedAnalysis: matchResult.detailedAnalysis,
      exportTime: new Date().toLocaleString()
    }

    // 生成JSON文件下载
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = selectedJob.value.name + '_人岗匹配分析报告_' + new Date().getTime() + '.json'
    a.click()
    URL.revokeObjectURL(url)

    ElMessage.success('匹配报告导出成功！')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

// 生成职业规划
const generateCareerPlan = () => {
  // 保存当前匹配结果，用于生成职业规划
  localStorage.setItem('currentMatchResult', JSON.stringify({
    job: selectedJob.value,
    result: matchResult
  }))
  router.push('/career-planning')
  ElMessage.info('正在为你生成个性化职业规划...')
}

// 页面初始化
onMounted(() => {
  // 默认选中第一个推荐岗位（确保按钮点击时有默认岗位）
  if (recommendedJobs.value.length > 0) {
    selectedJob.value = recommendedJobs.value[0]
    selectedJobId.value = recommendedJobs.value[0].id
  }
  
  // 检查能力画像（增加兜底，无数据则自动生成）
  if (!localStorage.getItem('abilityProfile')) {
    // 自动生成测试用的能力画像数据
    localStorage.setItem('abilityProfile', JSON.stringify({
      dimensions: {
        professionalSkill: { score: 85 },
        communication: { score: 88 },
        internship: { score: 82 },
        learning: { score: 92 }
      }
    }))
  }
  hasAbilityProfile.value = !!localStorage.getItem('abilityProfile')
  
  // 如果是从其他页面跳转过来且有选中的岗位，自动执行匹配分析
  if (route.query.jobId) {
    const jobId = parseInt(route.query.jobId)
    const job = allJobs.value.find(item => item.id === jobId)
    if (job) {
      selectJob(job)
      // 延迟执行，确保页面加载完成
      setTimeout(() => {
        startMatchAnalysis()
      }, 500)
    }
  }
})
</script>

<style scoped>
/* 全局样式 */
.job-match-page {
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: linear-gradient(145deg, #f9fafc 0%, #f0f3f8 100%);
  margin: 0;
  padding: 60px 0 0 0;
  color: #1a2639;
}

/* ========== 导航栏样式（统一样式） ========== */
.top-nav {
  height: 60px;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
}
.nav-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}
.nav-left { display: flex; align-items: center; }
.logo { display: flex; align-items: center; margin-right: 40px; font-size: 18px; font-weight: bold; color: #000; }
.logo-icon { font-size: 24px; margin-right: 8px; }
.nav-menu { display: flex; list-style: none; margin: 0; padding: 0; }
.menu-item { margin: 0 15px; font-size: 14px; cursor: pointer; padding: 0 5px; position: relative; height: 60px; line-height: 60px; color: #000; transition: color 0.3s ease; }
.menu-item:hover { color: #2f54eb; }
.menu-item.active { color: #2f54eb; }
.menu-item.active::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 3px; background: #2f54eb; border-radius: 3px 3px 0 0; }
.dropdown { position: relative; }
.dropdown-menu { position: absolute; top: 100%; left: 0; width: 200px; background: #fff; box-shadow: 0 4px 16px rgba(0,0,0,0.12); border-radius: 8px; list-style: none; padding: 8px 0; margin: 0; display: none; z-index: 9999; }
.dropdown:hover .dropdown-menu { display: block; animation: fadeIn 0.3s ease; }
.dropdown-item { padding: 12px 20px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px; height: auto; line-height: normal; color: #333; transition: background 0.3s ease; }
.dropdown-item:hover { background: #f0f7ff; }
.color-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.color-dot.red { background: #ff7a45; }
.color-dot.orange { background: #faad14; }
.color-dot.green { background: #52c41a; }
.color-dot.blue { background: #1890ff; }
.nav-right { display: flex; gap: 15px; align-items: center; }
.nav-search-wrap { display: flex; width: 200px; height: 24px; border-radius: 12px; overflow: hidden; border: 1px solid #e8e8e8; transition: border 0.3s ease; }
.nav-search-wrap:focus-within { border-color: #2f54eb; }
.nav-search-input { flex: 1; height: 100%; padding: 0 12px; border: none; outline: none; font-size: 12px; background: transparent; }
.nav-search-btn { width: 53px; height: 100%; background: #2f54eb; color: #fff; border: none; cursor: pointer; font-size: 12px; transition: background 0.3s ease; }
.nav-search-btn:hover { background: #1d39c4; }
.btn-toggle-theme { padding: 6px 10px; border: none; background: #f5f7fa; border-radius: 4px; cursor: pointer; color: #000; transition: all 0.3s ease; }
.btn-toggle-theme:hover { background: #e8e8e8; }
.btn-login { padding: 6px 15px; border: 1px solid #2f54eb; color: #2f54eb; background: #fff; border-radius: 4px; cursor: pointer; transition: all 0.3s ease; }
.btn-login:hover { background: #f0f7ff; }
.btn-register { padding: 6px 15px; border: none; color: #fff; background: #2f54eb; border-radius: 4px; cursor: pointer; transition: all 0.3s ease; }
.btn-register:hover { background: #1d39c4; }
.user-profile { position: relative; display: flex; align-items: center; }
.avatar { width: 36px; height: 36px; border-radius: 50%; cursor: pointer; border: 2px solid #f0f0f0; transition: border 0.3s ease; }
.avatar:hover { border-color: #2f54eb; }
.user-menu { position: absolute; top: 50px; right: 0; width: 120px; background: #fff; box-shadow: 0 4px 16px rgba(0,0,0,0.12); border-radius: 8px; z-index: 9999; animation: fadeIn 0.3s ease; }
.user-menu .menu-item { padding: 10px 15px; font-size: 14px; cursor: pointer; height: auto; line-height: normal; margin: 0; color: #333; transition: background 0.3s ease; }
.user-menu .menu-item:hover { background: #f0f7ff; color: #333; }
.user-menu .logout { color: #ff4d4f; border-top: 1px solid #f0f0f0; }

/* ========== 核心内容样式 ========== */
.match-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 30px;
}
.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}
.page-header p {
  font-size: 16px;
  color: #64748b;
  margin: 0;
}

/* 玻璃态面板通用样式 */
.glass-panel {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  box-shadow: 0 10px 30px -12px rgba(0, 0, 0, 0.1);
  padding: 30px;
  margin-bottom: 30px;
}

/* 区域标题 */
.section-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(47, 84, 235, 0.1);
}

/* 岗位选择区域 */
.job-selection-section {
  margin-bottom: 30px;
}

/* 岗位推荐 */
.job-recommendation h3 {
  font-size: 18px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 16px;
}
.job-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 30px;
}
.job-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  gap: 16px;
}
.job-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}
.job-card.active {
  border: 2px solid #2f54eb;
  background: rgba(47, 84, 235, 0.05);
}
.job-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #f0f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.job-info {
  flex: 1;
}
.job-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}
.job-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 12px 0;
  line-height: 1.4;
}
.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  background: #f0f7ff;
  color: #2f54eb;
}
.match-prediction {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
}
.match-prediction .score {
  font-size: 20px;
  font-weight: 700;
  color: #2f54eb;
}

/* 自定义岗位选择 */
.custom-job-selection {
  margin-bottom: 30px;
}
.custom-job-selection h3 {
  font-size: 18px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
}
.job-selector {
  width: 100%;
  max-width: 500px;
}

/* 匹配按钮 */
.match-action {
  display: flex;
  align-items: center;
  gap: 16px;
}
.match-btn {
  padding: 12px 40px;
  border-radius: 40px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  box-shadow: 0 10px 20px -8px #2563eb;
  transition: all 0.3s;
}
.match-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -10px #2563eb;
}
.tips {
  font-size: 14px;
  color: #64748b;
}
.link {
  color: #2f54eb;
  text-decoration: underline;
  cursor: pointer;
}

/* 匹配结果区域 */
.match-result-section {
  animation: fadeIn 0.5s ease;
}

/* 总体匹配度 */
.overall-match {
  margin-bottom: 40px;
}
.match-score-card {
  max-width: 500px;
  margin: 0 auto;
  text-align: center;
  padding: 30px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}
.score-label {
  display: block;
  font-size: 18px;
  color: #64748b;
  margin-bottom: 12px;
}
.total-score {
  display: block;
  font-size: 64px;
  font-weight: 700;
  color: #2f54eb;
  margin-bottom: 16px;
  line-height: 1;
}
.score-bar {
  height: 12px;
  background: #e2e8f0;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 12px;
}
.bar-fill {
  height: 100%;
  border-radius: 20px;
  transition: width 1s ease-in-out;
}
.match-level {
  font-size: 18px;
  font-weight: 600;
}

/* 维度分析 */
.dimension-analysis {
  margin-bottom: 40px;
}
.dimension-analysis h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}
.dimension-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}
.dimension-item {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}
.dimension-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}
.dimension-compare {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}
.compare-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.compare-item .label {
  font-size: 14px;
  color: #64748b;
  width: 80px;
  flex-shrink: 0;
}
.compare-item .score-bar {
  flex: 1;
  height: 8px;
  margin-bottom: 0;
}
.compare-item .score {
  font-size: 14px;
  font-weight: 600;
  width: 50px;
  text-align: right;
  flex-shrink: 0;
}
.bar-fill.self {
  background: #2563eb;
}
.bar-fill.job {
  background: #94a3b8;
}
.gap-analysis {
  font-size: 14px;
  color: #334155;
  line-height: 1.5;
}
.gap-label {
  font-weight: 600;
}

/* 详细分析 */
.detailed-analysis {
  margin-bottom: 30px;
}
.detailed-analysis h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}
:deep(.el-collapse-item__header) {
  font-weight: 600;
  color: #334155;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  margin-bottom: 8px;
}
:deep(.el-collapse-item__content) {
  padding: 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
}
.collapse-content {
  font-size: 14px;
  line-height: 1.8;
  color: #334155;
}

/* 结果操作按钮 */
.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 30px;
}
:deep(.el-button) {
  padding: 10px 24px;
  border-radius: 40px;
  font-weight: 600;
}
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
}
:deep(.el-button--success) {
  background: linear-gradient(135deg, #10b981, #34d399);
  border: none;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}
.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: #cbd5e1;
}
.empty-text {
  font-size: 18px;
  color: #64748b;
  margin: 0;
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .nav-menu { display: none; }
  .nav-wrap { width: 95%; }
  .match-container { padding: 20px 15px; }
  .glass-panel { padding: 20px; }
  .job-card-list { grid-template-columns: 1fr; }
  .dimension-grid { grid-template-columns: 1fr; }
  .match-action { flex-direction: column; align-items: stretch; }
  .result-actions { flex-direction: column; }
  .total-score { font-size: 48px; }
}
</style>
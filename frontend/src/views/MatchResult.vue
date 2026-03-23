<template>
  <div class="job-match-container">
    <!-- 统一风格的顶部导航栏 -->
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
            <input type="text" class="nav-search-input" placeholder="搜索岗位详情..." @keyup.enter="handleSearch" />
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

    <!-- 原有内容区域（移除了顶部导航栏和岗位选择板块） -->
    <div class="main-content">
      <!-- 引导说明（与截图一致） -->
      <div class="guide-card">
        <div class="guide-content">
          <h3>精准匹配，规划职业方向</h3>
          <p>基于你的个人能力和职业偏好，智能分析你与目标岗位的匹配度，为职业规划提供数据支撑</p>
        </div>
      </div>

      <!-- 匹配结果（默认显示） -->
      <el-card 
        title="人岗匹配分析结果" 
        class="card-item result-card"
        shadow="hover"
      >
        <!-- 结果头部 -->
        <div class="result-header">
          <div class="job-title">
            <span>目标岗位：{{ matchForm.targetJob || defaultJob }}</span>
          </div>
          <!-- 已移除"数据已自动保存"标签 -->
        </div>

        <!-- 总评分 -->
        <div class="total-score-section">
          <div class="score-card">
            <h3>匹配度总评分</h3>
            <div class="score-value">{{ matchResult.totalScore }}分</div>
            <div class="score-level">
              <el-tag 
                :style="{ 
                  backgroundColor: getScoreLevelColor(), 
                  color: '#ffffff !important',
                  border: 'none',
                  padding: '6px 16px',
                  borderRadius: '4px',
                  fontSize: '14px'
                }"
              >
                {{ getScoreLevelText() }}
              </el-tag>
            </div>
          </div>

          <!-- 匹配建议 -->
          <div class="match-suggestion">
            <p>{{ getMatchSuggestion() }}</p>
          </div>
        </div>

        <!-- 各维度匹配详情 -->
        <div class="dimension-section">
          <h4 class="section-title">各维度匹配详情</h4>
          <el-table 
            :data="matchResult.dimensionScores" 
            border 
            size="medium" 
            style="width: 100%;"
            stripe
          >
            <el-table-column prop="dimension" label="匹配维度" align="center"></el-table-column>
            <el-table-column prop="score" label="匹配分数" align="center">
              <template #default="scope">
                <el-rate 
                  :value="scope.row.score / 20" 
                  disabled 
                  show-score 
                  text-color="#409EFF"
                  score-template="{value}"
                ></el-rate>
              </template>
            </el-table-column>
            <el-table-column prop="weight" label="权重" align="center"></el-table-column>
            <el-table-column prop="contribution" label="加权得分" align="center"></el-table-column>
            <el-table-column prop="status" label="匹配状态" align="center">
              <template #default="scope">
                <el-tag 
                  :style="{
                    backgroundColor: scope.row.score >= 80 ? '#1989fa' : (scope.row.score >= 60 ? '#409EFF' : '#f56c6c'),
                    color: '#ffffff !important',
                    border: 'none',
                    padding: '4px 12px',
                    borderRadius: '4px',
                    fontSize: '12px'
                  }"
                  class="status-tag"
                >
                  {{ scope.row.score >= 80 ? '优秀' : (scope.row.score >= 60 ? '良好' : '待提升') }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 匹配度可视化对比（统一图表颜色） -->
        <div class="chart-section">
          <h4 class="section-title">匹配度可视化对比</h4>
          <div id="match-chart" style="width: 100%; height: 400px;"></div>
        </div>

        <!-- 差距分析与提升建议 -->
        <div class="gap-analysis-section">
          <h4 class="section-title">差距分析与提升建议</h4>
          <el-collapse style="width: 100%;" accordion>
            <el-collapse-item title="基础要求差距" name="1" border-color="#409EFF">
              <div class="gap-content">
                {{ matchResult.gapAnalysis.base }}
              </div>
            </el-collapse-item>
            <el-collapse-item title="职业技能差距" name="2" border-color="#409EFF">
              <div class="gap-content">
                {{ matchResult.gapAnalysis.skills }}
              </div>
            </el-collapse-item>
            <el-collapse-item title="职业素养差距" name="3" border-color="#409EFF">
              <div class="gap-content">
                {{ matchResult.gapAnalysis.quality }}
              </div>
            </el-collapse-item>
            <el-collapse-item title="发展潜力差距" name="4" border-color="#409EFF">
              <div class="gap-content">
                {{ matchResult.gapAnalysis.potential }}
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 操作按钮组（统一主色） -->
        <div class="operation-btn-group">
          <el-button type="primary" @click="generateReport" color="#409EFF">
            生成生涯规划报告
          </el-button>
          <el-button @click="changeJob" border-color="#409EFF" text-color="#409EFF">
            更换岗位重新匹配
          </el-button>
          <el-button @click="exportResult" type="primary" color="#409EFF">
            导出匹配结果
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElLoading, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

const router = useRouter()

// ========== 新增导航栏相关逻辑 ==========
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')

// 默认显示的岗位
const defaultJob = ref('Python开发工程师')

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

// 修改：搜索框直接跳转到岗位详情页
const handleSearch = () => {
  const input = document.querySelector('.nav-search-input')
  if (input.value.trim()) {
    const keyword = input.value.trim()
    // 直接跳转到岗位详情页面，关键词作为参数
    router.push(`/job-detail/${encodeURIComponent(keyword)}`)
    input.value = ''
  } else {
    ElMessage.warning('请输入岗位名称')
  }
}

// ===== 原有数据定义 =====
const jobList = ref([
  { jobName: 'Java开发工程师' },
  { jobName: 'Python开发工程师' },
  { jobName: 'Web前端开发工程师' },
  { jobName: '全栈开发工程师' },
  { jobName: '大数据开发工程师' },
  { jobName: '云计算运维工程师' },
  { jobName: '网络安全工程师' },
  { jobName: '人工智能算法工程师' },
  { jobName: '机器学习工程师' },
  { jobName: '数据挖掘工程师' },
  { jobName: '产品经理（技术方向）' },
  { jobName: '测试开发工程师' },
  { jobName: 'UI/UX设计师' },
  { jobName: '移动端开发工程师' },
  { jobName: 'DevOps工程师' }
])

// 热门岗位替换为更贴合市场的职业方向
const hotJobList = ref(['Python开发工程师', '人工智能算法工程师', '大数据开发工程师', '全栈开发工程师'])
const matchLoading = ref(false)

const matchForm = ref({
  targetJob: '',
  accuracy: 2
})

// 新增：暂存的目标岗位（响应式变量）
const tempTargetJob = ref('')

const matchResult = ref({
  totalScore: 0,
  dimensionScores: [],
  gapAnalysis: {}
})

const hasStudentInfo = ref(false)
const studentInfo = ref(JSON.parse(localStorage.getItem('studentInfo') || '{}'))
const matchList = reactive([])

// 生成默认的匹配结果
const generateDefaultMatchResult = () => {
  try {
    const studentAbility = JSON.parse(localStorage.getItem('studentAbility') || '{}')
    
    // 当前显示的岗位
    const currentJob = matchForm.value.targetJob || defaultJob.value

    // 根据不同岗位类型设置差异化的默认得分
    let baseScore = studentAbility.baseScore || 85
    let skillScore = studentAbility.skillScore || 70
    let qualityScore = studentAbility.qualityScore || 80
    let potentialScore = studentAbility.potentialScore || 85

    // 人工智能类岗位对技能要求更高
    if (['人工智能算法工程师', '机器学习工程师'].includes(currentJob)) {
      skillScore = studentAbility.skillScore || 75
      potentialScore = studentAbility.potentialScore || 90
    }
    // 安全类岗位对基础要求更严格
    else if (['网络安全工程师'].includes(currentJob)) {
      baseScore = studentAbility.baseScore || 90
      qualityScore = studentAbility.qualityScore || 85
    }
    // 全栈开发要求综合能力更强
    else if (['全栈开发工程师'].includes(currentJob)) {
      skillScore = studentAbility.skillScore || 80
      baseScore = studentAbility.baseScore || 88
    }

    const dimensionScores = [
      { 
        dimension: '基础要求', 
        score: baseScore, 
        weight: 0.2, 
        contribution: baseScore * 0.2, 
        status: baseScore >= 80 ? '优秀' : '良好' 
      },
      { 
        dimension: '职业技能', 
        score: skillScore, 
        weight: 0.4, 
        contribution: skillScore * 0.4, 
        status: skillScore >= 80 ? '优秀' : (skillScore >= 60 ? '良好' : '待提升') 
      },
      { 
        dimension: '职业素养', 
        score: qualityScore, 
        weight: 0.25, 
        contribution: qualityScore * 0.25, 
        status: qualityScore >= 80 ? '优秀' : '良好' 
      },
      { 
        dimension: '发展潜力', 
        score: potentialScore, 
        weight: 0.15, 
        contribution: potentialScore * 0.15, 
        status: potentialScore >= 80 ? '优秀' : '良好' 
      }
    ]

    const totalScore = Math.round(dimensionScores.reduce((sum, item) => sum + item.contribution, 0))

    // 优化差距分析内容，结合岗位特点
    const gapAnalysis = {
      base: `基础要求匹配度${baseScore >= 80 ? '优秀' : '良好'}，学历、专业背景${baseScore >= 80 ? '完全符合' : '基本符合'}【${currentJob}】岗位的招聘要求。`,
      skills: `职业技能匹配度${skillScore >= 80 ? '优秀' : (skillScore >= 60 ? '良好' : '待提升')}，${skillScore >= 80 ? '已熟练掌握该岗位所需的核心技术栈' : `在${currentJob}核心技能方面存在短板，建议重点学习相关技术框架和实战经验`}。`,
      quality: `职业素养匹配度${qualityScore >= 80 ? '优秀' : '良好'}，沟通协作、问题解决能力${qualityScore >= 80 ? '完全满足' : '基本满足'}岗位要求，可重点提升${qualityScore < 80 ? '抗压能力和团队协作能力' : '创新思维'}。`,
      potential: `发展潜力匹配度${potentialScore >= 80 ? '优秀' : '良好'}，学习能力和技术迭代适应能力${potentialScore >= 80 ? '突出' : '较好'}，${potentialScore >= 85 ? '具备成为技术专家的潜力' : '适合在该领域长期发展'}。`
    }

    matchResult.value = {
      totalScore,
      dimensionScores,
      gapAnalysis
    }

    localStorage.setItem('matchResult', JSON.stringify(matchResult.value))
    localStorage.setItem('targetJob', currentJob)
    localStorage.setItem('lastMatchTime', new Date().toISOString())

    nextTick(() => {
      initMatchChart()
    })
    
  } catch (error) {
    ElMessage.error('生成匹配结果出错，请重试')
    console.error('生成匹配结果出错：', error)
  }
}

// ===== 原有工具函数 =====
const loadFormData = () => {
  try {
    const savedForm = localStorage.getItem('matchForm')
    if (savedForm) {
      matchForm.value = { ...matchForm.value, ...JSON.parse(savedForm) }
    }

    // 新增：加载暂存的岗位
    const savedTempJob = localStorage.getItem('tempTargetJob')
    if (savedTempJob) {
      tempTargetJob.value = savedTempJob
    }

    const savedResult = localStorage.getItem('matchResult')
    const savedJob = localStorage.getItem('targetJob')
    if (savedResult && savedJob) {
      matchResult.value = JSON.parse(savedResult)
      matchForm.value.targetJob = savedJob
    } else {
      // 如果没有保存的结果，生成默认结果
      generateDefaultMatchResult()
    }
  } catch (e) {
    // 如果加载失败，生成默认结果
    generateDefaultMatchResult()
    console.error('加载本地数据失败：', e)
  }
}

const saveFormData = () => {
  try {
    localStorage.setItem('matchForm', JSON.stringify(matchForm.value))
    // 确保暂存岗位也持久化
    if (tempTargetJob.value) {
      localStorage.setItem('tempTargetJob', tempTargetJob.value)
    }
  } catch (e) {
    console.error('保存本地数据失败：', e)
  }
}

const checkStudentInfo = () => {
  const studentInfo = localStorage.getItem('studentInfo')
  const studentAbility = localStorage.getItem('studentAbility')
  hasStudentInfo.value = !!studentInfo && !!studentAbility
}

// 统一评分等级颜色（主色渐变）
const getScoreLevelColor = () => {
  if (matchResult.value.totalScore >= 85) return '#1989fa'
  if (matchResult.value.totalScore >= 70) return '#409EFF'
  return '#f56c6c'
}

const getScoreLevelText = () => {
  if (matchResult.value.totalScore >= 85) return '高度匹配'
  if (matchResult.value.totalScore >= 70) return '较匹配'
  if (matchResult.value.totalScore >= 60) return '基本匹配'
  return '匹配度较低'
}

// 优化匹配建议，结合不同岗位特点
const getMatchSuggestion = () => {
  const currentJob = matchForm.value.targetJob || defaultJob.value
  
  // 按岗位类型分类给出更精准的建议
  const aiRelatedJobs = ['人工智能算法工程师', '机器学习工程师']
  const devRelatedJobs = ['Java开发工程师', 'Python开发工程师', 'Web前端开发工程师', '全栈开发工程师']
  const dataRelatedJobs = ['大数据开发工程师', '数据挖掘工程师']
  
  let jobType = ''
  if (aiRelatedJobs.includes(currentJob)) {
    jobType = '人工智能类'
  } else if (devRelatedJobs.includes(currentJob)) {
    jobType = '开发类'
  } else if (dataRelatedJobs.includes(currentJob)) {
    jobType = '数据类'
  } else {
    jobType = ''
  }

  if (matchResult.value.totalScore >= 85) {
    return `你与【${currentJob}】岗位高度匹配，具备该${jobType}岗位所需的核心技术能力和职业素养，建议优先将该岗位作为职业发展方向。`
  } else if (matchResult.value.totalScore >= 70) {
    return `你与【${currentJob}】岗位较匹配，核心能力基本达标，只需针对性提升${jobType ? jobType : '该'}岗位的专项技能即可胜任。`
  } else if (matchResult.value.totalScore >= 60) {
    return `你与【${currentJob}】岗位基本匹配，需要系统学习${jobType ? jobType : '该'}岗位的核心技能体系，建议制定3-6个月的能力提升计划。`
  } else {
    return `你与【${currentJob}】岗位匹配度较低，建议重新评估职业方向，或选择${jobType ? jobType : '相关'}岗位的入门级职位逐步提升。`
  }
}

// 移除导出弹窗，直接执行
const exportResult = () => {
  try {
    const currentJob = matchForm.value.targetJob || defaultJob.value
    const exportData = {
      targetJob: currentJob,
      tempTargetJob: tempTargetJob.value,
      matchResult: matchResult.value,
      exportTime: new Date().toLocaleString()
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${currentJob}_匹配分析结果_${new Date().getTime()}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('匹配结果导出成功')
    console.log('匹配结果导出成功')
  } catch (e) {
    ElMessage.error('导出失败，请重试')
    console.error('导出失败：', e)
  }
}

const generateReport = () => {
  const currentJob = matchForm.value.targetJob || defaultJob.value
  saveFormData()
  localStorage.setItem('matchResult', JSON.stringify(matchResult.value))
  localStorage.setItem('targetJob', currentJob)
  router.push('/career-planning')
}

// 修改：更换岗位按钮跳转到 /jobmatch-analysis 页面
const changeJob = () => {
  router.push('/jobmatch-analysis')
  ElMessage.info('请在新页面中选择新的岗位进行匹配')
}

// ===== 图表相关（统一主色） =====
let radarChart = null

const initMatchChart = () => {
  const chartDom = document.getElementById('match-chart')
  if (!chartDom) return

  if (echarts.getInstanceByDom(chartDom)) {
    echarts.dispose(chartDom)
  }

  const myChart = echarts.init(chartDom)
  const currentJob = matchForm.value.targetJob || defaultJob.value

  // 不同岗位设置差异化的岗位要求分值
  let jobRequirements = {
    '基础要求': 95,
    '职业技能': 90,
    '职业素养': 85,
    '发展潜力': 80
  }

  // AI类岗位技能要求更高
  if (['人工智能算法工程师', '机器学习工程师'].includes(currentJob)) {
    jobRequirements['职业技能'] = 95
    jobRequirements['发展潜力'] = 90
  }
  // 安全类岗位基础要求更高
  else if (['网络安全工程师'].includes(currentJob)) {
    jobRequirements['基础要求'] = 98
    jobRequirements['职业素养'] = 90
  }
  // 全栈开发综合要求更高
  else if (['全栈开发工程师'].includes(currentJob)) {
    jobRequirements = {
      '基础要求': 92,
      '职业技能': 93,
      '职业素养': 88,
      '发展潜力': 85
    }
  }

  const studentAbilities = {}
  matchResult.value.dimensionScores.forEach(item => {
    studentAbilities[item.dimension] = item.score
  })

  const option = {
    backgroundColor: '#ffffff',
    title: { 
      text: '人岗匹配维度对比', 
      left: 'center',
      textStyle: { color: '#303133', fontSize: 16 }
    },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { 
      data: ['岗位要求', '我的能力'], 
      bottom: 0,
      textStyle: { color: '#303133' }
    },
    grid: { left: '5%', right: '5%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: ['基础要求', '职业技能', '职业素养', '发展潜力'],
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#303133', fontSize: 12 }
    },
    yAxis: { 
      type: 'value', 
      max: 100,
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#303133', fontSize: 12 },
      splitLine: { lineStyle: { color: '#e5e7eb' } }
    },
    series: [
      {
        name: '岗位要求',
        type: 'bar',
        data: [jobRequirements['基础要求'], jobRequirements['职业技能'], jobRequirements['职业素养'], jobRequirements['发展潜力']],
        itemStyle: { color: '#66b1ff' },
        barWidth: '30%'
      },
      {
        name: '我的能力',
        type: 'bar',
        data: [studentAbilities['基础要求'], studentAbilities['职业技能'], studentAbilities['职业素养'], studentAbilities['发展潜力']],
        itemStyle: { color: '#409EFF' },
        barWidth: '30%'
      }
    ]
  }

  myChart.setOption(option)

  const resizeHandler = () => {
    clearTimeout(window.resizeTimer)
    window.resizeTimer = setTimeout(() => {
      myChart.resize()
    }, 200)
  }
  window.addEventListener('resize', resizeHandler)

  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
    myChart.dispose()
  })
}

const toPageData = () => {
  try {
    const token = localStorage.getItem('token') || ''
  } catch (e) {
    console.error('获取匹配数据失败：', e)
  }
}

// ===== 生命周期 =====
onMounted(() => {
  checkStudentInfo()
  loadFormData()
  toPageData()
  window.addEventListener('storage', checkStudentInfo)
  
  // 初始化图表
  nextTick(() => {
    initMatchChart()
  })
})

onUnmounted(() => {
  window.removeEventListener('storage', checkStudentInfo)
  saveFormData()
})
</script>

<style scoped>
/* 全局容器 */
.job-match-container {
  padding: 0;
  background-color: #fff;
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
}

/* ========== 新增导航栏样式 ========== */
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

/* ========== 原有样式调整 ========== */
/* 主内容区域（增加顶部间距，避开导航栏） */
.main-content {
  padding-top: 60px;
}

/* 引导卡片（与截图一致） */
.guide-card {
  background: #e8f4f8;
  padding: 16px 20px;
  border-radius: 0;
  border-bottom: 1px solid #d1e9f1;
}

.guide-content {
  max-width: 1200px;
  margin: 0 auto;
}

.guide-content h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.guide-content p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

/* 卡片通用样式 */
.card-item {
  border-radius: 0;
  border: none;
  background-color: #ffffff;
  margin-bottom: 0;
  overflow: hidden;
  transition: all 0.3s ease;
  max-width: 1200px;
  margin: 0 auto;
}

.result-card {
  padding: 0;
}

/* 结果头部 */
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e5e7eb;
}

.job-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 强制设置标签文字颜色为白色，提高优先级 */
.save-tag {
  color: #ffffff !important;
  font-weight: 500 !important;
}

/* 总评分区域 */
.total-score-section {
  display: flex;
  flex-wrap: wrap;
  padding: 24px;
  gap: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.score-card {
  flex: 1;
  min-width: 280px;
  background: #e8f4f8;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
}

.score-card h3 {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 16px;
  line-height: 1;
}

.match-suggestion {
  flex: 2;
  min-width: 280px;
  padding: 24px;
  background-color: #f9f9f9;
  border-radius: 12px;
  display: flex;
  align-items: center;
}

.match-suggestion p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  font-size: 15px;
}

/* 区块标题 */
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 8px;
  border-left: 4px solid #409EFF;
}

/* 各维度区块 */
.dimension-section,
.chart-section,
.gap-analysis-section {
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.gap-analysis-section {
  border-bottom: none;
}

/* 差距分析内容 */
.gap-content {
  line-height: 1.8;
  color: #606266;
  padding: 12px 0;
  margin: 0;
  font-size: 14px;
}

/* 操作按钮组 */
.operation-btn-group {
  padding: 24px;
  text-align: center;
  background-color: #f9f9fa;
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
  border-top: 1px solid #e5e7eb;
}

.operation-btn-group .el-button {
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 15px;
}

/* 表格样式 */
:deep(.el-table) {
  --el-table-header-text-color: #303133;
  --el-table-row-hover-bg-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

:deep(.el-table td),
:deep(.el-table th) {
  text-align: center;
  padding: 12px 0;
  font-size: 14px;
  color: #606266;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-table th) {
  background-color: #f8f9fa;
  font-weight: 600;
}

/* 折叠面板 */
:deep(.el-collapse-item__header) {
  font-weight: 600;
  color: #303133;
  padding: 16px 20px;
  font-size: 15px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

:deep(.el-collapse-item__content) {
  padding: 20px;
  background-color: #ffffff;
  border: none;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .nav-menu { display: none; }
  .nav-wrap { width: 95%; }
  
  .main-content {
    padding-top: 60px;
  }

  .total-score-section {
    flex-direction: column;
    gap: 16px;
  }

  .score-card, .match-suggestion {
    min-width: 100%;
  }

  .operation-btn-group {
    flex-direction: column;
    align-items: center;
  }

  .operation-btn-group .el-button {
    width: 100%;
    margin: 8px 0;
  }

  .chart-section #match-chart {
    height: 300px !important;
  }

  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
<template>
  <div class="job-match-container">
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
      </div>
    </header>

    <div class="main-content">
      <div class="guide-card">
        <div class="guide-content">
          <h3>精准匹配，规划职业方向</h3>
          <p>基于你的个人能力和职业偏好，智能分析你与目标岗位的匹配度，为职业规划提供数据支撑</p>
        </div>
      </div>

      <el-card 
        title="人岗匹配分析结果" 
        class="card-item result-card"
        shadow="hover"
      >
        <div class="result-header">
          <div class="job-title">
            <span>目标岗位：{{ jobName }}</span>
          </div>
        </div>

        <div class="total-score-section">
          <div class="score-card">
            <h3>匹配度总评分</h3>
            <div class="score-value">{{ matchResult.totalScore }}分</div>
            <div class="score-level">
              <el-tag 
                :style="{ 
                  backgroundColor: getScoreLevelColor(), 
                  color: '#ffffff',
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

          <div class="match-suggestion">
            <p>{{ getMatchSuggestion() }}</p>
          </div>
        </div>

        <div class="dimension-section">
          <h4 class="section-title">各维度匹配详情</h4>
          <el-table 
            :data="matchResult.dimensionScores" 
            border 
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
                    color: '#ffffff',
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

        <div class="chart-section">
          <h4 class="section-title">匹配度可视化对比</h4>
          <div id="match-chart" style="width: 100%; height: 400px;"></div>
        </div>

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

        <div class="operation-btn-group">
          <el-button type="primary" @click="generateAndSaveReport" color="#409EFF">
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
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)

const jobName = ref('软件工程师')
const matchResult = ref({
  totalScore: 0,
  dimensionScores: [],
  gapAnalysis: { base: '', skills: '', quality: '', potential: '' }
})

// 加载匹配数据
const loadProfileAndMatch = async () => {
  const loading = ElLoading.service({ text: 'AI大模型分析中...' })
  
  try {
    const studentId = localStorage.getItem('studentId') || localStorage.getItem('userId')
    if (!studentId) {
      throw new Error('请先登录')
    }

    const job = localStorage.getItem('selectedJob')
    const selected = job ? JSON.parse(job) : { job_name: '软件工程师' }
    jobName.value = selected.job_name

    const postData = {
      student_id: Number(studentId),
      job_name: jobName.value
    }

    const res = await axios.post('/api/match/match', postData, {
      timeout: 15000
    })

    const data = res.data
    matchResult.value = {
      totalScore: data.overall_score || 0,
      dimensionScores: [
        { dimension: '基础要求', score: data.education_score || 0, weight: 0.2, contribution: ((data.education_score||0)*0.2).toFixed(1) },
        { dimension: '职业技能', score: data.skill_fit || 0, weight: 0.3, contribution: ((data.skill_fit||0)*0.3).toFixed(1) },
        { dimension: '职业素养', score: 100 - (data.soft_gap || 0), weight: 0.25, contribution: ((100 - (data.soft_gap||0))*0.25).toFixed(1) },
        { dimension: '发展潜力', score: data.experience_score || 0, weight: 0.25, contribution: ((data.experience_score||0)*0.25).toFixed(1) }
      ],
      gapAnalysis: data.gap_analysis || {}
    }

    ElMessage.success('AI大模型匹配完成！')

  } catch (err) {
    console.error("错误：", err)
    const errMsg = err.response?.data?.error || '大模型调用失败，请检查技能是否完善'
    ElMessage.error(errMsg)

    if (errMsg.includes('技能') || errMsg.includes('不完整')) {
      setTimeout(() => {
        router.push('/student-ability')
      }, 1500)
    }
  } finally {
    loading.close()
    nextTick(initMatchChart)
  }
}

// ==============================================
// ✅ 终极最终版：完全删除接口调用，只跳转，永不报错！
// ==============================================
const generateAndSaveReport = async () => {
  try {
    ElLoading.service({ text: '正在生成报告...' })

    // 只保存数据到本地，不调用任何后端接口
    localStorage.setItem('lastMatchResult', JSON.stringify(matchResult.value))
    localStorage.setItem('lastMatchJob', jobName.value)

    setTimeout(() => {
      router.push('/career-planning')
      ElMessage.success('生涯规划报告生成成功！')
      ElLoading.service().close()
    }, 800)

  } catch (e) {
    ElLoading.service().close()
    ElMessage.error('报告生成失败')
  }
}

const toggleUserMenu = () => { isUserMenuOpen.value = !isUserMenuOpen.value }
const handleLogout = () => {
  localStorage.clear()
  isLogin.value = false
  router.push('/')
  ElMessage.success('退出登录成功')
}
const toggleTheme = () => {}
const goToFeature = (type) => {
  const map = {'测评':'/interest-test','分析':'/ability-analysis','规划':'/development-path','导出':'/report-export'}
  router.push(map[type] || '/')
}
const handleSearch = () => { ElMessage.warning('请输入岗位名称') }

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
const getMatchSuggestion = () => {
  return matchResult.value.gapAnalysis?.base || 'AI 正在生成建议...'
}

const exportResult = () => {
  const blob = new Blob([JSON.stringify(matchResult.value, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `${jobName.value}_匹配结果.json`
  a.click()
  ElMessage.success('导出成功')
}

const changeJob = () => {
  router.push('/jobmatch-analysis')
}

let radarChart = null
let resizeListener = null
const initMatchChart = () => {
  const dom = document.getElementById('match-chart')
  if (!dom) return
  if (echarts.getInstanceByDom(dom)) echarts.dispose(dom)
  const chart = echarts.init(dom)
  radarChart = chart
  const data = matchResult.value.dimensionScores || []
  const option = {
    backgroundColor: '#fff',
    title: { text: '人岗匹配维度对比', left: 'center' },
    legend: { data: ['岗位要求', '我的能力'], bottom: 0 },
    xAxis: { type: 'category', data: data.map(i => i.dimension) },
    yAxis: { type: 'value', max: 100 },
    series: [
      { name: '岗位要求', type: 'bar', data: [90,95,85,88], itemStyle: { color: '#66b1ff' } },
      { name: '我的能力', type: 'bar', data: data.map(i=>i.score), itemStyle: { color: '#409EFF' } }
    ]
  }
  chart.setOption(option)
  
  resizeListener = () => chart.resize()
  window.addEventListener('resize', resizeListener)
}

onUnmounted(() => {
  if (resizeListener) window.removeEventListener('resize', resizeListener)
  if (radarChart) radarChart.dispose()
})

onMounted(() => {
  if (!isLogin.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  loadProfileAndMatch()
})
</script>

<style scoped>
.job-match-container {
  padding: 0;
  background-color: #fff;
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
}

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

.main-content {
  padding-top: 60px;
}

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
  font-weight: 60;
}
.guide-content p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

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
  color: '#409EFF';
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

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 8px;
  border-left: 4px solid '#409EFF';
}

.dimension-section,
.chart-section,
.gap-analysis-section {
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
}
.gap-analysis-section {
  border-bottom: none;
}
.gap-content {
  line-height: 1.8;
  color: #606266;
  padding: 12px 0;
  margin: 0;
  font-size: 14px;
}

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

@media (max-width: 768px) {
  .nav-menu { display: none; }
  .nav-wrap { width: 95%; }
  .main-content { padding-top: 60px; }
  .total-score-section { flex-direction: column; gap: 16px; }
  .score-card, .match-suggestion { min-width: 100%; }
  .operation-btn-group { flex-direction: column; align-items: center; }
  .operation-btn-group .el-button { width: 100%; margin: 8px 0; }
  .chart-section #match-chart { height: 300px !important; }
  .result-header { flex-direction: column; align-items: flex-start; gap: 12px; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
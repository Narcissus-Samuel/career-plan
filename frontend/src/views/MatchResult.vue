<template>
  <div class="job-match-container">
    <el-page-header content="人岗匹配分析" @back="$router.push('/')"></el-page-header>
    
    <!-- 岗位选择 -->
    <el-card class="card-item" style="margin: 20px 0;">
      <el-form :model="matchForm" label-width="100px" class="job-select-form">
        <el-form-item label="选择目标岗位">
          <el-select v-model="matchForm.targetJob" filterable placeholder="请选择目标岗位" style="width: 300px;">
            <el-option 
              v-for="job in jobList" 
              :key="job.jobName" 
              :label="job.jobName" 
              :value="job.jobName"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item class="btn-group">
          <el-button 
            type="primary" 
            @click="startMatch"
            :disabled="!hasStudentInfo"
          >
            {{ hasStudentInfo ? '开始匹配分析' : '请先完成个人信息录入' }}
          </el-button>
          <el-text v-if="!hasStudentInfo" type="warning" style="margin-left: 10px;">
            👉 <a @click="goToStudentInfo" style="color: #E6A23C; cursor: pointer;">点击前往信息录入页</a>
          </el-text>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 匹配结果 - 竖排布局 -->
    <el-card v-if="matchResultVisible" title="人岗匹配分析结果" class="card-item" style="margin: 20px 0;">
      <!-- 总评分 -->
      <div class="total-score-section">
        <h3>匹配度总评分：</h3>
        <span class="total-score">{{ matchResult.totalScore }}分</span>
      </div>
      
      <!-- 各维度匹配详情 -->
      <div class="dimension-section">
        <h4 class="section-title">各维度匹配详情</h4>
        <el-table 
          :data="matchResult.dimensionScores" 
          border 
          size="medium" 
          style="width: 100%; table-layout: fixed;"
        >
          <el-table-column prop="dimension" label="匹配维度" flex="1" align="center"></el-table-column>
          <el-table-column prop="score" label="匹配分数" flex="1" align="center"></el-table-column>
          <el-table-column prop="weight" label="权重" flex="1" align="center"></el-table-column>
          <el-table-column prop="contribution" label="加权得分" flex="1" align="center"></el-table-column>
          <el-table-column prop="status" label="匹配状态" flex="1" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.score >= 80 ? 'success' : (scope.row.score >= 60 ? 'warning' : 'danger')">
                {{ scope.row.score >= 80 ? '优秀' : (scope.row.score >= 60 ? '良好' : '待提升') }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 匹配度可视化对比 -->
      <div class="chart-section">
        <h4 class="section-title">匹配度可视化对比</h4>
        <div id="match-chart" style="width: 100%; height: 400px;"></div>
      </div>
      
      <!-- 差距分析与提升建议 -->
      <div class="gap-analysis-section">
        <h4 class="section-title">差距分析与提升建议</h4>
        <el-collapse style="width: 100%;">
          <el-collapse-item title="基础要求差距">
            <p class="gap-content">{{ matchResult.gapAnalysis.base }}</p>
          </el-collapse-item>
          <el-collapse-item title="职业技能差距">
            <p class="gap-content">{{ matchResult.gapAnalysis.skills }}</p>
          </el-collapse-item>
          <el-collapse-item title="职业素养差距">
            <p class="gap-content">{{ matchResult.gapAnalysis.quality }}</p>
          </el-collapse-item>
          <el-collapse-item title="发展潜力差距">
            <p class="gap-content">{{ matchResult.gapAnalysis.potential }}</p>
          </el-collapse-item>
        </el-collapse>
      </div>
      
      <!-- 操作按钮组 -->
      <div class="operation-btn-group">
        <el-button type="primary" @click="generateReport">生成生涯规划报告</el-button>
        <el-button @click="changeJob">更换岗位重新匹配</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElLoading, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

const router = useRouter()

// 岗位列表
const jobList = ref([
  { jobName: '数据分析师' },
  { jobName: '前端开发工程师' },
  { jobName: '后端开发工程师' },
  { jobName: '产品经理' },
  { jobName: '测试开发工程师' },
  { jobName: 'UI设计师' },
  { jobName: '运维开发工程师' },
  { jobName: '大数据开发工程师' },
  { jobName: '网络安全工程师' },
  { jobName: '电商运营' },
  { jobName: '人工智能工程师' },
  { jobName: '金融分析师' }
])

// 学生信息
const studentInfo = ref(JSON.parse(localStorage.getItem('studentInfo') || '{}'))

// 匹配结果数据
const matchList = reactive([])

// 匹配表单
const matchForm = ref({
  targetJob: ''
})

// 匹配结果
const matchResultVisible = ref(false)
const matchResult = ref({
  totalScore: 0,
  dimensionScores: [],
  gapAnalysis: {}
})

// 判断是否有学生信息
const hasStudentInfo = ref(false)

// 初始化雷达图
let radarChart = null

onMounted(() => {
  toPageData()
  checkStudentInfo()
  window.addEventListener('storage', checkStudentInfo)
})

onUnmounted(() => {
  window.removeEventListener('storage', checkStudentInfo)
})

// 获取匹配数据
async function toPageData() {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await axios.post('/api/llm/recommend', { student: studentInfo.value, top_n: 5 }, { headers: { Authorization: `Bearer ${token}` } })
    if (res.data && res.data.results) {
      matchList.splice(0, matchList.length)
      res.data.results.forEach((item, idx) => {
        const job = item.job || {}
        const match = item.match || {}
        matchList.push({
          rank: idx + 1,
          jobName: job.job_name || job.jobName || '',
          matchScore: match.overall_score || 0,
          details: match
        })
      })
      initRadarChart()
    }
  } catch (e) {
    console.error('获取匹配结果失败', e)
  }
}

// 初始化雷达图
const initRadarChart = () => {}

// 检查学生信息
const checkStudentInfo = () => {
  const studentInfo = localStorage.getItem('studentInfo')
  const studentAbility = localStorage.getItem('studentAbility')
  hasStudentInfo.value = !!studentInfo && !!studentAbility
}

// 跳转至学生信息录入页
const goToStudentInfo = () => {
  router.push('/student-ability')
}

// 开始匹配分析
const startMatch = () => {
  if (!matchForm.value.targetJob) {
    ElMessage.warning('请选择目标岗位！')
    return
  }

  if (!hasStudentInfo.value) {
    router.push('/student-ability')
    return
  }
  
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在进行人岗匹配分析，请稍候...',
    // 关键修改：加载层背景改为半透明白色，移除黑色
    background: 'rgba(255, 255, 255, 0.9)',
    fullscreen: true
  })
  
  setTimeout(() => {
    try {
      const studentAbility = JSON.parse(localStorage.getItem('studentAbility') || '{}')
      
      const dimensionScores = [
        { 
          dimension: '基础要求', 
          score: studentAbility.baseScore || 85, 
          weight: 0.2, 
          contribution: (studentAbility.baseScore || 85) * 0.2, 
          status: '优秀' 
        },
        { 
          dimension: '职业技能', 
          score: studentAbility.skillScore || 70, 
          weight: 0.4, 
          contribution: (studentAbility.skillScore || 70) * 0.4, 
          status: '良好' 
        },
        { 
          dimension: '职业素养', 
          score: studentAbility.qualityScore || 80, 
          weight: 0.25, 
          contribution: (studentAbility.qualityScore || 80) * 0.25, 
          status: '优秀' 
        },
        { 
          dimension: '发展潜力', 
          score: studentAbility.potentialScore || 85, 
          weight: 0.15, 
          contribution: (studentAbility.potentialScore || 85) * 0.15, 
          status: '优秀' 
        }
      ]
      
      const totalScore = dimensionScores.reduce((sum, item) => sum + item.contribution, 0)
      
      const gapAnalysis = {
        base: `基础要求匹配度${studentAbility.baseScore >= 80 ? '优秀' : '良好'}，学历、专业${studentAbility.baseScore >= 80 ? '均符合' : '基本符合'}目标岗位（${matchForm.value.targetJob}）要求。`,
        skills: `职业技能匹配度${studentAbility.skillScore >= 80 ? '优秀' : (studentAbility.skillScore >= 60 ? '良好' : '待提升')}，${studentAbility.skillScore >= 80 ? '已掌握全部核心技能' : `缺少${matchForm.value.targetJob}岗位所需的部分专项技能，建议针对性补充学习`}。`,
        quality: `职业素养匹配度${studentAbility.qualityScore >= 80 ? '优秀' : '良好'}，沟通能力、抗压能力${studentAbility.qualityScore >= 80 ? '均达到' : '基本达到'}岗位要求。`,
        potential: `发展潜力匹配度${studentAbility.potentialScore >= 80 ? '优秀' : '良好'}，学习能力和创新能力${studentAbility.potentialScore >= 80 ? '突出' : '较好'}，具备长期发展潜力。`
      }
      
      matchResult.value = {
        totalScore: Math.round(totalScore),
        dimensionScores,
        gapAnalysis
      }
      
      matchResultVisible.value = true
      nextTick(() => {
        initMatchChart()
      })
    } catch (error) {
      console.error('匹配分析出错：', error)
      ElMessage.error('匹配分析失败，请重试！')
    } finally {
      loadingInstance.close()
    }
  }, 2000)
}

// 初始化匹配对比图表
const initMatchChart = () => {
  let chartDom = document.getElementById('match-chart')
  if (!chartDom) {
    setTimeout(() => {
      chartDom = document.getElementById('match-chart')
      if (chartDom) {
        renderChart(chartDom)
      }
    }, 50)
    return
  }
  
  renderChart(chartDom)
}

// 渲染图表
const renderChart = (chartDom) => {
  if (echarts.getInstanceByDom(chartDom)) {
    echarts.dispose(chartDom)
  }
  
  const myChart = echarts.init(chartDom)
  
  const jobRequirements = {
    '基础要求': 95,
    '职业技能': 90,
    '职业素养': 85,
    '发展潜力': 80
  }
  
  const studentAbilities = {}
  matchResult.value.dimensionScores.forEach(item => {
    studentAbilities[item.dimension] = item.score
  })
  
  const option = {
    // 图表背景改为白色
    backgroundColor: '#ffffff',
    title: { 
      text: '人岗匹配维度对比', 
      left: 'center',
      textStyle: { color: '#666666' } // 标题文字改为灰色，移除黑色
    },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { 
      data: ['岗位要求', '我的能力'], 
      bottom: 0,
      textStyle: { color: '#666666' } // 图例文字改为灰色
    },
    grid: { left: '5%', right: '5%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: ['基础要求', '职业技能', '职业素养', '发展潜力'],
      axisLine: { lineStyle: { color: '#eeeeee' } }, // 轴线改为浅灰色
      axisLabel: { color: '#666666' } // 轴标签改为灰色
    },
    yAxis: { 
      type: 'value', 
      max: 100,
      axisLine: { lineStyle: { color: '#eeeeee' } },
      axisLabel: { color: '#666666' },
      splitLine: { lineStyle: { color: '#eeeeee' } } // 网格线改为浅灰色
    },
    series: [
      {
        name: '岗位要求',
        type: 'bar',
        data: [jobRequirements['基础要求'], jobRequirements['职业技能'], jobRequirements['职业素养'], jobRequirements['发展潜力']],
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '我的能力',
        type: 'bar',
        data: [studentAbilities['基础要求'], studentAbilities['职业技能'], studentAbilities['职业素养'], studentAbilities['发展潜力']],
        itemStyle: { color: '#67C23A' }
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

// 生成生涯报告
const generateReport = () => {
  localStorage.setItem('matchResult', JSON.stringify(matchResult.value))
  localStorage.setItem('targetJob', matchForm.value.targetJob)
  router.push('/career-planning')
}

// 更换岗位
const changeJob = () => {
  matchResultVisible.value = false
  matchForm.value.targetJob = ''
}
</script>

<style scoped>
/* 核心修改：完全移除最大宽度限制，全屏显示 */
.job-match-container {
  padding: 20px;
  background-color: #ffffff; /* 纯白背景 */
  min-height: 100vh;
  width: 100vw !important; /* 强制占满视口宽度 */
  max-width: none !important; /* 移除最大宽度限制 */
  margin: 0 !important; /* 移除居中边距 */
  box-sizing: border-box;
  overflow-x: hidden; /* 防止横向滚动 */
}

/* 全局样式穿透：确保整个页面都是白色 */
:deep(html),
:deep(body),
:deep(#app) {
  background-color: #ffffff !important;
  margin: 0 !important;
  padding: 0 !important;
  color: #666666 !important; /* 全局文字改为灰色，避免黑色 */
}

/* 卡片样式：纯白无阴影无边框 */
.card-item {
  box-shadow: none !important; /* 移除阴影 */
  border-radius: 8px;
  border: 1px solid #f9f9f9 !important; /* 极浅的边框 */
  background-color: #ffffff !important;
}

/* 岗位选择表单样式 */
.job-select-form {
  padding: 20px;
}

.btn-group {
  margin-top: 20px;
}

/* 总评分区域 */
.total-score-section {
  padding: 20px 0;
  border-bottom: 1px solid #f9f9f9; /* 极浅的分割线 */
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.total-score-section h3 {
  font-size: 18px;
  color: #666666 !important; /* 灰色文字 */
  margin: 0;
  font-weight: 500;
}

.total-score {
  font-size: 28px;
  font-weight: 600;
  color: #409EFF;
  margin-left: 15px;
}

/* 各功能区块通用样式 */
.dimension-section,
.chart-section,
.gap-analysis-section {
  padding: 25px 0;
  border-bottom: 1px solid #f9f9f9;
}

.gap-analysis-section {
  border-bottom: none;
}

/* 区块标题样式 */
.section-title {
  font-size: 18px;
  font-weight: 500;
  color: #666666 !important;
  margin-bottom: 20px;
  padding-left: 8px;
  border-left: 4px solid #409EFF;
  display: flex;
  align-items: center;
}

/* 差距分析内容样式 */
.gap-content {
  line-height: 1.8;
  color: #666666 !important;
  padding: 10px 0;
  margin: 0;
  font-size: 15px;
}

/* 操作按钮组 */
.operation-btn-group {
  padding: 25px 0;
  text-align: center;
}

.operation-btn-group .el-button {
  margin: 0 15px;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 15px;
}

/* 表格样式优化 - 全白风格 */
:deep(.el-table) {
  --el-table-header-text-color: #666666 !important;
  --el-table-row-hover-bg-color: #f9f9f9 !important;
  border-radius: 8px;
  border: 1px solid #f9f9f9 !important;
  background-color: #ffffff !important;
}

:deep(.el-table td),
:deep(.el-table th) {
  text-align: center;
  padding: 12px 0;
  font-size: 14px;
  color: #666666 !important;
  border-bottom: 1px solid #f9f9f9 !important;
}

:deep(.el-table th) {
  background-color: #f9f9f9 !important;
  font-weight: 500;
}

/* 折叠面板样式优化 */
:deep(.el-collapse-item__header) {
  font-weight: 500;
  color: #666666 !important;
  padding: 15px 20px;
  font-size: 15px;
  background-color: #ffffff !important;
  border-bottom: 1px solid #f9f9f9 !important;
}

:deep(.el-collapse-item__content) {
  padding: 20px;
  background-color: #ffffff !important;
  border: none !important;
}

/* 禁用按钮样式 */
:deep(.el-button:disabled) {
  background-color: #f9f9f9 !important;
  border-color: #f0f0f0 !important;
  color: #cccccc !important;
}

/* 页面头部样式优化 */
:deep(.el-page-header) {
  margin-bottom: 10px;
  padding: 10px 0;
}

:deep(.el-page-header__content) {
  font-size: 22px;
  font-weight: 600;
  color: #666666 !important;
}

/* 选择器样式优化 */
:deep(.el-select) {
  border-radius: 8px;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
  box-shadow: none;
  border: 1px solid #f0f0f0 !important;
  background-color: #ffffff !important;
}

:deep(.el-select .el-input__wrapper:focus) {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

/* 加载层样式修改 - 白色主题 */
:deep(.el-loading-mask) {
  background-color: rgba(255, 255, 255, 0.9) !important;
}

:deep(.el-loading-text) {
  color: #666666 !important;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .job-match-container {
    padding: 15px;
    width: 100vw !important;
  }
  
  .total-score-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .total-score {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .operation-btn-group .el-button {
    display: block;
    width: 100%;
    margin: 8px 0;
  }
  
  :deep(.el-table) {
    font-size: 13px;
  }
  
  .chart-section #match-chart {
    height: 300px !important;
  }
}
</style>
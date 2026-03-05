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
          <!-- 新增：按钮禁用逻辑 + 提示文字 -->
          <el-button 
            type="primary" 
            @click="startMatch"
            :disabled="!hasStudentInfo"
          >
            {{ hasStudentInfo ? '开始匹配分析' : '请先完成个人信息录入' }}
          </el-button>
          <!-- 辅助提示：无信息时显示引导 -->
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
      
      <!-- 各维度匹配详情 - 均匀列宽 -->
      <div class="dimension-section">
        <h4 class="section-title">各维度匹配详情</h4>
        <!-- 关键修改：添加table-layout:fixed + 每列flex=1实现均匀分配 -->
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
          <el-collapse-item title="基础要求差距" style="border-bottom: 1px solid #f0f0f0;">
            <p class="gap-content">{{ matchResult.gapAnalysis.base }}</p>
          </el-collapse-item>
          <el-collapse-item title="职业技能差距" style="border-bottom: 1px solid #f0f0f0;">
            <p class="gap-content">{{ matchResult.gapAnalysis.skills }}</p>
          </el-collapse-item>
          <el-collapse-item title="职业素养差距" style="border-bottom: 1px solid #f0f0f0;">
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
// 核心修复：合并重复的导入，只保留一次 Vue API 导入
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElLoading, ElMessage, ElMessageBox } from 'element-plus' // 合并 element-plus 导入
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

const router = useRouter()

// 岗位列表（复用岗位画像的12个岗位）
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

// 学生信息（新增：定义缺失的 studentInfo 变量）
const studentInfo = ref(JSON.parse(localStorage.getItem('studentInfo') || '{}'))

// 匹配结果数据（默认空，页面加载时调用后端计算）
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

// 核心：判断是否有学生信息（控制按钮禁用）
const hasStudentInfo = ref(false)

// 初始化雷达图
let radarChart = null

// 修复：合并重复的 onMounted，统一初始化逻辑
onMounted(() => {
  // 加载匹配数据
  toPageData()
  // 检查学生信息
  checkStudentInfo()
  // 监听路由返回时重新检查（比如从录入页返回）
  window.addEventListener('storage', checkStudentInfo)
})

// 组件卸载时清理事件监听（防止内存泄漏）
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
      initRadarChart() // 更新雷达图
    }
  } catch (e) {
    console.error('获取匹配结果失败', e)
    // 可以保留默认静态数据作为备用
  }
}

// 初始化雷达图（空实现，避免报错）
const initRadarChart = () => {
  // 如需实现雷达图，可补充逻辑
}

// 检查学生信息的通用函数
const checkStudentInfo = () => {
  const studentInfo = localStorage.getItem('studentInfo')
  const studentAbility = localStorage.getItem('studentAbility')
  hasStudentInfo.value = !!studentInfo && !!studentAbility
}

// 跳转至学生信息录入页
const goToStudentInfo = () => {
  router.push('/student-ability')
}

// 开始匹配分析（新增学生信息校验）
const startMatch = () => {
  // 1. 校验：未选择岗位
  if (!matchForm.value.targetJob) {
    ElMessage.warning('请选择目标岗位！')
    return
  }

  // 2. 核心校验：无学生信息则拦截
  if (!hasStudentInfo.value) {
    router.push('/student-ability')
    return
  }
  
  // 3. 显示加载提示
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在进行人岗匹配分析，请稍候...',
    background: 'rgba(0, 0, 0, 0.7)',
    fullscreen: true
  })
  
  // 模拟匹配计算（真实项目中替换为后端接口调用）
  setTimeout(() => {
    try {
      // 模拟从本地读取学生信息（真实场景：从后端接口获取）
      const studentAbility = JSON.parse(localStorage.getItem('studentAbility') || '{}')
      
      // 根据学生真实能力动态生成匹配分数（示例逻辑）
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
      
      // 计算总分
      const totalScore = dimensionScores.reduce((sum, item) => sum + item.contribution, 0)
      
      // 动态差距分析（结合目标岗位和学生信息）
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
      
      // 关键修改：先显示匹配结果，再通过nextTick确保DOM渲染完成后初始化图表
      matchResultVisible.value = true
      nextTick(() => {
        initMatchChart()
      })
    } catch (error) {
      // 异常捕获：避免代码报错导致loading无法关闭
      console.error('匹配分析出错：', error)
      ElMessage.error('匹配分析失败，请重试！')
    } finally {
      // 无论成功/失败，关闭加载提示
      loadingInstance.close()
    }
  }, 2000)
}

// 初始化匹配对比图表（增加鲁棒性）
const initMatchChart = () => {
  // 关键优化：多次尝试获取DOM元素，确保能找到
  let chartDom = document.getElementById('match-chart')
  if (!chartDom) {
    // 兜底：如果第一次没找到，延迟50ms再试一次
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

// 抽离图表渲染逻辑，便于复用
const renderChart = (chartDom) => {
  // 先销毁已存在的图表实例，避免重复渲染
  if (echarts.getInstanceByDom(chartDom)) {
    echarts.dispose(chartDom)
  }
  
  const myChart = echarts.init(chartDom)
  
  // 岗位要求的能力值（模拟）
  const jobRequirements = {
    '基础要求': 95,
    '职业技能': 90,
    '职业素养': 85,
    '发展潜力': 80
  }
  
  // 学生能力值（从匹配结果中读取）
  const studentAbilities = {}
  matchResult.value.dimensionScores.forEach(item => {
    studentAbilities[item.dimension] = item.score
  })
  
  const option = {
    title: { text: '人岗匹配维度对比', left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['岗位要求', '我的能力'], bottom: 0 },
    grid: { left: '5%', right: '5%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: ['基础要求', '职业技能', '职业素养', '发展潜力'] },
    yAxis: { type: 'value', max: 100 },
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
  
  // 设置并渲染图表
  myChart.setOption(option)
  
  // 防抖resize：避免频繁触发导致性能问题
  const resizeHandler = () => {
    clearTimeout(window.resizeTimer)
    window.resizeTimer = setTimeout(() => {
      myChart.resize()
    }, 200)
  }
  window.addEventListener('resize', resizeHandler)
  
  // 组件卸载时清理：防止内存泄漏
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
    myChart.dispose()
  })
}

// 生成生涯报告
const generateReport = () => {
  // 保存匹配结果到本地（供报告页使用）
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
.job-match-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
  max-width: 1200px;
  margin: 0 auto; /* 居中显示 */
}

/* 卡片通用样式 */
.card-item {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  overflow: hidden;
}

/* 岗位选择表单样式 */
.job-select-form {
  padding: 10px 0;
}

.btn-group {
  margin-top: 10px;
}

/* 总评分区域 */
.total-score-section {
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.total-score {
  font-size: 24px;
  font-weight: bold;
  color: #1989fa;
  margin-left: 10px;
}

/* 各功能区块通用样式 */
.dimension-section,
.chart-section,
.gap-analysis-section {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

/* 最后一个区块去掉下边框 */
.gap-analysis-section {
  border-bottom: none;
}

/* 区块标题样式 */
.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
  padding-left: 5px;
  border-left: 4px solid #409EFF;
}

/* 差距分析内容样式 */
.gap-content {
  line-height: 1.8;
  color: #666;
  padding: 10px 0;
  margin: 0;
}

/* 操作按钮组 */
.operation-btn-group {
  padding: 20px 0;
  text-align: center;
}

.operation-btn-group .el-button {
  margin: 0 10px;
}

/* 表格样式优化 - 确保列宽均匀 */
:deep(.el-table) {
  --el-table-header-text-color: #303133;
  --el-table-row-hover-bg-color: #f8f9fa;
  border-radius: 4px;
}

/* 表格单元格居中 */
:deep(.el-table td),
:deep(.el-table th) {
  text-align: center;
}

/* 折叠面板样式优化 */
:deep(.el-collapse-item__header) {
  font-weight: 500;
  color: #303133;
  padding: 12px 15px;
}

:deep(.el-collapse-item__content) {
  padding: 15px;
}

/* 禁用按钮样式 */
:deep(.el-button:disabled) {
  background-color: #e5e7eb;
  border-color: #d1d5db;
  color: #9ca3af;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .job-match-container {
    padding: 10px;
  }
  
  .total-score-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .total-score {
    margin-left: 0;
    margin-top: 5px;
  }
  
  .operation-btn-group .el-button {
    display: block;
    width: 100%;
    margin: 5px 0;
  }
  
  /* 移动端表格列宽自适应 */
  :deep(.el-table) {
    font-size: 12px;
  }
  
  /* 移动端图表高度适配 */
  .chart-section #match-chart {
    height: 300px !important;
  }
}
</style>
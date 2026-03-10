<template>
  <div class="job-match-container">
    <!-- 顶部导航栏（改为白色、居中、中文返回） -->
    <div class="top-nav">
      <div class="nav-wrapper">
        <el-button type="text" @click="$router.push('/')" class="back-btn">
          ← 返回
        </el-button>
        <span class="nav-title">人岗匹配分析</span>
        <div class="nav-right-placeholder"></div>
      </div>
    </div>

    <!-- 引导说明（与截图一致） -->
    <div class="guide-card">
      <div class="guide-content">
        <h3>精准匹配，规划职业方向</h3>
        <p>基于你的个人能力和职业偏好，智能分析你与目标岗位的匹配度，为职业规划提供数据支撑</p>
      </div>
    </div>

    <!-- 岗位选择卡片 -->
    <el-card class="card-item job-select-card">
      <div class="card-header">
        <h3>岗位匹配设置</h3>
      </div>

      <el-form :model="matchForm" label-width="100px" class="job-select-form">
        <el-form-item label="选择目标岗位" required>
          <el-select 
            v-model="matchForm.targetJob" 
            filterable 
            placeholder="请选择目标岗位" 
            style="width: 100%;"
            @change="saveFormData"
          >
            <el-option 
              v-for="job in jobList" 
              :key="job.jobName" 
              :label="job.jobName" 
              :value="job.jobName"
            ></el-option>
          </el-select>

          <!-- 热门岗位推荐（统一主色） -->
          <div class="hot-jobs">
            <span class="label">热门推荐：</span>
            <el-tag 
              v-for="job in hotJobList" 
              :key="job" 
              size="small" 
              effect="light"
              color="#409EFF"
              text-color="#fff"
              @click="selectHotJob(job)"
            >
              {{ job }}
            </el-tag>
          </div>

          <!-- 新增：岗位暂存功能 -->
          <div class="temp-job-actions" style="margin-top: 12px; display: flex; gap: 8px; align-items: center;">
            <el-button 
              type="text" 
              size="small" 
              @click="saveTempJob"
              :disabled="!matchForm.targetJob"
              style="color: #409EFF; padding: 0;"
            >
              💾 暂存当前岗位
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="restoreTempJob"
              :disabled="!tempTargetJob"
              style="color: #409EFF; padding: 0;"
            >
              ↩️ 恢复暂存岗位
            </el-button>
            <span v-if="tempTargetJob" class="temp-job-tip" style="font-size: 12px; color: #606266;">
              暂存岗位：{{ tempTargetJob }}
            </span>
          </div>
        </el-form-item>

        <!-- 匹配参数设置 -->
        <el-form-item label="匹配精度">
          <el-slider 
            v-model="matchForm.accuracy" 
            :min="1" 
            :max="3" 
            :marks="{ 1: '快速', 2: '标准', 3: '精准' }"
            @change="saveFormData"
            active-color="#409EFF"
          ></el-slider>
          <div class="accuracy-tip">
            {{ matchForm.accuracy === 1 ? '匹配耗时约1秒' : matchForm.accuracy === 2 ? '匹配耗时约2秒' : '匹配耗时约3秒' }}
          </div>
        </el-form-item>

        <el-form-item class="btn-group">
          <el-button 
            type="primary" 
            @click="startMatch"
            :disabled="!hasStudentInfo || !matchForm.targetJob"
            class="match-btn"
            color="#409EFF"
          >
            {{ hasStudentInfo ? (matchLoading ? '匹配中...' : '开始匹配分析') : '请先完成个人信息录入' }}
          </el-button>

          <el-button 
            type="default" 
            @click="resetForm"
            class="reset-btn"
            border-color="#409EFF"
            text-color="#409EFF"
          >
            重置
          </el-button>

          <span v-if="!hasStudentInfo" class="info-tip">
            👉 <a @click="goToStudentInfo" class="link">点击前往信息录入页</a>
          </span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 匹配结果 -->
    <el-card 
      v-if="matchResultVisible" 
      title="人岗匹配分析结果" 
      class="card-item result-card"
      shadow="hover"
    >
      <!-- 结果头部 -->
      <div class="result-header">
        <div class="job-title">
          <span>目标岗位：{{ matchForm.targetJob }}</span>
        </div>
        <el-tag class="save-tag" color="#409EFF" text-color="#fff">
          数据已自动保存
        </el-tag>
      </div>

      <!-- 总评分 -->
      <div class="total-score-section">
        <div class="score-card">
          <h3>匹配度总评分</h3>
          <div class="score-value">{{ matchResult.totalScore }}分</div>
          <div class="score-level">
            <el-tag :color="getScoreLevelColor()">{{ getScoreLevelText() }}</el-tag>
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
              <el-tag :color="scope.row.score >= 80 ? '#409EFF' : (scope.row.score >= 60 ? '#66b1ff' : '#ff7d7d')">
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

    <!-- 空状态提示 -->
    <div v-if="!matchResultVisible && hasStudentInfo && matchForm.targetJob" class="empty-state">
      <el-empty description="尚未进行匹配分析，请点击按钮开始"></el-empty>
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

// ===== 数据定义（替换为更丰富的岗位数据）=====
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

const matchResultVisible = ref(false)
const matchResult = ref({
  totalScore: 0,
  dimensionScores: [],
  gapAnalysis: {}
})

const hasStudentInfo = ref(false)
const studentInfo = ref(JSON.parse(localStorage.getItem('studentInfo') || '{}'))
const matchList = reactive([])

// ===== 工具函数 =====
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
      matchResultVisible.value = true
    }
  } catch (e) {
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

// 新增：保存暂存岗位
const saveTempJob = () => {
  tempTargetJob.value = matchForm.value.targetJob
  localStorage.setItem('tempTargetJob', tempTargetJob.value)
  ElMessage.success(`已暂存岗位：${tempTargetJob.value}`)
  console.log(`已暂存岗位：${tempTargetJob.value}`)
}

// 新增：恢复暂存岗位
const restoreTempJob = () => {
  matchForm.value.targetJob = tempTargetJob.value
  saveFormData()
  ElMessage.success(`已恢复暂存岗位：${tempTargetJob.value}`)
  console.log(`已恢复暂存岗位：${tempTargetJob.value}`)
}

const checkStudentInfo = () => {
  const studentInfo = localStorage.getItem('studentInfo')
  const studentAbility = localStorage.getItem('studentAbility')
  hasStudentInfo.value = !!studentInfo && !!studentAbility
}

// 移除弹窗，直接赋值
const selectHotJob = (jobName) => {
  matchForm.value.targetJob = jobName
  saveFormData()
  console.log(`已选择热门岗位：${jobName}`)
}

// 移除确认弹窗，直接重置
const resetForm = () => {
  matchForm.value = {
    targetJob: '',
    accuracy: 2
  }
  matchResultVisible.value = false
  // 重置时保留暂存岗位，如需清空可取消下面注释
  // tempTargetJob.value = ''
  // localStorage.removeItem('tempTargetJob')
  localStorage.removeItem('matchForm')
  localStorage.removeItem('matchResult')
  localStorage.removeItem('targetJob')
  ElMessage.info('匹配设置已重置（暂存岗位已保留）')
  console.log('匹配设置已重置')
}

const goToStudentInfo = () => {
  saveFormData()
  router.push('/student-ability')
}

// 统一评分等级颜色（主色渐变）
const getScoreLevelColor = () => {
  if (matchResult.value.totalScore >= 85) return '#409EFF'
  if (matchResult.value.totalScore >= 70) return '#66b1ff'
  return '#ff7d7d'
}

const getScoreLevelText = () => {
  if (matchResult.value.totalScore >= 85) return '高度匹配'
  if (matchResult.value.totalScore >= 70) return '较匹配'
  if (matchResult.value.totalScore >= 60) return '基本匹配'
  return '匹配度较低'
}

// 优化匹配建议，结合不同岗位特点
const getMatchSuggestion = () => {
  // 按岗位类型分类给出更精准的建议
  const aiRelatedJobs = ['人工智能算法工程师', '机器学习工程师']
  const devRelatedJobs = ['Java开发工程师', 'Python开发工程师', 'Web前端开发工程师', '全栈开发工程师']
  const dataRelatedJobs = ['大数据开发工程师', '数据挖掘工程师']
  
  let jobType = ''
  if (aiRelatedJobs.includes(matchForm.value.targetJob)) {
    jobType = '人工智能类'
  } else if (devRelatedJobs.includes(matchForm.value.targetJob)) {
    jobType = '开发类'
  } else if (dataRelatedJobs.includes(matchForm.value.targetJob)) {
    jobType = '数据类'
  } else {
    jobType = ''
  }

  if (matchResult.value.totalScore >= 85) {
    return `你与【${matchForm.value.targetJob}】岗位高度匹配，具备该${jobType}岗位所需的核心技术能力和职业素养，建议优先将该岗位作为职业发展方向。`
  } else if (matchResult.value.totalScore >= 70) {
    return `你与【${matchForm.value.targetJob}】岗位较匹配，核心能力基本达标，只需针对性提升${jobType ? jobType : '该'}岗位的专项技能即可胜任。`
  } else if (matchResult.value.totalScore >= 60) {
    return `你与【${matchForm.value.targetJob}】岗位基本匹配，需要系统学习${jobType ? jobType : '该'}岗位的核心技能体系，建议制定3-6个月的能力提升计划。`
  } else {
    return `你与【${matchForm.value.targetJob}】岗位匹配度较低，建议重新评估职业方向，或选择${jobType ? jobType : '相关'}岗位的入门级职位逐步提升。`
  }
}

// 移除导出弹窗，直接执行
const exportResult = () => {
  try {
    const exportData = {
      targetJob: matchForm.value.targetJob,
      tempTargetJob: tempTargetJob.value, // 新增：导出暂存岗位
      matchResult: matchResult.value,
      exportTime: new Date().toLocaleString()
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${matchForm.value.targetJob}_匹配分析结果_${new Date().getTime()}.json`
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
  saveFormData()
  localStorage.setItem('matchResult', JSON.stringify(matchResult.value))
  localStorage.setItem('targetJob', matchForm.value.targetJob)
  router.push('/career-planning')
}

const changeJob = () => {
  matchResultVisible.value = false
  matchForm.value.targetJob = ''
  saveFormData()
}

// ===== 匹配分析核心逻辑（优化不同岗位的默认得分）=====
const startMatch = () => {
  if (!matchForm.value.targetJob) {
    ElMessage.warning('请选择目标岗位！')
    return
  }

  if (!hasStudentInfo.value) {
    router.push('/student-ability')
    return
  }

  matchLoading.value = true
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在进行人岗匹配分析，请稍候...',
    background: 'rgba(255, 255, 255, 0.9)',
    fullscreen: true
  })

  const delayTime = matchForm.value.accuracy * 1000

  setTimeout(() => {
    try {
      const studentAbility = JSON.parse(localStorage.getItem('studentAbility') || '{}')

      // 根据不同岗位类型设置差异化的默认得分
      let baseScore = studentAbility.baseScore || 85
      let skillScore = studentAbility.skillScore || 70
      let qualityScore = studentAbility.qualityScore || 80
      let potentialScore = studentAbility.potentialScore || 85

      // 人工智能类岗位对技能要求更高
      if (['人工智能算法工程师', '机器学习工程师'].includes(matchForm.value.targetJob)) {
        skillScore = studentAbility.skillScore || 75
        potentialScore = studentAbility.potentialScore || 90
      }
      // 安全类岗位对基础要求更严格
      else if (['网络安全工程师'].includes(matchForm.value.targetJob)) {
        baseScore = studentAbility.baseScore || 90
        qualityScore = studentAbility.qualityScore || 85
      }
      // 全栈开发要求综合能力更强
      else if (['全栈开发工程师'].includes(matchForm.value.targetJob)) {
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
        base: `基础要求匹配度${baseScore >= 80 ? '优秀' : '良好'}，学历、专业背景${baseScore >= 80 ? '完全符合' : '基本符合'}【${matchForm.value.targetJob}】岗位的招聘要求。`,
        skills: `职业技能匹配度${skillScore >= 80 ? '优秀' : (skillScore >= 60 ? '良好' : '待提升')}，${skillScore >= 80 ? '已熟练掌握该岗位所需的核心技术栈' : `在${matchForm.value.targetJob}核心技能方面存在短板，建议重点学习相关技术框架和实战经验`}。`,
        quality: `职业素养匹配度${qualityScore >= 80 ? '优秀' : '良好'}，沟通协作、问题解决能力${qualityScore >= 80 ? '完全满足' : '基本满足'}岗位要求，可重点提升${qualityScore < 80 ? '抗压能力和团队协作能力' : '创新思维'}。`,
        potential: `发展潜力匹配度${potentialScore >= 80 ? '优秀' : '良好'}，学习能力和技术迭代适应能力${potentialScore >= 80 ? '突出' : '较好'}，${potentialScore >= 85 ? '具备成为技术专家的潜力' : '适合在该领域长期发展'}。`
      }

      matchResult.value = {
        totalScore,
        dimensionScores,
        gapAnalysis
      }

      localStorage.setItem('matchResult', JSON.stringify(matchResult.value))
      localStorage.setItem('targetJob', matchForm.value.targetJob)
      localStorage.setItem('lastMatchTime', new Date().toISOString())

      matchResultVisible.value = true

      nextTick(() => {
        initMatchChart()
      })

      ElMessage.success('人岗匹配分析完成！')
      console.log('人岗匹配分析完成！')
    } catch (error) {
      ElMessage.error('匹配分析出错，请重试')
      console.error('匹配分析出错：', error)
    } finally {
      matchLoading.value = false
      loadingInstance.close()
    }
  }, delayTime)
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

  // 不同岗位设置差异化的岗位要求分值
  let jobRequirements = {
    '基础要求': 95,
    '职业技能': 90,
    '职业素养': 85,
    '发展潜力': 80
  }

  // AI类岗位技能要求更高
  if (['人工智能算法工程师', '机器学习工程师'].includes(matchForm.value.targetJob)) {
    jobRequirements['职业技能'] = 95
    jobRequirements['发展潜力'] = 90
  }
  // 安全类岗位基础要求更高
  else if (['网络安全工程师'].includes(matchForm.value.targetJob)) {
    jobRequirements['基础要求'] = 98
    jobRequirements['职业素养'] = 90
  }
  // 全栈开发综合要求更高
  else if (['全栈开发工程师'].includes(matchForm.value.targetJob)) {
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

/* 顶部导航栏（改为白色、居中、中文返回） */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 20px;
  background-color: #fff;
  color: #333;
  font-size: 14px;
  border-bottom: 1px solid #e5e7eb;
}

.nav-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1200px;
}

.back-btn {
  color: #333 !important;
  padding: 0 !important;
  font-size: 14px !important;
}

.nav-title {
  font-weight: 500;
}

.nav-right-placeholder {
  width: 60px; /* 与返回按钮宽度平衡，使标题居中 */
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

.job-select-card {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.result-card {
  padding: 0;
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

/* 表单样式 */
.job-select-form {
  padding: 0;
}

/* 热门岗位 */
.hot-jobs {
  margin-top: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.hot-jobs .label {
  font-size: 12px;
  color: #909399;
  margin-right: 4px;
}

/* 精度提示 */
.accuracy-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* 按钮组 */
.btn-group {
  margin-top: 24px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.match-btn {
  padding: 12px 32px;
  font-size: 15px;
  border-radius: 8px;
}

.reset-btn {
  padding: 12px 24px;
  font-size: 15px;
  border-radius: 8px;
}

/* 信息提示 */
.info-tip {
  font-size: 12px;
  color: #409EFF;
}

.link {
  color: #409EFF;
  text-decoration: underline;
  cursor: pointer;
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

.save-tag {
  border: none !important;
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

/* 空状态 */
.empty-state {
  padding: 60px 20px;
  text-align: center;
  background-color: #ffffff;
  border-radius: 0;
  border-bottom: 1px solid #e5e7eb;
  margin: 0 auto;
  max-width: 1200px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .top-nav {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
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

  /* 响应式适配暂存按钮 */
  .temp-job-actions {
    flex-direction: column;
    align-items: flex-start !important;
  }
}
</style>
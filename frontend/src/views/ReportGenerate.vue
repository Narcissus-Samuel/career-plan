<template>
  <div class="report-generate">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-wrap">
        <div class="page-title">
          <span class="title-icon">📑</span>
          <h1>规划报告生成中心</h1>
        </div>
        <div class="page-nav">
          <button class="back-btn" @click="$router.push('/')">← 返回首页</button>
          <button class="history-btn" @click="showHistory = !showHistory">历史报告</button>
        </div>
      </div>
    </header>

    <!-- 历史报告弹窗 -->
    <div class="history-modal" v-show="showHistory">
      <div class="modal-mask" @click="showHistory = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>历史生成报告</h3>
          <button class="close-btn" @click="showHistory = false">×</button>
        </div>
        <div class="modal-body">
          <div class="history-empty" v-if="historyReports.length === 0">
            暂无历史报告，快去生成你的第一份报告吧！
          </div>
          <div class="history-list" v-else>
            <div class="history-item" v-for="(item, index) in historyReports" :key="index">
              <div class="history-title">{{ item.title }}</div>
              <div class="history-time">{{ item.createTime }}</div>
              <div class="history-actions">
                <button class="preview-btn" @click="previewHistoryReport(item)">预览</button>
                <button class="export-btn" @click="exportReport(item)">导出</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 报告配置区 -->
    <section class="config-section">
      <div class="config-wrap">
        <div class="config-card">
          <div class="config-title">
            <span class="title-icon">⚙️</span>
            报告生成配置
          </div>
          <div class="config-content">
            <!-- 报告类型选择 -->
            <div class="config-item">
              <label class="config-label">报告类型：</label>
              <select class="config-select" v-model="reportConfig.type" @change="updateReportTemplate">
                <option value="career">完整职业规划报告</option>
                <option value="ability">能力测评分析报告</option>
                <option value="combination">规划+测评综合报告</option>
                <option value="simple">极简版规划报告</option>
              </select>
            </div>

            <!-- 报告标题自定义 -->
            <div class="config-item">
              <label class="config-label">报告标题：</label>
              <input 
                type="text" 
                class="config-input" 
                v-model="reportConfig.title" 
                placeholder="请输入报告标题（默认：XX的职业规划报告）"
              >
            </div>

            <!-- 包含模块选择 -->
            <div class="config-item">
              <label class="config-label">包含模块：</label>
              <div class="module-group">
                <label class="module-item" v-for="module in reportModules" :key="module.key">
                  <input 
                    type="checkbox" 
                    v-model="module.checked"
                    :disabled="!module.supportedTypes.includes(reportConfig.type)"
                  >
                  <span class="module-text">{{ module.name }}</span>
                  <span class="module-tip" v-if="!module.supportedTypes.includes(reportConfig.type)">
                    该类型报告不包含此模块
                  </span>
                </label>
              </div>
            </div>

            <!-- 报告格式选择 -->
            <div class="config-item">
              <label class="config-label">导出格式：</label>
              <div class="format-group">
                <label class="format-item">
                  <input type="radio" v-model="reportConfig.format" value="pdf"> PDF（推荐）
                </label>
                <label class="format-item">
                  <input type="radio" v-model="reportConfig.format" value="word"> Word
                </label>
                <label class="format-item">
                  <input type="radio" v-model="reportConfig.format" value="txt"> 纯文本
                </label>
              </div>
            </div>

            <!-- 生成按钮 -->
            <div class="config-btn-group">
              <button class="generate-btn" @click="generateReport" :disabled="isGenerating">
                <span v-if="!isGenerating">生成报告</span>
                <span v-if="isGenerating">生成中... {{ generateProgress }}%</span>
              </button>
              <button class="reset-btn" @click="resetConfig">重置配置</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 报告预览区 -->
    <section class="preview-section" v-show="reportPreview">
      <div class="preview-wrap">
        <div class="preview-header">
          <h2>{{ reportConfig.title }}</h2>
          <div class="preview-actions">
            <button class="print-btn" @click="printReport">打印报告</button>
            <button class="export-btn" @click="exportCurrentReport">导出报告</button>
          </div>
        </div>

        <div class="preview-content" ref="previewRef">
          <!-- 报告头部 -->
          <div class="report-header">
            <div class="report-title">{{ reportConfig.title }}</div>
            <div class="report-subtitle">生成时间：{{ new Date().toLocaleString() }}</div>
            <div class="report-line"></div>
          </div>

          <!-- 基础信息模块 -->
          <div class="report-module" v-if="getModule('basicInfo').checked">
            <div class="module-title">一、基础信息</div>
            <div class="module-content">
              <table class="info-table">
                <tr>
                  <td class="table-label">姓名</td>
                  <td>{{ userInfo.name || '未填写' }}</td>
                  <td class="table-label">性别</td>
                  <td>{{ userInfo.gender || '未填写' }}</td>
                </tr>
                <tr>
                  <td class="table-label">年级</td>
                  <td>{{ userInfo.grade || '未填写' }}</td>
                  <td class="table-label">专业</td>
                  <td>{{ userInfo.major || '未填写' }}</td>
                </tr>
                <tr>
                  <td class="table-label">目标方向</td>
                  <td>{{ userInfo.target || '未填写' }}</td>
                  <td class="table-label">职业兴趣</td>
                  <td>{{ userInfo.interest?.join('、') || '未填写' }}</td>
                </tr>
              </table>
            </div>
          </div>

          <!-- 职业规划模块 -->
          <div class="report-module" v-if="getModule('careerPlan').checked">
            <div class="module-title">二、职业规划</div>
            <div class="module-content">
              <div class="plan-stage" v-for="stage in careerPlanStages" :key="stage.grade">
                <div class="stage-title">{{ stage.grade }}规划</div>
                <div class="stage-content">{{ stage.content }}</div>
              </div>
              <div class="plan-empty" v-if="careerPlanStages.length === 0">
                暂无职业规划数据，请先完成职业规划测评
              </div>
            </div>
          </div>

          <!-- 能力测评模块 -->
          <div class="report-module" v-if="getModule('abilityScore').checked">
            <div class="module-title">三、能力测评分析</div>
            <div class="module-content">
              <div class="ability-list" v-if="abilityScores.length > 0">
                <div class="ability-item" v-for="item in abilityScores" :key="item.dimension">
                  <div class="ability-dimension">{{ item.dimension }}</div>
                  <div class="ability-score">
                    得分：{{ item.score }}/20（{{ item.level }}）
                    <div class="score-bar">
                      <div class="score-fill" :style="{ width: (item.score/20)*100 + '%' }"></div>
                    </div>
                  </div>
                  <div class="ability-suggestion">{{ item.suggestion }}</div>
                </div>
              </div>
              <div class="ability-empty" v-else>
                暂无能力测评数据，请先完成能力测评
              </div>
            </div>
          </div>

          <!-- 职业适配建议模块 -->
          <div class="report-module" v-if="getModule('careerSuggest').checked">
            <div class="module-title">四、职业适配建议</div>
            <div class="module-content">
              <div class="suggest-content">{{ careerSuggestion || '暂无适配建议，请先完成能力测评' }}</div>
            </div>
          </div>

          <!-- 总结与建议模块 -->
          <div class="report-module" v-if="getModule('summary').checked">
            <div class="module-title">五、总结与建议</div>
            <div class="module-content">
              <div class="summary-content">{{ generateSummary() }}</div>
            </div>
          </div>

          <!-- 报告尾部 -->
          <div class="report-footer">
            <div class="footer-text">本报告由大学生职业规划系统智能生成，仅供参考</div>
            <div class="footer-tip">如有疑问，请联系系统管理员</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="page-footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 专业报告 · 科学规划
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 核心状态
const showHistory = ref(false)
const isGenerating = ref(false)
const generateProgress = ref(0)
const reportPreview = ref(false)
const historyReports = ref([])

// 报告配置
const reportConfig = ref({
  type: 'career',
  title: '',
  format: 'pdf'
})

// 报告模块配置
const reportModules = ref([
  { key: 'basicInfo', name: '基础信息', checked: true, supportedTypes: ['career', 'ability', 'combination', 'simple'] },
  { key: 'careerPlan', name: '职业规划', checked: true, supportedTypes: ['career', 'combination'] },
  { key: 'abilityScore', name: '能力测评分析', checked: true, supportedTypes: ['ability', 'combination'] },
  { key: 'careerSuggest', name: '职业适配建议', checked: true, supportedTypes: ['career', 'combination', 'ability'] },
  { key: 'summary', name: '总结与建议', checked: true, supportedTypes: ['career', 'ability', 'combination'] }
])

// 用户基础信息
const userInfo = ref({
  name: '',
  gender: '',
  grade: '',
  major: '',
  target: '',
  interest: []
})

// 职业规划数据
const careerPlanStages = ref([])

// 能力测评数据
const abilityScores = ref([])

// 职业适配建议
const careerSuggestion = ref('')

// 获取指定模块配置
const getModule = (key) => {
  return reportModules.value.find(module => module.key === key) || { checked: false }
}

// 初始化
onMounted(() => {
  // 读取职业规划数据
  const careerPlan = localStorage.getItem('careerPlan')
  if (careerPlan) {
    userInfo.value = JSON.parse(careerPlan)
    generateCareerPlanStages()
  }

  // 读取能力测评数据
  const abilityAnswers = localStorage.getItem('abilityAssessmentAnswers')
  if (abilityAnswers) {
    calculateAbilityScores(JSON.parse(abilityAnswers))
  }

  // 读取历史报告
  const savedHistory = localStorage.getItem('reportHistory')
  if (savedHistory) {
    historyReports.value = JSON.parse(savedHistory)
  }

  // 设置默认标题
  updateReportTemplate()
})

// 更新报告模板
const updateReportTemplate = () => {
  if (!reportConfig.value.title) {
    const typeTitles = {
      'career': `${userInfo.value.name || '大学生'}的职业规划报告`,
      'ability': `${userInfo.value.name || '大学生'}的能力测评分析报告`,
      'combination': `${userInfo.value.name || '大学生'}的职业规划+能力测评综合报告`,
      'simple': `${userInfo.value.name || '大学生'}的极简版职业规划报告`
    }
    reportConfig.value.title = typeTitles[reportConfig.value.type]
  }

  // 自动勾选模块
  reportModules.value.forEach(module => {
    module.checked = module.supportedTypes.includes(reportConfig.value.type)
  })

  // 极简版特殊处理
  if (reportConfig.value.type === 'simple') {
    reportModules.value.forEach(module => {
      module.checked = ['basicInfo', 'careerPlan', 'summary'].includes(module.key)
    })
  }
}

// 生成职业规划阶段数据
const generateCareerPlanStages = () => {
  if (!userInfo.value.target || !userInfo.value.grade || !userInfo.value.major) {
    careerPlanStages.value = []
    return
  }

  // 规则库
  const bigDataPlanRules = {
    "就业": {
      "计算机": {
        "大一": "1. 学好C语言/Java基础；2. 加入编程社团；3. 了解前端/后端/算法等细分方向",
        "大二": "1. 学习框架（Vue/React/SpringBoot）；2. 做2个以上实战项目；3. 参加蓝桥杯等编程竞赛",
        "大三": "1. 投递大厂暑期实习；2. 刷LeetCode（至少100题）；3. 准备秋招简历/笔试",
        "大四": "1. 冲刺秋招/春招；2. 完善项目作品集；3. 学习职场必备的沟通/协作技能"
      },
      "金融": {
        "大一": "1. 学好高数/宏微观经济学；2. 加入金融社团；3. 了解银行/证券/基金等细分领域",
        "大二": "1. 考取证券从业资格证；2. 参与金融建模比赛；3. 找券商/银行的实习（实习岗）",
        "大三": "1. 冲刺暑期实习（目标头部券商/基金）；2. 备考CFA一级；3. 学习财务分析技能",
        "大四": "1. 参加校招（银行校招/券商秋招）；2. 完善简历（突出实习经历）；3. 学习职场合规知识"
      },
      "默认": {
        "大一": "1. 夯实专业基础；2. 参加相关社团；3. 了解行业基本情况",
        "大二": "1. 考取核心证书；2. 参与实习/项目；3. 明确细分方向",
        "大三": "1. 针对性提升能力；2. 准备实习/求职材料；3. 参加校招宣讲会",
        "大四": "1. 冲刺校招；2. 完善简历/作品集；3. 学习职场适应技能"
      }
    },
    "考研": {
      "计算机": {
        "大一": "1. 学好数学（高数/线代）/英语；2. 了解考研院校排名；3. 确定学硕/专硕方向",
        "大二": "1. 开始一轮复习（数学/英语）；2. 确定目标院校/专业；3. 联系上岸学长学姐",
        "大三": "1. 二轮复习（专业课+政治）；2. 参加考研模拟考试；3. 关注目标院校招生简章",
        "大四": "1. 冲刺复习+参加初试；2. 准备复试（机试/面试）；3. 关注调剂信息"
      },
      "默认": {
        "大一": "1. 学好公共课（数学/英语）；2. 了解考研政策；3. 确定是否跨考",
        "大二": "1. 一轮复习公共课；2. 确定目标院校/专业；3. 收集专业课资料",
        "大三": "1. 二轮复习（专业课+政治）；2. 参加模拟考试；3. 关注招生简章",
        "大四": "1. 参加初试；2. 准备复试；3. 关注调剂信息"
      }
    },
    "默认": {
      "默认": {
        "大一": "1. 夯实专业基础；2. 参加相关社团；3. 了解行业基本情况",
        "大二": "1. 考取核心证书；2. 参与实习/项目；3. 明确细分方向",
        "大三": "1. 针对性提升能力；2. 准备实习/求职材料；3. 参加校招宣讲会",
        "大四": "1. 冲刺校招；2. 完善简历/作品集；3. 学习职场适应技能"
      }
    }
  }

  // 模糊匹配专业
  const getMatchedMajor = (major) => {
    const majorKeywords = {
      '计算机': ['计算机', '软件', '编程', '大数据', '人工智能'],
      '金融': ['金融', '经济', '证券', '银行', '投资'],
      '教育': ['教育', '师范', '语文', '数学', '英语']
    }
    for (const [key, keywords] of Object.entries(majorKeywords)) {
      if (keywords.some(k => major.includes(k))) {
        return key
      }
    }
    return '默认'
  }

  // 匹配规则
  const targetRules = bigDataPlanRules[userInfo.value.target] || bigDataPlanRules['默认']
  const matchedMajor = getMatchedMajor(userInfo.value.major)
  const majorRules = targetRules[matchedMajor] || targetRules['默认']

  // 生成阶段规划
  const grades = ['大一', '大二', '大三', '大四']
  const currentGradeIndex = grades.findIndex(g => g === userInfo.value.grade)
  const stages = []

  for (let i = currentGradeIndex; i < grades.length; i++) {
    stages.push({
      grade: grades[i],
      content: majorRules[grades[i]] || '暂无针对性规划，建议夯实专业基础，明确发展方向'
    })
  }

  careerPlanStages.value = stages
}

// 计算能力测评得分
const calculateAbilityScores = (answers) => {
  const dimensionScores = {
    '学习能力': 0,
    '沟通能力': 0,
    '团队协作': 0,
    '专业技能': 0,
    '创新能力': 0
  }

  answers.forEach(answer => {
    dimensionScores[answer.dimension] += Number(answer.score)
  })

  // 生成能力分析
  const analysis = Object.entries(dimensionScores).map(([dimension, score]) => {
    let level = ''
    let suggestion = ''

    if (score >= 16) {
      level = '优秀'
      suggestion = `你的${dimension}非常突出，可重点发挥该优势，在职业选择中优先考虑需要该能力的方向。`
    } else if (score >= 12) {
      level = '良好'
      suggestion = `你的${dimension}较好，可继续强化，在实践中进一步提升该能力。`
    } else if (score >= 8) {
      level = '一般'
      suggestion = `你的${dimension}处于中等水平，建议通过刻意练习（如参加培训/项目）提升。`
    } else {
      level = '待提升'
      suggestion = `你的${dimension}有待加强，可制定专项提升计划，从基础开始逐步改善。`
    }

    return {
      dimension,
      score,
      level,
      suggestion
    }
  })

  abilityScores.value = analysis

  // 生成职业适配建议
  const sortedDimensions = Object.entries(dimensionScores).sort((a, b) => b[1] - a[1])
  const topDimension = sortedDimensions[0][0]
  const lowDimension = sortedDimensions[sortedDimensions.length - 1][0]

  const baseSuggestions = {
    '学习能力': '优先选择需要持续学习的职业方向（如研发、咨询、教育等），你的快速学习能力能帮助你快速适应行业变化。',
    '沟通能力': '优先选择需要高频沟通的职业方向（如销售、运营、人力资源、管理等），你的沟通优势能让你在工作中事半功倍。',
    '团队协作': '优先选择团队型工作模式的职业（如项目管理、产品、金融投行等），你能很好地融入团队并发挥协作价值。',
    '专业技能': '优先选择专业型职业方向（如技术研发、医生、律师、会计等），你的专业能力是核心竞争力。',
    '创新能力': '优先选择需要创意的职业方向（如设计、策划、创业、科研等），你的创新思维能带来独特价值。'
  }

  careerSuggestion.value = `基于你的测评结果，你的${topDimension}表现最佳，${lowDimension}需要重点提升。${baseSuggestions[topDimension]}同时建议你针对性提升${lowDimension}，弥补能力短板，让职业发展更均衡。`
}

// 生成报告
const generateReport = () => {
  if (!userInfo.value.name) {
    alert('请先完成职业规划/能力测评，完善个人信息后再生成报告！')
    return
  }

  isGenerating.value = true
  generateProgress.value = 0

  // 模拟生成进度
  const progressTimer = setInterval(() => {
    generateProgress.value += 10
    if (generateProgress.value >= 100) {
      clearInterval(progressTimer)
      generateProgress.value = 100
      isGenerating.value = false
      reportPreview.value = true

      // 保存到历史报告
      const newReport = {
        title: reportConfig.value.title,
        createTime: new Date().toLocaleString(),
        type: reportConfig.value.type,
        format: reportConfig.value.format
      }
      historyReports.value.unshift(newReport)
      localStorage.setItem('reportHistory', JSON.stringify(historyReports.value))

      // 滚动到预览区
      document.querySelector('.preview-section').scrollIntoView({ behavior: 'smooth' })
    }
  }, 200)
}

// 生成总结建议
const generateSummary = () => {
  if (reportConfig.value.type === 'career') {
    return `综合来看，你选择了${userInfo.value.target}作为职业目标，结合你的${userInfo.value.major}专业背景，建议你按照规划的阶段逐步实施，重点提升相关专业技能和实践经验。在执行过程中，可根据实际情况动态调整规划内容，确保目标的可实现性。`
  } else if (reportConfig.value.type === 'ability') {
    return `你的核心能力中${abilityScores.value[0]?.dimension || '学习能力'}表现突出，${abilityScores.value[abilityScores.value.length-1]?.dimension || '创新能力'}需要重点提升。建议你在未来的学习和实践中，发挥优势能力，同时制定专项计划弥补短板，全面提升综合竞争力。`
  } else {
    return `你选择了${userInfo.value.target}作为职业目标，核心能力中${abilityScores.value[0]?.dimension || '学习能力'}表现突出。建议你结合职业规划和能力特点，优先选择能发挥优势的职业方向，同时针对性提升能力短板，为职业发展奠定坚实基础。`
  }
}

// 重置配置
const resetConfig = () => {
  reportConfig.value = {
    type: 'career',
    title: '',
    format: 'pdf'
  }
  updateReportTemplate()
  reportPreview.value = false
}

// 预览历史报告
const previewHistoryReport = (report) => {
  showHistory.value = false
  reportConfig.value.type = report.type
  reportConfig.value.title = report.title
  reportConfig.value.format = report.format
  updateReportTemplate()
  reportPreview.value = true
  document.querySelector('.preview-section').scrollIntoView({ behavior: 'smooth' })
}

// 导出报告
const exportReport = (report = null) => {
  const currentReport = report || {
    title: reportConfig.value.title,
    format: reportConfig.value.format
  }

  alert(`已开始导出【${currentReport.title}】为${currentReport.format.toUpperCase()}格式！`)

  // 导出文本版（基础版）
  exportTxtReport()
}

// 导出当前报告
const exportCurrentReport = () => {
  exportReport()
}

// 导出文本版报告
const exportTxtReport = () => {
  let reportContent = `
${reportConfig.value.title}
生成时间：${new Date().toLocaleString()}
==========================================
`

  // 基础信息
  if (getModule('basicInfo').checked) {
    reportContent += `一、基础信息
姓名：${userInfo.value.name || '未填写'}
性别：${userInfo.value.gender || '未填写'}
年级：${userInfo.value.grade || '未填写'}
专业：${userInfo.value.major || '未填写'}
目标方向：${userInfo.value.target || '未填写'}
职业兴趣：${userInfo.value.interest?.join('、') || '未填写'}

`
  }

  // 职业规划
  if (getModule('careerPlan').checked) {
    reportContent += `二、职业规划
${careerPlanStages.value.map(stage => `${stage.grade}：${stage.content}`).join('\n')}

`
  }

  // 能力测评
  if (getModule('abilityScore').checked) {
    reportContent += `三、能力测评分析
${abilityScores.value.map(item => `${item.dimension}：${item.score}/20（${item.level}）\n  建议：${item.suggestion}`).join('\n')}

`
  }

  // 职业适配建议
  if (getModule('careerSuggest').checked) {
    reportContent += `四、职业适配建议
${careerSuggestion || '暂无适配建议'}

`
  }

  // 总结与建议
  if (getModule('summary').checked) {
    reportContent += `五、总结与建议
${generateSummary()}

`
  }

  reportContent += `==========================================
本报告由大学生职业规划系统智能生成，仅供参考
`

  // 下载文件
  const blob = new Blob([reportContent], { type: 'text/plain' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `${reportConfig.value.title}_${new Date().getTime()}.txt`
  a.click()
  URL.revokeObjectURL(a.href)
}

// 打印报告
const printReport = () => {
  const previewContent = document.querySelector('.preview-content')
  if (previewContent) {
    const printWindow = window.open('', '_blank')
    printWindow.document.write(`
      <html>
        <head>
          <title>${reportConfig.value.title}</title>
          <style>
            body { font-family: "Microsoft Yahei", sans-serif; padding: 20px; }
            .report-header { text-align: center; margin-bottom: 20px; }
            .report-title { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
            .report-subtitle { font-size: 14px; color: #666; }
            .report-line { height: 1px; background: #333; margin: 10px 0; }
            .report-module { margin-bottom: 30px; }
            .module-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; border-left: 4px solid #2f54eb; padding-left: 10px; }
            .module-content { line-height: 1.8; }
            .info-table { width: 100%; border-collapse: collapse; }
            .info-table td { border: 1px solid #ccc; padding: 8px; }
            .table-label { font-weight: bold; width: 20%; }
            .stage-title { font-weight: bold; margin-bottom: 5px; }
            .stage-content { margin-bottom: 10px; line-height: 1.6; }
            .ability-item { margin-bottom: 15px; }
            .ability-dimension { font-weight: bold; margin-bottom: 5px; }
            .ability-score { margin-bottom: 5px; }
            .score-bar { height: 8px; background: #e8e8e8; border-radius: 4px; overflow: hidden; margin: 5px 0; }
            .score-fill { height: 100%; background: #2f54eb; }
            .report-footer { margin-top: 50px; text-align: center; font-size: 12px; color: #666; }
          </style>
        </head>
        <body>
          ${previewContent.innerHTML}
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }
}
</script>

<style scoped>
/* 全局容器 */
.report-generate {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f8f9fa;
  margin: 0;
  padding: 0;
}

/* 页面头部 */
.page-header {
  height: 70px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  width: 100%;
}
.header-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}
.page-title {
  display: flex;
  align-items: center;
  color: #2f54eb;
}
.title-icon {
  font-size: 24px;
  margin-right: 8px;
}
.page-title h1 {
  font-size: 20px;
  margin: 0;
}
.page-nav {
  display: flex;
  gap: 10px;
}
.back-btn, .history-btn {
  padding: 6px 15px;
  border: 1px solid #2f54eb;
  color: #2f54eb;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}

/* 历史报告弹窗 */
.history-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 999;
}
.modal-mask {
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
}
.modal-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  color: #2f54eb;
}
.close-btn {
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}
.modal-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}
.history-empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.history-item {
  padding: 15px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.history-title {
  font-weight: bold;
  flex: 1;
}
.history-time {
  font-size: 12px;
  color: #999;
  margin-right: 15px;
}
.history-actions {
  display: flex;
  gap: 10px;
}
.preview-btn {
  padding: 4px 10px;
  border: 1px solid #2f54eb;
  color: #2f54eb;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.export-btn {
  padding: 4px 10px;
  border: none;
  color: #fff;
  background: #2f54eb;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

/* 报告配置区 */
.config-section {
  padding: 40px 0;
}
.config-wrap {
  width: 1200px;
  margin: 0 auto;
}
.config-card {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.config-title {
  font-size: 20px;
  font-weight: bold;
  color: #2f54eb;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}
.config-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}
.config-item {
  display: flex;
  align-items: flex-start;
}
.config-label {
  width: 120px;
  text-align: right;
  margin-right: 20px;
  font-weight: bold;
  padding-top: 5px;
}
.config-select, .config-input {
  flex: 1;
  height: 36px;
  padding: 0 10px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  outline: none;
  max-width: 400px;
}
.module-group {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}
.module-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 15px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
.module-item input {
  margin-right: 8px;
}
.module-item:has(input:checked) {
  border-color: #2f54eb;
  background: rgba(47, 84, 235, 0.1);
}
.module-item:has(input:disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}
.module-tip {
  font-size: 12px;
  color: #999;
  margin-left: 8px;
}
.format-group {
  flex: 1;
  display: flex;
  gap: 20px;
}
.format-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.format-item input {
  margin-right: 8px;
}
.config-btn-group {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 10px;
}
.generate-btn {
  padding: 10px 30px;
  border: none;
  background: #2f54eb;
  color: #fff;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
.generate-btn:disabled {
  background: #e8e8e8;
  cursor: not-allowed;
}
.reset-btn {
  padding: 10px 30px;
  border: 1px solid #e8e8e8;
  color: #666;
  background: #fff;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

/* 报告预览区 */
.preview-section {
  padding: 20px 0 40px;
}
.preview-wrap {
  width: 1200px;
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}
.preview-header h2 {
  margin: 0;
  color: #2f54eb;
}
.preview-actions {
  display: flex;
  gap: 10px;
}
.print-btn {
  padding: 6px 15px;
  border: 1px solid #2f54eb;
  color: #2f54eb;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.preview-content {
  font-size: 14px;
  line-height: 1.8;
}
.report-header {
  text-align: center;
  margin-bottom: 40px;
}
.report-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}
.report-subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}
.report-line {
  height: 1px;
  background: #333;
  width: 80%;
  margin: 0 auto;
}
.report-module {
  margin-bottom: 40px;
}
.module-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  border-left: 4px solid #2f54eb;
  padding-left: 10px;
}
.info-table {
  width: 100%;
  border-collapse: collapse;
}
.info-table td {
  border: 1px solid #e8e8e8;
  padding: 10px;
}
.table-label {
  font-weight: bold;
  width: 20%;
  background: #f8f9fa;
}
.plan-stage {
  margin-bottom: 20px;
}
.stage-title {
  font-weight: bold;
  margin-bottom: 8px;
}
.plan-empty, .ability-empty {
  color: #999;
  padding: 20px 0;
  text-align: center;
}
.ability-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.ability-item {
  padding: 15px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
}
.ability-dimension {
  font-weight: bold;
  margin-bottom: 8px;
}
.ability-score {
  margin-bottom: 8px;
}
.score-bar {
  height: 8px;
  background: #e8e8e8;
  border-radius: 4px;
  overflow: hidden;
  margin: 8px 0;
}
.score-fill {
  height: 100%;
  background: #2f54eb;
}
.ability-suggestion {
  font-size: 14px;
  color: #666;
}
.suggest-content, .summary-content {
  line-height: 1.8;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}
.report-footer {
  margin-top: 60px;
  text-align: center;
  font-size: 12px;
  color: #999;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

/* 页脚 */
.page-footer {
  background: #fff;
  padding: 20px 0;
  border-top: 1px solid #e8e8e8;
  text-align: center;
  color: #666;
  font-size: 14px;
  margin-top: 20px;
}
.footer-wrap {
  width: 1200px;
  margin: 0 auto;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .header-wrap, .config-wrap, .preview-wrap, .footer-wrap {
    width: 90%;
  }
  .modal-content {
    width: 90%;
  }
}
@media (max-width: 768px) {
  .config-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .config-label {
    width: 100%;
    text-align: left;
    margin-bottom: 8px;
  }
  .module-group, .format-group {
    flex-direction: column;
    gap: 10px;
  }
  .preview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  .info-table td {
    display: block;
    width: 100%;
  }
}
</style>
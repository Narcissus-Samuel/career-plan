<template>
  <div class="career-planning-page">
    <div v-if="reportVisible" class="report-content">
      <div class="report-header">
        <div style="text-align: left; margin-bottom: 10px;">
          <el-button type="primary" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
        
        <h1 class="report-title">个人职业生涯发展报告</h1>
        <div class="report-meta">
          <span>生成时间：{{ reportTime }}</span>
          <span>目标岗位：{{ targetJob || '未匹配' }}</span>
          <span>职业兴趣：{{ careerTestAnalysis || '未填写' }}</span>
          <span>人岗匹配度：{{ matchDegree }}%</span>
        </div>
        <div class="report-actions">
          <el-button type="primary" @click="generateReport">重新生成报告</el-button>
          <el-button type="success" @click="editReport">编辑报告</el-button>
          <el-button type="warning" @click="exportReport">导出PDF</el-button>
        </div>
      </div>

      <div class="report-section">
        <h2 class="section-title">
          <i class="el-icon-user"></i> 个人基础信息
        </h2>
        <div class="info-grid">
          <div class="info-item"><label>姓名：</label>{{ studentName || '未知' }}</div>
          <div class="info-item"><label>性别：</label>{{ studentGender || '未知' }}</div>
          <div class="info-item"><label>专业：</label>{{ studentMajor || '未知' }}</div>
          <div class="info-item"><label>年级：</label>{{ studentGrade || '未知' }}</div>
          <div class="info-item"><label>学历：</label>{{ studentEducation || '本科' }}</div>
          <div class="info-item"><label>职业兴趣：</label>{{ careerTestAnalysis || '未知' }}</div>
          <div class="info-item"><label>目标岗位：</label>{{ targetJob || '未匹配' }}</div>
        </div>
      </div>

      <div class="report-section">
        <h2 class="section-title">
          <i class="el-icon-s-data"></i> 个人能力评分详情
        </h2>
        <el-table :data="abilityScoreTable" border style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="dimension" label="能力维度" align="center" />
          <el-table-column prop="score" label="个人得分" align="center" />
          <el-table-column prop="requirement" label="岗位要求" align="center" />
          <el-table-column prop="match" label="匹配度" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.match === '优秀' ? 'success' : scope.row.match === '良好' ? 'warning' : 'danger'">
                {{ scope.row.match }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="total-score">综合能力总分：{{ studentAbilityTotalScore }} 分</div>
      </div>

      <div class="report-section" v-if="studentInternship || studentProject">
        <h2 class="section-title">
          <i class="el-icon-briefcase"></i> 实习/项目经历
        </h2>
        <div class="experience-list">
          <div v-if="studentInternship" class="experience-item">
            <label>实习经历：</label>{{ studentInternship }}
          </div>
          <div v-if="studentProject" class="experience-item">
            <label>项目经历：</label>{{ studentProject }}
          </div>
        </div>
      </div>

      <div class="report-section">
        <h2 class="section-title">
          <i class="el-icon-user-check"></i> 人岗匹配核心分析
        </h2>
        <div class="match-overview">
          <h3>匹配度等级：{{ getMatchLevel() }}</h3>
          <el-progress :percentage="matchDegree" :status="getMatchStatus()" text-inside :stroke-width="20" />
          <p class="match-desc">
            {{ getMatchSummary() }}
          </p>
        </div>

        <div class="gap-analysis">
          <h3>核心短板识别</h3>
          <el-table :data="getWeakDimensions()" border style="width: 100%; margin-bottom: 15px" v-if="getWeakDimensions().length">
            <el-table-column prop="dimension" label="短板维度" align="center" />
            <el-table-column prop="gapValue" label="差距分值" align="center" />
            <el-table-column prop="impact" label="对匹配度影响" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.impact === '高' ? 'danger' : 'warning'">
                  {{ scope.row.impact }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <p v-else class="no-gap-text">恭喜！你在各维度均达到岗位要求，无明显短板。</p>
        </div>

        <div class="advantage-summary">
          <h3>核心优势总结</h3>
          <p>{{ getAdvantageSummary() }}</p>
        </div>
      </div>

      <div class="report-section">
        <h2 class="section-title">
          <i class="el-icon-search"></i> 职业探索与岗位匹配
        </h2>
        <div class="match-comparison">
          <h3>各维度契合度对比</h3>
          <el-table :data="matchComparisonList" border style="width: 100%; margin-bottom: 20px">
            <el-table-column prop="dimension" label="评估维度" align="center" />
            <el-table-column prop="personalScore" label="个人得分" align="center" />
            <el-table-column prop="jobRequirement" label="岗位要求" align="center" />
            <el-table-column prop="matchRate" label="契合度" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.matchRate >= 80 ? 'success' : scope.row.matchRate >= 60 ? 'warning' : 'danger'">
                  {{ scope.row.matchRate }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="gap" label="差距分析" align="center" />
          </el-table>
        </div>

        <div class="portrait-desc">
          <div class="portrait-item">
            <h3>目标岗位画像（{{ targetJob || '通用岗位' }}）</h3>
            <p>{{ getJobPortrait() }}</p>
          </div>
          <div class="portrait-item">
            <h3>个人就业能力画像</h3>
            <p>职业兴趣：{{ careerTestAnalysis || '未填写' }}；核心优势：{{ getPersonalAdvantage() }}；核心短板：{{ skillGap }}，需补充{{ certificateGap }}相关证书及实战经验。</p>
          </div>
        </div>
      </div>

      <div class="report-section">
        <h2 class="section-title">
          <i class="el-icon-sitemap"></i> 职业目标设定与职业路径规划
        </h2>

        <div class="career-goal">
          <h3>职业目标</h3>
          <div class="goal-list">
            <div class="goal-item">短期目标（{{ getShortTermDuration() }}）：{{ getShortTermGoal() }}</div>
            <div class="goal-item">中期目标（{{ getMidTermDuration() }}）：{{ getMidTermGoal() }}</div>
            <div class="goal-item">长期目标（{{ getLongTermDuration() }}）：{{ getLongTermGoal() }}</div>
          </div>
        </div>

        <div class="industry-trend">
          <h3>行业发展趋势与岗位数据关联性分析</h3>
          <p>{{ getIndustryTrend() }}</p>
          <p class="data-relevance">岗位数据关联性：{{ getJobDataRelevance() }}</p>
        </div>

        <div class="path-container">
          <div class="path-item">
            <h3>纵向晋升路径（核心路径）</h3>
            <div class="path-list">
              <span v-for="(item, index) in verticalPath" :key="index" class="path-node">
                {{ item }}
                <el-icon v-if="index < verticalPath.length - 1"><ArrowRight /></el-icon>
              </span>
            </div>
            <p class="path-desc">{{ getVerticalPathDesc() }}</p>
          </div>
          <div class="path-item">
            <h3>横向转型路径（备选路径）</h3>
            <div class="path-list">
              <span v-for="(item, index) in switchPath" :key="index" class="path-node">
                {{ item }}
                <el-icon v-if="index < switchPath.length - 1"><ArrowRight /></el-icon>
              </span>
            </div>
            <p class="path-desc">{{ getSwitchPathDesc() }}</p>
          </div>
        </div>
      </div>

      <div class="report-section">
        <h2 class="section-title">
          <i class="el-icon-lightbulb"></i> 行动计划与成果展示
        </h2>

        <div class="gap-makeup-plan" v-if="getWeakDimensions().length">
          <h3>差距弥补专项计划（优先级：{{ getGapPriority() }}）</h3>
          <div class="makeup-container">
            <div v-for="(weak, index) in getWeakDimensions()" :key="index" class="makeup-item">
              <h4>{{ weak.dimension }} - 差距{{ weak.gapValue }}分</h4>
              <div class="makeup-content">
                <div class="makeup-subitem">
                  <label>弥补目标：</label>
                  <p>{{ getMakeupTarget(weak.dimension) }}</p>
                </div>
                <div class="makeup-subitem">
                  <label>具体措施：</label>
                  <p>{{ getMakeupMeasures(weak.dimension) }}</p>
                </div>
                <div class="makeup-subitem">
                  <label>完成时限：</label>
                  <p>{{ getMakeupDeadline(weak.dimension) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="action-plan">
          <h3>分阶段成长计划</h3>
          <div class="plan-container">
            <div class="plan-item">
              <h4>短期计划（{{ getShortTermDuration() }}）</h4>
              <div class="plan-content">
                <div class="plan-subitem">
                  <label>学习路径：</label>
                  <p>{{ getShortTermStudyPath() }}</p>
                </div>
                <div class="plan-subitem">
                  <label>实践安排：</label>
                  <p>{{ getShortTermPracticePlan() }}</p>
                </div>
                <div class="plan-subitem">
                  <label>证书目标：</label>
                  <p>{{ getShortTermCertificatePlan() }}</p>
                </div>
              </div>
            </div>

            <div class="plan-item">
              <h4>中期计划（{{ getMidTermDuration() }}）</h4>
              <div class="plan-content">
                <div class="plan-subitem">
                  <label>学习路径：</label>
                  <p>{{ getMidTermStudyPath() }}</p>
                </div>
                <div class="plan-subitem">
                  <label>实践安排：</label>
                  <p>{{ getMidTermPracticePlan() }}</p>
                </div>
                <div class="plan-subitem">
                  <label>证书目标：</label>
                  <p>{{ getMidTermCertificatePlan() }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="evaluation">
          <h3>评估周期与指标</h3>
          <el-table :data="getEvaluationList()" border style="width: 100%">
            <el-table-column prop="cycle" label="评估周期" align="center" />
            <el-table-column prop="indicators" label="评估指标" align="center" />
            <el-table-column prop="adjustment" label="调整方式" align="center" />
          </el-table>
          <p class="evaluation-desc">说明：每完成一个评估周期，对照评估指标检查完成情况，若未达到预期，调整学习/实践计划；若超出预期，可提前推进下一阶段目标，确保职业发展路径贴合个人实际与行业变化。</p>
        </div>

        <div class="achievement">
          <h3>成果展示规划</h3>
          <p>{{ getAchievementPlan() }}</p>
        </div>
      </div>
    </div>

    <div v-else class="loading-container">
      <el-loading-spinner />
      <p>正在加载职业生涯发展报告，请稍候...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElLoading } from 'element-plus'
import { useRouter } from 'vue-router'
import { ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
import html2pdf from 'html2pdf.js'

const router = useRouter()

const goBack = () => {
  router.go(-1)
}

const reportVisible = ref(false)
const reportTime = ref('')
const targetJob = ref('')
const matchDegree = ref(0)
const careerTestAnalysis = ref('')

// 职业兴趣与岗位的映射关系
const jobInterestMapping = {
  '数据分析师': '数据分析与挖掘、数据可视化、商业智能',
  '前端开发工程师': '前端开发、用户界面设计、交互体验优化',
  '产品经理': '产品设计、需求分析、用户体验研究',
  'UI设计师': '视觉设计、交互设计、用户体验设计',
  '电商运营': '电商平台运营、流量增长、用户转化',
  '科研人员': '科学研究、实验设计、学术创新'
}

const matchComparisonList = ref([
  { dimension: '专业技能', personalScore: 0, jobRequirement: '85分', matchRate: 0, gap: '' },
  { dimension: '通用素质', personalScore: 0, jobRequirement: '80分', matchRate: 0, gap: '' },
  { dimension: '实践经验', personalScore: 0, jobRequirement: '75分', matchRate: 0, gap: '' },
  { dimension: '职业素养', personalScore: 0, jobRequirement: '80分', matchRate: 0, gap: '' },
])

const evaluationList = ref([
  { cycle: '每季度', indicators: '学习进度、技能掌握情况、实践成果', adjustment: '调整学习计划、补充薄弱技能' },
  { cycle: '每半年', indicators: '岗位适配度、证书完成情况、项目经验积累', adjustment: '优化实践安排、调整目标优先级' },
  { cycle: '每年', indicators: '综合能力提升、行业趋势适配性、职业目标达成度', adjustment: '调整职业路径、优化长期计划' },
])

const studentName = ref('')
const studentGender = ref('')
const studentMajor = ref('')
const studentGrade = ref('')
const studentEducation = ref('')
const studentSkills = ref([])
const studentCertificates = ref([])
const studentInternship = ref('')
const studentProject = ref('')

const studentInnovationScore = ref(80)
const studentLearningScore = ref(85)
const studentPressureScore = ref(75)
const studentCommunicationScore = ref(80)
const studentInternshipScore = ref(70)
const studentAbilityTotalScore = ref(0)

const testAnalysis = ref({})
const matchResult = ref({})
const verticalPath = ref([])
const switchPath = ref([])
const skillGap = ref('')
const certificateGap = ref('')

const abilityScoreTable = ref([
  { dimension: '基础要求', score: 0, requirement: '80分', match: '' },
  { dimension: '专业技能', score: 0, requirement: '85分', match: '' },
  { dimension: '职业素养', score: 0, requirement: '80分', match: '' },
  { dimension: '发展潜力', score: 0, requirement: '85分', match: '' },
])

const pathConfig = {
  '数据分析师': {
    vertical: ['初级数据分析师', '中级数据分析师', '高级数据分析师', '数据分析主管', '数据总监'],
    switch: ['大数据开发工程师', '产品经理', '金融分析师']
  },
  '前端开发工程师': {
    vertical: ['初级前端', '中级前端', '高级前端', '前端技术组长', '前端架构师'],
    switch: ['UI设计师', '全栈开发工程师', '产品经理']
  },
  '产品经理': {
    vertical: ['产品助理', '初级产品经理', '高级产品经理', '产品总监', 'CEO'],
    switch: ['数据分析师', '电商运营', '项目经理']
  },
  'UI设计师': {
    vertical: ['UI设计师', '资深UI设计师', '交互设计组长', '设计总监', '创意总监'],
    switch: ['前端开发工程师', '产品经理', '电商运营']
  },
  '电商运营': {
    vertical: ['运营助理', '电商运营专员', '运营主管', '运营经理', '运营总监'],
    switch: ['产品经理', '数据分析师', 'UI设计师']
  },
  '科研人员': {
    vertical: ['助理研究员', '副研究员', '研究员', '高级研究员', '学科带头人'],
    switch: ['高校教师', '企业研发主管', '技术顾问']
  }
}

const getMatchLevel = () => {
  if (matchDegree.value >= 90) return '优秀匹配'
  if (matchDegree.value >= 80) return '良好匹配'
  if (matchDegree.value >= 70) return '基本匹配'
  if (matchDegree.value >= 60) return '待提升匹配'
  return '低匹配度'
}

const getMatchStatus = () => {
  if (matchDegree.value >= 80) return 'success'
  if (matchDegree.value >= 60) return 'warning'
  return 'exception'
}

const getMatchSummary = () => {
  if (matchDegree.value >= 90) {
    return `你的综合人岗匹配度为${matchDegree.value}%（优秀匹配），在各维度均达到${targetJob.value}岗位要求，具备直接上岗的核心能力。建议重点提升差异化竞争力，向更高阶岗位目标迈进。`
  } else if (matchDegree.value >= 80) {
    return `你的综合人岗匹配度为${matchDegree.value}%（良好匹配），整体符合${targetJob.value}岗位要求，但在${getWeakDimensions()[0]?.dimension || '部分'}维度存在小幅差距。建议针对性弥补短板，快速达到优秀匹配水平。`
  } else if (matchDegree.value >= 70) {
    return `你的综合人岗匹配度为${matchDegree.value}%（基本匹配），具备${targetJob.value}岗位的基础能力，但在${getWeakDimensions().map(item => item.dimension).join('、')}维度存在明显差距。建议制定专项提升计划，优先弥补核心短板。`
  } else if (matchDegree.value >= 60) {
    return `你的综合人岗匹配度为${matchDegree.value}%（待提升匹配），与${targetJob.value}岗位要求仍有较大差距，核心短板为${getWeakDimensions().map(item => item.dimension).join('、')}。建议延长基础学习周期，重点夯实核心能力。`
  } else {
    return `你的综合人岗匹配度为${matchDegree.value}%（低匹配度），与${targetJob.value}岗位要求差距显著。建议重新评估岗位适配性，或制定长期系统性提升计划，从基础能力开始全面补强。`
  }
}

const getWeakDimensions = () => {
  return matchComparisonList.value
    .filter(item => item.matchRate < 70)
    .map(item => ({
      dimension: item.dimension,
      gapValue: item.dimension === '专业技能' ? 85 - item.personalScore :
                item.dimension === '通用素质' ? 80 - item.personalScore :
                item.dimension === '实践经验' ? 75 - item.personalScore : 80 - item.personalScore,
      impact: (item.dimension === '专业技能' || item.dimension === '实践经验') ? '高' : '中'
    }))
}

const getAdvantageSummary = () => {
  const advantages = matchComparisonList.value
    .filter(item => item.matchRate >= 85)
    .map(item => item.dimension)
  
  if (advantages.length === 0) {
    return '目前暂未形成明显竞争优势，建议先夯实基础能力，再逐步打造个人核心优势。'
  } else if (advantages.length === matchComparisonList.value.length) {
    return `你在${advantages.join('、')}等维度均表现优秀，具备${targetJob.value}岗位的核心竞争力，建议重点提升行业视野和高阶能力。`
  } else {
    return `你在${advantages.join('、')}维度表现突出，是匹配${targetJob.value}岗位的核心优势。建议发挥优势的同时，弥补其他维度的短板。`
  }
}

const getShortTermDuration = () => {
  return matchDegree.value >= 80 ? '1年' : matchDegree.value >= 70 ? '1.5年' : '2年'
}

const getMidTermDuration = () => {
  return matchDegree.value >= 80 ? '2-3年' : matchDegree.value >= 70 ? '3-4年' : '4-5年'
}

const getLongTermDuration = () => {
  return matchDegree.value >= 80 ? '3-5年' : matchDegree.value >= 70 ? '5-8年' : '8-10年'
}

const getShortTermGoal = () => {
  if (matchDegree.value >= 90) {
    return `立足${targetJob.value}正式岗位，快速适应工作节奏，3个月内独立完成核心工作任务，6个月内成为团队核心成员。`
  } else if (matchDegree.value >= 80) {
    return `立足${targetJob.value}入门岗位，3个月内弥补${getWeakDimensions()[0]?.dimension || '核心'}短板，6个月内达到岗位优秀匹配水平，1年内独立负责小型任务。`
  } else if (matchDegree.value >= 70) {
    return `先通过实习/培训夯实${targetJob.value}岗位基础能力，6个月内弥补核心短板（${getWeakDimensions().map(item => item.dimension).join('、')}），1.5年内达到岗位基本要求，实现稳定上岗。`
  } else {
    return `系统学习${targetJob.value}岗位核心技能，1年内完成基础能力建设，2年内通过实习积累实战经验，达到岗位60%以上匹配度，实现初步上岗。`
  }
}

const getMidTermGoal = () => {
  if (matchDegree.value >= 80) {
    return `晋升至${verticalPath.value[1] || '中级岗位'}，独立负责核心项目，将人岗匹配度提升至90%以上，成为团队骨干，形成个人核心竞争力。`
  } else {
    return `先达到${targetJob.value}岗位80%以上匹配度，再冲击${verticalPath.value[1] || '中级岗位'}，具备独立完成常规项目的能力，成为团队合格成员。`
  }
}

const getLongTermGoal = () => {
  if (matchDegree.value >= 80) {
    return `冲刺${verticalPath.value[3] || '管理/资深岗位'}，具备统筹规划、团队管理能力，成为${targetJob.value}领域的资深专家或管理者。`
  } else {
    return `先稳定胜任${verticalPath.value[2] || '高级岗位'}，再根据能力提升情况，向${verticalPath.value[3] || '管理/资深岗位'}迈进，实现职业价值最大化。`
  }
}

const getVerticalPathDesc = () => {
  if (matchDegree.value >= 80) {
    return `基于你较高的人岗匹配度，可加快晋升节奏，每1-2年完成一次晋升跃迁。重点在每个阶段巩固优势，同时补齐该阶段所需的新能力。`
  } else if (matchDegree.value >= 70) {
    return `基于你当前的匹配度水平，建议稳扎稳打推进晋升，每2-3年完成一次晋升。优先弥补核心短板，再学习该阶段所需的进阶能力。`
  } else {
    return `基于你当前的匹配度水平，建议延长基础阶段周期（2-3年），全面夯实核心能力。待匹配度提升至70%以上后，再按正常节奏推进晋升。`
  }
}

const getSwitchPathDesc = () => {
  if (matchDegree.value >= 80) {
    return `作为能力拓展的备选路径，当核心路径发展遇到瓶颈时，可利用现有优势转向相关领域，实现平滑转型。`
  } else {
    return `若核心路径推进困难（匹配度长期低于70%），可考虑转向技能要求相近的岗位，降低转型成本，先实现稳定就业，再逐步提升。`
  }
}

const getGapPriority = () => {
  const weakDimensions = getWeakDimensions()
  if (weakDimensions.some(item => item.impact === '高')) {
    return '先弥补高影响维度（专业技能/实践经验），再补充中影响维度'
  } else {
    return '按差距分值从高到低依次弥补'
  }
}

const getMakeupTarget = (dimension) => {
  const targetScore = dimension === '专业技能' ? 85 :
                     dimension === '通用素质' ? 80 :
                     dimension === '实践经验' ? 75 : 80
  return `在${getShortTermDuration()}内将${dimension}得分提升至${targetScore}分以上，匹配度达到70%以上`
}

const getMakeupMeasures = (dimension) => {
  switch(dimension) {
    case '专业技能':
      return `1. 系统学习${skillGap.value}核心知识点，完成至少3个专项练习；2. 跟随资深工程师/分析师学习，每周进行1次技能复盘；3. 参与${targetJob.value}相关实战项目，将理论转化为实操能力。`
    case '通用素质':
      return `1. 参加沟通/学习能力提升训练营，每月完成1次复盘；2. 主动承担团队沟通协调工作，积累实战经验；3. 建立知识管理体系，提升快速学习和应用能力。`
    case '实践经验':
      return `1. 寻找${targetJob.value}相关实习，至少累计6个月全职实习经验；2. 独立完成2-3个实战项目，形成可展示的作品集；3. 向行业前辈请教，学习实战技巧和工作方法。`
    case '职业素养':
      return `1. 学习职场礼仪和职业规范，建立职业心态；2. 制定抗压训练计划，提升情绪管理能力；3. 培养责任意识，做到事事有回应、件件有着落。`
    default:
      return `制定专项学习计划，每天投入2小时学习${dimension}相关知识，每月进行1次能力测评，持续优化提升。`
  }
}

const getMakeupDeadline = (dimension) => {
  const weakDimensions = getWeakDimensions()
  const targetDimension = weakDimensions.find(item => item.dimension === dimension)
  
  if (targetDimension?.impact === '高') {
    return `${getShortTermDuration().replace('年', '')}年内（优先完成）`
  } else {
    return `${getShortTermDuration().replace('年', '')}年内（第${weakDimensions.indexOf(targetDimension)+1}优先级）`
  }
}

const getShortTermPracticePlan = () => {
  if (matchDegree.value >= 80) {
    return `1. 入职${targetJob.value}正式岗位，参与核心项目；2. 每月完成1个技能提升小项目，强化优势能力；3. 参与行业高端沙龙，拓展人脉和视野。`
  } else if (matchDegree.value >= 70) {
    return `1. 寻找${targetJob.value}相关实习（至少3个月），积累实操经验；2. 完成${getProjectExample()}等2个实战项目，弥补实践短板；3. 参与行业基础培训，夯实核心技能。`
  } else {
    return `1. 先通过线上课程/培训掌握${targetJob.value}基础技能；2. 完成3-4个模拟项目，积累基础经验；3. 寻找入门级实习/兼职，逐步接触真实工作场景。`
  }
}

const getMidTermPracticePlan = () => {
  if (matchDegree.value >= 80) {
    return `1. 独立负责核心项目，带领1-2人小团队；2. 参与行业前沿项目，掌握最新技术/方法；3. 输出行业分享/案例，建立个人专业影响力。`
  } else {
    return `1. 从辅助参与项目到逐步独立负责小型项目；2. 积累3-5个完整项目经验，弥补实践短板；3. 学习项目管理基础，为团队管理做准备。`
  }
}

const getShortTermCertificatePlan = () => {
  const certs = certificateGap.value.split('、')
  if (matchDegree.value >= 80) {
    return `${certs[0]}（优先）、${certs[1] || '相关进阶证书'}，争取一次性通过，提升竞争力。`
  } else {
    return `优先考取${certs[0]}（基础证书），夯实能力基础；${certs[1] ? `待匹配度提升至70%以上后，再考取${certs[1]}` : ''}。`
  }
}

const getMidTermCertificatePlan = () => {
  const certs = certificateGap.value.split('、')
  return `${certs[2] || '高级行业证书'}，补充1项跨领域技能证书（如项目管理、数据分析相关），提升综合竞争力。`
}

const getEvaluationList = () => {
  if (matchDegree.value < 70) {
    return [
      { cycle: '每月', indicators: '基础技能学习进度、短板弥补情况', adjustment: '调整学习计划，增加薄弱技能学习时长' },
      { cycle: '每季度', indicators: '基础能力提升、入门级实践成果', adjustment: '优化学习方法，增加实战练习' },
      { cycle: '每半年', indicators: '岗位适配度提升、基础证书完成情况', adjustment: '调整学习重点，优先弥补核心短板' },
    ]
  } else if (matchDegree.value < 80) {
    return [
      { cycle: '每季度', indicators: '核心技能掌握情况、实践成果', adjustment: '调整学习计划、补充薄弱技能' },
      { cycle: '每半年', indicators: '岗位适配度、证书完成情况', adjustment: '优化实践安排、调整目标优先级' },
      { cycle: '每年', indicators: '综合能力提升、职业目标达成度', adjustment: '调整职业路径、优化长期计划' },
    ]
  } else {
    return [
      { cycle: '每季度', indicators: '进阶技能掌握、项目成果质量', adjustment: '加速学习进度、挑战更高阶任务' },
      { cycle: '每半年', indicators: '团队贡献度、行业影响力', adjustment: '拓展能力边界、向管理岗准备' },
      { cycle: '每年', indicators: '职业目标达成度、行业竞争力', adjustment: '优化职业路径、冲刺更高阶目标' },
    ]
  }
}

const getAchievementPlan = () => {
  if (matchDegree.value < 70) {
    return `1. 月度成果：每月记录${getWeakDimensions().map(item => item.dimension).join('、')}维度的能力提升分数，跟踪弥补进度；2. 季度成果：整理学习笔记、基础项目成果，对比岗位要求找差距；3. 年度成果：完成基础能力测评，确保匹配度提升至70%以上，具备上岗基础。`
  } else {
    return `1. 阶段性成果：每季度整理项目成果、技能提升报告，对比岗位高阶要求；2. 长期成果：完善个人作品集，重点展示核心优势维度的成果；3. 动态展示：定期更新人岗匹配度评分，确保每年提升5-10个百分点，逐步达到优秀匹配水平。`
  }
}

const getJobPortrait = () => {
  switch(targetJob.value) {
    case '数据分析师':
      return '核心要求：熟练掌握SQL、Python、Tableau等工具，具备数据清洗、可视化、分析能力；通用要求：逻辑思维清晰、沟通能力强，能将分析结果转化为业务建议；实践要求：有相关数据分析项目或实习经验。'
    case '前端开发工程师':
      return '核心要求：熟练掌握HTML、CSS、JavaScript，精通Vue3/React框架，了解工程化部署；通用要求：注重细节、学习能力强，能配合产品和设计完成开发需求；实践要求：有前端项目开发经验，熟悉浏览器兼容性问题。'
    case '产品经理':
      return '核心要求：掌握Axure、墨刀等原型工具，具备需求分析、用户调研能力，能撰写PRD文档；通用要求：沟通协调能力强、有同理心，了解行业动态和用户需求；实践要求：有产品原型设计、项目跟进经验。'
    case 'UI设计师':
      return '核心要求：熟练掌握Figma、PS等设计工具，具备视觉设计、交互设计能力，了解品牌视觉规范；通用要求：审美能力强、注重细节，能配合产品和前端落地设计方案；实践要求：有APP/网页设计作品集，了解设计趋势。'
    case '电商运营':
      return '核心要求：熟悉电商平台规则，具备流量运营、直播策划、数据分析能力；通用要求：执行力强、敏感度高，能快速响应平台变化；实践要求：有店铺运营、直播带货相关经验，能提升店铺转化和复购。'
    case '科研人员':
      return '核心要求：具备扎实的专业理论基础，掌握科研方法和实验技能，能独立开展研究工作；通用要求：逻辑思维严谨、创新能力强、耐挫力高；实践要求：有相关科研项目经验，发表过学术论文或申请过专利。'
    default:
      return '核心要求：具备岗位所需核心专业技能；通用要求：沟通能力、学习能力、抗压能力强；实践要求：有相关实习或项目经验，具备一定的实操能力。'
  }
}

const getPersonalAdvantage = () => {
  const advantages = [];
  if (studentSkills.value.length >= 3) advantages.push('专业技能扎实')
  if (studentCommunicationScore.value >= 80) advantages.push('沟通能力优秀')
  if (studentLearningScore.value >= 85) advantages.push('学习能力强')
  if (studentInternship.value) advantages.push('有相关实习经验')
  if (studentProject.value) advantages.push('有实战项目经验')
  return advantages.length > 0 ? advantages.join('、') : '学习态度积极，具备较强的适应能力'
}

const getIndustryTrend = () => {
  switch(targetJob.value) {
    case '数据分析师':
      return '随着大数据、人工智能的发展，数据分析师岗位需求持续增长，行业趋势向“数据驱动业务”转型，要求从业者具备跨领域知识（如业务+技术），能为企业决策提供精准支持，中高级数据分析师缺口较大。'
    case '前端开发工程师':
      return '前端开发行业技术更新迭代快，向“全栈化、工程化、智能化”发展，Vue3、React等框架成为主流，对前端工程师的工程化部署、跨端开发能力要求提升，具备全栈开发能力者更具竞争力。'
    case '产品经理':
      return '产品经理岗位覆盖互联网、传统行业等多个领域，趋势向“精细化、专业化”发展，ToB产品、AI相关产品需求增长，要求从业者具备较强的业务理解能力、数据分析能力和跨团队协作能力。'
    case 'UI设计师':
      return 'UI设计行业向“体验设计”转型，不再局限于视觉设计，要求从业者具备交互设计、动效设计、用户研究能力，Figma等协同设计工具广泛应用，具备全链路设计能力者更受企业青睐。'
    case '电商运营':
      return '电商行业持续发展，直播电商、跨境电商成为新增长点，行业趋势向“精细化运营、内容化运营”转型，要求从业者具备数据分析、流量运营、内容策划能力，能适应平台规则和用户需求的快速变化。'
    case '科研人员':
      return '科研行业注重创新能力和学术积累，趋势向“交叉学科、产学研结合”发展，要求科研人员具备跨学科研究能力，能将科研成果转化为实际应用，具备项目申报和团队协作能力者更具竞争力。'
    default:
      return '当前行业发展态势良好，岗位需求稳定，随着技术和市场的变化，对从业者的专业技能和综合素养要求不断提升，具备持续学习能力和实战经验者更易实现职业突破。'
  }
}

const getJobDataRelevance = () => {
  switch(targetJob.value) {
    case '数据分析师':
      return '岗位核心数据（如用户留存率、销售转化率）与业务指标强关联，需结合业务场景分析数据，数据准确性直接影响企业决策，个人擅长的数据处理能力与岗位核心需求高度契合。'
    case '前端开发工程师':
      return '岗位核心数据（如页面加载速度、兼容性通过率）与用户体验强关联，需结合产品需求优化开发方案，个人擅长的框架使用、代码优化能力与岗位技术要求高度匹配。'
    case '产品经理':
      return '岗位核心数据（如用户活跃度、需求落地率）与产品迭代强关联，需结合用户调研数据优化产品功能，个人擅长的需求分析、原型设计能力与岗位核心职责高度契合。'
    case 'UI设计师':
      return '岗位核心数据（如设计落地率、用户满意度）与产品视觉体验强关联，需结合产品定位和用户喜好优化设计方案，个人擅长的视觉设计、交互设计能力与岗位需求高度匹配。'
    case '电商运营':
      return '岗位核心数据（如店铺流量、转化率、复购率）与运营效果强关联，需结合数据调整运营策略，个人擅长的流量运营、直播策划能力与岗位核心目标高度契合。'
    case '科研人员':
      return '岗位核心数据（如论文发表数量、项目立项数、成果转化率）与科研成果强关联，需结合学科发展趋势开展研究工作，个人擅长的实验设计、数据分析能力与岗位核心要求高度契合。'
    default:
      return '岗位核心数据与业务目标、用户需求紧密关联，个人擅长方向与岗位核心要求匹配，需通过实践不断提升数据解读和实操能力，实现个人能力与岗位需求的深度契合。'
  }
}

const getShortTermStudyPath = () => {
  switch(targetJob.value) {
    case '数据分析师':
      return '1. 系统学习SQL、Python基础语法及数据分析库（Pandas、Matplotlib）；2. 学习Tableau数据可视化工具，掌握图表制作和仪表盘搭建；3. 学习数据分析思维，掌握数据清洗、建模、解读方法。'
    case '前端开发工程师':
      return '1. 巩固HTML、CSS、JavaScript基础，掌握ES6+语法；2. 系统学习Vue3框架（Composition API、Pinia），掌握组件开发、路由配置；3. 学习前端工程化（Webpack、Vite），了解跨域、性能优化基础。'
    case '产品经理':
      return '1. 学习产品经理基础理论，了解产品生命周期；2. 熟练掌握Axure、墨刀等原型工具，学习PRD文档撰写规范；3. 学习用户调研方法，掌握需求分析和优先级排序技巧。'
    case 'UI设计师':
      return '1. 熟练掌握Figma、PS等设计工具，学习视觉设计基础（色彩、排版、字体）；2. 学习交互设计原则，了解用户体验设计流程；3. 临摹优秀设计作品，积累设计灵感，制作个人作品集。'
    case '电商运营':
      return '1. 学习电商平台规则（淘宝、抖音等），了解流量获取逻辑；2. 学习数据分析基础，掌握店铺数据解读和优化方法；3. 学习直播策划、短视频制作基础，了解内容运营技巧。'
    case '科研人员':
      return '1. 夯实专业理论基础，系统学习科研方法论和实验设计；2. 学习文献检索和分析方法，掌握学术论文写作规范；3. 参与课题组研究项目，学习科研项目申报和执行流程。'
    default:
      return '1. 系统学习岗位核心专业技能，掌握基础工具和方法；2. 学习行业基础知识，了解岗位核心职责；3. 关注行业前沿动态，积累相关知识和经验。'
  }
}

const getMidTermStudyPath = () => {
  switch(targetJob.value) {
    case '数据分析师':
      return '1. 深入学习Python高级数据分析、机器学习基础，掌握常见算法应用；2. 学习业务分析方法，能结合业务场景提供精准分析建议；3. 学习数据可视化高级技巧，制作专业仪表盘，提升数据呈现能力。'
    case '前端开发工程师':
      return '1. 学习React框架，掌握Hooks、Redux等核心知识点；2. 深入学习前端性能优化、跨端开发（小程序、APP）；3. 学习Node.js基础，向全栈开发方向进阶，提升综合开发能力。'
    case '产品经理':
      return '1. 学习产品战略规划，掌握产品迭代和版本管理方法；2. 深入学习数据分析，能通过数据驱动产品优化；3. 学习项目管理基础，提升跨团队协作和项目推进能力。'
    case 'UI设计师':
      return '1. 学习动效设计、3D设计基础，提升设计表现力；2. 学习品牌视觉规范制定，掌握全链路设计方法；3. 学习用户研究进阶技巧，能结合用户需求优化设计方案，提升用户体验。'
    case '电商运营':
      return '1. 学习精细化运营方法，掌握用户分层、精准营销技巧；2. 学习跨境电商运营知识，拓展运营领域；3. 学习团队管理基础，提升团队协作和运营统筹能力。'
    case '科研人员':
      return '1. 深入开展专项研究，尝试独立申请科研项目；2. 学习跨学科研究方法，拓展研究视野；3. 学习科研成果转化路径，提升产学研结合能力。'
    default:
      return '1. 深入学习岗位高级技能，形成个人核心竞争力；2. 学习跨领域知识，提升综合素养；3. 学习管理基础，为晋升管理岗位做准备。'
  }
}

const getProjectExample = () => {
  if (targetJob.value === '数据分析师') {
    return '用户行为数据分析、销售数据可视化项目、电商用户画像分析'
  } else if (targetJob.value === '前端开发工程师') {
    return '企业官网开发、电商小程序、管理后台前端重构'
  } else if (targetJob.value === '产品经理') {
    return '校园服务小程序需求分析、ToB产品原型设计、用户调研与需求迭代'
  } else if (targetJob.value === 'UI设计师') {
    return 'APP界面设计、网页视觉重构、品牌视觉规范制定'
  } else if (targetJob.value === '电商运营') {
    return '店铺流量运营、直播带货策划、用户复购率提升项目'
  } else if (targetJob.value === '科研人员') {
    return '专项课题研究、实验数据整理分析、学术论文撰写发表'
  } else {
    return '贴合岗位需求的实战项目'
  }
}

const calculateAbilityMatch = () => {
  const studentAbility = JSON.parse(localStorage.getItem('studentAbility') || '{}')
  
  abilityScoreTable.value[0].score = studentAbility.baseScore || 90
  abilityScoreTable.value[0].match = abilityScoreTable.value[0].score >= 80 ? '优秀' : '良好'
  
  abilityScoreTable.value[1].score = studentAbility.skillScore || (studentSkills.value.length >= 3 ? 85 : 70)
  abilityScoreTable.value[1].match = abilityScoreTable.value[1].score >= 85 ? '优秀' : abilityScoreTable.value[1].score >= 70 ? '良好' : '待提升'
  
  abilityScoreTable.value[2].score = Math.round((studentCommunicationScore.value + studentPressureScore.value) / 2)
  abilityScoreTable.value[2].match = abilityScoreTable.value[2].score >= 80 ? '优秀' : abilityScoreTable.value[2].score >= 70 ? '良好' : '待提升'
  
  abilityScoreTable.value[3].score = Math.round((studentInnovationScore.value + studentLearningScore.value) / 2)
  abilityScoreTable.value[3].match = abilityScoreTable.value[3].score >= 85 ? '优秀' : abilityScoreTable.value[3].score >= 75 ? '良好' : '待提升'
  
  studentAbilityTotalScore.value = Math.round(
    (abilityScoreTable.value[0].score + abilityScoreTable.value[1].score + 
     abilityScoreTable.value[2].score + abilityScoreTable.value[3].score) / 4
  )

  const professionalScore = abilityScoreTable.value[1].score
  const qualityScore = abilityScoreTable.value[2].score
  const practiceScore = studentInternship.value ? 80 : (studentProject.value ? 75 : 65)
  const generalScore = Math.round((studentCommunicationScore.value + studentLearningScore.value) / 2)

  matchComparisonList.value[0] = {
    dimension: '专业技能',
    personalScore: professionalScore,
    jobRequirement: '85分',
    matchRate: Math.round((professionalScore / 85) * 100),
    gap: professionalScore >= 85 ? '无明显差距' : `需提升${85 - professionalScore}分，重点补充${skillGap.value}`
  }
  matchComparisonList.value[1] = {
    dimension: '通用素质',
    personalScore: generalScore,
    jobRequirement: '80分',
    matchRate: Math.round((generalScore / 80) * 100),
    gap: generalScore >= 80 ? '无明显差距' : `需提升${80 - generalScore}分，重点锻炼沟通、学习能力`
  }
  matchComparisonList.value[2] = {
    dimension: '实践经验',
    personalScore: practiceScore,
    jobRequirement: '75分',
    matchRate: Math.round((practiceScore / 75) * 100),
    gap: practiceScore >= 75 ? '无明显差距' : '需增加实习、项目经验，提升实操能力'
  }
  matchComparisonList.value[3] = {
    dimension: '职业素养',
    personalScore: qualityScore,
    jobRequirement: '80分',
    matchRate: Math.round((qualityScore / 80) * 100),
    gap: qualityScore >= 80 ? '无明显差距' : `需提升${80 - qualityScore}分，重点锻炼抗压、责任意识`
  }

  matchDegree.value = Math.round(
    (matchComparisonList.value[0].matchRate + 
     matchComparisonList.value[1].matchRate + 
     matchComparisonList.value[2].matchRate + 
     matchComparisonList.value[3].matchRate) / 4
  )
}

const initReportData = () => {
  const now = new Date()
  reportTime.value = `${now.getFullYear()}-${(now.getMonth()+1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

  // 从localStorage获取人岗匹配选择的目标岗位
  const savedTargetJob = localStorage.getItem('targetJob')
  if (savedTargetJob) {
    targetJob.value = savedTargetJob
  } else if (testAnalysis.value.recommendJob) {
    targetJob.value = testAnalysis.value.recommendJob
  }

  // 修改这里：使用真实的职业兴趣测评结果，而不是目标岗位映射
  // 优先使用测评结果中的兴趣类型
  if (testAnalysis.value.interestType) {
    careerTestAnalysis.value = testAnalysis.value.interestType; // 如：现实型、研究型等
  } else {
    // // 备用方案：如果没有测评结果，才使用目标岗位映射
    // careerTestAnalysis.value = jobInterestMapping[targetJob.value] || `${targetJob.value}相关领域`
  }

  const config = pathConfig[targetJob.value] || pathConfig['数据分析师']
  verticalPath.value = config.vertical
  switchPath.value = config.switch

  if (testAnalysis.value.abilityScores) {
    const abilityScores = Array.isArray(testAnalysis.value.abilityScores) 
      ? testAnalysis.value.abilityScores 
      : [];
    const lowAbility = abilityScores.length > 0 
      ? abilityScores.sort((a, b) => a.score - b.score)[0] 
      : null;
    skillGap.value = lowAbility ? lowAbility.name.replace('能力', '') : '核心专业'
  } else {
    switch(targetJob.value) {
      case '数据分析师':
        skillGap.value = 'Tableau、SQL、Python数据分析'
        certificateGap.value = 'CDA数据分析师、计算机二级、英语六级'
        break
      case '前端开发工程师':
        skillGap.value = 'Vue3、React、工程化部署'
        certificateGap.value = '软考Web前端、计算机三级、前端工程师认证'
        break
      case '产品经理':
        skillGap.value = 'Axure原型、用户调研、需求文档撰写'
        certificateGap.value = 'NPDP产品经理认证、PMP项目管理、英语六级'
        break
      case 'UI设计师':
        skillGap.value = 'Figma、交互设计、动效设计'
        certificateGap.value = 'Adobe认证设计师、UI设计专项证书、计算机二级'
        break
      case '电商运营':
        skillGap.value = '数据分析、流量运营、直播策划'
        certificateGap.value = '电商运营师、新媒体运营师、计算机二级'
        break
      case '科研人员':
        skillGap.value = '科研方法论、实验设计、论文写作'
        certificateGap.value = '相关专业资格证书、英语六级、计算机二级'
        break
      default:
        skillGap.value = '核心专业技能'
        certificateGap.value = '行业核心证书、计算机二级、英语六级'
    }
  }

  calculateAbilityMatch()
}

const generateReport = () => {
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在重新生成报告...',
    background: 'rgba(255, 255, 255, 0.9)'
  })

  setTimeout(() => {
    initReportData()
    loadingInstance.close()
    console.log('报告重新生成成功！')
  }, 1500)
}

const editReport = () => {
  console.log('进入报告编辑模式')
}

const exportReport = () => {
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在导出PDF报告，请稍候...',
    background: 'rgba(255, 255, 255, 0.9)'
  })

  const reportContent = document.querySelector('.report-content')
  if (!reportContent) {
    loadingInstance.close()
    console.error('导出失败：未找到报告内容')
    return
  }

  const opt = {
    margin: 10,
    filename: `${targetJob.value}_职业生涯发展报告_${reportTime.value.replace(/[:\s]/g, '-')}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  }

  html2pdf().set(opt).from(reportContent).save().then(() => {
    loadingInstance.close()
    console.log('PDF报告导出成功！')
  }).catch((error) => {
    loadingInstance.close()
    console.error('导出失败：', error)
    console.error('PDF报告导出失败，请重试')
  })
}

onMounted(() => {
  if (!localStorage.getItem('token')) {
    console.warn('请先登录')
    router.push('/login')
    return
  }

  const savedStudentInfo = localStorage.getItem('studentInfo')
  if (!savedStudentInfo) {
    console.warn('请先完成个人信息录入！')
    router.push('/student-ability')
    return
  }

  const savedTestAnalysis = localStorage.getItem('careerTestAnalysis')
  if (!savedTestAnalysis) {
    console.warn('请先完成职业兴趣测试！')
    router.push('/interest-test')
    return
  }

  const savedTargetJob = localStorage.getItem('targetJob')
  if (!savedTargetJob) {
    console.warn('请先完成人岗匹配并选择目标岗位！')
    router.push('/job-matching')
    return
  }

  testAnalysis.value = JSON.parse(savedTestAnalysis)
  const studentInfo = JSON.parse(savedStudentInfo)

  if (studentInfo.basic) {
    studentName.value = studentInfo.basic.name || '未知'
    studentGender.value = studentInfo.basic.gender || '未知'
    studentMajor.value = studentInfo.basic.major || '未知'
    studentGrade.value = studentInfo.basic.grade || '未知'
    studentEducation.value = studentInfo.basic.education || '本科'
  }

  if (studentInfo.skill) {
    studentSkills.value = studentInfo.skill.skills || []
    studentCertificates.value = studentInfo.skill.certificates || []
    studentInternship.value = studentInfo.skill.internship || ''
    studentProject.value = studentInfo.skill.project || ''
  }

  if (studentInfo.ability) {
    studentInnovationScore.value = studentInfo.ability.innovation || 80
    studentLearningScore.value = studentInfo.ability.learning || 85
    studentPressureScore.value = studentInfo.ability.pressure || 75
    studentCommunicationScore.value = studentInfo.ability.communication || 80
    studentInternshipScore.value = studentInfo.ability.internship || 70
  }

  const savedResumeInfo = JSON.parse(localStorage.getItem('resumeParsedInfo') || '{}')
  if (savedResumeInfo.skills && !studentSkills.value.length) {
    studentSkills.value = savedResumeInfo.skills
  }

  const savedMatchResult = localStorage.getItem('matchResult')
  
  if (savedMatchResult) {
    matchResult.value = JSON.parse(savedMatchResult)
  }
  
  // 优先使用localStorage中暂存的目标岗位
  targetJob.value = savedTargetJob
  
  // 将职业兴趣替换为目标岗位对应的职业兴趣描述
  careerTestAnalysis.value = jobInterestMapping[targetJob.value] || `${targetJob.value}相关领域`

  initReportData()
  reportVisible.value = true
})
</script>

<style scoped>
.career-planning-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
  box-sizing: border-box;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80vh;
  color: #666;
}
.loading-container p {
  margin-top: 20px;
  font-size: 16px;
}

.report-content {
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.report-header {
  margin-bottom: 30px;
  border-bottom: 1px solid #e6e6e6;
  padding-bottom: 20px;
}
.report-title {
  text-align: center;
  color: #1989fa;
  margin: 0 0 15px 0;
  font-size: 24px;
}
.report-meta {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
  flex-wrap: wrap;
}
.report-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.report-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 6px;
}
.section-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-left: 4px solid #1989fa;
  padding-left: 10px;
}

.match-overview {
  margin-bottom: 20px;
}
.match-overview h3, .gap-analysis h3, .advantage-summary h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
  font-weight: 600;
}
.match-desc {
  color: #666;
  margin-top: 10px;
  line-height: 1.6;
}
.no-gap-text {
  color: #666;
  text-align: center;
  padding: 10px;
  background: #f0f9ff;
  border-radius: 4px;
}
.advantage-summary p {
  color: #666;
  line-height: 1.6;
  background: #fff;
  padding: 15px;
  border-radius: 4px;
}

.gap-makeup-plan {
  margin-bottom: 20px;
}
.makeup-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.makeup-item {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
.makeup-item h4 {
  font-size: 15px;
  color: #e64340;
  margin-bottom: 10px;
  font-weight: 600;
}
.makeup-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.makeup-subitem label {
  font-weight: 600;
  color: #333;
  min-width: 80px;
  display: inline-block;
}
.makeup-subitem p {
  color: #666;
  line-height: 1.6;
  display: inline-block;
  margin: 0;
}

.match-comparison {
  margin-bottom: 20px;
}
.portrait-desc {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.portrait-item {
  flex: 1;
  min-width: 300px;
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
.portrait-item p {
  color: #666;
  line-height: 1.6;
}

.career-goal {
  margin-bottom: 20px;
}
.goal-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #fff;
  padding: 15px;
  border-radius: 4px;
}
.goal-item {
  color: #666;
  line-height: 1.6;
  padding-left: 20px;
  position: relative;
}
.goal-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1989fa;
}
.industry-trend {
  margin-bottom: 20px;
  background: #fff;
  padding: 15px;
  border-radius: 4px;
}
.industry-trend p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 10px;
}
.data-relevance {
  color: #1989fa;
  font-weight: 500;
}
.path-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.path-item {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
.path-item h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
  font-weight: 600;
}
.path-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.path-node {
  background: #f0f9ff;
  padding: 6px 12px;
  border-radius: 4px;
  color: #1989fa;
  font-size: 14px;
}
.path-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.action-plan {
  margin-bottom: 20px;
}
.plan-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.plan-item {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
.plan-item h4 {
  font-size: 15px;
  color: #1989fa;
  margin-bottom: 10px;
  font-weight: 600;
}
.plan-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.plan-subitem label {
  font-weight: 600;
  color: #333;
  min-width: 80px;
  display: inline-block;
}
.plan-subitem p {
  color: #666;
  line-height: 1.6;
  display: inline-block;
  margin: 0;
}

.evaluation {
  margin-bottom: 20px;
}
.evaluation-desc {
  color: #666;
  margin-top: 10px;
  line-height: 1.6;
  font-size: 14px;
}

.achievement {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
.achievement p {
  color: #666;
  line-height: 1.6;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  background: #fff;
  padding: 15px;
  border-radius: 4px;
}
.info-item {
  color: #666;
  font-size: 14px;
}
.info-item label {
  font-weight: 600;
  color: #333;
  margin-right: 5px;
}

.total-score {
  text-align: center;
  font-size: 16px;
  color: #1989fa;
  font-weight: 600;
  margin-top: 10px;
}

.experience-list {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
}
.experience-item {
  color: #666;
  line-height: 1.6;
  margin-bottom: 10px;
}
.experience-item label {
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 5px;
}
</style>
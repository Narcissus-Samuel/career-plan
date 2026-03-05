<template>
  <div class="career-report-container">
    <el-page-header content="生涯规划报告" @back="$router.push('/match-result')"></el-page-header>

    <!-- 报告操作区 -->
    <el-card style="margin: 20px 0;">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-button type="primary" @click="generateReport">重新生成报告</el-button>
        </el-col>
        <el-col :span="8">
          <el-button type="success" @click="editReport">编辑报告内容</el-button>
        </el-col>
        <el-col :span="8">
          <el-button type="warning" @click="exportReport">导出PDF报告</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 报告内容区 -->
    <el-card v-if="reportVisible" title="大学生职业规划报告" style="margin: 20px 0;">
      <div class="report-content" ref="reportContent">
        <!-- 报告封面 -->
        <div class="report-cover">
          <h1>大学生职业规划报告</h1>
          <p>报告生成时间：{{ reportTime }}</p>
          <p>目标岗位：{{ targetJob }}</p>
          <p>姓名：{{ studentName }}</p>
          <p>专业：{{ studentMajor }}</p>
        </div>

        <!-- 一、职业探索与岗位匹配 -->
        <div class="report-section">
          <h2>一、职业探索与岗位匹配分析</h2>
          <h3>1.1 匹配度总览</h3>
          <p>你与「{{ targetJob }}」岗位的综合匹配度为 <span class="score">{{ matchResult.totalScore }}</span> 分。</p>

          <h3>1.2 各维度匹配详情</h3>
          <el-table :data="matchResult.dimensionScores" border size="small" style="margin: 10px 0;">
            <el-table-column prop="dimension" label="匹配维度"></el-table-column>
            <el-table-column prop="score" label="匹配分数"></el-table-column>
            <el-table-column prop="weight" label="权重"></el-table-column>
            <el-table-column prop="contribution" label="加权得分"></el-table-column>
          </el-table>

          <h3>1.3 差距分析</h3>
          <el-collapse>
            <el-collapse-item title="基础要求差距">
              <p>{{ matchResult.gapAnalysis.base }}</p>
            </el-collapse-item>
            <el-collapse-item title="职业技能差距">
              <p>{{ matchResult.gapAnalysis.skills }}</p>
            </el-collapse-item>
            <el-collapse-item title="职业素养差距">
              <p>{{ matchResult.gapAnalysis.quality }}</p>
            </el-collapse-item>
            <el-collapse-item title="发展潜力差距">
              <p>{{ matchResult.gapAnalysis.potential }}</p>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 二、职业目标设定 -->
        <div class="report-section">
          <h2>二、职业目标设定</h2>
          <h3>2.1 短期目标（1-2年）</h3>
          <p>毕业后入职{{ targetJob }}相关岗位，完成从学生到职场人的转变，掌握岗位核心技能，通过试用期考核。</p>
          <h3>2.2 中期目标（3-5年）</h3>
          <p>成为{{ targetJob }}岗位的资深从业者，具备独立负责项目的能力，争取晋升为团队骨干或小组长。</p>
          <h3>2.3 长期目标（5-10年）</h3>
          <p>成为{{ targetJob }}相关领域的专家或管理者，如技术专家、项目经理、部门主管等。</p>
        </div>

        <!-- 三、职业路径规划 -->
        <div class="report-section">
          <h2>三、职业路径规划</h2>
          <h3>3.1 垂直晋升路径</h3>
          <div class="path-list">
            <el-tag v-for="(item, index) in verticalPath" :key="index" size="large">
              {{ item }}
              <el-icon v-if="index < verticalPath.length - 1"><ArrowRight /></el-icon>
            </el-tag>
          </div>

          <h3>3.2 换岗发展路径</h3>
          <div class="path-list">
            <el-tag v-for="(item, index) in switchPath" :key="index" size="large">
              {{ item }}
              <el-icon v-if="index < switchPath.length - 1"><ArrowRight /></el-icon>
            </el-tag>
          </div>
        </div>

        <!-- 四、行动计划与成果展示 -->
        <div class="report-section">
          <h2>四、行动计划与成果展示</h2>
          <h3>4.1 短期计划（在校期间/入职前1年）</h3>
          <ul>
            <li>学习{{ skillGap }}相关技能，完成至少1个实战项目</li>
            <li>参加{{ targetJob }}相关实习，积累职场经验</li>
            <li>考取{{ certificateGap }}相关证书，提升竞争力</li>
            <li>评估周期：每月一次，通过项目完成度、技能掌握度评估</li>
          </ul>

          <h3>4.2 中期计划（入职1-3年）</h3>
          <ul>
            <li>深入学习岗位进阶技能，参与核心项目开发/运营</li>
            <li>建立行业人脉，参加相关技术/行业交流活动</li>
            <li>尝试独立负责小型项目，提升管理能力</li>
            <li>评估周期：每季度一次，通过项目绩效、晋升考核评估</li>
          </ul>
        </div>

        <!-- 五、总结与建议 -->
        <div class="report-section">
          <h2>五、总结与建议</h2>
          <p>综合来看，你与{{ targetJob }}岗位的匹配度较高，具备良好的发展潜力。建议重点弥补{{ skillGap }}技能短板，
          同时保持学习能力和创新能力的提升。职业规划是动态调整的过程，建议每半年重新评估一次匹配度，
          根据自身发展和行业变化调整目标和计划。</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElLoading, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
// 如需导出PDF，需安装：npm install html2pdf.js
import html2pdf from 'html2pdf.js'

const router = useRouter()

// 报告数据
const reportVisible = ref(false)
const reportTime = ref('')
const targetJob = ref('')
const studentName = ref('')
const studentMajor = ref('')
const matchResult = ref({})

// 职业路径（根据目标岗位动态调整）
const verticalPath = ref([])
const switchPath = ref([])

// 差距补充
const skillGap = ref('')
const certificateGap = ref('')

// 页面加载时读取本地存储数据
onMounted(() => {
  // 读取匹配结果和学生信息
  const savedMatchResult = localStorage.getItem('matchResult')
  const savedTargetJob = localStorage.getItem('targetJob')
  const savedStudentInfo = localStorage.getItem('studentInfo')

  if (!savedMatchResult || !savedTargetJob) {
    ElMessage.warning('暂无匹配结果，请先完成人岗匹配')
    router.push('/match-result')
    return
  }

  // 解析数据
  matchResult.value = JSON.parse(savedMatchResult)
  targetJob.value = savedTargetJob
  
  if (savedStudentInfo) {
    const studentInfo = JSON.parse(savedStudentInfo)
    studentName.value = studentInfo.basic.name || '未知'
    studentMajor.value = studentInfo.basic.major || '未知'
  }

  // 初始化报告
  initReportData()
  reportVisible.value = true
})

// 初始化报告数据
const initReportData = () => {
  // 设置报告生成时间
  const now = new Date()
  reportTime.value = `${now.getFullYear()}-${(now.getMonth()+1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

  // 根据目标岗位设置发展路径
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
    }
  }

  // 默认使用数据分析师路径
  const config = pathConfig[targetJob.value] || pathConfig['数据分析师']
  verticalPath.value = config.vertical
  switchPath.value = config.switch

  // 设置差距补充
  skillGap.value = targetJob.value === '数据分析师' ? 'Tableau、SQL' : '核心专业'
  certificateGap.value = targetJob.value === '数据分析师' ? 'CDA、计算机二级' : '行业相关'
}

// 重新生成报告
const generateReport = () => {
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在重新生成报告...',
    background: 'rgba(0, 0, 0, 0.7)'
  })

  setTimeout(() => {
    initReportData()
    loadingInstance.close()
    ElMessage.success('报告重新生成成功！')
  }, 1500)
}

// 编辑报告
const editReport = () => {
  ElMessageBox.prompt('请输入需要修改的报告内容（仅示例，真实场景需富文本编辑）', '编辑报告', {
    inputType: 'textarea',
    inputRows: 10,
    confirmButtonText: '保存',
    cancelButtonText: '取消'
  }).then(({ value }) => {
    if (value) {
      ElMessage.success('报告编辑成功！')
    }
  }).catch(() => {
    ElMessage.info('已取消编辑')
  })
}

// 导出PDF报告
const exportReport = () => {
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在导出PDF报告，请稍候...',
    background: 'rgba(0, 0, 0, 0.7)'
  })

  // 获取报告内容DOM
  const reportContent = document.querySelector('.report-content')
  if (!reportContent) {
    loadingInstance.close()
    ElMessage.error('导出失败：未找到报告内容')
    return
  }

  // 配置导出选项
  const opt = {
    margin: 10,
    filename: `${targetJob.value}_职业规划报告_${reportTime.value.replace(/[:\s]/g, '-')}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  }

  // 执行导出
  html2pdf().set(opt).from(reportContent).save().then(() => {
    loadingInstance.close()
    ElMessage.success('PDF报告导出成功！')
  }).catch((error) => {
    loadingInstance.close()
    console.error('导出失败：', error)
    ElMessage.error('PDF报告导出失败，请重试')
  })
}
</script>

<style scoped>
.career-report-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.report-content {
  padding: 20px;
  font-family: "Microsoft YaHei", sans-serif;
  line-height: 1.8;
}

.report-cover {
  text-align: center;
  padding: 40px 0;
  border-bottom: 2px solid #409EFF;
  margin-bottom: 40px;
}

.report-cover h1 {
  font-size: 32px;
  color: #409EFF;
  margin-bottom: 20px;
}

.report-section {
  margin-bottom: 40px;
}

.report-section h2 {
  color: #303133;
  border-left: 5px solid #409EFF;
  padding-left: 10px;
  margin-bottom: 20px;
}

.report-section h3 {
  color: #666;
  margin: 15px 0;
}

.score {
  color: #409EFF;
  font-weight: bold;
  font-size: 18px;
}

.path-list {
  margin: 10px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

ul {
  padding-left: 20px;
}

li {
  margin: 5px 0;
}
</style>
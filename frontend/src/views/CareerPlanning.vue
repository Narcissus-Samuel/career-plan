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

    <!-- 2. 规划步骤导航 -->
    <section class="step-nav">
      <div class="step-wrap">
        <div class="step-item" :class="{ active: currentStep === 1, finished: currentStep > 1 }">
          <div class="step-num">1</div>
          <div class="step-text">基础信息</div>
        </div>
        <div class="step-line"></div>
        <div class="step-item" :class="{ active: currentStep === 2, finished: currentStep > 2 }">
          <div class="step-num">2</div>
          <div class="step-text">职业兴趣</div>
        </div>
        <div class="step-line"></div>
        <div class="step-item" :class="{ active: currentStep === 3, finished: currentStep > 3 }">
          <div class="step-num">3</div>
          <div class="step-text">能力评估</div>
        </div>
        <div class="step-line"></div>
        <div class="step-item" :class="{ active: currentStep === 4, finished: currentStep > 4 }">
          <div class="step-num">4</div>
          <div class="step-text">规划生成</div>
        </div>
      </div>
    </section>

    <!-- 3. 规划表单区域（分步显示） -->
    <section class="form-section">
      <div class="form-wrap">
        <!-- 步骤1：基础信息 -->
        <div class="form-step" v-show="currentStep === 1">
          <div class="form-title">填写你的基础信息</div>
          <div class="form-content">
            <div class="form-row">
              <label class="form-label">姓名：</label>
              <input type="text" class="form-input" v-model="planInfo.name" placeholder="请输入你的姓名">
            </div>
            <div class="form-row">
              <label class="form-label">性别：</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input type="radio" v-model="planInfo.gender" value="男"> 男
                </label>
                <label class="radio-item">
                  <input type="radio" v-model="planInfo.gender" value="女"> 女
                </label>
              </div>
            </div>
            <div class="form-row">
              <label class="form-label">年级：</label>
              <select class="form-select" v-model="planInfo.grade">
                <option value="">请选择年级</option>
                <option value="大一">大一</option>
                <option value="大二">大二</option>
                <option value="大三">大三</option>
                <option value="大四">大四</option>
              </select>
            </div>
            <div class="form-row">
              <label class="form-label">专业：</label>
              <input type="text" class="form-input" v-model="planInfo.major" placeholder="请输入你的专业">
            </div>
            <div class="form-row">
              <label class="form-label">目标方向：</label>
              <select class="form-select" v-model="planInfo.target">
                <option value="">请选择职业目标</option>
                <option value="就业">就业</option>
                <option value="考研">考研</option>
                <option value="留学">留学</option>
                <option value="考公">考公</option>
                <option value="创业">创业</option>
              </select>
            </div>
          </div>
          <div class="form-btn-group">
            <button class="next-btn" @click="nextStep">下一步 →</button>
          </div>
        </div>

        <!-- 步骤2：职业兴趣 -->
        <div class="form-step" v-show="currentStep === 2">
          <div class="form-title">选择你的职业兴趣（可多选）</div>
          <div class="form-content">
            <div class="checkbox-group">
              <label class="checkbox-item" v-for="item in interestList" :key="item.id">
                <input type="checkbox" v-model="planInfo.interest" :value="item.id"> {{ item.name }}
              </label>
            </div>
            <div class="form-row">
              <label class="form-label">兴趣描述：</label>
              <textarea class="form-textarea" v-model="planInfo.interestDesc" placeholder="请补充你的兴趣相关描述（选填）"></textarea>
            </div>
          </div>
          <div class="form-btn-group">
            <button class="prev-btn" @click="prevStep">← 上一步</button>
            <button class="next-btn" @click="nextStep">下一步 →</button>
          </div>
        </div>

        <!-- 步骤3：能力评估 -->
        <div class="form-step" v-show="currentStep === 3">
          <div class="form-title">评估你的核心能力</div>
          <div class="form-content">
            <div class="form-row" v-for="item in abilityList" :key="item.id">
              <label class="form-label">{{ item.name }}：</label>
              <div class="rate-group">
                <span class="rate-item" v-for="star in 5" :key="star" 
                  :class="{ active: star <= planInfo.ability[item.code] }"
                  @click="setAbility(item.code, star)"
                >★</span>
                <span class="rate-text">{{ planInfo.ability[item.code] }}星</span>
              </div>
            </div>
            <div class="form-row">
              <label class="form-label">能力短板：</label>
              <textarea class="form-textarea" v-model="planInfo.abilityDesc" placeholder="请描述你的能力短板及提升计划"></textarea>
            </div>
          </div>
          <div class="form-btn-group">
            <button class="prev-btn" @click="prevStep">← 上一步</button>
            <button class="next-btn" @click="nextStep">下一步 →</button>
          </div>
        </div>

        <!-- 步骤4：规划生成 -->
        <div class="form-step" v-show="currentStep === 4">
          <div class="form-title">你的专属职业规划</div>
          <div class="plan-result">
            <div class="result-header">
              <h3>{{ planInfo.name }}的{{ planInfo.grade }}/{{ planInfo.major }}职业规划</h3>
              <div class="result-date">生成时间：{{ currentDate }}</div>
            </div>
            <div class="result-content">
              <div class="result-item">
                <div class="result-label">目标方向：</div>
                <div class="result-value">{{ planInfo.target || '未选择' }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">职业兴趣：</div>
                <div class="result-value">{{ selectedInterestNames.join('、') || '未选择' }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">核心能力评估：</div>
                <div class="result-value">
                  <div v-for="item in abilityList" :key="item.id">
                    {{ item.name }}：{{ planInfo.ability[item.code] }}星
                  </div>
                </div>
              </div>
              <div class="result-item">
                <div class="result-label">能力提升计划：</div>
                <div class="result-value">{{ planInfo.abilityDesc || '未填写' }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">阶段性规划：</div>
                <div class="result-value">
                  <ul class="stage-list">
                    <li v-if="planInfo.grade === '大一'">
                      <strong>大一阶段：</strong> 夯实专业基础，参加1-2个相关社团，了解行业基本情况
                    </li>
                    <li v-if="planInfo.grade === '大二'">
                      <strong>大二阶段：</strong> 考取核心证书，参与相关实习/项目，明确细分方向
                    </li>
                    <li v-if="planInfo.grade === '大三'">
                      <strong>大三阶段：</strong> 针对性提升目标方向能力，准备实习/备考/申请材料
                    </li>
                    <li v-if="planInfo.grade === '大四'">
                      <strong>大四阶段：</strong> 冲刺目标，完成求职/考研/留学/考公相关流程
                    </li>
                    <li v-else>请选择年级后查看个性化阶段性规划</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div class="form-btn-group">
            <button class="prev-btn" @click="prevStep">← 上一步</button>
            <button class="finish-btn" @click="finishPlan">完成规划</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. 推荐资源区域 -->
    <section class="resource-section" v-show="currentStep === 4">
      <div class="resource-wrap">
        <div class="resource-title">为你推荐的规划资源</div>
        <div class="resource-list">
          <div class="resource-card" v-for="(item, i) in resourceList" :key="i" @click="$router.push(`/detail/${item.id}`)">
            <div class="resource-icon">{{ item.icon }}</div>
            <div class="resource-name">{{ item.title }}</div>
            <div class="resource-desc">{{ item.description }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 5. 页脚 -->
    <footer class="page-footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 你的职业未来，我们一起规划
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
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

// 规划步骤
const currentStep = ref(1)

// 规划信息
const planInfo = ref({
  name: '',
  gender: '',
  grade: '',
  major: '',
  target: '',
  interest: [],          // 存储兴趣ID数组
  interestDesc: '',
  ability: {
    communication: 0,
    learning: 0,
    teamwork: 0,
    professional: 0,
    innovation: 0
  },
  abilityDesc: ''
})

// 兴趣列表（从后端获取）
const interestList = ref([])

// 能力列表（从后端获取）
const abilityList = ref([])

// 推荐资源列表（从后端获取）
const resourceList = ref([])

// 当前日期
const currentDate = computed(() => {
  const date = new Date()
  return `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
})

// 计算选中的兴趣名称（用于显示）
const selectedInterestNames = computed(() => {
  if (!planInfo.value.interest.length) return []
  return interestList.value
    .filter(item => planInfo.value.interest.includes(item.id))
    .map(item => item.name)
})

// 获取请求头（包含 token）
const getHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  }
}

// 加载所有初始数据
const loadData = async () => {
  try {
    const [
      interestsRes,
      dimensionsRes,
      baseRes,
      userInterestsRes,
      abilityRes,
      resourcesRes
    ] = await Promise.all([
      fetch('/api/profile/interests'),
      fetch('/api/profile/ability-dimensions'),
      fetch('/api/profile/base', { headers: getHeaders() }),
      fetch('/api/profile/user-interests', { headers: getHeaders() }),
      fetch('/api/profile/ability', { headers: getHeaders() }),
      fetch('/api/path/learning-resources')
    ])

    if (interestsRes.ok) {
      interestList.value = await interestsRes.json()
    }

    if (dimensionsRes.ok) {
      const dimensions = await dimensionsRes.json()
      abilityList.value = dimensions.map(d => ({
        id: d.id,
        name: d.name,
        code: d.code
      }))
    }

    if (baseRes.ok) {
      const data = await baseRes.json()
      if (data && Object.keys(data).length) {
        planInfo.value.name = data.name || ''
        planInfo.value.gender = data.gender || ''
        planInfo.value.grade = data.grade || ''
        planInfo.value.major = data.major || ''
        planInfo.value.target = data.target || ''
      }
    }

    if (userInterestsRes.ok) {
      const data = await userInterestsRes.json()
      if (data && data.length) {
        planInfo.value.interest = data.map(item => item.id)
        planInfo.value.interestDesc = data[0]?.description || ''
      }
    }

    if (abilityRes.ok) {
      const data = await abilityRes.json()
      if (data && data.length) {
        const abilityMap = {}
        data.forEach(item => {
          abilityMap[item.code] = item.score
        })
        planInfo.value.ability = { ...planInfo.value.ability, ...abilityMap }
        planInfo.value.abilityDesc = data[0]?.description || ''
      }
    }

    if (resourcesRes.ok) {
      resourceList.value = await resourcesRes.json()
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    alert('加载数据失败，请刷新重试')
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// 下一步
const nextStep = async () => {
  if (currentStep.value === 1) {
    if (!planInfo.value.name || !planInfo.value.grade || !planInfo.value.major) {
      alert('请填写姓名、年级、专业等必填信息！')
      return
    }
    await saveBaseInfo(false)
  }
  if (currentStep.value === 2) {
    if (planInfo.value.interest.length === 0) {
      alert('请至少选择一个职业兴趣！')
      return
    }
    await saveInterests(false)
  }
  if (currentStep.value === 3) {
    const hasAbility = Object.values(planInfo.value.ability).some(v => v > 0)
    if (!hasAbility) {
      alert('请至少评估一项核心能力！')
      return
    }
    await saveAbility(false)
  }
  
  if (currentStep.value < 4) {
    currentStep.value++
  }

  // 默认使用数据分析师路径
  const config = pathConfig[targetJob.value] || pathConfig['数据分析师']
  verticalPath.value = config.vertical
  switchPath.value = config.switch

  // 设置差距补充
  skillGap.value = targetJob.value === '数据分析师' ? 'Tableau、SQL' : '核心专业'
  certificateGap.value = targetJob.value === '数据分析师' ? 'CDA、计算机二级' : '行业相关'
}

// 设置能力评分
const setAbility = (code, star) => {
  planInfo.value.ability[code] = star
}

// 保存基础信息
const saveBaseInfo = async (showAlert = true) => {
  try {
    const res = await fetch('/api/profile/base', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        name: planInfo.value.name,
        gender: planInfo.value.gender,
        grade: planInfo.value.grade,
        major: planInfo.value.major,
        target: planInfo.value.target
      })
    })
    if (!res.ok) throw new Error('保存基础信息失败')
    if (showAlert) alert('基础信息保存成功')
  } catch (error) {
    alert(error.message)
  }
}

// 保存兴趣
const saveInterests = async (showAlert = true) => {
  try {
    const interests = planInfo.value.interest.map(id => ({ id }))
    const res = await fetch('/api/profile/user-interests', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        interests,
        interestDesc: planInfo.value.interestDesc
      })
    })
    if (!res.ok) throw new Error('保存兴趣失败')
    if (showAlert) alert('兴趣保存成功')
  } catch (error) {
    alert(error.message)
  }
}

// 保存能力评估
const saveAbility = async (showAlert = true) => {
  try {
    const abilities = abilityList.value.map(item => ({
      code: item.code,
      score: planInfo.value.ability[item.code] || 0
    }))
    const res = await fetch('/api/profile/ability', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        abilities,
        abilityDesc: planInfo.value.abilityDesc
      })
    })
    if (!res.ok) throw new Error('保存能力评估失败')
    if (showAlert) alert('能力评估保存成功')
  } catch (error) {
    alert(error.message)
  }
}

// 保存规划（调用三个保存接口）
const savePlan = async () => {
  await saveBaseInfo(true)
  await saveInterests(true)
  await saveAbility(true)
}

// 导出报告 - 生成报告并跳转到报告页面
const exportPlan = async () => {
  await finishPlan() // 复用完成规划逻辑
}

// 完成规划 - 生成报告并跳转
const finishPlan = async () => {
  await savePlan()

  try {
    const res = await fetch('/api/report/generate', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        title: `${planInfo.value.name}的职业规划报告`,
        type: 1, // 综合职业规划报告
        format: 'html',
        modules: [] // 可根据需要传递选中的模块
      })
    })
    if (!res.ok) throw new Error('生成报告失败')
    const data = await res.json()
    const reportId = data.id
    router.push(`/report?id=${reportId}`)
  } catch (error) {
    alert('生成报告失败：' + error.message)
  }
}

// 页面加载时读取本地存储数据
onMounted(() => {
  // 验证登录状态
  if (!localStorage.getItem('token')) {
    alert('请先登录')
    router.push('/login')
    return
  }

  // 加载分步规划的初始数据
  loadData()

  // 读取匹配结果和学生信息
  const savedMatchResult = localStorage.getItem('matchResult')
  const savedTargetJob = localStorage.getItem('targetJob')
  const savedStudentInfo = localStorage.getItem('studentInfo')

  if (savedMatchResult && savedTargetJob) {
    // 解析匹配数据
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
  }
})

// 职业路径配置
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

// 初始化报告数据
const initReportData = () => {
  // 设置报告生成时间
  const now = new Date()
  reportTime.value = `${now.getFullYear()}-${(now.getMonth()+1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

  // 根据目标岗位设置发展路径
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

/* 规划步骤导航样式 */
.step-nav {
  padding: 30px 0;
  max-width: 800px;
  margin: 0 auto;
}
.step-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 80px;
}
.step-num {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e6e6e6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
}
.step-text {
  font-size: 14px;
  color: #999;
}
.step-line {
  flex: 1;
  height: 2px;
  background: #e6e6e6;
  margin: 0 10px;
}
.step-item.active .step-num {
  background: #409eff;
}
.step-item.active .step-text {
  color: #409eff;
  font-weight: bold;
}
.step-item.finished .step-num {
  background: #67c23a;
}
.step-item.finished .step-text {
  color: #67c23a;
}

/* 表单区域样式 */
.form-section {
  max-width: 800px;
  margin: 0 auto 40px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.form-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}
.form-row {
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
}
.form-label {
  width: 100px;
  text-align: right;
  padding-right: 16px;
  color: #666;
  line-height: 32px;
}
.form-input, .form-select {
  flex: 1;
  height: 32px;
  padding: 0 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
.form-textarea {
  flex: 1;
  min-height: 80px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
}
.radio-group, .checkbox-group {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.radio-item, .checkbox-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.rate-group {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}
.rate-item {
  font-size: 20px;
  color: #ccc;
  cursor: pointer;
}
.rate-item.active {
  color: #f5a623;
}
.rate-text {
  margin-left: 10px;
  color: #666;
}
.form-btn-group {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}
.prev-btn, .next-btn, .finish-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.prev-btn {
  background: #f5f7fa;
  color: #666;
}
.next-btn {
  background: #409eff;
  color: #fff;
}
.finish-btn {
  background: #67c23a;
  color: #fff;
}

/* 规划结果样式 */
.plan-result {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}
.result-header {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}
.result-date {
  color: #999;
  font-size: 14px;
  margin-top: 8px;
}
.result-item {
  margin-bottom: 16px;
}
.result-label {
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}
.result-value {
  color: #666;
  line-height: 1.6;
}
.stage-list {
  padding-left: 20px;
}

/* 推荐资源样式 */
.resource-section {
  max-width: 800px;
  margin: 0 auto 40px;
}
.resource-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}
.resource-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}
.resource-card {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s;
}
.resource-card:hover {
  transform: translateY(-5px);
}
.resource-icon {
  font-size: 24px;
  color: #409eff;
  margin-bottom: 8px;
}
.resource-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}
.resource-desc {
  font-size: 12px;
  color: #999;
  line-height: 1.4;
}

/* 页脚样式 */
.page-footer {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
  border-top: 1px solid #eee;
  margin-top: 40px;
}

/* AI 生成 loading 提示 */
.loading-tip {
  text-align: center;
  padding: 30px;
  color: #2f54eb;
  font-size: 16px;
}

/* AI 生成结果样式 */
.ai-result {
  line-height: 1.8;
  color: #333;
}
.ai-result h3 {
  color: #2f54eb;
  margin: 15px 0 10px;
}
.ai-result ul {
  padding-left: 20px;
}
.ai-result li {
  margin: 8px 0;
}
</style>
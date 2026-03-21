<template>
  <div class="student-ability-page">
    <!-- 顶部导航栏（保持不变） -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item active" @click="$router.push('/student-ability')">职业规划</li>
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
                  <span class="color-dot blue"></span> 规划报告导出
                </li>
              </ul>
            </li>
          </ul>
        </div>
        <div class="nav-right">
          <div class="nav-search-wrap">
            <input type="text" class="nav-search-input" placeholder="搜索..." @keyup.enter="handleSearch" />
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

    <!-- 主体内容区域 - 改为左侧步骤导航 + 右侧内容 -->
    <div class="main-container">
      <!-- 左侧瀑布式步骤导航 -->
      <aside class="sidebar-step-indicator">
        <div class="sidebar-step-container">
          <div class="step-sidebar-header">
            <h3>职业规划流程</h3>
            <p>完成以下步骤，生成专属职业规划报告</p>
          </div>
          
          <div class="step-list">
            <div 
              v-for="(step, index) in steps" 
              :key="index" 
              class="sidebar-step-item"
              :class="{ 
                active: index === activeStep, 
                completed: index < activeStep 
              }"
              @click="jumpToStep(index)"
            >
              <!-- 步骤连接线 -->
              <div class="step-connector" :class="{
                completed: index < activeStep,
                active: index === activeStep && index < steps.length - 1,
                inactive: index > activeStep
              }"></div>
              
              <!-- 步骤内容 -->
              <div class="step-content-wrapper">
                <!-- 步骤图标 -->
                <div class="step-icon">
                  <span v-if="index < activeStep" class="completed-icon">✓</span>
                  <span v-else-if="index === activeStep" class="active-icon">{{ index + 1 }}</span>
                  <span v-else class="inactive-icon">{{ index + 1 }}</span>
                </div>
                
                <!-- 步骤文本 -->
                <div class="step-text">
                  <div class="step-name">{{ step }}</div>
                  <div class="step-status" v-if="index === activeStep">当前步骤</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧主体内容 -->
      <main class="main-content">
        <div class="content-container">
          <!-- 第一步：个人信息与简历信息 -->
          <div v-if="activeStep === 0" class="step-content glass-panel">
            <h2 class="section-title">
              <span class="step-badge">1</span>
              📋 个人信息与简历
            </h2>
            <div class="personal-info">
              <el-input v-model="personalInfo.name" placeholder="姓名" size="large" class="info-input" clearable />
              <el-input v-model="personalInfo.phone" placeholder="手机号" size="large" class="info-input" clearable />
              <el-input v-model="personalInfo.email" placeholder="邮箱" size="large" class="info-input" clearable />
            </div>

            <h2 class="section-title" style="margin-top: 32px;">📄 简历信息</h2>
            <div v-if="studentId" class="resume-score">
              <span class="score-label">简历完整度</span>
              <span class="score-value">{{ resumeScore }}%</span>
              <div class="score-bar"><div class="bar-fill" :style="{ width: resumeScore + '%' }"></div></div>
            </div>

            <div class="input-mode-switch">
              <button class="mode-btn" :class="{ active: inputMode === 'upload' }" @click="inputMode = 'upload'">
                📤 上传简历
              </button>
              <button class="mode-btn" :class="{ active: inputMode === 'manual' }" @click="inputMode = 'manual'">
                ✏️ 手动填写
              </button>
            </div>

            <!-- 上传模式 -->
            <div v-if="inputMode === 'upload'" class="upload-section">
              <div class="upload-area" @click="triggerFileUpload" @dragover.prevent @drop.prevent="handleFileDrop">
                <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" style="display: none" @change="handleFileSelect" />
                <div class="upload-icon">📂</div>
                <div class="upload-text">拖拽文件到此处或点击上传</div>
                <div class="upload-tip">支持 PDF、Word 格式，最大 10MB</div>
              </div>
              <div v-if="uploadedFile" class="file-info">
                <span class="file-name">{{ uploadedFile.name }}</span>
                <span class="file-size">{{ (uploadedFile.size / 1024).toFixed(1) }} KB</span>
                <el-button type="text" @click="removeFile">移除</el-button>
              </div>
              <div class="step-actions" style="margin-top: 20px;">
                <el-button type="primary" size="large" @click="submitUpload" :loading="uploading">开始解析</el-button>
              </div>
            </div>

            <!-- 手动填写模式 -->
            <div v-if="inputMode === 'manual'" class="manual-section">
              <div class="form-tip"><i>💡</i> 请根据实际情况填写，每个区域都提供了示例文本。</div>
              <div class="resume-block">
                <h3 class="block-title">📚 教育经历</h3>
                <textarea v-model="resumeText.education" class="block-textarea" rows="3" placeholder="例如：清华大学 计算机科学与技术 本科 2020-2024 GPA:3.8/4.0"></textarea>
                <div class="block-hint">示例：清华大学 计算机科学与技术 本科 2020-2024 GPA:3.8/4.0 主修课程：数据结构、算法、数据库</div>
              </div>
              <div class="resume-block">
                <h3 class="block-title">💼 工作经历</h3>
                <textarea v-model="resumeText.work" class="block-textarea" rows="3" placeholder="例如：腾讯科技 后端开发实习生 2023.07-2023.09"></textarea>
                <div class="block-hint">示例：腾讯科技 后端开发实习生 2023.07-2023.09 负责用户中心微服务开发，使用Spring Boot，日均接口调用量提升30%</div>
              </div>
              <div class="resume-block">
                <h3 class="block-title">🚀 项目经历</h3>
                <textarea v-model="resumeText.project" class="block-textarea" rows="3" placeholder="例如：校园二手交易平台 2024.03-2024.06"></textarea>
                <div class="block-hint">示例：校园二手交易平台 2024.03-2024.06 担任后端开发，使用Spring Boot+Vue，实现商品发布、订单管理，用户数500+</div>
              </div>
              <div class="resume-block">
                <h3 class="block-title">🔧 技能与证书</h3>
                <textarea v-model="resumeText.skillsCerts" class="block-textarea" rows="2" placeholder="例如：Python、Java、SQL；英语六级、计算机二级"></textarea>
                <div class="block-hint">示例：Python、Java、SQL；英语六级、计算机二级</div>
              </div>
              <div class="resume-block">
                <h3 class="block-title">📝 自我总结</h3>
                <textarea v-model="resumeText.summary" class="block-textarea" rows="3" placeholder="例如：3年后端开发经验，熟悉Java技术栈..."></textarea>
                <div class="block-hint">示例：3年后端开发经验，熟悉Java技术栈，有高并发项目经历，善于团队协作，致力于成为全栈工程师</div>
              </div>
            </div>

            <div class="step-actions" v-if="inputMode === 'manual'">
              <el-button type="primary" size="large" @click="submitManualAndRedirect" :loading="submitting">保存并下一步</el-button>
            </div>
          </div>

          <!-- 第二步：兴趣探索（真实测评） -->
          <div v-if="activeStep === 1" class="step-content glass-panel">
            <h2 class="section-title">
              <span class="step-badge">2</span>
              🎯 兴趣探索
            </h2>
            <div class="interest-box">
              <p>通过兴趣测试，你可以发现更适合自己的职业方向。你也可以选择跳过，直接基于能力进行匹配。</p>
              <el-checkbox v-model="skipInterest">跳过兴趣探索</el-checkbox>
              <div v-if="!skipInterest" class="interest-test">
                <div v-if="loadingQuestions" class="loading">加载题目中...</div>
                <div v-else>
                  <div v-for="(question, idx) in questions" :key="question.id" class="question-item">
                    <p>{{ idx + 1 }}. {{ question.question }}</p>
                    <el-slider
                      v-model="answers[question.id]"
                      :min="1"
                      :max="5"
                      :step="1"
                      show-stops
                      :marks="marks"
                    />
                  </div>
                  <el-button type="primary" @click="submitInterestTest" :loading="submittingTest">提交测评</el-button>
                </div>
              </div>
            </div>
            <div class="step-actions">
              <el-button size="large" @click="prevStep">上一步</el-button>
              <el-button type="primary" size="large" @click="nextStep">下一步</el-button>
            </div>
          </div>

          <!-- 第三步：AI能力画像生成 -->
          <div v-if="activeStep === 2" class="step-content glass-panel">
            <h2 class="section-title">
              <span class="step-badge">3</span>
              🤖 AI能力画像
            </h2>
            <div v-if="!profileGenerated" class="generate-area">
              <p>点击下方按钮，获取AI生成的能力画像。</p>
              <el-button type="primary" size="large" @click="fetchProfile" :loading="fetchingProfile">获取能力画像</el-button>
            </div>
            <div v-else class="profile-result">
              <div class="result-card">
                <div class="score-overview">
                  <div class="score-item">
                    <span class="score-label">完整度</span>
                    <span class="score-value">{{ profile.completeness }}%</span>
                    <div class="score-bar"><div class="bar-fill" :style="{ width: profile.completeness + '%' }"></div></div>
                  </div>
                  <div class="score-item">
                    <span class="score-label">竞争力</span>
                    <span class="score-value">{{ profile.competitiveness }}%</span>
                    <div class="score-bar"><div class="bar-fill" :style="{ width: profile.competitiveness + '%' }"></div></div>
                  </div>
                </div>
                <div class="dimension-scores">
                  <h3>各维度能力评分</h3>
                  <div class="dimension-grid">
                    <div v-for="(score, name) in profile.dimensions" :key="name" class="dimension-item">
                      <div class="dimension-name">{{ name }}</div>
                      <div class="dimension-bar"><div class="bar-fill" :style="{ width: score + '%' }"></div></div>
                      <div class="dimension-score">{{ score }}</div>
                    </div>
                  </div>
                </div>
                <div class="skill-cert">
                  <div class="skill-section"><h4>专业技能</h4><div class="tags"><span v-for="s in profile.skills" :key="s" class="tag skill-tag">{{ s }}</span></div></div>
                  <div class="cert-section"><h4>证书</h4><div class="tags"><span v-for="c in profile.certificates" :key="c" class="tag cert-tag">{{ c }}</span></div></div>
                </div>
              </div>
            </div>
            <div class="step-actions">
              <el-button size="large" @click="prevStep">上一步</el-button>
              <el-button type="primary" size="large" @click="nextStep" :disabled="!profileGenerated">下一步</el-button>
            </div>
          </div>

          <!-- 第四步：人岗匹配 -->
          <div v-if="activeStep === 3" class="step-content glass-panel">
            <h2 class="section-title">
              <span class="step-badge">4</span>
              🎯 人岗匹配
            </h2>
            <div v-if="!matchStarted" class="match-start">
              <p>点击“立即匹配”，AI将分析你的能力与岗位的契合度，并推荐最适合的岗位。</p>
              <el-button type="primary" size="large" @click="fetchMatchList" :loading="matching">立即匹配</el-button>
            </div>
            <div v-else class="match-result">
              <el-table :data="matchList" style="width: 100%" stripe>
                <el-table-column prop="job_name" label="岗位名称" width="180" />
                <el-table-column prop="overall_score" label="匹配度" width="100">
                  <template #default="{ row }">{{ row.overall_score }}%</template>
                </el-table-column>
                <el-table-column label="专业技能契合度" width="140">
                  <template #default="{ row }">{{ row.skill_fit }}%</template>
                </el-table-column>
                <el-table-column label="通用素质差距" width="140">
                  <template #default="{ row }">{{ row.soft_gap }}%</template>
                </el-table-column>
              </el-table>
              <p class="match-note">系统将基于匹配度最高的岗位生成职业发展报告。</p>
            </div>
            <div class="step-actions">
              <el-button size="large" @click="prevStep">上一步</el-button>
              <el-button type="primary" size="large" @click="nextStep" :disabled="!matchStarted">下一步</el-button>
            </div>
          </div>

          <!-- 第五步：职业发展报告 -->
          <div v-if="activeStep === 4" class="step-content glass-panel">
            <h2 class="section-title">
              <span class="step-badge">5</span>
              📄 职业发展报告
            </h2>
            <div class="report-area">
              <el-input
                v-model="reportContent"
                type="textarea"
                :rows="15"
                placeholder="报告内容..."
                resize="vertical"
                class="report-editor"
              />
              <div class="report-actions">
                <el-button @click="polishReport" :loading="polishing">智能润色</el-button>
                <el-button type="primary" @click="exportReport" :loading="exporting">导出PDF</el-button>
                <el-button @click="resetReport">重置</el-button>
              </div>
              <div class="edit-tip">💡 你可以直接在上方编辑修改报告内容，点击润色可优化表达。</div>
            </div>
            <div class="step-actions">
              <el-button size="large" @click="prevStep">上一步</el-button>
              <el-button type="success" size="large" @click="finish">完成</el-button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')
const token = localStorage.getItem('token')
const userId = 3   // 临时写死，测试用

// Axios 实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  headers: { Authorization: token ? `Bearer ${token}` : '' }
})

// 步骤定义
const steps = ['填写信息', '兴趣探索', '能力画像', '人岗匹配', '生成报告']
const activeStep = ref(0)

// 第一步数据
const personalInfo = reactive({ name: '', phone: '', email: '' })
const inputMode = ref('manual')
const uploadedFile = ref(null)
const fileInput = ref(null)
const resumeText = reactive({
  education: '',
  work: '',
  project: '',
  skillsCerts: '',
  summary: ''
})
const studentId = ref(null)
const resumeScore = computed(() => profile?.completeness || 0)
const uploading = ref(false)
const submitting = ref(false)

// 第二步数据
const skipInterest = ref(false)
const questions = ref([])
const answers = ref({})
const loadingQuestions = ref(false)
const submittingTest = ref(false)
const marks = { 1: '1', 2: '2', 3: '3', 4: '4', 5: '5' }

// 第三步数据
const fetchingProfile = ref(false)
const profileGenerated = ref(false)
const profile = reactive({
  completeness: 0,
  competitiveness: 0,
  dimensions: {},
  skills: [],
  certificates: []
})

// 第四步数据
const matching = ref(false)
const matchStarted = ref(false)
const matchList = ref([])

// 第五步数据
const reportContent = ref('')
const polishing = ref(false)
const exporting = ref(false)
const reportId = ref(null)

// ========== 导航栏方法 ==========
const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const handleLogout = () => {
  localStorage.clear()
  isLogin.value = false
  router.push('/')
}

const toggleTheme = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
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
    router.push(`/search?keyword=${encodeURIComponent(input.value.trim())}`)
  }
}

// ========== 新增：跳转到指定步骤 ==========
const jumpToStep = (index) => {
  // 限制只能跳转到已完成或当前步骤，不能跳转到未完成的后续步骤
  if (index <= activeStep.value) {
    activeStep.value = index
  } else {
    ElMessage.warning('请先完成前面的步骤')
  }
}

// ========== 文件上传方法 ==========
const triggerFileUpload = () => { fileInput.value.click() }

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) validateAndSetFile(file)
}

const handleFileDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file) validateAndSetFile(file)
}

const validateAndSetFile = (file) => {
  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('仅支持 PDF 或 Word 文档')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return
  }
  uploadedFile.value = file
}

const removeFile = () => { uploadedFile.value = null }

// ========== 新增：保存并跳转到测评页面的方法 ==========
const submitManualAndRedirect = async () => {
  await submitManual()
  if (studentId.value) {
    router.push({ 
      path: '/ability-analysis', 
      name: 'AbilityAnalysis',
      query: { studentId: studentId.value } 
    })
  }
}

// ========== 手动提交（原有方法保留） ==========
const submitManual = async () => {
  if (!personalInfo.name || !personalInfo.phone || !personalInfo.email) {
    ElMessage.warning('请填写完整的个人信息')
    return
  }
  if (!userId) {
    ElMessage.warning('请先登录')
    return
  }
  submitting.value = true
  try {
    const payload = {
      user_id: parseInt(userId),
      name: personalInfo.name,
      phone: personalInfo.phone,
      email: personalInfo.email,
      education: resumeText.education,
      work: resumeText.work,
      project: resumeText.project,
      skills_certs: resumeText.skillsCerts,
      summary: resumeText.summary
    }
    const res = await api.post('/profile/submit', payload)
    studentId.value = res.data.student_id
    profile.completeness = res.data.completeness
    profile.skills = res.data.skills
    profile.certificates = res.data.certificates
    const soft = res.data.soft_abilities
    profile.dimensions = Object.fromEntries(Object.entries(soft).map(([k, v]) => [k, v.score]))
    profileGenerated.value = true
    ElMessage.success('信息提交成功')
  } catch (err) {
    ElMessage.error('提交失败：' + (err.response?.data?.error || err.message))
  } finally {
    submitting.value = false
  }
}

// ========== 上传文件并解析 ==========
const submitUpload = async () => {
  if (!uploadedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  if (!userId) {
    ElMessage.warning('请先登录')
    return
  }
  uploading.value = true
  const formData = new FormData()
  formData.append('file', uploadedFile.value)
  formData.append('user_id', parseInt(userId))
  try {
    const res = await api.post('/profile/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    studentId.value = res.data.student_id
    profile.skills = res.data.skills
    profile.certificates = res.data.certificates
    const soft = res.data.soft_abilities
    profile.dimensions = Object.fromEntries(Object.entries(soft).map(([k, v]) => [k, v.score]))
    profile.completeness = 80
    profileGenerated.value = true
    router.push({ 
      path: '/interest-test', 
      name: 'CareerInterestTest',
      query: { studentId: studentId.value } 
    })
    ElMessage.success('文件解析成功，即将跳转到兴趣测评')
  } catch (err) {
    ElMessage.error('上传失败：' + (err.response?.data?.error || err.message))
  } finally {
    uploading.value = false
  }
}

// ========== 获取能力画像 ==========
const fetchProfile = async () => {
  if (!studentId.value) {
    ElMessage.warning('尚无学生信息，请先完成第一步')
    return
  }
  fetchingProfile.value = true
  try {
    const res = await api.get(`/profile/${studentId.value}`)
    const data = res.data
    profile.skills = data.skills || []
    profile.certificates = data.certificates || []
    const soft = data.soft_abilities || {}
    profile.dimensions = Object.fromEntries(Object.entries(soft).map(([k, v]) => [k, v.score]))
    profile.completeness = data.completeness || 0
    profile.competitiveness = data.completeness || 70
    profileGenerated.value = true
  } catch (err) {
    ElMessage.error('获取画像失败：' + err.message)
  } finally {
    fetchingProfile.value = false
  }
}

// ========== 获取测评题目 ==========
const fetchQuestions = async () => {
  loadingQuestions.value = true
  try {
    const res = await api.get('/assessment/questions')
    questions.value = res.data
    answers.value = {}
    questions.value.forEach(q => { answers.value[q.id] = 3 })
  } catch (err) {
    ElMessage.error('获取题目失败：' + err.message)
  } finally {
    loadingQuestions.value = false
  }
}

// ========== 提交兴趣测试 ==========
const submitInterestTest = async () => {
  if (!userId) {
    ElMessage.warning('请先登录')
    return
  }
  const answerList = Object.entries(answers.value).map(([question_id, score]) => ({
    question_id: parseInt(question_id),
    score
  }))
  submittingTest.value = true
  try {
    await api.post('/assessment/submit', {
      user_id: parseInt(userId),
      answers: answerList,
      test_mode: false
    })
    ElMessage.success('兴趣测试提交成功')
  } catch (err) {
    ElMessage.error('提交失败：' + (err.response?.data?.error || err.message))
  } finally {
    submittingTest.value = false
  }
}

// ========== 人岗匹配 ==========
const fetchMatchList = async () => {
  if (!studentId.value) {
    ElMessage.warning('尚无学生信息')
    return
  }
  matching.value = true
  try {
    const res = await api.get(`/match/recommend?student_id=${studentId.value}&limit=10`)
    matchList.value = res.data
    matchStarted.value = true
    if (matchList.value.length > 0) {
      generateReport(matchList.value[0])
    }
  } catch (err) {
    ElMessage.error('匹配失败：' + err.message)
  } finally {
    matching.value = false
  }
}

// ========== 生成报告 ==========
const generateReport = async (job) => {
  try {
    const res = await api.post('/report/generate', { student_id: studentId.value, job_name: job.job_name })
    reportContent.value = res.data.content
    reportId.value = res.data.report_id
  } catch (err) {
    ElMessage.error('报告生成失败')
  }
}

// ========== 润色 ==========
const polishReport = async () => {
  if (!reportContent.value) return
  polishing.value = true
  try {
    const res = await api.post('/report/polish', { text: reportContent.value })
    reportContent.value = res.data.polished
  } catch (err) {
    ElMessage.error('润色失败')
  } finally {
    polishing.value = false
  }
}

// ========== 导出 PDF ==========
const exportReport = async () => {
  if (!reportContent.value) return
  exporting.value = true
  try {
    const res = await api.post('/report/export', { markdown: reportContent.value }, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'career_report.pdf')
    document.body.appendChild(link)
    link.click()
    link.remove()
    ElMessage.success('导出成功')
  } catch (err) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// ========== 重置报告 ==========
const resetReport = () => {
  if (matchList.value.length > 0) {
    generateReport(matchList.value[0])
  } else {
    reportContent.value = ''
  }
}

// ========== 步骤导航 ==========
const prevStep = () => { if (activeStep.value > 0) activeStep.value-- }

const nextStep = () => {
  if (activeStep.value === 0 && !studentId.value) {
    ElMessage.warning('请先提交个人信息')
    return
  }
  if (activeStep.value === 1) {
    // 兴趣探索可跳过
  }
  if (activeStep.value === 2 && !profileGenerated.value) {
    ElMessage.warning('请先获取能力画像')
    return
  }
  if (activeStep.value === 3 && !matchStarted.value) {
    ElMessage.warning('请先完成人岗匹配')
    return
  }
  if (activeStep.value < steps.length - 1) activeStep.value++
}

const finish = () => {
  ElMessage.success('恭喜你完成了职业规划！')
  router.push('/')
}

// ========== 监听步骤变化加载题目 ==========
watch(() => activeStep.value, (newVal) => {
  if (newVal === 1 && !skipInterest.value && questions.value.length === 0) {
    fetchQuestions()
  }
})

// 组件挂载时检查登录状态（可选）
onMounted(() => {
  // 可在此处执行初始化操作，如检查 token 有效性
})
</script>
<style scoped>
/* ========== 全局样式优化 ========== */
.student-ability-page {
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: linear-gradient(145deg, #f9fafc 0%, #f0f3f8 100%);
  margin: 0;
  padding: 60px 0 0 0;
  color: #1a2639;
}

/* ========== 导航栏 ========== */
.top-nav {
  height: 60px;
  background: #fff;
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

/* ========== 主体容器布局 - 左侧步骤 + 右侧内容 ========== */
.main-container {
  display: flex;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  gap: 24px;
}

/* ========== 左侧瀑布式步骤导航 ========== */
.sidebar-step-indicator {
  width: 280px;
  min-width: 280px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-radius: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  padding: 24px;
  height: fit-content;
  position: sticky;
  top: 100px;
  align-self: flex-start;
}

.step-sidebar-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
}

.step-sidebar-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.step-sidebar-header p {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.step-list {
  position: relative;
  padding-left: 16px;
}

.sidebar-step-item {
  display: flex;
  position: relative;
  margin-bottom: 8px;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.3s ease;
  padding: 12px 16px;
  margin-left: 8px;
}

/* 步骤连接线样式 */
.step-connector {
  position: absolute;
  left: -16px;
  top: 40px;
  width: 2px;
  height: calc(100% + 8px);
  background: #e2e8f0;
  z-index: 1;
}

.step-connector.completed {
  background: #10b981;
}

.step-connector.active {
  background: #2563eb;
}

.step-connector.inactive {
  background: #e2e8f0;
}

/* 最后一个步骤隐藏连接线 */
.sidebar-step-item:last-child .step-connector {
  display: none;
}

.step-content-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 2;
  width: 100%;
}

/* 步骤状态样式 */
.sidebar-step-item:hover {
  background: rgba(37, 99, 235, 0.05);
}

.sidebar-step-item.active {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}

.sidebar-step-item.completed {
  background: rgba(16, 185, 129, 0.05);
}

/* 步骤图标样式 */
.step-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 12px;
  flex-shrink: 0;
}

/* 不同状态的图标样式 */
.inactive-icon {
  background: #e2e8f0;
  color: #94a3b8;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.completed-icon {
  background: #10b981;
  color: white;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.active-icon {
  background: white;
  color: #2563eb;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 步骤文本样式 */
.step-text {
  overflow: hidden;
}

.step-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #475569;
}

.sidebar-step-item.completed .step-name {
  color: #065f46;
  font-weight: 600;
}

.sidebar-step-item.active .step-name {
  color: white;
  font-weight: 600;
}

.step-status {
  font-size: 11px;
  opacity: 0.8;
  margin-top: 2px;
  color: white;
}

/* ========== 右侧主体内容 ========== */
.main-content {
  flex: 1;
  padding: 8px 0;
}

.content-container {
  width: 100%;
}

/* ========== 步骤标题徽章样式 ========== */
.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  font-size: 16px;
  font-weight: 600;
  margin-right: 12px;
}

/* 玻璃态卡片 */
.glass-panel {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 32px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15), inset 0 1px 2px rgba(255,255,255,0.6);
}

/* 步骤内容卡片 */
.step-content {
  padding: 40px;
  margin-top: 0;
}
.section-title {
  font-size: 26px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 24px 0;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(37, 99, 235, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 个人信息 */
.personal-info {
  display: flex;
  gap: 20px;
  margin-bottom: 32px;
}
.info-input :deep(.el-input__wrapper) {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.02);
  border: 1px solid #edf2f7;
  transition: all 0.2s;
}
.info-input :deep(.el-input__wrapper:hover) {
  border-color: #2563eb;
  box-shadow: 0 8px 16px -8px rgba(37,99,235,0.2);
}

/* 输入模式切换 */
.input-mode-switch {
  display: flex;
  gap: 16px;
  margin: 24px 0;
}
.mode-btn {
  flex: 1;
  padding: 14px 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 40px;
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  backdrop-filter: blur(4px);
}
.mode-btn.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
  box-shadow: 0 12px 20px -10px #2563eb;
}
.mode-btn:hover:not(.active) {
  background: #f8fafc;
  border-color: #94a3b8;
}

/* 上传区域 */
.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 32px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255,255,255,0.5);
}
.upload-area:hover {
  border-color: #2563eb;
  background: rgba(37,99,235,0.02);
  transform: scale(1.01);
}
.upload-icon { font-size: 56px; color: #94a3b8; margin-bottom: 16px; }
.upload-text { font-size: 20px; font-weight: 500; color: #1e293b; margin-bottom: 8px; }
.upload-tip { font-size: 14px; color: #64748b; }

/* 手动填写模块 */
.resume-block { margin-bottom: 28px; }
.block-title { font-size: 18px; font-weight: 600; color: #1f2937; margin: 0 0 10px 0; }
.block-textarea {
  width: 100%;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 15px;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
  background: white;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}
.block-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 4px rgba(37,99,235,0.1);
}
.block-hint { font-size: 13px; color: #94a3b8; margin-top: 8px; padding-left: 8px; }

/* 能力画像结果卡片 */
.result-card {
  background: rgba(255,255,255,0.7);
  border-radius: 28px;
  padding: 32px;
  backdrop-filter: blur(4px);
}
.score-overview { display: flex; gap: 40px; margin-bottom: 32px; }
.score-item { flex: 1; }
.score-label { display: block; font-size: 14px; color: #64748b; margin-bottom: 6px; }
.score-value { font-size: 32px; font-weight: 700; color: #1f2937; display: block; margin-bottom: 8px; }
.score-bar { height: 10px; background: #e2e8f0; border-radius: 20px; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, #2563eb, #3b82f6); border-radius: 20px; }

/* 维度网格 */
.dimension-item {
  display: grid;
  grid-template-columns: 120px 1fr 50px;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}
.dimension-name { color: #475569; font-weight: 500; }
.dimension-bar { height: 10px; background: #e2e8f0; border-radius: 20px; }
.dimension-score { font-weight: 600; color: #1f2937; }

/* 技能证书标签 */
.tags { display: flex; flex-wrap: wrap; gap: 10px; }
.tag {
  padding: 6px 16px;
  border-radius: 40px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}
.skill-tag { background: #dbeafe; color: #1e40af; }
.cert-tag { background: #dcfce7; color: #166534; }

/* 表格美化 */
:deep(.el-table) {
  border-radius: 24px;
  overflow: hidden;
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(4px);
}
:deep(.el-table th) {
  background: #f8fafc;
  color: #1e293b;
  font-weight: 600;
  border-bottom: none;
}
:deep(.el-table tr) { background: transparent; }

/* 按钮优化 */
.el-button--primary {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  border-radius: 40px;
  padding: 12px 32px;
  font-weight: 600;
  box-shadow: 0 10px 20px -8px #2563eb;
  transition: all 0.3s;
}
.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 30px -10px #2563eb;
}
.el-button--success {
  background: linear-gradient(135deg, #10b981, #34d399);
  border: none;
  border-radius: 40px;
  padding: 12px 32px;
  font-weight: 600;
  box-shadow: 0 10px 20px -8px #10b981;
}

/* 步骤操作按钮 */
.step-actions {
  display: flex;
  gap: 16px;
  margin-top: 32px;
  justify-content: flex-end;
}

/* 响应式优化 */
@media (max-width: 1024px) {
  .main-container {
    flex-direction: column;
    padding: 16px;
  }
  
  .sidebar-step-indicator {
    width: 100%;
    min-width: auto;
    position: static;
  }
  
  .step-list {
    display: flex;
    flex-wrap: wrap;
    padding-left: 0;
    gap: 8px;
  }
  
  .sidebar-step-item {
    flex: 1;
    min-width: calc(50% - 4px);
    margin-left: 0;
  }
  
  .step-connector {
    display: none;
  }
  
  .personal-info { 
    flex-direction: column; 
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .step-list {
    flex-direction: column;
  }
  
  .sidebar-step-item {
    min-width: auto;
  }
  
  .step-content {
    padding: 24px 16px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .step-actions {
    flex-direction: column;
    align-items: stretch;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
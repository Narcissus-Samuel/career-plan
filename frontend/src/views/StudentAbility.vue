<template>
  <div class="student-ability-page">
    <!-- 顶部导航栏（与之前相同） -->
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

    <!-- 主体内容 -->
    <main class="main-content">
      <div class="content-container">
        <!-- 步骤指示器 -->
        <div class="step-indicator">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="step-item"
            :class="{ active: activeStep === index, completed: activeStep > index }"
          >
            <div class="step-number">{{ activeStep > index ? '✓' : index + 1 }}</div>
            <div class="step-text">{{ step }}</div>
          </div>
        </div>

        <!-- 第一步：个人信息与简历信息 -->
        <div v-if="activeStep === 0" class="step-content">
          <h2 class="section-title">📋 个人信息</h2>
          <div class="personal-info">
            <el-input v-model="personalInfo.name" placeholder="姓名" size="large" class="info-input" />
            <el-input v-model="personalInfo.phone" placeholder="手机号" size="large" class="info-input" />
            <el-input v-model="personalInfo.email" placeholder="邮箱" size="large" class="info-input" />
          </div>

          <h2 class="section-title" style="margin-top: 32px;">📄 简历信息</h2>
          <div class="resume-score" v-if="resumeScore">
            <span class="score-label">简历完成度</span>
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

          <div class="step-actions">
            <el-button type="primary" size="large" @click="nextStep">保存并下一步</el-button>
          </div>
        </div>

        <!-- 第二步：兴趣探索 -->
        <div v-if="activeStep === 1" class="step-content">
          <h2 class="section-title">🎯 兴趣探索</h2>
          <div class="interest-box">
            <p>通过兴趣测试，你可以发现更适合自己的职业方向。你也可以选择跳过，直接基于能力进行匹配。</p>
            <el-checkbox v-model="skipInterest">跳过兴趣探索</el-checkbox>
            <div v-if="!skipInterest" class="interest-test">
              <p>（此处可嵌入霍兰德职业兴趣测试题目）</p>
              <el-button type="primary" @click="finishInterestTest">完成测试</el-button>
            </div>
          </div>
          <div class="step-actions">
            <el-button size="large" @click="prevStep">上一步</el-button>
            <el-button type="primary" size="large" @click="nextStep">下一步</el-button>
          </div>
        </div>

        <!-- 第三步：AI能力画像生成 -->
        <div v-if="activeStep === 2" class="step-content">
          <h2 class="section-title">🤖 AI能力画像生成</h2>
          <div v-if="!profileGenerated" class="generate-area">
            <p>点击下方按钮，AI将根据你填写的信息生成能力画像。</p>
            <el-button type="primary" size="large" @click="generateProfile" :loading="generating">
              {{ generating ? '生成中...' : '生成能力画像' }}
            </el-button>
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

        <!-- 第四步：人岗匹配（查看列表，无需选择） -->
        <div v-if="activeStep === 3" class="step-content">
          <h2 class="section-title">🎯 人岗匹配</h2>
          <div v-if="!matchStarted" class="match-start">
            <p>点击“立即匹配”，AI将分析你的能力与岗位的契合度，并推荐最适合的岗位。</p>
            <el-button type="primary" size="large" @click="startMatch">立即匹配</el-button>
          </div>
          <div v-else class="match-result">
            <el-table :data="matchList" style="width: 100%">
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

        <!-- 第五步：职业发展报告（可编辑、润色、导出） -->
        <div v-if="activeStep === 4" class="step-content">
          <h2 class="section-title">📄 职业发展报告</h2>
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
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'

// 导航栏相关（与之前相同）
const router = useRouter()
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')

const toggleUserMenu = () => { isUserMenuOpen.value = !isUserMenuOpen.value }
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
  const map = { '测评': '/interest-test', '分析': '/ability-analysis', '规划': '/development-path', '导出': '/report-export' }
  router.push(map[type] || '/')
}
const handleSearch = () => {
  const input = document.querySelector('.nav-search-input')
  if (input.value.trim()) router.push(`/search?keyword=${encodeURIComponent(input.value.trim())}`)
}

// 步骤配置
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
const resumeScore = computed(() => {
  let filled = 0
  if (personalInfo.name) filled++
  if (personalInfo.phone) filled++
  if (personalInfo.email) filled++
  if (resumeText.education) filled++
  if (resumeText.work) filled++
  if (resumeText.project) filled++
  if (resumeText.skillsCerts) filled++
  if (resumeText.summary) filled++
  return Math.min(100, Math.round((filled / 8) * 100))
})

// 第二步数据
const skipInterest = ref(false)

// 第三步数据
const generating = ref(false)
const profileGenerated = ref(false)
const profile = reactive({
  completeness: 0,
  competitiveness: 0,
  dimensions: {},
  skills: [],
  certificates: []
})

// 第四步数据
const matchStarted = ref(false)
const matchList = ref([])

// 第五步数据
const reportContent = ref('')
const polishing = ref(false)
const exporting = ref(false)

// 文件上传方法
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

// 生成能力画像（模拟）
const generateProfile = async () => {
  generating.value = true
  const loading = ElLoading.service({ lock: true, text: 'AI 正在分析...', background: 'rgba(0,0,0,0.7)' })
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    profile.completeness = 85
    profile.competitiveness = 78
    profile.dimensions = { '专业技能': 82, '创新能力': 70, '学习能力': 88, '抗压能力': 75, '沟通能力': 80, '实习能力': 65 }
    profile.skills = ['Python', 'Java', 'SQL', 'Vue']
    profile.certificates = ['英语六级', '计算机二级']
    profileGenerated.value = true
    ElMessage.success('能力画像生成成功！')
  } finally {
    generating.value = false
    loading.close()
  }
}

// 兴趣探索完成
const finishInterestTest = () => {
  ElMessage.success('兴趣测试完成！')
}

// 开始匹配
const startMatch = async () => {
  matchStarted.value = true
  // 模拟获取匹配结果（包含详细分析）
  matchList.value = [
    { job_name: 'Java开发工程师', overall_score: 92, skill_fit: 88, soft_gap: 15 },
    { job_name: '前端开发工程师', overall_score: 88, skill_fit: 85, soft_gap: 18 },
    { job_name: '数据分析师', overall_score: 85, skill_fit: 80, soft_gap: 20 },
    { job_name: '产品经理', overall_score: 82, skill_fit: 70, soft_gap: 25 },
  ]
  // 自动生成报告（基于匹配度最高的岗位）
  generateReport(matchList.value[0])
}

// 生成报告（基于给定岗位）
const generateReport = (job) => {
  reportContent.value = `# 职业生涯发展报告

## 1. 人岗匹配分析
根据您的能力画像，与您匹配度最高的岗位是 **${job.job_name}**，综合匹配度为 **${job.overall_score}%**。
- **专业技能契合度**：${job.skill_fit}%，您在 ${profile.skills.join('、')} 等技能上与岗位要求匹配良好，建议进一步补充框架知识。
- **通用素质差距**：${job.soft_gap}%，主要差距体现在创新能力和抗压能力上，建议通过参与项目锻炼。

## 2. 职业目标设定
结合您的兴趣和能力，建议将 **高级${job.job_name}** 作为中期目标，最终向架构师/技术专家方向发展。

## 3. 职业发展路径
参考岗位图谱，您的可能晋升路径为：
- ${job.job_name} → 高级${job.job_name} → 技术主管 → 架构师

## 4. 分阶段行动计划
- **短期（0-6个月）**：深入学习Spring Boot/微服务架构，完成一个完整项目；考取相关证书。
- **中期（6-12个月）**：参与开源项目或实习，积累实战经验；提升沟通与团队协作能力。

## 5. 评估与调整
建议每季度进行一次能力复盘，根据行业变化动态调整学习计划。`
}

// 报告操作
const polishReport = async () => {
  polishing.value = true
  ElMessage.loading({ content: '润色中...', duration: 0 })
  await new Promise(resolve => setTimeout(resolve, 1500))
  // 模拟润色，在末尾添加标记
  reportContent.value = reportContent.value + '\n\n（已智能润色，表达更专业流畅）'
  ElMessage.closeAll()
  ElMessage.success('润色完成')
  polishing.value = false
}
const exportReport = async () => {
  exporting.value = true
  ElMessage.loading({ content: '正在生成PDF...', duration: 0 })
  await new Promise(resolve => setTimeout(resolve, 2000))
  // 模拟导出成功
  ElMessage.closeAll()
  ElMessage.success('报告导出成功！文件已保存到下载目录。')
  exporting.value = false
}
const resetReport = () => {
  if (matchList.value.length > 0) {
    generateReport(matchList.value[0])
  } else {
    reportContent.value = ''
  }
}

// 步骤导航
const prevStep = () => {
  if (activeStep.value > 0) activeStep.value--
}
const nextStep = () => {
  if (activeStep.value === 0) {
    if (!personalInfo.name || !personalInfo.phone || !personalInfo.email) {
      ElMessage.warning('请填写完整的个人信息')
      return
    }
  }
  if (activeStep.value === 1) {
    // 兴趣探索可跳过，无需验证
  }
  if (activeStep.value === 2 && !profileGenerated.value) {
    ElMessage.warning('请先生成能力画像')
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
</script>



<style scoped>
/* ========== 全局样式 ========== */
.student-ability-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf5 100%);
  margin: 0;
  padding: 60px 0 0 0;
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

/* ========== 主体内容 ========== */
.main-content {
  padding: 40px 20px;
  display: flex;
  justify-content: center;
}
.content-container {
  max-width: 1000px;
  width: 100%;
}

/* ========== 步骤指示器 ========== */
.step-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 0 20px;
}
.step-item {
  flex: 1;
  text-align: center;
  position: relative;
}
.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin: 0 auto 8px;
  transition: all 0.3s;
}
.step-text {
  font-size: 14px;
  color: #6b7280;
}
.step-item.active .step-number {
  background: #2563eb;
  color: white;
}
.step-item.active .step-text {
  color: #2563eb;
  font-weight: 500;
}
.step-item.completed .step-number {
  background: #22c55e;
  color: white;
}
.step-item.completed .step-text {
  color: #22c55e;
}

/* ========== 步骤内容卡片 ========== */
.step-content {
  background: white;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}
.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #eef2f6;
}

/* ========== 个人信息 ========== */
.personal-info {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
}
.info-input {
  flex: 1;
}

/* ========== 输入模式切换 ========== */
.input-mode-switch {
  display: flex;
  gap: 16px;
  margin: 20px 0;
}
.mode-btn {
  flex: 1;
  padding: 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}
.mode-btn.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

/* ========== 上传简历区域 ========== */
.upload-section, .manual-section {
  margin-top: 20px;
}
.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.upload-area:hover {
  border-color: #2563eb;
  background: #f0f9ff;
}
.upload-icon {
  font-size: 48px;
  color: #94a3b8;
  margin-bottom: 16px;
}
.upload-text {
  font-size: 18px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 8px;
}
.upload-tip {
  font-size: 14px;
  color: #64748b;
}
.file-info {
  margin-top: 16px;
  padding: 12px;
  background: #f1f5f9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.file-name {
  font-weight: 500;
  color: #1e293b;
}
.file-size {
  color: #64748b;
  font-size: 14px;
}

/* ========== 手动填写简历模块 ========== */
.resume-block {
  margin-bottom: 24px;
}
.block-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}
.block-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  transition: border 0.2s;
}
.block-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
}
.block-hint {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 4px;
}

/* ========== 步骤操作按钮 ========== */
.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
}

/* ========== 兴趣探索 ========== */
.interest-box {
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}
.interest-test {
  margin-top: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

/* ========== 能力画像结果 ========== */
.profile-result { margin-top: 20px; }
.result-card { background: #f9fafb; border-radius: 16px; padding: 24px; }
.score-overview { display: flex; gap: 40px; margin-bottom: 24px; }
.score-item { flex: 1; }
.score-label { display: block; font-size: 14px; color: #64748b; margin-bottom: 4px; }
.score-value { font-size: 28px; font-weight: 700; color: #1f2937; display: block; margin-bottom: 8px; }
.score-bar { height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; background: #2563eb; border-radius: 4px; }
.dimension-scores { margin-bottom: 24px; }
.dimension-grid { display: grid; gap: 12px; }
.dimension-item { display: grid; grid-template-columns: 100px 1fr 40px; align-items: center; gap: 12px; }
.dimension-name { color: #475569; }
.dimension-bar { height: 8px; background: #e2e8f0; border-radius: 4px; }
.dimension-score { font-weight: 600; color: #1e293b; }
.skill-cert { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.tag { padding: 4px 12px; border-radius: 16px; font-size: 13px; }
.skill-tag { background: #dbeafe; color: #1e40af; }
.cert-tag { background: #dcfce7; color: #166534; }

/* ========== 人岗匹配表格 ========== */
.match-start { text-align: center; padding: 40px; }
.match-result { margin-top: 20px; }
:deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
}

/* ========== 报告区域 ========== */
.report-area { margin-top: 20px; }
.report-actions { display: flex; gap: 16px; margin-top: 16px; justify-content: flex-end; }

/* ========== 页脚 ========== */
.footer {
  background: #fff;
  padding: 30px 0;
  border-top: 1px solid #f0f0f0;
  text-align: center;
  color: #666;
  font-size: 14px;
  margin-top: 40px;
}
.footer-wrap {
  width: 1200px;
  margin: 0 auto;
}

/* ========== 动画 ========== */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .nav-wrap, .footer-wrap { width: 95%; padding: 0 20px; }
  .content-container { width: 95%; }
}
@media (max-width: 768px) {
  .nav-menu { display: none; }
  .personal-info { flex-direction: column; }
  .input-mode-switch { flex-direction: column; }
  .score-overview { flex-direction: column; gap: 20px; }
  .skill-cert { grid-template-columns: 1fr; }
  .dimension-item { grid-template-columns: 80px 1fr 30px; }
  .step-actions { flex-direction: column; }
  .report-actions { flex-direction: column; }
}
</style>
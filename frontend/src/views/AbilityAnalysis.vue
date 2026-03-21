<template>
  <div class="ability-profile-page">
    <!-- 顶部导航栏（与学生信息页样式一致，背景为白色） -->
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

    <!-- AI能力画像核心展示区域 -->
    <div class="profile-container">
      <div class="step-content glass-panel">
        <h2 class="section-title">🤖 AI 学生就业能力画像</h2>
        
        <!-- 加载状态 -->
        <div v-if="generatingProfile" class="loading-container">
          <div class="loading-spinner">🔄</div>
          <p class="loading-text">AI 正在分析你的简历数据，生成多维度能力画像...</p>
        </div>

        <!-- 画像结果（核心展示） -->
        <div v-else-if="profileGenerated" class="profile-result">
          <!-- 核心评分 -->
          <div class="core-scores">
            <div class="score-card">
              <span class="score-type">完整度评分</span>
              <span class="score-num">{{ profile.completeness }}%</span>
              <div class="score-bar">
                <div class="bar-fill" :style="{ width: profile.completeness + '%', background: getScoreColor(profile.completeness) }"></div>
              </div>
              <p class="score-desc">{{ getCompletenessDesc(profile.completeness) }}</p>
            </div>
            <div class="score-card">
              <span class="score-type">竞争力评分</span>
              <span class="score-num">{{ profile.competitiveness }}%</span>
              <div class="score-bar">
                <div class="bar-fill" :style="{ width: profile.competitiveness + '%', background: getScoreColor(profile.competitiveness) }"></div>
              </div>
              <p class="score-desc">{{ getCompetitiveDesc(profile.competitiveness) }}</p>
            </div>
          </div>

          <!-- 多维度能力评分（核心） -->
          <div class="dimension-scores">
            <h3 class="dimension-title">📊 多维度能力细分评分</h3>
            <div class="dimension-grid">
              <div v-for="(item, key) in profile.dimensions" :key="key" class="dimension-item">
                <div class="dimension-name">{{ item.label }}</div>
                <div class="dimension-bar">
                  <div class="bar-fill" :style="{ width: item.score + '%', background: getScoreColor(item.score) }"></div>
                </div>
                <div class="dimension-score">{{ item.score }}分</div>
                <div class="dimension-tip">{{ item.evaluation }}</div>
              </div>
            </div>
          </div>

          <!-- 专业技能 & 证书 -->
          <div class="skill-cert-section">
            <div class="skill-card">
              <h3 class="skill-title">💻 专业技能</h3>
              <div class="tags">
                <span v-for="skill in profile.skills" :key="skill.name" class="tag skill-tag">
                  {{ skill.name }} <small>(熟练度{{ skill.proficiency }}%)</small>
                </span>
              </div>
            </div>
            <div class="cert-card">
              <h3 class="cert-title">📜 证书资质</h3>
              <div class="tags">
                <span v-for="cert in profile.certificates" :key="cert.name" class="tag cert-tag">
                  {{ cert.name }} <small>({{ cert.level }})</small>
                </span>
              </div>
            </div>
          </div>

          <!-- AI 综合评价 -->
          <div class="ai-evaluation">
            <h3 class="eval-title">📝 AI 综合能力评价</h3>
            <div class="eval-content">{{ profile.aiEvaluation }}</div>
          </div>

          <!-- 操作按钮 -->
          <div class="profile-actions">
            <el-button @click="regenerateProfile" :loading="generatingProfile">重新生成画像</el-button>
            <el-button type="primary" @click="exportProfile">导出能力画像</el-button>
            <el-button type="success" @click="goToMatch">进入人岗匹配</el-button>
          </div>
        </div>

        <!-- 未生成状态 -->
        <div v-else class="empty-profile">
          <p class="empty-text">暂无能力画像数据，请先完成简历上传/手动录入</p>
          <el-button type="primary" @click="goBack">返回填写信息</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 路由实例
const router = useRouter()

// ========== 导航栏相关数据 ==========
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')

// ========== 基础配置 ==========
const token = localStorage.getItem('token')
const userId = localStorage.getItem('userId') || 3
const studentId = ref(localStorage.getItem('studentId') || null)

// Axios 实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  headers: { Authorization: token ? `Bearer ${token}` : '' },
  timeout: 30000
})

// ========== 核心数据 ==========
// 加载状态
const generatingProfile = ref(false)
// 画像生成状态
const profileGenerated = ref(true) // 直接设为true，模拟生成完成状态

// AI能力画像数据（模拟生成后的完整数据）
const profile = reactive({
  // 核心评分
  completeness: 85,     // 完整度
  competitiveness: 88,   // 竞争力
  // 多维度能力（包含所有核心维度）
  dimensions: {
    professionalSkill: { label: '专业技能', score: 90, evaluation: '专业技能扎实，掌握Java/Python等核心技术' },
    certificate: { label: '证书资质', score: 80, evaluation: '持有英语六级、计算机二级等核心证书' },
    innovation: { label: '创新能力', score: 75, evaluation: '具备一定创新思维，能提出优化方案' },
    learning: { label: '学习能力', score: 92, evaluation: '学习能力极强，能快速掌握新技术' },
    pressureResistance: { label: '抗压能力', score: 85, evaluation: '抗压能力良好，能应对紧急项目' },
    communication: { label: '沟通能力', score: 88, evaluation: '沟通表达清晰，善于团队协作沟通' },
    internship: { label: '实习能力', score: 82, evaluation: '有大厂实习经历，实践能力突出' },
    teamwork: { label: '团队协作', score: 89, evaluation: '团队协作能力优秀，能有效配合团队' },
    problemSolving: { label: '问题解决', score: 87, evaluation: '独立解决问题能力强，逻辑清晰' }
  },
  // 技能详情（带熟练度）
  skills: [
    { name: 'Java', proficiency: 90 },
    { name: 'Python', proficiency: 85 },
    { name: 'Spring Boot', proficiency: 88 },
    { name: 'MySQL', proficiency: 82 },
    { name: 'Vue.js', proficiency: 75 }
  ],
  // 证书详情（带等级）
  certificates: [
    { name: '英语六级', level: '优秀' },
    { name: '计算机二级', level: '良好' },
    { name: 'PMP项目管理师', level: '认证' }
  ],
  // AI综合评价
  aiEvaluation: `该学生综合能力优秀，专业技能扎实，尤其在Java后端开发领域具备较强竞争力。
学习能力突出，能快速适应新技术和新环境，实习经历丰富，具备实际项目经验。
沟通能力和团队协作能力良好，抗压能力强，适合互联网企业后端开发岗位。
建议重点提升前端技能和云原生技术，进一步增强全栈开发能力。`
})

// ========== 导航栏方法 ==========
const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const handleLogout = () => {
  localStorage.clear()
  isLogin.value = false
  router.push('/')
  ElMessage.success('退出登录成功')
}

const toggleTheme = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  // 可在这里添加主题切换的实际逻辑
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

// ========== 核心方法 ==========
/**
 * 重新生成能力画像
 */
const regenerateProfile = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重新生成能力画像吗？当前画像数据将被覆盖',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    generatingProfile.value = true
    // 调用接口重新生成（此处保留真实接口逻辑）
    const res = await api.get(`/profile/${studentId.value}/resume-data`)
    const newProfile = res.data
    
    // 更新画像数据
    profile.completeness = newProfile.completeness || profile.completeness
    profile.competitiveness = newProfile.competitiveness || profile.competitiveness
    profile.dimensions = newProfile.dimensions || profile.dimensions
    profile.skills = newProfile.skills || profile.skills
    profile.certificates = newProfile.certificates || profile.certificates
    profile.aiEvaluation = newProfile.ai_evaluation || profile.aiEvaluation
    
    ElMessage.success('AI能力画像重新生成成功！')
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('重新生成失败：' + (err.message || '服务器错误'))
    }
  } finally {
    generatingProfile.value = false
  }
}

/**
 * 导出能力画像为PDF
 */
const exportProfile = async () => {
  try {
    const res = await api.post('/profile/export', {
      student_id: studentId.value,
      format: 'pdf',
      profile_data: profile  // 传入当前画像数据
    }, { responseType: 'blob' })
    
    // 下载文件
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `学生能力画像_${localStorage.getItem('userName') || '未知用户'}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('能力画像导出成功！')
  } catch (err) {
    ElMessage.error('导出失败：' + (err.message || '服务器错误'))
  }
}

// ========== 辅助方法 ==========
/**
 * 根据分数获取评分颜色
 * @param {number} score 分数
 * @returns {string} 颜色值
 */
const getScoreColor = (score) => {
  if (score >= 80) return '#10b981'  // 绿色
  if (score >= 60) return '#f59e0b'  // 黄色
  if (score >= 40) return '#f97316'  // 橙色
  return '#ef4444'                   // 红色
}

/**
 * 获取完整度描述
 * @param {number} score 分数
 * @returns {string} 描述文本
 */
const getCompletenessDesc = (score) => {
  if (score >= 90) return '信息完整度极高，包含了所有核心维度的信息'
  if (score >= 80) return '信息完整度优秀，仅少量维度信息缺失'
  if (score >= 70) return '信息完整度良好，部分维度信息可补充'
  if (score >= 60) return '信息完整度一般，建议补充关键维度信息'
  return '信息完整度较低，需补充更多个人能力相关信息'
}

/**
 * 获取竞争力描述
 * @param {number} score 分数
 * @returns {string} 描述文本
 */
const getCompetitiveDesc = (score) => {
  if (score >= 90) return '在同批次求职者中竞争力极强，具备核心优势'
  if (score >= 80) return '在同批次求职者中竞争力优秀，具备明显优势'
  if (score >= 70) return '在同批次求职者中竞争力良好，有一定优势'
  if (score >= 60) return '在同批次求职者中竞争力一般，需提升核心能力'
  return '在同批次求职者中竞争力较弱，建议重点提升短板能力'
}

// ========== 页面跳转方法 ==========
const goBack = () => {
  // 跳回信息填写页
  router.push('/student-ability')
}

const goToMatch = () => {
  // 跳转到人岗匹配页
  router.push('/interest-test')
}
</script>

<style scoped>
/* 页面全局样式 */
.ability-profile-page {
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: linear-gradient(145deg, #f9fafc 0%, #f0f3f8 100%);
  margin: 0;
  padding: 60px 0 0 0; /* 给导航栏留出空间 */
  color: #1a2639;
}

/* ========== 导航栏样式（白色背景） ========== */
.top-nav {
  height: 60px;
  background: #ffffff; /* 导航栏背景改为白色 */
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

/* 容器样式 */
.profile-container {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

/* 玻璃态卡片 */
.glass-panel {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 32px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15), inset 0 1px 2px rgba(255,255,255,0.6);
  padding: 40px;
}

/* 标题样式 */
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

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}
.loading-spinner {
  font-size: 48px;
  animation: spin 2s linear infinite;
  margin-bottom: 20px;
}
.loading-text {
  font-size: 16px;
  color: #64748b;
  text-align: center;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 核心评分卡片 */
.core-scores {
  display: flex;
  gap: 24px;
  margin-bottom: 40px;
}
.score-card {
  flex: 1;
  background: rgba(255,255,255,0.9);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.05);
}
.score-type {
  display: block;
  font-size: 16px;
  color: #64748b;
  margin-bottom: 8px;
}
.score-num {
  display: block;
  font-size: 48px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 12px;
}
.score-bar {
  height: 12px;
  background: #e2e8f0;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 8px;
}
.bar-fill {
  height: 100%;
  border-radius: 20px;
  transition: width 1s ease-in-out;
}
.score-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* 多维度能力评分 */
.dimension-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}
.dimension-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 40px;
}
.dimension-item {
  background: rgba(255,255,255,0.9);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.dimension-name {
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 8px;
}
.dimension-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 8px;
}
.dimension-score {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
  margin-bottom: 4px;
}
.dimension-tip {
  font-size: 12px;
  color: #94a3b8;
  font-style: italic;
}

/* 技能证书区域 */
.skill-cert-section {
  display: flex;
  gap: 24px;
  margin-bottom: 40px;
}
.skill-card, .cert-card {
  flex: 1;
  background: rgba(255,255,255,0.9);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.05);
}
.skill-title, .cert-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tag {
  padding: 8px 16px;
  border-radius: 40px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}
.skill-tag { background: #dbeafe; color: #1e40af; }
.cert-tag { background: #dcfce7; color: #166534; }
.tag small {
  font-size: 12px;
  opacity: 0.8;
  font-weight: normal;
}

/* AI综合评价 */
.ai-evaluation {
  background: rgba(255,255,255,0.9);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.05);
  margin-bottom: 32px;
}
.eval-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}
.eval-content {
  font-size: 15px;
  line-height: 1.6;
  color: #334155;
  white-space: pre-line;
}

/* 操作按钮 */
.profile-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 20px;
}

/* 空状态 */
.empty-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}
.empty-text {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 20px;
}

/* 按钮样式优化 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  border-radius: 40px;
  padding: 12px 32px;
  font-weight: 600;
  box-shadow: 0 10px 20px -8px #2563eb;
  transition: all 0.3s;
}
:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 20px 30px -10px #2563eb;
}
:deep(.el-button--success) {
  background: linear-gradient(135deg, #10b981, #34d399);
  border: none;
  border-radius: 40px;
  padding: 12px 32px;
  font-weight: 600;
  box-shadow: 0 10px 20px -8px #10b981;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .core-scores { flex-direction: column; }
  .skill-cert-section { flex-direction: column; }
  .dimension-grid { grid-template-columns: 1fr; }
  .glass-panel { padding: 20px; }
  .nav-wrap { width: 95%; }
  .nav-menu { display: none; } /* 移动端隐藏导航菜单 */
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
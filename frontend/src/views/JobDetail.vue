<template>
  <div class="job-detail-page">
    <!-- 1. 顶部导航（完全复用原代码，固定在顶部） -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item" @click="$router.push('/job-portrait')">岗位画像</li>
            <li class="menu-item" @click="$router.push('/career-planning')">职业规划</li>
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
            <input 
              type="text" 
              class="nav-search-input" 
              placeholder="搜索职业方向、专业、院校、岗位类型"
              @keyup.enter="handleSearch"
            >
            <button class="nav-search-btn" @click="handleSearch">搜索</button>
          </div>

          <button class="btn-toggle-theme" @click="toggleTheme">🌙</button>
          
          <button class="btn-login" @click="$router.push('/login')" v-if="!isLogin">登录</button>
          <button class="btn-register" @click="$router.push('/register')" v-if="!isLogin">注册</button>
          
          <div class="user-profile" v-if="isLogin">
            <img 
              :src="userAvatar || 'https://picsum.photos/seed/avatar/40/40'" 
              alt="用户头像" 
              class="avatar"
              @click="toggleUserMenu"
            >
            <div class="user-menu" v-show="isUserMenuOpen">
              <div class="menu-item" @click="$router.push('/profile')">个人中心</div>
              <div class="menu-item" @click="$router.push('/settings')">账号设置</div>
              <div class="menu-item logout" @click="handleLogout">退出登录</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 2. 岗位详情主体内容（模仿番茄小说网书籍详情页布局） -->
    <main class="job-detail-main">
      <div class="detail-container">
        <!-- 新增：面包屑导航（和图片样式一致） -->
        <div class="breadcrumb">
          <span @click="$router.push('/')">首页</span>
          <span class="separator">/</span>
          <span class="current">{{ jobDetail.jobTitle }}</span>
        </div>

        <!-- 顶部信息区：左侧封面 + 右侧核心信息 -->
        <div class="job-top-section">
          <div class="job-cover-wrap">
            <img 
              :src="`https://picsum.photos/seed/${jobDetail.jobTitle}/200/260`" 
              :alt="jobDetail.jobTitle"
              class="job-cover"
            />
          </div>
          <div class="job-info-wrap">
            <h1 class="job-title">{{ jobDetail.jobTitle }}</h1>
            <div class="job-tags">
              <span class="tag status">{{ jobDetail.status }}</span>
              <span class="tag category" v-for="tag in jobDetail.tags" :key="tag">{{ tag }}</span>
            </div>
            <div class="job-meta">
              <span class="meta-item">薪资范围：{{ jobDetail.salaryRange }}</span>
              <span class="meta-item">最近更新：{{ jobDetail.updateTime }}</span>
            </div>
            <div class="job-actions">
              <button class="btn-read" @click="$router.push('/job-portrait')">查看岗位画像</button>
              <button class="btn-app" @click="handleApply">申请该岗位</button>
              <button class="btn-share" @click="handleShare">分享</button>
            </div>
          </div>
          <div class="job-author-wrap">
            <div class="author-avatar">
              <img src="https://picsum.photos/seed/company/60/60" alt="企业头像" />
            </div>
            <div class="author-info">
              <div class="author-name">{{ jobDetail.company }}</div>
              <div class="author-desc">{{ jobDetail.companyBasicInfo }}</div>
            </div>
          </div>
        </div>

        <!-- 岗位简介区 -->
        <section class="job-intro-section">
          <h2 class="section-title">岗位简介</h2>
          <div class="intro-content">
            <p>{{ jobDetail.intro }}</p>
          </div>
        </section>

        <!-- 岗位目录/章节区（对应小说目录） -->
        <section class="job-chapter-section">
          <h2 class="section-title">岗位要求 · {{ jobDetail.requireCount }} 条</h2>
          <div class="chapter-list">
            <div 
              class="chapter-item" 
              v-for="(item, index) in jobDetail.requirements" 
              :key="index"
              @click="handleViewRequirement(item)"
            >
              第{{ index + 1 }}条 {{ item.title }}
            </div>
          </div>
        </section>

        <!-- 新增：公司简介板块 -->
        <section class="company-intro-section">
          <h2 class="section-title">公司简介</h2>
          <div class="company-intro-content">
            <p>{{ jobDetail.companyIntro }}</p>
            <div class="company-detail-list">
              <div class="company-detail-item">
                <span class="detail-label">公司地点：</span>
                <span class="detail-value">{{ jobDetail.companyLocation }}</span>
              </div>
              <div class="company-detail-item">
                <span class="detail-label">所属行业：</span>
                <span class="detail-value">{{ jobDetail.companyIndustry }}</span>
              </div>
              <div class="company-detail-item">
                <span class="detail-label">公司规模：</span>
                <span class="detail-value">{{ jobDetail.companyScale }}</span>
              </div>
              <div class="company-detail-item">
                <span class="detail-label">公司类型：</span>
                <span class="detail-value">{{ jobDetail.companyType }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- 3. 页脚（和首页保持一致） -->
    <footer class="footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 助力大学生精准规划职业方向
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

// ========== 导航栏相关逻辑（完全复用） ==========
const router = useRouter()
const route = useRoute()

const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)

watch(
  () => route.path,
  () => {
    isLogin.value = !!localStorage.getItem('token')
    userAvatar.value = localStorage.getItem('avatar') || ''
  },
  { immediate: true }
)

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('avatar')
  localStorage.removeItem('nickname')
  isLogin.value = false
  isUserMenuOpen.value = false
  router.push('/')
}

const darkMode = ref(localStorage.getItem('darkMode') === 'true')
function applyTheme() {
  if (darkMode.value) document.body.classList.add('dark')
  else document.body.classList.remove('dark')
}
function toggleTheme() {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  applyTheme()
}

const goToFeature = (type) => {
  switch(type) {
    case '测评':
      router.push('/interest-test')
      break
    case '分析':
      router.push('/ability-analysis')
      break
    case '规划':
      router.push('/development-path')
      break
    case '导出':
      router.push('/report-export')
      break
    default:
      break
  }
}

const handleSearch = () => {
  const searchInput = document.querySelector('.nav-search-input')
  const keyword = searchInput.value.trim()
  if (keyword) {
    router.push(`/search?keyword=${encodeURIComponent(keyword)}`)
    searchInput.value = ''
  }
}

// ========== 岗位详情数据 ==========
const jobDetail = ref({
  jobTitle: '前端开发工程师',
  status: '热招中',
  tags: ['技术类', '前端', 'Vue', 'React'],
  salaryRange: '15-30K', // 薪资范围（替换原wordCount）
  updateTime: '2026-03-12 10:30',
  company: '字节跳动',
  // 公司基础信息（替换原companyDesc）
  companyBasicInfo: '北京 | 互联网 | 10000+人 | 民营企业',
  // 公司详细信息
  companyLocation: '北京市海淀区北四环西路58号理想国际大厦',
  companyIndustry: '互联网/电子商务/新媒体',
  companyScale: '10000人以上',
  companyType: '民营企业（独角兽企业）',
  // 公司简介
  companyIntro: '字节跳动成立于2012年3月，是一家全球化的互联网科技公司。公司致力于打造全球创作与交流平台，旗下拥有抖音、今日头条、西瓜视频、飞书、火山引擎等多款知名产品。字节跳动始终坚持技术驱动，通过人工智能等技术创新，为全球用户提供丰富的内容创作和消费体验，业务覆盖超过150个国家和地区，拥有数万名员工，是全球增长最快的科技公司之一。',
  intro: '【高薪岗位+双休+五险一金】入职即享完善福利体系。本岗位负责公司核心产品Web端开发，与优秀团队共同打造亿级用户产品，从需求评审到上线发布全流程参与，经历技术选型、性能优化、工程化建设等关键环节，技术栈涵盖Vue3/React、TypeScript、工程化构建等。我们期待对前端技术有热情、追求极致体验的你加入，一起构建流畅、高效、美观的用户界面。',
  requireCount: 6,
  requirements: [
    { id: 1, title: '熟练掌握HTML/CSS/JavaScript基础', content: '需深入理解DOM操作、事件机制、异步编程' },
    { id: 2, title: '掌握至少一种主流框架', content: 'Vue3或React技术栈，有相关项目经验优先' },
    { id: 3, title: '熟悉TypeScript', content: '能使用类型系统提升代码可维护性' },
    { id: 4, title: '了解工程化与性能优化', content: '熟悉Webpack/Vite构建工具，有性能优化经验' },
    { id: 5, title: '本科及以上学历', content: '计算机相关专业优先，1-3年前端开发经验' },
    { id: 6, title: '良好的沟通与协作能力', content: '能与产品、设计、后端高效协作' }
  ]
})

// ========== 交互方法 ==========
const handleApply = () => {
  ElMessage.success('已成功申请该岗位！')
}

const handleShare = () => {
  ElMessage.info('分享功能开发中，敬请期待')
}

const handleViewRequirement = (item) => {
  ElMessage.info(`查看要求：${item.title}\n${item.content}`)
}

onMounted(() => {
  applyTheme()
})
</script>

<style scoped>
/* 全局容器：顶部padding=导航栏高度，避免内容被遮挡 */
.job-detail-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #fff;
  margin: 0;
  padding: 60px 0 0 0;
}

/* ========== 顶部导航样式（完全复用原代码，保持固定） ========== */
.top-nav {
  height: 60px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
.nav-left {
  display: flex;
  align-items: center;
}
.logo {
  display: flex;
  align-items: center;
  margin-right: 40px;
  font-size: 18px;
  font-weight: bold;
  color: #000;
}
.logo-icon {
  font-size: 24px;
  margin-right: 8px;
}
.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}
.menu-item {
  margin: 0 15px;
  font-size: 14px;
  cursor: pointer;
  padding: 0 5px;
  position: relative;
  height: 60px;
  line-height: 60px;
  color: #000;
}
/* 激活状态样式：蓝色下划线 */
.menu-item.active {
  color: #2f54eb; /* 文字也改为蓝色，增强视觉效果 */
}
.menu-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #2f54eb; /* 蓝色下划线 */
}
.dropdown {
  position: relative;
}
.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  width: 200px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 4px;
  list-style: none;
  padding: 8px 0;
  margin: 0;
  display: none;
  z-index: 9999;
}
.dropdown:hover .dropdown-menu {
  display: block;
}
.dropdown-item {
  padding: 10px 15px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  height: auto;
  line-height: normal;
  color: #000;
}
.dropdown-item:hover {
  background: #f5f7fa;
}
.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.color-dot.red { background: #ff7a45; }
.color-dot.orange { background: #faad14; }
.color-dot.green { background: #52c41a; }
.color-dot.blue { background: #1890ff; }
.nav-right {
  display: flex;
  gap: 15px;
  align-items: center;
}
/* 搜索框缩小至原尺寸的2/3：原宽度300px → 200px，原高度36px → 24px */
.nav-search-wrap {
  display: flex;
  width: 200px; /* 300 * 2/3 = 200 */
  height: 24px; /* 36 * 2/3 = 24 */
}
.nav-search-input {
  flex: 1;
  height: 100%;
  padding: 0 10px; /* 内边距同步缩小 */
  border: 1px solid #e8e8e8;
  border-radius: 4px 0 0 4px;
  outline: none;
  font-size: 12px; /* 字体同步缩小 */
}
/* 搜索按钮缩小至原尺寸的2/3：原宽度80px → 约53px，原高度36px → 24px */
.nav-search-btn {
  width: 53px; /* 80 * 2/3 ≈ 53 */
  height: 100%;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 12px; /* 字体同步缩小 */
}
.btn-toggle-theme {
  padding: 6px 10px;
  border: none;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  color: #000;
}
.btn-login {
  padding: 6px 15px;
  border: 1px solid #2f54eb;
  color: #000;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.btn-register {
  padding: 6px 15px;
  border: none;
  color: #fff;
  background: #2f54eb;
  border-radius: 4px;
  cursor: pointer;
}
.user-profile {
  position: relative;
  display: flex;
  align-items: center;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #f0f0f0;
}
.user-menu {
  position: absolute;
  top: 50px;
  right: 0;
  width: 120px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  border-radius: 4px;
  z-index: 9999;
}
.user-menu .menu-item {
  padding: 8px 15px;
  font-size: 14px;
  cursor: pointer;
  height: auto;
  line-height: normal;
  margin: 0;
  color: #000;
}
.user-menu .menu-item:hover {
  background: #f5f7fa;
}
.user-menu .logout {
  color: #ff4d4f;
  border-top: 1px solid #e8e8e8;
}

/* ========== 面包屑导航样式（和岗位介绍字体一致） ========== */
.breadcrumb {
  font-size: 14px; /* 和岗位介绍字体大小一致 */
  line-height: 1.8; /* 和岗位介绍行高一致 */
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px; /* 缩小间距更协调 */
}
.breadcrumb span {
  cursor: pointer;
  color: #999; /* 浅灰色，和岗位meta信息颜色一致 */
  text-shadow: none; /* 移除阴影 */
}
.breadcrumb .separator {
  color: #999; /* 浅灰色 */
  cursor: default;
}
.breadcrumb .current {
  color: #999; /* 浅灰色，取消蓝色高亮 */
  cursor: default;
  text-shadow: none; /* 移除阴影 */
}

/* ========== 岗位详情主体样式 ========== */
.job-detail-main {
  width: 100%;
  padding: 20px 0;
  background: #f8f9fa;
}
.detail-container {
  width: 1200px;
  margin: 0 auto;
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.job-top-section {
  display: flex;
  gap: 30px;
  margin-bottom: 40px;
}
.job-cover-wrap {
  width: 200px;
  flex-shrink: 0;
}
.job-cover {
  width: 100%;
  height: 260px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.job-info-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.job-title {
  font-size: 28px;
  font-weight: bold;
  color: #222;
  margin: 0 0 15px 0;
}
.job-tags {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}
.tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}
.tag.status {
  background: #f0f9ff;
  color: #1890ff;
  border: 1px solid #b3ddff;
}
.tag.category {
  background: #f6f7f9;
  color: #666;
  border: 1px solid #e8e8e8;
}
.job-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #999;
  margin-bottom: 20px;
}
.job-actions {
  display: flex;
  gap: 15px;
}
.btn-read {
  padding: 10px 30px;
  background: #ff6b35;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}
.btn-app {
  padding: 10px 30px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}
.btn-share {
  padding: 10px 20px;
  background: #fff;
  color: #666;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.job-author-wrap {
  width: 200px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 15px;
  border-left: 1px solid #e8e8e8;
  padding-left: 30px;
}
.author-avatar img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}
.author-name {
  font-size: 16px;
  font-weight: 600;
  color: #222;
  margin-bottom: 4px;
}
.author-desc {
  font-size: 12px;
  color: #999;
}
.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #222;
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}
.job-intro-section {
  margin-bottom: 40px;
}
.intro-content {
  font-size: 14px;
  line-height: 1.8;
  color: #333;
}
.job-chapter-section {
  margin-bottom: 40px;
}
.chapter-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}
.chapter-item {
  padding: 12px 15px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
}
.chapter-item:hover {
  background: #e8f4ff;
  color: #2f54eb;
}

/* 新增：公司简介样式 */
.company-intro-section {
  margin-bottom: 40px;
}
.company-intro-content {
  font-size: 14px;
  line-height: 1.8;
  color: #333;
}
.company-detail-list {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}
.company-detail-item {
  display: flex;
  align-items: center;
}
.detail-label {
  font-weight: 600;
  color: #666;
  width: 80px;
  flex-shrink: 0;
}
.detail-value {
  color: #333;
}

/* ========== 页脚样式（和首页保持一致） ========== */
.footer {
  background: #fff;
  padding: 20px 0;
  border-top: 1px solid #e8e8e8;
  text-align: center;
  color: #666;
  font-size: 14px;
}
.footer-wrap {
  width: 1200px;
  margin: 0 auto;
}
</style>
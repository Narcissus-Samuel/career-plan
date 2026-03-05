<template>
  <div class="career-home">
    <!-- 1. 顶部导航 -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item active" @click="$router.push('/')">首页</li>
            <li class="menu-item" @click="$router.push('/job-portrait')">岗位画像</li>
            <li class="menu-item" @click="$router.push('/match-result')">人岗匹配</li>
            <li class="menu-item" @click="$router.push('/student-ability')">学生信息</li>
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
          <button class="btn-toggle-theme" @click="toggleTheme">🌙</button>
          
          <!-- 未登录：显示登录/注册按钮 -->
          <button class="btn-login" @click="$router.push('/login')" v-if="!isLogin">登录</button>
          <button class="btn-register" @click="$router.push('/register')" v-if="!isLogin">注册</button>
          
          <!-- 已登录：显示用户头像 + 下拉菜单 -->
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

    <!-- 2. Banner区（轮播图） -->
    <section class="banner-carousel">
      <div class="carousel-container" ref="carouselRef">
        <div 
          class="carousel-track" 
          :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
        >
          <div class="carousel-item" v-for="(item, index) in carouselList" :key="index">
            <img 
              :src="item.url" 
              alt="轮播图" 
              class="carousel-img"
            >
            <div class="carousel-overlay">
              <div class="overlay-left">
                <h1 class="overlay-title">大学生智能职业规划系统</h1>
                <p class="overlay-subtitle">精准匹配职业方向 · 科学规划成长路径</p>
                <div class="overlay-tags">
                  <span class="tag">个性化分析</span>
                  <span class="tag">多维度评估</span>
                  <span class="tag">一站式规划</span>
                  <span class="tag">数据驱动</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <button class="carousel-btn prev-btn" @click="prevSlide">◀</button>
        <button class="carousel-btn next-btn" @click="nextSlide">▶</button>
        <div class="carousel-indicators">
          <span 
            class="indicator" 
            v-for="(item, index) in carouselList" 
            :key="index"
            :class="{ active: index === currentIndex }"
            @click="goToSlide(index)"
          ></span>
        </div>
        <div class="upload-area">
          <label class="upload-btn">
            <input 
              type="file" 
              accept="image/*" 
              @change="handleImageUpload"
              hidden
            >
            📤 更换轮播图片
          </label>
        </div>
      </div>
    </section>

    <!-- 3. 搜索区 -->
    <section class="search-section">
      <div class="search-wrap">
        <input 
          type="text" 
          class="search-input" 
          placeholder="搜索职业方向、专业、院校、岗位类型"
          @keyup.enter="handleSearch"
        >
        <button class="search-btn" @click="handleSearch">搜索</button>
      </div>
    </section>

    <!-- 4. 核心分类入口（注释保留，如需启用可取消注释） -->
    <!-- <section class="category-section">
      <div class="category-wrap">
        <div class="category-card" @click="$router.push('/job-planning')">
          <div class="card-icon">👨💼</div>
          <div class="card-title">找工作规划</div>
          <div class="card-desc">校招、实习、应届生求职</div>
        </div>
        <div class="category-card" @click="$router.push('/postgraduate-planning')">
          <div class="card-icon">🎓</div>
          <div class="card-title">考研规划</div>
          <div class="card-desc">择校、择专业、备考计划</div>
        </div>
        <div class="category-card" @click="$router.push('/study-abroad-planning')">
          <div class="card-icon">🌏</div>
          <div class="card-title">留学规划</div>
          <div class="card-desc">选校、文书、语言备考</div>
        </div>
        <div class="category-card" @click="$router.push('/civil-service-planning')">
          <div class="card-icon">💼</div>
          <div class="card-title">考公规划</div>
          <div class="card-desc">岗位筛选、备考指导</div>
        </div>
        <div class="category-card" @click="$router.push('/entrepreneurship-planning')">
          <div class="card-icon">📈</div>
          <div class="card-title">创业规划</div>
          <div class="card-desc">项目分析、资源对接</div>
        </div>
      </div>
    </section> -->

    <!-- 5. 内容筛选区（含滑动分页） -->
    <section class="content-section">
      <div class="content-wrap">
        <div class="content-tabs">
          <span class="tab-item active" @click="switchTab('direction')">职业方向(200+)</span>
          <span class="tab-item" @click="switchTab('template')">规划模板(50+)</span>
          <span class="tab-item" @click="switchTab('case')">成功案例(1000+) <span class="new-tag">NEW</span></span>
        </div>
        <div class="filter-section">
          <div class="filter-tabs">
            <span class="filter-tab active" @click="switchFilter('industry')">行业</span>
            <span class="filter-tab" @click="switchFilter('education')">学历要求</span>
            <span class="filter-tab" @click="switchFilter('stage')">发展阶段</span>
          </div>
          <div class="filter-tags">
            <span class="filter-tag active" @click="selectTag('all')">全部</span>
            <span class="filter-tag" @click="selectTag('internet')">互联网</span>
            <span class="filter-tag" @click="selectTag('finance')">金融</span>
            <span class="filter-tag" @click="selectTag('education')">教育</span>
            <span class="filter-tag" @click="selectTag('manufacturing')">制造业</span>
            <span class="filter-tag" @click="selectTag('medical')">医疗健康</span>
            <span class="filter-tag" @click="selectTag('civil')">公务员</span>
            <span class="filter-tag" @click="selectTag('state-own')">国企</span>
            <span class="filter-tag" @click="selectTag('foreign')">外企</span>
            <span class="filter-tag" @click="selectTag('research')">科研</span>
          </div>
          <div class="sort-section">
            <span class="sort-label">排序方式:</span>
            <select class="sort-select" @change="handleSortChange">
              <option value="match">匹配度优先</option>
              <option value="hot">热门程度</option>
            </select>
            <span class="sort-label">适用阶段:</span>
            <select class="sort-select" @change="handleStageChange">
              <option value="all">全部阶段</option>
              <option value="fresh">大一/大二</option>
              <option value="senior">大三/大四</option>
            </select>
            <label class="checkbox-label">
              <input type="checkbox" @change="handleFreeFilter"> 仅看免费内容
            </label>
          </div>
        </div>

        <!-- 滑动内容容器 -->
        <div class="content-slider-container">
          <div 
            class="content-slider" 
            :style="{ transform: `translateX(-${(currentPage - 1) * 100}%)` }"
          >
            <div 
              class="slider-page" 
              v-for="page in totalPages" 
              :key="page"
            >
              <div class="content-preview">
                <div 
                  class="content-card" 
                  v-for="item in getPageData(page)" 
                  :key="item.id" 
                  @click="$router.push(`/detail/${item.id}`)"
                >
                  <div class="card-header">
                    <span class="card-title">{{ item.title }}</span>
                  </div>
                  <div class="card-body">
                    <img :src="item.imgUrl" alt="规划案例" class="card-img">
                  </div>
                  <div class="card-footer">
                    <span class="tag">{{ item.stage }}</span>
                    <span class="tag">{{ item.type }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页控件 -->
        <div class="pagination-wrap" style="margin-top: 30px; text-align: center;">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="total"
            :page-size="pageSize"
            :current-page="currentPage"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </section>

    <!-- 6. 页脚 -->
    <footer class="footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 助力大学生精准规划职业方向
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

// ========== 新增：登录状态核心逻辑 ==========
const router = useRouter()
const route = useRoute()

// 登录状态（从本地存储读取，初始值安全）
const isLogin = ref(!!localStorage.getItem('token'))
// 用户头像（无则用默认头像）
const userAvatar = ref(localStorage.getItem('avatar') || '')
// 用户下拉菜单展开状态
const isUserMenuOpen = ref(false)

// 监听路由变化，确保登录/退出后状态实时更新
watch(
  () => route.path,
  () => {
    isLogin.value = !!localStorage.getItem('token')
    userAvatar.value = localStorage.getItem('avatar') || ''
  },
  { immediate: true }
)

// 切换用户菜单显示/隐藏
const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

// 退出登录逻辑（移除alert弹窗）
const handleLogout = () => {
  // 清空本地存储的登录信息
  localStorage.removeItem('token')
  localStorage.removeItem('avatar')
  localStorage.removeItem('nickname')
  
  // 更新状态
  isLogin.value = false
  isUserMenuOpen.value = false
  
  // 跳转到首页
  router.push('/')
}

// ========== 原有：主题切换逻辑 ==========
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

// ========== 原有：轮播图逻辑 ==========
const carouselRef = ref(null)
const currentIndex = ref(0)
const carouselList = ref([
  { url: 'https://picsum.photos/seed/carousel1/1200/300' },
  { url: 'https://picsum.photos/seed/carousel2/1200/300' },
  { url: 'https://picsum.photos/seed/carousel3/1200/300' }
])
let carouselTimer = null

const startCarousel = () => {
  carouselTimer = setInterval(() => {
    nextSlide()
  }, 3000)
}
const prevSlide = () => {
  currentIndex.value = (currentIndex.value - 1 + carouselList.value.length) % carouselList.value.length
}
const nextSlide = () => {
  currentIndex.value = (currentIndex.value + 1) % carouselList.value.length
}
const goToSlide = (index) => {
  currentIndex.value = index
}
// 轮播图上传（移除所有alert弹窗）
const handleImageUpload = (e) => {
  const file = e.target.files[0]
  if (!file) return
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    return // 移除alert提示
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    return // 移除alert提示
  }
  const reader = new FileReader()
  reader.onload = (event) => {
    carouselList.value.push({ url: event.target.result })
    currentIndex.value = carouselList.value.length - 1
    // 移除alert提示
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

// ========== 原有：内容列表分页逻辑 ==========
const allData = ref([])
const loading = ref(false)
const pageSize = ref(8)
const currentPage = ref(1)

const total = computed(() => allData.value.length)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const getPageData = (page) => {
  const start = (page - 1) * pageSize.value
  const end = start + pageSize.value
  return allData.value.slice(start, end)
}

const fetchAllContents = async () => {
  loading.value = true
  try {
    // 模拟数据（如果后端接口未就绪，可先用这个测试）
    allData.value = [
      { id: 1, title: '互联网产品经理职业规划', imgUrl: 'https://picsum.photos/seed/job1/300/200', stage: '大三/大四', type: '互联网' },
      { id: 2, title: '金融行业风控岗位发展路径', imgUrl: 'https://picsum.photos/seed/job2/300/200', stage: '大四/毕业', type: '金融' },
      { id: 3, title: '教育行业教师职业规划', imgUrl: 'https://picsum.photos/seed/job3/300/200', stage: '大二/大三', type: '教育' },
      { id: 4, title: '制造业工程师成长路径', imgUrl: 'https://picsum.photos/seed/job4/300/200', stage: '大三/实习', type: '制造业' },
      { id: 5, title: '医疗行业临床医生规划', imgUrl: 'https://picsum.photos/seed/job5/300/200', stage: '读研/规培', type: '医疗健康' },
      { id: 6, title: '公务员岗位报考与备考指南', imgUrl: 'https://picsum.photos/seed/job6/300/200', stage: '大四/毕业', type: '公务员' },
      { id: 7, title: '国企技术岗职业发展规划', imgUrl: 'https://picsum.photos/seed/job7/300/200', stage: '毕业/入职', type: '国企' },
      { id: 8, title: '外企市场岗成长路径', imgUrl: 'https://picsum.photos/seed/job8/300/200', stage: '大三/实习', type: '外企' },
      { id: 9, title: '科研院所研究员职业规划', imgUrl: 'https://picsum.photos/seed/job9/300/200', stage: '读研/读博', type: '科研' },
    ]
    // 真实接口（后端就绪后替换）
    // const res = await axios.get('/api/contents?size=1000')
    // allData.value = res.data.data || []
  } catch (error) {
    console.error('获取内容列表失败', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
}

// ========== 原有：其他功能逻辑 ==========
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

// 搜索功能（移除alert弹窗）
const handleSearch = () => {
  const searchInput = document.querySelector('.search-input')
  const keyword = searchInput.value.trim()
  if (keyword) {
    router.push(`/search?keyword=${encodeURIComponent(keyword)}`)
  }
  // 移除空关键词的alert提示
}

const switchTab = (tabType) => {
  console.log('切换标签：', tabType)
  // 可根据实际需求重新获取数据
}

const switchFilter = (filterType) => {
  console.log('切换筛选类型：', filterType)
}

const selectTag = (tag) => {
  console.log('选择筛选标签：', tag)
}

const handleSortChange = (e) => {
  console.log('排序方式：', e.target.value)
}

const handleStageChange = (e) => {
  console.log('适用阶段：', e.target.value)
}

const handleFreeFilter = (e) => {
  console.log('仅看免费内容：', e.target.checked)
}

// ========== 原有：生命周期 ==========
onMounted(() => {
  fetchAllContents()
  startCarousel()
  applyTheme()
})

onUnmounted(() => {
  clearInterval(carouselTimer)
})
</script>

<style scoped>
/* 全局容器 */
.career-home {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f8f9fa;
  margin: 0;
  padding: 0;
}

/* 新增：用户头像和菜单样式 */
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
  z-index: 999;
}
.user-menu .menu-item {
  padding: 8px 15px;
  font-size: 14px;
  cursor: pointer;
  height: auto;
  line-height: normal;
  margin: 0;
  color: #000; /* 用户下拉菜单文字黑色 */
}
.user-menu .menu-item:hover {
  background: #f5f7fa;
}
.user-menu .logout {
  color: #ff4d4f;
  border-top: 1px solid #e8e8e8;
}

/* 滑动容器样式 */
.content-slider-container {
  width: 100%;
  overflow: hidden;        
  position: relative;
}
.content-slider {
  display: flex;           
  width: 100%;
  transition: transform 0.3s ease;  
}
.slider-page {
  flex: 0 0 100%;          
  width: 100%;
}
.content-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  width: 100%;
}

/* 1. 顶部导航样式 */
.top-nav {
  height: 60px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  width: 100%;
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
  color: #000; /* logo文字黑色 */
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
  color: #000; /* 导航菜单项默认黑色 */
}
.menu-item.active {
  color: #000; /* 激活状态也为黑色 */
}
.menu-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #2f54eb; /* 激活下划线保留蓝色 */
}

/* 下拉菜单样式 */
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
  z-index: 999;
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
  color: #000; /* 下拉菜单项文字黑色 */
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
  gap: 10px;
  align-items: center;
}
.btn-toggle-theme {
  padding: 6px 10px;
  border: none;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  color: #000; /* 主题切换按钮文字黑色 */
}
.btn-login {
  padding: 6px 15px;
  border: 1px solid #2f54eb;
  color: #000; /* 登录按钮文字黑色 */
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.btn-register {
  padding: 6px 15px;
  border: none;
  color: #fff; /* 注册按钮文字白色（背景蓝色保留） */
  background: #2f54eb;
  border-radius: 4px;
  cursor: pointer;
}

/* 2. 轮播Banner区样式 */
.banner-carousel {
  width: 100%;
  height: 280px;
  position: relative;
  overflow: hidden;
}
.carousel-container {
  width: 100%;
  height: 100%;
  position: relative;
}
.carousel-track {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease;
}
.carousel-item {
  flex: 0 0 100%;
  height: 100%;
  position: relative;
}
.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
/* 轮播图文字遮罩层 */
.carousel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 120px;
  box-sizing: border-box;
  color: #fff;
}
.overlay-left {
  text-align: center;
}
.overlay-title {
  font-size: 38px;
  font-weight: bold;
  margin: 0 0 15px 0;
}
.overlay-subtitle {
  font-size: 18px;
  margin: 0 0 20px 0;
  opacity: 0.9;
}
.overlay-tags {
  display: flex;
  gap: 10px;
  justify-content: center;
}
.overlay-tags .tag {
  background: rgba(255,255,255,0.2);
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 14px;
}
/* 轮播控制按钮 */
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.3);
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  z-index: 10;
}
.carousel-btn:hover {
  background: rgba(0,0,0,0.5);
}
.prev-btn {
  left: 20px;
}
.next-btn {
  right: 20px;
}
/* 轮播指示器 */
.carousel-indicators {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}
.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.5);
  cursor: pointer;
}
.indicator.active {
  background: #fff;
}
/* 上传按钮 */
.upload-area {
  position: absolute;
  bottom: 15px;
  right: 20px;
}
.upload-btn {
  padding: 6px 15px;
  background: rgba(255,255,255,0.8);
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.upload-btn:hover {
  background: #fff;
}

/* 3. 搜索区样式 */
.search-section {
  padding: 30px 0;
}
.search-wrap {
  width: 800px;
  margin: 0 auto;
  display: flex;
}
.search-input {
  flex: 1;
  height: 42px;
  padding: 0 15px;
  border: 1px solid #e8e8e8;
  border-radius: 4px 0 0 4px;
  outline: none;
  font-size: 14px;
}
.search-btn {
  width: 80px;
  height: 42px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

/* 4. 核心分类入口样式 */
.category-section {
  padding: 10px 0 40px;
}
.category-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
}
.category-card {
  flex: 1;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 25px 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}
.category-card:hover {
  border-color: #2f54eb;
  box-shadow: 0 4px 12px rgba(47,84,235,0.1);
}
.card-icon {
  font-size: 28px;
  margin-bottom: 12px;
}
.card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 6px;
}
.card-desc {
  font-size: 12px;
  color: #666;
}

/* 5. 内容筛选区样式 */
.content-section {
  padding-bottom: 40px;
}
.content-wrap {
  width: 1200px;
  margin: 0 auto;
}
.content-tabs {
  margin-bottom: 20px;
}
.tab-item {
  font-size: 16px;
  margin-right: 25px;
  cursor: pointer;
}
.tab-item.active {
  color: #2f54eb;
  font-weight: bold;
}
.new-tag {
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 5px;
}
.filter-section {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.filter-tabs {
  display: flex;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 10px;
  margin-bottom: 15px;
}
.filter-tab {
  padding: 5px 20px;
  cursor: pointer;
  font-size: 14px;
}
.filter-tab.active {
  color: #2f54eb;
  font-weight: bold;
  border-bottom: 2px solid #2f54eb;
}
.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}
.filter-tag {
  padding: 4px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
}
.filter-tag.active {
  background: #2f54eb;
  color: #fff;
  border-color: #2f54eb;
}
.sort-section {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
  gap: 15px;
}
.sort-label {
  margin-right: 5px;
}
.sort-select {
  height: 28px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 0 5px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.checkbox-label input {
  margin-right: 5px;
}
.content-preview {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.content-card {
  width: calc(25% - 15px);
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: box-shadow 0.3s;
}
.content-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.card-header {
  padding: 10px 15px;
  border-bottom: 1px solid #e8e8e8;
}
.card-title {
  font-size: 14px;
  font-weight: bold;
}
.card-body {
  padding: 10px;
}
.card-img {
  width: 100%;
  height: auto;
  border-radius: 4px;
}
.card-footer {
  padding: 10px 15px;
  display: flex;
  gap: 8px;
}

/* 6. 页脚样式 */
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
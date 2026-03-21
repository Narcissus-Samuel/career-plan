<template>
  <div class="career-home">
    <!-- 1. 顶部导航（整合搜索框）- 固定在顶部 -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item active" @click="$router.push('/')">首页</li>
            <li class="menu-item" @click="$router.push('/student-ability')">岗位画像</li>
            <li class="menu-item" @click="$router.push('/career-planning-intro')">职业规划</li>
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

        <!-- 导航栏右侧：搜索框 + 原有功能 -->
        <div class="nav-right">
          <!-- 导航栏内的搜索框 -->
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

    <!-- 2. Banner区（轮播图）- 调整顶部间距避免被导航栏遮挡 -->
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

    <!-- 调整：轮播图下方功能模块样式（番茄小说网风格） -->
    <section class="function-modules">
      <div class="modules-wrap">
        <div class="module-item" @click="$router.push('/job-portrait')">
          <div class="module-content">
            <div class="module-title">岗位画像</div>
            <div class="module-desc">优秀岗位信息展示</div>
          </div>
          <span class="module-arrow">></span>
        </div>
        <div class="module-item" @click="$router.push('/career-planning')">
          <div class="module-content">
            <div class="module-title">AI职业规划</div>
            <div class="module-desc">智能生成职业规划</div>
          </div>
          <span class="module-arrow">></span>
        </div>
        <div class="module-item" @click="$router.push('/match-result')">
          <div class="module-content">
            <div class="module-title">人岗匹配结果</div>
            <div class="module-desc">查看个人匹配岗位</div>
          </div>
          <span class="module-arrow">></span>
        </div>
      </div>
    </section>

    <!-- 7. 招聘岗位卡片区（修改为五列两行，和图片一致） -->
    <section class="job-section">
      <div class="job-wrap">
        <!-- 新增：岗位信息标题 + 筛选栏 - 调整布局，筛选词放在标题下方 -->
        <div class="job-header">
          <h2 class="job-title-main">岗位信息</h2>
          <!-- 修改：筛选栏移到标题下方，移除重置按钮 -->
          <div class="job-filter">
            <div class="filter-tags">
              <!-- 动态渲染岗位名称筛选标签 -->
              <span 
                class="filter-tag" 
                :class="{ active: filterJobName === '' }"
                @click="filterJobName = ''; filterJobs()"
              >
                全部岗位
              </span>
              <span 
                class="filter-tag" 
                v-for="jobName in jobNameList" 
                :key="jobName"
                :class="{ active: filterJobName === jobName }"
                @click="filterJobName = jobName; filterJobs()"
              >
                {{ jobName }}
              </span>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在加载岗位数据...</p>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class="error-container">
          <p class="error-text">{{ error }}</p>
          <button class="reload-btn" @click="fetchAllJobData">重新加载</button>
        </div>

        <!-- 岗位卡片容器（改为五列网格布局，和图片一致） -->
        <div 
          class="job-card-container" 
          ref="jobContainerRef"
          v-else
        >
          <!-- 岗位卡片（五列两行排列，和图片样式一致） -->
          <div
            class="job-card"
            v-for="(item, index) in currentPageJobs" 
            :key="item.id"
            :class="{ 'animate-in': jobCardAnimateStates[index] }"
            @mouseenter="hoverJobCard = item.id"
            @mouseleave="hoverJobCard = null"
            @dblclick="goToJobDetail(item.id)"
          >
            <!-- 岗位卡片背景图（带弧形底部，和图片一致） -->
            <div class="card-image-wrap">
              <!-- 修改：使用岗位名称作为seed生成对应图片 -->
              <img 
                :src="`https://picsum.photos/seed/${item.job_name}/200/200`" 
                alt="岗位图片" 
                class="portrait-cover"
              >
              <!-- 左侧竖排文字（和图片一致） -->
              <div class="vertical-text">
                <span>{{ item.companyShort || item.company?.substring(0, 2) || '未知' }}</span>
                <span>{{ item.category || '其他' }}</span>
                <span class="date">{{ item.date || '2026-03' }}</span>
              </div>
              
              <!-- 新增：悬浮时显示的岗位画像和薪资信息（右下角） -->
              <div class="job-hover-info" v-if="hoverJobCard === item.id">
                <div class="job-portrait-tag">
                  <span>岗位画像</span>
                </div>
                <div class="job-salary-tag">
                  <span>{{ item.salary_range || item.salary || '面议' }}</span>
                </div>
              </div>
            </div>
            
            <!-- 岗位信息文字（修改：岗位名称在上，公司名称在下，颜色区分） -->
            <div class="job-card-content">
              <div class="job-title">{{ item.job_name || '未知岗位' }}</div>
              <div class="job-company">{{ item.company || '未知公司' }}</div>
              <!-- 移除原有的desc，如需保留可调整位置 -->
            </div>
          </div>

          <!-- 空数据提示 -->
          <div v-if="filteredJobList.length === 0" class="empty-job-container">
            <p class="empty-text">暂无匹配的岗位数据</p>
          </div>
        </div>

        <!-- 分页导航 -->
        <div v-if="filteredJobList.length > 0" class="pagination-container">
          <div class="pagination-info">
            共 {{ filteredJobList.length }} 个岗位，当前第 {{ currentPage }}/{{ totalPages }} 页
          </div>
          <div class="pagination">
            <button 
              class="page-btn" 
              @click="changePage(1)"
              :disabled="currentPage === 1"
            >
              首页
            </button>
            <button 
              class="page-btn" 
              @click="changePage(currentPage - 1)"
              :disabled="currentPage === 1"
            >
              上一页
            </button>
            
            <button 
              v-for="pageNum in pageNumbers" 
              :key="pageNum"
              class="page-number"
              :class="{ active: pageNum === currentPage }"
              @click="changePage(pageNum)"
              v-if="pageNum !== -1"
            >
              {{ pageNum }}
            </button>
            <span class="page-ellipsis" v-for="(pageNum, index) in pageNumbers" :key="`ellipsis-${index}`" v-if="pageNum === -1">...</span>
            
            <button 
              class="page-btn" 
              @click="changePage(currentPage + 1)"
              :disabled="currentPage === totalPages"
            >
              下一页
            </button>
            <button 
              class="page-btn" 
              @click="changePage(totalPages)"
              :disabled="currentPage === totalPages"
            >
              尾页
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 新增：最适配十大岗位 - 传送带形式 -->
    <section class="top-ten-jobs-section">
      <div class="section-header">
        <h2 class="section-title">最适配十大岗位</h2>
        <el-button type="text" @click="$router.push('/match-result')">查看全部 ></el-button>
      </div>
      <div class="slider-container" ref="sliderRef">
        <div 
          class="slider-track" 
          :style="{ transform: `translateX(-${sliderOffset}%)` }"
        >
          <!-- 复制一份数据实现无缝循环 -->
          <div
            class="slider-card"
            v-for="(job, index) in [...topTenJobs, ...topTenJobs]"
            :key="index"
            @click="$router.push('/match-result')"
          >
            <img :src="job.cover" :alt="job.jobName" class="slider-card-cover" />
            <div class="slider-card-info">
              <div class="slider-card-title">{{ job.jobName }}</div>
              <div class="slider-card-match">匹配度：{{ job.matchRate }}%</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 新增：岗位画像卡片区域（番茄小说网瀑布流排版+黑色背景） -->
    <section class="job-portrait-card-section" ref="portraitSectionRef">
      <div class="section-header">
        <h2 class="section-title">热门岗位画像</h2>
        <el-button type="text" @click="$router.push('/job-portrait')">查看全部 ></el-button>
      </div>
      <div 
        class="portrait-card-container" 
        ref="portraitContainerRef"
        @mousemove="handleMouseMove"
      >
        <div
          class="portrait-card"
          v-for="(job, index) in jobPortraitList"
          :key="job.jobName"
          :style="getCardStyle(index)"
          :class="{ 'animate-in': cardAnimateStates[index] }"
          @click="$router.push('/job-portrait')"
          @mouseenter="hoverPortrait = job.jobName"
          @mouseleave="hoverPortrait = null"
        >
          <!-- 仅显示岗位画像图片，无默认文字 -->
          <img :src="job.cover" :alt="job.jobName" class="portrait-cover" />
          
          <!-- 悬浮时显示岗位名称 -->
          <div class="portrait-name-tooltip" v-if="hoverPortrait === job.jobName">
            {{ job.jobName }}
          </div>
        </div>
      </div>
    </section>

    <!-- 8. 页脚 -->
    <footer class="footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 助力大学生精准规划职业方向
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// ========== 登录状态核心逻辑 ==========
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
  ElMessage.success('退出登录成功')
}

// ========== 主题切换逻辑 ==========
const darkMode = ref(localStorage.getItem('darkMode') === 'true')
function applyTheme() {
  if (darkMode.value) {
    document.body.classList.add('dark')
  } else {
    document.body.classList.remove('dark')
  }
}

function toggleTheme() {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  applyTheme()
  ElMessage.success(`已切换为${darkMode.value ? '暗黑' : '明亮'}模式`)
}

// ========== 轮播图逻辑 ==========
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

const handleImageUpload = (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请选择图片文件')
    return
  }
  
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过5MB')
    return
  }
  
  const reader = new FileReader()
  reader.onload = (event) => {
    carouselList.value.push({ url: event.target.result })
    currentIndex.value = carouselList.value.length - 1
    ElMessage.success('轮播图片上传成功')
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

// ========== 招聘岗位数据（适配新的Flask接口） ==========
const jobList = ref([])
const jobNameList = ref([]) // 存储所有唯一的岗位名称
const loading = ref(false) // 加载状态
const error = ref('') // 错误信息

// 后端接口基础地址
const API_BASE_URL = 'http://localhost:5000' 

// 更新接口地址，匹配Flask后端
const ALL_JOBS_API_URL = `${API_BASE_URL}/api/jobs/simple_search` // 使用simple_search获取所有岗位
const JOB_DETAIL_API_URL = `${API_BASE_URL}/api/jobs/` // 获取岗位详情
const JOB_PROFILE_API_URL = `${API_BASE_URL}/api/jobs/` // 获取岗位画像
const JOB_CATEGORIES_API_URL = `${API_BASE_URL}/api/jobs/categories` // 获取岗位分类
const JOB_NAMES_API_URL = `${API_BASE_URL}/api/jobs/names` // 新增：获取所有岗位名称接口

// 计算薪资中间值（用于排序）
const calculateSalaryValue = (salaryRange) => {
  if (!salaryRange || salaryRange === '面议') return 0
  
  // 提取薪资范围中的数字
  const match = salaryRange.match(/(\d+)K-(\d+)K/)
  if (match && match.length === 3) {
    const min = parseFloat(match[1])
    const max = parseFloat(match[2])
    return (min + max) / 2
  }
  
  return 0
}

// 获取所有唯一的岗位名称
const fetchJobNames = async () => {
  try {
    const response = await axios.get(JOB_NAMES_API_URL, {
      timeout: 5000,
      headers: { 
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      withCredentials: false,
    })
    
    // 处理返回的岗位名称列表，去重并过滤空值
    if (Array.isArray(response.data)) {
      const uniqueNames = Array.from(new Set(response.data))
        .filter(name => name && name.trim() && name !== '未知岗位')
        .sort() // 按字母顺序排序
      jobNameList.value = uniqueNames
    } else if (response.data?.names) {
      const uniqueNames = Array.from(new Set(response.data.names))
        .filter(name => name && name.trim() && name !== '未知岗位')
        .sort()
      jobNameList.value = uniqueNames
    }
  } catch (err) {
    console.error('获取岗位名称列表失败:', err)
    // 备用方案：从已获取的岗位数据中提取名称
    if (jobList.value.length > 0) {
      const uniqueNames = Array.from(new Set(jobList.value.map(item => item.job_name)))
        .filter(name => name && name.trim() && name !== '未知岗位')
        .sort()
      jobNameList.value = uniqueNames
    }
  }
}

// 跳转到岗位详情页（需要时才获取详情）
const goToJobDetail = async (jobId) => {
  try {
    // 先查找本地是否有该岗位的详细信息
    const jobItem = jobList.value.find(item => item.id === jobId)
    
    // 如果没有详细信息，则获取
    if (jobItem && !jobItem.detailFetched) {
      ElMessage.info('正在加载岗位详情...')
      const detail = await fetchJobDetail(jobId)
      const profile = await fetchJobProfile(jobId)
      
      // 更新本地数据
      const index = jobList.value.findIndex(item => item.id === jobId)
      if (index !== -1) {
        jobList.value[index] = {
          ...jobList.value[index],
          ...detail,
          profile,
          detailFetched: true
        }
      }
    }
    
    // 跳转到详情页
    router.push({ path: '/job-detail', query: { id: jobId } })
  } catch (err) {
    console.error('获取岗位详情失败:', err)
    ElMessage.error('获取岗位详情失败，将跳转到基础详情页')
    router.push({ path: '/job-detail', query: { id: jobId } })
  }
}

// 获取岗位详情（按需加载）
const fetchJobDetail = async (jobId) => {
  try {
    const response = await axios.get(`${JOB_DETAIL_API_URL}${jobId}`, {
      timeout: 5000,
      headers: { 'Accept': 'application/json' }
    })
    return response.data || {}
  } catch (err) {
    console.error(`获取岗位${jobId}详情失败:`, err)
    return {}
  }
}

// 获取岗位画像（按需加载）
const fetchJobProfile = async (jobId) => {
  try {
    const response = await axios.get(`${JOB_PROFILE_API_URL}${jobId}/profile`, {
      timeout: 5000,
      headers: { 'Accept': 'application/json' }
    })
    return response.data || {}
  } catch (err) {
    console.error(`获取岗位${jobId}画像失败:`, err)
    return {}
  }
}

// 获取所有岗位分类
const fetchJobCategories = async () => {
  try {
    const response = await axios.get(JOB_CATEGORIES_API_URL, {
      timeout: 5000,
      headers: { 'Accept': 'application/json' }
    })
    return response.data || []
  } catch (err) {
    console.error('获取岗位分类失败:', err)
    return []
  }
}

const fetchAllJobData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const config = {
      timeout: 60000,
      headers: { 
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      withCredentials: false,
    }
    
    const token = localStorage.getItem('token')
    let allJobs = []
    let currentPage = 1
    const pageSize = 1000
    let hasMoreData = true
    let failedAttempts = 0 // 失败计数器
    const MAX_FAILED_ATTEMPTS = 5 // 最大失败次数
    const MAX_TOTAL_PAGES = 20 // 最大请求页数（防止无限循环）

    // 优化循环条件
    while (hasMoreData && currentPage <= MAX_TOTAL_PAGES && failedAttempts < MAX_FAILED_ATTEMPTS) {
      try {
        const params = new URLSearchParams()
        if (token) params.append('token', token)
        params.append('page', currentPage)
        params.append('size', pageSize)
        
        console.log(`正在请求第${currentPage}页数据...`)
        const response = await axios.get(`${ALL_JOBS_API_URL}?${params.toString()}`, config)
        
        // 统一数据处理
        let pageData = []
        if (Array.isArray(response.data)) {
          pageData = response.data
        } else if (response.data && Array.isArray(response.data.data)) {
          pageData = response.data.data
        }
        
        // 记录总条数（如果后端返回）
        const totalCount = response.data?.total || response.data?.count || 0
        console.log(`第${currentPage}页获取到${pageData.length}条数据，总计${totalCount}条`)
        
        if (pageData.length > 0) {
          allJobs = [...allJobs, ...pageData]
          failedAttempts = 0 // 重置失败计数器
          // 判断是否还有更多数据
          hasMoreData = pageData.length === pageSize && 
                        (totalCount === 0 || allJobs.length < totalCount)
        } else {
          hasMoreData = false
        }
        
        currentPage++
        await new Promise(resolve => setTimeout(resolve, 200)) // 增加延迟，减轻服务器压力
        
      } catch (pageError) {
        console.error(`获取第${currentPage}页数据失败:`, pageError)
        failedAttempts++
        currentPage++
        
        // 仅当连续失败次数达到上限时停止
        if (failedAttempts >= MAX_FAILED_ATTEMPTS) {
          ElMessage.warning(`连续${MAX_FAILED_ATTEMPTS}页请求失败，已停止获取更多数据`)
          hasMoreData = false
        }
      }
    }
    
    // 数据处理
    if (allJobs.length > 0) {
      const categories = await fetchJobCategories()
      
      const jobDataWithBasicInfo = allJobs.map(item => {
        // 原有数据处理逻辑保持不变
        const matchedCategory = categories.find(cat => cat.id === item.category_id)
        
        let jobType = '技术类'
        if (matchedCategory) {
          if (matchedCategory.name.includes('产品')) jobType = '产品类'
          else if (matchedCategory.name.includes('运营')) jobType = '运营类'
          else if (matchedCategory.name.includes('算法')) jobType = '算法类'
          else jobType = '技术类'
        } else if (item.type) {
          jobType = item.type
        }
        
        const salaryValue = calculateSalaryValue(item.salary_range || item.salary)
        
        return {
          id: item.id || Math.random().toString(36).substr(2, 9),
          company: item.company || '未知公司',
          companyShort: item.company?.substring(0, 2) || '未知',
          category: matchedCategory?.name || item.category || '其他',
          job_name: item.job_name || '未知岗位',
          type: jobType,
          salary_range: item.salary_range || item.salary || '面议',
          salaryValue,
          education: item.education || '本科及以上',
          experience: item.experience || '1-3年',
          date: item.date || '2026-03',
          detailFetched: false
        }
      })
      
      jobList.value = jobDataWithBasicInfo
      // 获取岗位名称列表（从已加载的数据中提取）
      await fetchJobNames()
      initCardAnimateStates()
    } else {
      error.value = '未获取到任何岗位数据，请检查后端接口'
      ElMessage.warning('接口返回空数据')
    }
  } catch (err) {
    // 原有错误处理逻辑保持不变
    console.error('获取岗位数据失败:', err)
    
    let errorMsg = ''
    if (err.code === 'ECONNREFUSED') {
      errorMsg = '加载失败：无法连接到后端服务器，请检查后端是否启动'
    } else if (err.code === 'ECONNABORTED') {
      errorMsg = '加载失败：请求超时，请检查网络或后端服务'
    } else if (err.message.includes('CORS') || err.message.includes('Access-Control')) {
      errorMsg = '加载失败：跨域请求被阻止，请配置后端CORS'
    } else {
      errorMsg = `加载失败：${err.message || '网络异常，请稍后重试'}`
    }
    
    error.value = errorMsg
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 筛选逻辑 - 修改为按岗位名称筛选
const filterJobName = ref('')

// 筛选并按薪资从高到低排序
const filteredJobList = computed(() => {
  // 复制原始数据，避免修改原数组
  let filtered = [...jobList.value]
  
  // 按岗位名称筛选
  if (filterJobName.value && filterJobName.value !== '') {
    filtered = filtered.filter(item => {
      return item.job_name === filterJobName.value
    })
  }
  
  // 按薪资从高到低排序
  filtered.sort((a, b) => {
    return b.salaryValue - a.salaryValue
  })
  
  return filtered
})

// ========== 分页功能核心逻辑 ==========
const pageSize = ref(10) // 每页显示10个岗位（5列×2行）
const currentPage = ref(1) // 当前页码

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(filteredJobList.value.length / pageSize.value)
})

// 计算当前页显示的岗位数据
const currentPageJobs = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredJobList.value.slice(startIndex, endIndex)
})

// 计算显示的页码范围（优化显示，只显示当前页前后2页）
const pageNumbers = computed(() => {
  const pages = []
  const total = totalPages.value
  
  // 如果总页数小于等于7，显示所有页码
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // 显示当前页前后2页，首页和尾页
    if (currentPage.value <= 3) {
      // 前3页，显示1-5和最后一页
      pages.push(1, 2, 3, 4, 5, -1, total)
    } else if (currentPage.value >= total - 2) {
      // 后3页，显示第一页和最后5页
      pages.push(1, -1, total - 4, total - 3, total - 2, total - 1, total)
    } else {
      // 中间页，显示首页、当前页前后2页、尾页
      pages.push(
        1, 
        -1, 
        currentPage.value - 2, 
        currentPage.value - 1, 
        currentPage.value, 
        currentPage.value + 1, 
        currentPage.value + 2, 
        -1, 
        total
      )
    }
  }
  
  return pages
})

// 切换页码
const changePage = (pageNum) => {
  if (pageNum < 1 || pageNum > totalPages.value || pageNum === currentPage.value) {
    return
  }
  currentPage.value = pageNum
  // 重新初始化动画状态
  initCardAnimateStates()
  // 滚动到岗位列表顶部
  const jobSection = document.querySelector('.job-section')
  if (jobSection) {
    jobSection.scrollIntoView({ behavior: 'smooth' })
  }
}

// 筛选时重置页码
const filterJobs = () => {
  currentPage.value = 1
  initCardAnimateStates()
}

// ========== 保留原有悬浮状态逻辑 ==========
const hoverCard = ref(null)
const hoverPortrait = ref(null)
const hoverJobCard = ref(null)

// ========== 保留原有其他功能逻辑 ==========
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
    ElMessage.success(`正在搜索：${keyword}`)
  } else {
    ElMessage.warning('请输入搜索关键词')
  }
}

// ========== 保留原有最适配十大岗位数据 ==========
const topTenJobs = ref([
  { jobName: '前端开发工程师', matchRate: 95, cover: 'https://picsum.photos/seed/top1/200/280' },
  { jobName: '产品经理', matchRate: 92, cover: 'https://picsum.photos/seed/top2/200/280' },
  { jobName: '数据分析师', matchRate: 89, cover: 'https://picsum.photos/seed/top3/200/280' },
  { jobName: 'UI设计师', matchRate: 87, cover: 'https://picsum.photos/seed/top4/200/280' },
  { jobName: 'Java开发工程师', matchRate: 85, cover: 'https://picsum.photos/seed/top5/200/280' },
  { jobName: '运营专员', matchRate: 83, cover: 'https://picsum.photos/seed/top6/200/280' },
  { jobName: 'AI算法工程师', matchRate: 81, cover: 'https://picsum.photos/seed/top7/200/280' },
  { jobName: '测试开发工程师', matchRate: 79, cover: 'https://picsum.photos/seed/top8/200/280' },
  { jobName: '嵌入式工程师', matchRate: 77, cover: 'https://picsum.photos/seed/top9/200/280' },
  { jobName: '游戏策划', matchRate: 75, cover: 'https://picsum.photos/seed/top10/200/280' }
])

// ========== 保留原有最适配十大岗位传送带逻辑 ==========
const sliderRef = ref(null)
const sliderOffset = ref(0)
let sliderTimer = null
const sliderSpeed = 0.1 

const startSlider = () => {
  sliderTimer = setInterval(() => {
    sliderOffset.value += sliderSpeed
    if (sliderOffset.value >= 100) {
      sliderOffset.value = 0
    }
  }, 30)
}

// ========== 保留原有岗位画像卡片区域逻辑 ==========
const portraitContainerRef = ref(null)
const portraitSectionRef = ref(null)
const jobContainerRef = ref(null)
const mousePos = ref({ x: 0, y: 0 })
const containerRect = ref({ left: 0, top: 0, width: 0, height: 0 })
const cardAnimateStates = ref([])
const jobCardAnimateStates = ref([])
const animateTimers = ref([])
const jobAnimateTimers = ref([])

// 保留原有岗位画像数据
const jobPortraitList = ref([
  {
    jobName: '数据分析师',
    skills: ['Python', 'SQL', 'Tableau', 'Excel'],
    cover: 'https://picsum.photos/seed/data-analyst/200/280'
  },
  {
    jobName: '前端开发工程师',
    skills: ['HTML/CSS', 'JavaScript', 'Vue', 'React'],
    cover: 'https://picsum.photos/seed/frontend-dev/200/280'
  },
  {
    jobName: '产品经理',
    skills: ['Axure', 'PRD', '用户调研', '数据分析'],
    cover: 'https://picsum.photos/seed/product-manager/200/280'
  },
  {
    jobName: 'UI设计师',
    skills: ['PS', 'AI', 'Figma', '交互设计'],
    cover: 'https://picsum.photos/seed/ui-designer/200/280'
  },
  {
    jobName: '电商运营',
    skills: ['淘宝运营', '数据分析', '文案写作'],
    cover: 'https://picsum.photos/seed/e-commerce/200/280'
  },
  {
    jobName: '后端开发工程师',
    skills: ['Java', 'SpringBoot', 'MySQL', 'Redis'],
    cover: 'https://picsum.photos/seed/backend-dev/200/280'
  },
  {
    jobName: '测试开发工程师',
    skills: ['Python', 'JUnit', 'Selenium', '接口测试'],
    cover: 'https://picsum.photos/seed/test-dev/200/280'
  },
  {
    jobName: '人工智能工程师',
    skills: ['Python', 'TensorFlow', 'PyTorch', '机器学习'],
    cover: 'https://picsum.photos/seed/ai-engineer/200/280'
  },
  {
    jobName: '运维开发工程师',
    skills: ['Linux', 'Docker', 'K8s', 'Shell'],
    cover: 'https://picsum.photos/seed/devops/200/280'
  },
  {
    jobName: '大数据开发工程师',
    skills: ['Hadoop', 'Spark', 'Hive', 'Java'],
    cover: 'https://picsum.photos/seed/bigdata-dev/200/280'
  },
  {
    jobName: '网络安全工程师',
    skills: ['渗透测试', '防火墙', '漏洞挖掘'],
    cover: 'https://picsum.photos/seed/security-engineer/200/280'
  },
  {
    jobName: '金融分析师',
    skills: ['Excel', 'SQL', '金融建模', '行业分析'],
    cover: 'https://picsum.photos/seed/finance-analyst/200/280'
  }
])

// 保留原有初始化卡片动画状态逻辑
const initCardAnimateStates = () => {
  cardAnimateStates.value = jobPortraitList.value.map(() => false)
  jobCardAnimateStates.value = currentPageJobs.value.map(() => false)
}

// 保留原有监听滚动触发动画逻辑
const handleScroll = () => {
  if (!portraitSectionRef.value) return
  
  const rect = portraitSectionRef.value.getBoundingClientRect()
  if (rect.top < window.innerHeight * 0.8 && !cardAnimateStates.value[0]) {
    startCardAnimation()
  }
  
  const jobRect = document.querySelector('.job-section').getBoundingClientRect()
  if (jobRect.top < window.innerHeight * 0.8 && !jobCardAnimateStates.value[0] && currentPageJobs.value.length > 0) {
    startJobCardAnimation()
  }
}

// 保留原有启动卡片动画逻辑
const startCardAnimation = () => {
  jobPortraitList.value.forEach((_, index) => {
    const timer = setTimeout(() => {
      cardAnimateStates.value[index] = true
    }, index * 150)
    animateTimers.value.push(timer)
  })
}

// 保留原有启动岗位卡片动画逻辑
const startJobCardAnimation = () => {
  currentPageJobs.value.forEach((_, index) => {
    const timer = setTimeout(() => {
      jobCardAnimateStates.value[index] = true
    }, index * 150)
    jobAnimateTimers.value.push(timer)
  })
}

// 保留原有鼠标移动事件逻辑
const handleMouseMove = (e) => {
  if (!portraitContainerRef.value) return
  const rect = portraitContainerRef.value.getBoundingClientRect()
  containerRect.value = rect
  mousePos.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
}

// 保留原有计算卡片样式逻辑
const getCardStyle = (index) => {
  const { x, y } = mousePos.value
  const { width, height } = containerRect.value
  if (!width || !height) return {}

  const col = index % 6
  const row = Math.floor(index / 6)
  const cardWidth = 200
  const cardHeight = 280
  const gapX = 60
  const gapY = 60
  
  const colOffset = col % 2 === 1 ? cardHeight / 2 : 0
  
  const baseX = (width - 6 * cardWidth - 5 * gapX) / 2 + col * (cardWidth + gapX)
  const baseY = row * (cardHeight + gapY) + colOffset

  const ratioX = x / width
  const ratioY = y / height
  const followX = -(ratioX - 0.5) * 300
  const followY = -(ratioY - 0.5) * 300

  return {
    left: `${baseX + followX}px`,
    top: `${baseY + followY}px`,
    transition: cardAnimateStates.value[index] ? 'all 0.3s ease' : 'none'
  }
}

// ========== 生命周期逻辑 ==========
onMounted(() => {
  startCarousel()
  startSlider()
  applyTheme()
  initCardAnimateStates()
  
  nextTick(() => {
    if (portraitContainerRef.value) {
      containerRect.value = portraitContainerRef.value.getBoundingClientRect()
    }
    window.addEventListener('scroll', handleScroll)
    handleScroll()
    
    // 调用优化后的获取岗位数据函数
    fetchAllJobData()
  })
})

onUnmounted(() => {
  clearInterval(carouselTimer)
  clearInterval(sliderTimer)
  animateTimers.value.forEach(timer => clearTimeout(timer))
  jobAnimateTimers.value.forEach(timer => clearTimeout(timer))
  window.removeEventListener('scroll', handleScroll)
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
  padding: 60px 0 0 0;
}

/* 用户头像和菜单样式 */
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

/* 顶部导航样式 */
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
.menu-item.active {
  color: #000;
}
.menu-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #2f54eb;
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

/* 导航栏右侧 */
.nav-right {
  display: flex;
  gap: 15px;
  align-items: center;
}
.nav-search-wrap {
  display: flex;
  width: 200px;
  height: 24px;
}
.nav-search-input {
  flex: 1;
  height: 100%;
  padding: 0 10px;
  border: 1px solid #e8e8e8;
  border-radius: 4px 0 0 4px;
  outline: none;
  font-size: 12px;
}
.nav-search-btn {
  width: 53px;
  height: 100%;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 12px;
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

/* 轮播Banner区样式 */
.banner-carousel {
  width: 100%;
  height: 320px;
  position: relative;
  overflow: hidden;
  margin-top: 0;
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

/* 功能模块样式 */
.function-modules {
  width: 100%;
  background: #fff;
  padding: 20px 0;
  border-bottom: 1px solid #e8e8e8;
}
.modules-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
}
.module-item {
  width: 33.33%;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  border-right: 1px solid #e8e8e8;
}
.module-item:last-child {
  border-right: none;
}
.module-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.module-title {
  font-size: 16px;
  color: #222;
  margin-bottom: 4px;
}
.module-desc {
  font-size: 14px;
  color: #999;
}
.module-arrow {
  font-size: 16px;
  color: #999;
}

/* 招聘岗位卡片区样式 */
.job-section {
  padding: 30px 0;
  background: #f8f9fa;
}
.job-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
}

/* 岗位信息标题 + 筛选栏样式 - 调整布局 */
.job-header {
  width: 100%;
  display: flex;
  flex-direction: column; /* 改为垂直布局 */
  align-items: flex-start; /* 左对齐 */
  margin-bottom: 20px;
  gap: 15px; /* 添加间距 */
}
.job-title-main {
  font-size: 24px;
  color: #222;
  font-weight: 600;
  margin: 0;
}
.job-filter {
  width: 100%; /* 占满宽度 */
  display: flex;
  justify-content: flex-start; /* 左对齐 */
}

/* 修改：岗位名称筛选标签样式（适配多标签换行） */
.filter-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap; /* 允许换行 */
  max-height: 120px; /* 限制最大高度，避免标签过多 */
  overflow-y: auto; /* 超出高度滚动 */
  padding: 5px;
  width: 100%;
}
.filter-tag {
  padding: 6px 15px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap; /* 防止标签文字换行 */
}
.filter-tag:hover {
  border-color: #2f54eb;
  color: #2f54eb;
}
.filter-tag.active {
  background: #2f54eb;
  color: #fff;
  border-color: #2f54eb;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #666;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2f54eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误提示样式 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #ff4d4f;
  gap: 15px;
}
.error-text {
  margin-bottom: 10px;
  font-size: 14px;
}
.reload-btn {
  padding: 8px 16px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.reload-btn:hover {
  background: #1d39c4;
}

/* 空数据样式 */
.empty-job-container {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #999;
}
.empty-text {
  font-size: 14px;
}

/* 岗位卡片容器 */
.job-card-container {
  width: 100%;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  padding: 20px 0;
  box-sizing: border-box;
}

/* 岗位卡片样式 */
.job-card {
  width: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
  cursor: pointer;
  transform: translateY(20px);
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: 1;
  box-sizing: border-box;
}

/* 岗位卡片飞入动画 */
.job-card.animate-in {
  transform: translateY(0);
  opacity: 1;
}

/* 岗位卡片悬浮效果 */
.job-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  z-index: 10;
}

/* 卡片图片容器 */
.card-image-wrap {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-bottom-left-radius: 50% 20%;
  border-bottom-right-radius: 50% 20%;
}
.portrait-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 左侧竖排文字 */
.vertical-text {
  position: absolute;
  top: 15px;
  left: 15px;
  display: flex;
  flex-direction: column;
  color: #000;
  font-size: 24px;
  font-weight: bold;
  line-height: 1.2;
}
.vertical-text .date {
  font-size: 16px;
  margin-top: 5px;
  font-weight: normal;
}

/* 悬浮时显示的岗位画像和薪资信息样式 */
.job-hover-info {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 5;
}
.job-portrait-tag {
  background: rgba(47, 84, 235, 0.9);
  color: #fff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  text-align: center;
  animation: fadeInUp 0.3s ease;
}
.job-salary-tag {
  background: rgba(255, 255, 255, 0.9);
  color: #2f54eb;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  animation: fadeInUp 0.4s ease;
}

/* 岗位卡片内容样式 */
.job-card-content {
  padding: 15px;
}
.job-card-content .job-title {
  font-size: 16px;
  font-weight: 600;
  color: #222;
  margin-bottom: 6px;
  line-height: 1.4;
}
.job-card-content .job-company {
  font-size: 14px;
  color: #999;
  line-height: 1.4;
}

/* 分页导航样式 */
.pagination-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
  gap: 15px;
}
.pagination-info {
  font-size: 14px;
  color: #666;
}
.pagination {
  display: flex;
  align-items: center;
  gap: 8px;
}
.page-btn {
  padding: 8px 15px;
  border: 1px solid #e8e8e8;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.2s ease;
}
.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
  color: #2f54eb;
  border-color: #2f54eb;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.page-number {
  width: 36px;
  height: 36px;
  border: 1px solid #e8e8e8;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.page-number:hover:not(.active) {
  border-color: #2f54eb;
  color: #2f54eb;
}
.page-number.active {
  background: #2f54eb;
  color: #fff;
  border-color: #2f54eb;
}
.page-ellipsis {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #ccc;
}


/* 最适配十大岗位 - 传送带样式 */
.top-ten-jobs-section {
  padding: 40px 0;
  background: #000;
  width: 100%;
}
.top-ten-jobs-section .section-header {
  width: 90%;
  max-width: 1400px;
  margin: 0 auto 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.top-ten-jobs-section .section-title {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}
/* 传送带容器 */
.slider-container {
  width: 100%;
  overflow: hidden;
  position: relative;
  height: 320px;
}
/* 传送带轨道 */
.slider-track {
  display: flex;
  gap: 20px;
  transition: none;
  will-change: transform;
}
/* 传送带卡片 */
.slider-card {
  width: 200px;
  height: 280px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.3s ease;
}
.slider-card:hover {
  transform: translateY(-8px) scale(1.05);
  box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}
.slider-card-cover {
  width: 100%;
  height: 220px;
  object-fit: cover;
}
.slider-card-info {
  padding: 12px;
}
.slider-card-title {
  font-size: 16px;
  font-weight: 600;
  color: #222;
  margin-bottom: 4px;
}
.slider-card-match {
  font-size: 14px;
  color: #2f54eb;
  font-weight: 500;
}

/* 岗位画像卡片区域样式 */
.job-portrait-card-section {
  padding: 40px 0;
  background: #f5f5f0;
  width: 100%;
}
.job-portrait-card-section .section-header {
  width: 90%;
  max-width: 1400px;
  margin: 0 auto 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.job-portrait-card-section .section-title {
  font-size: 24px;
  font-weight: 600;
  color: #000;
  margin: 0;
}
/* 容器高度适配6列瀑布流 */
.portrait-card-container {
  width: 100%;
  min-height: 800px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  padding: 20px 0;
}

/* 岗位画像卡片基础样式 */
.portrait-card {
  width: 200px;
  height: 280px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  overflow: hidden;
  cursor: pointer;
  position: absolute;
  transform: translateX(1000px) translateY(0);
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: 1;
}
/* 飞入动画激活状态 */
.portrait-card.animate-in {
  transform: translateX(0) translateY(0);
  opacity: 1;
}
/* 悬浮时浮起效果 */
.portrait-card:hover {
  transform: translateY(-12px) scale(1.05);
  box-shadow: 0 15px 30px rgba(0,0,0,0.2);
  z-index: 10;
}
/* 岗位名称提示框样式 */
.portrait-name-tooltip {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255,255,255,0.9);
  color: #000;
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 500;
  white-space: nowrap;
  z-index: 11;
  animation: fadeInUp 0.3s ease;
}

/* 通用动画 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 淡入上移动画 */
@keyframes fadeInUp {
  from { 
    opacity: 0; 
    transform: translate(-50%, 10px); 
  }
  to { 
    opacity: 1; 
    transform: translate(-50%, 0); 
  }
}

/* 页脚样式 */
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
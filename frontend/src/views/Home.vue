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

    <!-- 7. 招聘岗位卡片区（新增标题+筛选功能+调整悬浮详情位置） -->
    <section class="job-section">
      <div class="job-wrap">
        <!-- 新增：岗位信息标题 + 筛选栏 -->
        <div class="job-header">
          <h2 class="job-title-main">岗位信息</h2>
          <div class="job-filter">
            <!-- 新增：全部岗位筛选 -->
            <select v-model="filterJobType" class="filter-select" @change="filterJobs">
              <option value="">全部岗位</option>
              <option value="技术类">技术类</option>
              <option value="产品类">产品类</option>
              <option value="运营类">运营类</option>
              <option value="算法类">算法类</option>
            </select>
            <select v-model="filterEducation" class="filter-select" @change="filterJobs">
              <option value="">全部学历</option>
              <option value="大专及以上">大专及以上</option>
              <option value="本科及以上">本科及以上</option>
              <option value="硕士及以上">硕士及以上</option>
            </select>
            <select v-model="filterExperience" class="filter-select" @change="filterJobs">
              <option value="">全部经验</option>
              <option value="1-2年">1-2年</option>
              <option value="1-3年">1-3年</option>
              <option value="2-5年">2-5年</option>
              <option value="3-5年">3-5年</option>
            </select>
            <select v-model="filterSalary" class="filter-select" @change="filterJobs">
              <option value="">全部薪资</option>
              <option value="10K-20K">10K-20K</option>
              <option value="15K-30K">15K-30K</option>
              <option value="18K-35K">18K-35K</option>
              <option value="20K-40K">20K-40K</option>
              <option value="25K-50K">25K-50K</option>
            </select>
            <button class="filter-reset" @click="resetFilter">重置筛选</button>
          </div>
        </div>

        <!-- 岗位卡片列表 -->
        <div 
          class="job-card" 
          v-for="item in filteredJobList" 
          :key="item.id"
          @mouseenter="hoverCard = item.id"
          @mouseleave="hoverCard = null"
        >
          <!-- 默认显示区域 -->
          <div class="card-default">
            <div class="company-name">{{ item.company }}</div>
            <div class="job-title">{{ item.title }}</div>
          </div>
          
          <!-- 调整：悬浮详情移至卡片右下角独立显示（修复遮挡问题） -->
          <div class="card-detail" v-if="hoverCard === item.id">
            <div class="detail-item">
              <span class="label">岗位要求：</span>
              <span class="value">{{ item.requirement }}</span>
            </div>
            <div class="detail-item">
              <span class="label">薪资待遇：</span>
              <span class="value salary">{{ item.salary }}</span>
            </div>
            <div class="detail-item">
              <span class="label">学历要求：</span>
              <span class="value">{{ item.education }}</span>
            </div>
            <div class="detail-item">
              <span class="label">工作经验：</span>
              <span class="value">{{ item.experience }}</span>
            </div>
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
}

// ========== 主题切换逻辑 ==========
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
  if (!isImage) return
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) return
  const reader = new FileReader()
  reader.onload = (event) => {
    carouselList.value.push({ url: event.target.result })
    currentIndex.value = carouselList.value.length - 1
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

// ========== 招聘岗位数据 + 新增筛选逻辑 ==========
const jobList = ref([
  {
    id: 1,
    company: '腾讯科技',
    title: '前端开发工程师',
    type: '技术类', // 新增：岗位类型
    requirement: '熟练掌握Vue/React，熟悉工程化构建',
    salary: '15K-30K',
    education: '本科及以上',
    experience: '1-3年'
  },
  {
    id: 2,
    company: '阿里巴巴',
    title: '产品经理',
    type: '产品类', // 新增：岗位类型
    requirement: '具备需求分析能力，熟悉互联网产品流程',
    salary: '20K-40K',
    education: '本科及以上',
    experience: '2-5年'
  },
  {
    id: 3,
    company: '字节跳动',
    title: '数据分析师',
    type: '技术类', // 新增：岗位类型
    requirement: '掌握SQL/Python，熟悉数据可视化工具',
    salary: '18K-35K',
    education: '本科及以上',
    experience: '1-3年'
  },
  {
    id: 4,
    company: '华为',
    title: '嵌入式工程师',
    type: '技术类', // 新增：岗位类型
    requirement: '熟悉C/C++，掌握嵌入式开发流程',
    salary: '20K-40K',
    education: '本科及以上',
    experience: '2-5年'
  },
  {
    id: 5,
    company: '美团',
    title: '运营专员',
    type: '运营类', // 新增：岗位类型
    requirement: '具备活动策划能力，熟悉用户运营',
    salary: '10K-20K',
    education: '大专及以上',
    experience: '1-2年'
  },
  {
    id: 6,
    company: '京东',
    title: 'Java开发工程师',
    type: '技术类', // 新增：岗位类型
    requirement: '熟练掌握SpringBoot，熟悉微服务架构',
    salary: '18K-35K',
    education: '本科及以上',
    experience: '2-5年'
  },
  {
    id: 7,
    company: '百度',
    title: 'AI算法工程师',
    type: '算法类', // 新增：岗位类型
    requirement: '掌握机器学习算法，熟悉Python/TensorFlow',
    salary: '25K-50K',
    education: '硕士及以上',
    experience: '3-5年'
  },
  {
    id: 8,
    company: '网易',
    title: '游戏策划',
    type: '产品类', // 新增：岗位类型
    requirement: '具备游戏设计思维，熟悉游戏开发流程',
    salary: '15K-30K',
    education: '本科及以上',
    experience: '1-3年'
  }
])

// 新增：筛选条件（新增岗位类型筛选）
const filterJobType = ref('')
const filterEducation = ref('')
const filterExperience = ref('')
const filterSalary = ref('')

// 新增：筛选后的岗位列表（计算属性，增加岗位类型筛选）
const filteredJobList = computed(() => {
  return jobList.value.filter(item => {
    const typeMatch = filterJobType.value ? item.type === filterJobType.value : true
    const educationMatch = filterEducation.value ? item.education === filterEducation.value : true
    const experienceMatch = filterExperience.value ? item.experience === filterExperience.value : true
    const salaryMatch = filterSalary.value ? item.salary === filterSalary.value : true
    return typeMatch && educationMatch && experienceMatch && salaryMatch
  })
})

// 新增：筛选方法
const filterJobs = () => {
  // 依赖计算属性自动筛选，无需额外逻辑
}

// 新增：重置筛选（包含岗位类型）
const resetFilter = () => {
  filterJobType.value = ''
  filterEducation.value = ''
  filterExperience.value = ''
  filterSalary.value = ''
}

// ========== 悬浮状态 ==========
const hoverCard = ref(null)
const hoverPortrait = ref(null) // 岗位画像悬浮状态

// ========== 其他功能逻辑 ==========
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

// ========== 新增：最适配十大岗位数据 ==========
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

// ========== 新增：最适配十大岗位传送带逻辑 ==========
const sliderRef = ref(null)
const sliderOffset = ref(0)
let sliderTimer = null
// 修改：速度从0.5减慢到0.1（等效慢2秒）
const sliderSpeed = 0.1 

const startSlider = () => {
  sliderTimer = setInterval(() => {
    sliderOffset.value += sliderSpeed
    // 当移动到一半时（即复制的那份数据开始时），重置偏移量实现无缝循环
    if (sliderOffset.value >= 100) {
      sliderOffset.value = 0
    }
  }, 30)
}

// ========== 新增：岗位画像卡片区域逻辑（番茄小说网瀑布流排版） ==========
const portraitContainerRef = ref(null)
const portraitSectionRef = ref(null) // 新增：岗位画像区域引用
const mousePos = ref({ x: 0, y: 0 })
const containerRect = ref({ left: 0, top: 0, width: 0, height: 0 })
// 新增：卡片动画状态（控制逐个飞入）
const cardAnimateStates = ref([])
// 新增：动画定时器数组（用于清理）
const animateTimers = ref([])

// 岗位画像数据（带封面图）
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

// 新增：初始化卡片动画状态
const initCardAnimateStates = () => {
  cardAnimateStates.value = jobPortraitList.value.map(() => false)
}

// 新增：监听滚动，实现滚动到区域时触发动画
const handleScroll = () => {
  if (!portraitSectionRef.value) return
  
  const rect = portraitSectionRef.value.getBoundingClientRect()
  // 当区域进入视口（顶部距离小于窗口高度的80%）
  if (rect.top < window.innerHeight * 0.8 && !cardAnimateStates.value[0]) {
    startCardAnimation()
    // 只执行一次，移除监听
    window.removeEventListener('scroll', handleScroll)
  }
}

// 新增：启动卡片逐个飞入动画
const startCardAnimation = () => {
  jobPortraitList.value.forEach((_, index) => {
    const timer = setTimeout(() => {
      cardAnimateStates.value[index] = true
    }, index * 150) // 每个卡片间隔150ms飞入
    animateTimers.value.push(timer)
  })
}

// 鼠标移动事件：更新鼠标位置
const handleMouseMove = (e) => {
  if (!portraitContainerRef.value) return
  const rect = portraitContainerRef.value.getBoundingClientRect()
  containerRect.value = rect
  mousePos.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
}

// 计算每个卡片的偏移样式（番茄小说网瀑布流排版+反向鼠标跟随）
const getCardStyle = (index) => {
  const { x, y } = mousePos.value
  const { width, height } = containerRect.value
  if (!width || !height) return {}

  // 番茄小说网瀑布流排版：6列布局，错落排列
  const col = index % 6 // 0-5列
  const row = Math.floor(index / 6) // 行号
  const cardWidth = 200 // 卡片宽度
  const cardHeight = 280 // 卡片高度
  const gapX = 60 // 列间距增大三倍（从20改为60）
  const gapY = 60 // 行间距增大三倍（从20改为60）
  
  // 错落布局：偶数列向下偏移半个卡片高度，模拟番茄小说网排版
  const colOffset = col % 2 === 1 ? cardHeight / 2 : 0
  
  // 基础位置：6列均匀分布+水平居中+错落排版
  const baseX = (width - 6 * cardWidth - 5 * gapX) / 2 + col * (cardWidth + gapX)
  const baseY = row * (cardHeight + gapY) + colOffset

  // 反向鼠标跟随：鼠标下移卡片上移，鼠标右移卡片左移（取反）
  const ratioX = x / width
  const ratioY = y / height
  const followX = -(ratioX - 0.5) * 300 // 取反实现反向移动
  const followY = -(ratioY - 0.5) * 300 // 取反实现反向移动

  return {
    left: `${baseX + followX}px`,
    top: `${baseY + followY}px`,
    transition: cardAnimateStates.value[index] ? 'all 0.3s ease' : 'none'
  }
}

// ========== 生命周期 ==========
onMounted(() => {
  startCarousel()
  startSlider() // 启动传送带
  applyTheme()
  initCardAnimateStates() // 初始化卡片动画状态
  
  nextTick(() => {
    if (portraitContainerRef.value) {
      containerRect.value = portraitContainerRef.value.getBoundingClientRect()
    }
    // 添加滚动监听，实现滚动到区域时触发动画
    window.addEventListener('scroll', handleScroll)
    // 立即检查一次，避免页面加载时已经在区域内
    handleScroll()
  })
})

onUnmounted(() => {
  clearInterval(carouselTimer)
  clearInterval(sliderTimer) // 清理传送带定时器
  // 清理卡片动画定时器
  animateTimers.value.forEach(timer => clearTimeout(timer))
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 全局容器 - 新增顶部内边距，避免内容被固定导航栏遮挡 */
.career-home {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f8f9fa;
  margin: 0;
  padding: 60px 0 0 0; /* 顶部padding等于导航栏高度，避免内容被遮挡 */
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
  z-index: 9999; /* 提高层级确保显示在最上层 */
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

/* 1. 顶部导航样式 - 核心修改：固定在顶部 */
.top-nav {
  height: 60px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  width: 100%;
  /* 核心修改：固定定位 */
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999; /* 最高层级，确保不被其他元素遮挡 */
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
  z-index: 9999; /* 提高层级 */
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

/* 导航栏右侧 - 整合搜索框 */
.nav-right {
  display: flex;
  gap: 15px;
  align-items: center;
}
.nav-search-wrap {
  display: flex;
  width: 300px;
  height: 36px;
}
.nav-search-input {
  flex: 1;
  height: 100%;
  padding: 0 15px;
  border: 1px solid #e8e8e8;
  border-radius: 4px 0 0 4px;
  outline: none;
  font-size: 14px;
}
.nav-search-btn {
  width: 80px;
  height: 100%;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 14px;
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

/* 2. 轮播Banner区样式 - 调整顶部间距，移除负边距 */
.banner-carousel {
  width: 100%;
  height: 320px;
  position: relative;
  overflow: hidden;
  margin-top: 0; /* 移除负边距，避免被导航栏遮挡 */
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

/* 调整：轮播图下方功能模块样式（番茄小说网风格） */
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

/* 新增：招聘岗位卡片区样式（含标题、筛选、调整悬浮详情） */
.job-section {
  padding: 30px 0;
}
.job-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

/* 新增：岗位信息标题 + 筛选栏样式 */
.job-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.job-title-main {
  font-size: 24px;
  color: #222;
  font-weight: 600;
  margin: 0;
}
.job-filter {
  display: flex;
  gap: 15px;
  align-items: center;
}
.filter-select {
  padding: 8px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  outline: none;
  font-size: 14px;
  color: #333;
}
.filter-reset {
  padding: 8px 15px;
  border: 1px solid #e8e8e8;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}
.filter-reset:hover {
  background: #f5f7fa;
}

/* 岗位卡片样式（修复遮挡核心：提升层级 + 调整布局） */
.job-card {
  width: calc(25% - 15px);
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: visible; /* 确保悬浮框不被裁剪 */
  z-index: 1; /* 基础层级 */
}
/* 悬浮时提升卡片层级，确保弹窗在最上层 */
.job-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.15);
  z-index: 100; /* 悬浮时提升层级，高于其他卡片 */
}
.card-default {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.company-name {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
.job-title {
  font-size: 16px;
  color: #222;
  font-weight: 600;
}

/* 调整：悬浮详情移至卡片右下角独立显示（修复遮挡问题） */
.card-detail {
  position: absolute;
  bottom: -140px; /* 定位到卡片下方 */
  right: 0; /* 靠右对齐 */
  width: 220px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 101; /* 弹窗层级高于卡片 */
  animation: fadeIn 0.2s ease;
  /* 防止弹窗超出容器 */
  pointer-events: auto;
}
/* 修复最后一行卡片弹窗超出问题 */
.job-wrap > .job-card:nth-child(n+9) .card-detail {
  bottom: auto;
  top: -140px;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.detail-item {
  display: flex;
  align-items: flex-start;
  font-size: 13px;
  line-height: 1.4;
}
.label {
  color: #666;
  min-width: 70px;
  flex-shrink: 0;
}
.value {
  color: #333;
  flex: 1;
}
.salary {
  color: #ff4d4f;
  font-weight: 600;
}

/* ========== 新增：最适配十大岗位 - 传送带样式 ========== */
.top-ten-jobs-section {
  padding: 40px 0;
  /* 修改：背景改为黑色 */
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
  /* 修改：文字改为白色适配黑色背景 */
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
/* 传送带轨道 - 实现无缝循环 */
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

/* ========== 核心修改：岗位画像卡片区域样式（番茄小说网瀑布流排版+黑色背景） ========== */
.job-portrait-card-section {
  padding: 40px 0;
  /* 修改：背景改为米白色 */
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
  /* 修改：文字改为黑色适配米白色背景 */
  color: #000;
  margin: 0;
}
/* 容器高度适配6列瀑布流（增大高度适配更大间距） */
.portrait-card-container {
  width: 100%;
  min-height: 800px; /* 增大容器高度适配更大间距 */
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  padding: 20px 0;
}
/* 岗位画像卡片基础样式（新增飞入动画） */
.portrait-card {
  width: 200px;
  height: 280px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  overflow: hidden;
  cursor: pointer;
  position: absolute;
  /* 初始状态：右侧外 + 透明 */
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
/* 悬浮时浮起效果（叠加在飞入动画上） */
.portrait-card:hover {
  transform: translateY(-12px) scale(1.05);
  box-shadow: 0 15px 30px rgba(0,0,0,0.2);
  z-index: 10;
}
.portrait-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
@keyframes fadeInUp {
  from { opacity: 0; transform: translate(-50%, 10px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

/* 7. 页脚样式 */
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
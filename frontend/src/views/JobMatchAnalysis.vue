<template>
  <div class="job-match-page">
    <!-- 统一样式的顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item active" @click="$router.push('/match-result')">人岗匹配</li>
            <li class="menu-item" @click="$router.push('/student-ability')">能力画像</li>
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
                  <span class="color-dot blue"></span> 匹配报告导出
                </li>
              </ul>
            </li>
          </ul>
        </div>
        <div class="nav-right">
          <div class="nav-search-wrap">
            <input type="text" class="nav-search-input" placeholder="搜索目标岗位/首字母..." @keyup.enter="handleSearch" v-model="searchKeyword" />
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

    <!-- 核心内容区域 -->
    <div class="match-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>岗位信息</h1>
      </div>

      <!-- 新增：推荐岗位板块 -->
      <div class="recommended-jobs-section">
        <div class="section-header">
          <h2>为你推荐的适配岗位</h2>
          <span class="match-rate-tip">基于你的能力画像，匹配度 {{recommendMatchRate}}%</span>
        </div>
        
        <div class="recommended-jobs-list">
          <div 
            class="recommended-job-card" 
            v-for="job in recommendedJobs" 
            :key="job.id"
            :class="{ active: selectedJob.id === job.id }"
            @click="selectJob(job)"
          >
            <div class="match-rate-badge">
              {{ job.predictedMatch }}%
            </div>
            <div class="job-image">
              <img :src="job.image || 'https://picsum.photos/seed/' + job.id + '/400/250'" alt="岗位背景" />
            </div>
            <div class="job-info">
              <div class="job-location-date">
                <span class="location">{{ job.city }}</span>
                <span class="date">{{ job.date }}</span>
              </div>
              <h4 class="job-name">{{ job.name }}</h4>
              <p class="company">{{ job.company }}</p>
              <div class="match-tag">
                <span>匹配度：{{ job.predictedMatch }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 所有岗位选择 -->
      <div class="all-job-selection">
        <h3>所有岗位列表</h3>
        <!-- 岗位分类标签栏 -->
        <div class="job-category-tabs">
          <div 
            class="tab-item" 
            :class="{ active: activeCategory === '全部岗位' }"
            @click="activeCategory = '全部岗位'"
          >
            全部岗位
          </div>
          <div 
            v-for="cat in categoryList" 
            :key="cat"
            class="tab-item"
            :class="{ active: activeCategory === cat }"
            @click="activeCategory = cat"
          >
            {{ cat }}
          </div>
        </div>
        <!-- 搜索框 -->
        <div class="search-wrap">
          <input 
            type="text" 
            v-model="allJobsSearchKeyword"
            placeholder="搜索所有岗位..." 
            class="all-jobs-search-input"
            @keyup.enter="handleAllJobsSearch"
          />
          <button class="all-jobs-search-btn" @click="handleAllJobsSearch">搜索</button>
        </div>
        <div class="job-card-list">
          <div 
            class="job-card" 
            v-for="job in filteredAllJobs" 
            :key="job.id"
            :class="{ active: selectedJob.id === job.id }"
            @click="selectJob(job)"
          >
            <div class="job-image">
              <img :src="job.image || 'https://picsum.photos/seed/' + job.id + '/400/250'" alt="岗位背景" />
              <div class="job-overlay" v-if="job.salary">
                <span class="salary">{{ job.salary }}</span>
                <span class="portrait-tag">岗位画像</span>
              </div>
            </div>
            <div class="job-info">
              <div class="job-location-date">
                <span class="location">{{ job.city }}</span>
                <span class="date">{{ job.date }}</span>
              </div>
              <h4 class="job-name">{{ job.name }}</h4>
              <p class="company">{{ job.company }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 开始人岗匹配按钮 - 移到最下方并居中 -->
      <div class="match-action-bar">
        <el-button type="primary" size="large" @click="startJobMatch">
          开始人岗匹配
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

// 路由实例
const router = useRouter()
const route = useRoute()

// ========== 导航栏相关 ==========
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')
const searchKeyword = ref('') // 顶部搜索关键词

// 导航栏方法
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
  ElMessage.info('已切换为' + (darkMode.value ? '暗黑' : '亮色') + '模式')
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

// 拼音首字母匹配函数
const getFirstLetter = (str) => {
  const pyMap = {
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G',
    'H': 'H', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N', 'P': 'P',
    'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
    'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G',
    'h': 'H', 'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'p': 'P',
    'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z'
  }
  
  const chineseFirstLetter = (char) => {
    const charCode = char.charCodeAt(0)
    if (charCode >= 19968 && charCode <= 40869) {
      const index = Math.floor((charCode - 19968) / 94)
      const letters = 'ABCDEFGHJKLMNOPQRSTWXYZ'
      return letters[index] || ''
    }
    return ''
  }
  
  for (let i = 0; i < str.length; i++) {
    const char = str.charAt(i)
    if (pyMap[char]) {
      return pyMap[char]
    } else if (/[\u4e00-\u9fa5]/.test(char)) {
      return chineseFirstLetter(char)
    }
  }
  return ''
}

// 处理顶部搜索
const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    ElMessage.warning('请输入搜索关键词或首字母')
    return
  }
  
  let matchedJobs = []
  const firstLetter = getFirstLetter(keyword)
  if (firstLetter) {
    matchedJobs = allJobs.value.filter(job => {
      const jobFirstLetter = getFirstLetter(job.name)
      return jobFirstLetter === firstLetter
    })
  }
  
  if (matchedJobs.length === 0) {
    matchedJobs = allJobs.value.filter(job => 
      job.name.includes(keyword) || job.tags.some(tag => tag.includes(keyword))
    )
  }
  
  if (matchedJobs.length > 0) {
    selectJob(matchedJobs[0])
    ElMessage.success(`找到 ${matchedJobs.length} 个匹配岗位，已选中第一个：${matchedJobs[0].name}`)
  } else {
    ElMessage.warning('未找到包含"' + keyword + '"或对应首字母的岗位')
  }
  searchKeyword.value = ''
}

// ========== 核心业务逻辑 ==========
// 检查是否有能力画像数据
const hasAbilityProfile = ref(false)

// 岗位分类
const categoryList = ref([
  'APP推广', 'BD经理', 'C/C++', 'Java', '产品专员/助理', '储备干部', '储备经理人',
  '内容审核', '前端开发', '咨询顾问', '售后客服', '商务专员', '培训师', '大客户代表',
  '实施工程师', '广告销售', '律师', '律师助理', '总助/CEO助理/董事长助理',
  '技术支持工程师', '招聘专员/助理', '日语翻译', '档案管理', '法务专员/助理',
  '测试工程师', '游戏推广', '游戏运营', '猎头顾问', '电话客服', '电话销售',
  '知识产权/专利代理', '硬件测试'
])
const activeCategory = ref('全部岗位')

// 所有岗位数据
const allJobs = ref([
  { id: 1, name: '前端开发', icon: '🌐', city: '东莞', area: '其他', date: '2026-03', company: '东莞市恒亚罗斯计算机科技有限公司', tags: ['前端', 'Vue', 'React'], predictedMatch: 75, salary: '', image: 'https://picsum.photos/seed/forest/400/250' },
  { id: 2, name: '实施工程师', icon: '🔧', city: '广东', area: '其他', date: '2026-03', company: '广东南方数码科技股份有限公司', tags: ['全栈', '实施'], predictedMatch: 80, salary: '', image: 'https://picsum.photos/seed/mountain/400/250' },
  { id: 3, name: '科研人员', icon: '🔬', city: '河南', area: '其他', date: '2026-03', company: '河南二建集团', tags: ['科研'], predictedMatch: 82, salary: '1-1.3万', image: 'https://picsum.photos/seed/waterfall/400/250' },
  { id: 4, name: '科研人员', icon: '🔬', city: '香港', area: '其他', date: '2026-03', company: '香港中文大学深圳研究院', tags: ['科研'], predictedMatch: 82, salary: '', image: 'https://picsum.photos/seed/pool/400/250' },
  { id: 5, name: '科研人员', icon: '🔬', city: '成都', area: '其他', date: '2026-03', company: '成都新朝阳作物科学股份有限公司', tags: ['科研'], predictedMatch: 82, salary: '', image: 'https://picsum.photos/seed/pool2/400/250' },
  { id: 6, name: '技术支持工程师', icon: '🛠️', city: '昆山', area: '其他', date: '2026-03', company: '昆山华海环保科技有限公司', tags: ['技术支持'], predictedMatch: 76, salary: '', image: 'https://picsum.photos/seed/mountain2/400/250' },
  { id: 7, name: '技术支持工程师', icon: '🛠️', city: '唐山', area: '其他', date: '2026-03', company: '唐山松下产业机器有限公司', tags: ['技术支持'], predictedMatch: 76, salary: '', image: 'https://picsum.photos/seed/mountain3/400/250' },
  { id: 8, name: '实施工程师', icon: '🔧', city: '安科', area: '其他', date: '2026-03', company: '安科瑞', tags: ['全栈', '实施'], predictedMatch: 80, salary: '', image: 'https://picsum.photos/seed/bird/400/250' },
  { id: 9, name: 'Java', icon: '☕', city: '济南', area: '其他', date: '2026-03', company: '济南北海软件工程有限公司', tags: ['后端', 'Java'], predictedMatch: 85, salary: '', image: 'https://picsum.photos/seed/snow/400/250' },
  { id: 10, name: '软件测试', icon: '🧪', city: '源创', area: '其他', date: '2026-03', company: '源创客成都科技有限公司', tags: ['测试'], predictedMatch: 83, salary: '', image: 'https://picsum.photos/seed/field/400/250' }
])

// 新增：推荐岗位相关
const recommendMatchRate = ref(82) // 整体匹配度
// 计算属性：获取匹配度最高的8个岗位作为推荐岗位（正好两行，每行4个）
const recommendedJobs = computed(() => {
  // 按匹配度降序排序，取前8个（两行，每行4个）
  return [...allJobs.value]
    .sort((a, b) => b.predictedMatch - a.predictedMatch)
    .slice(0, 8)
})

// 所有岗位搜索关键词
const allJobsSearchKeyword = ref('')

// 过滤后的所有岗位（支持搜索和分类）
const filteredAllJobs = computed(() => {
  let list = allJobs.value
  
  // 按分类过滤
  if (activeCategory.value !== '全部岗位') {
    list = list.filter(job => job.tags.includes(activeCategory.value) || job.name.includes(activeCategory.value))
  }
  
  // 按搜索关键词过滤
  if (allJobsSearchKeyword.value) {
    const keyword = allJobsSearchKeyword.value.trim()
    const firstLetter = getFirstLetter(keyword)
    
    list = list.filter(job => {
      const jobFirstLetter = getFirstLetter(job.name)
      return (firstLetter && jobFirstLetter === firstLetter) || 
             job.name.includes(keyword) || 
             job.tags.some(tag => tag.includes(keyword))
    })
  }
  
  return list
})

// 选中的岗位
const selectedJobId = ref('')
const selectedJob = ref({})

// 选择岗位
const selectJob = (job) => {
  selectedJob.value = job
  selectedJobId.value = job.id
  ElMessage.info(`已选中岗位：${job.name} - ${job.company}`)
}

// 处理所有岗位搜索
const handleAllJobsSearch = () => {
  const keyword = allJobsSearchKeyword.value.trim()
  if (!keyword) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  ElMessage.success(`搜索关键词：${keyword}，共找到 ${filteredAllJobs.value.length} 个匹配岗位`)
}

// 开始人岗匹配
const startJobMatch = () => {
  if (!hasAbilityProfile.value) {
    ElMessage.warning('请先完成能力画像测评，才能进行人岗匹配！')
    router.push('/student-ability')
    return
  }
  ElMessage.success('正在为您生成最佳匹配岗位...')
  router.push('/match-result')
}

// 页面初始化
onMounted(() => {
  if (!localStorage.getItem('abilityProfile')) {
    localStorage.setItem('abilityProfile', JSON.stringify({
      dimensions: {
        professionalSkill: { score: 85 },
        communication: { score: 88 },
        internship: { score: 82 },
        learning: { score: 92 }
      }
    }))
  }
  hasAbilityProfile.value = !!localStorage.getItem('abilityProfile')
  
  if (route.query.jobId) {
    const jobId = parseInt(route.query.jobId)
    const job = allJobs.value.find(item => item.id === jobId)
    if (job) {
      selectJob(job)
    }
  }
})
</script>

<style scoped>
/* 全局样式 */
.job-match-page {
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: #fff;
  margin: 0;
  padding: 60px 0 0 0;
  color: #1a2639;
}

/* ========== 导航栏样式（统一样式） ========== */
.top-nav {
  height: 60px;
  background: #ffffff;
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

/* ========== 核心内容样式 ========== */
.match-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

/* 页面标题 */
.page-header {
  margin-bottom: 20px;
}
.page-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

/* 新增：推荐岗位样式 */
.recommended-jobs-section {
  background: #f8f9ff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  /* 增大推荐岗位板块尺寸 */
  min-height: 600px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}
.match-rate-tip {
  font-size: 14px;
  color: #2f54eb;
  background: #e6f7ff;
  padding: 4px 12px;
  border-radius: 16px;
}
.recommended-jobs-list {
  /* 修改为每行4个，固定网格布局 */
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px; /* 增大间距 */
  /* 调整高度，确保内容不被遮挡 */
  max-height: 500px;
  overflow: hidden;
}
.recommended-job-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  /* 增大卡片尺寸 */
  width: 100%;
  height: 220px;
}
.recommended-job-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.recommended-job-card.active {
  border: 2px solid #2f54eb;
}
.match-rate-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #2f54eb;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  z-index: 1;
  /* 增加背景透明度，避免完全遮挡 */
  background: rgba(47, 84, 235, 0.9);
}
.recommended-job-card .job-image {
  width: 100%;
  height: 130px; /* 增大图片区域 */
  overflow: hidden;
}
.recommended-job-card .job-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.recommended-job-card .job-info {
  padding: 12px;
}
.recommended-job-card .job-location-date {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}
.recommended-job-card .job-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}
.recommended-job-card .company {
  font-size: 12px;
  color: #64748b;
  margin: 0 0 6px 0;
}
.recommended-job-card .match-tag {
  font-size: 11px;
  color: #52c41a;
}

/* 所有岗位选择 */
.all-job-selection {
  background: #f8f9ff; /* 增加背景色 */
  border-radius: 16px; /* 圆角 */
  padding: 24px; /* 内边距 */
  margin-top: 0;
  margin-bottom: 40px; /* 增加底部间距，为按钮留出空间 */
  box-shadow: 0 2px 8px rgba(0,0,0,0.05); /* 阴影效果 */
}
.all-job-selection h3 {
  font-size: 20px; /* 增大标题字号 */
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8; /* 增加下划线 */
}
/* 岗位分类标签栏 */
.job-category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  max-height: 80px; /* 减小高度 */
  overflow-y: auto;
}
.tab-item {
  padding: 6px 14px;
  border-radius: 20px;
  background: #f5f7fa;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
}
.tab-item:hover {
  background: #e8e8e8;
}
.tab-item.active {
  background: #2f54eb;
  color: #fff;
}
.search-wrap {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
.all-jobs-search-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border 0.3s ease;
}
.all-jobs-search-input:focus {
  border-color: #2f54eb;
}
.all-jobs-search-btn {
  padding: 10px 20px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}
.all-jobs-search-btn:hover {
  background: #1d39c4;
}
.job-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 20px;
  /* 限制只显示两行 */
  max-height: calc((220px + 20px) * 2);
  overflow: hidden;
}
.job-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  height: 220px; /* 固定卡片高度 */
}
.job-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.job-card.active {
  border: 2px solid #2f54eb;
}
.job-image {
  position: relative;
  width: 100%;
  height: 130px;
  overflow: hidden;
}
.job-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.job-overlay {
  position: absolute;
  bottom: 10px;
  left: 10px;
  right: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.salary {
  background: rgba(0,0,0,0.6);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.portrait-tag {
  background: #2f54eb;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.job-info {
  padding: 12px;
}
.job-location-date {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}
.job-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 6px 0;
}
.company {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* 人岗匹配按钮栏 - 修改为居中显示，放在页面最下方 */
.match-action-bar {
  margin-top: 40px;
  margin-bottom: 60px;
  text-align: center; /* 按钮居中 */
}
.match-action-bar .el-button {
  padding: 12px 40px; /* 增大按钮尺寸 */
  font-size: 16px;
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .nav-menu { display: none; }
  .nav-wrap { width: 95%; }
  .match-container { padding: 20px 15px; }
  /* 移动端推荐岗位改为每行2个 */
  .recommended-jobs-list {
    grid-template-columns: repeat(2, 1fr);
  }
  .job-card-list { 
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    max-height: calc((200px + 15px) * 2);
  }
  .job-card { height: 200px; }
  .recommended-job-card { height: 200px; }
  .search-wrap { flex-direction: column; }
  .section-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .recommended-jobs-section { min-height: auto; }
}
</style>
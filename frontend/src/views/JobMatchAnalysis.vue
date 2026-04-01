<template>
  <div class="job-match-page">
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item active" @click="$router.push('/career-planning-intro')">职业规划</li>
            <li class="menu-item" @click="$router.push('/report-export')">报告导出</li>
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
            <img :src="userAvatar || 'https://picsum.photos/seed-avatar/40/40'" alt="头像" class="avatar" @click="toggleUserMenu" />
            <div class="user-menu" v-show="isUserMenuOpen">
              <div class="menu-item" @click="$router.push('/profile')">个人中心</div>
              <div class="menu-item" @click="$router.push('/settings')">账号设置</div>
              <div class="menu-item logout" @click="handleLogout">退出登录</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="match-container">
      <div class="page-header">
        <h1>岗位信息</h1>
      </div>

      <div class="recommended-jobs-section">
        <div class="section-header">
          <h2>为你推荐的适配岗位</h2>
          <span class="match-rate-tip">基于大模型能力画像智能推荐</span>
        </div>
        
        <div class="recommended-jobs-list">
          <div 
            class="recommended-job-card" 
            v-for="(job,index) in recommendedJobs" 
            :key="job.id"
            :class="{ active: selectedJob.id === job.id }"
            @click="selectJob(job)"
          >
            <div class="card-corner" :style="getCornerStyle(index)"></div>
            
            <div class="match-rate-badge">
              {{ job.overall_score }}%
            </div>
            <div class="job-info">
              <h4 class="job-name">{{ job.job_name }}</h4>
              <div class="match-tag">
                <span>匹配度：{{ job.overall_score }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="all-job-selection">
        <h3>所有岗位列表</h3>
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
            v-for="(job,idx) in uniqueFilteredJobs" 
            :key="job.id"
            :class="{ active: selectedJob.id === job.id }"
            @click="selectJob(job)"
            :style="getCardColor(idx)"
          >
            <h4 class="job-name">{{ job.job_name }}</h4>
          </div>
        </div>
      </div>

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
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')
const searchKeyword = ref('')

const hasAbilityProfile = ref(false)
const categoryList = ref([])
const activeCategory = ref('全部岗位')
const allJobs = ref([])
const allJobsSearchKeyword = ref('')
const selectedJob = ref({})

const recommendedJobs = ref([
  { id: 1, job_name: '后端开发工程师', overall_score: 92 },
  { id: 2, job_name: 'Java开发工程师', overall_score: 88 },
  { id: 3, job_name: 'Python开发工程师', overall_score: 85 },
  { id: 4, job_name: '全栈开发工程师', overall_score: 82 },
  { id: 5, job_name: '软件开发工程师', overall_score: 80 },
  { id: 6, job_name: '大数据开发工程师', overall_score: 78 },
  { id: 7, job_name: '云计算工程师', overall_score: 75 },
  { id: 8, job_name: '微服务开发工程师', overall_score: 72 }
])

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

const getFirstLetter = (str) => {
  const pyMap = {'A':'A','B':'B','C':'C','D':'D','E':'E','F':'F','G':'G','H':'H','J':'J','K':'K','L':'L','M':'M','N':'N','P':'P','Q':'Q','R':'R','S':'S','T':'T','W':'W','X':'X','Y':'Y','Z':'Z'}
  const chineseFirstLetter = (char) => {
    const charCode = char.charCodeAt(0)
    if(charCode >= 19968 && charCode <= 40869) {
      const index = Math.floor((charCode-19968)/94)
      const letters = 'ABCDEFGHJKLMNOPQRSTWXYZ'
      return letters[index] || ''
    }
    return ''
  }
  for(let i=0;i<str.length;i++){
    const char = str.charAt(i).toUpperCase()
    if(pyMap[char]) return pyMap[char]
    if(/[\u4e0-\u9fa5]/.test(char)) return chineseFirstLetter(char)
  }
  return ''
}
const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  if(!keyword) { ElMessage.warning('请输入关键词'); return }
  let matched = allJobs.value.filter(j=>getFirstLetter(j.job_name)===getFirstLetter(keyword))
  if(matched.length===0) matched = allJobs.value.filter(j=>j.job_name.includes(keyword))
  if(matched.length>0) { selectJob(matched[0]); ElMessage.success('已选中') }
  else ElMessage.warning('未找到')
  searchKeyword.value=''
}

const getCornerStyle = (index) => {
  const colors = [
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fad0c4 100%)',
    'linear-gradient(135deg, #ffd1ff 0%, #c7f4ff 100%)',
    'linear-gradient(135deg, #2af598 0%, #009efd 100%)'
  ]
  return { background: colors[index % colors.length] }
}
const getCardColor = (index) => {
  const list = [
    'linear-gradient(135deg, #e0f7ff 0%, #f3fcff 100%)',
    'linear-gradient(135deg, #fff0f6 0%, #fff5f7 100%)',
    'linear-gradient(135deg, #f0f9ff 0%, #f7fcff 100%)',
    'linear-gradient(135deg, #fffbf0 0%, #fffcf5 100%)',
    'linear-gradient(135deg, #f6ffed 0%, #fafff0 100%)'
  ]
  return { background: list[index % list.length] }
}

const loadAllJobsFromDB = async () => {
  try {
    const res = await axios.get('/api/jobs/search?page=1&size=9999')
    allJobs.value = res.data.items || []
  } catch (err) {
    allJobs.value = recommendedJobs.value
  }
}

const loadJobCategories = async () => {
  try {
    const res = await axios.get('/api/jobs/names')
    categoryList.value = res.data.slice(0, 40)
  } catch (err) {}
}

const filteredAllJobs = computed(() => {
  let list = allJobs.value
  if (activeCategory.value !== '全部岗位') {
    list = list.filter(job => job.job_name.includes(activeCategory.value))
  }
  if (allJobsSearchKeyword.value) {
    const kw = allJobsSearchKeyword.value.toLowerCase()
    list = list.filter(j => j.job_name?.toLowerCase().includes(kw))
  }
  return list
})
const uniqueFilteredJobs = computed(() => {
  const seen = new Set()
  return filteredAllJobs.value.filter(item => {
    if (!item.job_name) return false
    if (seen.has(item.job_name)) return false
    seen.add(item.job_name)
    return true
  })
})

// ==============================
// ✅ 核心：选择岗位时保存完整画像
// ==============================
const selectJob = (job) => {
  selectedJob.value = job
  localStorage.setItem('selectedJob', JSON.stringify(job))
  ElMessage.success(`已选择：${job.job_name}`)
}

const handleAllJobsSearch = () => {
  ElMessage.success(`找到 ${uniqueFilteredJobs.value.length} 个岗位`)
}

// ==============================
// ✅ 跳转匹配结果页
// ==============================
const startJobMatch = async () => {
  if (!selectedJob.value.id) {
    ElMessage.warning('请先选择一个岗位')
    return
  }
  router.push({
    path: '/match-result',
    query: {
      jobId: selectedJob.value.id,
      jobName: selectedJob.value.job_name
    }
  })
}

onMounted(async () => {
  hasAbilityProfile.value = true
  await loadAllJobsFromDB()
  await loadJobCategories()

  if (route.query.jobId) {
    const job = allJobs.value.find(j => j.id == route.query.jobId)
    if (job) selectJob(job)
  }
})
</script>

<style scoped>
.job-match-page {
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  background: #fff;
  margin: 0;
  padding: 60px 0 0 0;
  color: #1a2639;
}
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
  justify-content:space-between;
  align-items: center;
  height: 100%;
}
.nav-left { display: flex; align-items: center; }
.logo { display: flex; align-items: center; margin-right: 40px; font-size: 18px; font-weight: bold; }
.logo-icon { font-size: 24px; margin-right: 8px; }
.nav-menu { display: flex; list-style: none; margin: 0; padding: 0; }
.menu-item { margin: 0 15px; font-size: 14px; cursor: pointer; height: 60px; line-height: 60px; position: relative; }
.menu-item:hover { color: #2f54eb; }
.menu-item.active { color: #2f54eb; }
.menu-item.active::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 3px; background: #2f54eb; }
.dropdown { position: relative; }
.dropdown-menu { position: absolute; top: 100%; left: 0; width: 200px; background: #fff; box-shadow: 0 4px 16px rgba(0,0,0,0.12); border-radius: 8px; list-style: none; padding: 8px 0; display: none; z-index: 9999; }
.dropdown:hover .dropdown-menu { display: block; }
.dropdown-item { padding: 12px 20px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.dropdown-item:hover { background: #f0f7ff; }
.color-dot { width: 8px; height: 8px; border-radius: 50%; }
.color-dot.red { background: #ff7a45; }
.color-dot.orange { background: #faad14; }
.color-dot.green { background: #52c41a; }
.color-dot.blue { background: #1890ff; }
.nav-right { display: flex; gap: 15px; align-items: center; }
.nav-search-wrap { display: flex; width: 200px; height: 24px; border-radius: 12px; border: 1px solid #e8e8e8; }
.nav-search-input { flex: 1; padding: 0 12px; border: none; outline: none; font-size: 12px; }
.nav-search-btn { width: 53px; background: #2f54eb; color: #fff; border: none; font-size: 12px; cursor: pointer; }
.btn-toggle-theme { padding: 6px 10px; border: none; background: #f5f7fa; border-radius: 4px; cursor: pointer; }
.btn-login { padding: 6px 15px; border: 1px solid #2f54eb; color: #2f54eb; background: #fff; border-radius: 4px; cursor: pointer; }
.btn-register { padding: 6px 15px; border: none; color: #fff; background: #2f54eb; border-radius: 4px; cursor: pointer; }
.user-profile { position: relative; }
.avatar { width: 36px; height: 36px; border-radius: 50%; cursor: pointer; border: 2px solid #f0f0f0; }
.user-menu { position: absolute; top: 50px; right: 0; width: 120px; background: #fff; box-shadow: 0 4px 16px rgba(0,0,0,0.12); border-radius: 8px; z-index: 9999; }
.user-menu .menu-item { padding: 10px 15px; font-size: 14px; cursor: pointer; margin: 0; }
.user-menu .logout { color: #ff4d4f; border-top: 1px solid #f0f0f0; }

.match-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}
.page-header { margin-bottom: 20px; }
.page-header h1 { font-size: 24px; font-weight: 700; color: #1f2937; margin: 0; }

.recommended-jobs-section {
  background: #f8f9ff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 30px;
  min-height: 400px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.section-header h2 { font-size: 20px; font-weight: 600; color: #1f2937; }
.match-rate-tip { font-size: 14px; color: #2f54eb; background: #e6f7ff; padding: 4px 12px; border-radius: 16px; }
.recommended-jobs-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.recommended-job-card {
  background: #fff;
  border-radius: 20px;
  padding: 26px;
  height: 240px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.35s ease;
  position: relative;
  border: 1px solid #f0f7ff;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.card-corner {
  position: absolute;
  top: 0;
  left: 0;
  width: 50px;
  height: 50px;
  border-bottom-right-radius: 20px;
}
.recommended-job-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 32px rgba(47,84,235,0.15);
  border-color: #c0d0ff;
}
.recommended-job-card.active {
  border: 2px solid #2f54eb;
  background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
}
.match-rate-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  padding: 5px 11px;
  border-radius: 20px;
  box-shadow: 0 3px 8px rgba(79,172,254,0.3);
}
.job-info {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.job-info .job-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.5;
  margin: 0;
}
.match-tag {
  font-size: 14px;
  color: #36ad6a;
  font-weight: 500;
  padding: 6px 14px;
  background: #f6ffed;
  border-radius: 12px;
}

.all-job-selection {
  background: #f8f9ff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 40px;
}
.all-job-selection h3 {
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 10px;
  margin-bottom: 20px;
}
.job-category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  max-height: 80px;
  overflow-y: auto;
}
.tab-item {
  padding: 6px 14px;
  border-radius: 20px;
  background: #f5f7fa;
  font-size: 14px;
  cursor: pointer;
  transition: 0.25s;
}
.tab-item.active { background: #2f54eb; color: #fff; }
.tab-item:hover { background: #e0e8ff; }
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
  outline: none;
}
.all-jobs-search-btn {
  padding: 10px 20px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.job-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 18px;
}

.job-card {
  border-radius: 20px;
  padding: 32px 16px;
  height: 110px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: all 0.35s ease;
  border: 1px solid #e8f3ff;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.job-card:hover {
  transform: translateY(-7px);
  box-shadow: 0 12px 24px rgba(47,84,235,0.12);
  border-color: #b8d0ff;
}
.job-card.active {
  border: 2px solid #2f54eb;
  background: linear-gradient(135deg, #e6f7ff 0%, #ffffff 100%) !important;
}
.job-card .job-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.5;
}

.match-action-bar {
  text-align: center;
  margin-top: 30px;
  margin-bottom: 60px;
}
.match-action-bar .el-button {
  padding: 12px 40px;
  font-size: 16px;
  border-radius: 10px;
}

@media (max-width: 768px) {
  .nav-menu { display: none; }
  .nav-wrap { width: 95%; }
  .recommended-jobs-list { grid-template-columns: repeat(2, 1fr); }
  .job-card-list { grid-template-columns: repeat(2, 1fr); }
}
</style>
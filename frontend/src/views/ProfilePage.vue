<template>
  <div class="profile-page">
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item" @click="$router.push('/career-planning-intro')">职业规划</li>
            <li class="menu-item" @click="$router.push('/report-export')">报告导出</li>
            <!-- <li class="menu-item" @click="$router.push('/about-us')">关于我们</li>
            <li class="menu-item dropdown">
              核心功能 ▼
              <ul class="dropdown-menu">
                <li class="dropdown-item" @click="goToFeature('测评')">
                  <span class="color-dot red"></span>
                  职业兴趣测评
                </li>
                <li class="dropdown-item" @click="goToFeature('分析')">
                  <span class="color-dot orange"></span>
                  能力短板分析
                </li>
                <li class="dropdown-item" @click="goToFeature('规划')">
                  <span class="color-dot green"></span>
                  发展路径规划
                </li>
                <li class="dropdown-item" @click="goToFeature('导出')">
                  <span class="color-dot blue"></span>
                  规划报告导出
                </li>
              </ul>
            </li> -->
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
          
          <div class="user-profile">
            <img 
              :src="userInfo.avatar || 'https://picsum.photos/seed/avatar/40/40'" 
              alt="用户头像" 
              class="avatar"
              @click="toggleUserMenu"
            >
            <div class="user-menu" v-show="isUserMenuOpen">
              <div class="menu-item" @click="$router.push('/profile')">个人中心</div>
              <!-- <div class="menu-item" @click="$router.push('/settings')">账号设置</div> -->
              <div class="menu-item logout" @click="handleLogout">退出登录</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="profile-main">
      <div class="profile-container">
        <aside class="profile-sidebar">
          <div class="user-info-card">
            <div class="avatar-container">
              <img :src="userInfo.avatar || 'https://picsum.photos/seed/avatar/200/200'" alt="用户头像" class="user-avatar">
              <label class="avatar-upload-btn" @click="triggerAvatarUpload">
                <input type="file" accept="image/*" @change="handleAvatarUpload" hidden ref="avatarInput">
                更换头像
              </label>
            </div>
            <div class="user-basic-info">
              <h3 class="username">{{ userInfo.username || '未设置昵称' }}</h3>
              <p class="user-role">{{ userInfo.role || '普通用户' }}</p>
              <p class="user-status">
                <span class="status-dot"></span>
                已加入 {{ formatDate(userInfo.joinTime) }}
              </p>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <span class="stat-value">{{ userStats.assessmentCount }}</span>
                <span class="stat-label">测评次数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ userStats.planCount }}</span>
                <span class="stat-label">规划方案</span>
              </div>
            </div>
          </div>

          <nav class="sidebar-nav">
            <ul class="nav-list">
              <li class="nav-item" :class="{ active: activeTab === 'security' }" @click="switchTab('security')">
                <span class="nav-icon">🔒</span>
                <span class="nav-text">账号安全</span>
              </li>
              <li class="nav-item" :class="{ active: activeTab === 'career' }" @click="switchTab('career')">
                <span class="nav-icon">📝</span>
                <span class="nav-text">我的职业规划</span>
              </li>
              <li class="nav-item" :class="{ active: activeTab === 'interest' }" @click="switchTab('interest')">
                <span class="nav-icon">📊</span>
                <span class="nav-text">兴趣测试报告</span>
              </li>
              <li class="nav-item" :class="{ active: activeTab === 'match' }" @click="switchTab('match')">
                <span class="nav-icon">🎯</span>
                <span class="nav-text">人岗匹配报告</span>
              </li>
            </ul>
          </nav>
        </aside>

        <div class="profile-content">
          <div class="tab-content" v-show="activeTab === 'security'">
            <div class="content-header">
              <h2 class="content-title">账号安全</h2>
            </div>
            <div class="security-settings">
              <div class="security-item">
                <div class="item-left">
                  <span class="item-icon">📱</span>
                  <div class="item-text">
                    <span class="item-title">绑定手机号</span>
                    <span class="item-desc">{{ userInfo.phone || '未绑定' }}</span>
                  </div>
                </div>
                <button class="operate-btn" @click="showBindPhoneModal = true">
                  {{ userInfo.phone ? '修改' : '绑定' }}
                </button>
              </div>
              <div class="security-item">
                <div class="item-left">
                  <span class="item-icon">🔑</span>
                  <div class="item-text">
                    <span class="item-title">修改密码</span>
                    <span class="item-desc">建议定期更换密码，保障账号安全</span>
                  </div>
                </div>
                <button class="operate-btn" @click="showChangePwdModal = true">修改</button>
              </div>
            </div>
          </div>

          <div class="tab-content" v-show="activeTab === 'career'">
            <div class="content-header">
              <h2 class="content-title">我的职业规划</h2>
              <button class="create-btn" @click="$router.push('/career-planning-intro')">创建新规划</button>
            </div>
            <div v-if="careerPlans.length === 0" class="empty-state">
              <div class="empty-icon">📄</div>
              <div class="empty-text">暂无职业规划方案</div>
              <button class="empty-btn" @click="$router.push('/career-planning-intro')">立即创建</button>
            </div>
            <div class="career-plan-list" v-else>
              <div class="plan-card" v-for="plan in careerPlans" :key="plan.id">
                <div class="plan-header">
                  <h3 class="plan-title">{{ plan.title || '未命名规划' }}</h3>
                  <div class="plan-date">{{ formatDate(plan.created_at) }}</div>
                </div>
                <div class="plan-content">
                  <div class="plan-item">
                    <span class="item-label">目标职业：</span>
                    <span class="item-value">{{ plan.target || '未设置' }}</span>
                  </div>
                  <div class="plan-item">
                    <span class="item-label">规划周期：</span>
                    <span class="item-value">长期规划</span>
                  </div>
                  <div class="plan-item">
                    <span class="item-label">创建时间：</span>
                    <span class="item-value">{{ formatDate(plan.created_at) }}</span>
                  </div>
                </div>
                <div class="plan-actions">
                  <button class="export-btn" @click="exportPlan(plan.id)">导出报告</button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="tab-content" v-show="activeTab === 'interest'">
            <div class="content-header">
              <h2 class="content-title">兴趣测试报告</h2>
              <button class="create-btn" @click="$router.push('/interest-test')">前往测评</button>
            </div>
            <div v-if="interestReports.length === 0" class="empty-state">
              <div class="empty-icon">📊</div>
              <div class="empty-text">暂无兴趣测试报告</div>
              <button class="empty-btn" @click="$router.push('/interest-test')">立即测评</button>
            </div>
            <div class="report-list" v-else>
              <div class="report-card" v-for="item in interestReports" :key="item.id">
                <div class="report-header">
                  <h3 class="report-title">职业兴趣测评报告 #{{ item.id }}</h3>
                  <div class="report-date">{{ formatDate(item.created_at) }}</div>
                </div>
                <div class="report-content">
                  <div class="report-item">
                    <span class="item-label">测试类型：</span>
                    <span class="item-value">霍兰德职业兴趣测试</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">测评时间：</span>
                    <span class="item-value">{{ formatDate(item.created_at) }}</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">报告状态：</span>
                    <span class="item-value">已完成</span>
                  </div>
                </div>
                <div class="report-actions">
                  <button class="export-btn" @click="exportReport('interest', item.id)">导出报告</button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="tab-content" v-show="activeTab === 'match'">
            <div class="content-header">
              <h2 class="content-title">人岗匹配结果报告</h2>
              <button class="create-btn" @click="$router.push('/ability-analysis')">开始匹配</button>
            </div>
            <div v-if="matchReports.length === 0" class="empty-state">
              <div class="empty-icon">🎯</div>
              <div class="empty-text">暂无人岗匹配报告</div>
              <button class="empty-btn" @click="$router.push('/ability-analysis')">立即匹配</button>
            </div>
            <div class="report-list" v-else>
              <div class="report-card" v-for="item in matchReports" :key="item.id">
                <div class="report-header">
                  <h3 class="report-title">{{ item.job_name }} 匹配报告</h3>
                  <div class="report-date">{{ formatDate(item.created_at) }}</div>
                </div>
                <div class="report-content">
                  <div class="report-item">
                    <span class="item-label">目标岗位：</span>
                    <span class="item-value">{{ item.job_name }}</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">匹配得分：</span>
                    <span class="item-value">{{ item.match_score }}分</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">匹配时间：</span>
                    <span class="item-value">{{ formatDate(item.created_at) }}</span>
                  </div>
                </div>
                <div class="report-actions">
                  <button class="export-btn" @click="exportReport('match', item.id)">导出报告</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 美化后的修改密码弹窗 -->
    <div class="modal-overlay" v-show="showChangePwdModal" @click="closeModal('changePwd')">
      <div class="modal-content modern-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">修改密码</h3>
          <button class="close-btn" @click="closeModal('changePwd')">×</button>
        </div>
        <form class="modal-form" @submit.prevent="changePassword">
          <div class="form-row">
            <label class="form-label">原密码</label>
            <input type="password" class="form-input" v-model="pwdForm.oldPwd" placeholder="请输入原密码">
          </div>
          <div class="form-row">
            <label class="form-label">新密码</label>
            <input type="password" class="form-input" v-model="pwdForm.newPwd" placeholder="请输入新密码">
          </div>
          <div class="form-row">
            <label class="form-label">确认新密码</label>
            <input type="password" class="form-input" v-model="pwdForm.confirmPwd" placeholder="请再次输入新密码">
          </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal('changePwd')">取消</button>
            <button type="submit" class="confirm-btn">确认修改</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 美化后的修改手机号弹窗（无验证码） -->
    <div class="modal-overlay" v-show="showBindPhoneModal" @click="closeModal('bindPhone')">
      <div class="modal-content modern-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">{{ userInfo.phone ? '修改手机号' : '绑定手机号' }}</h3>
          <button class="close-btn" @click="closeModal('bindPhone')">×</button>
        </div>
        <form class="modal-form" @submit.prevent="bindPhone">
          <div class="form-row">
            <label class="form-label">手机号</label>
            <input type="text" class="form-input" v-model="phoneForm.phone" placeholder="请输入手机号">
          </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal('bindPhone')">取消</button>
            <button type="submit" class="confirm-btn">确认绑定</button>
          </div>
        </form>
      </div>
    </div>

    <footer class="footer">
      <div class="footer-wrap">© 2026 大学生职业规划系统 | 助力大学生精准规划职业方向</div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const token = localStorage.getItem('token')
if (!token) {
  ElMessage.warning('请先登录')
  router.push('/login')
}

const authAxios = axios.create({
  baseURL: '/api',
  headers: {
    Authorization: 'Bearer ' + token
  }
})

const userInfo = ref({
  id: '',
  avatar: '',
  username: '',
  name: '',
  phone: '',
  email: '',
  role: '',
  joinTime: '',
  education_text: '',
  work_text: '',
  project_text: '',
  skills_certs_text: '',
  summary: '',
  skills: '',
  certificates: '',
  soft_abilities: '',
  completeness: 0,
  created_at: '',
  expanded: false
})

const userStats = ref({ assessmentCount: 0, planCount: 0 })
const careerPlans = ref([])
const interestReports = ref([])
const matchReports = ref([])

const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')
const activeTab = ref('security')
const showChangePwdModal = ref(false)
const showBindPhoneModal = ref(false)

const phoneForm = ref({ phone: '' })
const pwdForm = ref({ oldPwd: '', newPwd: '', confirmPwd: '' })

const loadUserProfile = async () => {
  try {
    const { data } = await authAxios.get('/user/profile')
    userInfo.value = { ...data, expanded: false }
  } catch (e) {
    ElMessage.error('加载用户信息失败')
  }
}

const loadUserStats = async () => {
  try {
    const { data } = await authAxios.get('/user/stats')
    userStats.value = data || { assessmentCount: 0, planCount: 0 }
  } catch (e) {}
}

const loadCareerPlans = async () => {
  try {
    const studentId = localStorage.getItem('studentId')
    if (!studentId) {
      careerPlans.value = []
      return
    }
    const { data } = await authAxios.get(`/report/history/${studentId}`)
    careerPlans.value = data.map(item => ({
      id: item.id,
      title: `${item.job_name} 职业规划报告`,
      target: item.job_name,
      created_at: item.created_at
    }))
  } catch (e) {
    console.error('加载职业规划报告失败', e)
    careerPlans.value = []
  }
}

const loadInterestReports = async () => {
  try {
    if (!userInfo.value.id) {
      interestReports.value = []
      return
    }
    const { data } = await authAxios.get(`/assessment/history/${userInfo.value.id}`)
    console.log("当前用户真实测评报告：", data)
    let list = Array.isArray(data) ? data : (data?.list || [])
    interestReports.value = list.map(item => ({
      id: item.id || 1,
      title: item.title || '职业兴趣测评',
      type: item.type || '霍兰德测试',
      result: item.result || '已完成测评',
      suitableJobs: item.suitableJobs || '待查看',
      created_at: item.created_at || item.createTime || item.time || new Date()
    }))
  } catch (e) {
    console.error("兴趣报告加载失败", e)
    interestReports.value = []
  }
}

const loadMatchReports = async () => {
  try {
    const studentId = localStorage.getItem('studentId')
    if (!studentId) {
      matchReports.value = []
      return
    }
    const { data } = await authAxios.get(`/match/history/${studentId}`)
    matchReports.value = data.history || []
  } catch (e) {
    console.error('加载匹配报告失败', e)
    matchReports.value = []
  }
}

const switchTab = (tab) => { activeTab.value = tab }

const formatDate = (s) => {
  if (!s) return ''
  try {
    return new Date(s).toLocaleString()
  } catch {
    return ''
  }
}

const triggerAvatarUpload = () => {
  document.querySelector('.avatar-upload-btn input')?.click()
}

const handleAvatarUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const { data } = await authAxios.post('/api/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    userInfo.value.avatar = data.avatar
    ElMessage.success('头像更新成功')
  } catch (e) {
    ElMessage.error('上传失败')
  }
}

const changePassword = async () => {
  const { oldPwd, newPwd, confirmPwd } = pwdForm.value
  if (!oldPwd || !newPwd || newPwd !== confirmPwd) {
    ElMessage.warning('请检查密码输入')
    return
  }
  try {
    await authAxios.post('/user/change-password', { oldPwd, newPwd })
    ElMessage.success('密码修改成功，请重新登录')
    handleLogout()
  } catch (e) {
    ElMessage.error('原密码错误')
  }
}

const bindPhone = async () => {
  const { phone } = phoneForm.value
  if (!phone) {
    ElMessage.warning('请输入手机号')
    return
  }
  try {
    await authAxios.post('/user/bind-phone', { phone })
    userInfo.value.phone = phone
    ElMessage.success('绑定成功')
    showBindPhoneModal.value = false
  } catch (e) {
    ElMessage.error('绑定失败')
  }
}

const closeModal = (t) => {
  if (t === 'changePwd') showChangePwdModal.value = false
  if (t === 'bindPhone') showBindPhoneModal.value = false
}

const exportPlan = (id) => {
  window.open(`/api/report/export/career/${id}`, '_blank')
  ElMessage.success('报告导出中')
}

const exportReport = (type, id) => {
  if (type === 'interest') {
    window.open(`/api/report/export/interest/${id}`, '_blank')
  } else if (type === 'match') {
    window.open(`/api/report/export/match/${id}`, '_blank')
  }
  ElMessage.success('报告导出中')
}

const toggleTheme = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  document.body.classList.toggle('dark', darkMode.value)
}

const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const goToFeature = (t) => {
  const map = {
    '测评': '/interest-test',
    '分析': '/ability-analysis',
    '规划': '/development-path',
    '导出': '/report-export'
  }
  router.push(map[t] || '/')
}

const handleSearch = () => {
  const i = document.querySelector('.nav-search-input')
  if (i?.value) router.push(`/search?keyword=${i.value}`)
}

onMounted(async () => {
  document.body.classList.toggle('dark', darkMode.value)
  await loadUserProfile()
  await loadUserStats()
  await loadCareerPlans()
  await loadInterestReports()
  await loadMatchReports()
})
</script>

<style scoped>
.profile-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f8f9fa;
  margin: 0;
  padding: 60px 0 0 0;
}
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
.profile-main {
  width: 100%;
  padding: 30px 0;
}
.profile-container {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
}
.profile-sidebar {
  width: 260px;
  flex-shrink: 0;
}
.user-info-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
}
.avatar-container {
  position: relative;
  display: inline-block;
  margin-bottom: 15px;
}
.user-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f5f5f5;
}
.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #2f54eb;
  color: #fff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}
.user-basic-info {
  margin-bottom: 20px;
}
.username {
  font-size: 18px;
  font-weight: 60;
  margin: 0 0 5px 0;
}
.user-role {
  color: #999;
  font-size: 14px;
  margin: 0 0 5px 0;
}
.user-status {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #52c41a;
  margin-right: 5px;
}
.user-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}
.stat-item {
  text-align: center;
}
.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #2f54eb;
  margin-bottom: 4px;
}
.stat-label {
  font-size: 12px;
  color: #999;
}
.sidebar-nav {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.nav-list {
  list-style: none;
  margin: 0;
  padding: 10px 0;
}
.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
}
.nav-item:hover {
  background: #f5f7fa;
}
.nav-item.active {
  background: #e6f7ff;
  color: #2f54eb;
  font-weight: 500;
}
.nav-icon {
  font-size: 16px;
  margin-right: 10px;
}
.nav-text {
  flex: 1;
}
.profile-content {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 20px;
}
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}
.content-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}
.edit-btn, .create-btn {
  padding: 6px 15px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.clear-btn {
  padding: 6px 15px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.user-card-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.user-summary-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8e8e8;
  cursor: pointer;
  transition: all 0.2s;
}
.user-summary-card:hover {
  border-color: #2f54eb;
  background: #f5f7ff;
}
.card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.card-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
}
.card-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}
.card-brief {
  margin-bottom: 15px;
}
.brief-item {
  display: flex;
  margin-bottom: 6px;
  font-size: 14px;
}
.brief-item label {
  width: 50px;
  color: #666;
  font-weight: 500;
}
.brief-item span {
  color: #333;
}
.card-actions {
  margin-bottom: 15px;
}
.view-btn {
  padding: 6px 15px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.card-detail {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #eee;
}
.basic-info-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 24px;
  border: 1px solid #e8e8e8;
}
.card-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #eee;
}
.card-row:last-child {
  margin-bottom: 0;
  border-bottom: none;
}
.card-label {
  width: 140px;
  flex-shrink: 0;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
.card-value {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}
.security-settings {
  width: 100%;
}
.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}
.security-item:last-child {
  border-bottom: none;
}
.item-left {
  display: flex;
  align-items: center;
  gap: 15px;
}
.item-icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}
.item-text {
  display: flex;
  flex-direction: column;
}
.item-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
  width: 400px;
}
.item-desc {
  font-size: 12px;
  color: #999;
}
.operate-btn {
  padding: 6px 15px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.code-input-wrap {
  display: flex;
  gap: 10px;
  flex: 1;
}
.code-input {
  flex: 1;
}
.code-btn {
  width: 120px;
  padding: 0 10px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}
.career-plan-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.plan-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8e8e8;
}
.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
}
.plan-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}
.plan-date {
  font-size: 12px;
  color: #999;
}
.plan-content {
  margin-bottom: 15px;
}
.plan-item {
  display: flex;
  margin-bottom: 8px;
}
.item-label {
  width: 80px;
  flex-shrink: 0;
  color: #666;
  font-size: 14px;
}
.item-value {
  flex: 1;
  font-size: 14px;
}
.plan-actions {
  display: flex;
  gap: 10px;
}
.plan-actions .export-btn {
  padding: 6px 12px;
  background: #52c41a;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.report-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.report-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8e8e8;
}
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
}
.report-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}
.report-date {
  font-size: 12px;
  color: #999;
}
.report-content {
  margin-bottom: 15px;
}
.report-item {
  display: flex;
  margin-bottom: 8px;
}
.report-actions {
  display: flex;
  gap: 10px;
}
.report-actions .export-btn {
  padding: 6px 12px;
  background: #52c41a;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.history-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}
.item-left {
  width: 60px;
  flex-shrink: 0;
}
.history-cover {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}
.item-middle {
  flex: 1;
  padding: 0 15px;
}
.history-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}
.history-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-line-orient: vertical;
  overflow: hidden;
}
.history-time {
  font-size: 12px;
  color: #999;
}
.item-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.item-right .view-btn {
  padding: 6px 12px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.item-right .delete-btn {
  padding: 6px 12px;
  background: #fff;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #999;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #ccc;
}
.empty-text {
  font-size: 16px;
  margin-bottom: 8px;
}
.empty-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 美化弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}
.modal-content {
  width: 420px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
  padding: 24px;
  position: relative;
}
.modern-modal {
  border-top: 4px solid #2f54eb;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}
.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #262626;
}
.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: #999;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: 0.2s;
}
.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}
.modal-form {
  width: 100%;
}
.form-row {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}
.form-input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: 0.2s;
  outline: none;
}
.form-input:focus {
  border-color: #2f54eb;
  box-shadow: 0 0 0 2px rgba(47, 84, 235, 0.1);
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
.confirm-btn {
  padding: 8px 20px;
  height: 40px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: 0.2s;
}
.confirm-btn:hover {
  background: #274bdb;
}
.cancel-btn {
  padding: 8px 20px;
  height: 40px;
  background: #f7f8fa;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: 0.2s;
}
.cancel-btn:hover {
  background: #e5e6eb;
}

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
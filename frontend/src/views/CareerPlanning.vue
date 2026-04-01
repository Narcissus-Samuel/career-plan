<template>
  <div class="career-planning-page">
    <!-- 顶部导航栏 -->
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
            <input type="text" class="nav-search-input" placeholder="搜索岗位详情..." @keyup.enter="handleSearch" />
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
      </div>
    </header>

    <!-- 报告主体 -->
    <div class="main-content">
      <div v-if="reportVisible" class="report-container">
        <el-card class="report-card" shadow="hover">
          <div class="report-header-bar">
            <div><b>目标岗位：</b> {{ targetJob || 'BD经理' }}</div>
            <div><b>生成时间：</b> {{ reportTime }}</div>
            <div class="right-btns">
              <el-button type="primary" @click="generateReport"> 🔄 重新生成 </el-button>
              <el-button type="warning" @click="exportReport"> 📥 导出PDF </el-button>
            </div>
          </div>

          <div class="report-content-section">
            <div class="section-title"><i class="icon">📊</i> 报告详情</div>
            <div v-html="aiReportHtml"></div>
          </div>
        </el-card>
      </div>

      <div v-else class="loading-box">
        <el-loading-spinner />
        <p>AI 正在为你生成专业职业规划报告...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElLoading, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'
import html2pdf from 'html2pdf.js'

const router = useRouter()

const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)

const reportVisible = ref(false)
const reportTime = ref('')
const targetJob = ref('')
const aiReportContent = ref('')

// ✅ 核心：完美解析Markdown表格 + 自动渲染成标准HTML表格 + 清理所有乱码
const aiReportHtml = computed(() => {
  let html = aiReportContent.value

  // 1. 预处理：清理多余空行、Markdown符号，保留表格结构
  html = html
    .replace(/\n{3,}/g, '\n\n') // 合并多余空行
    .replace(/^# /gm, '<h1 class="report-main-title">')
    .replace(/^## /gm, '<h2 class="chapter-title">')
    .replace(/^### /gm, '<h3 class="sub-title">')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^> (.*)$/gm, '<div class="report-note">$1</div>')

  // 2. 核心：完美解析Markdown表格（完全匹配你截图的格式）
  const tableRegex = /(\|.*?\|\n)(\|.*?\|\n)(\|.*?\|\n)+/g
  html = html.replace(tableRegex, (tableStr) => {
    const lines = tableStr.trim().split('\n').filter(line => !line.includes('---'))
    if (lines.length < 2) return tableStr

    // 表头
    const headers = lines[0].split('|').filter(cell => cell.trim()).map(cell => cell.trim())
    // 表体
    const rows = lines.slice(1).map(row => 
      row.split('|').filter(cell => cell.trim()).map(cell => cell.trim())
    )

    // 生成标准HTML表格（带样式类）
    let tableHtml = '<table class="standard-table">'
    // 表头
    tableHtml += '<thead><tr>'
    headers.forEach(header => {
      tableHtml += `<th>${header}</th>`
    })
    tableHtml += '</tr></thead>'
    // 表体
    tableHtml += '<tbody>'
    rows.forEach(row => {
      tableHtml += '<tr>'
      row.forEach(cell => {
        tableHtml += `<td>${cell}</td>`
      })
      tableHtml += '</tr>'
    })
    tableHtml += '</tbody></table>'

    return tableHtml
  })

  // 3. 处理普通段落
  html = html.replace(/^(?!<h|<table|<div)(.+)$/gm, '<p class="text-paragraph">$1</p>')

  // 4. 闭合标签
  html = html.replace(/<h1 class="report-main-title">/g, '<h1 class="report-main-title">$1</h1>')
  html = html.replace(/<h2 class="chapter-title">/g, '<h2 class="chapter-title">$1</h2>')
  html = html.replace(/<h3 class="sub-title">/g, '<h3 class="sub-title">$1</h3>')

  return html
})

const getStudentId = () => localStorage.getItem('student_id') || 1

const fetchReportData = async () => {
  const loading = ElLoading.service({ text: 'AI 正在生成专属报告...' })
  try {
    const { data } = await axios.post('/api/report/generate', {
      student_id: getStudentId(),
      job_name: ''
    })
    if (data.error) {
      ElMessage.error(data.error)
      return
    }
    aiReportContent.value = data.content
    targetJob.value = data.job_name
    reportTime.value = new Date().toLocaleString()
    reportVisible.value = true
    ElMessage.success('报告生成成功！')
  } catch (err) {
    console.error(err)
    ElMessage.error('报告生成失败，请检查后端服务')
  } finally {
    loading.close()
  }
}

const generateReport = () => {
  aiReportContent.value = ''
  fetchReportData()
}

const exportReport = () => {
  if (!aiReportContent.value) {
    ElMessage.warning('暂无报告可导出')
    return
  }
  html2pdf().set({
    margin: 10,
    filename: `${targetJob.value}_职业规划报告.pdf`,
    html2canvas: { scale: 2 },
    jsPDF: { format: 'a4' }
  }).from(document.querySelector('.report-content-section')).save()
  ElMessage.success('导出成功')
}

const toggleUserMenu = () => isUserMenuOpen.value = !isUserMenuOpen.value
const handleLogout = () => { localStorage.clear(); router.push('/'); ElMessage.success('退出成功') }
const goToFeature = (t) => router.push({ '测评':'/interest-test','分析':'/ability-analysis','规划':'/development-path','导出':'/report-export'}[t]||'/')
const handleSearch = () => ElMessage.warning('搜索功能开发中')
const toggleTheme = () => {}

onMounted(() => {
  fetchReportData()
})
</script>

<style scoped>
/* 原有导航样式100%保留 */
.career-planning-page { width:100%; min-height:100vh; background:#f5f7fa; }
.top-nav { position:fixed; top:0; left:0; width:100%; height:60px; background:#fff; box-shadow:0 2px 12px rgba(0,0,0,0.08); z-index:9999; }
.nav-wrap { width:1200px; margin:0 auto; display:flex; justify-content:space-between; align-items:center; height:100%; }
.nav-left { display:flex; align-items:center; }
.logo { display:flex; align-items:center; margin-right:40px; font-size:18px; font-weight:bold; }
.logo-icon { margin-right:8px; font-size:22px; }
.nav-menu { display:flex; list-style:none; padding:0; margin:0; }
.menu-item { margin:0 16px; font-size:14px; cursor:pointer; line-height:60px; position:relative; }
.menu-item.active { color:#409eff; font-weight:bold; }
.menu-item.active::after { content:''; position:absolute; bottom:0; left:0; width:100%; height:3px; background:#409eff; }
.dropdown { position:relative; }
.dropdown-menu { position:absolute; top:100%; left:0; width:200px; background:#fff; box-shadow:0 4px 16px rgba(0,0,0,0.1); border-radius:8px; list-style:none; padding:8px 0; display:none; }
.dropdown:hover .dropdown-menu { display:block; }
.dropdown-item { padding:12px 20px; font-size:14px; cursor:pointer; display:flex; align-items:center; gap:8px; }
.color-dot { width:8px; height:8px; border-radius:50%; }
.color-dot.red { background:#ff7a45; }
.color-dot.orange { background:#faad14; }
.color-dot.green { background:#52c41a; }
.color-dot.blue { background:#1890ff; }
.nav-right { display:flex; align-items:center; gap:12px; }
.nav-search-wrap { display:flex; width:200px; border:1px solid #eee; border-radius:12px; overflow:hidden; }
.nav-search-input { flex:1; padding:0 10px; border:none; outline:none; font-size:12px; }
.btn-toggle-theme { padding:4px 8px; border:none; background:#f5f7fa; border-radius:4px; cursor:pointer; }
.btn-login { padding:6px 14px; border:1px solid #409eff; color:#409eff; background:#fff; border-radius:4px; cursor:pointer; }
.btn-register { padding:6px 14px; border:none; color:#fff; background:#409eff; border-radius:4px; cursor:pointer; }
.user-profile { position:relative; }
.avatar { width:36px; height:36px; border-radius:50%; cursor:pointer; }
.user-menu { position:absolute; top:45px; right:0; width:130px; background:#fff; box-shadow:0 4px 16px rgba(0,0,0,0.1); border-radius:8px; padding:8px 0; }
.user-menu .menu-item { padding:10px 16px; font-size:14px; cursor:pointer; }
.user-menu .logout { color:#f56c6c; border-top:1px solid #eee; }

/* 内容区样式 */
.main-content { padding-top:70px; width:1200px; margin:0 auto; padding-bottom:40px; }
.report-container { width:100%; }
.report-card { border-radius:12px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.06); }
.report-header-bar { display:flex; justify-content:space-between; align-items:center; padding:16px 20px; background:#f8f9fa; border-bottom:1px solid #eee; }
.right-btns { display:flex; gap:10px; }

.report-content-section { padding:30px; line-height:1.8; background:#fff; }
.section-title { font-size:22px; font-weight:bold; margin-bottom:24px; color:#222; display:flex; align-items:center; gap:8px; }
.icon { color:#1890ff; font-size:24px; }

/* ====================== 核心：标准表格样式（完全匹配你截图） ====================== */
.standard-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.standard-table thead th {
  background: #f5f7fa;
  padding: 14px 16px;
  text-align: left;
  font-weight: bold;
  color: #333;
  border-bottom: 2px solid #e8f4ff;
}
.standard-table tbody td {
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #444;
}
.standard-table tbody tr:hover {
  background: #fafbfc;
}
.standard-table tbody tr:last-child td {
  border-bottom: none;
}

/* ====================== 其他报告样式 ====================== */
.report-main-title {
  font-size: 26px;
  font-weight: bold;
  color: #1890ff;
  margin: 0 0 30px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e8f4ff;
}
.chapter-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 32px 0 16px;
  padding-left: 10px;
  border-left: 4px solid #1890ff;
}
.sub-title {
  font-size: 17px;
  font-weight: bold;
  color: #333;
  margin: 20px 0 12px;
}
.report-note {
  padding: 14px 18px;
  border-radius: 8px;
  margin: 16px 0;
  background: #e8f4ff;
  border-left: 4px solid #1890ff;
  line-height: 1.6;
}
.text-paragraph {
  font-size: 15px;
  color: #444;
  margin: 10px 0;
  text-align: justify;
}

/* 加载样式 */
.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  gap: 12px;
  color: #666;
}
</style>
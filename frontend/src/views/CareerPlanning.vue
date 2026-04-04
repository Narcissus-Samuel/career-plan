<template>
  <div class="career-planning-page">
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

    <div class="main-content">
      <div v-if="reportVisible" class="report-container">
        <el-card class="report-card" shadow="hover">
          <div class="report-header-bar">
            <div><b>目标岗位：</b> {{ targetJob || '前端开发' }}</div>
            <div><b>生成时间：</b> {{ reportTime }}</div>
            <div class="right-btns">
              <el-button type="primary" @click="generateReport"> 🔄 重新生成 </el-button>
              <el-button type="warning" @click="exportReport"> 📥 导出PDF </el-button>
            </div>
          </div>

          <div class="report-content-section">
            <div class="section-title"><i class="icon">📊</i> 职业生涯发展报告</div>
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
const currentReportId = ref(null)

const aiReportHtml = computed(() => {
  let txt = aiReportContent.value || ''

  // 1. 按「一、二、三、四、」拆分章节
  const parts = txt.split(/(?=一、|二、|三、|四、)/)

  let html = ''

  parts.forEach(part => {
    if (!part.trim()) return

    // 2. 每个章节自动包成白色卡片
    html += '<div class="card-block">'

    // 替换标题：一、XXX → 蓝色左侧边框标题
    let p = part
      .replace(/^(一、|二、|三、|四、)(.+)$/gm, '<h2 class="chapter-title">$1$2</h2>')

    // 表格自动渲染
    const tableRex = /(\|.*?\|\n)+/g
    p = p.replace(tableRex, (tableStr) => {
      const lines = tableStr.trim().split('\n').filter(l => !l.includes('---'))
      if (lines.length < 2) return tableStr

      let ths = lines[0].split('|').map(c => c.trim()).filter(Boolean)
      let rows = lines.slice(1).map(r => r.split('|').map(c => c.trim()).filter(Boolean))

      let t = '<table class="standard-table"><thead><tr>'
      ths.forEach(h => t += `<th>${h}</th>`)
      t += '</tr></thead><tbody>'
      rows.forEach(r => {
        t += '<tr>'
        r.forEach(c => t += `<td>${c}</td>`)
        t += '</tr>'
      })
      t += '</tbody></table>'
      return t
    })

    // 加粗 **xxx**
    p = p.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

    // 段落
    p = p.replace(/^(.+)$/gm, (line) => {
      if (line.match(/<h|<table|^\s*$/)) return line
      return `<p class="text-paragraph">${line}</p>`
    })

    html += p
    html += '</div>'
  })

  return html
})

const getStudentId = () => {
  const id = localStorage.getItem('studentId') || localStorage.getItem('student_id')
  return id ? parseInt(id) : null
}

const fetchReportData = async () => {
  const loading = ElLoading.service({ text: 'AI 正在生成专属报告...' })
  try {
    const studentId = getStudentId()
    if (!studentId) {
      ElMessage.error('未获取到学生信息，请重新登录')
      return
    }

    const { data } = await axios.post('/api/report/generate', {
      student_id: studentId,
      job_name: ''
    })

    if (data.error) {
      ElMessage.error(data.error)
      return
    }

    aiReportContent.value = data.content
    targetJob.value = data.job_name || '前端开发'
    currentReportId.value = data.report_id
    reportTime.value = new Date().toLocaleString()
    reportVisible.value = true

    ElMessage.success('报告生成并已自动保存！')
  } catch (err) {
    console.error(err)
    ElMessage.error('报告生成失败')
  } finally {
    loading.close()
  }
}

const generateReport = () => {
  aiReportContent.value = ''
  reportVisible.value = false
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
}

const toggleUserMenu = () => (isUserMenuOpen.value = !isUserMenuOpen.value)
const handleLogout = () => { localStorage.clear(); router.push('/'); ElMessage.success('退出成功') }
const goToFeature = (t) => router.push({ '测评':'/interest-test','分析':'/ability-analysis','规划':'/development-path','导出':'/report-export'}[t]||'/')
const handleSearch = () => ElMessage.warning('搜索功能开发中')
const toggleTheme = () => {}

onMounted(() => {
  fetchReportData()
})
</script>

<style scoped>
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

.main-content { padding-top:70px; width:1200px; margin:0 auto; padding-bottom:40px; }
.report-container { width:100%; }
.report-card { border-radius:12px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.06); }
.report-header-bar { display:flex; justify-content:space-between; align-items:center; padding:16px 20px; background:#f8f9fa; border-bottom:1px solid #eee; }
.right-btns { display:flex; gap:10px; }

.report-content-section { padding:30px; line-height:1.8; background:#fff; }
.section-title { font-size:22px; font-weight:bold; margin-bottom:24px; color:#222; display:flex; align-items:center; gap:8px; }
.icon { color:#1890ff; font-size:24px; }

/* 🔥 卡片式布局核心（你要的整洁效果） */
.card-block {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  border: 1px solid #f0f0f0;
}

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

.report-main-title {
  font-size: 26px;
  font-weight: bold;
  color: #1890ff;
  margin: 0 0 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e8f4ff;
}
.chapter-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 0 0 16px;
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
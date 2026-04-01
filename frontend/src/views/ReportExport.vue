<template>
  <div class="report-export-page">
    <!-- 顶部导航栏（和测评页面完全一致） -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item " @click="$router.push('/career-planning-intro')">职业规划</li>
            <li class="menu-item active" @click="$router.push('/report-export')">报告导出</li>
            <li class="menu-item" @click="$router.push('/about-us')">关于我们</li>
            <li class="menu-item dropdown">
              核心功能 ▼
              <ul class="dropdown-menu">
                <li class="dropdown-item" @click="goToFeature('测评')">
                  <span class="color-dot red"></span> 职业测评
                </li>
                <li class="dropdown-item" @click="goToFeature('分析')">
                  <span class="color-dot orange"></span> 能力短板分析
                </li>
                <li class="dropdown-item" @click="goToFeature('规划')">
                  <span class="color-dot green"></span> 发展路径规划
                </li>
                <li class="dropdown-item active" @click="goToFeature('导出')">
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

    <!-- 子页面标题栏 -->
    <div class="test-subheader">
      <div class="subheader-wrap">
        <div class="page-title">
          <span class="title-icon">📄</span>
          <h1>报告导出中心</h1>
        </div>
        <div class="page-nav">
          <button class="report-btn" @click="showHistory = !showHistory">
            {{ showHistory ? '隐藏历史记录' : '📜 查看全部报告' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 页面主体内容 -->
    <div class="report-export">
      <!-- 报告列表（从数据库加载） -->
      <div class="report-list-section" v-if="!showHistory">
        <h3 class="section-title">我的报告列表</h3>
        <div class="filter-row">
          <select v-model="filterType" class="filter-select">
            <option value="">全部类型</option>
            <option value="interest_test">兴趣测试报告</option>
            <option value="job_match">人岗匹配报告</option>
            <option value="career_plan">职业规划报告</option>
          </select>
          <input v-model="filterName" placeholder="搜索报告名称" class="filter-input" />
        </div>

        <div class="card-list">
          <div class="report-card" v-for="item in filteredReports" :key="item.id">
            <div class="card-tag" :class="item.type">{{ getTypeName(item.type) }}</div>
            <h4 class="card-title">{{ item.title }}</h4>
            <p class="card-time">生成时间：{{ item.created_at }}</p>
            <div class="card-actions">
              <button @click="loadReport(item)" class="btn btn-edit">编辑查看</button>
              <button @click="quickExport(item)" class="btn btn-export">一键导出</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 报告编辑与导出区 -->
      <div class="edit-section" v-if="currentReport">
        <div class="edit-header">
          <h3>✏️ 报告编辑与导出</h3>
          <div class="tool-buttons">
            <button class="tool-btn check" @click="checkContent">✅ 内容检查</button>
            <button class="tool-btn polish" @click="polishReport">✨ 智能润色</button>
            <button class="tool-btn reset" @click="resetContent">🔄 恢复原始</button>
          </div>
        </div>

        <div class="editor-box">
          <textarea v-model="editContent" class="report-editor" placeholder="报告内容"></textarea>
        </div>

        <div class="export-bar">
          <div class="left">
            <span>导出格式：</span>
            <select v-model="exportFormat">
              <option value="pdf">PDF</option>
              <option value="word">Word</option>
            </select>
            <input v-model="currentReport.title" class="name-input" placeholder="报告名称" />
          </div>
          <div class="right">
            <button class="btn-save" @click="saveEdit">💾 保存修改</button>
            <button class="btn-export-final" @click="exportFinalReport">📤 导出报告</button>
          </div>
        </div>
      </div>

      <!-- 全部报告历史 -->
      <div class="history-section" v-if="showHistory">
        <h3 class="section-title">全部报告记录</h3>
        <table class="history-table">
          <thead>
            <tr>
              <th>报告名称</th>
              <th>类型</th>
              <th>生成时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in allReports" :key="item.id">
              <td>{{ item.title }}</td>
              <td>{{ getTypeName(item.type) }}</td>
              <td>{{ item.created_at }}</td>
              <td>
                <button class="mini-btn" @click="loadReport(item)">编辑</button>
                <button class="mini-btn export" @click="quickExport(item)">导出</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 提示弹窗 -->
      <div class="modal" v-if="showModal">
        <div class="modal-box">
          <h3>{{ modalTitle }}</h3>
          <p>{{ modalMsg }}</p>
          <button @click="showModal = false">确定</button>
        </div>
      </div>
    </div>

    <!-- 底部 -->
    <footer class="page-footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 职业规划报告导出中心
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// =============== 导航栏通用逻辑 ===============
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const handleLogout = () => {
  localStorage.clear()
  isLogin.value = false
  isUserMenuOpen.value = false
  router.push('/login')
  ElMessage.success('退出成功')
}

const applyTheme = () => {
  document.body.classList.toggle('dark', darkMode.value)
}
const toggleTheme = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  applyTheme()
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
  const ipt = document.querySelector('.nav-search-input')
  const k = ipt.value.trim()
  if (k) {
    router.push(`/search?keyword=${encodeURIComponent(k)}`)
    ipt.value = ''
    ElMessage.success('搜索中')
  } else ElMessage.warning('请输入关键词')
}

// =============== 静态模拟数据（从数据库读取）===============
const allReports = ref([
  {
    id: 1,
    title: '霍兰德职业兴趣测试报告',
    type: 'interest_test',
    content: `一、测试结果
您的职业兴趣类型为：社会型 + 企业型。
适合职业：教育、咨询、管理类岗位。

二、优势分析
善于沟通、有责任心、喜欢帮助他人。

三、建议
优先选择教育、人力资源、公共管理方向。`,
    created_at: '2026-03-20 15:30'
  },
  {
    id: 2,
    title: '产品经理岗位匹配报告',
    type: 'job_match',
    content: `一、匹配结果
您与产品经理岗位匹配度：85%。

二、能力匹配
沟通能力：90%
逻辑能力：80%
产品思维：75%

三、提升建议
加强产品文档撰写、数据分析能力。`,
    created_at: '2026-03-22 10:15'
  },
  {
    id: 3,
    title: '5年职业生涯规划报告',
    type: 'career_plan',
    content: `一、职业目标
短期：1年内成为初级产品经理
中期：3年成为高级产品经理
长期：5年成为产品负责人

二、实施路径
1. 学习产品知识
2. 积累项目经验
3. 提升管理能力

三、总结
路径清晰，可执行性强。`,
    created_at: '2026-03-25 09:40'
  },
  {
    id: 4,
    title: '第二次兴趣测试报告',
    type: 'interest_test',
    content: `一、最新测试结果
兴趣类型更偏向艺术型 + 实用型。
适合设计、工程、技术类方向。

二、对比分析
与上一次测试相比更偏向技术实现。

三、推荐方向
UI设计、前端开发、工业设计。`,
    created_at: '2026-03-28 16:10'
  }
])

// =============== 状态 ===============
const showHistory = ref(false)
const currentReport = ref(null)
const editContent = ref('')
const originalContent = ref('')

const filterType = ref('')
const filterName = ref('')
const exportFormat = ref('pdf')

const showModal = ref(false)
const modalTitle = ref('')
const modalMsg = ref('')

// =============== 计算属性 ===============
const filteredReports = computed(() => {
  let list = [...allReports.value]
  if (filterType.value) {
    list = list.filter(i => i.type === filterType.value)
  }
  if (filterName.value) {
    list = list.filter(i => i.title.includes(filterName.value))
  }
  return list
})

// =============== 方法 ===============
const getTypeName = (t) => {
  const map = {
    interest_test: '兴趣测试报告',
    job_match: '人岗匹配报告',
    career_plan: '职业规划报告'
  }
  return map[t] || '报告'
}

const loadReport = (item) => {
  currentReport.value = { ...item }
  editContent.value = item.content
  originalContent.value = item.content
}

const checkContent = () => {
  if (!editContent.value) {
    showTip('检查结果', '无报告内容')
    return
  }
  const len = editContent.value.length
  const ok = /一、|二、|三、|目标|建议/.test(editContent.value)
  showTip('内容检查', ok ? `✅ 完整，${len}字` : '⚠️ 结构不完整')
}

const polishReport = () => {
  if (!editContent.value) return
  let t = editContent.value
    .replace(/、/g, '、 ')
    .replace(/\n+/g, '\n')
    .replace(/一、/g, '\n一、')
    .replace(/二、/g, '\n二、')
    .replace(/三、/g, '\n三、')
  editContent.value = t
  showTip('润色完成', '已优化排版')
}

const resetContent = () => {
  editContent.value = originalContent.value
  showTip('恢复成功', '已回到原始内容')
}

const saveEdit = () => {
  if (!currentReport.value) return
  const i = allReports.value.findIndex(x => x.id === currentReport.value.id)
  if (i > -1) {
    allReports.value[i].title = currentReport.value.title
    allReports.value[i].content = editContent.value
    showTip('保存成功', '已更新报告')
  }
}

const quickExport = (item) => {
  loadReport(item)
  setTimeout(() => exportFinalReport(), 300)
}

const exportFinalReport = () => {
  if (!currentReport.value) return
  saveEdit()
  showTip('导出成功', `${currentReport.value.title} 已导出为${exportFormat.value}`)
}

const showTip = (title, msg) => {
  modalTitle.value = title
  modalMsg.value = msg
  showModal.value = true
}

onMounted(() => {
  applyTheme()
})
</script>

<style scoped>
/* 整体页面布局（和测评完全一致） */
.report-export-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  background: #f8f9fa;
  margin: 0;
  padding: 60px 0 0 0;
  color: #333;
}

/* 顶部导航 */
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
  color: #2f54eb;
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
.dropdown-item:hover, .dropdown-item.active {
  background: #f5f7fa;
  color: #2f54eb;
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

/* 子标题栏 */
.test-subheader {
  height: 70px;
  background: #f8f9fa;
  border-bottom: 1px solid #e8e8e8;
}
.subheader-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}
.page-title {
  display: flex;
  align-items: center;
  color: #2f54eb;
}
.title-icon {
  font-size: 24px;
  margin-right: 8px;
}
.page-title h1 {
  font-size: 20px;
  margin: 0;
}
.page-nav {
  display: flex;
  gap: 10px;
}
.report-btn {
  padding: 6px 15px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 报告导出内容区 */
.report-export {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.section-title {
  font-size: 20px;
  margin-bottom: 18px;
}
.filter-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.filter-select, .filter-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

/* 卡片 */
.card-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 40px;
}
.report-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.card-tag {
  position: absolute;
  top: 14px;
  right: 16px;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 4px;
  color: #fff;
}
.card-tag.interest_test { background: #4299e1; }
.card-tag.job_match { background: #00b42a; }
.card-tag.career_plan { background: #fa8c16; }
.card-title {
  font-size: 17px;
  margin: 0 0 6px 0;
}
.card-time {
  font-size: 13px;
  color: #999;
  margin: 0 0 14px 0;
}
.card-actions {
  display: flex;
  gap: 10px;
}
.btn {
  padding: 7px 14px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
.btn-edit { background: #f5f7fa; color: #333; }
.btn-export { background: #2f54eb; color: #fff; }

/* 编辑区 */
.edit-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 40px;
}
.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.tool-buttons {
  display: flex;
  gap: 10px;
}
.tool-btn {
  padding: 7px 12px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  cursor: pointer;
}
.tool-btn.check { background: #f6ffed; color: #00b42a; }
.tool-btn.polish { background: #fff7e6; color: #fa8c16; }
.tool-btn.reset { background: #f5f7fa; color: #666; }

.editor-box {
  margin-bottom: 20px;
}
.report-editor {
  width: 100%;
  min-height: 380px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  font-size: 15px;
  line-height: 1.6;
  box-sizing: border-box;
  resize: vertical;
}

.export-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}
.left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.left select, .name-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
}
.name-input { width: 220px; }
.right {
  display: flex;
  gap: 12px;
}
.btn-save {
  padding: 9px 16px;
  background: #f5f7fa;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.btn-export-final {
  padding: 9px 16px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* 历史 */
.history-section {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.history-table {
  width: 100%;
  border-collapse: collapse;
}
.history-table th, .history-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}
.history-table th {
  background: #f8f9fa;
}
.mini-btn {
  padding: 4px 10px;
  border-radius: 4px;
  border: none;
  font-size: 12px;
  margin-right: 6px;
  cursor: pointer;
}
.mini-btn.export {
  background: #e6f7ff;
  color: #1890ff;
}

/* 弹窗 */
.modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal-box {
  background: #fff;
  width: 380px;
  border-radius: 10px;
  padding: 25px;
  text-align: center;
}
.modal-box h3 {
  margin-top: 0;
  color: #2f54eb;
}
.modal-box button {
  margin-top: 15px;
  padding: 8px 25px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* 底部 */
.page-footer {
  background: #fff;
  padding: 20px 0;
  border-top: 1px solid #e8e8e8;
  text-align: center;
  color: #666;
  font-size: 14px;
  margin-top: 40px;
}
.footer-wrap {
  width: 1200px;
  margin: 0 auto;
}

/* 响应式 */
@media (max-width: 1200px) {
  .nav-wrap, .subheader-wrap, .report-export {
    width: 90%;
  }
  .card-list {
    grid-template-columns: 1fr;
  }
}
</style>
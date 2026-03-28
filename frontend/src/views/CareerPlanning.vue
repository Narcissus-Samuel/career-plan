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
            <div><b>目标岗位：</b> {{ targetJob || '日语翻译' }}</div>
            <div><b>生成时间：</b> {{ reportTime }}</div>
            <div class="right-btns">
              <el-button type="primary" @click="generateReport"> 🔄 重新生成 </el-button>
              <el-button type="warning" @click="exportReport"> 📥 导出PDF </el-button>
            </div>
          </div>

          <!-- 报告内容（已全部美化排版） -->
          <div class="report-content-section">
            <div class="section-title"><i class="icon">📊</i> 报告详情</div>

            <!-- 报告标题 -->
            <div class="report-title-box">
              <h1>职业生涯发展报告：从技术开发转向日语翻译的转型规划</h1>
              <p class="subtitle">——基于南华大学软件工程背景学生的个性化发展路径</p>
            </div>

            <!-- 报告说明 -->
            <div class="report-tip blue">
              <strong>报告说明：</strong>
              本报告严格依据您提供的完整数据生成，不套用通用模板。您的核心特征是——<br>
              <span class="highlight">已具备头部互联网公司前端开发实战经验的技术人才，正主动寻求向语言服务与跨文化职能方向转型</span>。
              这并非“转行失败”，而是高阶能力迁移（逻辑思维、系统理解、快速学习）与新领域价值重构的战略选择。
              报告将直面现实差距，但更聚焦可达成的跃迁路径。
            </div>

            <!-- 一、自我认知 -->
            <div class="section">
              <h3 class="section-head">一、自我认知总结：被低估的复合型潜力</h3>
              <p>您不是“零基础转行者”，而是一位拥有<strong>扎实工程底色+真实商业场景历练+强学习迁移能力</strong>的复合型人才。以下分析全部锚定您的具体数据：</p>

              <div class="card green">
                <h4>✅ 教育与学术基础坚实</h4>
                <p>南华大学软件工程本科（GPA 3.44，专业前10%），证明您具备优秀的抽象建模能力、结构化思维与持续学习纪律性——这些恰恰是高质量笔译/口译所需的底层认知能力。</p>
              </div>

              <div class="card green">
                <h4>✅ 实战经历含金量突出</h4>
                <p>字节跳动前端开发实习，绝非普通实习。您熟悉敏捷协作流程、跨职能对齐、线上系统交付，能快速理解客户业务系统运作逻辑，大幅提升商务日语场景下的术语准确率与沟通效率。</p>
              </div>

              <div class="card green">
                <h4>✅ 技术栈呈现独特优势</h4>
                <p>Python + Java 双栈 → 多语言语法迁移能力，为日语学习提供认知脚手架；<br>
                MySQL + 前端 → 对数据结构、业务流程天然敏感，<strong>远超纯语言背景者</strong>。</p>
              </div>

              <div class="card green">
                <h4>✅ 软能力画像清晰且可信</h4>
                <p>学习能力（4/5）是您的王牌；实习能力（4/5）与责任心突出；兴趣测评C型4.5分、I型3.5分，<strong>完美契合翻译+行政+跨文化协调职能</strong>。</p>
              </div>

              <div class="card yellow">
                <h4>⚠️ 待激活的隐藏资产</h4>
                <p>您未提供证书、项目细节，但E型得分仅1.5分，说明您天然排斥纯销售角色——恰恰印证您选择的是以专业能力为根基的服务型岗位，这是清醒的职业判断。</p>
              </div>
            </div>

            <!-- 二、人岗匹配 -->
            <div class="section">
              <h3 class="section-head">二、人岗匹配分析：优势显著，差距精准可控</h3>
              <el-table :data="matchTable" border stripe style="width:100%;margin-top:12px;">
                <el-table-column prop="dim" label="维度" align="center" />
                <el-table-column prop="status" label="匹配情况" align="center" />
                <el-table-column prop="desc" label="关键证据与解读" />
              </el-table>

              <div class="report-tip red" style="margin-top:16px;">
                <strong>🔑 差距本质诊断：</strong><br>
                您与目标岗位的差距<strong>不在能力底层，而在能力载体（中文→日语）与领域知识</strong>。
                这不是能力缺陷，而是<strong>技能树的定向移植</strong>——您已有的学习方法论、工程化执行习惯是绝大多数纯语言求职者不具备的稀缺资产。
              </div>
            </div>

            <!-- 三、职业路径 -->
            <div class="section">
              <h3 class="section-head">三、职业发展路径：立足翻译，延伸为“技术+语言”复合型专家</h3>
              <p>基于行业真实晋升逻辑，为您定制<strong>双轨发展路径</strong>，规避“翻译岗天花板低”的常见困境：</p>

              <div class="path-box">
                <div class="path-item">
                  <h4>▶ 主路径：专业翻译 → 行业解决方案专家</h4>
                  <div class="flow">
                    日语翻译（基础岗）
                    <span>→</span>
                    垂直领域翻译专家（技术文档/IT本地化）
                    <span>→</span>
                    中日IT项目协调经理
                  </div>
                  <p class="info">您的软件工程+前端经验，让您在IT、电商、SaaS领域翻译具备绝对壁垒！</p>
                </div>

                <div class="path-item">
                  <h4>▶ 辅路径：翻译+行政 → 中日企业运营枢纽</h4>
                  <div class="flow">
                    日语翻译（基础岗）
                    <span>→</span>
                    中日业务运营支持
                    <span>→</span>
                    中日合资公司运营管理
                  </div>
                  <p class="info">贴合岗位JD：资质审核、数据整理、客户管理、数字化运营</p>
                </div>
              </div>

              <div class="report-tip green" style="margin-top:12px;">
                💡 <strong>关键提醒：</strong>
                拒绝“翻译只是过渡”的心态。您的技术背景是<strong>放大翻译价值的杠杆</strong>——
                当别人在翻译文案时，您能优化前端逻辑；当别人整理数据时，您能写自动化脚本。这才是不可替代性。
              </div>
            </div>

            <!-- 四、行动计划 -->
            <div class="section">
              <h3 class="section-head">四、分阶段行动计划：以3个月为单位，结果可验证</h3>

              <div class="plan-section">
                <div class="plan-title blue">📅 短期（0–3个月）：筑基·认证突破</div>
                <el-table :data="plan1" border stripe style="width:100%;">
                  <el-table-column prop="title" label="目标" align="center" />
                  <el-table-column prop="action" label="具体行动" />
                  <el-table-column prop="check" label="验证方式" align="center" />
                  <el-table-column prop="advantage" label="您的独特优势" />
                </el-table>
              </div>

              <div class="plan-section">
                <div class="plan-title orange">📅 中期（4–12个月）：实战·场景扎根</div>
                <el-table :data="plan2" border stripe style="width:100%;">
                  <el-table-column prop="title" label="目标" align="center" />
                  <el-table-column prop="action" label="具体行动" />
                  <el-table-column prop="check" label="验证方式" align="center" />
                  <el-table-column prop="risk" label="风险控制点" />
                </el-table>
              </div>

              <div class="plan-section">
                <div class="plan-title purple">📅 长期（1–3年）：定义·价值升维</div>
                <el-table :data="plan3" border stripe style="width:100%;">
                  <el-table-column prop="title" label="目标" align="center" />
                  <el-table-column prop="action" label="具体行动" />
                  <el-table-column prop="success" label="成功标志" />
                </el-table>
              </div>
            </div>
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
import { ref, onMounted } from 'vue'
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
const targetJob = ref('日语翻译')
const matchScore = ref(68)

// 表格数据
const matchTable = ref([
  { dim: '硬技能', status: '❌ 当前不匹配', desc: '无日语证书；无翻译实操；需系统补足' },
  { dim: '软能力', status: '✅ 高度匹配', desc: '学习/责任/沟通/协作6项达标，2项超配；前端跨团队协作经验直接复用' },
  { dim: '岗位特质', status: '✅ 深层契合', desc: 'C型+I型人格适配审核/整理/分析；技术背景避免术语误译' }
])

const plan1 = ref([
  { title: '拿下JLPT N2', action: '每日2h语法+刷题；每周3篇技术文档翻译', check: 'N2考试140+', advantage: '技术文档逻辑清晰，字节语料现成' },
  { title: '构建翻译作品集', action: '项目README翻译；Python生成日语数据字典', check: 'GitHub双语展示', advantage: '技术+翻译双重壁垒' },
  { title: '行业知识输入', action: '日文运营白皮书+免税店网站研究', check: '输出中日双语checklist', advantage: '前端经验快速理解网站结构' }
])

const plan2 = ref([
  { title: '首份翻译实习/兼职', action: '主攻IT本地化/跨境电商；强调技术+翻译', check: '3份验收交付物', risk: '优先中小日企，降低竞争' },
  { title: '行政-技术交叉能力', action: 'Airtable/Notion日语系统；Python自动化归档', check: '可演示工具+手册', risk: '围绕真实需求，不为学而学' },
  { title: '考取JLPT N1', action: 'N1阅读听力；商务场景口语训练', check: 'N1考试130+', risk: '用字节场景模拟日语会议' }
])

const plan3 = ref([
  { title: '成为技术翻译顾问', action: 'LinkedIn个人品牌；SaaS日文准入翻译包', success: '付费客户≥2家，单价500+/千字' },
  { title: '打通中日IT职场通道', action: '赴日工作/转岗；三维经验积累', success: '中日数字化落地关键接口人' }
])

const fetchReportData = async () => {
  const loading = ElLoading.service({ text: 'AI生成报告中...' })
  try {
    reportVisible.value = true
    targetJob.value = '日语翻译'
    reportTime.value = new Date().toLocaleString()
  } catch (e) {
    ElMessage.error('生成失败')
  } finally {
    loading.close()
  }
}

const generateReport = () => fetchReportData()
const exportReport = () => {
  html2pdf().set({
    margin:10, filename:`日语翻译职业规划报告.pdf`,
    html2canvas:{scale:2}, jsPDF:{format:'a4'}
  }).from(document.querySelector('.report-content-section')).save()
  ElMessage.success('导出成功')
}

const toggleUserMenu = () => isUserMenuOpen.value = !isUserMenuOpen.value
const handleLogout = () => { localStorage.clear(); router.push('/'); ElMessage.success('退出成功') }
const goToFeature = (t) => router.push({ '测评':'/interest-test','分析':'/ability-analysis','规划':'/development-path','导出':'/report-export'}[t]||'/')
const handleSearch = () => ElMessage.warning('搜索功能开发中')
const toggleTheme = () => {}

onMounted(() => fetchReportData())
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

.main-content { padding-top:70px; width:1200px; margin:0 auto; }
.page-header-card { background:linear-gradient(90deg,#409eff,#1989fa); color:#fff; padding:20px 24px; border-radius:12px; margin-bottom:20px; }
.page-header-card h2 { margin:0 0 8px; font-size:20px; }
.page-header-card p { margin:0; opacity:0.9; font-size:14px; }

.report-container { width:100%; }
.report-card { border-radius:12px; overflow:hidden; }
.report-header-bar { display:flex; justify-content:space-between; align-items:center; padding:16px 20px; background:#f8f9fa; border-bottom:1px solid #eee; }
.right-btns { display:flex; gap:10px; }

.report-content-section { padding:20px; }
.section-title { font-size:18px; font-weight:bold; margin-bottom:16px; color:#333; display:flex; align-items:center; gap:8px; }
.icon { color:#409eff; }

/* 报告美化样式 */
.report-title-box { margin-bottom:20px; }
.report-title-box h1 { font-size:22px; color:#1989fa; margin:0; }
.report-title-box .subtitle { font-size:14px; color:#666; margin-top:6px; }

.report-tip { padding:14px 16px; border-radius:8px; line-height:1.7; margin:12px 0; }
.report-tip.blue { background:#e8f4ff; border-left:4px solid #409eff; }
.report-tip.red { background:#fff1f0; border-left:4px solid #f56c6c; }
.report-tip.green { background:#f0f9ff; border-left:4px solid #00b42a; }
.highlight { color:#1989fa; font-weight:bold; }

.section { margin:28px 0; }
.section-head { font-size:19px; color:#333; padding-left:10px; border-left:4px solid #409eff; margin-bottom:14px; }

.card { padding:14px 16px; border-radius:8px; margin-bottom:12px; line-height:1.7; }
.card.green { background:#f0f9ff; border:1px solid #b3e5fc; }
.card.yellow { background:#fff8e1; border:1px solid #ffecb3; }
.card h4 { margin:0 0 6px; color:#1989fa; font-size:15px; }

.path-box { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:16px 0; }
.path-item { padding:16px; background:#fafafa; border-radius:10px; border:1px solid #eee; }
.path-item h4 { margin:0 0 10px; color:#333; font-size:15px; }
.flow { font-size:14px; color:#1989fa; font-weight:bold; display:flex; align-items:center; gap:8px; margin-bottom:8px; }
.flow span { color:#999; }
.path-item .info { font-size:13px; color:#666; margin:0; }

.plan-section { margin:20px 0; }
.plan-title { padding:10px 14px; border-radius:8px; color:#fff; font-weight:bold; margin-bottom:10px; }
.plan-title.blue { background:#409eff; }
.plan-title.orange { background:#ff9800; }
.plan-title.purple { background:#722ed1; }

.loading-box { display:flex; flex-direction:column; align-items:center; justify-content:center; height:60vh; gap:12px; color:#666; }
</style>
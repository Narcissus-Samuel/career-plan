<template>
  <div class="ability-profile-page">
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item active" @click="$router.push('/ability-analysis')">职业规划</li>
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
          <div class="nav-search-wrap">
            <input type="text" class="nav-search-input" placeholder="搜索..." @keyup.enter="handleSearch" />
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

    <div class="profile-container">
      <div class="step-content glass-panel">
        <h2 class="section-title">🤖 AI 学生就业能力画像</h2>

        <div v-if="generatingProfile" class="loading-container">
          <div class="loading-spinner">🔄</div>
          <p class="loading-text">AI 正在分析你的简历数据，生成多维度能力画像...</p>
        </div>

        <div v-else-if="profileGenerated" class="profile-result">
          <!-- 基础信息横向卡片 -->
          <div class="basic-info-card card-effect">
            <div class="info-card-item">
              <span class="info-icon">👤</span>
              <span class="info-label">姓名</span>
              <span class="info-value">{{ profile.name || '未填写' }}</span>
            </div>
            <div class="info-card-divider"></div>
            <div class="info-card-item">
              <span class="info-icon">📞</span>
              <span class="info-label">联系方式</span>
              <span class="info-value">{{ profile.phone || '未填写' }} | {{ profile.email || '未填写' }}</span>
            </div>
            <div class="info-card-divider"></div>
            <div class="info-card-item">
              <span class="info-icon">📊</span>
              <span class="info-label">简历完整度</span>
              <span class="info-value">{{ profile.completeness }}%</span>
            </div>
          </div>

          <div class="core-scores">
            <div class="score-card card-effect">
              <span class="score-type">完整度评分</span>
              <span class="score-num">{{ profile.completeness }}%</span>
              <div class="score-bar">
                <div class="bar-fill" :style="{ width: profile.completeness + '%', background: getScoreColor(profile.completeness) }"></div>
              </div>
              <p class="score-desc">{{ getCompletenessDesc(profile.completeness) }}</p>
            </div>
            <div class="score-card card-effect">
              <span class="score-type">综合竞争力</span>
              <!-- 修改1：显示--或数值 -->
              <span class="score-num">{{ isCompetitiveScoreValid ? getCompetitiveScore() + '%' : '--' }}</span>
              <div class="score-bar">
                <!-- 修改2：无数据时隐藏进度条填充 -->
                <div class="bar-fill" v-if="isCompetitiveScoreValid" :style="{ width: getCompetitiveScore() + '%', background: getScoreColor(getCompetitiveScore()) }"></div>
                <!-- 无数据时显示空进度条 -->
                <div v-else class="bar-empty" style="width: 100%; height: 100%; background: #e2e8f0;"></div>
              </div>
              <p class="score-desc">{{ isCompetitiveScoreValid ? getCompetitiveDesc(getCompetitiveScore()) : '暂无足够简历信息评估综合竞争力' }}</p>
            </div>
          </div>

          <div class="dimension-scores">
            <h3 class="dimension-title">📊 软能力维度评分</h3>
            <div class="radar-chart-container card-effect">
              <div id="softAbilityRadarChart" class="radar-chart"></div>
            </div>
            <div class="dimension-grid">
              <div v-for="(item, key) in getSoftAbilityList()" :key="key" class="dimension-item card-effect">
                <div class="dimension-name">{{ key }}</div>
                <div class="dimension-bar">
                  <div class="bar-fill" :style="{ width: (item.score * 20) + '%', background: getScoreColor(item.score * 20) }"></div>
                </div>
                <div class="dimension-score">{{ item.score === 0 ? '--' : item.score * 20 }}分</div>
                <div class="dimension-tip">{{ item.description || '暂无评价' }}</div>
              </div>
            </div>
          </div>

          <div class="skill-cert-section">
            <div class="skill-card card-effect">
              <h3 class="skill-title">💻 专业技能</h3>
              <div class="tags">
                <span v-for="skill in profile.skills" :key="skill" class="tag skill-tag">
                  {{ skill }} <small>(熟练度{{ getSkillProficiency(skill) }}%)</small>
                </span>
                <span v-if="!profile.skills.length" class="empty-tag">暂无技能信息</span>
              </div>
            </div>
            <div class="cert-card card-effect">
              <h3 class="cert-title">📜 证书资质</h3>
              <div class="tags">
                <span v-for="cert in profile.certificates" :key="cert" class="tag cert-tag">
                  {{ cert }}
                </span>
                <span v-if="!profile.certificates.length" class="empty-tag">暂无证书信息</span>
              </div>
            </div>
          </div>

          <div class="experience-section">
            <div class="exp-card card-effect">
              <h3 class="exp-title">🎓 教育经历</h3>
              <div class="exp-content">
                <p v-if="profile.education_json.school">
                  {{ profile.education_json.school }} {{ profile.education_json.degree }} - {{ profile.education_json.major || '未填写专业' }}
                  <span v-if="profile.education_json.gpa"> | 绩点：{{ profile.education_json.gpa }}</span>
                  <span v-if="profile.education_json.ranking"> | 排名：{{ profile.education_json.ranking }}</span>
                </p>
                <p v-else>{{ profile.education_text || '暂无教育经历' }}</p>
              </div>
            </div>
            <div class="exp-card card-effect">
              <h3 class="exp-title">💼 工作/实习经历</h3>
              <div class="exp-content">
                <div v-if="profile.work_json.length">
                  <div v-for="(work, idx) in profile.work_json" :key="idx" class="work-item">
                    <p class="work-header">{{ work.company }} {{ work.position }} <span class="date-range">({{ work.date_range || '时间未填写' }})</span></p>
                    <p class="work-content">职责：{{ work.responsibilities || '未填写' }}</p>
                    <p class="work-achievements">成果：{{ work.achievements || '无' }}</p>
                    <hr v-if="idx < profile.work_json.length - 1">
                  </div>
                </div>
                <p v-else>{{ profile.work_text || '暂无工作/实习经历' }}</p>
              </div>
            </div>
            <div class="exp-card card-effect">
              <h3 class="exp-title">📖 项目经历</h3>
              <div class="exp-content">
                <div v-if="profile.project_json.length">
                  <div v-for="(proj, idx) in profile.project_json" :key="idx" class="project-item">
                    <p class="project-header">{{ proj.project_name }} <span class="role">({{ proj.role || '参与者' }})</span></p>
                    <p class="project-tech">技术栈：{{ proj.technology_stack || '未填写' }}</p>
                    <p class="project-desc">描述：{{ proj.description || '未填写' }}</p>
                    <p class="project-outcome">成果：{{ proj.outcome || '无' }}</p>
                    <hr v-if="idx < profile.project_json.length - 1">
                  </div>
                </div>
                <p v-else>{{ profile.project_text || '暂无项目经历' }}</p>
              </div>
            </div>
          </div>

          <div class="ai-evaluation card-effect">
            <h3 class="eval-title">📝 AI 综合能力评价</h3>
            <div class="eval-content">{{ profile.aiEvaluation }}</div>
          </div>

          <div class="profile-actions">
            <el-button class="btn-effect" @click="regenerateProfile" :loading="generatingProfile">重新生成画像</el-button>
            <!-- 新增：重新填写学生信息按钮 -->
            <el-button class="btn-effect" type="info" @click="goToEditInfo">重新填写学生信息</el-button>
            <el-button class="btn-effect" type="primary" @click="exportProfile">导出能力画像</el-button>
            <!-- 修改：按钮文字改为兴趣测试 -->
            <el-button class="btn-effect" type="success" @click="goToInterestTest">兴趣测试</el-button>
          </div>
        </div>

        <div v-else class="empty-profile">
          <p class="empty-text">暂无能力画像数据，请先完成简历上传/手动录入</p>
          <el-button class="btn-effect" type="primary" @click="goBack">返回填写信息</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()

const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')

const token = localStorage.getItem('token')
const userId = ref(localStorage.getItem('userId') || 3)
const studentId = ref(route.query.studentId || localStorage.getItem('studentId') || 1)

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  headers: { Authorization: token ? `Bearer ${token}` : '' },
  timeout: 30000
})

const generatingProfile = ref(false)
const profileGenerated = ref(false)
const profile = reactive({
  id: '', user_id: '', name: '', phone: '', email: '', completeness: 0,
  skills: [], certificates: [], soft_abilities: {},
  education_text: '', education_json: {}, work_text: '', work_json: [],
  project_text: '', project_json: [], aiEvaluation: ''
})

// 修改3：计算属性 - 判断综合竞争力是否有效
const isCompetitiveScoreValid = computed(() => {
  const softAbilities = getSoftAbilityList()
  // 检查是否有至少一个软能力分数大于0
  return Object.values(softAbilities).some(item => item.score > 0)
})

let radarChartInstance = null

onMounted(() => {
  getProfileData()
})

watch(() => profile.soft_abilities, () => {
  if (profileGenerated.value) initRadarChart()
}, { deep: true })

const initRadarChart = () => {
  const chartDom = document.getElementById('softAbilityRadarChart')
  if (!chartDom) { return setTimeout(() => initRadarChart(), 120) }

  if (radarChartInstance) radarChartInstance.dispose()
  radarChartInstance = echarts.init(chartDom)

  const softAbilities = getSoftAbilityList()
  const categories = Object.keys(softAbilities)
  const values = Object.values(softAbilities).map(item => item.score * 20)

  const option = {
    title: { text: '软能力维度分布', left: 'center', textStyle: { fontSize: 16, fontWeight: 600, color: '#1f2937' } },
    tooltip: { trigger: 'item', formatter: '{b}: {c}分' },
    legend: { orient: 'vertical', right: 10, top: 'center', data: ['个人能力评分'] },
    radar: {
      indicator: categories.map(name => ({ name, max: 100, min: 0 })),
      shape: 'polygon', splitNumber: 5,
      name: { textStyle: { color: '#334155', fontSize: 12 } },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      splitArea: { areaStyle: { color: ['rgba(255,255,255,0.8)', 'rgba(245,247,250,0.8)'] } }
    },
    series: [{
      name: '个人能力评分', type: 'radar',
      data: [{
        value: values, name: '个人能力评分',
        areaStyle: { color: 'rgba(37, 99, 235, 0.2)' },
        lineStyle: { color: '#2563eb', width: 2 },
        itemStyle: { color: '#2563eb', borderColor: '#fff', borderWidth: 2 },
        symbol: 'circle', symbolSize: 8
      }]
    }],
    backgroundColor: 'transparent'
  }

  radarChartInstance.setOption(option)
  const resizeFn = () => radarChartInstance?.resize()
  window.addEventListener('resize', resizeFn)
}

const getProfileData = async () => {
  try {
    generatingProfile.value = true
    const res = await api.get(`/profile/${studentId.value}`)
    const data = res.data
    Object.assign(profile, data)
    profile.aiEvaluation = generateAIEvaluation(data)
    profileGenerated.value = true
    await nextTick()
    initRadarChart()
  } catch (err) {
    console.error('获取画像失败', err)
    ElMessage.error('获取能力画像失败：' + (err.response?.data?.error || '请先完成简历'))
    profileGenerated.value = false
  } finally {
    generatingProfile.value = false
  }
}

// 核心修改：信息不足时软能力默认0分，不再给3分（60分）兜底
const getSoftAbilityList = () => {
  const result = {}
  
  // 1. 优先使用后端返回的软能力数据（大模型分析结果）
  if (typeof profile.soft_abilities === 'object' && profile.soft_abilities !== null) {
    Object.entries(profile.soft_abilities).forEach(([key, value]) => {
      // 兼容后端两种返回格式：直接数字 或 {score, description} 对象
      if (typeof value === 'number') {
        // 后端返回1-5分制，直接使用
        const score = Math.min(5, Math.max(0, value)) // 允许0分
        result[key] = { 
          score: score, 
          description: score === 0 ? '暂无足够简历信息评估该能力' : 'AI分析简历得出的能力评估' 
        }
      } else if (value && typeof value === 'object' && 'score' in value) {
        // 后端返回完整对象，直接使用
        const score = Math.min(5, Math.max(0, value.score))
        result[key] = {
          score: score,
          description: value.description || (score === 0 ? '暂无足够简历信息评估该能力' : 'AI分析暂无详细描述')
        }
      }
    })
  }

  // 2. 兜底逻辑：如果后端没有返回任何软能力数据，使用默认维度且分数为0
  if (Object.keys(result).length === 0) {
    const defaultAbilities = {
      '创新能力': { score: 0, description: '暂无足够简历信息评估该能力' },
      '学习能力': { score: 0, description: '暂无足够简历信息评估该能力' },
      '抗压能力': { score: 0, description: '暂无足够简历信息评估该能力' },
      '沟通能力': { score: 0, description: '暂无足够简历信息评估该能力' },
      '实习能力': { score: 0, description: '暂无足够简历信息评估该能力' }
    }
    Object.assign(result, defaultAbilities)
  }

  return result
}

const generateAIEvaluation = (data) => {
  const skillsStr = data.skills?.length ? data.skills.join('、') : '无'
  const certsStr = data.certificates?.length ? data.certificates.join('、') : '无'
  const eduStr = data.education_text || '无'
  const workStr = data.work_text || '无'
  const completeness = data.completeness || 0

  let baseEval = `简历完整度${completeness}%，教育背景：${eduStr}。掌握技能：${skillsStr}；证书：${certsStr}。${workStr ? '具备实习经历，' : '暂无实习经历，'}`

  const soft = getSoftAbilityList()
  const arr = Object.entries(soft).sort((a, b) => b[1].score - a[1].score)
  const top = arr[0], low = arr[arr.length - 1]
  
  if (top[1].score === 0) {
    baseEval += '当前简历信息不足，无法评估软能力强弱，建议补充完整经历后再生成画像。'
  } else {
    baseEval += `强项${top[0]}(${top[1].score*20}分)，${top[1].description}；需提升${low[0]}(${low[1].score*20}分)。`
  }

  if (completeness >= 80) baseEval += '整体竞争力优秀，建议精准投递匹配岗位。'
  else if (completeness >= 60) baseEval += '竞争力良好，补充项目/实习更有优势。'
  else baseEval += '竞争力偏弱，优先补齐简历关键信息与实践。'
  return baseEval
}

const regenerateProfile = async () => {
  try {
    await ElMessageBox.confirm('确定重新生成画像？当前数据将更新', '提示', { type: 'warning' })
    generatingProfile.value = true
    await getProfileData()
    ElMessage.success('重新生成成功')
  } catch (e) { if (e !== 'cancel') ElMessage.error('生成失败') } finally { generatingProfile.value = false }
}

const exportProfile = async () => {
  try {
    const res = await api.post('/profile/export', { student_id: studentId.value, format: 'pdf', profile_data: profile }, { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url; a.download = `能力画像_${profile.name||'用户'}.pdf`
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) { ElMessage.error('导出失败：后端暂未实现或网络异常') }
}

const getScoreColor = (s) => s>=80?'#10b981':s>=60?'#f59e0b':s>=40?'#f97316':'#ef4444'
const getCompletenessDesc = (s)=>{
  if(s>=90) return '信息极完整，覆盖全部核心维度'
  if(s>=80) return '信息优秀，仅少量字段缺失'
  if(s>=70) return '信息良好，建议补充亮点经历'
  if(s>=60) return '信息一般，需补齐关键能力资料'
  return '信息偏低，优先完善技能与实践'
}

// 修改4：综合竞争力计算函数（仅在有效时返回数值）
const getCompetitiveScore = () => {
  // 如果无效，返回0（实际不会显示）
  if (!isCompetitiveScoreValid.value) return 0
  
  const soft = getSoftAbilityList()
  const avg = Object.values(soft).reduce((p,c)=>p+c.score,0)/Object.keys(soft).length*20
  return Math.round(profile.completeness*0.6 + avg*0.4)
}

const getCompetitiveDesc = (s)=>{
  if(s>=90) return '同批次竞争力极强，具备明显核心优势'
  if(s>=80) return '竞争力优秀，简历匹配度高'
  if(s>=70) return '竞争力良好，针对性补强即可'
  if(s>=60) return '竞争力一般，优先补齐短板软能力'
  return '竞争力偏弱，建议重排能力规划与实习'
}
const getSkillProficiency = (sk) => ['Python','Java','SQL','Vue.js','Spring Boot','JavaScript'].includes(sk)?80+Math.random()*20:60+Math.random()*30

const goBack = ()=>router.push('/student-ability')
// 新增：跳转至重新填写学生信息页面
const goToEditInfo = ()=>router.push('/student-ability')
// 修改：兴趣测试跳转函数（保持原有逻辑，仅改名）
const goToInterestTest = ()=>router.push({path:'/interest-test',query:{studentId:studentId.value}})
const toggleUserMenu = ()=>isUserMenuOpen.value=!isUserMenuOpen.value
const handleLogout = ()=>{localStorage.clear();isLogin.value=false;router.push('/');ElMessage.success('已退出')}
const toggleTheme = ()=>{darkMode.value=!darkMode.value;localStorage.setItem('darkMode',darkMode.value)}
const goToFeature = (t)=>{const m={'测评':'/interest-test','分析':'/ability-analysis','规划':'/development-path','导出':'/report-export'};router.push(m[t]||'/')}
const handleSearch = ()=>{const i=document.querySelector('.nav-search-input');if(i.value.trim())router.push(`/search?keyword=${encodeURIComponent(i.value.trim())}`)}
</script>

<style scoped>
/* 核心优化：卡片特效样式 */
.card-effect {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  /* 渐变边框效果 */
  border: double 1px transparent;
  background-image: linear-gradient(#ffffff, #ffffff), 
                    linear-gradient(135deg, #e0f2fe, #dbeafe, #f0f9ff);
  background-origin: border-box;
  background-clip: padding-box, border-box;
}
/* 悬浮放大+阴影加深特效 */
.card-effect:hover {
  transform: translateY(-5px) scale(1.01);
  box-shadow: 0 12px 24px rgba(0,0,0,0.08), 0 4px 8px rgba(37, 99, 235, 0.1);
}
/* 按钮强化特效 */
.btn-effect {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease !important;
}
.btn-effect::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.6s ease;
}
.btn-effect:hover::after {
  left: 100%;
}

/* 核心优化：基础信息横向卡片样式 */
.basic-info-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  border-radius: 16px;
  padding: 20px 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.info-card-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  text-align: center;
  justify-content: center;
}
.info-icon {
  font-size: 18px;
  color: #2563eb;
  transition: transform 0.3s ease;
}
.card-effect:hover .info-icon {
  transform: rotate(5deg) scale(1.1);
}
.info-label {
  font-weight: 600;
  color: #334155;
  font-size: 14px;
  min-width: 70px;
}
.info-value {
  color: #1e293b;
  font-size: 15px;
  font-weight: 500;
}
.info-card-divider {
  width: 1px;
  height: 30px;
  background: rgba(148, 163, 184, 0.2);
  margin: 0 10px;
  transition: opacity 0.3s ease;
}
.card-effect:hover .info-card-divider {
  opacity: 1;
  background: rgba(37, 99, 235, 0.3);
}

/* 整体视觉优化 */
.ability-profile-page {
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: linear-gradient(145deg, #f9fafc 0%, #eef2f7 100%);
  margin: 0;
  padding: 60px 0 40px 0;
  color: #1a2639;
}

.profile-container {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.9);
  padding: 40px;
  /* 淡入动画 */
  animation: fadeInUp 0.8s ease-out;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 30px 0;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(37, 99, 235, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}
.section-title::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 80px;
  height: 2px;
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  border-radius: 2px;
}

/* 评分卡片优化 */
.core-scores {
  display: flex;
  gap: 20px;
  margin-bottom: 35px;
}
.score-card {
  flex: 1;
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.04);
}
.score-type {
  display: block;
  font-size: 15px;
  color: #64748b;
  margin-bottom: 10px;
}
.score-num {
  display: block;
  font-size: 42px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
  transition: color 0.3s ease;
}
.card-effect:hover .score-num {
  color: #2563eb;
}
.score-bar {
  height: 10px;
  background: #f1f5f9;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 10px;
  position: relative;
}
.score-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, rgba(255,255,255,0.1), rgba(255,255,255,0.4));
  pointer-events: none;
}
.bar-fill {
  height: 100%;
  border-radius: 20px;
  transition: width 1s ease-in-out;
  background: linear-gradient(90deg, var(--fill-color), #3b82f6);
}
/* 修改5：新增空进度条样式 */
.bar-empty {
  height: 100%;
  border-radius: 20px;
  background: #e2e8f0;
}
.score-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

/* 软能力维度优化 */
.dimension-title {
  font-size: 19px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.radar-chart-container {
  width: 100%;
  height: 400px;
  margin-bottom: 30px;
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.04);
}
.radar-chart {
  width: 100%;
  height: 100%;
  transition: opacity 0.5s ease;
}
.card-effect:hover .radar-chart {
  opacity: 0.98;
}
.dimension-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 35px;
}
.dimension-item {
  background: #ffffff;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}
.dimension-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  font-size: 15px;
  transition: color 0.3s ease;
}
.card-effect:hover .dimension-name {
  color: #2563eb;
}
.dimension-bar {
  height: 8px;
  background: #f1f5f9;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 8px;
}
.dimension-score {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  margin-bottom: 4px;
}
.dimension-tip {
  font-size: 12px;
  color: #94a3b8;
  font-style: italic;
  line-height: 1.4;
}

/* 技能证书区域优化 */
.skill-cert-section {
  display: flex;
  gap: 20px;
  margin-bottom: 35px;
}
.skill-card, .cert-card {
  flex: 1;
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.04);
}
.skill-title, .cert-title {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: color 0.3s ease;
}
.card-effect:hover .skill-title,
.card-effect:hover .cert-title {
  color: #2563eb;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tag {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}
.tag::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}
.tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
.tag:hover::before {
  transform: translateX(0);
}
.skill-tag { 
  background: #eff6ff; 
  color: #1e40af; 
  border: 1px solid #dbeafe;
}
.cert-tag { 
  background: #f0fdf4; 
  color: #166534;
  border: 1px solid #dcfce7;
}
.tag small {
  font-size: 12px;
  opacity: 0.8;
  font-weight: normal;
}
.empty-tag {
  color: #94a3b8;
  font-size: 14px;
  padding: 8px 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

/* 经历区域优化 */
.experience-section {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 35px;
}
.exp-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.04);
}
.exp-title {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: color 0.3s ease;
}
.card-effect:hover .exp-title {
  color: #2563eb;
}
.exp-content {
  font-size: 14px;
  line-height: 1.6;
  color: #334155;
}
.work-item, .project-item {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed rgba(148, 163, 184, 0.1);
  transition: border-color 0.3s ease;
}
.card-effect:hover .work-item,
.card-effect:hover .project-item {
  border-color: rgba(37, 99, 235, 0.2);
}
.work-header, .project-header {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}
.date-range, .role {
  font-size: 12px;
  color: #64748b;
  font-weight: normal;
}
.work-content, .project-tech, .project-desc {
  margin-bottom: 4px;
  color: #475569;
}
.work-achievements, .project-outcome {
  color: #0f766e;
  font-size: 13px;
  font-weight: 500;
}

/* AI评价区域优化 */
.ai-evaluation {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.04);
  margin-bottom: 30px;
}
.eval-title {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.eval-content {
  font-size: 15px;
  line-height: 1.7;
  color: #334155;
  white-space: pre-line;
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  border-left: 3px solid #2563eb;
  transition: all 0.3s ease;
}
.card-effect:hover .eval-content {
  background: #f0f9ff;
  border-left-color: #3b82f6;
}

/* 按钮区域优化 */
.profile-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 20px;
}
:deep(.el-button) {
  border-radius: 8px !important;
  padding: 10px 24px !important;
  font-weight: 500 !important;
  transition: all 0.2s ease !important;
  position: relative;
  overflow: hidden;
}
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
}
:deep(.el-button--primary:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3) !important;
}
:deep(.el-button--success) {
  background: linear-gradient(135deg, #10b981, #34d399) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
}
:deep(.el-button--success:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3) !important;
}
/* 新增：info类型按钮样式优化 */
:deep(.el-button--info) {
  background: linear-gradient(135deg, #64748b, #94a3b8) !important;
  border: none !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.2) !important;
}
:deep(.el-button--info:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(100, 116, 139, 0.3) !important;
}

/* 空状态优化 */
.empty-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}
.empty-text {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 24px;
  line-height: 1.6;
}

/* 导航栏样式（保留原有） */
.top-nav {
  height: 60px;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
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
.avatar { width: 36px; height: 36px; border-radius: 50%; cursor: pointer; border: 2px solid #f0f0f0; transition: border 0.3s ease, transform 0.3s ease; }
.avatar:hover { border-color: #2f54eb; transform: scale(1.05); }
.user-menu { position: absolute; top: 50px; right: 0; width: 120px; background: #fff; box-shadow: 0 4px 16px rgba(0,0,0,0.12); border-radius: 8px; z-index: 9999; animation: fadeIn 0.3s ease; }
.user-menu .menu-item { padding: 10px 15px; font-size: 14px; cursor: pointer; height: auto; line-height: normal; margin: 0; color: #333; transition: background 0.3s ease; }
.user-menu .menu-item:hover { background: #f0f7ff; color: #333; }
.user-menu .logout { color: #ff4d4f; border-top: 1px solid #f0f0f0; }

/* 响应式优化 */
@media(max-width:768px) {
  .basic-info-card {
    flex-direction: column;
    gap: 15px;
    padding: 20px;
  }
  .info-card-divider {
    width: 80%;
    height: 1px;
    margin: 10px 0;
  }
  .info-card-item {
    width: 100%;
    justify-content: flex-start;
  }
  .core-scores { flex-direction: column; }
  .skill-cert-section { flex-direction: column; }
  .experience-section { grid-template-columns: 1fr; }
  .dimension-grid { grid-template-columns: 1fr; }
  .glass-panel { padding: 24px; }
  .nav-wrap { width: 95%; }
  .nav-menu { display: none; }
  .radar-chart-container { height: 300px; }
  /* 移动端弱化放大特效 */
  .card-effect:hover {
    transform: translateY(-3px) scale(1.005);
  }
  /* 移动端按钮换行 */
  .profile-actions {
    flex-wrap: wrap;
  }
}

/* 新增动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
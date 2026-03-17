<template>
  <div class="student-ability-page">
    <!-- 1. 顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item active" @click="$router.push('/student-ability')">岗位画像</li>
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

    <!-- 2. 主体内容 -->
    <div class="student-ability-container">
      <!-- 步骤指示器：仅在非第四步时显示 -->
      <div class="step-indicator" v-if="activeStep !== 3">
        <div class="step-item" :class="{ active: activeStep >= 0, completed: activeStep > 0 }">
          <div class="step-number">{{ activeStep > 0 ? '✓' : '1' }}</div>
          <div class="step-text">基础信息</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: activeStep >= 1, completed: activeStep > 1 }">
          <div class="step-number">{{ activeStep > 1 ? '✓' : '2' }}</div>
          <div class="step-text">简历信息</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: activeStep >= 2, completed: activeStep > 2 }">
          <div class="step-number">{{ activeStep > 2 ? '✓' : '3' }}</div>
          <div class="step-text">AI能力评分</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: activeStep >= 3 }">
          <div class="step-number">4</div>
          <div class="step-text">能力画像</div>
        </div>
      </div>

      <!-- 表单卡片容器 -->
      <div class="form-card" :class="{ 'result-card': activeStep === 3 }">
        <!-- 第一步：基础信息 -->
        <div v-if="activeStep === 0" class="form-content">
          <el-form :model="basicForm" label-width="120px" :rules="basicRules" ref="basicFormRef" class="info-form">
            <el-form-item label="用户名" prop="nickname">
              <el-input v-model="basicForm.nickname" placeholder="请输入用户名" size="large"></el-input>
            </el-form-item>
            <el-form-item label="姓名" prop="name">
              <el-input v-model="basicForm.name" placeholder="请输入真实姓名" size="large"></el-input>
            </el-form-item>
            <el-form-item label="性别" prop="gender">
              <el-select v-model="basicForm.gender" placeholder="请选择性别" size="large">
                <el-option label="男" value="男"></el-option>
                <el-option label="女" value="女"></el-option>
                <el-option label="保密" value="保密"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="学校" prop="school">
              <el-input v-model="basicForm.school" placeholder="请输入所在学校" size="large"></el-input>
            </el-form-item>
            <el-form-item label="专业" prop="major">
              <el-input v-model="basicForm.major" placeholder="请输入所学专业" size="large"></el-input>
            </el-form-item>
            <el-form-item label="年级" prop="grade">
              <el-select v-model="basicForm.grade" placeholder="请选择年级" size="large">
                <el-option label="大一" value="大一"></el-option>
                <el-option label="大二" value="大二"></el-option>
                <el-option label="大三" value="大三"></el-option>
                <el-option label="大四" value="大四"></el-option>
                <el-option label="研一" value="研一"></el-option>
                <el-option label="研二" value="研二"></el-option>
                <el-option label="研三" value="研三"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="学历" prop="education">
              <el-select v-model="basicForm.education" placeholder="请选择学历" size="large">
                <el-option label="本科" value="本科"></el-option>
                <el-option label="硕士" value="硕士"></el-option>
                <el-option label="博士" value="博士"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="联系方式" prop="phone">
              <el-input v-model="basicForm.phone" placeholder="请输入手机号码" size="large"></el-input>
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="basicForm.email" placeholder="请输入邮箱地址" size="large"></el-input>
            </el-form-item>
            <el-form-item label="自我介绍" prop="introduction">
              <el-input v-model="basicForm.introduction" type="textarea" rows="4" placeholder="请输入自我介绍（选填）" size="large"></el-input>
            </el-form-item>
            <el-form-item class="form-actions">
              <el-button type="primary" size="large" @click="nextStep" class="btn-next">下一步</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 第二步：简历信息 -->
        <div v-if="activeStep === 1" class="form-content">
          <div class="input-mode-tabs">
            <div class="tab-item" :class="{ active: inputMode === 'upload' }" @click="inputMode = 'upload'">
              <i class="icon-upload">📤</i>
              <span>上传简历</span>
            </div>
            <div class="tab-item" :class="{ active: inputMode === 'manual' }" @click="inputMode = 'manual'">
              <i class="icon-edit">✏️</i>
              <span>手动输入</span>
            </div>
          </div>

          <div v-if="inputMode === 'upload'" class="upload-mode">
            <el-upload
              class="resume-uploader"
              drag
              action="/api/upload/resume"
              :on-success="handleResumeUploadSuccess"
              :on-error="handleResumeUploadError"
              :before-upload="beforeResumeUpload"
              accept=".pdf,.doc,.docx"
            >
              <i class="el-icon-upload"></i>
              <div class="el-upload__text">
                <h3>拖放简历文件到此处</h3>
                <p>或 <em>点击上传</em>，支持 PDF、Word 格式（最大 10MB）</p>
              </div>
              <div class="el-upload__tip" slot="tip">
                系统将自动识别简历中的技能、证书、实习经历等信息
              </div>
            </el-upload>
            
            <div v-if="uploadedResume" class="uploaded-file">
              <el-card>
                <div class="file-info">
                  <i class="file-icon">📄</i>
                  <div class="file-details">
                    <div class="file-name">{{ uploadedResume.name }}</div>
                    <div class="file-size">{{ formatFileSize(uploadedResume.size) }}</div>
                  </div>
                  <el-button type="text" @click="removeResume">移除</el-button>
                </div>
                <el-button type="primary" size="small" @click="parseResume">解析简历信息</el-button>
              </el-card>
            </div>
          </div>

          <div v-if="inputMode === 'manual'" class="manual-mode">
            <el-form :model="skillForm" label-width="120px" ref="skillFormRef" class="skill-form">
              <el-form-item label="专业技能">
                <div class="tag-input-container">
                  <el-tag
                    v-for="(skill, index) in skillForm.skills"
                    :key="index"
                    closable
                    @close="handleTagClose(skillForm.skills, index)"
                    style="margin: 0 8px 8px 0;"
                  >
                    {{ skill }}
                  </el-tag>
                  <el-input
                    v-model="tempSkill"
                    placeholder="输入技能后按回车添加（如Python、Java）"
                    @keyup.enter="handleTagAdd(skillForm.skills, tempSkill)"
                    style="width: 200px; margin-top: 8px;"
                    size="large"
                  ></el-input>
                </div>
              </el-form-item>
              <el-form-item label="已获证书">
                <div class="tag-input-container">
                  <el-tag
                    v-for="(cert, index) in skillForm.certificates"
                    :key="index"
                    closable
                    @close="handleTagClose(skillForm.certificates, index)"
                    style="margin: 0 8px 8px 0;"
                  >
                    {{ cert }}
                  </el-tag>
                  <el-input
                    v-model="tempCert"
                    placeholder="输入证书后按回车添加（如计算机二级、英语六级）"
                    @keyup.enter="handleTagAdd(skillForm.certificates, tempCert)"
                    style="width: 200px; margin-top: 8px;"
                    size="large"
                  ></el-input>
                </div>
              </el-form-item>
              <el-form-item label="实习经历">
                <el-input v-model="skillForm.internship" type="textarea" rows="4" placeholder="请简要描述实习经历，包括公司、岗位、主要职责和成果" size="large"></el-input>
              </el-form-item>
              <el-form-item label="项目经历">
                <el-input v-model="skillForm.project" type="textarea" rows="4" placeholder="请简要描述项目经历，包括项目名称、角色、使用技术、成果等" size="large"></el-input>
              </el-form-item>
            </el-form>
          </div>

          <div class="form-actions resume-actions">
            <el-button size="large" @click="prevStep" class="btn-prev">上一步</el-button>
            <el-button type="primary" size="large" @click="nextStep" class="btn-next">下一步</el-button>
          </div>
        </div>

        <!-- 第三步：AI能力评分 -->
        <div v-if="activeStep === 2" class="form-content">
          <div class="ability-form">
            <div class="ai-score-tip" style="text-align: center; margin-bottom: 20px; font-size: 16px; color: #6b7280;">
              <p>基于你的简历信息，AI已自动分析以下能力评分</p>
            </div>
            
            <el-table :data="abilityTableData" border size="large" class="ability-table" style="width: 100%;">
              <el-table-column prop="name" label="能力维度" width="180"></el-table-column>
              <el-table-column prop="score" label="AI评分" width="120">
                <template #default="scope">
                  <div class="score-value">{{ scope.row.score }}</div>
                </template>
              </el-table-column>
              <el-table-column prop="level" label="能力等级">
                <template #default="scope">
                  <el-tag 
                    :type="scope.row.score >= 80 ? 'success' : (scope.row.score >= 60 ? 'warning' : 'danger')"
                    size="large"
                  >
                    {{ scope.row.score >= 80 ? '优秀' : (scope.row.score >= 60 ? '良好' : '待提升') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="能力曲线" width="200">
                <template #default="scope">
                  <div class="score-bar">
                    <div class="bar-fill" :style="{ width: scope.row.score + '%' }"></div>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="form-actions">
            <el-button size="large" @click="prevStep" class="btn-prev">上一步</el-button>
            <el-button type="primary" size="large" @click="generateAbility" class="btn-next">生成能力画像</el-button>
          </div>
        </div>

        <!-- 第四步：能力画像（优化雷达图交互） -->
        <div v-if="activeStep === 3" class="form-content result-content">
          <!-- 头部标题 -->
          <div class="result-header">
            <h2 class="main-title">
              <i class="title-icon">🎯</i>
              个人能力画像报告
            </h2>
            <p class="subtitle">基于您的信息生成的专属职业能力分析</p>
          </div>
          
          <!-- 卡片容器 - 竖排排列 -->
          <div class="cards-container vertical-layout">
            <!-- 基础信息卡片 -->
            <div class="info-card animate-card">
              <div class="card-header">
                <div class="card-icon">👤</div>
                <h3 class="card-title">基础信息</h3>
              </div>
              <div class="card-body">
                <div class="info-grid">
                  <div class="info-pair">
                    <span class="info-label">用户名</span>
                    <span class="info-value">{{ basicForm.nickname || '未填写' }}</span>
                  </div>
                  <div class="info-pair">
                    <span class="info-label">姓名</span>
                    <span class="info-value">{{ basicForm.name || '未填写' }}</span>
                  </div>
                  <div class="info-pair">
                    <span class="info-label">性别</span>
                    <span class="info-value">{{ basicForm.gender || '未填写' }}</span>
                  </div>
                  <div class="info-pair">
                    <span class="info-label">学校</span>
                    <span class="info-value">{{ basicForm.school || '未填写' }}</span>
                  </div>
                  <div class="info-pair">
                    <span class="info-label">专业</span>
                    <span class="info-value">{{ basicForm.major || '未填写' }}</span>
                  </div>
                  <div class="info-pair">
                    <span class="info-label">年级</span>
                    <span class="info-value">{{ basicForm.grade || '未填写' }}</span>
                  </div>
                  <div class="info-pair">
                    <span class="info-label">学历</span>
                    <span class="info-value">{{ basicForm.education || '未填写' }}</span>
                  </div>
                  <div class="info-pair">
                    <span class="info-label">联系方式</span>
                    <span class="info-value">{{ basicForm.phone || '未填写' }}</span>
                  </div>
                  <div class="info-pair">
                    <span class="info-label">邮箱</span>
                    <span class="info-value">{{ basicForm.email || '未填写' }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 技能证书卡片 -->
            <div class="skills-card animate-card">
              <div class="card-header">
                <div class="card-icon">💡</div>
                <h3 class="card-title">技能与证书</h3>
              </div>
              <div class="card-body">
                <div class="skills-section">
                  <h4 class="section-subtitle">专业技能</h4>
                  <div class="tags-container skills-tags">
                    <el-tag 
                      v-for="skill in skillForm.skills" 
                      :key="skill" 
                      size="large" 
                      type="primary"
                      class="skill-tag"
                    >{{ skill }}</el-tag>
                    <el-tag 
                      v-if="skillForm.skills.length === 0" 
                      size="large" 
                      type="info"
                    >暂无技能信息</el-tag>
                  </div>
                </div>
                
                <div class="certificates-section">
                  <h4 class="section-subtitle">已获证书</h4>
                  <div class="tags-container cert-tags">
                    <el-tag 
                      v-for="cert in skillForm.certificates" 
                      :key="cert" 
                      size="large" 
                      type="success"
                      class="cert-tag"
                    >{{ cert }}</el-tag>
                    <el-tag 
                      v-if="skillForm.certificates.length === 0" 
                      size="large" 
                      type="info"
                    >暂无证书信息</el-tag>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 实习&项目经历卡片 -->
            <div class="experience-card animate-card">
              <div class="card-header">
                <div class="card-icon">📝</div>
                <h3 class="card-title">实习与项目经历</h3>
              </div>
              <div class="card-body">
                <div class="experience-section">
                  <h4 class="section-subtitle">实习经历</h4>
                  <div class="experience-content">
                    <p v-if="skillForm.internship" class="experience-text">{{ skillForm.internship }}</p>
                    <el-tag v-else size="large" type="info">暂无实习经历</el-tag>
                  </div>
                </div>
                
                <div class="experience-section">
                  <h4 class="section-subtitle">项目经历</h4>
                  <div class="experience-content">
                    <p v-if="skillForm.project" class="experience-text">{{ skillForm.project }}</p>
                    <el-tag v-else size="large" type="info">暂无项目经历</el-tag>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 能力评分卡片（优化雷达图交互） -->
            <div class="ability-card animate-card">
              <div class="card-header">
                <div class="card-icon">📊</div>
                <h3 class="card-title">综合能力评估</h3>
                <div class="score-summary">
                  <span class="score-label">综合能力评分</span>
                  <span class="score-value">{{ Math.round(abilityTableData.reduce((sum, item) => sum + item.score, 0) / abilityTableData.length) }}分</span>
                  <div class="stars">
                    <i v-for="i in 5" :key="i" :class="i <= Math.round((Math.round(abilityTableData.reduce((sum, item) => sum + item.score, 0) / abilityTableData.length)) / 20) ? 'el-icon-star-on' : 'el-icon-star-off'"></i>
                  </div>
                </div>
              </div>
              <div class="card-body">
                <!-- ECharts雷达图容器 -->
                <div ref="radarChartRef" class="radar-chart-container"></div>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="result-actions">
            <el-button type="primary" size="large" @click="saveAbility" class="btn-save">
              <i class="btn-icon">💾</i>
              保存画像并前往匹配
            </el-button>
            <el-button size="large" @click="resetForm" class="btn-reset">
              <i class="btn-icon">🔄</i>
              重新录入
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. 页脚 -->
    <footer class="footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 助力大学生精准规划职业方向
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'

// ========== 导航栏逻辑 ==========
const router = useRouter()
const route = useRoute()

const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)

// ECharts实例引用
const radarChartRef = ref(null)
let radarChart = null

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

// ========== 表单逻辑 ==========
const activeStep = ref(0)
const inputMode = ref('upload')
const uploadedResume = ref(null)
const tempSkill = ref('')
const tempCert = ref('')

const basicFormRef = ref(null)
const basicForm = reactive({
  nickname: localStorage.getItem('nickname') || '',
  name: '',
  gender: '保密',
  school: '',
  major: '',
  grade: '',
  education: '',
  phone: '',
  email: '',
  introduction: ''
})
const basicRules = {
  nickname: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  education: [{ required: true, message: '请选择学历', trigger: 'change' }],
  phone: [{ required: true, message: '请输入手机号码', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱地址', trigger: 'blur' }]
}

const skillFormRef = ref(null)
const skillForm = reactive({
  skills: [],
  certificates: [],
  internship: '',
  project: ''
})

const abilityForm = reactive({
  innovation: 80,
  learning: 85,
  pressure: 75,
  communication: 80,
  internship: 70
})

const abilityTableData = ref([
  { name: '创新能力', score: abilityForm.innovation, level: '' },
  { name: '学习能力', score: abilityForm.learning, level: '' },
  { name: '抗压能力', score: abilityForm.pressure, level: '' },
  { name: '沟通能力', score: abilityForm.communication, level: '' },
  { name: '实践能力', score: abilityForm.internship, level: '' }
])

// 初始化ECharts雷达图（优化交互效果）
const initRadarChart = () => {
  if (!radarChartRef.value) return
  
  // 销毁已有实例防止内存泄漏
  if (radarChart) {
    radarChart.dispose()
  }
  
  radarChart = echarts.init(radarChartRef.value)
  
  const radarData = abilityTableData.value.map(item => ({
    name: item.name,
    value: item.score
  }))
  
  // 获取能力等级文本
  const getLevelText = (score) => {
    if (score >= 80) return '优秀'
    if (score >= 60) return '良好'
    return '待提升'
  }
  
  // 获取能力等级描述
  const getLevelDesc = (name, score) => {
    const level = getLevelText(score)
    let desc = ''
    
    switch(name) {
      case '创新能力':
        desc = level === '优秀' ? '具备出色的创新思维和问题解决能力' : 
               level === '良好' ? '有一定的创新意识，能够提出改进建议' : 
               '需要加强创新思维训练，多参与创意项目'
        break
      case '学习能力':
        desc = level === '优秀' ? '学习能力极强，能快速掌握新知识技能' : 
               level === '良好' ? '学习能力良好，能掌握基础的专业知识' : 
               '学习效率有待提高，需要制定系统的学习计划'
        break
      case '抗压能力':
        desc = level === '优秀' ? '抗压能力出色，能应对高强度工作压力' : 
               level === '良好' ? '能承受一般工作压力，偶有情绪波动' : 
               '抗压能力较弱，需要加强心理调适能力'
        break
      case '沟通能力':
        desc = level === '优秀' ? '沟通表达能力优秀，善于团队协作' : 
               level === '良好' ? '沟通能力良好，能清晰表达自己的想法' : 
               '沟通技巧不足，需要多参与团队交流'
        break
      case '实践能力':
        desc = level === '优秀' ? '实践经验丰富，动手能力强' : 
               level === '良好' ? '有一定实践经验，能完成基础实操任务' : 
               '实践经验不足，需要多参与实习和项目'
        break
    }
    
    return desc
  }
  
  const option = {
    backgroundColor: 'transparent',
    // 优化提示框样式和内容
    tooltip: { 
      trigger: 'item',
      triggerOn: 'mousemove', // 鼠标移动时就触发
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133', fontSize: 14 },
      padding: 15,
      borderRadius: 8,
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      // 自定义提示框内容
      formatter: function(params) {
        const score = params.value
        const level = getLevelText(score)
        const desc = getLevelDesc(params.name, score)
        
        return `
          <div style="text-align: left;">
            <div style="font-weight: bold; color: #2563eb; font-size: 16px; margin-bottom: 8px;">
              ${params.name}
            </div>
            <div style="margin-bottom: 4px;">
              <span style="color: #666;">评分：</span>
              <span style="font-weight: bold; color: #333;">${score}分</span>
            </div>
            <div style="margin-bottom: 4px;">
              <span style="color: #666;">等级：</span>
              <span style="font-weight: bold; ${score >= 80 ? 'color: #22c55e;' : score >= 60 ? 'color: #faad14;' : 'color: #ff4d4f;'}">${level}</span>
            </div>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee; color: #666; font-size: 13px;">
              ${desc}
            </div>
          </div>
        `
      },
      // 提示框位置自适应
      position: function(point, params, dom, rect, size) {
        // 防止提示框超出可视区域
        const x = point[0] < size.viewSize[0] / 2 ? point[0] + 10 : point[0] - dom.offsetWidth - 10
        const y = point[1] < size.viewSize[1] / 2 ? point[1] + 10 : point[1] - dom.offsetHeight - 10
        return [x, y]
      }
    },
    radar: {
      indicator: radarData.map(item => ({ 
        name: item.name, 
        max: 100,
        // 指示器文本样式
        textStyle: {
          fontSize: 14,
          color: '#606266',
          fontWeight: 500
        }
      })),
      shape: 'circle',
      splitNumber: 5,
      radius: '80%',
      // 分割线样式
      splitLine: { 
        lineStyle: { 
          color: '#e4e7ed', 
          width: 1,
          type: 'dashed'
        } 
      },
      // 分割区域样式
      splitArea: { 
        areaStyle: { 
          color: ['#f8f9fa', '#ffffff'], 
          opacity: 0.8 
        } 
      },
      // 坐标轴样式
      axisLine: { 
        lineStyle: { 
          color: '#c0c4cc',
          width: 1
        } 
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: radarData.map(item => item.value),
        name: '能力评分',
        // 区域填充样式
        areaStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.4)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ]),
          opacity: 0.8 
        },
        // 线条样式
        lineStyle: { 
          color: '#409EFF', 
          width: 3,
          shadowColor: 'rgba(64, 158, 255, 0.3)',
          shadowBlur: 10,
          shadowOffsetY: 5
        },
        // 数据点样式
        itemStyle: { 
          color: '#409EFF', 
          borderWidth: 2, 
          borderColor: '#ffffff',
          shadowColor: 'rgba(64, 158, 255, 0.5)',
          shadowBlur: 5
        },
        symbol: 'circle',
        symbolSize: 10,
        // 数据点高亮样式
        emphasis: {
          itemStyle: {
            color: '#ffffff',
            borderColor: '#409EFF',
            borderWidth: 3,
            shadowBlur: 10
          },
          symbolSize: 14
        }
      }]
    }]
  }
  
  radarChart.setOption(option)
  
  // 添加鼠标交互事件
  radarChart.on('mouseover', function(params) {
    // 鼠标悬停时高亮对应的数据点
    radarChart.dispatchAction({
      type: 'highlight',
      seriesIndex: 0,
      dataIndex: 0,
      dataType: 'radar',
      dimensionIndex: params.dimensionIndex
    })
  })
  
  radarChart.on('mouseout', function() {
    // 鼠标离开时取消高亮
    radarChart.dispatchAction({
      type: 'downplay',
      seriesIndex: 0,
      dataIndex: 0
    })
  })
  
  // 监听窗口大小变化自适应
  const resizeHandler = () => {
    radarChart.resize()
  }
  window.addEventListener('resize', resizeHandler)
  
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
  })
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  else return (bytes / 1048576).toFixed(1) + ' MB'
}

const beforeResumeUpload = (file) => {
  const isAllowedType = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)
  const isAllowedSize = file.size <= 10 * 1024 * 1024
  if (!isAllowedType) {
    ElMessage.error('仅支持上传 PDF、Word 格式的简历文件！')
    return false
  }
  if (!isAllowedSize) {
    ElMessage.error('简历文件大小不能超过 10MB！')
    return false
  }
  return true
}

const handleResumeUploadSuccess = (response, file) => {
  uploadedResume.value = { name: file.name, size: file.size, url: response.url || '' }
  ElMessage.success('简历上传成功！')
}

const handleResumeUploadError = () => {
  ElMessage.error('简历上传失败，请重试！')
}

const removeResume = () => {
  uploadedResume.value = null
  ElMessage.info('已移除上传的简历文件')
}

const parseResume = () => {
  const loadingInstance = ElLoading.service({ lock: true, text: '正在解析简历信息...', background: 'rgba(0, 0, 0, 0.7)' })
  setTimeout(() => {
    skillForm.skills = ['Python', 'Java', 'SQL', '前端开发']
    skillForm.certificates = ['计算机二级', '英语六级', 'PMP认证']
    skillForm.internship = 'XX科技有限公司 - 后端开发实习生（2023.07-2023.09）：参与公司核心业务系统开发，负责接口设计和实现，使用Spring Boot框架完成接口开发，优化接口性能提升30%。'
    skillForm.project = '校园二手交易平台（2023.03-2023.06）：担任后端开发，使用Spring Boot + Vue3开发，实现用户认证、商品发布、交易管理等功能，项目上线后累计用户500+。'
    abilityForm.innovation = 85
    abilityForm.learning = 90
    abilityForm.pressure = 80
    abilityForm.communication = 88
    abilityForm.internship = 82
    updateAbilityTable()
    loadingInstance.close()
    ElMessage.success('简历解析成功，已自动填充信息并生成AI评分！')
    inputMode.value = 'manual'
  }, 2000)
}

const handleTagAdd = (list, value) => {
  if (value.trim() && !list.includes(value.trim())) {
    list.push(value.trim())
    if (list === skillForm.skills) tempSkill.value = ''
    else if (list === skillForm.certificates) tempCert.value = ''
  } else if (list.includes(value.trim())) {
    ElMessage.warning('该标签已存在')
  }
}

const handleTagClose = (list, index) => {
  list.splice(index, 1)
}

const nextStep = () => {
  if (activeStep.value === 0) {
    basicFormRef.value.validate((valid) => {
      if (valid) {
        // 同步用户名到localStorage，供个人中心读取
        localStorage.setItem('nickname', basicForm.nickname)
        activeStep.value++
      } else {
        ElMessage.warning('请完善基础信息')
      }
    })
  } else if (activeStep.value === 1) {
    activeStep.value++
    if (skillForm.skills.length > 0 || uploadedResume.value) {
      abilityForm.innovation = Math.floor(Math.random() * 20) + 70
      abilityForm.learning = Math.floor(Math.random() * 20) + 75
      abilityForm.pressure = Math.floor(Math.random() * 20) + 70
      abilityForm.communication = Math.floor(Math.random() * 20) + 75
      abilityForm.internship = Math.floor(Math.random() * 20) + 70
    }
    updateAbilityTable()
  }
}

const prevStep = () => {
  activeStep.value--
}

const updateAbilityTable = () => {
  abilityTableData.value = [
    { name: '创新能力', score: abilityForm.innovation },
    { name: '学习能力', score: abilityForm.learning },
    { name: '抗压能力', score: abilityForm.pressure },
    { name: '沟通能力', score: abilityForm.communication },
    { name: '实践能力', score: abilityForm.internship }
  ]
}

const generateAbility = () => {
  const loadingInstance = ElLoading.service({ lock: true, text: '正在生成你的能力画像...', background: 'rgba(0, 0, 0, 0.7)' })
  setTimeout(() => {
    updateAbilityTable()
    activeStep.value++
    // 生成能力画像后初始化雷达图（确保DOM已渲染）
    nextTick(() => {
      initRadarChart()
    })
    loadingInstance.close()
    ElMessage.success('能力画像生成成功！')
  }, 1500)
}

const saveAbility = () => {
  // 保存完整学生信息到localStorage
  const studentInfo = { 
    basic: { ...basicForm }, 
    skill: { ...skillForm }, 
    ability: { ...abilityForm }, 
    resumeMode: inputMode.value, 
    hasUploadedResume: !!uploadedResume.value 
  }
  const studentAbility = { 
    baseScore: 90, 
    skillScore: skillForm.skills.length >= 3 ? 85 : 70, 
    qualityScore: (abilityForm.communication + abilityForm.pressure) / 2, 
    potentialScore: (abilityForm.innovation + abilityForm.learning) / 2 
  }
  localStorage.setItem('studentInfo', JSON.stringify(studentInfo))
  localStorage.setItem('studentAbility', JSON.stringify(studentAbility))
  
  // 同步个人中心所需字段到localStorage
  localStorage.setItem('nickname', basicForm.nickname)
  localStorage.setItem('realName', basicForm.name)
  localStorage.setItem('gender', basicForm.gender)
  localStorage.setItem('school', basicForm.school)
  localStorage.setItem('major', basicForm.major)
  localStorage.setItem('grade', basicForm.grade)
  localStorage.setItem('phone', basicForm.phone)
  localStorage.setItem('email', basicForm.email)
  localStorage.setItem('introduction', basicForm.introduction)
  
  ElMessage.success('能力画像保存成功！')
  router.push('/match-result')
}

const resetForm = () => {
  activeStep.value = 0
  inputMode.value = 'upload'
  uploadedResume.value = null
  if (basicFormRef.value) basicFormRef.value.resetFields()
  skillForm.skills = []
  skillForm.certificates = []
  skillForm.internship = ''
  skillForm.project = ''
  abilityForm.innovation = 80
  abilityForm.learning = 85
  abilityForm.pressure = 75
  abilityForm.communication = 80
  abilityForm.internship = 70
  tempSkill.value = ''
  tempCert.value = ''
  updateAbilityTable()
  ElMessage.info('表单已重置为初始状态')
}

onMounted(() => {
  applyTheme()
  // 如果直接进入第四步，初始化雷达图
  if (activeStep.value === 3) {
    nextTick(() => {
      initRadarChart()
    })
  }
})

// 监听activeStep变化，第四步时自动初始化雷达图
watch(activeStep, (newStep) => {
  if (newStep === 3) {
    nextTick(() => {
      initRadarChart()
    })
  }
})

// 组件卸载时销毁ECharts实例
onUnmounted(() => {
  if (radarChart) {
    radarChart.dispose()
  }
})
</script>

<style scoped>
/* 全局容器 */
.student-ability-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf5 100%);
  margin: 0;
  padding: 60px 0 0 0;
}

/* 导航栏 */
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

/* 主体容器 */
.student-ability-container {
  padding: 30px 20px;
  min-height: calc(100vh - 60px);
  max-width: 1200px;
  margin: 0 auto;
}

/* 步骤指示器 */
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40px;
  gap: 8px;
}
.step-item { display: flex; flex-direction: column; align-items: center; position: relative; }
.step-number { width: 40px; height: 40px; border-radius: 50%; background: #e5e7eb; color: #6b7280; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-bottom: 8px; transition: all 0.3s ease; }
.step-text { font-size: 14px; color: #6b7280; transition: all 0.3s ease; }
.step-divider { width: 60px; height: 2px; background: #e5e7eb; transition: all 0.3s ease; }
.step-item.active .step-number { background: #2563eb; color: #fff; }
.step-item.active .step-text { color: #2563eb; font-weight: 500; }
.step-item.completed .step-number { background: #22c55e; color: #fff; }
.step-item.completed ~ .step-divider { background: #22c55e; }

/* 表单卡片：第四步保留白色背景 */
.form-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  padding: 40px;
  margin-bottom: 40px;
}
/* 第四步专属样式 - 保留白色背景，不取消卡片样式 */
.form-card.result-card {
  background: #fff;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  padding: 40px;
  border-radius: 16px;
}

/* 表单内容 */
.form-content { width: 100%; }
.info-form { max-width: 800px; margin: 0 auto; }
:deep(.info-form .el-form-item) { margin-bottom: 24px; }
:deep(.info-form .el-input), :deep(.info-form .el-select) { width: 100%; }

.input-mode-tabs { display: flex; border-bottom: 1px solid #e5e7eb; margin-bottom: 30px; }
.tab-item { padding: 12px 24px; font-size: 16px; font-weight: 500; color: #6b7280; cursor: pointer; border-bottom: 3px solid transparent; display: flex; align-items: center; gap: 8px; transition: all 0.3s ease; }
.tab-item.active { color: #2563eb; border-bottom-color: #2563eb; }
.tab-item:hover { color: #2563eb; }
.icon-upload, .icon-edit { font-size: 18px; }

.upload-mode { padding: 20px; text-align: center; }
:deep(.resume-uploader) { border: 2px dashed #d1d5db; border-radius: 12px; padding: 40px 20px; background: #f9fafb; transition: all 0.3s ease; }
:deep(.resume-uploader:hover) { border-color: #2563eb; background: #eff6ff; }
:deep(.resume-uploader .el-upload__text) { margin-top: 16px; }
:deep(.resume-uploader .el-upload__text h3) { font-size: 18px; color: #1f2937; margin: 0 0 8px 0; }
:deep(.resume-uploader .el-upload__text p) { font-size: 14px; color: #6b7280; margin: 0; }
:deep(.resume-uploader .el-upload__text em) { color: #2563eb; font-style: normal; font-weight: 500; }
.uploaded-file { margin-top: 20px; max-width: 600px; margin-left: auto; margin-right: auto; }
:deep(.uploaded-file .el-card) { border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.file-info { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #e5e7eb; }
.file-icon { font-size: 24px; margin-right: 12px; }
.file-details { flex: 1; text-align: left; }
.file-name { font-weight: 500; color: #1f2937; margin-bottom: 4px; }
.file-size { font-size: 12px; color: #6b7280; }

.manual-mode { max-width: 900px; margin: 0 auto; }
.skill-form { width: 100%; }
:deep(.skill-form .el-form-item) { margin-bottom: 24px; }
.tag-input-container { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 8px; padding: 8px; border: 1px solid #e5e7eb; border-radius: 8px; min-height: 80px; }
:deep(.tag-input-container .el-tag) { font-size: 14px; }

.ability-form { max-width: 800px; margin: 0 auto; }
.slider-item { margin-bottom: 24px; }
:deep(.slider-item .el-slider) { width: 100%; }

.form-actions { display: flex; justify-content: center; gap: 16px; margin-top: 30px; }
.resume-actions { margin-top: 40px; }
.btn-prev, .btn-next, .btn-save, .btn-reset { padding: 12px 32px; border-radius: 8px; font-size: 16px; font-weight: 500; }
.btn-next, .btn-save { background: #2563eb; border-color: #2563eb; }
.btn-next:hover, .btn-save:hover { background: #1d4ed8; border-color: #1d4ed8; }

/* ========== 优化后的第四步样式 ========== */
.result-content {
  padding: 20px 0;
}

/* 头部标题 */
.result-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(37, 99, 235, 0.1);
}

.main-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
  animation: pulse 2s infinite;
}

.subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 卡片容器 - 竖排排列 */
.cards-container.vertical-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 24px;
}

/* 通用卡片样式 */
.animate-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

.info-card { animation-delay: 0.1s; }
.skills-card { animation-delay: 0.2s; }
.experience-card { animation-delay: 0.25s; }
.ability-card { animation-delay: 0.3s; }

.animate-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  background: #fff;
  color: #333;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f0f0f0;
}

.card-icon {
  font-size: 24px;
  background: rgba(37, 99, 235, 0.1);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2563eb;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.score-summary {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-label {
  font-size: 14px;
  color: #6b7280;
}

.score-summary .score-value {
  font-size: 24px;
  font-weight: 700;
  color: #2563eb;
}

.stars {
  color: #ffc107;
  font-size: 16px;
}

.card-body {
  padding: 24px;
}

/* 基础信息卡片 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-pair {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.info-pair:hover {
  background: #eff6ff;
  transform: translateX(4px);
}

.info-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  color: #1f2937;
  font-weight: 600;
}

/* 技能证书卡片 */
.section-subtitle {
  font-size: 16px;
  color: #1f2937;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

:deep(.skill-tag) {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
  border: 1px solid #dbeafe;
  transition: all 0.2s ease;
}

:deep(.skill-tag:hover) {
  background: #2563eb;
  color: white;
  transform: scale(1.05);
}

:deep(.cert-tag) {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid #dcfce7;
  transition: all 0.2s ease;
}

:deep(.cert-tag:hover) {
  background: #22c55e;
  color: white;
  transform: scale(1.05);
}

/* 实习&项目经历卡片样式 */
.experience-section {
  margin-bottom: 24px;
}

.experience-section:last-child {
  margin-bottom: 0;
}

.experience-content {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  min-height: 80px;
  display: flex;
  align-items: center;
}

.experience-text {
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
  margin: 0;
  white-space: pre-line;
}

/* 能力评分卡片 */
.ability-card {
  width: 100%;
}

:deep(.ability-table) {
  --el-table-header-text-color: #1f2937;
  --el-table-row-hover-bg-color: #f9fafb;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 30px;
}

.ability-name {
  font-weight: 500;
  color: #1f2937;
}

.score-value {
  font-weight: 700;
  color: #2563eb;
  font-size: 18px;
}

:deep(.level-tag) {
  font-weight: 600;
}

.score-bar {
  width: 100%;
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
  border-radius: 6px;
  transition: width 1s ease;
  position: relative;
}

.score-tooltip {
  position: absolute;
  top: -25px;
  transform: translateX(-50%);
  background: #1f2937;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.score-bar:hover .score-tooltip {
  opacity: 1;
}

/* ECharts雷达图容器样式 */
.radar-chart-container {
  width: 100%;
  height: 400px;
  margin: 0 auto;
  /* 添加鼠标样式 */
  cursor: crosshair;
}

/* 操作按钮 */
.result-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.btn-save, .btn-reset {
  padding: 14px 40px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-icon {
  font-size: 18px;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.2);
}

.btn-reset:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(107, 114, 128, 0.2);
}

/* 页脚 */
.footer { background: #fff; padding: 30px 0; border-top: 1px solid #f0f0f0; text-align: center; color: #666; font-size: 14px; margin-top: 40px; }
.footer-wrap { width: 1200px; margin: 0 auto; }

/* 动画效果 */
@keyframes fadeIn { 
  from { opacity: 0; transform: translateY(10px); } 
  to { opacity: 1; transform: translateY(0); } 
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* 响应式 */
@media (max-width: 1200px) {
  .nav-wrap, .student-ability-container, .footer-wrap { width: 95%; padding: 0 20px; }
  .form-card { padding: 30px 20px; }
  .form-card.result-card { padding: 30px 20px; }
  .step-indicator { flex-wrap: wrap; }
  .cards-container.vertical-layout { gap: 20px; }
}

@media (max-width: 768px) {
  .nav-menu { display: none; }
  .step-item { margin-bottom: 10px; }
  .step-divider { display: none; }
  .form-actions { flex-direction: column; }
  .result-actions { flex-direction: column; }
  .info-grid { grid-template-columns: 1fr; }
  .radar-chart-container { height: 300px; }
  .main-title { font-size: 24px; }
}
</style>
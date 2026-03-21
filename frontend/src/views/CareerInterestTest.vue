<template>
  <div class="career-test">
    <!-- 替换为统一的顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item" @click="$router.push('/student-ability')">岗位画像</li>
            <!-- 添加 active 类使职业规划导航项变蓝并有下划线 -->
            <li class="menu-item active" @click="$router.push('/career-planning-intro')">职业规划</li>
            <li class="menu-item" @click="$router.push('/resource-library')">资源库</li>
            <li class="menu-item" @click="$router.push('/about-us')">关于我们</li>
            <li class="menu-item dropdown">
              核心功能 ▼
              <ul class="dropdown-menu">
                <li class="dropdown-item active" @click="goToFeature('测评')">
                  <span class="color-dot red"></span> 职业测评
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

    <!-- 页面副标题区域（保留原有功能按钮） -->
    <div class="test-subheader">
      <div class="subheader-wrap">
        <div class="page-title">
          <span class="title-icon">🧭</span>
          <h1>职业测评</h1>
        </div>
        <div class="page-nav">
          <!-- 删除了返回首页按钮 -->
          <button 
            class="report-btn" 
            @click="showReportModal = true" 
            v-if="testCompleted"
          >
            📄 查看测评报告
          </button>
        </div>
      </div>
    </div>

    <!-- 2. 测评介绍（未开始答题时显示） -->
    <section class="test-intro" v-if="!testStarted && !testCompleted">
      <div class="intro-wrap">
        <div class="intro-card">
          <div class="intro-header">
            <h2>职业测评</h2>
            <p class="intro-subtitle">了解你的职业倾向，找到适合的职业方向</p>
          </div>
          <div class="intro-content">
            <div class="theory-desc">
              <h3>职业测评理论</h3>
              <p>
                职业测评综合多种心理学理论，从多个维度评估你的职业倾向、能力特点和人格特质，
                帮助人们找到与自身特质相匹配的职业方向。
              </p>
            </div>
            
            <div class="type-cards">
              <div class="type-card" v-for="type in interestTypes" :key="type.code">
                <div class="type-icon">{{ type.icon }}</div>
                <div class="type-info">
                  <h4>{{ type.name }}({{ type.code }})</h4>
                  <p>{{ type.desc }}</p>
                </div>
              </div>
            </div>
            
            <div class="test-rules">
              <h3>测评规则</h3>
              <ul>
                <li>本测评共60道题目，预计耗时10-15分钟</li>
                <li>请根据自身实际情况选择符合程度，无需过度思考</li>
                <li>答案无对错之分，仅反映你的职业倾向</li>
                <li>完成后可查看详细的测评报告和职业推荐</li>
              </ul>
            </div>
          </div>
          
          <div class="intro-footer">
            <button class="start-btn" @click="startTest">开始测评</button>
            <p class="tips">测评结果仅用于个人职业规划参考，我们将严格保护你的隐私</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 3. 答题界面（答题中显示） -->
    <section class="test-questions" v-if="testStarted && !testCompleted">
      <div class="questions-wrap">
        <!-- 答题进度 -->
        <div class="progress-bar">
          <div class="progress-info">
            <span>答题进度：{{ currentQuestionIndex + 1 }}/{{ testQuestions.length }}</span>
            <span>剩余时间：{{ remainingTime }}秒</span>
          </div>
          <div class="progress-container">
            <div 
              class="progress-fill" 
              :style="{ width: (currentQuestionIndex + 1) / testQuestions.length * 100 + '%' }"
            ></div>
          </div>
        </div>

        <!-- 题目区域 -->
        <div class="question-card">
          <div class="question-header">
            <h3>第 {{ currentQuestionIndex + 1 }} 题</h3>
          </div>
          <div class="question-content">
            <p class="question-text">{{ currentQuestion.content }}</p>
            <div class="options-list">
              <label 
                class="option-item" 
                v-for="(option, idx) in options" 
                :key="idx"
              >
                <input 
                  type="radio" 
                  name="answer" 
                  :value="idx + 1" 
                  v-model="currentAnswer"
                  @change="selectAnswerAndNext(idx + 1)"
                >
                <span class="option-text">{{ option.label }} - {{ option.desc }}</span>
              </label>
            </div>
          </div>
          <div class="question-footer">
            <button 
              class="prev-btn" 
              @click="prevQuestion" 
              :disabled="currentQuestionIndex === 0"
            >
              上一题
            </button>
            <button 
              class="next-btn" 
              @click="nextQuestion"
              :disabled="currentAnswer === 0"
            >
              {{ currentQuestionIndex === testQuestions.length - 1 ? '完成测评' : '下一题' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. 测评结果（完成答题后显示） -->
    <section class="test-result" v-if="testCompleted">
      <div class="result-wrap">
        <div class="result-header">
          <h2>你的职业测评结果</h2>
          <p class="result-subtitle">基于你的答题情况，生成专属职业分析</p>
        </div>

        <!-- 结果雷达图 -->
        <div class="result-chart">
          <h3>职业维度得分</h3>
          <div class="chart-container">
            <!-- 修复后的雷达图 -->
            <div class="radar-chart">
              <div class="radar-grid"></div>
              <div class="radar-axis" v-for="(axis, idx) in radarAxes" :key="idx" :style="getRadarAxisStyle(idx)">
                <div class="axis-label">{{ axis.label }}</div>
                <div class="axis-line"></div>
                <div 
                  class="axis-point" 
                  :style="{ 
                    bottom: `${axis.score}%`,
                    transform: 'translateX(-50%)'
                  }"
                ></div>
              </div>
              <!-- 得分区域填充 -->
              <div class="radar-fill" :style="getRadarFillStyle()"></div>
            </div>
          </div>
        </div>

        <!-- 核心结果 -->
        <div class="core-result">
          <div class="core-card">
            <div class="core-icon">{{ topType.icon }}</div>
            <div class="core-content">
              <h3>你的主导职业类型：{{ topType.name }}</h3>
              <p class="core-desc">{{ topType.detailDesc }}</p>
              <div class="core-tips">
                <h4>适合你的职业方向：</h4>
                <div class="career-tags">
                  <span class="career-tag" v-for="career in topType.careers" :key="career">{{ career }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 详细分析 -->
        <div class="detail-analysis">
          <h3>各维度详细分析</h3>
          <div class="analysis-cards">
            <div 
              class="analysis-card" 
              v-for="type in interestTypes" 
              :key="type.code"
              :class="{ top: type.code === topType.code }"
            >
              <div class="analysis-header">
                <span class="type-icon">{{ type.icon }}</span>
                <h4>{{ type.name }}({{ type.code }})</h4>
                <span class="score-tag">{{ scores[type.code] }}分</span>
              </div>
              <div class="analysis-content">
                <p>{{ type.analysis }}</p>
                <div class="career-recommend" v-if="type.careers.length > 0">
                  <p class="recommend-title">推荐职业：</p>
                  <div class="recommend-list">
                    <span v-for="career in type.careers.slice(0, 5)" :key="career">{{ career }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="result-actions">
          <button class="restart-btn" @click="restartTest">重新测评</button>
          <button class="export-btn" @click="exportReport">导出测评报告</button>
          <button class="share-btn" @click="shareResult">分享测评结果</button>
          <!-- 修改：人岗匹配按钮 -->
          <button class="career-plan-btn" @click="goToMatchResult">
            📋 进行人岗匹配分析
          </button>
        </div>
      </div>
    </section>

    <!-- 测评报告弹窗 -->
    <div class="report-modal" v-if="showReportModal">
      <div class="modal-mask" @click="showReportModal = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>职业测评报告</h3>
          <button class="close-btn" @click="showReportModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="report-header">
            <p class="report-date">测评时间：{{ testResultDate }}</p>
            <h2>职业测评报告</h2>
          </div>
          
          <div class="report-section">
            <h3>一、测评结果总览</h3>
            <p>你的主导职业类型：<strong>{{ topType.name }}({{ topType.code }})</strong></p>
            <p>各维度得分：</p>
            <div class="score-table">
              <div class="table-row header">
                <div class="table-cell">类型</div>
                <div class="table-cell">代码</div>
                <div class="table-cell">得分</div>
                <div class="table-cell">等级</div>
              </div>
              <div class="table-row" v-for="type in interestTypes" :key="type.code">
                <div class="table-cell">{{ type.name }}</div>
                <div class="table-cell">{{ type.code }}</div>
                <div class="table-cell">{{ scores[type.code] }}</div>
                <div class="table-cell">{{ getScoreLevel(scores[type.code]) }}</div>
              </div>
            </div>
          </div>
          
          <div class="report-section">
            <h3>二、主导类型分析</h3>
            <p>{{ topType.detailDesc }}</p>
            <p>核心优势：{{ topType.advantages }}</p>
            <p>发展建议：{{ topType.suggestions }}</p>
          </div>
          
          <div class="report-section">
            <h3>三、职业推荐</h3>
            <div class="career-group">
              <h4>高度匹配职业：</h4>
              <div class="career-list">
                <span v-for="career in topType.careers.slice(0, 8)" :key="career">{{ career }}</span>
              </div>
            </div>
            <div class="career-group">
              <h4>较匹配职业：</h4>
              <div class="career-list">
                <span v-for="(type, idx) in interestTypes.filter(t => t.code !== topType.code).slice(0, 2)" :key="idx">
                  {{ type.name }}：{{ type.careers.slice(0, 3).join('、') }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="report-section">
            <h3>四、发展建议</h3>
            <ul class="suggestion-list">
              <li>根据职业倾向选择专业课程和实践活动</li>
              <li>多了解目标职业的发展前景和能力要求</li>
              <li>参加相关的实习和社会实践，积累经验</li>
              <li>持续提升自身能力，匹配目标职业要求</li>
              <li>定期重新测评，跟踪职业倾向变化</li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button class="print-btn" @click="printReport">打印报告</button>
          <button class="download-btn" @click="downloadReport">下载PDF</button>
          <button class="close-btn" @click="showReportModal = false">关闭</button>
        </div>
      </div>
    </div>

    <!-- 5. 页脚 -->
    <footer class="page-footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 职业测评基于多维度职业理论开发
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// ========== 导航栏相关逻辑 ==========
// 登录状态
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
  ElMessage.success('退出登录成功')
}

// 主题切换
const darkMode = ref(localStorage.getItem('darkMode') === 'true')
function applyTheme() {
  if (darkMode.value) {
    document.body.classList.add('dark')
  } else {
    document.body.classList.remove('dark')
  }
}

function toggleTheme() {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  applyTheme()
  ElMessage.success(`已切换为${darkMode.value ? '暗黑' : '明亮'}模式`)
}

// 核心功能跳转
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

// 搜索功能
const handleSearch = () => {
  const searchInput = document.querySelector('.nav-search-input')
  const keyword = searchInput.value.trim()
  if (keyword) {
    router.push(`/search?keyword=${encodeURIComponent(keyword)}`)
    searchInput.value = ''
    ElMessage.success(`正在搜索：${keyword}`)
  } else {
    ElMessage.warning('请输入搜索关键词')
  }
}

// ========== 测评相关逻辑 ==========
// 暂存相关常量
const DRAFT_STORAGE_KEY = 'careerInterestTestDraft'
const RESULT_STORAGE_KEY = 'careerInterestTestResult'

// 基础状态
const testStarted = ref(false)       // 是否开始测评
const testCompleted = ref(false)     // 是否完成测评
const currentQuestionIndex = ref(0)  // 当前题目索引
const currentAnswer = ref(0)         // 当前题答案
const answers = ref({})              // 所有答案存储
const showReportModal = ref(false)   // 是否显示报告弹窗
const testResultDate = ref('')       // 测评完成时间

// 计时相关
const totalTime = 900 // 总答题时间（秒）- 15分钟
const remainingTime = ref(totalTime)
let timer = null

// 职业类型定义
const interestTypes = ref([
  {
    code: 'R',
    name: '现实型',
    icon: '🛠️',
    desc: '偏好与物体打交道，喜欢具体的、实际操作性的工作',
    detailDesc: '你属于现实型人格，偏好与物体打交道，喜欢具体的、实际操作性的工作。你动手能力强，做事踏实，喜欢使用工具和机械，偏好具体任务，不善言辞，做事保守，较为谦虚。喜欢独立做事，注重实际效果。',
    analysis: '你的现实型维度得分较高，说明你具备较强的动手能力和实操能力，喜欢具体、明确的任务，不喜欢抽象的理论思考。你适合从事需要实际操作的职业，能够在具体的工作中找到成就感。',
    careers: ['机械维修师', '电工', '土木工程师', '建筑工人', '厨师', '司机', '消防员', '园艺师', '飞行员', '机械设计师'],
    advantages: '动手能力强、务实、细心、有耐心、执行力强',
    suggestions: '可以重点关注工程技术、手工操作、技术维修等领域的职业发展，注重专业技能的提升和实践经验的积累。'
  },
  {
    code: 'I',
    name: '研究型',
    icon: '🔬',
    desc: '喜欢智力活动和抽象推理，乐于探索和解决复杂问题',
    detailDesc: '你属于研究型人格，喜欢智力活动和抽象推理，乐于探索和解决复杂问题。你好奇心强，追求知识，喜欢独立思考和研究，逻辑思维能力强，做事严谨，注重分析和推理。不喜欢繁琐的行政事务和重复性工作。',
    analysis: '你的研究型维度得分较高，说明你具备较强的逻辑思维和分析能力，喜欢探索未知领域，善于发现问题和解决问题。你适合从事需要深度思考和研究的职业，能够在学术研究和技术研发中找到价值。',
    careers: ['科研人员', '数据分析师', '软件工程师', '医生', '大学教师', '心理学家', '化学家', '生物学家', '数学家', '统计学家'],
    advantages: '逻辑思维强、好奇心重、善于分析、学习能力强、追求真理',
    suggestions: '适合从事科研、数据分析、学术研究、技术研发等领域的工作，建议继续深造提升专业水平，保持对新知识的探索精神。'
  },
  {
    code: 'A',
    name: '艺术型',
    icon: '🎨',
    desc: '喜欢创造性的表达，追求美感和独特性，富有想象力',
    detailDesc: '你属于艺术型人格，喜欢创造性的表达，追求美感和独特性，富有想象力。你情感丰富，直觉敏锐，喜欢通过各种艺术形式表达自己，不拘小节，喜欢自由的工作环境，不喜欢受规则束缚。',
    analysis: '你的艺术型维度得分较高，说明你具备较强的创造力和想象力，对美有独特的追求，善于用艺术的方式表达自己。你适合从事需要创意和表达的职业，能够在艺术创作和审美设计中实现自我价值。',
    careers: ['设计师', '摄影师', '音乐家', '作家', '画家', '演员', '导演', '广告创意', '时尚编辑', '室内设计师'],
    advantages: '创造力强、想象力丰富、审美能力高、情感细腻、表达能力强',
    suggestions: '适合从事设计、艺术创作、文化创意等领域的工作，保持创作热情，不断提升审美水平和创意能力。'
  },
  {
    code: 'S',
    name: '社会型',
    icon: '🤝',
    desc: '喜欢与人交往，乐于助人，关心社会问题，渴望发挥社会作用',
    detailDesc: '你属于社会型人格，喜欢与人交往，乐于助人，关心社会问题，渴望发挥社会作用。你善于沟通，有同理心，喜欢帮助他人解决问题，乐于从事教育、咨询、公益等工作，具有较强的社会责任感。',
    analysis: '你的社会型维度得分较高，说明你具备良好的沟通能力和人际交往能力，乐于助人，有较强的同理心和社会责任感。你适合从事与人打交道的职业，能够在帮助他人和服务社会中获得满足感。',
    careers: ['教师', '心理咨询师', '社会工作者', '医生', '护士', '人力资源专员', '培训师', '公益志愿者', '客服主管', '职业规划师'],
    advantages: '沟通能力强、有同理心、乐于助人、有耐心、善于倾听',
    suggestions: '适合从事教育、医疗、咨询、公益、人力资源等领域的工作，注重沟通技巧和服务意识的提升。'
  },
  {
    code: 'E',
    name: '企业型',
    icon: '💼',
    desc: '喜欢影响、说服和领导他人，追求成功和成就感',
    detailDesc: '你属于企业型人格，喜欢影响、说服和领导他人，追求成功和成就感。你自信果断，有领导才能，喜欢竞争和挑战，目标明确，注重效率和结果，乐于从事管理和销售类工作。',
    analysis: '你的企业型维度得分较高，说明你具备较强的领导能力和决策能力，有进取心，喜欢挑战和竞争，追求成功和成就感。你适合从事管理、销售、创业等职业，能够在带领团队和实现目标中体现价值。',
    careers: ['企业家', '销售经理', '市场营销总监', '人力资源总监', '项目经理', '律师', '公关经理', '行政主管', '投资顾问', '职业经理人'],
    advantages: '领导力强、决策果断、目标导向、沟通能力强、抗压能力强',
    suggestions: '适合从事管理、销售、创业、商务等领域的工作，注重领导力和商业思维的培养，积累管理经验。'
  },
  {
    code: 'C',
    name: '常规型',
    icon: '📋',
    desc: '喜欢有规则的、有序的工作，注重细节和准确性',
    detailDesc: '你属于常规型人格，喜欢有规则的、有序的工作，注重细节和准确性。你做事认真细致，有责任心，喜欢按部就班地完成任务，善于处理数据和文书工作，注重秩序和规范。',
    analysis: '你的常规型维度得分较高，说明你具备较强的细心和耐心，做事认真负责，注重规则和秩序，善于处理细节性的工作。你适合从事需要细心和规范的职业，能够在有序的工作环境中发挥优势。',
    careers: ['会计', '出纳', '行政文员', '档案管理员', '图书管理员', '数据录入员', '银行柜员', '秘书', '统计员', '审计员'],
    advantages: '细心认真、有耐心、责任心强、遵守规则、执行力强',
    suggestions: '适合从事财务、行政、档案管理、数据处理等领域的工作，注重专业技能和细致程度的提升。'
  }
])

// 答题选项
const options = ref([
  { label: '非常不符合', desc: '完全不符合我的情况', score: 1 },
  { label: '不太符合', desc: '不太符合我的情况', score: 2 },
  { label: '一般', desc: '不确定是否符合', score: 3 },
  { label: '比较符合', desc: '比较符合我的情况', score: 4 },
  { label: '非常符合', desc: '完全符合我的情况', score: 5 }
])

// 测评题目（60道职业测试题）
const testQuestions = ref([
  // 现实型(R)题目
  { content: '我喜欢动手制作东西，比如模型、家具等', type: 'R' },
  { content: '我喜欢修理家电、电脑等设备', type: 'R' },
  { content: '我喜欢户外活动，比如登山、露营', type: 'R' },
  { content: '我喜欢使用工具进行手工制作', type: 'R' },
  { content: '我喜欢从事具体的、操作性强的工作', type: 'R' },
  { content: '我不喜欢整天坐在办公室里', type: 'R' },
  { content: '我喜欢学习机械原理和操作', type: 'R' },
  { content: '我喜欢从事建筑、维修类工作', type: 'R' },
  { content: '我喜欢亲自动手解决问题', type: 'R' },
  { content: '我喜欢从事农业、林业相关工作', type: 'R' },
  
  // 研究型(I)题目
  { content: '我喜欢研究和分析复杂的问题', type: 'I' },
  { content: '我喜欢阅读科学技术类书籍', type: 'I' },
  { content: '我喜欢做实验和数据分析', type: 'I' },
  { content: '我喜欢探索未知的领域和知识', type: 'I' },
  { content: '我喜欢独立思考和研究问题', type: 'I' },
  { content: '我对数学、物理等学科感兴趣', type: 'I' },
  { content: '我喜欢通过逻辑推理解决问题', type: 'I' },
  { content: '我喜欢了解事物的原理和规律', type: 'I' },
  { content: '我喜欢从事需要深度思考的工作', type: 'I' },
  { content: '我对新技术、新理论充满好奇', type: 'I' },
  
  // 艺术型(A)题目
  { content: '我喜欢绘画、书法、摄影等艺术创作', type: 'A' },
  { content: '我喜欢欣赏音乐、戏剧、电影等艺术形式', type: 'A' },
  { content: '我喜欢用创意的方式表达自己的想法', type: 'A' },
  { content: '我对时尚、美学有自己的见解', type: 'A' },
  { content: '我喜欢写作、写诗或创作故事', type: 'A' },
  { content: '我喜欢设计和装饰环境', type: 'A' },
  { content: '我喜欢参加文艺活动和展览', type: 'A' },
  { content: '我喜欢用非传统的方式解决问题', type: 'A' },
  { content: '我对色彩、造型有敏锐的感知', type: 'A' },
  { content: '我喜欢自由、无拘束的创作环境', type: 'A' },
  
  // 社会型(S)题目
  { content: '我喜欢帮助他人解决问题和困难', type: 'S' },
  { content: '我喜欢与人交流和沟通', type: 'S' },
  { content: '我喜欢从事教育、培训类工作', type: 'S' },
  { content: '我关心社会问题和公益事业', type: 'S' },
  { content: '我喜欢倾听他人的烦恼并给予建议', type: 'S' },
  { content: '我喜欢组织和参与社交活动', type: 'S' },
  { content: '我有较强的同理心和包容心', type: 'S' },
  { content: '我喜欢从事医疗、护理类工作', type: 'S' },
  { content: '我乐于分享自己的知识和经验', type: 'S' },
  { content: '我喜欢从事心理咨询、辅导类工作', type: 'S' },
  
  // 企业型(E)题目
  { content: '我喜欢领导和管理团队完成目标', type: 'E' },
  { content: '我喜欢销售和谈判工作', type: 'E' },
  { content: '我有较强的说服力和影响力', type: 'E' },
  { content: '我喜欢挑战和竞争，追求成功', type: 'E' },
  { content: '我有创业的想法和意愿', type: 'E' },
  { content: '我喜欢制定计划和策略', type: 'E' },
  { content: '我善于发现商业机会', type: 'E' },
  { content: '我喜欢在公众场合发言和演讲', type: 'E' },
  { content: '我有较强的决策能力和判断力', type: 'E' },
  { content: '我追求成就感和社会地位', type: 'E' },
  
  // 常规型(C)题目
  { content: '我喜欢有条理、有规则的工作环境', type: 'C' },
  { content: '我做事认真细致，注重细节', type: 'C' },
  { content: '我喜欢处理数据、文件和报表', type: 'C' },
  { content: '我擅长按部就班地完成任务', type: 'C' },
  { content: '我喜欢从事财务、会计类工作', type: 'C' },
  { content: '我有较强的责任心和耐心', type: 'C' },
  { content: '我喜欢整理和归档各类资料', type: 'C' },
  { content: '我遵守规章制度，不喜欢冒险', type: 'C' },
  { content: '我擅长文字录入和数据处理', type: 'C' },
  { content: '我喜欢从事行政、文秘类工作', type: 'C' }
])

// 当前题目
const currentQuestion = computed(() => {
  return testQuestions.value[currentQuestionIndex.value] || {}
})

// 计算各类型得分
const scores = computed(() => {
  const initialScores = { R: 0, I: 0, A: 0, S: 0, E: 0, C: 0 }
  
  // 遍历所有答案计算得分
  Object.entries(answers.value).forEach(([qIdx, answerScore]) => {
    const question = testQuestions.value[parseInt(qIdx)]
    if (question && answerScore) {
      initialScores[question.type] += answerScore
    }
  })
  
  // 归一化得分（0-100）
  const maxPossible = 50 // 每个类型10题，每题最高5分
  Object.keys(initialScores).forEach(type => {
    initialScores[type] = Math.round((initialScores[type] / maxPossible) * 100)
  })
  
  return initialScores
})

// 主导类型
const topType = computed(() => {
  // 找到得分最高的类型
  let maxScore = 0
  let topCode = 'R'
  
  Object.entries(scores.value).forEach(([code, score]) => {
    if (score > maxScore) {
      maxScore = score
      topCode = code
    }
  })
  
  return interestTypes.value.find(type => type.code === topCode) || interestTypes.value[0]
})

// 雷达图轴数据
const radarAxes = computed(() => {
  return [
    { label: '现实型(R)', score: scores.value.R },
    { label: '研究型(I)', score: scores.value.I },
    { label: '艺术型(A)', score: scores.value.A },
    { label: '社会型(S)', score: scores.value.S },
    { label: '企业型(E)', score: scores.value.E },
    { label: '常规型(C)', score: scores.value.C }
  ]
})

// 加载暂存的测试数据
const loadTestDraft = () => {
  const draft = localStorage.getItem(DRAFT_STORAGE_KEY)
  if (draft) {
    try {
      const draftData = JSON.parse(draft)
      currentQuestionIndex.value = draftData.currentIndex || 0
      answers.value = draftData.answers || {}
      currentAnswer.value = draftData.currentAnswer || 0
      testStarted.value = draftData.testStarted || false
      testCompleted.value = draftData.testCompleted || false
      
      // 如果有已完成的结果，直接加载
      if (testCompleted.value) {
        const result = localStorage.getItem(RESULT_STORAGE_KEY)
        if (result) {
          const resultData = JSON.parse(result)
          testResultDate.value = resultData.testResultDate || ''
        }
      }
      
      ElMessage.info('检测到上次未完成的测评，已为你恢复答题进度')
    } catch (e) {
      console.error('加载测评暂存数据失败:', e)
    }
  }
}

// 保存测试暂存数据
const saveTestDraft = () => {
  const draftData = {
    currentIndex: currentQuestionIndex.value,
    answers: answers.value,
    currentAnswer: currentAnswer.value,
    testStarted: testStarted.value,
    testCompleted: testCompleted.value
  }
  localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draftData))
}

// 保存测试最终结果
const saveTestResult = () => {
  const resultData = {
    scores: scores.value,
    topType: topType.value,
    testResultDate: testResultDate.value,
    answers: answers.value
  }
  localStorage.setItem(RESULT_STORAGE_KEY, JSON.stringify(resultData))
  
  // 保存到职业规划需要的key中
  const careerTestAnalysis = {
    interestType: topType.value.name,
    coreValues: ['薪资待遇', '成长空间', '职业匹配'],
    recommendJob: topType.value.careers[0],
    abilityLevel: getScoreLevel(scores.value[topType.value.code]),
    abilityScores: scores.value,
    abilityScoresDetail: radarAxes.value
  }
  
  localStorage.setItem('careerTestAnalysis', JSON.stringify(careerTestAnalysis))
  localStorage.setItem('targetJob', topType.value.careers[0])
}

// 开始测评
const startTest = () => {
  testStarted.value = true
  currentQuestionIndex.value = 0
  currentAnswer.value = 0
  answers.value = {}
  
  // 保存暂存
  saveTestDraft()
  
  // 启动计时器
  startTimer()
}

// 启动计时器
const startTimer = () => {
  remainingTime.value = totalTime
  
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    remainingTime.value -= 1
    
    // 时间到自动提交
    if (remainingTime.value <= 0) {
      completeTest()
    }
  }, 1000)
}

// 选择答案并自动跳转到下一题
const selectAnswerAndNext = (score) => {
  // 保存当前答案
  answers.value[currentQuestionIndex.value] = score
  currentAnswer.value = score
  
  // 保存暂存
  saveTestDraft()
  
  // 延迟一小段时间再跳转，让用户看到选择的效果
  setTimeout(() => {
    // 判断是否是最后一题
    if (currentQuestionIndex.value < testQuestions.value.length - 1) {
      currentQuestionIndex.value += 1
      currentAnswer.value = answers.value[currentQuestionIndex.value] || 0
      saveTestDraft()
    } else {
      completeTest()
    }
  }, 300)
}

// 上一题
const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value -= 1
    currentAnswer.value = answers.value[currentQuestionIndex.value] || 0
    // 保存暂存
    saveTestDraft()
  }
}

// 下一题/完成测评
const nextQuestion = () => {
  // 保存当前答案
  if (currentAnswer.value > 0) {
    answers.value[currentQuestionIndex.value] = currentAnswer.value
  }
  
  // 判断是否是最后一题
  if (currentQuestionIndex.value < testQuestions.value.length - 1) {
    currentQuestionIndex.value += 1
    currentAnswer.value = answers.value[currentQuestionIndex.value] || 0
    // 保存暂存
    saveTestDraft()
  } else {
    completeTest()
  }
}

// 完成测评
const completeTest = () => {
  // 停止计时器
  if (timer) clearInterval(timer)
  
  testCompleted.value = true
  testStarted.value = false
  
  // 记录完成时间
  const now = new Date()
  testResultDate.value = `${now.getFullYear()}-${(now.getMonth()+1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  // 计算最终得分（补全未答题，默认3分）
  testQuestions.value.forEach((_, idx) => {
    if (!answers.value[idx]) {
      answers.value[idx] = 3
    }
  })
  
  // 保存结果和暂存
  saveTestDraft()
  saveTestResult()
  
  ElMessage.success('测评完成！已为你保存测评结果')
}

// 重新测评
const restartTest = () => {
  testCompleted.value = false
  testStarted.value = false
  currentQuestionIndex.value = 0
  currentAnswer.value = 0
  answers.value = {}
  showReportModal.value = false
  
  // 清空暂存
  localStorage.removeItem(DRAFT_STORAGE_KEY)
  
  ElMessage.info('已重置测评，可重新开始答题')
}

// 导出测评报告
const exportReport = () => {
  showReportModal.value = true
}

// 分享测评结果
const shareResult = () => {
  const shareText = `我的职业测评结果：${topType.value.name}(${topType.value.code})，适合的职业方向：${topType.value.careers.slice(0, 3).join('、')}`
  try {
    navigator.clipboard.writeText(shareText)
    ElMessage.success('测评结果已复制到剪贴板，可分享给好友！')
  } catch (e) {
    alert(shareText + '\n\n复制失败，请手动复制')
  }
}

// 修改：跳转到人岗匹配分析页面
const goToMatchResult = () => {
  // 确保结果已保存
  saveTestResult()
  
  ElMessage.success('正在为你进行人岗匹配分析...')
  router.push('/jobmatch-analysis') // 跳转到MatchResult.vue页面
}

// 打印报告
const printReport = () => {
  window.print()
}

// 下载PDF报告
const downloadReport = () => {
  ElMessage.success('测评报告PDF已开始下载！')
  // 实际项目中可集成jsPDF等库实现真实下载
}

// 获取雷达图轴样式
const getRadarAxisStyle = (index) => {
  const angle = (index * 60) - 30 // 修正角度计算
  return {
    transform: `rotate(${angle}deg)`,
    transformOrigin: 'bottom center'
  }
}

// 获取雷达图填充样式
const getRadarFillStyle = () => {
  // 生成多边形路径
  const points = radarAxes.value.map((axis, idx) => {
    const angle = ((idx * 60) - 30) * Math.PI / 180
    const radius = axis.score // 直接使用百分比
    const x = 50 + (radius / 2) * Math.cos(angle)
    const y = 50 + (radius / 2) * Math.sin(angle)
    return `${x}% ${y}%`
  })
  
  return {
    clipPath: `polygon(${points.join(', ')})`
  }
}

// 获取得分等级
const getScoreLevel = (score) => {
  if (score >= 80) return '极高'
  if (score >= 60) return '较高'
  if (score >= 40) return '中等'
  if (score >= 20) return '较低'
  return '极低'
}

// 页面加载时加载暂存和应用主题
onMounted(() => {
  loadTestDraft()
  applyTheme()
})

// 组件卸载时保存暂存并清除计时器
onUnmounted(() => {
  saveTestDraft()
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
/* 全局容器 */
.career-test {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f8f9fa;
  margin: 0;
  padding: 60px 0 0 0; /* 给顶部导航栏留出空间 */
}

/* ========== 统一导航栏样式 ========== */
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
/* 修改active样式：字体变蓝 + 蓝色下划线 */
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

/* 导航栏右侧 */
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

/* 用户头像和菜单样式 */
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

/* ========== 测评页面副标题区域 ========== */
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
.back-btn, .report-btn {
  padding: 6px 15px;
  border: 1px solid #2f54eb;
  color: #2f54eb;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.report-btn {
  background: #2f54eb;
  color: #fff;
}

/* ========== 原有测评页面样式 ========== */
/* 2. 测评介绍 */
.test-intro {
  padding: 40px 0;
}
.intro-wrap {
  width: 1200px;
  margin: 0 auto;
}
.intro-card {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.intro-header {
  text-align: center;
  margin-bottom: 30px;
}
.intro-header h2 {
  font-size: 28px;
  color: #2f54eb;
  margin: 0 0 10px 0;
}
.intro-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}
.intro-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}
.theory-desc h3, .test-rules h3 {
  font-size: 20px;
  color: #333;
  margin: 0 0 15px 0;
}
.theory-desc p, .test-rules p {
  font-size: 16px;
  line-height: 1.8;
  color: #666;
  margin: 0;
}
.test-rules ul {
  list-style: none;
  padding: 0;
  margin: 0;
  line-height: 2;
}
.test-rules li {
  position: relative;
  padding-left: 25px;
  margin-bottom: 8px;
}
.test-rules li::before {
  content: "✓";
  color: #2f54eb;
  position: absolute;
  left: 0;
}
.type-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}
.type-card {
  display: flex;
  gap: 15px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  align-items: flex-start;
}
.type-icon {
  font-size: 30px;
}
.type-info h4 {
  font-size: 16px;
  margin: 0 0 8px 0;
  color: #2f54eb;
}
.type-info p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}
.intro-footer {
  text-align: center;
  margin-top: 40px;
}
.start-btn {
  padding: 12px 40px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.3s;
}
.start-btn:hover {
  background: #1d39c4;
}
.tips {
  font-size: 14px;
  color: #999;
  margin-top: 15px;
}

/* 3. 答题界面 */
.test-questions {
  padding: 40px 0;
}
.questions-wrap {
  width: 1200px;
  margin: 0 auto;
}
.progress-bar {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 16px;
}
.progress-container {
  width: 100%;
  height: 8px;
  background: #e8e8e8;
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #2f54eb;
  border-radius: 4px;
  transition: width 0.3s;
}
.question-card {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.question-header h3 {
  font-size: 20px;
  color: #2f54eb;
  margin: 0 0 20px 0;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}
.question-text {
  font-size: 18px;
  line-height: 1.8;
  margin: 0 0 30px 0;
}
.options-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 40px;
}
.option-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}
.option-item:hover {
  border-color: #2f54eb;
  background: #f0f2ff;
}
.option-item input {
  margin-right: 15px;
  width: 20px;
  height: 20px;
  accent-color: #2f54eb;
}
.option-text {
  font-size: 16px;
  color: #666;
}
.question-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}
.prev-btn, .next-btn {
  padding: 10px 30px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
.prev-btn {
  border: 1px solid #e8e8e8;
  color: #666;
  background: #fff;
}
.next-btn {
  border: none;
  background: #2f54eb;
  color: #fff;
}
.prev-btn:disabled, .next-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 4. 测评结果 */
.test-result {
  padding: 40px 0;
}
.result-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 40px;
}
.result-header {
  text-align: center;
}
.result-header h2 {
  font-size: 28px;
  color: #2f54eb;
  margin: 0 0 10px 0;
}
.result-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}
.result-chart {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  text-align: center;
}
.result-chart h3 {
  font-size: 20px;
  color: #333;
  margin: 0 0 30px 0;
}
.chart-container {
  width: 100%;
  max-width: 600px;
  height: 400px;
  margin: 0 auto;
  position: relative;
}
.radar-chart {
  width: 100%;
  height: 100%;
  position: relative;
}
/* 新增：雷达图网格背景 */
.radar-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at center, 
    rgba(47, 84, 235, 0.05) 0%, 
    rgba(47, 84, 235, 0.05) 20%, 
    rgba(47, 84, 235, 0.03) 20%,
    rgba(47, 84, 235, 0.03) 40%,
    rgba(47, 84, 235, 0.02) 40%,
    rgba(47, 84, 235, 0.02) 60%,
    rgba(47, 84, 235, 0.01) 60%,
    rgba(47, 84, 235, 0.01) 80%,
    transparent 80%);
  border-radius: 50%;
}
.radar-axis {
  position: absolute;
  bottom: 50%;
  left: 50%;
  width: 100px;
  height: 50%;
  transform-origin: bottom center;
}
.axis-label {
  position: absolute;
  top: -30px;
  left: 0;
  transform: translateX(-50%);
  font-size: 12px;
  white-space: nowrap;
  z-index: 10;
}
.axis-line {
  width: 2px;
  height: 100%;
  background: #e8e8e8;
  margin: 0 auto;
}
/* 修复：雷达图数据点样式 */
.axis-point {
  position: absolute;
  left: 50%;
  width: 8px !important;
  height: 8px !important;
  background: #2f54eb;
  border-radius: 50%;
  z-index: 20;
}
.radar-fill {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(47, 84, 235, 0.2);
  pointer-events: none;
  z-index: 5;
}
.core-result {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.core-card {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}
.core-icon {
  font-size: 60px;
}
.core-content h3 {
  font-size: 22px;
  color: #2f54eb;
  margin: 0 0 15px 0;
}
.core-desc {
  font-size: 16px;
  line-height: 1.8;
  color: #666;
  margin: 0 0 20px 0;
}
.core-tips h4 {
  font-size: 18px;
  color: #333;
  margin: 0 0 15px 0;
}
.career-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.career-tag {
  padding: 6px 15px;
  background: #f0f2ff;
  color: #2f54eb;
  border-radius: 20px;
  font-size: 14px;
}
.detail-analysis {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.detail-analysis h3 {
  font-size: 20px;
  color: #333;
  margin: 0 0 20px 0;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}
.analysis-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.analysis-card {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #e8e8e8;
}
.analysis-card.top {
  border-left-color: #2f54eb;
  background: #f0f2ff;
}
.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.analysis-header .type-icon {
  font-size: 24px;
}
.analysis-header h4 {
  font-size: 16px;
  margin: 0;
  flex: 1;
  margin-left: 10px;
}
.score-tag {
  padding: 2px 8px;
  background: #2f54eb;
  color: #fff;
  border-radius: 4px;
  font-size: 12px;
}
.analysis-content p {
  font-size: 14px;
  line-height: 1.6;
  color: #666;
  margin: 0 0 15px 0;
}
.recommend-title {
  font-weight: bold;
  margin-bottom: 8px;
}
.recommend-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.recommend-list span {
  padding: 4px 10px;
  background: #fff;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}
.result-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}
.restart-btn, .export-btn, .share-btn, .career-plan-btn {
  padding: 10px 30px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
.restart-btn {
  border: 1px solid #e8e8e8;
  color: #666;
  background: #fff;
}
.export-btn {
  border: none;
  background: #2f54eb;
  color: #fff;
}
.share-btn {
  border: 1px solid #2f54eb;
  color: #2f54eb;
  background: #fff;
}
/* 新增：职业规划报告按钮样式 */
.career-plan-btn {
  border: none;
  background: #1d39c4;
  color: #fff;
  font-weight: bold;
}
.career-plan-btn:hover {
  background: #0f2699;
}

/* 测评报告弹窗 */
.report-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 999;
}
.modal-mask {
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
}
.modal-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
}
.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  color: #2f54eb;
}
.close-btn {
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}
.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}
.report-header {
  text-align: center;
  margin-bottom: 30px;
}
.report-date {
  font-size: 14px;
  color: #999;
  margin: 0 0 10px 0;
}
.report-header h2 {
  font-size: 24px;
  color: #2f54eb;
  margin: 0;
}
.report-section {
  margin-bottom: 30px;
}
.report-section h3 {
  font-size: 18px;
  color: #333;
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}
.report-section p {
  font-size: 16px;
  line-height: 1.8;
  color: #666;
  margin: 0 0 15px 0;
}
.score-table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}
.table-row {
  display: flex;
  border-bottom: 1px solid #e8e8e8;
}
.table-row.header {
  background: #f8f9fa;
  font-weight: bold;
}
.table-cell {
  flex: 1;
  padding: 10px;
  text-align: center;
}
.career-group {
  margin-bottom: 15px;
}
.career-group h4 {
  font-size: 16px;
  margin: 0 0 10px 0;
}
.career-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.career-list span {
  padding: 4px 12px;
  background: #f0f2ff;
  color: #2f54eb;
  border-radius: 4px;
  font-size: 14px;
}
.suggestion-list {
  list-style: none;
  padding: 0;
  margin: 0;
  line-height: 2;
}
.suggestion-list li {
  position: relative;
  padding-left: 25px;
  margin-bottom: 8px;
}
.suggestion-list li::before {
  content: "•";
  color: #2f54eb;
  position: absolute;
  left: 0;
  font-size: 20px;
  line-height: 1;
}
.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #e8e8e8;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.print-btn, .download-btn {
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
}
.print-btn {
  border: 1px solid #2f54eb;
  color: #2f54eb;
  background: #fff;
}
.download-btn {
  border: none;
  background: #2f54eb;
  color: #fff;
}

/* 5. 页脚 */
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

/* 响应式适配 */
@media (max-width: 1200px) {
  .header-wrap,
  .intro-wrap,
  .questions-wrap,
  .result-wrap,
  .footer-wrap {
    width: 90%;
  }
  .type-cards, .analysis-cards {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 768px) {
  .core-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .chart-container {
    height: 300px;
  }
  .question-card {
    padding: 20px;
  }
  .question-text {
    font-size: 16px;
  }
  .result-actions {
    flex-direction: column;
    align-items: center;
  }
  .restart-btn, .export-btn, .share-btn, .career-plan-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>
<template>
  <div class="job-portrait-page">
    <!-- 固定顶部的导航栏 -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" :class="{active: $route.path === '/'}" @click="$router.push('/')">首页</li>
            <li class="menu-item" :class="{active: $route.path.includes('/job-portrait')}" @click="$router.push('/job-portrait')">岗位画像</li>
            <li class="menu-item" :class="{active: $route.path === '/career-planning'}" @click="$router.push('/career-planning')">职业规划</li>
            <li class="menu-item" :class="{active: $route.path === '/resource-library'}" @click="$router.push('/resource-library')">资源库</li>
            <li class="menu-item" :class="{active: $route.path === '/about-us'}" @click="$router.push('/about-us')">关于我们</li>
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
              ref="searchInputRef"
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
  
    <!-- 岗位画像内容容器（适配固定导航栏，避免遮挡） -->
    <div class="job-portrait-container">
      <!-- 面包屑导航 + 岗位标题区域 -->
      <div class="page-header">
        <div class="breadcrumb">
          <span class="breadcrumb-item" @click="$router.push('/')">首页</span>
          <span class="separator">/</span>
          <span class="breadcrumb-item">{{ currentJob.jobName }}</span>
          <span class="separator">/</span>
          <span class="breadcrumb-item current">岗位画像详情</span>
        </div>
        
        <!-- 岗位标题卡片 -->
        <div class="job-header-card">
          <h1 class="job-title">{{ currentJob.jobName }}</h1>
          <div class="job-tag-container">
            <el-tag 
              v-for="tag in getCoreTags()" 
              :key="tag" 
              size="medium" 
              class="job-tag"
            >{{ tag }}</el-tag>
          </div>
          <div class="job-score-card">
            <div class="score-label">综合能力评分</div>
            <div class="score-value">{{ totalScore }}分</div>
            <!-- 修改后的星星评分展示 - 支持半星 -->
            <div class="star-rating">
              <div 
                v-for="(star, index) in 5" 
                :key="index" 
                class="star-wrapper"
              >
                <!-- 背景星星（灰色） -->
                <span class="star background">★</span>
                <!-- 前景星星（黄色）- 通过裁剪控制显示 -->
                <span 
                  class="star foreground"
                  :style="{clipPath: getStarClipPath(index)}"
                >★</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 核心信息区域 - 重新布局 -->
      <div class="core-info-section">
        <!-- 左侧：技能和证书 -->
        <div class="left-panel">
          <el-card 
            header="专业技能要求" 
            shadow="hover" 
            class="info-card skills-card"
          >
            <div class="skill-grid">
              <div 
                v-for="(skill, index) in currentJob.skills" 
                :key="skill" 
                class="skill-card"
                :style="{animationDelay: `${index * 0.1}s`}"
              >
                <i class="el-icon-s-tools skill-icon"></i> 
                <span class="skill-text">{{ skill }}</span>
              </div>
            </div>
          </el-card>
          
          <el-card 
            header="证书资质要求" 
            shadow="hover" 
            class="info-card certs-card"
          >
            <div class="cert-grid">
              <div 
                v-for="(cert, index) in currentJob.certificates" 
                :key="cert" 
                class="cert-card"
                :style="{animationDelay: `${index * 0.1}s`}"
              >
                <i class="el-icon-trophy cert-icon"></i> 
                <span class="cert-text">{{ cert }}</span>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 右侧：能力雷达图 -->
        <div class="right-panel">
          <el-card 
            header="综合能力评估" 
            shadow="hover" 
            class="info-card radar-card"
          >
            <div ref="radarChartRef" class="radar-chart-container"></div>
          </el-card>
        </div>
      </div>
      
      <!-- 岗位发展路径区域 -->
      <div class="career-path-section">
        <el-card 
          header="岗位发展路径规划" 
          shadow="hover" 
          class="info-card path-card"
        >
          <div class="path-header">
            <el-button 
              type="primary" 
              icon="el-icon-map-location" 
              @click="openGraphDialog"
              class="graph-btn"
            >
              查看岗位发展路径图谱
            </el-button>
            <p class="path-desc">清晰的职业发展路径，助力你的职业规划</p>
          </div>
          
          <!-- 路径展示 - 双列布局 -->
          <div class="path-content">
            <div class="path-column">
              <h3 class="path-column-title">
                <i class="el-icon-arrow-up"></i> 垂直晋升路径
              </h3>
              <div class="path-timeline">
                <div 
                  v-for="(item, index) in jobGraphConfig.vertical" 
                  :key="index" 
                  class="timeline-item"
                >
                  <div class="timeline-dot" :style="{backgroundColor: getStepColor(index)}"></div>
                  <div class="timeline-content">
                    <div class="timeline-step">第{{ index + 1 }}阶段</div>
                    <div class="timeline-position">{{ item }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="path-column">
              <h3 class="path-column-title">
                <i class="el-icon-switch"></i> 换岗发展路径
              </h3>
              <div class="path-grid">
                <div 
                  v-for="(item, index) in jobGraphConfig.switch" 
                  :key="index" 
                  class="switch-card"
                >
                  <div class="switch-icon">
                    <i class="el-icon-refresh"></i>
                  </div>
                  <div class="switch-position">{{ item }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 岗位图谱弹窗 -->
      <el-dialog 
        v-model="graphVisible" 
        :title="`${currentJob.jobName} - 职业发展路径图谱`" 
        width="90%"
        top="50px"
        class="graph-dialog"
        custom-class="custom-dialog"
        append-to-body
      >
        <div ref="graphChartRef" class="graph-chart-container"></div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// 导航栏相关状态
const router = useRouter()
const route = useRoute()
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const showDropdown = ref(false)
const searchInputRef = ref(null)
const radarChartRef = ref(null)
const graphChartRef = ref(null)

// 存储echarts实例，防止内存泄漏
let radarChart = null
let graphChart = null

// 监听路由变化更新登录状态
watch(
  () => route.path,
  () => {
    isLogin.value = !!localStorage.getItem('token')
    userAvatar.value = localStorage.getItem('avatar') || ''
  },
  { immediate: true }
)

// 导航栏方法
const goToFeature = (feature) => {
  showDropdown.value = false
  const featureRoutes = {
    '测评': '/interest-test',
    '分析': '/ability-analysis',
    '规划': '/development-path',
    '导出': '/report-export'
  }
  router.push(featureRoutes[feature] || '/')
  ElMessage.info(`即将前往${feature}功能页面`)
}

const handleSearch = () => {
  if (!searchInputRef.value) return
  const keyword = searchInputRef.value.value?.trim()
  if (!keyword) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  router.push({ path: '/search', query: { keyword } })
  searchInputRef.value.value = ''
  ElMessage.success(`正在搜索：${keyword}`)
}

const toggleTheme = () => {
  const darkMode = localStorage.getItem('darkMode') === 'true'
  localStorage.setItem('darkMode', !darkMode)
  if (!darkMode) document.body.classList.add('dark')
  else document.body.classList.remove('dark')
  ElMessage.success(`已切换${!darkMode ? '暗黑' : '默认'}主题`)
}

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

// 能力映射
const abilityMap = {
  innovation: '创新能力',
  learning: '学习能力',
  pressure: '抗压能力',
  communication: '沟通能力',
  internship: '实践能力'
}

// 获取步骤颜色
const getStepColor = (index) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  return colors[index % colors.length]
}

// 所有岗位数据
const allJobs = [
  {
    jobName: '数据分析师',
    skills: ['Python', 'SQL', 'Tableau', 'Excel'],
    certificates: ['计算机二级', 'CDA', '英语六级'],
    abilities: { innovation: 85, learning: 90, pressure: 80, communication: 85, internship: 88 },
    coreTags: ['数据分析', '可视化', '业务理解']
  },
  {
    jobName: '前端开发工程师',
    skills: ['HTML/CSS', 'JavaScript', 'Vue', 'React', 'TS'],
    certificates: ['计算机二级', '软考中级'],
    abilities: { innovation: 80, learning: 95, pressure: 85, communication: 75, internship: 82 },
    coreTags: ['前端开发', '用户体验', '跨端开发']
  },
  {
    jobName: '后端开发工程师',
    skills: ['Java', 'SpringBoot', 'MySQL', 'Redis'],
    certificates: ['计算机二级', '软考中级'],
    abilities: { innovation: 75, learning: 90, pressure: 90, communication: 70, internship: 78 },
    coreTags: ['后端开发', '数据库', '高并发']
  },
  {
    jobName: '产品经理',
    skills: ['Axure', 'PRD', '用户调研', '数据分析'],
    certificates: ['PMP', '英语六级'],
    abilities: { innovation: 90, learning: 85, pressure: 85, communication: 95, internship: 90 },
    coreTags: ['产品设计', '需求分析', '项目管理']
  },
  {
    jobName: '测试开发工程师',
    skills: ['Python', 'JUnit', 'Selenium', '接口测试'],
    certificates: ['计算机二级', '软件测试工程师认证'],
    abilities: { innovation: 70, learning: 85, pressure: 80, communication: 75, internship: 80 },
    coreTags: ['自动化测试', '质量保障', '接口测试']
  },
  {
    jobName: 'UI设计师',
    skills: ['PS', 'AI', 'Figma', '交互设计'],
    certificates: ['Adobe认证', '设计类大赛证书'],
    abilities: { innovation: 95, learning: 85, pressure: 75, communication: 80, internship: 82 },
    coreTags: ['视觉设计', '交互体验', '创意设计']
  },
  {
    jobName: '运维开发工程师',
    skills: ['Linux', 'Docker', 'K8s', 'Shell'],
    certificates: ['红帽认证', '软考中级'],
    abilities: { innovation: 75, learning: 80, pressure: 85, communication: 70, internship: 75 },
    coreTags: ['运维自动化', '容器化', '云原生']
  },
  {
    jobName: '大数据开发工程师',
    skills: ['Hadoop', 'Spark', 'Hive', 'Java'],
    certificates: ['计算机二级', 'CDA高级'],
    abilities: { innovation: 80, learning: 95, pressure: 90, communication: 75, internship: 78 },
    coreTags: ['大数据', '分布式计算', '数据仓库']
  },
  {
    jobName: '网络安全工程师',
    skills: ['渗透测试', '防火墙', '漏洞挖掘', 'Python'],
    certificates: ['CISP', 'CEH'],
    abilities: { innovation: 85, learning: 90, pressure: 85, communication: 70, internship: 75 },
    coreTags: ['网络安全', '渗透测试', '漏洞修复']
  },
  {
    jobName: '电商运营',
    skills: ['淘宝运营', '数据分析', '文案写作', '直播策划'],
    certificates: ['电商运营师', '英语四级'],
    abilities: { innovation: 85, learning: 80, pressure: 80, communication: 90, internship: 92 },
    coreTags: ['电商运营', '直播策划', '用户增长']
  },
  {
    jobName: '人工智能工程师',
    skills: ['Python', 'TensorFlow', 'PyTorch', '机器学习'],
    certificates: ['计算机二级', 'AI工程师认证'],
    abilities: { innovation: 90, learning: 95, pressure: 90, communication: 80, internship: 75 },
    coreTags: ['机器学习', '深度学习', '模型训练']
  },
  {
    jobName: '金融分析师',
    skills: ['Excel', 'SQL', '金融建模', '行业分析'],
    certificates: ['CFA', 'FRM', '英语六级'],
    abilities: { innovation: 80, learning: 90, pressure: 85, communication: 85, internship: 88 },
    coreTags: ['金融分析', '风险评估', '投资分析']
  }
]

// 岗位路径配置
const jobGraphConfigs = {
  '数据分析师': {
    vertical: ['初级数据分析师', '中级数据分析师', '高级数据分析师', '数据分析主管', '数据总监'],
    switch: ['大数据开发工程师', '产品经理', '金融分析师']
  },
  '前端开发工程师': {
    vertical: ['初级前端', '中级前端', '高级前端', '前端技术组长', '前端架构师'],
    switch: ['UI设计师', '全栈开发工程师', '产品经理']
  },
  '产品经理': {
    vertical: ['产品助理', '初级产品经理', '高级产品经理', '产品总监', 'CEO'],
    switch: ['数据分析师', '电商运营', '项目经理']
  },
  'UI设计师': {
    vertical: ['UI设计师', '资深UI设计师', '交互设计组长', '设计总监', '创意总监'],
    switch: ['前端开发工程师', '产品经理', '电商运营']
  },
  '电商运营': {
    vertical: ['运营助理', '电商运营专员', '运营主管', '运营经理', '运营总监'],
    switch: ['产品经理', '数据分析师', 'UI设计师']
  },
  '后端开发工程师': {
    vertical: ['初级后端', '中级后端', '高级后端', '后端技术组长', '后端架构师'],
    switch: ['大数据开发工程师', '运维开发工程师', '测试开发工程师']
  },
  '测试开发工程师': {
    vertical: ['初级测试', '中级测试', '高级测试', '测试组长', '测试经理'],
    switch: ['后端开发工程师', '产品经理', '运维开发工程师']
  },
  '运维开发工程师': {
    vertical: ['初级运维', '中级运维', '高级运维', '运维组长', '运维总监'],
    switch: ['后端开发工程师', '大数据开发工程师', '网络安全工程师']
  },
  '大数据开发工程师': {
    vertical: ['初级大数据开发', '中级大数据开发', '高级大数据开发', '大数据架构师', '数据技术总监'],
    switch: ['数据分析师', '后端开发工程师', '人工智能工程师']
  },
  '网络安全工程师': {
    vertical: ['初级安全工程师', '中级安全工程师', '高级安全工程师', '安全主管', '安全总监'],
    switch: ['运维开发工程师', '大数据开发工程师', '后端开发工程师']
  },
  '人工智能工程师': {
    vertical: ['初级AI工程师', '中级AI工程师', '高级AI工程师', 'AI架构师', 'AI技术总监'],
    switch: ['数据分析师', '大数据开发工程师', '后端开发工程师']
  },
  '金融分析师': {
    vertical: ['初级金融分析师', '中级金融分析师', '高级金融分析师', '金融分析主管', '金融分析总监'],
    switch: ['数据分析师', '产品经理', '电商运营']
  }
}

// 路由参数和状态管理
const currentJob = ref(allJobs[0])
const graphVisible = ref(false)
const jobGraphConfig = ref(jobGraphConfigs['数据分析师'])

// 计算综合能力总分
const totalScore = computed(() => {
  const abilities = currentJob.value.abilities
  const sum = Object.values(abilities).reduce((a, b) => a + b, 0)
  return Math.round(sum / Object.keys(abilities).length)
})

// 计算精确的星星数（支持小数）
const starCount = computed(() => {
  // 总分/100*5 得到精确的星星数
  return (totalScore.value / 100) * 5
})

// 获取星星的裁剪路径，实现半星效果
const getStarClipPath = (index) => {
  const starNumber = index + 1
  const starValue = starCount.value
  
  if (starValue >= starNumber) {
    // 完整星星
    return 'inset(0 0 0 0)'
  } else if (starValue > index) {
    // 半星 - 计算显示的比例
    const percentage = ((starValue - index) * 100).toFixed(2) + '%'
    return `inset(0 ${100 - parseFloat(percentage)}% 0 0)`
  } else {
    // 空星星 - 完全裁剪掉前景
    return 'inset(0 100% 0 0)'
  }
}

// 获取核心标签
const getCoreTags = () => {
  return currentJob.value.coreTags || ['暂无标签']
}

// 打开图谱弹窗
const openGraphDialog = () => {
  graphVisible.value = true
  setTimeout(() => {
    initJobGraph()
  }, 100)
}

// 初始化能力雷达图
const initRadarChart = () => {
  if (!radarChartRef.value) return
  
  if (radarChart) {
    radarChart.dispose()
  }
  
  radarChart = echarts.init(radarChartRef.value)
  
  const abilities = currentJob.value.abilities
  const radarData = Object.keys(abilities).map(key => ({
    name: abilityMap[key],
    value: abilities[key]
  }))
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133' },
      padding: 12,
      borderRadius: 8
    },
    radar: {
      indicator: radarData.map(item => ({ name: item.name, max: 100 })),
      shape: 'circle',
      splitNumber: 5,
      radius: '80%',
      name: {
        textStyle: { color: '#606266', fontSize: 14 }
      },
      splitLine: { lineStyle: { color: '#e4e7ed', width: 1 } },
      splitArea: { areaStyle: { color: ['#f8f9fa', '#ffffff'], opacity: 0.8 } },
      axisLine: { lineStyle: { color: '#c0c4cc' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: radarData.map(item => item.value),
        name: '能力评分',
        areaStyle: { color: 'rgba(64, 158, 255, 0.25)', opacity: 0.8 },
        lineStyle: { color: '#409EFF', width: 3 },
        itemStyle: { color: '#409EFF', borderWidth: 2, borderColor: '#ffffff' },
        symbol: 'circle',
        symbolSize: 8
      }]
    }]
  }
  
  radarChart.setOption(option)
  
  const resizeHandler = () => {
    radarChart.resize()
  }
  window.addEventListener('resize', resizeHandler)
  
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
  })
}

// 初始化岗位发展路径图谱
const initJobGraph = () => {
  if (!graphChartRef.value) return
  
  if (graphChart) {
    graphChart.dispose()
  }
  
  graphChart = echarts.init(graphChartRef.value)
  
  const config = jobGraphConfig.value
  const nodes = []
  const links = []
  
  // 垂直路径节点
  config.vertical.forEach((item, index) => {
    nodes.push({ 
      name: item, 
      category: 0, 
      symbolSize: 50 + (index * 5),
      itemStyle: { 
        color: '#409EFF',
        borderColor: '#ffffff',
        borderWidth: 2,
        shadowColor: 'rgba(64, 158, 255, 0.5)',
        shadowBlur: 10
      }
    })
    if (index > 0) {
      links.push({ 
        source: config.vertical[index-1], 
        target: item, 
        lineStyle: { 
          color: '#409EFF', 
          width: 3,
          shadowColor: 'rgba(64, 158, 255, 0.2)',
          shadowBlur: 5
        },
        label: { 
          show: true, 
          formatter: '晋升',
          fontSize: 12,
          color: '#606266',
          backgroundColor: 'rgba(255,255,255,0.8)',
          borderRadius: 4,
          padding: [2, 6]
        }
      })
    }
  })
  
  // 换岗路径节点
  config.switch.forEach((item) => {
    nodes.push({ 
      name: item, 
      category: 1, 
      symbolSize: 45,
      itemStyle: { 
        color: '#67C23A',
        borderColor: '#ffffff',
        borderWidth: 2,
        shadowColor: 'rgba(103, 194, 58, 0.5)',
        shadowBlur: 10
      }
    })
    links.push({ 
      source: config.vertical[2], 
      target: item, 
      lineStyle: { 
        color: '#67C23A', 
        width: 2, 
        type: 'dashed',
        shadowColor: 'rgba(103, 194, 58, 0.2)',
        shadowBlur: 5
      },
      label: { 
        show: true, 
        formatter: '换岗',
        fontSize: 12,
        color: '#606266',
        backgroundColor: 'rgba(255,255,255,0.8)',
        borderRadius: 4,
        padding: [2, 6]
      }
    })
  })
  
  const option = {
    backgroundColor: '#ffffff',
    title: { 
      text: `${currentJob.value.jobName} - 职业发展路径图谱`,
      left: 'center',
      textStyle: { fontSize: 18, fontWeight: 600, color: '#303133' }
    },
    tooltip: { 
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133' }
    },
    legend: [{ 
      data: ['垂直晋升', '换岗路径'], 
      top: 'bottom',
      textStyle: { color: '#606266' }
    }],
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: links,
        categories: [{ name: '垂直晋升' }, { name: '换岗路径' }],
        roam: true,
        label: {
          show: true,
          fontSize: 14,
          color: '#fff',
          fontWeight: 'bold',
          shadowColor: 'rgba(0,0,0,0.2)',
          shadowBlur: 2
        },
        force: {
          repulsion: 2800,
          edgeLength: 220,
          gravity: 0.15
        }
      }
    ]
  }
  
  graphChart.setOption(option)
  
  const resizeHandler = () => {
    graphChart.resize()
  }
  window.addEventListener('resize', resizeHandler)
  
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
  })
}

// 监听路由参数变化加载对应岗位
watch(() => route.query.jobName, (jobName) => {
  if (jobName) {
    const job = allJobs.find(item => item.jobName === jobName)
    if (job) {
      currentJob.value = job
      jobGraphConfig.value = jobGraphConfigs[jobName] || jobGraphConfigs['数据分析师']
    } else {
      ElMessage.warning('未找到该岗位画像，显示默认岗位')
      currentJob.value = allJobs[0]
      jobGraphConfig.value = jobGraphConfigs['数据分析师']
    }
  }
  initRadarChart()
}, { immediate: true })

// 页面挂载时初始化
onMounted(() => {
  initRadarChart()
  jobGraphConfig.value = jobGraphConfigs[currentJob.value.jobName] || jobGraphConfigs['数据分析师']
  
  // 点击页面其他区域关闭下拉菜单
  const clickHandler = (e) => {
    if (!e.target.closest('.dropdown')) {
      showDropdown.value = false
    }
    if (!e.target.closest('.user-profile')) {
      isUserMenuOpen.value = false
    }
  }
  document.addEventListener('click', clickHandler)
  
  // 应用暗黑主题
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark')
  }
  
  // 组件卸载时清理
  onUnmounted(() => {
    document.removeEventListener('click', clickHandler)
    if (radarChart) radarChart.dispose()
    if (graphChart) graphChart.dispose()
  })
})
</script>

<style scoped>
/* 全局容器 */
.job-portrait-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", "PingFang SC", sans-serif;
  color: #303133;
  /* 修改为偏白色的背景 - 浅灰白色调 */
  background: #fafbfc;
  margin: 0;
  padding: 0;
}

/* ========== 导航栏样式（保留原有样式） ========== */
:deep(.top-nav) {
  height: 60px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
}

:deep(.nav-wrap) {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

:deep(.nav-left) {
  display: flex;
  align-items: center;
}

:deep(.logo) {
  display: flex;
  align-items: center;
  margin-right: 40px;
  font-size: 18px;
  font-weight: bold;
  color: #000;
}

:deep(.logo-icon) {
  font-size: 24px;
  margin-right: 8px;
}

:deep(.nav-menu) {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

:deep(.menu-item) {
  margin: 0 15px;
  font-size: 14px;
  cursor: pointer;
  padding: 0 5px;
  position: relative;
  height: 60px;
  line-height: 60px;
  color: #000;
  transition: color 0.3s ease;
}

:deep(.menu-item:hover) {
  color: #2f54eb;
}

:deep(.menu-item.active) {
  color: #2f54eb;
}

:deep(.dropdown) {
  position: relative;
}

:deep(.dropdown-menu) {
  position: absolute;
  top: 100%;
  left: 0;
  width: 200px;
  background: #fff;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  border-radius: 8px;
  list-style: none;
  padding: 8px 0;
  margin: 0;
  display: none;
  z-index: 9999;
}

:deep(.dropdown:hover .dropdown-menu) {
  display: block;
  animation: fadeIn 0.3s ease;
}

:deep(.dropdown-item) {
  padding: 12px 20px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  height: auto;
  line-height: normal;
  color: #333;
  transition: background 0.3s ease;
}

:deep(.dropdown-item:hover) {
  background: #f0f7ff;
}

:deep(.color-dot) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

:deep(.color-dot.red) { background: #ff7a45; }
:deep(.color-dot.orange) { background: #faad14; }
:deep(.color-dot.green) { background: #52c41a; }
:deep(.color-dot.blue) { background: #1890ff; }

:deep(.nav-right) {
  display: flex;
  gap: 15px;
  align-items: center;
}

:deep(.nav-search-wrap) {
  display: flex;
  width: 200px;
  height: 24px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  transition: border 0.3s ease;
}

:deep(.nav-search-wrap:focus-within) {
  border-color: #2f54eb;
}

:deep(.nav-search-input) {
  flex: 1;
  height: 100%;
  padding: 0 12px;
  border: none;
  outline: none;
  font-size: 12px;
  background: transparent;
}

:deep(.nav-search-btn) {
  width: 53px;
  height: 100%;
  background: #2f54eb;
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.3s ease;
}

:deep(.nav-search-btn:hover) {
  background: #1d39c4;
}

:deep(.btn-toggle-theme) {
  padding: 6px 10px;
  border: none;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  color: #000;
  transition: all 0.3s ease;
}

:deep(.btn-toggle-theme:hover) {
  background: #e8e8e8;
}

:deep(.btn-login) {
  padding: 6px 15px;
  border: 1px solid #2f54eb;
  color: #2f54eb;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

:deep(.btn-login:hover) {
  background: #f0f7ff;
}

:deep(.btn-register) {
  padding: 6px 15px;
  border: none;
  color: #fff;
  background: #2f54eb;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

:deep(.btn-register:hover) {
  background: #1d39c4;
}

:deep(.user-profile) {
  position: relative;
  display: flex;
  align-items: center;
}

:deep(.avatar) {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #f0f0f0;
  transition: border 0.3s ease;
}

:deep(.avatar:hover) {
  border-color: #2f54eb;
}

:deep(.user-menu) {
  position: absolute;
  top: 50px;
  right: 0;
  width: 120px;
  background: #fff;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  border-radius: 8px;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

:deep(.user-menu .menu-item) {
  padding: 10px 15px;
  font-size: 14px;
  cursor: pointer;
  height: auto;
  line-height: normal;
  margin: 0;
  color: #333;
  transition: background 0.3s ease;
}

:deep(.user-menu .menu-item:hover) {
  background: #f0f7ff;
  color: #333;
}

:deep(.user-menu .logout) {
  color: #ff4d4f;
  border-top: 1px solid #f0f0f0;
}

/* ========== 重新设计的页面内容样式 ========== */
.job-portrait-container {
  width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 60px;
  min-height: calc(100vh - 60px);
  /* 内容容器使用纯白色背景 */
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

/* 页面头部 - 面包屑 + 岗位标题 */
.page-header {
  padding: 24px 32px;
  /* 添加背景色并设置高优先级 */
  background: #fff !important;
}

.breadcrumb {
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.breadcrumb-item {
  cursor: pointer;
  transition: all 0.3s ease;
}

.breadcrumb-item:hover {
  color: #409EFF;
  transform: translateY(-1px);
}

.separator {
  color: #909399;
  cursor: default;
}

.current {
  color: #303133;
  font-weight: 600;
  cursor: default;
}

/* 岗位标题卡片 */
.job-header-card {
  padding: 0 0 24px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0;
  border-bottom: 1px solid #f0f2f5;
}

.job-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 20px 0 0;
  background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.job-tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 0 20px;
}

.job-tag {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
  color: #409EFF;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.job-tag:hover {
  background: #409EFF;
  color: #ffffff;
  transform: scale(1.05);
}

.job-score-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f8f9fa;
  padding: 12px 20px;
  border-radius: 12px;
}

.score-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
  margin: 0 8px;
  white-space: nowrap;
}

/* 修复星星评分样式 - 支持半星 */
.star-rating {
  display: flex;
  gap: 2px;
  line-height: 1;
  align-items: center;
}

.star-wrapper {
  position: relative;
  display: inline-block;
  height: 20px;
  width: 20px;
  line-height: 1;
}

.star {
  position: absolute;
  top: 0;
  left: 0;
  font-size: 20px;
  width: 100%;
  height: 100%;
  display: inline-block;
  line-height: 1;
}

/* 背景星星 - 灰色 */
.star.background {
  color: #dcdfe6; /* 未激活星星颜色 - 灰色 */
  z-index: 1;
}

/* 前景星星 - 黄色 */
.star.foreground {
  color: #E6A23C; /* 激活星星的黄色 */
  z-index: 2;
  transition: clip-path 0.3s ease;
}

/* 通用卡片样式 */
:deep(.info-card) {
  border: none;
  border-radius: 0;
  box-shadow: none;
  margin-bottom: 0;
  border-bottom: 1px solid #f0f2f5;
}

:deep(.info-card:last-child) {
  border-bottom: none;
}

:deep(.info-card .el-card__header) {
  background: #f9fafc;
  border-bottom: 1px solid #f0f2f5;
  padding: 16px 20px;
  font-weight: 600;
  font-size: 16px;
  color: #1f2937;
  border-radius: 0;
}

:deep(.info-card .el-card__body) {
  padding: 20px;
}

/* 核心信息区域 */
.core-info-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border-bottom: 1px solid #f0f2f5;
}

.left-panel, .right-panel {
  border-right: 1px solid #f0f2f5;
}

.right-panel {
  border-right: none;
}

/* 技能卡片样式 */
.skill-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.skill-card {
  background: linear-gradient(135deg, #e8f4f8 0%, #f0f9ff 100%);
  border-radius: 10px;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 1px solid rgba(64, 158, 255, 0.1);
  transition: all 0.4s ease;
  animation: fadeInUp 0.6s ease forwards;
  opacity: 0;
  transform: translateY(10px);
}

.skill-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 8px 16px rgba(64, 158, 255, 0.15);
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
}

.skill-icon {
  font-size: 24px;
  color: #409EFF;
  margin-bottom: 8px;
}

.skill-text {
  font-size: 14px;
  font-weight: 500;
  color: #1989fa;
}

/* 证书卡片样式 */
.cert-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.cert-card {
  background: linear-gradient(135deg, #fef7fb 0%, #fef0c7 100%);
  border-radius: 10px;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 1px solid rgba(230, 162, 60, 0.1);
  transition: all 0.4s ease;
  animation: fadeInUp 0.6s ease forwards;
  opacity: 0;
  transform: translateY(10px);
}

.cert-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 8px 16px rgba(230, 162, 60, 0.15);
  background: linear-gradient(135deg, #fef0c7 0%, #fde68a 100%);
}

.cert-icon {
  font-size: 24px;
  color: #E6A23C;
  margin-bottom: 8px;
}

.cert-text {
  font-size: 14px;
  font-weight: 500;
  color: #d48806;
}

/* 雷达图样式 */
.radar-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.radar-chart-container {
  width: 100%;
  height: 400px;
  flex: 1;
}

/* 职业发展路径区域 */
.career-path-section {
  margin-bottom: 0;
}

.path-card {
  height: 100%;
}

.path-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.graph-btn {
  background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);
  border: none;
  border-radius: 8px;
  padding: 10px 24px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
}

.graph-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  background: linear-gradient(135deg, #3399ff 0%, #52c41a 100%);
}

.path-desc {
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.path-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.path-column {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
}

.path-column-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.path-column-title i {
  color: #409EFF;
  font-size: 18px;
}

/* 时间线样式 */
.path-timeline {
  position: relative;
  padding-left: 30px;
}

.path-timeline::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #409EFF 0%, #67C23A 100%);
  border-radius: 1px;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
  padding-bottom: 8px;
}

.timeline-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -30px;
  top: 4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.1);
  z-index: 1;
}

.timeline-content {
  background: #ffffff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.timeline-content:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.timeline-step {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.timeline-position {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

/* 换岗路径网格 */
.path-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.switch-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(103, 194, 58, 0.1);
  transition: all 0.3s ease;
}

.switch-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.15);
}

.switch-icon {
  font-size: 24px;
  color: #67C23A;
  margin-bottom: 8px;
}

.switch-position {
  font-size: 14px;
  font-weight: 500;
  color: #52c41a;
}

/* 图谱弹窗样式 - 核心修改：去掉黑条，改为白色背景 */
:deep(.custom-dialog) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

/* 弹窗头部：彻底覆盖 Element Plus 默认的 #2A2A2A 黑色背景，改为纯白色 */
:deep(.custom-dialog .el-dialog__header) {
  background: #ffffff !important;
  border-bottom: 1px solid #f0f2f5;
  padding: 20px 24px;
}

:deep(.custom-dialog .el-dialog__title) {
  font-weight: 600;
  color: #1f2937;
  font-size: 18px;
}

/* 关闭按钮颜色适配白色背景 */
:deep(.custom-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: #606266 !important;
}
:deep(.custom-dialog .el-dialog__headerbtn .el-dialog__close:hover) {
  color: #409EFF !important;
}

:deep(.custom-dialog .el-dialog__body) {
  padding: 24px;
  background: #ffffff !important;
}

.graph-chart-container {
  width: 100%;
  height: 600px;
  background: #ffffff !important;
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式适配 */
@media (max-width: 1200px) {
  :deep(.nav-wrap), .job-portrait-container {
    width: 95%;
    padding-left: 20px;
    padding-right: 20px;
  }
  
  .core-info-section {
    grid-template-columns: 1fr !important;
  }
  
  .left-panel {
    border-right: none;
    border-bottom: 1px solid #f0f2f5;
  }
  
  .radar-chart-container {
    height: 350px;
  }
  
  .graph-chart-container {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .job-header-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .path-content {
    grid-template-columns: 1fr;
  }
  
  .radar-chart-container {
    height: 300px;
  }
  
  .graph-chart-container {
    height: 400px;
  }
  
  .skill-grid, .cert-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .skill-grid, .cert-grid {
    grid-template-columns: 1fr;
  }
  
  .path-grid {
    grid-template-columns: 1fr;
  }
}
</style>
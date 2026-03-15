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
      <!-- 面包屑导航（移除Back按钮） -->
      <div class="breadcrumb">
        <span class="breadcrumb-item" @click="$router.push('/')">首页</span>
        <span class="separator">/</span>
        <span class="breadcrumb-item">{{ currentJob.jobName }}</span>
        <span class="separator">/</span>
        <span class="breadcrumb-item current">岗位画像详情</span>
      </div>
      
      <!-- 岗位画像核心信息卡片 -->
      <el-row :gutter="20" style="margin: 20px 0;">
        <!-- 岗位基本信息 -->
        <el-col :span="8">
          <el-card header="岗位基本信息" shadow="hover">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="岗位名称">
                <span class="job-name">{{ currentJob.jobName }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="核心标签">
                <el-tag v-for="tag in getCoreTags()" :key="tag" size="small">{{ tag }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="综合能力评分">
                <el-rate 
                  v-model="totalScore" 
                  disabled 
                  max="100" 
                  show-score 
                  text-color="#ff9900"
                  score-template="{value}分"
                ></el-rate>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
        
        <!-- 专业技能 -->
        <el-col :span="8">
          <el-card header="专业技能要求" shadow="hover">
            <div class="skill-list">
              <div 
                v-for="skill in currentJob.skills" 
                :key="skill" 
                class="skill-item"
              >
                <i class="el-icon-s-tools"></i> {{ skill }}
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 证书要求 -->
        <el-col :span="8">
          <el-card header="证书资质要求" shadow="hover">
            <div class="cert-list">
              <div 
                v-for="cert in currentJob.certificates" 
                :key="cert" 
                class="cert-item"
              >
                <i class="el-icon-trophy"></i> {{ cert }}
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 综合能力雷达图 -->
      <el-card header="综合能力评估雷达图" shadow="hover" style="margin: 20px 0;">
        <div ref="radarChartRef" style="width: 100%; height: 400px;"></div>
      </el-card>
      
      <!-- 岗位发展路径 -->
      <el-card header="岗位发展路径规划" shadow="hover" style="margin: 20px 0;">
        <el-button 
          type="primary" 
          icon="el-icon-map-location" 
          @click="openGraphDialog"
          style="margin-bottom: 20px;"
        >
          查看岗位发展路径图谱
        </el-button>
        
        <!-- 路径说明 -->
        <el-collapse>
          <el-collapse-item title="垂直晋升路径" name="1">
            <div class="path-list">
              <div v-for="(item, index) in jobGraphConfig.vertical" :key="index" class="path-item">
                <span class="step">{{ index + 1 }}.</span> {{ item }}
              </div>
            </div>
          </el-collapse-item>
          <el-collapse-item title="换岗发展路径" name="2">
            <div class="path-list">
              <div v-for="(item, index) in jobGraphConfig.switch" :key="index" class="path-item">
                <span class="step">{{ index + 1 }}.</span> {{ item }}
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>
      
      <!-- 岗位图谱弹窗 -->
      <el-dialog 
        v-model="graphVisible" 
        :title="`${currentJob.jobName} - 垂直晋升+换岗路径图谱`" 
        width="80%"
        top="80px"
      >
        <div ref="graphChartRef" style="width: 100%; height: 600px;"></div>
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
  internship: '实习能力'
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
    title: { text: '综合能力评估', left: 'center' },
    tooltip: { trigger: 'item' },
    radar: {
      indicator: radarData.map(item => ({ name: item.name, max: 100 })),
      shape: 'polygon',
      splitNumber: 5,
      name: {
        textStyle: { color: '#333' }
      },
      splitLine: { lineStyle: { color: '#e0e0e0' } },
      splitArea: { areaStyle: { color: ['#f9f9f9', '#ffffff'] } },
      axisLine: { lineStyle: { color: '#333' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: radarData.map(item => item.value),
        name: '能力评分',
        areaStyle: { color: 'rgba(64, 158, 255, 0.2)' },
        lineStyle: { color: '#409EFF', width: 2 },
        itemStyle: { color: '#409EFF' }
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
      itemStyle: { color: '#409EFF' }
    })
    if (index > 0) {
      links.push({ 
        source: config.vertical[index-1], 
        target: item, 
        lineStyle: { color: '#409EFF', width: 2 },
        label: { show: true, formatter: '晋升' }
      })
    }
  })
  
  // 换岗路径节点
  config.switch.forEach((item) => {
    nodes.push({ 
      name: item, 
      category: 1, 
      symbolSize: 45,
      itemStyle: { color: '#67C23A' }
    })
    links.push({ 
      source: config.vertical[2], 
      target: item, 
      lineStyle: { color: '#67C23A', width: 2, type: 'dashed' },
      label: { show: true, formatter: '换岗' }
    })
  })
  
  const option = {
    title: { 
      text: `${currentJob.value.jobName} - 垂直晋升+换岗路径图谱`,
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: { trigger: 'item' },
    legend: [{ data: ['垂直晋升', '换岗路径'], top: 'bottom' }],
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
          fontWeight: 'bold'
        },
        force: {
          repulsion: 2500,
          edgeLength: 200,
          gravity: 0.1
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
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f5f7fa;
  margin: 0;
  padding: 0;
}

/* ========== 导航栏样式（使用:deep()穿透scoped，保证固定定位生效） ========== */
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

:deep(.menu-item.active::after) {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: #2f54eb;
  border-radius: 3px 3px 0 0;
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

/* ========== 面包屑导航样式 ========== */
.breadcrumb {
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}
.breadcrumb span {
  cursor: pointer;
  transition: color 0.3s ease;
}
.breadcrumb span:hover {
  color: #2f54eb; /* 鼠标悬浮时变蓝色 */
}
.breadcrumb .separator {
  color: #999;
  cursor: default; /* 分隔符不可点击 */
}
.breadcrumb .current {
  color: #333;
  font-weight: 600; /* 岗位名称加粗 */
  cursor: default; /* 岗位名称不可点击 */
}

/* ========== 岗位画像内容容器样式 ========== */
.job-portrait-container {
  width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 40px; /* 顶部留出导航栏高度+20px间距，避免被遮挡 */
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* 岗位画像内容样式 */
.job-name {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.skill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-item {
  padding: 8px 12px;
  background-color: #e8f4f8;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #1989fa;
}

.cert-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.cert-item {
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #0a6ed1;
}

.path-list {
  padding: 10px 20px;
}

.path-item {
  display: flex;
  align-items: center;
  margin: 8px 0;
  font-size: 14px;
}

.step {
  display: inline-block;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  background-color: #409EFF;
  color: #fff;
  border-radius: 50%;
  margin-right: 10px;
  font-size: 12px;
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式适配 */
@media (max-width: 1200px) {
  :deep(.nav-wrap), .job-portrait-container {
    width: 95%;
    padding-left: 20px;
    padding-right: 20px;
  }
}
</style>
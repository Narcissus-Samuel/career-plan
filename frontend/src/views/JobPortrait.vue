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
            <li class="menu-item" :class="{active: $route.path === '/career-planning'}" @click="$router.push('/career-planning-intro')">职业规划</li>
            <li class="menu-item" :class="{active: $route.path === '/report-export'}" @click="$router.push('/report-export')">报告导出</li>
            <!-- <li class="menu-item" :class="{active: $route.path === '/about-us'}" @click="$router.push('/about-us')">关于我们</li>
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
              <!-- <div class="menu-item" @click="$router.push('/settings')">账号设置</div> -->
              <div class="menu-item logout" @click="handleLogout">退出登录</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  
    <!-- 岗位画像内容容器（适配固定导航栏，避免遮挡） -->
    <div class="job-portrait-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-loading-spinner></el-loading-spinner>
        <p>正在加载岗位画像数据...</p>
      </div>
      
      <!-- 内容区域（加载完成后显示） -->
      <div v-else>
        <!-- 面包屑导航 + 岗位标题区域 -->
        <div class="page-header">
          <div class="breadcrumb">
            <span class="breadcrumb-item" @click="$router.push('/')">首页</span>
            <span class="separator">/</span>
            <!-- 修复：增加空值保护 -->
            <span class="breadcrumb-item">{{ currentJob?.job_name || '岗位画像' }}</span>
            <span class="separator">/</span>
            <span class="breadcrumb-item current">岗位画像详情</span>
          </div>
          
          <!-- 岗位标题卡片 -->
          <div class="job-header-card">
            <!-- 修复：增加空值保护 -->
            <h1 class="job-title">{{ currentJob?.job_name || '岗位画像' }}</h1>
            <div class="job-tag-container">
              <el-tag 
                v-for="tag in getCoreTags()" 
                :key="tag" 
                size="medium" 
                class="job-tag"
              >{{ tag }}</el-tag>
            </div>
          </div>
        </div>
        
        <!-- 核心信息区域 - 横向滚动排列 -->
        <div class="core-info-section">
          <!-- 专业技能要求 -->
          <div class="ability-card">
            <el-card 
              header="专业技能要求" 
              shadow="hover" 
              class="info-card skills-card"
            >
              <div class="skill-grid vertical">
                <!-- 修复：增加空值保护 -->
                <div 
                  v-for="(skill, index) in (currentJob?.skills || [])" 
                  :key="skill || index" 
                  class="skill-card"
                  :style="{animationDelay: `${index * 0.1}s`}"
                >
                  <i class="el-icon-s-tools skill-icon"></i> 
                  <span class="skill-text">{{ skill }}</span>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 证书资质要求 -->
          <div class="ability-card">
            <el-card 
              header="证书资质要求" 
              shadow="hover" 
              class="info-card certs-card"
            >
              <div class="cert-grid vertical">
                <!-- 修复：增加空值保护 -->
                <div 
                  v-for="(cert, index) in (currentJob?.certificates || [])" 
                  :key="cert || index" 
                  class="cert-card"
                  :style="{animationDelay: `${index * 0.1}s`}"
                >
                  <i class="el-icon-trophy cert-icon"></i> 
                  <span class="cert-text">{{ cert }}</span>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 创新能力 -->
          <!-- 修复：增加空值保护 -->
          <div class="ability-card" v-if="currentJob?.soft_abilities?.创新能力">
            <el-card 
              header="创新能力要求" 
              shadow="hover" 
              class="info-card skills-card"
            >
              <div class="skill-grid vertical">
                <div class="skill-card">
                  <i class="el-icon-document skill-icon"></i> 
                  <span class="skill-text">{{ currentJob.soft_abilities.创新能力.description }}</span>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 学习能力 -->
          <!-- 修复：增加空值保护 -->
          <div class="ability-card" v-if="currentJob?.soft_abilities?.学习能力">
            <el-card 
              header="学习能力要求" 
              shadow="hover" 
              class="info-card skills-card"
            >
              <div class="skill-grid vertical">
                <div class="skill-card">
                  <i class="el-icon-document skill-icon"></i> 
                  <span class="skill-text">{{ currentJob.soft_abilities.学习能力.description }}</span>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 抗压能力 -->
          <!-- 修复：增加空值保护 -->
          <div class="ability-card" v-if="currentJob?.soft_abilities?.抗压能力">
            <el-card 
              header="抗压能力要求" 
              shadow="hover" 
              class="info-card skills-card"
            >
              <div class="skill-grid vertical">
                <div class="skill-card">
                  <i class="el-icon-document skill-icon"></i> 
                  <span class="skill-text">{{ currentJob.soft_abilities.抗压能力.description }}</span>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 沟通能力 -->
          <!-- 修复：增加空值保护 -->
          <div class="ability-card" v-if="currentJob?.soft_abilities?.沟通能力">
            <el-card 
              header="沟通能力要求" 
              shadow="hover" 
              class="info-card skills-card"
            >
              <div class="skill-grid vertical">
                <div class="skill-card">
                  <i class="el-icon-document skill-icon"></i> 
                  <span class="skill-text">{{ currentJob.soft_abilities.沟通能力.description }}</span>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 实践能力 -->
          <!-- 修复：增加空值保护 -->
          <div class="ability-card" v-if="currentJob?.soft_abilities?.实习能力">
            <el-card 
              header="实践能力要求" 
              shadow="hover" 
              class="info-card skills-card"
            >
              <div class="skill-grid vertical">
                <div class="skill-card">
                  <i class="el-icon-document skill-icon"></i> 
                  <span class="skill-text">{{ currentJob.soft_abilities.实习能力.description }}</span>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 其他软能力（动态展示） -->
          <div 
            class="ability-card" 
            v-for="(ability, key) in getOtherSoftAbilities()" 
            :key="key"
          >
            <el-card 
              :header="`${key}要求`" 
              shadow="hover" 
              class="info-card skills-card"
            >
              <div class="skill-grid vertical">
                <div class="skill-card">
                  <i class="el-icon-user skill-icon"></i> 
                  <span class="skill-text">{{ ability.description }}</span>
                </div>
              </div>
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
        
        <!-- 软能力雷达图区域 -->
        <div class="soft-ability-radar-section">
          <el-card 
            header="岗位软能力要求雷达图" 
            shadow="hover" 
            class="info-card radar-card"
          >
            <div ref="radarChartRef" class="radar-chart-container"></div>
          </el-card>
        </div>
        
        <!-- 岗位图谱弹窗 -->
        <el-dialog 
          v-model="graphVisible" 
          :title="`${currentJob?.job_name || '岗位'} - 职业发展路径图谱`" 
          width="90%"
          center
          class="graph-dialog"
          custom-class="custom-dialog"
          append-to-body
        >
          <div ref="graphChartRef" class="graph-chart-container"></div>
        </el-dialog>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'

// 导航栏相关状态
const router = useRouter()
const route = useRoute()
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const showDropdown = ref(false)
const searchInputRef = ref(null)
const graphChartRef = ref(null)
const radarChartRef = ref(null) // 雷达图ref
const loading = ref(true) // 加载状态

// 关键修复：定义缺失的响应式变量，初始化更完善
const currentJob = ref({
  job_name: '',
  skills: [],
  certificates: [],
  soft_abilities: {},
  coreTags: []
})
const jobGraphConfig = ref({
  vertical: [],
  switch: []
})
const graphVisible = ref(false) // 图谱弹窗可见性

// 存储echarts实例，防止内存泄漏
let graphChart = null
let radarChart = null // 雷达图实例

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

// 获取步骤颜色
const getStepColor = (index) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#722ED1', '#F7BA1E']
  return colors[index % colors.length]
}

// 获取其他软能力（排除固定展示的5个）
const getOtherSoftAbilities = () => {
  const fixedAbilities = ['创新能力', '学习能力', '抗压能力', '沟通能力', '实习能力']
  const otherAbilities = {}
  
  // 修复：增加空值保护
  const softAbilities = currentJob.value?.soft_abilities || {}
  for (const [key, value] of Object.entries(softAbilities)) {
    if (!fixedAbilities.includes(key) && value && value.description) {
      otherAbilities[key] = value
    }
  }
  
  return otherAbilities
}

// 初始化软能力雷达图
const initRadarChart = () => {
  if (!radarChartRef.value) return
  
  // 销毁已有实例防止内存泄漏
  if (radarChart) {
    radarChart.dispose()
  }
  
  radarChart = echarts.init(radarChartRef.value)
  
  // 整理雷达图数据
  // 修复：增加完整的空值保护
  const softAbilities = currentJob.value?.soft_abilities || {}
  const abilityData = [
    { 
      name: '创新能力', 
      value: softAbilities.创新能力?.score || 0 
    },
    { 
      name: '学习能力', 
      value: softAbilities.学习能力?.score || 0 
    },
    { 
      name: '抗压能力', 
      value: softAbilities.抗压能力?.score || 0 
    },
    { 
      name: '沟通能力', 
      value: softAbilities.沟通能力?.score || 0 
    },
    { 
      name: '实践能力', 
      value: softAbilities.实习能力?.score || 0 
    }
  ]
  
  // 生成自定义tooltip文本，按能力名称+分数纵向展示
  const scoreList = abilityData.map(item => `${item.name}：${item.value}分`).join('\n')
  const option = {
    backgroundColor: '#ffffff',
    title: {
      // 修复：增加空值保护
      text: `${currentJob.value?.job_name || '岗位'} 软能力要求评估`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 60,
        color: '#303133'
      }
    },
    tooltip: {
      trigger: 'item',
      // 保持纵向换行显示完整能力名称+分数列表
      formatter: (params) => {
        const data = params.data || {}
        return `
          <div style="padding: 8px; line-height: 1.8;">
            <div style="font-weight: 600; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 4px;">岗位要求</div>
            ${abilityData.map(item => `<div>${item.name}：${item.value}分</div>`).join('')}
            <div style="margin-top: 8px; font-size: 12px; color: #999;">(满分5分)</div>
          </div>
        `
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: ['岗位要求'],
      textStyle: {
        color: '#606266'
      }
    },
    radar: {
      indicator: abilityData.map(item => ({
        name: item.name,
        max: 5,
        min: 0
      })),
      shape: 'polygon',
      splitNumber: 5,
      name: {
        textStyle: {
          color: '#303133',
          fontSize: 14
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e8e8e8'
        }
      },
      splitArea: {
        areaStyle: {
          color: ['#f8f9fa', '#ffffff'],
          opacity: 0.5
        }
      },
      axisLine: {
        lineStyle: {
          color: '#dcdfe6'
        }
      }
    },
    series: [
      {
        name: '岗位要求',
        type: 'radar',
        data: [
          {
            value: abilityData.map(item => item.value),
            name: '岗位要求',
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.2)',
              opacity: 0.7
            },
            lineStyle: {
              color: '#409EFF',
              width: 2
            },
            itemStyle: {
              color: '#409EFF',
              borderColor: '#ffffff',
              borderWidth: 2
            },
            symbol: 'circle',
            symbolSize: 8
          }
        ]
      }
    ]
  }
  
  radarChart.setOption(option)
  
  // 监听窗口大小变化，自适应雷达图
  const radarResizeHandler = () => {
    radarChart.resize()
  }
  window.addEventListener('resize', radarResizeHandler)
  
  onUnmounted(() => {
    window.removeEventListener('resize', radarResizeHandler)
  })
}

// 打开图谱弹窗
const openGraphDialog = () => {
  graphVisible.value = true
  nextTick(() => {
    initJobGraph()
  })
}

// 初始化岗位发展路径图谱 - 【仅修改这里，修复ECharts报错】
const initJobGraph = () => {
  if (!graphChartRef.value) return
  
  if (graphChart) {
    graphChart.dispose()
  }
  
  graphChart = echarts.init(graphChartRef.value)
  
  const config = jobGraphConfig.value
  // 严格过滤空值、去重
  const verticalList = (config.vertical || []).filter(item => item && item.trim())
  const switchList = (config.switch || []).filter(item => item && item.trim())
  // 去重，防止节点重复
  const uniqueVertical = [...new Set(verticalList)]
  const uniqueSwitch = [...new Set(switchList)]
  
  const nodes = []
  const links = []
  const nodeMap = {} // 存储id映射，防止重复
  
  // 垂直路径节点 - 添加唯一ID，不重复
  uniqueVertical.forEach((item, index) => {
    const nodeId = `v_${index}`
    if(nodeMap[nodeId]) return
    nodeMap[nodeId] = true
    
    nodes.push({ 
      id: nodeId,
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
    // 连线使用ID关联
    if (index > 0) {
      links.push({ 
        source: `v_${index-1}`, 
        target: nodeId, 
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
  
  // 换岗路径节点 - 添加唯一ID，不重复
  uniqueSwitch.forEach((item, index) => {
    const nodeId = `s_${index}`
    if(nodeMap[nodeId]) return
    nodeMap[nodeId] = true
    
    nodes.push({ 
      id: nodeId,
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
    // 从垂直路径第3个/第1个节点连线，使用ID
    const sourceId = uniqueVertical.length >=3 ? 'v_2' : (uniqueVertical[0] ? 'v_0' : '')
    if(sourceId){
      links.push({ 
        source: sourceId, 
        target: nodeId, 
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
    }
  })

  // 终极兜底：无数据时显示默认节点
  if(nodes.length === 0){
    nodes.push({
      id: 'default',
      name: '暂无发展路径',
      category:0,
      symbolSize:60,
      itemStyle:{color:'#909399'}
    })
  }
  
  const option = {
    backgroundColor: '#ffffff',
    title: { 
      // 修复：增加空值保护
      text: `${currentJob.value?.job_name || '岗位'} - 职业发展路径图谱`,
      left: 'center',
      textStyle: { fontSize: 18, fontWeight: 60, color: '#303133' }
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

// 从后端获取岗位画像数据（完整获取大模型生成的所有数据）
const fetchJobProfile = async () => {
  try {
    loading.value = true
    // 获取路由参数（优先job_id，兼容jobName）
    const jobId = route.query.job_id
    const jobName = route.query.jobName
    
    let res
    if (jobId) {
      // 通过job_id获取画像（后端返回大模型分析的完整数据）
      res = await axios.get(`/api/jobs/${jobId}/profile`)
    } else if (jobName) {
      // 兼容旧版：通过名称获取岗位详情，再获取画像
      const jobDetail = await axios.get(`/api/jobs/profile/${jobName}`)
      if (jobDetail.data.id) {
        res = await axios.get(`/api/jobs/${jobDetail.data.id}/profile`)
      } else {
        throw new Error('未找到岗位ID')
      }
    } else {
      // 默认加载第一个岗位
      const categories = await axios.get('/api/jobs/categories')
      const firstJob = categories.data[0] || {}
      currentJob.value = {
        job_name: firstJob.name || '数据分析师',
        skills: firstJob.skills || [],
        certificates: firstJob.certificates || [],
        soft_abilities: firstJob.soft_abilities || {}, // 使用大类画像的软能力
        coreTags: firstJob.coreTags || []
      }
      loading.value = false
      await nextTick() // 等待DOM更新
      await fetchJobPaths(currentJob.value.job_name)
      initRadarChart() // 初始化雷达图
      return
    }
    
    if (res && res.data) {
      // 直接使用后端大模型生成的完整数据
      currentJob.value = {
        ...currentJob.value,
        job_name: res.data.job_name || '',
        skills: res.data.skills || [],
        certificates: res.data.certificates || [],
        soft_abilities: res.data.soft_abilities || {}, // 核心：大模型生成的软能力数据
        coreTags: res.data.coreTags || []
      }
    }
    
    // 获取发展路径
    await fetchJobPaths(currentJob.value.job_name)
    
  } catch (error) {
    console.error('获取岗位画像失败:', error)
    ElMessage.error('加载岗位画像失败，将显示默认数据')
    // 加载默认数据（模拟大模型生成的结构）
    currentJob.value = {
      job_name: '数据分析师',
      skills: ['Python', 'SQL', 'Tableau', 'Excel', '数据分析'],
      certificates: ['计算机二级', 'CDA', '英语六级'],
      soft_abilities: {
        '创新能力': {
          score: 4,
          description: '需要具备独立思考能力，能够针对业务问题提出创新性的分析方法和解决方案，优化现有分析流程。'
        },
        '学习能力': {
          score: 5,
          description: '数据领域技术迭代快，需快速学习新的分析工具和算法，掌握行业最新分析方法和思维模式。'
        },
        '抗压能力': {
          score: 3,
          description: '需应对多任务并行处理，在业务高峰期能够快速响应分析需求，保持工作效率和数据准确性。'
        },
        '沟通能力': {
          score: 4,
          description: '需要将复杂的数据分析结果转化为易懂的业务结论，与产品、运营、管理层有效沟通分析成果。'
        },
        '实习能力': {
          score: 4,
          description: '具备实际项目操作经验，能够独立完成数据分析项目，将理论知识落地到实际业务场景中。'
        }
      },
      coreTags: ['Python', 'SQL', '数据分析']
    }
    // 默认路径
    jobGraphConfig.value = {
      vertical: ['初级数据分析师', '中级数据分析师', '高级数据分析师', '数据分析主管', '数据总监', '数据VP'],
      switch: ['大数据开发工程师', '产品经理', '金融分析师', '商业分析师']
    }
  } finally {
    loading.value = false
    nextTick(() => {
      initRadarChart() // 初始化雷达图
    })
  }
}

// 获取岗位发展路径（从后端大模型生成的图谱数据）
const fetchJobPaths = async (jobName) => {
  try {
    // 获取垂直晋升路径（后端返回大模型生成的路径）
    const verticalRes = await axios.get(`/api/jobs/${encodeURIComponent(jobName)}/vertical`)
    // 获取换岗路径（后端返回大模型生成的路径）
    const lateralRes = await axios.get(`/api/jobs/${encodeURIComponent(jobName)}/lateral`)
    
    // 处理垂直路径（确保≥5个）
    let verticalPaths = verticalRes.data?.map(item => item.to_job) || []
    if (verticalPaths.length < 5) {
      // 补充默认路径
      const defaultVertical = [
        `初级${jobName}`,
        `中级${jobName}`,
        `高级${jobName}`,
        `${jobName}主管`,
        `${jobName}经理`,
        `${jobName}总监`,
        `${jobName}VP`
      ]
      verticalPaths = [...verticalPaths, ...defaultVertical].slice(0, 6)
    }
    
    // 处理换岗路径（确保≥3个）
    let switchPaths = lateralRes.data?.map(item => item.to_job) || []
    if (switchPaths.length < 3) {
      // 补充默认路径
      const defaultSwitch = [
        '产品经理',
        '大数据开发工程师',
        '商业分析师',
        '运营分析师'
      ]
      switchPaths = [...switchPaths, ...defaultSwitch].slice(0, 4)
    }
    
    jobGraphConfig.value = {
      vertical: verticalPaths,
      switch: switchPaths
    }
    
  } catch (error) {
    console.error('获取发展路径失败:', error)
    // 默认路径
    jobGraphConfig.value = {
      vertical: [
        `初级${jobName}`,
        `中级${jobName}`,
        `高级${jobName}`,
        `${jobName}主管`,
        `${jobName}经理`,
        `${jobName}总监`
      ],
      switch: [
        '产品经理',
        '大数据开发工程师',
        '金融分析师',
        '商业分析师'
      ]
    }
  }
}

// 获取核心标签
const getCoreTags = () => {
  // 从技能中提取核心标签，或使用默认值
  // 修复：增加空值保护
  const skills = currentJob.value?.skills || []
  if (skills.length > 0) {
    return skills.slice(0, 3).map(skill => {
      if (skill.includes('/')) return skill.split('/')[0]
      return skill
    })
  }
  return ['暂无标签']
}

// 监听路由参数变化加载对应岗位
watch([() => route.query.job_id, () => route.query.jobName], () => {
  fetchJobProfile()
}, { immediate: true })

// 页面挂载时初始化
onMounted(() => {
  // 初始化暗黑主题
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark')
  }
  
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
  
  // 组件卸载时清理
  onUnmounted(() => {
    document.removeEventListener('click', clickHandler)
    if (graphChart) graphChart.dispose()
    if (radarChart) radarChart.dispose() // 销毁雷达图实例
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
  background: #fafbfc;
  margin: 0;
  padding: 0;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 600px;
  color: #606266;
}

/* ========== 导航栏样式 ========== */
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

/* ========== 页面内容样式 ========== */
.job-portrait-container {
  width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 60px;
  min-height: calc(100vh - 60px);
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

/* 页面头部 - 面包屑 + 岗位标题 */
.page-header {
  padding: 24px 32px;
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

/* 通用卡片样式 */
:deep(.info-card) {
  border: none;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.info-card .el-card__header) {
  background: #f9fafc;
  border-bottom: 1px solid #f0f2f5;
  padding: 16px 20px;
  font-weight: 600;
  font-size: 16px;
  color: #1f2937;
  border-radius: 8px 8px 0 0;
}

:deep(.info-card .el-card__body) {
  padding: 20px;
  flex: 1;
}

/* 核心信息区域 - 横向排列（可滚动） */
.core-info-section {
  display: flex;
  gap: 20px;
  padding: 24px 0;
  border-bottom: 1px solid #f0f2f5;
  margin-bottom: 24px;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: thin;
  scrollbar-color: #409EFF #f0f2f5;
  padding-bottom: 10px;
}

/* 自定义滚动条 */
.core-info-section::-webkit-scrollbar {
  height: 6px;
}

.core-info-section::-webkit-scrollbar-track {
  background: #f0f2f5;
  border-radius: 3px;
}

.core-info-section::-webkit-scrollbar-thumb {
  background: #409EFF;
  border-radius: 3px;
}

.core-info-section::-webkit-scrollbar-thumb:hover {
  background: #3399ff;
}

.ability-card {
  flex: 0 0 280px;
  height: 400px;
}

/* 技能卡片样式 - 竖向排列 */
.skill-grid.vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.skill-card {
  background: linear-gradient(135deg, #e8f4f8 0%, #f0f9ff 100%);
  border-radius: 10px;
  padding: 12px 8px;
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
  flex: 1;
}

.skill-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 8px 16px rgba(64, 158, 255, 0.15);
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
}

.skill-icon {
  font-size: 20px;
  color: #409EFF;
  margin-bottom: 6px;
}

.skill-text {
  font-size: 12px;
  font-weight: 500;
  color: #1989fa;
  word-break: break-all;
  padding: 0 4px;
}

/* 证书卡片样式 - 竖向排列 */
.cert-grid.vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.cert-card {
  background: linear-gradient(135deg, #fef7fb 0%, #fef0c7 100%);
  border-radius: 10px;
  padding: 12px 8px;
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
  flex: 1;
}

.cert-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 8px 16px rgba(230, 162, 60, 0.15);
  background: linear-gradient(135deg, #fef0c7 0%, #fde68a 100%);
}

.cert-icon {
  font-size: 20px;
  color: '#E6A23C';
  margin-bottom: 6px;
}

.cert-text {
  font-size: 12px;
  font-weight: 500;
  color: #d48806;
}

/* 职业发展路径区域 */
.career-path-section {
  margin-bottom: 24px;
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
  color: '#67C23A';
  margin-bottom: 8px;
}

.switch-position {
  font-size: 14px;
  font-weight: 500;
  color: #52c41a;
}

/* 软能力雷达图区域样式 */
.soft-ability-radar-section {
  margin-bottom: 24px;
}

.radar-card {
  height: 100%;
}

.radar-chart-container {
  width: 100%;
  height: 500px;
  background: #ffffff !important;
}

/* 图谱弹窗样式 */
:deep(.custom-dialog) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

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
  
  .graph-chart-container {
    height: 500px;
  }
  
  .radar-chart-container {
    height: 400px;
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
  
  .graph-chart-container {
    height: 400px;
  }
  
  .radar-chart-container {
    height: 400px;
  }
  
  .ability-card {
    flex: 0 0 250px;
    height: 350px;
  }
}

@media (max-width: 480px) {
  .ability-card {
    flex: 0 0 220px;
    height: 300px;
  }
  
  .path-grid {
    grid-template-columns: 1fr;
  }
  
  .radar-chart-container {
    height: 300px;
  }
}
</style>
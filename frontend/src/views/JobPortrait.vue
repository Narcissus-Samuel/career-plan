<template>
  <div class="job-portrait-container">
    <el-page-header content="岗位画像管理" @back="$router.push('/')"></el-page-header>
    
    <!-- 岗位列表 -->
    <el-card header="已配置岗位画像（12个）" shadow="hover" style="margin: 20px 0;">
      <el-table :data="jobList" border size="large" style="width: 100%;">
        <el-table-column prop="jobName" label="岗位名称" min-width="150"></el-table-column>
        <el-table-column prop="skills" label="专业技能" min-width="200">
          <template #default="scope">
            <el-tag v-for="skill in scope.row.skills" :key="skill" size="small">{{ skill }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="certificates" label="证书要求" min-width="150">
          <template #default="scope">
            <el-tag v-for="cert in scope.row.certificates" :key="cert" size="small">{{ cert }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="abilities" label="综合能力" min-width="200">
          <template #default="scope">
            <div v-for="(score, key) in scope.row.abilities" :key="key">
              {{ abilityMap[key] }}：{{ score }}分
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="text" @click="viewJobGraph(scope.row)">查看发展路径</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 岗位图谱弹窗 -->
    <el-dialog v-model="graphVisible" title="岗位发展路径图谱" width="80%">
      <div id="job-graph" style="width: 100%; height: 600px;"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// 能力映射
const abilityMap = {
  innovation: '创新能力',
  learning: '学习能力',
  pressure: '抗压能力',
  communication: '沟通能力',
  internship: '实习能力'
}

// 12个岗位画像（满足≥10个要求）
const jobList = ref([
  {
    jobName: '数据分析师',
    skills: ['Python', 'SQL', 'Tableau', 'Excel'],
    certificates: ['计算机二级', 'CDA', '英语六级'],
    abilities: { innovation: 85, learning: 90, pressure: 80, communication: 85, internship: 88 }
  },
  {
    jobName: '前端开发工程师',
    skills: ['HTML/CSS', 'JavaScript', 'Vue', 'React', 'TS'],
    certificates: ['计算机二级', '软考中级'],
    abilities: { innovation: 80, learning: 95, pressure: 85, communication: 75, internship: 82 }
  },
  {
    jobName: '后端开发工程师',
    skills: ['Java', 'SpringBoot', 'MySQL', 'Redis'],
    certificates: ['计算机二级', '软考中级'],
    abilities: { innovation: 75, learning: 90, pressure: 90, communication: 70, internship: 78 }
  },
  {
    jobName: '产品经理',
    skills: ['Axure', 'PRD', '用户调研', '数据分析'],
    certificates: ['PMP', '英语六级'],
    abilities: { innovation: 90, learning: 85, pressure: 85, communication: 95, internship: 90 }
  },
  {
    jobName: '测试开发工程师',
    skills: ['Python', 'JUnit', 'Selenium', '接口测试'],
    certificates: ['计算机二级', '软件测试工程师认证'],
    abilities: { innovation: 70, learning: 85, pressure: 80, communication: 75, internship: 80 }
  },
  {
    jobName: 'UI设计师',
    skills: ['PS', 'AI', 'Figma', '交互设计'],
    certificates: ['Adobe认证', '设计类大赛证书'],
    abilities: { innovation: 95, learning: 85, pressure: 75, communication: 80, internship: 82 }
  },
  {
    jobName: '运维开发工程师',
    skills: ['Linux', 'Docker', 'K8s', 'Shell'],
    certificates: ['红帽认证', '软考中级'],
    abilities: { innovation: 75, learning: 80, pressure: 85, communication: 70, internship: 75 }
  },
  {
    jobName: '大数据开发工程师',
    skills: ['Hadoop', 'Spark', 'Hive', 'Java'],
    certificates: ['计算机二级', 'CDA高级'],
    abilities: { innovation: 80, learning: 95, pressure: 90, communication: 75, internship: 78 }
  },
  {
    jobName: '网络安全工程师',
    skills: ['渗透测试', '防火墙', '漏洞挖掘', 'Python'],
    certificates: ['CISP', 'CEH'],
    abilities: { innovation: 85, learning: 90, pressure: 85, communication: 70, internship: 75 }
  },
  {
    jobName: '电商运营',
    skills: ['淘宝运营', '数据分析', '文案写作', '直播策划'],
    certificates: ['电商运营师', '英语四级'],
    abilities: { innovation: 85, learning: 80, pressure: 80, communication: 90, internship: 92 }
  },
  {
    jobName: '人工智能工程师',
    skills: ['Python', 'TensorFlow', 'PyTorch', '机器学习'],
    certificates: ['计算机二级', 'AI工程师认证'],
    abilities: { innovation: 90, learning: 95, pressure: 90, communication: 80, internship: 75 }
  },
  {
    jobName: '金融分析师',
    skills: ['Excel', 'SQL', '金融建模', '行业分析'],
    certificates: ['CFA', 'FRM', '英语六级'],
    abilities: { innovation: 80, learning: 90, pressure: 85, communication: 85, internship: 88 }
  }
])

// 图谱弹窗控制
const graphVisible = ref(false)
const currentJob = ref({})

// 查看岗位发展路径
const viewJobGraph = (job) => {
  currentJob.value = job
  graphVisible.value = true
  // 延迟初始化图表（等待弹窗渲染）
  setTimeout(() => {
    initJobGraph()
  }, 500)
}

// 初始化岗位图谱（垂直+换岗路径）
const initJobGraph = () => {
  const chartDom = document.getElementById('job-graph')
  const myChart = echarts.init(chartDom)
  
  // 岗位路径配置（满足：5个岗位换岗路径，每个≥2条）
  const jobGraphConfig = {
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
    }
  }
  
  // 默认路径（无配置则用数据分析师）
  const config = jobGraphConfig[currentJob.value.jobName] || jobGraphConfig['数据分析师']
  
  // 图谱配置
  const nodes = []
  const links = []
  
  // 垂直路径节点
  config.vertical.forEach((item, index) => {
    nodes.push({ name: item, category: 0, symbolSize: 50 })
    if (index > 0) {
      links.push({ source: config.vertical[index-1], target: item, lineStyle: { color: '#409EFF' } })
    }
  })
  
  // 换岗路径节点
  config.switch.forEach((item, index) => {
    nodes.push({ name: item, category: 1, symbolSize: 40 })
    links.push({ source: config.vertical[2], target: item, lineStyle: { color: '#67C23A' } })
  })
  
  const option = {
    title: { text: `${currentJob.value.jobName} - 垂直晋升+换岗路径图谱` },
    tooltip: { trigger: 'item' },
    legend: [{ data: ['垂直晋升', '换岗路径'] }],
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: links,
        categories: [
          { name: '垂直晋升' },
          { name: '换岗路径' }
        ],
        roam: true,
        label: {
          show: true,
          fontSize: 14
        },
        force: {
          repulsion: 2000,
          edgeLength: 150
        }
      }
    ]
  }
  
  myChart.setOption(option)
  window.addEventListener('resize', () => myChart.resize())
}
</script>

<style scoped>
.job-portrait-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
</style>
<template>
  <div class="match-result-container">
    <!-- 页面头部 -->
    <el-page-header 
      content="人岗匹配结果" 
      @back="$router.push('/')"
      style="margin-bottom: 20px;"
    ></el-page-header>
    
    <!-- 学生信息卡片 -->
    <el-card shadow="hover" style="margin-bottom: 20px; border-radius: 10px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <div style="font-size: 18px; font-weight: bold;">
          {{ studentInfo.name }}（{{ studentInfo.major }} · {{ studentInfo.grade }}）
        </div>
        <el-tag type="info">匹配时间：{{ new Date().toLocaleString() }}</el-tag>
      </div>
      
      <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
        <div style="font-size: 14px; color: #666; margin-right: 10px;">技能：</div>
        <el-tag type="primary" v-for="skill in studentInfo.skills" :key="skill" size="medium">
          {{ skill }}
        </el-tag>
      </div>
      
      <div style="display: flex; flex-wrap: wrap; gap: 8px;">
        <div style="font-size: 14px; color: #666; margin-right: 10px;">证书：</div>
        <el-tag type="success" v-for="cert in studentInfo.certificates" :key="cert" size="medium">
          {{ cert }}
        </el-tag>
      </div>
    </el-card>

    <!-- 匹配结果榜单 -->
    <el-card 
      header="TOP5匹配岗位" 
      shadow="hover"
      style="margin-bottom: 20px; border-radius: 10px;"
    >
      <el-table 
        :data="matchList" 
        border 
        style="width: 100%;"
        size="large"
        :row-style="{ height: '60px' }"
      >
        <el-table-column 
          prop="rank" 
          label="排名" 
          width="80"
          align="center"
        ></el-table-column>
        
        <el-table-column 
          prop="jobName" 
          label="岗位名称" 
          min-width="180"
          align="center"
        ></el-table-column>
        
        <el-table-column 
          prop="matchScore" 
          label="匹配度" 
          width="200"
          align="center"
        >
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.matchScore * 100" 
              :color="getProgressColor(scope.row.matchScore)"
              :show-text="true"
              stroke-width="12"
            ></el-progress>
          </template>
        </el-table-column>
        
        <el-table-column 
          label="操作" 
          width="120"
          align="center"
        >
          <template #default="scope">
            <el-button 
              type="text" 
              @click="viewDetail(scope.row)"
              style="color: #409EFF;"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 匹配维度分析（ECharts雷达图） -->
    <el-card 
      header="匹配维度分析（TOP1岗位）" 
      shadow="hover"
      style="margin-bottom: 20px; border-radius: 10px;"
    >
      <div id="radar-chart" style="width: 100%; height: 400px;"></div>
    </el-card>

    <!-- 生成报告按钮 -->
    <el-row justify="center" style="margin-top: 20px;">
      <el-button 
        type="primary" 
        size="large" 
        icon="Document" 
        @click="$router.push('/report')"
        style="padding: 12px 60px; border-radius: 8px; font-size: 16px;"
      >
        生成职业规划报告
      </el-button>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

// 获取本地存储的学生信息（无则用默认数据）
const studentInfo = ref(JSON.parse(localStorage.getItem('studentInfo')) || {
  name: '张三',
  major: '计算机科学与技术',
  grade: '大三',
  skills: ['Python', 'SQL'],
  certificates: ['计算机二级', '英语六级'],
  internships: '某互联网公司数据实习',
  interests: ['数据分析']
})

// 模拟匹配结果数据
const matchList = reactive([
  { 
    rank: 1, 
    jobName: '数据分析师', 
    matchScore: 0.85, 
    details: { base: 0.9, skill: 0.88, quality: 0.8, potential: 0.82 } 
  },
  { 
    rank: 2, 
    jobName: '前端开发工程师', 
    matchScore: 0.72,
    details: { base: 0.8, skill: 0.75, quality: 0.7, potential: 0.68 } 
  },
  { 
    rank: 3, 
    jobName: '后端开发工程师', 
    matchScore: 0.65,
    details: { base: 0.75, skill: 0.6, quality: 0.7, potential: 0.72 } 
  },
  { 
    rank: 4, 
    jobName: '产品经理', 
    matchScore: 0.58,
    details: { base: 0.7, skill: 0.5, quality: 0.65, potential: 0.75 } 
  },
  { 
    rank: 5, 
    jobName: '测试开发工程师', 
    matchScore: 0.55,
    details: { base: 0.68, skill: 0.55, quality: 0.6, potential: 0.6 } 
  }
])

// 进度条颜色（按匹配度分色）
const getProgressColor = (score) => {
  if (score >= 0.8) return '#67C23A'  // 绿色（优秀）
  if (score >= 0.7) return '#409EFF'  // 蓝色（良好）
  if (score >= 0.6) return '#E6A23C'  // 黄色（一般）
  return '#F56C6C'                    // 红色（较差）
}

// 查看岗位详情
const viewDetail = (row) => {
  ElMessageBox.alert(
    `<div style="text-align: left; line-height: 1.8;">
      <h4 style="margin-bottom: 10px;">${row.jobName} - 匹配详情</h4>
      <p>基础要求匹配度：${(row.details.base * 100).toFixed(1)}%</p>
      <p>职业技能匹配度：${(row.details.skill * 100).toFixed(1)}%</p>
      <p>职业素养匹配度：${(row.details.quality * 100).toFixed(1)}%</p>
      <p>发展潜力匹配度：${(row.details.potential * 100).toFixed(1)}%</p>
      <p style="margin-top: 10px; color: #F56C6C;">
        提升建议：补充${row.jobName}核心技能，增加相关实习经历
      </p>
    </div>`,
    '岗位匹配详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭',
      type: 'info'
    }
  )
}

// 初始化雷达图
let radarChart = null
onMounted(() => {
  const chartDom = document.getElementById('radar-chart')
  radarChart = echarts.init(chartDom)
  
  // 雷达图配置
  const option = {
    title: { 
      text: `${matchList[0].jobName} 维度得分`,
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: { 
      trigger: 'item',
      textStyle: { fontSize: 14 }
    },
    radar: {
      indicator: [
        { name: '基础要求', max: 1 },
        { name: '职业技能', max: 1 },
        { name: '职业素养', max: 1 },
        { name: '发展潜力', max: 1 }
      ],
      radius: '70%',
      axisName: {
        fontSize: 14,
        color: '#333'
      }
    },
    series: [
      {
        name: '匹配得分',
        type: 'radar',
        data: [
          {
            value: [
              matchList[0].details.base,
              matchList[0].details.skill,
              matchList[0].details.quality,
              matchList[0].details.potential
            ],
            name: matchList[0].jobName,
            areaStyle: { color: 'rgba(64, 158, 255, 0.2)' },
            lineStyle: { color: '#409EFF', width: 2 },
            itemStyle: { color: '#409EFF' }
          }
        ]
      }
    ]
  }
  
  radarChart.setOption(option)
  
  // 自适应窗口大小
  window.addEventListener('resize', resizeChart)
})

// 窗口大小变化时重绘图表
const resizeChart = () => {
  if (radarChart) {
    radarChart.resize()
  }
}

// 组件卸载时销毁图表
onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  if (radarChart) {
    radarChart.dispose()
  }
})
</script>

<style scoped>
.match-result-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.el-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}
.el-table {
  --el-table-row-hover-bg-color: #f0f7ff;
}
</style>
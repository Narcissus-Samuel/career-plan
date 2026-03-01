<template>
  <div class="report-export">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">规划报告导出</h1>
      <p class="page-desc">根据你的职业测评和规划数据，生成并导出个性化的职业规划报告</p>
      <div class="header-actions">
        <button class="btn-template" @click="manageTemplates">📋 模板管理</button>
        <button class="btn-history" @click="showHistory = !showHistory">📜 导出记录</button>
      </div>
    </div>

    <!-- 报告类型选择 -->
    <div class="report-type-section">
      <h3 class="section-subtitle">选择报告类型</h3>
      <div class="type-cards">
        <div 
          class="type-card" 
          v-for="(item, index) in reportTypes" 
          :key="index"
          :class="{ active: item.id === activeReportId }"
          @click="selectReportType(item.id)"
        >
          <div class="card-icon" :style="{ backgroundColor: item.color }">{{ item.icon }}</div>
          <div class="card-content">
            <h4 class="card-title">{{ item.name }}</h4>
            <p class="card-desc">{{ item.description }}</p>
            <div class="card-features">
              <span class="feature-tag" v-for="tag in item.features" :key="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出配置区 -->
    <div class="export-config-section" v-if="activeReport">
      <h3 class="section-subtitle">导出配置</h3>
      <div class="config-card">
        <!-- 基础配置 -->
        <div class="config-group">
          <h4 class="config-title">基础设置</h4>
          <div class="config-items">
            <div class="config-item">
              <label class="config-label">报告名称：</label>
              <input 
                type="text" 
                class="config-input" 
                v-model="exportConfig.reportName"
                placeholder="请输入报告名称"
              >
            </div>
            <div class="config-item">
              <label class="config-label">导出格式：</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="format" 
                    value="pdf" 
                    v-model="exportConfig.format"
                  >
                  PDF（推荐）
                </label>
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="format" 
                    value="word" 
                    v-model="exportConfig.format"
                  >
                  Word
                </label>
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="format" 
                    value="excel" 
                    v-model="exportConfig.format"
                  >
                  Excel
                </label>
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="format" 
                    value="html" 
                    v-model="exportConfig.format"
                  >
                  HTML
                </label>
              </div>
            </div>
            <div class="config-item">
              <label class="config-label">报告语言：</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="language" 
                    value="zh-CN" 
                    v-model="exportConfig.language"
                  >
                  简体中文
                </label>
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="language" 
                    value="en" 
                    v-model="exportConfig.language"
                  >
                  英文
                </label>
              </div>
            </div>
            <div class="config-item">
              <label class="config-label">添加水印：</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="watermark" 
                    value="none" 
                    v-model="exportConfig.watermark"
                  >
                  无
                </label>
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="watermark" 
                    value="text" 
                    v-model="exportConfig.watermark"
                  >
                  文字水印
                </label>
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="watermark" 
                    value="logo" 
                    v-model="exportConfig.watermark"
                  >
                  Logo水印
                </label>
              </div>
              <input 
                type="text" 
                class="config-input small-input" 
                v-model="exportConfig.watermarkText"
                placeholder="请输入水印文字"
                v-if="exportConfig.watermark === 'text'"
              >
            </div>
          </div>
        </div>

        <!-- 内容配置 -->
        <div class="config-group">
          <h4 class="config-title">报告内容设置</h4>
          <div class="content-config">
            <div class="content-category" v-for="(category, index) in contentCategories" :key="index">
              <div class="category-header">
                <input 
                  type="checkbox" 
                  :id="`category-${index}`" 
                  v-model="category.checked"
                  @change="toggleCategory(category)"
                >
                <label :for="`category-${index}`" class="category-title">{{ category.name }}</label>
                <span class="category-count">({{ category.items.filter(item => item.checked).length }}/{{ category.items.length }})</span>
              </div>
              <div class="content-items" v-if="category.checked">
                <div class="content-item" v-for="(item, i) in category.items" :key="i">
                  <input 
                    type="checkbox" 
                    :id="`item-${index}-${i}`" 
                    v-model="item.checked"
                  >
                  <label :for="`item-${index}-${i}`">{{ item.name }}</label>
                  <span class="item-desc">{{ item.description }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 样式配置 -->
        <div class="config-group">
          <h4 class="config-title">样式设置</h4>
          <div class="style-config">
            <div class="config-item">
              <label class="config-label">模板风格：</label>
              <select class="config-select" v-model="exportConfig.templateStyle">
                <option value="default">默认风格</option>
                <option value="professional">专业风格</option>
                <option value="simple">简约风格</option>
                <option value="colorful">多彩风格</option>
              </select>
            </div>
            <div class="config-item">
              <label class="config-label">字体大小：</label>
              <select class="config-select" v-model="exportConfig.fontSize">
                <option value="12">12px（小号）</option>
                <option value="14">14px（默认）</option>
                <option value="16">16px（大号）</option>
                <option value="18">18px（超大号）</option>
              </select>
            </div>
            <div class="config-item">
              <label class="config-label">图表类型：</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="chartType" 
                    value="default" 
                    v-model="exportConfig.chartType"
                  >
                  默认图表
                </label>
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="chartType" 
                    value="minimalist" 
                    v-model="exportConfig.chartType"
                  >
                  极简图表
                </label>
                <label class="radio-item">
                  <input 
                    type="radio" 
                    name="chartType" 
                    value="colorful" 
                    v-model="exportConfig.chartType"
                  >
                  彩色图表
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- 导出按钮 -->
        <div class="export-actions">
          <button class="btn-preview" @click="previewReport">👁️ 预览报告</button>
          <button class="btn-export" @click="exportReport">📤 立即导出</button>
          <button class="btn-save-template" @click="saveAsTemplate">💾 保存为模板</button>
        </div>
      </div>
    </div>

    <!-- 导出记录区 -->
    <div class="export-history-section" v-if="showHistory">
      <h3 class="section-subtitle">导出记录</h3>
      <div class="history-card">
        <div class="history-filter">
          <input 
            type="text" 
            class="filter-input" 
            v-model="searchKeyword"
            placeholder="搜索报告名称..."
          >
          <select class="filter-select" v-model="filterType">
            <option value="all">所有类型</option>
            <option v-for="type in reportTypes" :key="type.id" :value="type.id">{{ type.name }}</option>
          </select>
          <select class="filter-select" v-model="filterFormat">
            <option value="all">所有格式</option>
            <option value="pdf">PDF</option>
            <option value="word">Word</option>
            <option value="excel">Excel</option>
            <option value="html">HTML</option>
          </select>
          <button class="btn-clear" @click="clearFilter">清空筛选</button>
        </div>
        <div class="history-table">
          <table>
            <thead>
              <tr>
                <th>报告名称</th>
                <th>报告类型</th>
                <th>导出格式</th>
                <th>导出时间</th>
                <th>文件大小</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in filteredHistory" :key="index">
                <td>{{ record.name }}</td>
                <td>
                  <span class="type-tag" :style="{ backgroundColor: record.typeColor }">{{ record.typeName }}</span>
                </td>
                <td>{{ record.format.toUpperCase() }}</td>
                <td>{{ record.time }}</td>
                <td>{{ record.size }}</td>
                <td class="action-buttons">
                  <button class="btn-download" @click="downloadRecord(record)">下载</button>
                  <button class="btn-delete" @click="deleteRecord(index)">删除</button>
                  <button class="btn-reexport" @click="reexportRecord(record)">重新导出</button>
                </td>
              </tr>
              <tr v-if="filteredHistory.length === 0">
                <td colspan="6" class="empty-row">暂无导出记录</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="history-pagination">
          <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">上一页</button>
          <span class="page-info">{{ currentPage }}/{{ totalPages }}页</span>
          <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">下一页</button>
        </div>
      </div>
    </div>

    <!-- 导出进度弹窗 -->
    <div class="export-modal" v-if="showExportModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>正在导出报告</h3>
          <button class="modal-close" @click="showExportModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="export-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${exportProgress}%` }"></div>
            </div>
            <span class="progress-text">{{ exportProgress }}%</span>
          </div>
          <div class="export-status">{{ exportStatus }}</div>
        </div>
        <div class="modal-footer" v-if="exportProgress === 100">
          <button class="btn-complete" @click="completeExport">完成</button>
          <button class="btn-open-file" @click="openExportedFile">打开文件</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 初始化路由实例
const router = useRouter()

// 页面核心数据
const reportTypes = ref([
  {
    id: 1,
    icon: '📊',
    name: '综合职业规划报告',
    description: '包含测评结果、能力分析、发展路径的完整报告',
    color: '#1890ff',
    features: ['完整数据', '可视化图表', '专业建议', '可打印']
  },
  {
    id: 2,
    icon: '🎯',
    name: '能力短板分析报告',
    description: '聚焦能力短板，提供详细的提升建议和学习资源',
    color: '#faad14',
    features: ['短板分析', '提升方案', '资源推荐', '进度跟踪']
  },
  {
    id: 3,
    icon: '🗺️',
    name: '发展路径规划报告',
    description: '详细的分阶段发展路径，包含里程碑和目标设置',
    color: '#52c41a',
    features: ['阶段规划', '里程碑', '进度统计', '资源匹配']
  },
  {
    id: 4,
    icon: '📈',
    name: '职业测评结果报告',
    description: '仅包含职业兴趣测评的原始数据和基础分析',
    color: '#ff7a45',
    features: ['原始数据', '基础分析', '简洁明了', '快速导出']
  }
])

// 激活的报告类型
const activeReportId = ref(1)
const activeReport = ref(reportTypes.value[0])

// 导出配置
const exportConfig = ref({
  reportName: '我的职业规划报告',
  format: 'pdf',
  language: 'zh-CN',
  watermark: 'none',
  watermarkText: '个人专属报告',
  templateStyle: 'default',
  fontSize: '14',
  chartType: 'default'
})

// 报告内容分类
const contentCategories = ref([
  {
    name: '测评基础信息',
    checked: true,
    items: [
      { name: '个人基本信息', description: '姓名、性别、学历等基础信息', checked: true },
      { name: '测评时间与环境', description: '测评完成时间、设备等信息', checked: true },
      { name: '测评有效性分析', description: '测评数据的可靠性分析', checked: false }
    ]
  },
  {
    name: '职业兴趣测评结果',
    checked: true,
    items: [
      { name: '兴趣维度得分', description: '各职业兴趣维度的具体得分', checked: true },
      { name: '兴趣雷达图', description: '可视化的兴趣维度雷达图', checked: true },
      { name: '兴趣类型解读', description: '基于得分的兴趣类型分析', checked: true },
      { name: '匹配职业推荐', description: '基于兴趣的职业匹配推荐', checked: true }
    ]
  },
  {
    name: '能力短板分析',
    checked: true,
    items: [
      { name: '能力维度得分', description: '各能力维度的具体得分', checked: true },
      { name: '短板识别结果', description: '核心短板的详细分析', checked: true },
      { name: '提升建议', description: '针对短板的具体提升建议', checked: true },
      { name: '学习资源推荐', description: '匹配短板的学习资源', checked: false }
    ]
  },
  {
    name: '发展路径规划',
    checked: true,
    items: [
      { name: '职业目标设定', description: '短期和长期职业目标', checked: true },
      { name: '分阶段规划', description: '各阶段的具体目标和任务', checked: true },
      { name: '里程碑设置', description: '关键的时间节点和成果', checked: true },
      { name: '进度跟踪图表', description: '可视化的进度跟踪图表', checked: false }
    ]
  },
  {
    name: '专业建议与总结',
    checked: true,
    items: [
      { name: '整体评估总结', description: '综合的职业发展评估', checked: true },
      { name: '个性化建议', description: '针对个人的专属发展建议', checked: true },
      { name: '风险提示', description: '职业发展中的潜在风险', checked: false },
      { name: '后续行动计划', description: '可落地的后续行动建议', checked: true }
    ]
  }
])

// 导出记录相关
const showHistory = ref(false)
const exportHistory = ref([
  {
    name: '我的职业规划报告',
    typeId: 1,
    typeName: '综合职业规划报告',
    typeColor: '#1890ff',
    format: 'pdf',
    time: '2026-02-15 14:30:25',
    size: '2.4MB'
  },
  {
    name: '能力短板分析报告',
    typeId: 2,
    typeName: '能力短板分析报告',
    typeColor: '#faad14',
    format: 'word',
    time: '2026-02-10 09:15:40',
    size: '1.8MB'
  },
  {
    name: '发展路径规划报告',
    typeId: 3,
    typeName: '发展路径规划报告',
    typeColor: '#52c41a',
    format: 'pdf',
    time: '2026-02-05 16:20:10',
    size: '3.2MB'
  },
  {
    name: '职业测评结果报告',
    typeId: 4,
    typeName: '职业测评结果报告',
    typeColor: '#ff7a45',
    format: 'excel',
    time: '2026-02-01 11:05:30',
    size: '0.8MB'
  }
])

// 筛选条件
const searchKeyword = ref('')
const filterType = ref('all')
const filterFormat = ref('all')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 导出弹窗相关
const showExportModal = ref(false)
const exportProgress = ref(0)
const exportStatus = ref('正在准备导出数据...')

// 选择报告类型
const selectReportType = (id) => {
  activeReportId.value = id
  const selectedReport = reportTypes.value.find(item => item.id === id)
  activeReport.value = selectedReport
  
  // 更新默认报告名称
  exportConfig.value.reportName = `我的${selectedReport.name}`
}

// 切换分类选中状态
const toggleCategory = (category) => {
  // 如果取消选中，取消所有子项
  if (!category.checked) {
    category.items.forEach(item => {
      item.checked = false
    })
  } else {
    // 如果选中，选中所有子项
    category.items.forEach(item => {
      item.checked = true
    })
  }
}

// 筛选后的导出记录
const filteredHistory = computed(() => {
  let filtered = exportHistory.value
  
  // 关键词筛选
  if (searchKeyword.value) {
    filtered = filtered.filter(record => 
      record.name.includes(searchKeyword.value)
    )
  }
  
  // 类型筛选
  if (filterType.value !== 'all') {
    filtered = filtered.filter(record => 
      record.typeId === Number(filterType.value)
    )
  }
  
  // 格式筛选
  if (filterFormat.value !== 'all') {
    filtered = filtered.filter(record => 
      record.format === filterFormat.value
    )
  }
  
  // 分页处理
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filtered.slice(startIndex, endIndex)
})

// 总页数
const totalPages = computed(() => {
  let filtered = exportHistory.value
  
  // 应用筛选条件计算总条数
  if (searchKeyword.value) {
    filtered = filtered.filter(record => 
      record.name.includes(searchKeyword.value)
    )
  }
  
  if (filterType.value !== 'all') {
    filtered = filtered.filter(record => 
      record.typeId === Number(filterType.value)
    )
  }
  
  if (filterFormat.value !== 'all') {
    filtered = filtered.filter(record => 
      record.format === filterFormat.value
    )
  }
  
  return Math.ceil(filtered.length / pageSize.value) || 1
})

// 清空筛选
const clearFilter = () => {
  searchKeyword.value = ''
  filterType.value = 'all'
  filterFormat.value = 'all'
  currentPage.value = 1
}

// 预览报告
const previewReport = () => {
  router.push({
    path: '/report-preview',
    query: {
      reportType: activeReportId.value,
      config: JSON.stringify(exportConfig.value),
      content: JSON.stringify(contentCategories.value)
    }
  })
}

// 导出报告
const exportReport = () => {
  // 显示导出弹窗
  showExportModal.value = true
  exportProgress.value = 0
  exportStatus.value = '正在准备导出数据...'
  
  // 模拟导出进度
  const progressInterval = setInterval(() => {
    exportProgress.value += Math.floor(Math.random() * 10) + 5
    
    if (exportProgress.value <= 30) {
      exportStatus.value = '正在整理报告数据...'
    } else if (exportProgress.value <= 60) {
      exportStatus.value = '正在生成报告内容...'
    } else if (exportProgress.value <= 90) {
      exportStatus.value = '正在转换文件格式...'
    } else if (exportProgress.value < 100) {
      exportStatus.value = '正在准备下载文件...'
    }
    
    if (exportProgress.value >= 100) {
      exportProgress.value = 100
      exportStatus.value = '报告导出完成！'
      clearInterval(progressInterval)
      
      // 添加到导出记录
      exportHistory.value.unshift({
        name: exportConfig.value.reportName,
        typeId: activeReportId.value,
        typeName: activeReport.value.name,
        typeColor: activeReport.value.color,
        format: exportConfig.value.format,
        time: new Date().toLocaleString().replace(/\//g, '-'),
        size: `${(Math.random() * 3 + 0.5).toFixed(1)}MB`
      })
    }
  }, 300)
}

// 完成导出
const completeExport = () => {
  showExportModal.value = false
}

// 打开导出文件
const openExportedFile = () => {
  alert(`已打开「${exportConfig.value.reportName}.${exportConfig.value.format}」文件！`)
  showExportModal.value = false
}

// 保存为模板
const saveAsTemplate = () => {
  const templateName = prompt('请输入模板名称：', exportConfig.value.reportName)
  if (templateName) {
    alert(`「${templateName}」模板已保存成功！`)
  }
}

// 模板管理
const manageTemplates = () => {
  router.push('/template-management')
}

// 下载记录
const downloadRecord = (record) => {
  alert(`正在下载「${record.name}.${record.format}」文件...`)
}

// 删除记录
const deleteRecord = (index) => {
  if (confirm('确定要删除这条导出记录吗？')) {
    exportHistory.value.splice(index, 1)
  }
}

// 重新导出
const reexportRecord = (record) => {
  // 恢复该记录的配置
  selectReportType(record.typeId)
  exportConfig.value.format = record.format
  exportConfig.value.reportName = record.name
  
  // 开始导出
  exportReport()
}

// 页面挂载初始化
onMounted(() => {
  selectReportType(1)
})
</script>

<style scoped>
/* 全局样式 */
.report-export {
  width: 1200px;
  margin: 0 auto;
  padding: 20px 0 50px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
}

/* 页面头部 */
.page-header {
  margin-bottom: 30px;
}
.page-title {
  font-size: 28px;
  margin: 0 0 8px 0;
  color: #2f54eb;
}
.page-desc {
  font-size: 16px;
  color: #666;
  margin: 0 0 15px 0;
}
.header-actions {
  display: flex;
  gap: 10px;
}
.btn-template, .btn-history {
  padding: 8px 15px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
.btn-template {
  background: #f5f7fa;
  color: #2f54eb;
}
.btn-history {
  background: #e6f7ff;
  color: #1890ff;
}

/* 报告类型选择区 */
.report-type-section {
  margin-bottom: 40px;
}
.section-subtitle {
  font-size: 20px;
  margin: 0 0 20px 0;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
}
.type-cards {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.type-card {
  width: calc(25% - 15px);
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}
.type-card.active {
  border-color: #2f54eb;
  box-shadow: 0 4px 12px rgba(47,84,235,0.1);
}
.type-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  margin-bottom: 15px;
}
.card-title {
  font-size: 18px;
  margin: 0 0 8px 0;
}
.card-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 10px 0;
  line-height: 1.6;
}
.card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.feature-tag {
  padding: 2px 8px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

/* 导出配置区 */
.export-config-section {
  margin-bottom: 40px;
}
.config-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
}
.config-group {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}
.config-group:last-child {
  border-bottom: none;
  margin-bottom: 20px;
  padding-bottom: 0;
}
.config-title {
  font-size: 16px;
  margin: 0 0 15px 0;
  color: #2f54eb;
}
.config-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.config-label {
  font-size: 14px;
  color: #333;
  font-weight: bold;
}
.config-input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  width: 300px;
}
.small-input {
  width: 200px;
  margin-top: 5px;
}
.config-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  width: 200px;
}
.radio-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}
.radio-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  cursor: pointer;
}

/* 内容配置 */
.content-config {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.content-category {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}
.category-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.category-title {
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
}
.category-count {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}
.content-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 25px;
}
.content-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.content-item label {
  font-size: 14px;
  color: #333;
  cursor: pointer;
}
.item-desc {
  font-size: 12px;
  color: #999;
  padding-left: 20px;
}

/* 样式配置 */
.style-config {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 导出按钮 */
.export-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}
.btn-preview, .btn-export, .btn-save-template {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
.btn-preview {
  background: #f5f7fa;
  color: #2f54eb;
}
.btn-export {
  background: #2f54eb;
  color: #fff;
}
.btn-save-template {
  background: #52c41a;
  color: #fff;
}

/* 导出记录区 */
.export-history-section {
  margin-bottom: 40px;
}
.history-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
}
.history-filter {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
}
.filter-input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  flex: 1;
  max-width: 300px;
}
.filter-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  width: 150px;
}
.btn-clear {
  padding: 8px 15px;
  background: #f5f7fa;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 历史记录表格 */
.history-table {
  overflow-x: auto;
}
.history-table table {
  width: 100%;
  border-collapse: collapse;
}
.history-table th, .history-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}
.history-table th {
  background: #f8f9fa;
  font-weight: bold;
  font-size: 14px;
}
.history-table td {
  font-size: 14px;
  color: #333;
}
.type-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
}
.action-buttons {
  display: flex;
  gap: 8px;
}
.btn-download, .btn-delete, .btn-reexport {
  padding: 4px 8px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
}
.btn-download {
  background: #e6f7ff;
  color: #1890ff;
}
.btn-delete {
  background: #fff1f0;
  color: #ff4d4f;
}
.btn-reexport {
  background: #f6ffed;
  color: #52c41a;
}
.empty-row {
  text-align: center;
  color: #999;
}

/* 分页样式 */
.history-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}
.page-btn {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
}
.page-btn:disabled {
  background: #f5f7fa;
  color: #999;
  cursor: not-allowed;
}
.page-info {
  font-size: 14px;
  color: #666;
}

/* 导出弹窗 */
.export-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  width: 500px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  font-size: 18px;
}
.modal-close {
  background: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}
.modal-body {
  padding: 20px;
}
.export-progress {
  width: 100%;
  margin-bottom: 15px;
}
.progress-bar {
  height: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #52c41a;
  border-radius: 4px;
  transition: width 0.3s;
}
.progress-text {
  display: block;
  text-align: right;
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}
.export-status {
  font-size: 14px;
  color: #333;
  text-align: center;
}
.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
  gap: 15px;
}
.btn-complete, .btn-open-file {
  padding: 8px 15px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
.btn-complete {
  background: #f5f7fa;
  color: #666;
}
.btn-open-file {
  background: #2f54eb;
  color: #fff;
}
</style>
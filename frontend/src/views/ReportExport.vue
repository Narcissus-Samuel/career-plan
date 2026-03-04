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
          :key="item.id"
          :class="{ active: item.id === activeReportId }"
          @click="selectReportType(item.id)"
        >
          <div class="card-icon" :style="{ backgroundColor: item.color }">{{ item.icon }}</div>
          <div class="card-content">
            <h4 class="card-title">{{ item.name }}</h4>
            <p class="card-desc">{{ item.description }}</p>
            <!-- features 不再显示，如果需要可自行从后端数据添加 -->
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
          <button class="btn-export" @click="exportReport" :disabled="isExporting">📤 立即导出</button>
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
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in paginatedHistory" :key="record.id">
                <td>{{ record.title }}</td>
                <td>
                  <span class="type-tag" :style="{ backgroundColor: getTypeColor(record.type) }">{{ getTypeName(record.type) }}</span>
                </td>
                <td>{{ record.format.toUpperCase() }}</td>
                <td>{{ formatDate(record.created_at) }}</td>
                <td class="action-buttons">
                  <button class="btn-download" @click="downloadReport(record.id)">下载</button>
                  <button class="btn-delete" @click="deleteRecord(record.id)">删除</button>
                  <button class="btn-reexport" @click="reexportRecord(record)">重新导出</button>
                </td>
              </tr>
              <tr v-if="historyReports.length === 0">
                <td colspan="5" class="empty-row">暂无导出记录</td>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ---------- 状态 ----------
const reportTypes = ref([])                     // 报告类型列表（从后端获取）
const activeReportId = ref(null)                 // 当前选中的报告类型ID
const activeReport = ref(null)                   // 当前选中的报告类型对象
const contentCategories = ref([])                 // 内容分类（从模板构建）
const showHistory = ref(false)                    // 是否显示历史记录
const isExporting = ref(false)                    // 导出中状态
const showExportModal = ref(false)                 // 导出进度弹窗
const exportProgress = ref(0)                      // 导出进度
const exportStatus = ref('正在准备导出数据...')      // 导出状态

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

// 历史报告列表（从后端获取）
const historyReports = ref([])

// 筛选条件
const searchKeyword = ref('')
const filterType = ref('all')
const filterFormat = ref('all')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// ---------- 工具函数 ----------
const getHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2,'0')}-${date.getDate().toString().padStart(2,'0')} ${date.getHours().toString().padStart(2,'0')}:${date.getMinutes().toString().padStart(2,'0')}`
}

// 根据类型ID获取类型名称
const getTypeName = (typeId) => {
  const type = reportTypes.value.find(t => t.id === Number(typeId))
  return type ? type.name : '未知'
}

// 根据类型ID获取颜色
const getTypeColor = (typeId) => {
  const type = reportTypes.value.find(t => t.id === Number(typeId))
  return type ? type.color : '#999'
}

// ---------- 数据获取 ----------
// 获取报告类型列表
const fetchReportTypes = async () => {
  try {
    const res = await fetch('/api/report/types')
    if (!res.ok) throw new Error('获取报告类型失败')
    const data = await res.json()
    reportTypes.value = data
    if (data.length > 0) {
      selectReportType(data[0].id)
    }
  } catch (error) {
    console.error(error)
    alert('加载报告类型失败')
  }
}

// 根据类型ID获取报告模板（内容分类）
const fetchReportTemplate = async (typeId) => {
  try {
    const res = await fetch(`/api/report/templates/${typeId}`)
    if (!res.ok) throw new Error('获取模板失败')
    const template = await res.json()
    // 将后端返回的modules转换为contentCategories格式
    // 假设template.modules = [ {key, name, default}, ... ]
    // 每个模块可以作为一个分类，其子项可以自定义或从默认配置中补充
    // 这里简单构造：每个模块作为一个分类，分类下有一个子项代表是否包含该模块
    const categories = template.modules.map(module => ({
      name: module.name,
      checked: module.default,
      items: [
        {
          name: `包含${module.name}`,
          description: '',
          checked: module.default
        }
      ]
    }))
    contentCategories.value = categories
  } catch (error) {
    console.error(error)
    contentCategories.value = []
  }
}

// 获取历史报告列表
const fetchHistory = async () => {
  try {
    const res = await fetch('/api/report/history', { headers: getHeaders() })
    if (!res.ok) throw new Error('获取历史记录失败')
    const data = await res.json()
    historyReports.value = data
  } catch (error) {
    console.error(error)
    alert('加载历史记录失败')
  }
}

// ---------- 操作 ----------
const selectReportType = (id) => {
  activeReportId.value = id
  const selected = reportTypes.value.find(t => t.id === id)
  activeReport.value = selected
  if (selected) {
    exportConfig.value.reportName = `我的${selected.name}`
    fetchReportTemplate(id)
  }
}

// 切换分类选中状态（兼容原有逻辑）
const toggleCategory = (category) => {
  if (!category.checked) {
    category.items.forEach(item => item.checked = false)
  } else {
    category.items.forEach(item => item.checked = true)
  }
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
const exportReport = async () => {
  if (!activeReportId.value) return

  isExporting.value = true
  showExportModal.value = true
  exportProgress.value = 0
  exportStatus.value = '正在生成报告...'

  try {
    // 调用生成报告接口
    const res = await fetch('/api/report/generate', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        title: exportConfig.value.reportName,
        type: activeReportId.value,
        format: exportConfig.value.format,
        modules: contentCategories.value
          .filter(c => c.checked)
          .map(c => c.name) // 简化：传递模块名称作为key
      })
    })
    if (!res.ok) throw new Error('生成报告失败')
    const data = await res.json()
    const reportId = data.id

    // 模拟进度更新
    exportProgress.value = 50
    exportStatus.value = '报告生成成功，准备下载...'

    // 触发下载
    await downloadReport(reportId)

    exportProgress.value = 100
    exportStatus.value = '导出完成！'

    // 刷新历史记录
    await fetchHistory()
  } catch (error) {
    console.error(error)
    exportStatus.value = '导出失败：' + error.message
    exportProgress.value = 0
  } finally {
    isExporting.value = false
  }
}

// 下载报告文件
const downloadReport = async (reportId) => {
  try {
    const res = await fetch(`/api/report/${reportId}/download`, {
      headers: getHeaders()
    })
    if (!res.ok) throw new Error('下载失败')

    const blob = await res.blob()
    const disposition = res.headers.get('Content-Disposition')
    let filename = `report.${exportConfig.value.format}`
    if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '')
    }

    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error(error)
    throw error
  }
}

// 完成导出
const completeExport = () => {
  showExportModal.value = false
}

// 打开导出文件（模拟）
const openExportedFile = () => {
  alert(`文件已下载到您的电脑，请查看下载文件夹。`)
  showExportModal.value = false
}

// 保存为模板（模拟）
const saveAsTemplate = () => {
  const templateName = prompt('请输入模板名称：', exportConfig.value.reportName)
  if (templateName) {
    alert(`「${templateName}」模板已保存成功！`)
  }
}

// 模板管理（模拟）
const manageTemplates = () => {
  router.push('/template-management')
}

// 删除记录
const deleteRecord = async (reportId) => {
  if (!confirm('确定要删除这条导出记录吗？')) return
  try {
    // 如果后端有删除接口，可调用；否则仅前端删除
    // 假设后端无删除接口，暂时前端删除
    const index = historyReports.value.findIndex(r => r.id === reportId)
    if (index !== -1) {
      historyReports.value.splice(index, 1)
    }
    alert('删除成功')
  } catch (error) {
    console.error(error)
    alert('删除失败')
  }
}

// 重新导出
const reexportRecord = (record) => {
  selectReportType(record.type)
  exportConfig.value.format = record.format
  exportConfig.value.reportName = record.title
  exportReport()
}

// 清空筛选
const clearFilter = () => {
  searchKeyword.value = ''
  filterType.value = 'all'
  filterFormat.value = 'all'
  currentPage.value = 1
}

// 筛选后的历史记录
const filteredHistory = computed(() => {
  let filtered = historyReports.value

  if (searchKeyword.value) {
    filtered = filtered.filter(r => r.title.includes(searchKeyword.value))
  }
  if (filterType.value !== 'all') {
    filtered = filtered.filter(r => r.type === Number(filterType.value))
  }
  if (filterFormat.value !== 'all') {
    filtered = filtered.filter(r => r.format === filterFormat.value)
  }
  return filtered
})

// 分页后的记录
const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredHistory.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredHistory.value.length / pageSize.value) || 1
})

// 当筛选条件变化时重置页码
watch([searchKeyword, filterType, filterFormat], () => {
  currentPage.value = 1
})

// 切换历史记录显示时获取数据
watch(showHistory, (newVal) => {
  if (newVal) {
    fetchHistory()
  }
})

// 初始化
onMounted(async () => {
  // 检查登录
  if (!localStorage.getItem('token')) {
    alert('请先登录')
    router.push('/login')
    return
  }
  await fetchReportTypes()
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
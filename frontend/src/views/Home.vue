<template>
  <div class="career-home">
    <!-- 1. 顶部导航（默认选中首页，新增核心功能下拉菜单） -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <!-- 首页 - 激活状态 + 跳转事件 -->
            <li class="menu-item active" @click="$router.push('/')">首页</li>
            <!-- 职业规划 - 跳转事件 -->
            <li class="menu-item" @click="$router.push('/career-planning')">职业规划</li>
            <!-- 能力测评 - 跳转事件 -->
            <li class="menu-item" @click="$router.push('/ability-assessment')">能力测评</li>
            <!-- 报告生成 - 跳转事件 -->
            <li class="menu-item" @click="$router.push('/report-generate')">报告生成</li>
            <!-- 资源库 - 跳转事件 -->
            <li class="menu-item" @click="$router.push('/resource-library')">资源库</li>
            <!-- 关于我们 - 跳转事件 -->
            <li class="menu-item" @click="$router.push('/about-us')">关于我们</li>
            <!-- 核心功能下拉菜单（原Banner区四个按钮迁移至此） -->
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
          <!-- 登录/注册按钮 - 跳转事件 -->
          <button class="btn-login" @click="$router.push('/login')">登录</button>
          <button class="btn-register" @click="$router.push('/register')">注册</button>
        </div>
      </div>
    </header>

    <!-- 2. Banner区（替换为可上传的滚动轮播图） -->
    <section class="banner-carousel">
      <div class="carousel-container" ref="carouselRef">
        <div 
          class="carousel-track" 
          :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
        >
          <div class="carousel-item" v-for="(item, index) in carouselList" :key="index">
            <img 
              :src="item.url" 
              alt="轮播图" 
              class="carousel-img"
            >
            <!-- 轮播图上保留核心文案（无按钮，按钮已迁移到导航） -->
            <div class="carousel-overlay">
              <div class="overlay-left">
                <h1 class="overlay-title">大学生智能职业规划系统</h1>
                <p class="overlay-subtitle">精准匹配职业方向 · 科学规划成长路径</p>
                <div class="overlay-tags">
                  <span class="tag">个性化分析</span>
                  <span class="tag">多维度评估</span>
                  <span class="tag">一站式规划</span>
                  <span class="tag">数据驱动</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 轮播控制按钮 -->
        <button class="carousel-btn prev-btn" @click="prevSlide">◀</button>
        <button class="carousel-btn next-btn" @click="nextSlide">▶</button>
        <!-- 轮播指示器 -->
        <div class="carousel-indicators">
          <span 
            class="indicator" 
            v-for="(item, index) in carouselList" 
            :key="index"
            :class="{ active: index === currentIndex }"
            @click="goToSlide(index)"
          ></span>
        </div>
        <!-- 图片上传按钮 -->
        <div class="upload-area">
          <label class="upload-btn">
            <input 
              type="file" 
              accept="image/*" 
              @change="handleImageUpload"
              hidden
            >
            📤 更换轮播图片
          </label>
        </div>
      </div>
    </section>

    <!-- 3. 搜索区 -->
    <section class="search-section">
      <div class="search-wrap">
        <input 
          type="text" 
          class="search-input" 
          placeholder="搜索职业方向、专业、院校、岗位类型"
          @keyup.enter="handleSearch"
        >
        <button class="search-btn" @click="handleSearch">搜索</button>
      </div>
    </section>

    <!-- 4. 核心分类入口（取消找工作/考研卡片颜色加深） -->
    <section class="category-section">
      <div class="category-wrap">
        <!-- 找工作规划 - 跳转事件 -->
        <div class="category-card" @click="$router.push('/job-planning')">
          <div class="card-icon">👨💼</div>
          <div class="card-title">找工作规划</div>
          <div class="card-desc">校招、实习、应届生求职</div>
        </div>
        <!-- 考研规划 - 跳转事件 -->
        <div class="category-card" @click="$router.push('/postgraduate-planning')">
          <div class="card-icon">🎓</div>
          <div class="card-title">考研规划</div>
          <div class="card-desc">择校、择专业、备考计划</div>
        </div>
        <!-- 留学规划 - 跳转事件 -->
        <div class="category-card" @click="$router.push('/study-abroad-planning')">
          <div class="card-icon">🌏</div>
          <div class="card-title">留学规划</div>
          <div class="card-desc">选校、文书、语言备考</div>
        </div>
        <!-- 考公规划 - 跳转事件 -->
        <div class="category-card" @click="$router.push('/civil-service-planning')">
          <div class="card-icon">💼</div>
          <div class="card-title">考公规划</div>
          <div class="card-desc">岗位筛选、备考指导</div>
        </div>
        <!-- 创业规划 - 跳转事件 -->
        <div class="category-card" @click="$router.push('/entrepreneurship-planning')">
          <div class="card-icon">📈</div>
          <div class="card-title">创业规划</div>
          <div class="card-desc">项目分析、资源对接</div>
        </div>
      </div>
    </section>

    <!-- 5. 内容筛选区 -->
    <section class="content-section">
      <div class="content-wrap">
        <div class="content-tabs">
          <!-- 职业方向 - 点击切换 + 跳转 -->
          <span class="tab-item active" @click="switchTab('direction')">职业方向(200+)</span>
          <!-- 规划模板 - 点击切换 + 跳转 -->
          <span class="tab-item" @click="switchTab('template')">规划模板(50+)</span>
          <!-- 成功案例 - 点击切换 + 跳转 -->
          <span class="tab-item" @click="switchTab('case')">成功案例(1000+) <span class="new-tag">NEW</span></span>
        </div>
        <div class="filter-section">
          <div class="filter-tabs">
            <span class="filter-tab active" @click="switchFilter('industry')">行业</span>
            <span class="filter-tab" @click="switchFilter('education')">学历要求</span>
            <span class="filter-tab" @click="switchFilter('stage')">发展阶段</span>
          </div>
          <div class="filter-tags">
            <span class="filter-tag active" @click="selectTag('all')">全部</span>
            <span class="filter-tag" @click="selectTag('internet')">互联网</span>
            <span class="filter-tag" @click="selectTag('finance')">金融</span>
            <span class="filter-tag" @click="selectTag('education')">教育</span>
            <span class="filter-tag" @click="selectTag('manufacturing')">制造业</span>
            <span class="filter-tag" @click="selectTag('medical')">医疗健康</span>
            <span class="filter-tag" @click="selectTag('civil')">公务员</span>
            <span class="filter-tag" @click="selectTag('state-own')">国企</span>
            <span class="filter-tag" @click="selectTag('foreign')">外企</span>
            <span class="filter-tag" @click="selectTag('research')">科研</span>
          </div>
          <div class="sort-section">
            <span class="sort-label">排序方式:</span>
            <select class="sort-select" @change="handleSortChange">
              <option value="match">匹配度优先</option>
              <option value="hot">热门程度</option>
            </select>
            <span class="sort-label">适用阶段:</span>
            <select class="sort-select" @change="handleStageChange">
              <option value="all">全部阶段</option>
              <option value="fresh">大一/大二</option>
              <option value="senior">大三/大四</option>
            </select>
            <label class="checkbox-label">
              <input type="checkbox" @change="handleFreeFilter"> 仅看免费内容
            </label>
          </div>
        </div>
        <div class="content-preview">
          <!-- 内容卡片 - 跳转事件 -->
          <div class="content-card" v-for="(item, i) in contentList" :key="i" @click="$router.push(`/detail/${item.id}`)">
            <div class="card-header">
              <span class="card-title">{{ item.title }}</span>
            </div>
            <div class="card-body">
              <img :src="item.imgUrl" alt="规划案例" class="card-img">
            </div>
            <div class="card-footer">
              <span class="tag">{{ item.stage }}</span>
              <span class="tag">{{ item.type }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 6. 页脚 -->
    <footer class="footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 助力大学生精准规划职业方向
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

// 初始化路由实例
const router = useRouter()

// 轮播相关数据
const carouselRef = ref(null)
const currentIndex = ref(0)
const carouselList = ref([
  { url: 'https://picsum.photos/seed/carousel1/1200/300' },
  { url: 'https://picsum.photos/seed/carousel2/1200/300' },
  { url: 'https://picsum.photos/seed/carousel3/1200/300' }
])
let carouselTimer = null

// 内容列表数据（替换原硬编码）
const contentList = ref([
  { 
    id: 1, 
    title: '互联网产品岗规划', 
    imgUrl: 'https://picsum.photos/seed/career1/300/200', 
    stage: '适配大三', 
    type: '免费' 
  },
  { 
    id: 2, 
    title: '计算机考研规划', 
    imgUrl: 'https://picsum.photos/seed/career2/300/200', 
    stage: '适配大三', 
    type: '免费' 
  },
  { 
    id: 3, 
    title: '金融行业求职规划', 
    imgUrl: 'https://picsum.photos/seed/career3/300/200', 
    stage: '适配大三', 
    type: '免费' 
  },
  { 
    id: 4, 
    title: '考公备考规划', 
    imgUrl: 'https://picsum.photos/seed/career4/300/200', 
    stage: '适配大三', 
    type: '免费' 
  }
])

// 轮播自动播放
const startCarousel = () => {
  carouselTimer = setInterval(() => {
    nextSlide()
  }, 3000)
}

// 上一张轮播图
const prevSlide = () => {
  currentIndex.value = (currentIndex.value - 1 + carouselList.value.length) % carouselList.value.length
}

// 下一张轮播图
const nextSlide = () => {
  currentIndex.value = (currentIndex.value + 1) % carouselList.value.length
}

// 跳转到指定轮播图
const goToSlide = (index) => {
  currentIndex.value = index
}

// 处理轮播图片上传
const handleImageUpload = (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    alert('请上传图片格式的文件（jpg/png）！')
    return
  }

  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    alert('图片大小不能超过5MB！')
    return
  }

  const reader = new FileReader()
  reader.onload = (event) => {
    carouselList.value.push({ url: event.target.result })
    currentIndex.value = carouselList.value.length - 1
    alert('轮播图片更新成功！')
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

// 核心功能按钮跳转逻辑
const goToFeature = (type) => {
  switch(type) {
    case '测评':
      router.push('/interest-assessment')
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
  const searchInput = document.querySelector('.search-input')
  const keyword = searchInput.value.trim()
  if (keyword) {
    // 跳转到搜索结果页
    router.push(`/search?keyword=${encodeURIComponent(keyword)}`)
  } else {
    alert('请输入搜索关键词！')
  }
}

// 切换内容标签
const switchTab = (tabType) => {
  // 实际项目中可根据tabType跳转不同页面
  switch(tabType) {
    case 'direction':
      router.push('/career-direction')
      break
    case 'template':
      router.push('/planning-template')
      break
    case 'case':
      router.push('/success-case')
      break
    default:
      break
  }
}

// 切换筛选标签
const switchFilter = (filterType) => {
  // 仅示例：实际可结合筛选条件跳转
  console.log('切换筛选类型：', filterType)
}

// 选择筛选标签
const selectTag = (tag) => {
  // 仅示例：实际可结合标签跳转筛选结果页
  console.log('选择筛选标签：', tag)
}

// 排序方式变更
const handleSortChange = (e) => {
  console.log('排序方式：', e.target.value)
}

// 适用阶段变更
const handleStageChange = (e) => {
  console.log('适用阶段：', e.target.value)
}

// 免费内容筛选
const handleFreeFilter = (e) => {
  console.log('仅看免费内容：', e.target.checked)
}

// 生命周期
onMounted(() => {
  startCarousel()
})

onUnmounted(() => {
  clearInterval(carouselTimer)
})
</script>

<style scoped>
/* 全局容器 */
.career-home {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f8f9fa;
  margin: 0;
  padding: 0;
}

/* 1. 顶部导航样式 */
.top-nav {
  height: 60px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  width: 100%;
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
  color: #2f54eb;
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
}
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
  z-index: 999;
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
}
.dropdown-item:hover {
  background: #f5f7fa;
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

.nav-right {
  display: flex;
  gap: 10px;
}
.btn-login {
  padding: 6px 15px;
  border: 1px solid #2f54eb;
  color: #2f54eb;
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

/* 2. 轮播Banner区样式 */
.banner-carousel {
  width: 100%;
  height: 280px;
  position: relative;
  overflow: hidden;
}
.carousel-container {
  width: 100%;
  height: 100%;
  position: relative;
}
.carousel-track {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease;
}
.carousel-item {
  flex: 0 0 100%;
  height: 100%;
  position: relative;
}
.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
/* 轮播图文字遮罩层 */
.carousel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 120px;
  box-sizing: border-box;
  color: #fff;
}
.overlay-left {
  text-align: center;
}
.overlay-title {
  font-size: 38px;
  font-weight: bold;
  margin: 0 0 15px 0;
}
.overlay-subtitle {
  font-size: 18px;
  margin: 0 0 20px 0;
  opacity: 0.9;
}
.overlay-tags {
  display: flex;
  gap: 10px;
  justify-content: center;
}
.overlay-tags .tag {
  background: rgba(255,255,255,0.2);
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 14px;
}
/* 轮播控制按钮 */
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.3);
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  z-index: 10;
}
.carousel-btn:hover {
  background: rgba(0,0,0,0.5);
}
.prev-btn {
  left: 20px;
}
.next-btn {
  right: 20px;
}
/* 轮播指示器 */
.carousel-indicators {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}
.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.5);
  cursor: pointer;
}
.indicator.active {
  background: #fff;
}
/* 上传按钮 */
.upload-area {
  position: absolute;
  bottom: 15px;
  right: 20px;
}
.upload-btn {
  padding: 6px 15px;
  background: rgba(255,255,255,0.8);
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.upload-btn:hover {
  background: #fff;
}

/* 3. 搜索区样式 */
.search-section {
  padding: 30px 0;
}
.search-wrap {
  width: 800px;
  margin: 0 auto;
  display: flex;
}
.search-input {
  flex: 1;
  height: 42px;
  padding: 0 15px;
  border: 1px solid #e8e8e8;
  border-radius: 4px 0 0 4px;
  outline: none;
  font-size: 14px;
}
.search-btn {
  width: 80px;
  height: 42px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

/* 4. 核心分类入口样式 */
.category-section {
  padding: 10px 0 40px;
}
.category-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
}
.category-card {
  flex: 1;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 25px 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}
.category-card:hover {
  border-color: #2f54eb;
  box-shadow: 0 4px 12px rgba(47,84,235,0.1);
}
.card-icon {
  font-size: 28px;
  margin-bottom: 12px;
}
.card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 6px;
}
.card-desc {
  font-size: 12px;
  color: #666;
}

/* 5. 内容筛选区样式 */
.content-section {
  padding-bottom: 40px;
}
.content-wrap {
  width: 1200px;
  margin: 0 auto;
}
.content-tabs {
  margin-bottom: 20px;
}
.tab-item {
  font-size: 16px;
  margin-right: 25px;
  cursor: pointer;
}
.tab-item.active {
  color: #2f54eb;
  font-weight: bold;
}
.new-tag {
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 5px;
}
.filter-section {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.filter-tabs {
  display: flex;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 10px;
  margin-bottom: 15px;
}
.filter-tab {
  padding: 5px 20px;
  cursor: pointer;
  font-size: 14px;
}
.filter-tab.active {
  color: #2f54eb;
  font-weight: bold;
  border-bottom: 2px solid #2f54eb;
}
.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}
.filter-tag {
  padding: 4px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
}
.filter-tag.active {
  background: #2f54eb;
  color: #fff;
  border-color: #2f54eb;
}
.sort-section {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
  gap: 15px;
}
.sort-label {
  margin-right: 5px;
}
.sort-select {
  height: 28px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 0 5px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.checkbox-label input {
  margin-right: 5px;
}
.content-preview {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.content-card {
  width: calc(25% - 15px);
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: box-shadow 0.3s;
}
.content-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.card-header {
  padding: 10px 15px;
  border-bottom: 1px solid #e8e8e8;
}
.card-title {
  font-size: 14px;
  font-weight: bold;
}
.card-body {
  padding: 10px;
}
.card-img {
  width: 100%;
  height: auto;
  border-radius: 4px;
}
.card-footer {
  padding: 10px 15px;
  display: flex;
  gap: 8px;
}

/* 6. 页脚样式 */
.footer {
  background: #fff;
  padding: 20px 0;
  border-top: 1px solid #e8e8e8;
  text-align: center;
  color: #666;
  font-size: 14px;
}
.footer-wrap {
  width: 1200px;
  margin: 0 auto;
}
</style>
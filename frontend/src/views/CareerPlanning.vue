<template>
  <div class="career-planning">
    <!-- 1. 页面头部（保持和首页一致的导航风格） -->
    <header class="page-header">
      <div class="header-wrap">
        <div class="page-title">
          <span class="title-icon">🎯</span>
          <h1>职业规划定制中心</h1>
        </div>
        <div class="page-nav">
          <button class="back-btn" @click="$router.push('/')">← 返回首页</button>
          <button class="save-btn" @click="savePlan">保存规划</button>
          <button class="export-btn" @click="exportPlan">导出报告</button>
        </div>
      </div>
    </header>

    <!-- 2. 规划步骤导航 -->
    <section class="step-nav">
      <div class="step-wrap">
        <div class="step-item" :class="{ active: currentStep === 1, finished: currentStep > 1 }">
          <div class="step-num">1</div>
          <div class="step-text">基础信息</div>
        </div>
        <div class="step-line"></div>
        <div class="step-item" :class="{ active: currentStep === 2, finished: currentStep > 2 }">
          <div class="step-num">2</div>
          <div class="step-text">职业兴趣</div>
        </div>
        <div class="step-line"></div>
        <div class="step-item" :class="{ active: currentStep === 3, finished: currentStep > 3 }">
          <div class="step-num">3</div>
          <div class="step-text">能力评估</div>
        </div>
        <div class="step-line"></div>
        <div class="step-item" :class="{ active: currentStep === 4, finished: currentStep > 4 }">
          <div class="step-num">4</div>
          <div class="step-text">规划生成</div>
        </div>
      </div>
    </section>

    <!-- 3. 规划表单区域（分步显示） -->
    <section class="form-section">
      <div class="form-wrap">
        <!-- 步骤1：基础信息 -->
        <div class="form-step" v-show="currentStep === 1">
          <div class="form-title">填写你的基础信息</div>
          <div class="form-content">
            <div class="form-row">
              <label class="form-label">姓名：</label>
              <input type="text" class="form-input" v-model="planInfo.name" placeholder="请输入你的姓名">
            </div>
            <div class="form-row">
              <label class="form-label">性别：</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input type="radio" v-model="planInfo.gender" value="男"> 男
                </label>
                <label class="radio-item">
                  <input type="radio" v-model="planInfo.gender" value="女"> 女
                </label>
              </div>
            </div>
            <div class="form-row">
              <label class="form-label">年级：</label>
              <select class="form-select" v-model="planInfo.grade">
                <option value="">请选择年级</option>
                <option value="大一">大一</option>
                <option value="大二">大二</option>
                <option value="大三">大三</option>
                <option value="大四">大四</option>
              </select>
            </div>
            <div class="form-row">
              <label class="form-label">专业：</label>
              <input type="text" class="form-input" v-model="planInfo.major" placeholder="请输入你的专业">
            </div>
            <div class="form-row">
              <label class="form-label">目标方向：</label>
              <select class="form-select" v-model="planInfo.target">
                <option value="">请选择职业目标</option>
                <option value="就业">就业</option>
                <option value="考研">考研</option>
                <option value="留学">留学</option>
                <option value="考公">考公</option>
                <option value="创业">创业</option>
              </select>
            </div>
          </div>
          <div class="form-btn-group">
            <button class="next-btn" @click="nextStep">下一步 →</button>
          </div>
        </div>

        <!-- 步骤2：职业兴趣 -->
        <div class="form-step" v-show="currentStep === 2">
          <div class="form-title">选择你的职业兴趣（可多选）</div>
          <div class="form-content">
            <div class="checkbox-group">
              <label class="checkbox-item" v-for="item in interestList" :key="item.id">
                <input type="checkbox" v-model="planInfo.interest" :value="item.id"> {{ item.name }}
              </label>
            </div>
            <div class="form-row">
              <label class="form-label">兴趣描述：</label>
              <textarea class="form-textarea" v-model="planInfo.interestDesc" placeholder="请补充你的兴趣相关描述（选填）"></textarea>
            </div>
          </div>
          <div class="form-btn-group">
            <button class="prev-btn" @click="prevStep">← 上一步</button>
            <button class="next-btn" @click="nextStep">下一步 →</button>
          </div>
        </div>

        <!-- 步骤3：能力评估 -->
        <div class="form-step" v-show="currentStep === 3">
          <div class="form-title">评估你的核心能力</div>
          <div class="form-content">
            <div class="form-row" v-for="item in abilityList" :key="item.id">
              <label class="form-label">{{ item.name }}：</label>
              <div class="rate-group">
                <span class="rate-item" v-for="star in 5" :key="star" 
                  :class="{ active: star <= planInfo.ability[item.code] }"
                  @click="setAbility(item.code, star)"
                >★</span>
                <span class="rate-text">{{ planInfo.ability[item.code] }}星</span>
              </div>
            </div>
            <div class="form-row">
              <label class="form-label">能力短板：</label>
              <textarea class="form-textarea" v-model="planInfo.abilityDesc" placeholder="请描述你的能力短板及提升计划"></textarea>
            </div>
          </div>
          <div class="form-btn-group">
            <button class="prev-btn" @click="prevStep">← 上一步</button>
            <button class="next-btn" @click="nextStep">下一步 →</button>
          </div>
        </div>

        <!-- 步骤4：规划生成 -->
        <div class="form-step" v-show="currentStep === 4">
          <div class="form-title">你的专属职业规划</div>
          <div class="plan-result">
            <div class="result-header">
              <h3>{{ planInfo.name }}的{{ planInfo.grade }}/{{ planInfo.major }}职业规划</h3>
              <div class="result-date">生成时间：{{ currentDate }}</div>
            </div>
            <div class="result-content">
              <div class="result-item">
                <div class="result-label">目标方向：</div>
                <div class="result-value">{{ planInfo.target || '未选择' }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">职业兴趣：</div>
                <div class="result-value">{{ selectedInterestNames.join('、') || '未选择' }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">核心能力评估：</div>
                <div class="result-value">
                  <div v-for="item in abilityList" :key="item.id">
                    {{ item.name }}：{{ planInfo.ability[item.code] }}星
                  </div>
                </div>
              </div>
              <div class="result-item">
                <div class="result-label">能力提升计划：</div>
                <div class="result-value">{{ planInfo.abilityDesc || '未填写' }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">阶段性规划：</div>
                <div class="result-value">
                  <ul class="stage-list">
                    <li v-if="planInfo.grade === '大一'">
                      <strong>大一阶段：</strong> 夯实专业基础，参加1-2个相关社团，了解行业基本情况
                    </li>
                    <li v-if="planInfo.grade === '大二'">
                      <strong>大二阶段：</strong> 考取核心证书，参与相关实习/项目，明确细分方向
                    </li>
                    <li v-if="planInfo.grade === '大三'">
                      <strong>大三阶段：</strong> 针对性提升目标方向能力，准备实习/备考/申请材料
                    </li>
                    <li v-if="planInfo.grade === '大四'">
                      <strong>大四阶段：</strong> 冲刺目标，完成求职/考研/留学/考公相关流程
                    </li>
                    <li v-else>请选择年级后查看个性化阶段性规划</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div class="form-btn-group">
            <button class="prev-btn" @click="prevStep">← 上一步</button>
            <button class="finish-btn" @click="finishPlan">完成规划</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. 推荐资源区域 -->
    <section class="resource-section" v-show="currentStep === 4">
      <div class="resource-wrap">
        <div class="resource-title">为你推荐的规划资源</div>
        <div class="resource-list">
          <div class="resource-card" v-for="(item, i) in resourceList" :key="i" @click="$router.push(`/detail/${item.id}`)">
            <div class="resource-icon">{{ item.icon }}</div>
            <div class="resource-name">{{ item.title }}</div>
            <div class="resource-desc">{{ item.description }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 5. 页脚 -->
    <footer class="page-footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 你的职业未来，我们一起规划
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 当前步骤
const currentStep = ref(1)

// 规划信息
const planInfo = ref({
  name: '',
  gender: '',
  grade: '',
  major: '',
  target: '',
  interest: [],          // 存储兴趣ID数组
  interestDesc: '',
  ability: {
    communication: 0,
    learning: 0,
    teamwork: 0,
    professional: 0,
    innovation: 0
  },
  abilityDesc: ''
})

// 兴趣列表（从后端获取）
const interestList = ref([])

// 能力列表（从后端获取）
const abilityList = ref([])

// 推荐资源列表（从后端获取）
const resourceList = ref([])

// 当前日期
const currentDate = computed(() => {
  const date = new Date()
  return `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
})

// 计算选中的兴趣名称（用于显示）
const selectedInterestNames = computed(() => {
  if (!planInfo.value.interest.length) return []
  return interestList.value
    .filter(item => planInfo.value.interest.includes(item.id))
    .map(item => item.name)
})

// 获取请求头（包含 token）
const getHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  }
}

// 加载所有初始数据
const loadData = async () => {
  try {
    const [
      interestsRes,
      dimensionsRes,
      baseRes,
      userInterestsRes,
      abilityRes,
      resourcesRes
    ] = await Promise.all([
      fetch('/api/profile/interests'),
      fetch('/api/profile/ability-dimensions'),
      fetch('/api/profile/base', { headers: getHeaders() }),
      fetch('/api/profile/user-interests', { headers: getHeaders() }),
      fetch('/api/profile/ability', { headers: getHeaders() }),
      fetch('/api/path/learning-resources')
    ])

    if (interestsRes.ok) {
      interestList.value = await interestsRes.json()
    }

    if (dimensionsRes.ok) {
      const dimensions = await dimensionsRes.json()
      abilityList.value = dimensions.map(d => ({
        id: d.id,
        name: d.name,
        code: d.code
      }))
    }

    if (baseRes.ok) {
      const data = await baseRes.json()
      if (data && Object.keys(data).length) {
        planInfo.value.name = data.name || ''
        planInfo.value.gender = data.gender || ''
        planInfo.value.grade = data.grade || ''
        planInfo.value.major = data.major || ''
        planInfo.value.target = data.target || ''
      }
    }

    if (userInterestsRes.ok) {
      const data = await userInterestsRes.json()
      if (data && data.length) {
        planInfo.value.interest = data.map(item => item.id)
        planInfo.value.interestDesc = data[0]?.description || ''
      }
    }

    if (abilityRes.ok) {
      const data = await abilityRes.json()
      if (data && data.length) {
        const abilityMap = {}
        data.forEach(item => {
          abilityMap[item.code] = item.score
        })
        planInfo.value.ability = { ...planInfo.value.ability, ...abilityMap }
        planInfo.value.abilityDesc = data[0]?.description || ''
      }
    }

    if (resourcesRes.ok) {
      resourceList.value = await resourcesRes.json()
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    alert('加载数据失败，请刷新重试')
  }
}

// 下一步
const nextStep = async () => {
  if (currentStep.value === 1) {
    if (!planInfo.value.name || !planInfo.value.grade || !planInfo.value.major) {
      alert('请填写姓名、年级、专业等必填信息！')
      return
    }
    await saveBaseInfo(false)
  }
  if (currentStep.value === 2) {
    if (planInfo.value.interest.length === 0) {
      alert('请至少选择一个职业兴趣！')
      return
    }
    await saveInterests(false)
  }
  if (currentStep.value === 3) {
    const hasAbility = Object.values(planInfo.value.ability).some(v => v > 0)
    if (!hasAbility) {
      alert('请至少评估一项核心能力！')
      return
    }
    await saveAbility(false)
  }
  
  if (currentStep.value < 4) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// 设置能力评分
const setAbility = (key, star) => {
  planInfo.value.ability[key] = star
}

// 保存基础信息
const saveBaseInfo = async (showAlert = true) => {
  try {
    const res = await fetch('/api/profile/base', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        name: planInfo.value.name,
        gender: planInfo.value.gender,
        grade: planInfo.value.grade,
        major: planInfo.value.major,
        target: planInfo.value.target
      })
    })
    if (!res.ok) throw new Error('保存基础信息失败')
    if (showAlert) alert('基础信息保存成功')
  } catch (error) {
    alert(error.message)
  }
}

// 保存兴趣
const saveInterests = async (showAlert = true) => {
  try {
    const interests = planInfo.value.interest.map(id => ({ id }))
    const res = await fetch('/api/profile/user-interests', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        interests,
        interestDesc: planInfo.value.interestDesc
      })
    })
    if (!res.ok) throw new Error('保存兴趣失败')
    if (showAlert) alert('兴趣保存成功')
  } catch (error) {
    alert(error.message)
  }
}

// 保存能力评估
const saveAbility = async (showAlert = true) => {
  try {
    const abilities = abilityList.value.map(item => ({
      code: item.code,
      score: planInfo.value.ability[item.code] || 0
    }))
    const res = await fetch('/api/profile/ability', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        abilities,
        abilityDesc: planInfo.value.abilityDesc
      })
    })
    if (!res.ok) throw new Error('保存能力评估失败')
    if (showAlert) alert('能力评估保存成功')
  } catch (error) {
    alert(error.message)
  }
}

// 保存规划（调用三个保存接口）
const savePlan = async () => {
  await saveBaseInfo(true)
  await saveInterests(true)
  await saveAbility(true)
}

// 导出报告 - 生成报告并跳转到报告页面
const exportPlan = async () => {
  await finishPlan() // 复用完成规划逻辑
}

// 完成规划 - 生成报告并跳转
const finishPlan = async () => {
  await savePlan()

  try {
    const res = await fetch('/api/report/generate', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        title: `${planInfo.value.name}的职业规划报告`,
        type: 1, // 综合职业规划报告
        format: 'html',
        modules: [] // 可根据需要传递选中的模块
      })
    })
    if (!res.ok) throw new Error('生成报告失败')
    const data = await res.json()
    const reportId = data.id
    router.push(`/report?id=${reportId}`)
  } catch (error) {
    alert('生成报告失败：' + error.message)
  }
}

// 初始化
onMounted(() => {
  if (!localStorage.getItem('token')) {
    alert('请先登录')
    router.push('/login')
    return
  }
  loadData()
})
</script>

<style scoped>
/* 全局容器 */
.career-planning {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f8f9fa;
  margin: 0;
  padding: 0;
}

/* 1. 页面头部 */
.page-header {
  height: 70px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  width: 100%;
}
.header-wrap {
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
.back-btn {
  padding: 6px 15px;
  border: 1px solid #2f54eb;
  color: #2f54eb;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.save-btn {
  padding: 6px 15px;
  border: 1px solid #52c41a;
  color: #52c41a;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.export-btn {
  padding: 6px 15px;
  border: none;
  color: #fff;
  background: #2f54eb;
  border-radius: 4px;
  cursor: pointer;
}

/* 2. 步骤导航 */
.step-nav {
  padding: 30px 0;
  background: #fff;
  margin: 20px 0;
}
.step-wrap {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
.step-num {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e8e8e8;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
  transition: all 0.3s;
}
.step-text {
  font-size: 14px;
  color: #666;
}
.step-item.active .step-num {
  background: #2f54eb;
  color: #fff;
}
.step-item.active .step-text {
  color: #2f54eb;
  font-weight: bold;
}
.step-item.finished .step-num {
  background: #52c41a;
  color: #fff;
}
.step-line {
  width: 80px;
  height: 2px;
  background: #e8e8e8;
  margin: 0 10px;
}
.step-item.finished + .step-line {
  background: #52c41a;
}

/* 3. 表单区域 */
.form-section {
  padding: 0 0 30px;
}
.form-wrap {
  width: 1200px;
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.form-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #2f54eb;
  border-left: 4px solid #2f54eb;
  padding-left: 10px;
}
.form-content {
  margin-bottom: 30px;
}
.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
.form-label {
  width: 100px;
  text-align: right;
  margin-right: 20px;
  font-size: 14px;
}
.form-input, .form-select {
  flex: 1;
  height: 36px;
  padding: 0 10px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  outline: none;
}
.form-textarea {
  flex: 1;
  min-height: 100px;
  padding: 10px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  outline: none;
  resize: vertical;
}
.radio-group {
  display: flex;
  gap: 20px;
}
.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.radio-item input {
  margin-right: 5px;
}
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  flex: 1;
}
.checkbox-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  width: calc(25% - 12px);
}
.checkbox-item input {
  margin-right: 5px;
}
.rate-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.rate-item {
  font-size: 20px;
  color: #e8e8e8;
  cursor: pointer;
}
.rate-item.active {
  color: #faad14;
}
.rate-text {
  font-size: 14px;
  color: #666;
}
.form-btn-group {
  display: flex;
  justify-content: center;
  gap: 20px;
}
.prev-btn {
  padding: 8px 20px;
  border: 1px solid #e8e8e8;
  color: #666;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.next-btn, .finish-btn {
  padding: 8px 20px;
  border: none;
  color: #fff;
  background: #2f54eb;
  border-radius: 4px;
  cursor: pointer;
}
.finish-btn {
  background: #52c41a;
}

/* 规划结果 */
.plan-result {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
}
.result-header {
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 10px;
  margin-bottom: 20px;
}
.result-header h3 {
  margin: 0 0 5px 0;
  color: #2f54eb;
}
.result-date {
  font-size: 12px;
  color: #999;
}
.result-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.result-item {
  display: flex;
}
.result-label {
  width: 120px;
  font-weight: bold;
  color: #666;
}
.result-value {
  flex: 1;
  line-height: 1.6;
}
.stage-list {
  padding-left: 20px;
  margin: 0;
}
.stage-list li {
  margin-bottom: 8px;
}

/* 4. 推荐资源 */
.resource-section {
  padding: 20px 0 40px;
}
.resource-wrap {
  width: 1200px;
  margin: 0 auto;
}
.resource-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #2f54eb;
}
.resource-list {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.resource-card {
  width: calc(20% - 16px);
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: all 0.3s;
}
.resource-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  border-color: #2f54eb;
}
.resource-icon {
  font-size: 24px;
  margin-bottom: 10px;
}
.resource-name {
  font-weight: bold;
  margin-bottom: 5px;
}
.resource-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 5. 页脚 */
.page-footer {
  background: #fff;
  padding: 20px 0;
  border-top: 1px solid #e8e8e8;
  text-align: center;
  color: #666;
  font-size: 14px;
  margin-top: 20px;
}
.footer-wrap {
  width: 1200px;
  margin: 0 auto;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .header-wrap, .step-wrap, .form-wrap, .resource-wrap, .footer-wrap {
    width: 90%;
  }
  .resource-card {
    width: calc(33.33% - 14px);
  }
}
@media (max-width: 768px) {
  .step-line {
    width: 40px;
  }
  .checkbox-item {
    width: calc(50% - 12px);
  }
  .resource-card {
    width: calc(50% - 10px);
  }
  .form-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .form-label {
    width: 100%;
    text-align: left;
    margin-bottom: 5px;
  }
}
</style>
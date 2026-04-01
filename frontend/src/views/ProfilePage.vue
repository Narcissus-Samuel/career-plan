<template>
  <div class="profile-page">
    <!-- 顶部导航（复用首页导航） -->
    <header class="top-nav">
      <div class="nav-wrap">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🎯</span>
            <span class="logo-text">大学生职业规划系统</span>
          </div>
          <ul class="nav-menu">
            <li class="menu-item" @click="$router.push('/')">首页</li>
            <li class="menu-item" @click="$router.push('/career-planning')">职业规划</li>
            <li class="menu-item" @click="$router.push('/report-export')">报告导出</li>
            <li class="menu-item" @click="$router.push('/about-us')">关于我们</li>
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
            >
            <button class="nav-search-btn" @click="handleSearch">搜索</button>
          </div>

          <button class="btn-toggle-theme" @click="toggleTheme">🌙</button>
          
          <div class="user-profile">
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

    <!-- 主要内容区 -->
    <main class="profile-main">
      <div class="profile-container">
        <!-- 左侧侧边栏 -->
        <aside class="profile-sidebar">
          <!-- 用户信息卡片 -->
          <div class="user-info-card">
            <div class="avatar-container">
              <img :src="userInfo.avatar || 'https://picsum.photos/seed/avatar/200/200'" alt="用户头像" class="user-avatar">
              <label class="avatar-upload-btn" @click="triggerAvatarUpload">
                <input type="file" accept="image/*" @change="handleAvatarUpload" hidden ref="avatarInput">
                更换头像
              </label>
            </div>
            <div class="user-basic-info">
              <h3 class="username">{{ userInfo.nickname || '未设置昵称' }}</h3>
              <p class="user-role">{{ userInfo.role || '普通用户' }}</p>
              <p class="user-status">
                <span class="status-dot"></span>
                已加入 {{ formatDate(userInfo.joinTime) }}
              </p>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <span class="stat-value">{{ userStats.assessmentCount }}</span>
                <span class="stat-label">测评次数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ userStats.planCount }}</span>
                <span class="stat-label">规划方案</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ userStats.collectionCount }}</span>
                <span class="stat-label">收藏岗位</span>
              </div>
            </div>
          </div>

          <!-- 侧边栏导航 -->
          <nav class="sidebar-nav">
            <ul class="nav-list">
              <li class="nav-item" :class="{ active: activeTab === 'basic' }" @click="switchTab('basic')">
                <span class="nav-icon">👤</span>
                <span class="nav-text">基本资料</span>
              </li>
              <li class="nav-item" :class="{ active: activeTab === 'security' }" @click="switchTab('security')">
                <span class="nav-icon">🔒</span>
                <span class="nav-text">账号安全</span>
              </li>
              <li class="nav-item" :class="{ active: activeTab === 'career' }" @click="switchTab('career')">
                <span class="nav-icon">📝</span>
                <span class="nav-text">我的职业规划</span>
              </li>
              <li class="nav-item" :class="{ active: activeTab === 'interest' }" @click="switchTab('interest')">
                <span class="nav-icon">📊</span>
                <span class="nav-text">兴趣测试报告</span>
              </li>
              <li class="nav-item" :class="{ active: activeTab === 'match' }" @click="switchTab('match')">
                <span class="nav-icon">🎯</span>
                <span class="nav-text">人岗匹配报告</span>
              </li>
              <li class="nav-item" :class="{ active: activeTab === 'history' }" @click="switchTab('history')">
                <span class="nav-icon">🕒</span>
                <span class="nav-text">浏览历史</span>
              </li>
            </ul>
          </nav>
        </aside>

        <!-- 右侧内容区 -->
        <div class="profile-content">
          <!-- 基本资料标签页 → 多用户卡片模式 -->
          <div class="tab-content" v-show="activeTab === 'basic'">
            <div class="content-header">
              <h2 class="content-title">基本资料</h2>
              <button class="edit-btn" @click="isEditingBasic = !isEditingBasic">
                {{ isEditingBasic ? '取消编辑' : '编辑资料' }}
              </button>
            </div>

            <!-- 多用户卡片列表 -->
            <div class="user-card-list">
              <div 
                class="user-summary-card" 
                v-for="item in userList" 
                :key="item.id"
                @dblclick="item.expanded = !item.expanded"
              >
                <!-- 卡片头部：姓名 + 头像 -->
                <div class="card-head">
                  <img :src="item.avatar" alt="头像" class="card-avatar">
                  <div class="card-name">{{ item.name }}</div>
                </div>

                <!-- 简要信息 -->
                <div class="card-brief">
                  <div class="brief-item">
                    <label>专业：</label>
                    <span>{{ item.education_text.split(' ')[2] || '未填写' }}</span>
                  </div>
                  <div class="brief-item">
                    <label>手机：</label>
                    <span>{{ item.phone || '未填写' }}</span>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="card-actions">
                  <button class="view-btn" @click="viewUserDetail(item)">查看详情</button>
                </div>

                <!-- 双击展开 → 完整信息（原样式） -->
                <div class="card-detail" v-show="item.expanded">
                  <div class="basic-info-card">
                    <div class="card-row">
                      <label class="card-label">姓名</label>
                      <div class="card-value">{{ item.name || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">手机号</label>
                      <div class="card-value">{{ item.phone || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">邮箱</label>
                      <div class="card-value">{{ item.email || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">教育经历</label>
                      <div class="card-value">{{ item.education_text || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">工作/实习经历</label>
                      <div class="card-value">{{ item.work_text || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">项目经历</label>
                      <div class="card-value">{{ item.project_text || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">技能与证书描述</label>
                      <div class="card-value">{{ item.skills_certs_text || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">个人总结</label>
                      <div class="card-value">{{ item.summary || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">专业技能</label>
                      <div class="card-value">{{ item.skills || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">证书资质</label>
                      <div class="card-value">{{ item.certificates || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">软能力</label>
                      <div class="card-value">{{ item.soft_abilities || '未填写' }}</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">资料完整度</label>
                      <div class="card-value">{{ item.completeness || 0 }}%</div>
                    </div>
                    <div class="card-row">
                      <label class="card-label">创建时间</label>
                      <div class="card-value">{{ formatDate(item.created_at) || '未记录' }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 账号安全标签页 -->
          <div class="tab-content" v-show="activeTab === 'security'">
            <div class="content-header">
              <h2 class="content-title">账号安全</h2>
            </div>

            <div class="security-settings">
              <!-- 绑定手机号 -->
              <div class="security-item">
                <div class="item-left">
                  <span class="item-icon">📱</span>
                  <div class="item-text">
                    <span class="item-title">绑定手机号</span>
                    <span class="item-desc">{{ userInfo.phone || '未绑定' }}</span>
                  </div>
                </div>
                <button class="operate-btn" @click="showBindPhoneModal = true">
                  {{ userInfo.phone ? '修改' : '绑定' }}
                </button>
              </div>

              <!-- 修改密码 -->
              <div class="security-item">
                <div class="item-left">
                  <span class="item-icon">🔑</span>
                  <div class="item-text">
                    <span class="item-title">修改密码</span>
                    <span class="item-desc">建议定期更换密码，保障账号安全</span>
                  </div>
                </div>
                <button class="operate-btn" @click="showChangePwdModal = true">修改</button>
              </div>
            </div>
          </div>

          <!-- 我的职业规划标签页 -->
          <div class="tab-content" v-show="activeTab === 'career'">
            <div class="content-header">
              <h2 class="content-title">我的职业规划</h2>
              <button class="create-btn" @click="$router.push('/career-planning')">
                创建新规划
              </button>
            </div>

            <div v-if="careerPlans.length === 0" class="empty-state">
              <div class="empty-icon">📄</div>
              <div class="empty-text">暂无职业规划方案</div>
              <button class="empty-btn" @click="$router.push('/career-planning')">立即创建</button>
            </div>

            <div class="career-plan-list" v-else>
              <div class="plan-card" v-for="plan in careerPlans" :key="plan.id">
                <div class="plan-header">
                  <h3 class="plan-title">{{ plan.title }}</h3>
                  <div class="plan-date">{{ formatDate(plan.createTime) }}</div>
                </div>
                <div class="plan-content">
                  <div class="plan-item">
                    <span class="item-label">目标职业：</span>
                    <span class="item-value">{{ plan.targetJob }}</span>
                  </div>
                  <div class="plan-item">
                    <span class="item-label">规划周期：</span>
                    <span class="item-value">{{ plan.cycle }}</span>
                  </div>
                  <div class="plan-item">
                    <span class="item-label">匹配度：</span>
                    <span class="item-value">{{ plan.matchRate }}%</span>
                  </div>
                </div>
                <div class="plan-actions">
                  <button class="view-btn" @click="$router.push(`/plan-detail?id=${plan.id}`)">查看详情</button>
                  <button class="edit-btn" @click="$router.push(`/edit-plan?id=${plan.id}`)">编辑</button>
                  <button class="export-btn" @click="exportPlan(plan.id)">导出报告</button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 兴趣测试报告标签页 -->
          <div class="tab-content" v-show="activeTab === 'interest'">
            <div class="content-header">
              <h2 class="content-title">兴趣测试报告</h2>
              <button class="create-btn" @click="$router.push('/interest-test')">
                前往测评
              </button>
            </div>

            <div v-if="interestReports.length === 0" class="empty-state">
              <div class="empty-icon">📊</div>
              <div class="empty-text">暂无兴趣测试报告</div>
              <button class="empty-btn" @click="$router.push('/interest-test')">立即测评</button>
            </div>

            <div class="report-list" v-else>
              <div class="report-card" v-for="item in interestReports" :key="item.id">
                <div class="report-header">
                  <h3 class="report-title">{{ item.title }}</h3>
                  <div class="report-date">{{ formatDate(item.createTime) }}</div>
                </div>
                <div class="report-content">
                  <div class="report-item">
                    <span class="item-label">测试类型：</span>
                    <span class="item-value">{{ item.type }}</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">职业倾向：</span>
                    <span class="item-value">{{ item.result }}</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">适合岗位：</span>
                    <span class="item-value">{{ item.suitableJobs }}</span>
                  </div>
                </div>
                <div class="report-actions">
                  <button class="view-btn" @click="viewReport('interest', item.id)">查看报告</button>
                  <button class="export-btn" @click="exportReport('interest', item.id)">导出报告</button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 人岗匹配结果报告标签页 -->
          <div class="tab-content" v-show="activeTab === 'match'">
            <div class="content-header">
              <h2 class="content-title">人岗匹配结果报告</h2>
              <button class="create-btn" @click="$router.push('/ability-analysis')">
                开始匹配
              </button>
            </div>

            <div v-if="matchReports.length === 0" class="empty-state">
              <div class="empty-icon">🎯</div>
              <div class="empty-text">暂无人岗匹配报告</div>
              <button class="empty-btn" @click="$router.push('/ability-analysis')">立即匹配</button>
            </div>

            <div class="report-list" v-else>
              <div class="report-card" v-for="item in matchReports" :key="item.id">
                <div class="report-header">
                  <h3 class="report-title">{{ item.title }}</h3>
                  <div class="report-date">{{ formatDate(item.createTime) }}</div>
                </div>
                <div class="report-content">
                  <div class="report-item">
                    <span class="item-label">目标岗位：</span>
                    <span class="item-value">{{ item.targetJob }}</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">匹配得分：</span>
                    <span class="item-value">{{ item.score }}分</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">匹配结果：</span>
                    <span class="item-value">{{ item.result }}</span>
                  </div>
                  <div class="report-item">
                    <span class="item-label">提升建议：</span>
                    <span class="item-value">{{ item.suggestion }}</span>
                  </div>
                </div>
                <div class="report-actions">
                  <button class="view-btn" @click="viewReport('match', item.id)">查看报告</button>
                  <button class="export-btn" @click="exportReport('match', item.id)">导出报告</button>
                </div>
              </div>
            </div>
          </div>

          <!-- 浏览历史标签页 -->
          <div class="tab-content" v-show="activeTab === 'history'">
            <div class="content-header">
              <h2 class="content-title">浏览历史</h2>
              <button class="clear-btn" @click="clearHistory">清空历史</button>
            </div>

            <div v-if="browseHistory.length === 0" class="empty-state">
              <div class="empty-icon">🕒</div>
              <div class="empty-text">暂无浏览记录</div>
            </div>

            <div class="history-list" v-else>
              <div class="history-item" v-for="item in browseHistory" :key="item.id">
                <div class="item-left">
                  <img :src="item.cover || 'https://picsum.photos/seed/history/80/80'" alt="" class="history-cover">
                </div>
                <div class="item-middle">
                  <h3 class="history-title">{{ item.title }}</h3>
                  <p class="history-desc">{{ item.desc }}</p>
                  <div class="history-time">{{ formatDate(item.browseTime) }}</div>
                </div>
                <div class="item-right">
                  <button class="view-btn" @click="viewHistory(item)">再次查看</button>
                  <button class="delete-btn" @click="removeHistory(item.id)">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 修改密码弹窗 -->
    <div class="modal-overlay" v-show="showChangePwdModal" @click="closeModal('changePwd')">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">修改密码</h3>
          <button class="close-btn" @click="closeModal('changePwd')">×</button>
        </div>
        <form class="modal-form" @submit.prevent="changePassword">
          <div class="form-row">
            <label class="form-label">原密码</label>
            <input type="password" class="form-input" v-model="pwdForm.oldPwd" placeholder="请输入原密码">
          </div>
          <div class="form-row">
            <label class="form-label">新密码</label>
            <input type="password" class="form-input" v-model="pwdForm.newPwd" placeholder="请输入新密码">
          </div>
          <div class="form-row">
            <label class="form-label">确认新密码</label>
            <input type="password" class="form-input" v-model="pwdForm.confirmPwd" placeholder="请再次输入新密码">
          </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal('changePwd')">取消</button>
            <button type="submit" class="confirm-btn">确认修改</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 绑定/修改手机号弹窗 -->
    <div class="modal-overlay" v-show="showBindPhoneModal" @click="closeModal('bindPhone')">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">{{ userInfo.phone ? '修改手机号' : '绑定手机号' }}</h3>
          <button class="close-btn" @click="closeModal('bindPhone')">×</button>
        </div>
        <form class="modal-form" @submit.prevent="bindPhone">
          <div class="form-row">
            <label class="form-label">手机号</label>
            <input type="text" class="form-input" v-model="phoneForm.phone" placeholder="请输入手机号">
          </div>
          <div class="form-row">
            <label class="form-label">验证码</label>
            <div class="code-input-wrap">
              <input type="text" class="form-input code-input" v-model="phoneForm.code" placeholder="请输入验证码">
              <button type="button" class="code-btn" @click="sendCode">{{ codeText }}</button>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal('bindPhone')">取消</button>
            <button type="submit" class="confirm-btn">确认绑定</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-wrap">
        © 2026 大学生职业规划系统 | 助力大学生精准规划职业方向
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// ✅ 第一步：先声明 userInfo（修复核心）
const userInfo = ref({
  avatar: localStorage.getItem('avatar') || 'https://picsum.photos/seed/avatar/200/200',
  nickname: localStorage.getItem('nickname') || '用户' + Math.floor(Math.random() * 10000),
  realName: '',
  gender: '保密',
  school: '',
  major: '',
  grade: '',
  phone: localStorage.getItem('phone') || '',
  email: '',
  introduction: '',
  role: '普通用户',
  joinTime: '2026-01-15',
  name: '张三',
  education_text: 'XX大学 计算机科学与技术 本科',
  work_text: 'XX科技有限公司 前端开发实习生',
  project_text: '校园招聘系统、个人简历平台',
  skills_certs_text: '英语四级、计算机二级、Vue开发认证',
  summary: '热爱前端开发，具备扎实的编程基础与项目经验',
  skills: 'HTML/CSS/JS、Vue、React、小程序',
  certificates: '英语四级、计算机二级',
  soft_abilities: '沟通能力、学习能力、团队协作',
  education_json: '',
  work_json: '',
  project_json: '',
  completeness: 85,
  created_at: '2026-01-15'
})

// ========== 基础状态管理 ==========
const isLogin = ref(!!localStorage.getItem('token'))
const userAvatar = ref(localStorage.getItem('avatar') || '')
const isUserMenuOpen = ref(false)
const darkMode = ref(localStorage.getItem('darkMode') === 'true')

// 标签页切换
const activeTab = ref('basic')
const isEditingBasic = ref(false)

// 弹窗状态
const showChangePwdModal = ref(false)
const showBindPhoneModal = ref(false)

// 绑定手机号表单
const phoneForm = ref({
  phone: userInfo.value.phone || '',
  code: ''
})

// 验证码倒计时
const codeText = ref('获取验证码')
const codeTimer = ref(null)

// ========== 多用户卡片数据 ==========
const userList = ref([
  {
    id: 1,
    name: '张三',
    avatar: 'https://picsum.photos/seed/user1/200/200',
    phone: '13800138000',
    email: 'zhangsan@xxx.com',
    education_text: 'XX大学 计算机科学与技术 本科',
    work_text: 'XX科技有限公司 前端开发实习生',
    project_text: '校园招聘系统、个人简历平台',
    skills_certs_text: '英语四级、计算机二级、Vue开发认证',
    summary: '热爱前端开发，具备扎实的编程基础与项目经验',
    skills: 'HTML/CSS/JS、Vue、React、小程序',
    certificates: '英语四级、计算机二级',
    soft_abilities: '沟通能力、学习能力、团队协作',
    completeness: 85,
    created_at: '2026-01-15',
    expanded: false
  },
  {
    id: 2,
    name: '李四',
    avatar: 'https://picsum.photos/seed/user2/200/200',
    phone: '13900139000',
    email: 'lisi@xxx.com',
    education_text: 'XX大学 软件工程 本科',
    work_text: 'XX互联网公司 后端开发实习生',
    project_text: '用户管理系统、数据统计平台',
    skills_certs_text: '英语六级、计算机二级、Java认证',
    summary: '专注后端开发，熟悉数据库与服务端技术',
    skills: 'Java、SpringBoot、MySQL、Redis',
    certificates: '英语六级、计算机二级',
    soft_abilities: '逻辑思维、问题解决、责任心',
    completeness: 90,
    created_at: '2026-02-20',
    expanded: false
  }
])

// 编辑表单
const editForm = ref({
  nickname: userInfo.value.nickname,
  realName: userInfo.value.realName,
  gender: userInfo.value.gender,
  school: userInfo.value.school,
  major: userInfo.value.major,
  grade: userInfo.value.grade,
  phone: userInfo.value.phone,
  email: userInfo.value.email,
  introduction: userInfo.value.introduction
})

// 密码修改表单
const pwdForm = ref({
  oldPwd: '',
  newPwd: '',
  confirmPwd: ''
})

// 用户统计数据
const userStats = ref({
  assessmentCount: 2,
  planCount: 1,
  collectionCount: 8
})

// 职业规划列表
const careerPlans = ref([
  { id: 1, title: '前端开发工程师职业规划', createTime: '2026-02-10', targetJob: '前端开发工程师', cycle: '3年', matchRate: 92 },
  { id: 2, title: '产品经理职业规划', createTime: '2026-01-20', targetJob: '产品经理', cycle: '2年', matchRate: 85 }
])

// 兴趣测试报告数据
const interestReports = ref([
  { id: 1, title: '霍兰德职业兴趣测试报告', createTime: '2026-03-10', type: '霍兰德测试', result: '社会型 + 企业型', suitableJobs: '产品经理、运营、人力资源' },
  { id: 2, title: 'MBTI性格测试报告', createTime: '2026-02-25', type: 'MBTI测试', result: 'INTJ 专家型', suitableJobs: '架构师、数据分析师、研发主管' }
])

// 人岗匹配报告数据
const matchReports = ref([
  { id: 1, title: '前端开发工程师-人岗匹配报告', createTime: '2026-03-15', targetJob: '前端开发工程师', score: 88, result: '高度匹配', suggestion: '加强工程化与性能优化能力' },
  { id: 2, title: 'Java开发工程师-人岗匹配报告', createTime: '2026-03-05', targetJob: 'Java开发工程师', score: 72, result: '中度匹配', suggestion: '补充微服务与分布式知识' }
])

// 浏览历史
const browseHistory = ref([
  { id: 1, title: '数据分析师岗位画像', desc: '数据分析师的岗位要求、技能要求、薪资水平等', cover: 'https://picsum.photos/seed/history1/80/80', browseTime: '2026-03-15' },
  { id: 2, title: 'Python数据分析实战教程', desc: '从入门到精通的Python数据分析教程', cover: 'https://picsum.photos/seed/history2/80/80', browseTime: '2026-03-14' }
])

// ========== 方法定义 ==========
// 查看用户详情
const viewUserDetail = (item) => {
  ElMessage.info(`查看【${item.name}】的详细资料`)
}

// 切换标签页
const switchTab = (tab) => {
  activeTab.value = tab
}

// 编辑资料相关
const cancelEdit = () => {
  isEditingBasic.value = false
  editForm.value = {
    nickname: userInfo.value.nickname,
    realName: userInfo.value.realName,
    gender: userInfo.value.gender,
    school: userInfo.value.school,
    major: userInfo.value.major,
    grade: userInfo.value.grade,
    phone: userInfo.value.phone,
    email: userInfo.value.email,
    introduction: userInfo.value.introduction
  }
}

const saveBasicInfo = () => {
  userInfo.value = { ...editForm.value, role: userInfo.value.role, joinTime: userInfo.value.joinTime }
  localStorage.setItem('nickname', editForm.value.nickname)
  isEditingBasic.value = false
  ElMessage.success('基本资料修改成功')
}

// 头像上传
const triggerAvatarUpload = () => {
  const avatarInput = document.querySelector('.avatar-upload-btn input')
  avatarInput.click()
}

const handleAvatarUpload = (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  const isImage = file.type.startsWith('image/')
  if (!isImage) { ElMessage.error('请选择图片文件'); return }
  
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) { ElMessage.error('图片大小不能超过5MB'); return }
  
  const reader = new FileReader()
  reader.onload = (event) => {
    userInfo.value.avatar = event.target.result
    localStorage.setItem('avatar', event.target.result)
    userAvatar.value = event.target.result
    ElMessage.success('头像上传成功')
  }
  reader.readAsDataURL(file)
}

// 密码修改相关
const changePassword = () => {
  if (!pwdForm.value.oldPwd) { ElMessage.warning('请输入原密码'); return }
  if (!pwdForm.value.newPwd) { ElMessage.warning('请输入新密码'); return }
  if (pwdForm.value.newPwd !== pwdForm.value.confirmPwd) { ElMessage.warning('两次输入的密码不一致'); return }
  
  showChangePwdModal.value = false
  pwdForm.value = { oldPwd: '', newPwd: '', confirmPwd: '' }
  ElMessage.success('密码修改成功，请重新登录')
}

// 绑定手机号相关
const sendCode = () => {
  if (!phoneForm.value.phone) {
    ElMessage.warning('请输入手机号')
    return
  }
  if (!/^1[3-9]\d{9}$/.test(phoneForm.value.phone)) {
    ElMessage.error('手机号格式不正确')
    return
  }
  
  // 倒计时逻辑
  let second = 60
  codeText.value = `${second}秒后重新获取`
  codeTimer.value = setInterval(() => {
    second--
    codeText.value = `${second}秒后重新获取`
    if (second <= 0) {
      clearInterval(codeTimer.value)
      codeText.value = '获取验证码'
    }
  }, 1000)
  
  ElMessage.success('验证码已发送，请注意查收')
}

const bindPhone = () => {
  if (!phoneForm.value.phone) { ElMessage.warning('请输入手机号'); return }
  if (!/^1[3-9]\d{9}$/.test(phoneForm.value.phone)) { ElMessage.error('手机号格式不正确'); return }
  if (!phoneForm.value.code) { ElMessage.warning('请输入验证码'); return }
  
  // 保存手机号
  userInfo.value.phone = phoneForm.value.phone
  localStorage.setItem('phone', phoneForm.value.phone)
  editForm.value.phone = phoneForm.value.phone
  
  showBindPhoneModal.value = false
  phoneForm.value.code = ''
  ElMessage.success(userInfo.value.phone ? '手机号修改成功' : '手机号绑定成功')
}

// 关闭弹窗
const closeModal = (type) => {
  if (type === 'changePwd') {
    showChangePwdModal.value = false
    pwdForm.value = { oldPwd: '', newPwd: '', confirmPwd: '' }
  } else if (type === 'bindPhone') {
    showBindPhoneModal.value = false
    phoneForm.value.code = ''
    if (codeTimer.value) {
      clearInterval(codeTimer.value)
      codeText.value = '获取验证码'
    }
  }
}

// 职业规划相关
const exportPlan = (id) => {
  ElMessage.success(`规划方案${id}导出成功`)
}

// 报告相关
const viewReport = (type, id) => {
  ElMessage.success(`查看${type === 'interest' ? '兴趣测试' : '人岗匹配'}报告 ${id}`)
}

const exportReport = (type, id) => {
  ElMessage.success(`${type === 'interest' ? '兴趣测试' : '人岗匹配'}报告 ${id} 导出成功`)
}

// 历史记录相关
const clearHistory = () => {
  browseHistory.value = []
  ElMessage.success('浏览历史已清空')
}
const viewHistory = (item) => {
  ElMessage.info('正在打开历史记录')
}
const removeHistory = (id) => {
  browseHistory.value = browseHistory.value.filter(item => item.id !== id)
  ElMessage.success('删除成功')
}

// 通用方法
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

// 主题切换
const applyTheme = () => {
  if (darkMode.value) document.body.classList.add('dark')
  else document.body.classList.remove('dark')
}
const toggleTheme = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  applyTheme()
  ElMessage.success(`已切换为${darkMode.value ? '暗黑' : '明亮'}模式`)
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('avatar')
  localStorage.removeItem('nickname')
  localStorage.removeItem('phone')
  isLogin.value = false
  isUserMenuOpen.value = false
  router.push('/')
  ElMessage.success('退出登录成功')
}

// 切换用户菜单
const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

// 导航到功能页面
const goToFeature = (type) => {
  switch(type) {
    case '测评': router.push('/interest-test'); break
    case '分析': router.push('/ability-analysis'); break
    case '规划': router.push('/development-path'); break
    case '导出': router.push('/report-export'); break
    default: break
  }
}

// 搜索处理
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

// 生命周期
onMounted(() => {
  applyTheme()
  if (!isLogin.value) {
    router.push('/login')
    ElMessage.warning('请先登录')
  }
})
</script>

<style scoped>
/* 全局样式 */
.profile-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background: #f8f9fa;
  margin: 0;
  padding: 60px 0 0 0;
}

/* 复用首页导航样式 */
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
.menu-item.active {
  color: #000;
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

/* 主要内容区 */
.profile-main {
  width: 100%;
  padding: 30px 0;
}
.profile-container {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
}

/* 左侧侧边栏 */
.profile-sidebar {
  width: 260px;
  flex-shrink: 0;
}

/* 用户信息卡片 */
.user-info-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
}
.avatar-container {
  position: relative;
  display: inline-block;
  margin-bottom: 15px;
}
.user-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f5f5f5;
}
.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #2f54eb;
  color: #fff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}
.user-basic-info {
  margin-bottom: 20px;
}
.username {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 5px 0;
}
.user-role {
  color: #999;
  font-size: 14px;
  margin: 0 0 5px 0;
}
.user-status {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #52c41a;
  margin-right: 5px;
}
.user-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}
.stat-item {
  text-align: center;
}
.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #2f54eb;
  margin-bottom: 4px;
}
.stat-label {
  font-size: 12px;
  color: #999;
}

/* 侧边栏导航 */
.sidebar-nav {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.nav-list {
  list-style: none;
  margin: 0;
  padding: 10px 0;
}
.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
}
.nav-item:hover {
  background: #f5f7fa;
}
.nav-item.active {
  background: #e6f7ff;
  color: #2f54eb;
  font-weight: 500;
}
.nav-icon {
  font-size: 16px;
  margin-right: 10px;
}
.nav-text {
  flex: 1;
}

/* 右侧内容区 */
.profile-content {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 20px;
}

/* 内容头部 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}
.content-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}
.edit-btn, .create-btn {
  padding: 6px 15px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.clear-btn {
  padding: 6px 15px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 筛选控件 */
.filter-controls {
  display: flex;
  gap: 10px;
}
.filter-btn {
  padding: 6px 12px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.filter-btn.active {
  background: #2f54eb;
  color: #fff;
  border-color: #2f54eb;
}

/* ========== 新增：多用户卡片样式 ========== */
.user-card-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 用户简要卡片 */
.user-summary-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8e8e8;
  cursor: pointer;
  transition: all 0.2s;
}
.user-summary-card:hover {
  border-color: #2f54eb;
  background: #f5f7ff;
}

/* 卡片头部 */
.card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.card-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
}
.card-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

/* 简要信息 */
.card-brief {
  margin-bottom: 15px;
}
.brief-item {
  display: flex;
  margin-bottom: 6px;
  font-size: 14px;
}
.brief-item label {
  width: 50px;
  color: #666;
  font-weight: 500;
}
.brief-item span {
  color: #333;
}

/* 卡片按钮 */
.card-actions {
  margin-bottom: 15px;
}
.view-btn {
  padding: 6px 15px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 双击展开的详情（完全沿用你原来的样式） */
.card-detail {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #eee;
}

/* ========== 原有基础信息卡片样式（完全保留） ========== */
.basic-info-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 24px;
  border: 1px solid #e8e8e8;
}
.card-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #eee;
}
.card-row:last-child {
  margin-bottom: 0;
  border-bottom: none;
}
.card-label {
  width: 140px;
  flex-shrink: 0;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
.card-value {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

/* 表单样式 */
.basic-info-form {
  width: 100%;
}
.form-row {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}
.form-label {
  width: 120px;
  flex-shrink: 0;
  font-size: 14px;
  color: #666;
  padding-top: 6px;
}
.form-input, .form-select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}
.form-input:disabled, .form-select:disabled {
  background: #f5f5f5;
  color: #999;
}
.form-textarea {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  resize: vertical;
}
.form-textarea:disabled {
  background: #f5f5f5;
  color: #999;
}

/* 单选框组 */
.radio-group {
  flex: 1;
  display: flex;
  gap: 20px;
  padding-top: 6px;
}
.radio-group.disabled {
  color: #999;
}
.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.radio-item input {
  margin-right: 5px;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-start;
  margin-left: 120px;
  gap: 15px;
}
.cancel-btn {
  padding: 8px 20px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.save-btn {
  padding: 8px 20px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 账号安全设置 */
.security-settings {
  width: 100%;
}
.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}
.security-item:last-child {
  border-bottom: none;
}
.item-left {
  display: flex;
  align-items: center;
  gap: 15px;
}
.item-icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}
.item-text {
  display: flex;
  flex-direction: column;
}
.item-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}
.item-desc {
  font-size: 12px;
  color: #999;
}
.item-desc.unbound {
  color: #ff4d4f;
}
.operate-btn {
  padding: 6px 15px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 验证码输入框样式 */
.code-input-wrap {
  display: flex;
  gap: 10px;
  flex: 1;
}
.code-input {
  flex: 1;
}
.code-btn {
  width: 120px;
  padding: 0 10px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}

/* 职业规划列表 */
.career-plan-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.plan-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8e8e8;
}
.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
}
.plan-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}
.plan-date {
  font-size: 12px;
  color: #999;
}
.plan-content {
  margin-bottom: 15px;
}
.plan-item {
  display: flex;
  margin-bottom: 8px;
}
.item-label {
  width: 80px;
  flex-shrink: 0;
  color: #666;
  font-size: 14px;
}
.item-value {
  flex: 1;
  font-size: 14px;
}
.plan-actions {
  display: flex;
  gap: 10px;
}
.plan-actions .view-btn {
  padding: 6px 12px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.plan-actions .edit-btn {
  padding: 6px 12px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.plan-actions .export-btn {
  padding: 6px 12px;
  background: #52c41a;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

/* 报告列表样式 */
.report-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.report-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8e8e8;
}
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
}
.report-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}
.report-date {
  font-size: 12px;
  color: #999;
}
.report-content {
  margin-bottom: 15px;
}
.report-item {
  display: flex;
  margin-bottom: 8px;
}
.report-actions {
  display: flex;
  gap: 10px;
}
.report-actions .view-btn {
  padding: 6px 12px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.report-actions .export-btn {
  padding: 6px 12px;
  background: #52c41a;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

/* 浏览历史列表 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.history-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}
.item-left {
  width: 60px;
  flex-shrink: 0;
}
.history-cover {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}
.item-middle {
  flex: 1;
  padding: 0 15px;
}
.history-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}
.history-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.history-time {
  font-size: 12px;
  color: #999;
}
.item-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.item-right .view-btn {
  padding: 6px 12px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.item-right .delete-btn {
  padding: 6px 12px;
  background: #fff;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #999;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #ccc;
}
.empty-text {
  font-size: 16px;
  margin-bottom: 8px;
}
.empty-desc {
  font-size: 14px;
}
.empty-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal-content {
  width: 400px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  padding: 20px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}
.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}
.modal-form {
  width: 100%;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
}
.confirm-btn {
  padding: 8px 20px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.cancel-btn {
  padding: 8px 20px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 页脚样式 */
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
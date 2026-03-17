import { createRouter, createWebHistory } from 'vue-router'
import html2pdf from 'html2pdf.js'
import { ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
// 导入所有页面组件
import Home from '../views/Home.vue'
import StudentAbility from '../views/StudentAbility.vue'
import MatchResult from '../views/MatchResult.vue'
import Report from '../views/Report.vue'
import JobPortrait from '../views/JobPortrait.vue'
// 新增：导入登录、注册组件
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
// 新增：导入个人中心组件（核心添加）
import ProfilePage from '../views/ProfilePage.vue'

// 新增：导入其他功能页面组件（未创建的组件先用Home占位）
import CareerPlanning from '../views/CareerPlanning.vue'
import AbilityAssessment from '../views/AbilityAssessment.vue'
import ReportGenerate from '../views/ReportGenerate.vue'
import ResourceLibrary from '../views/ResourceLibrary.vue'
import AboutUs from '../views/AboutUs.vue'
import CareerInterestTest from '../views/CareerInterestTest.vue'
import ResumeUpload from '../views/ResumeUpload.vue'
// 新增：导入岗位详情组件
import JobDetail from '../views/JobDetail.vue'

const PostgraduatePlanning = () => import('../views/Home.vue') // 临时占位
const StudyAbroadPlanning = () => import('../views/Home.vue') // 临时占位
const CivilServicePlanning = () => import('../views/Home.vue') // 临时占位
const EntrepreneurshipPlanning = () => import('../views/Home.vue') // 临时占位
const InterestAssessment = () => import('../views/Home.vue') // 临时占位
import AbilityAnalysis from '../views/AbilityAnalysis.vue'
import DevelopmentPath from '../views/DevelopmentPath.vue'
import ReportExport from '../views/ReportExport.vue'
const Search = () => import('../views/Home.vue') // 临时占位
// 移除原有Detail占位，改用JobDetail

const routes = [
  { 
    path: '/', 
    name: 'Home',
    component: Home 
  },
  // 新增：登录页路由
  { 
    path: '/login', 
    name: 'Login',
    component: Login 
  },
  {
    path: '/admin-login',
    name: 'AdminLogin',
    component: AdminLogin
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard
  },
  // 新增：注册页路由
  { 
    path: '/register', 
    name: 'Register',
    component: Register 
  },
  // 新增：个人中心路由（核心添加）
  { 
    path: '/profile', 
    name: 'ProfilePage',
    component: ProfilePage,
    // 可选：添加路由元信息，标记需要登录才能访问
    meta: { 
      requireAuth: true 
    }
  },
  // 原有功能页面路由
  {
     path: '/student-ability', 
     name: 'StudentAbility', 
     component: StudentAbility 
  },
  { 
    path: '/match-result', 
    name: 'MatchResult',
    component: MatchResult 
  },
  { 
    path: '/report', 
    name: 'Report',
    component: Report 
  },
  { 
    path: '/job-portrait', 
    name: 'JobPortrait',
    component: JobPortrait 
  },
  // 新增：岗位详情页路由（核心修改）
  { 
    path: '/job-detail', 
    name: 'JobDetail',
    component: JobDetail,
    // 接收URL参数
    props: (route) => ({ 
      id: route.query.id 
    })
  },
  // 新增：顶部导航菜单路由
  { 
    path: '/career-planning', 
    name: 'CareerPlanning',
    component: CareerPlanning 
  },
  { path: '/resume-upload', component: ResumeUpload },
  { 
    path: '/ability-assessment', 
    name: 'AbilityAssessment',
    component: AbilityAssessment 
  },
  { 
    path: '/report-generate', 
    name: 'ReportGenerate',
    component: ReportGenerate 
  },
  { 
    path: '/resource-library', 
    name: 'ResourceLibrary',
    component: ResourceLibrary 
  },
  { 
    path: '/about-us', 
    name: 'AboutUs',
    component: AboutUs 
  },
  {
    path: '/interest-test',
    name: 'CareerInterestTest',
    component:CareerInterestTest
  },
  // 新增：核心分类入口路由
  // { 
  //   path: '/job-planning', 
  //   name: 'JobPlanning',
  //   component: JobPlanning 
  // },
  { 
    path: '/postgraduate-planning', 
    name: 'PostgraduatePlanning',
    component: PostgraduatePlanning 
  },
  { 
    path: '/study-abroad-planning', 
    name: 'StudyAbroadPlanning',
    component: StudyAbroadPlanning 
  },
  { 
    path: '/civil-service-planning', 
    name: 'CivilServicePlanning',
    component: CivilServicePlanning 
  },
  { 
    path: '/entrepreneurship-planning', 
    name: 'EntrepreneurshipPlanning',
    component: EntrepreneurshipPlanning 
  },
  // 新增：核心功能下拉菜单路由
  { 
    path: '/interest-assessment', 
    name: 'InterestAssessment',
    component: InterestAssessment 
  },
  { 
    path: '/ability-analysis', 
    name: 'AbilityAnalysis',
    component: AbilityAnalysis 
  },
  { 
    path: '/development-path', 
    name: 'DevelopmentPath',
    component: DevelopmentPath 
  },
  { 
    path: '/report-export', 
    name: 'ReportExport',
    component: ReportExport 
  },
  // 新增：搜索和详情页路由
  { 
    path: '/search', 
    name: 'Search',
    component: Search 
  },
  // 保留原有detail路由作为兼容（可选）
  { 
    path: '/detail/:id', 
    name: 'Detail',
    component: JobDetail,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 可选：添加路由守卫（如需登录后才能访问其他页面，可取消注释）
router.beforeEach((to, from, next) => {
  // 排除登录、注册、首页（可根据需求调整）
  const whiteList = ['/login', '/register', '/', '/job-detail']
  // 从localStorage获取token（登录成功后存储）
  const hasToken = localStorage.getItem('token')
  
  // 如果路由需要认证且不在白名单，检查token
  if (to.meta.requireAuth && !whiteList.includes(to.path)) {
    hasToken ? next() : next('/login')
  } else {
    next()
  }
})

export default router
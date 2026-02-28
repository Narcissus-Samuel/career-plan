import { createRouter, createWebHistory } from 'vue-router'
// 导入所有页面组件
import Home from '../views/Home.vue'
import StudentInfo from '../views/StudentInfo.vue'
import MatchResult from '../views/MatchResult.vue'
import Report from '../views/Report.vue'
import JobPortrait from '../views/JobPortrait.vue'

const routes = [
  { 
    path: '/', 
    name: 'Home',
    component: Home 
  },
  { 
    path: '/student-info', 
    name: 'StudentInfo',
    component: StudentInfo 
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
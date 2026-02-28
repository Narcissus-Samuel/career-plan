<template>
  <div class="login-page">
    <!-- 顶部logo栏 -->
    <header class="login-header">
      <div class="logo">
        <span class="logo-icon">🎯</span>
        <span class="logo-text">大学生职业规划系统</span>
      </div>
    </header>

    <!-- 登录表单区 -->
    <main class="login-main">
      <div class="login-card">
        <div class="login-title">用户登录</div>
        <form class="login-form" @submit.prevent="handleLogin">
          <!-- 账号输入框 -->
          <div class="form-item">
            <label class="form-label">账号</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="loginForm.username" 
              placeholder="请输入手机号/用户名"
              :class="{ error: formError.username }"
            >
            <span class="error-tip" v-if="formError.username">{{ formError.username }}</span>
          </div>

          <!-- 密码输入框 -->
          <div class="form-item">
            <label class="form-label">密码</label>
            <input 
              type="password" 
              class="form-input" 
              v-model="loginForm.password" 
              placeholder="请输入密码"
              :class="{ error: formError.password }"
            >
            <span class="error-tip" v-if="formError.password">{{ formError.password }}</span>
          </div>

          <!-- 记住密码 & 忘记密码 -->
          <div class="form-extra">
            <label class="checkbox-label">
              <input type="checkbox" v-model="loginForm.remember"> 记住密码
            </label>
            <a href="#" class="forgot-pwd">忘记密码？</a>
          </div>

          <!-- 登录按钮 -->
          <button type="submit" class="login-btn" :disabled="isLoading">
            <span v-if="!isLoading">登录</span>
            <span v-if="isLoading">登录中...</span>
          </button>

          <!-- 注册入口 -->
          <div class="register-link">
            还没有账号？<a href="/register" class="link-text">立即注册</a>
          </div>
        </form>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="login-footer">
      © 2026 大学生职业规划系统 | 助力大学生精准规划职业方向
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 登录表单数据
const loginForm = ref({
  username: '',
  password: '',
  remember: false
})

// 表单错误提示
const formError = ref({
  username: '',
  password: ''
})

// 加载状态
const isLoading = ref(false)

// 表单验证
const validateForm = () => {
  let isValid = true
  formError.value = {}

  // 验证账号
  if (!loginForm.value.username.trim()) {
    formError.value.username = '请输入账号'
    isValid = false
  }

  // 验证密码
  if (!loginForm.value.password.trim()) {
    formError.value.password = '请输入密码'
    isValid = false
  } else if (loginForm.value.password.length < 6) {
    formError.value.password = '密码长度不能少于6位'
    isValid = false
  }

  return isValid
}

// 处理登录逻辑
const handleLogin = async () => {
  // 表单验证
  if (!validateForm()) return

  try {
    isLoading.value = true
    // 模拟接口请求（实际项目替换为真实接口）
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 登录成功逻辑
    alert('登录成功！')
    // 存储token（示例）
    localStorage.setItem('token', 'mock-token-' + Date.now())
    // 跳转到首页
    router.push('/')
  } catch (error) {
    alert('登录失败：账号或密码错误')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 全局样式 */
.login-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
}

/* 顶部logo */
.login-header {
  height: 80px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  padding: 0 40px;
}
.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  color: #2f54eb;
}
.logo-icon {
  font-size: 28px;
  margin-right: 10px;
}

/* 登录主体区 */
.login-main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}
.login-card {
  width: 400px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  padding: 30px;
}
.login-title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 25px;
  color: #333;
}

/* 表单样式 */
.login-form {
  width: 100%;
}
.form-item {
  margin-bottom: 20px;
}
.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}
.form-input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  outline: none;
}
.form-input.error {
  border-color: #ff4d4f;
}
.form-input:focus {
  border-color: #2f54eb;
}
.error-tip {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #ff4d4f;
}

/* 表单额外选项 */
.form-extra {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  font-size: 14px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #666;
}
.checkbox-label input {
  margin-right: 6px;
}
.forgot-pwd {
  color: #2f54eb;
  text-decoration: none;
}
.forgot-pwd:hover {
  text-decoration: underline;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 44px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}
.login-btn:disabled {
  background: #85a5ff;
  cursor: not-allowed;
}
.login-btn:hover:not(:disabled) {
  background: #1d39c4;
}

/* 注册链接 */
.register-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}
.link-text {
  color: #2f54eb;
  text-decoration: none;
}
.link-text:hover {
  text-decoration: underline;
}

/* 页脚 */
.login-footer {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 12px;
  color: #999;
  border-top: 1px solid #e8e8e8;
}
</style>
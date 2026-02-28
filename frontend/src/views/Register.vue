<template>
  <div class="register-page">
    <!-- 顶部logo栏 -->
    <header class="register-header">
      <div class="logo">
        <span class="logo-icon">🎯</span>
        <span class="logo-text">大学生职业规划系统</span>
      </div>
    </header>

    <!-- 注册表单区 -->
    <main class="register-main">
      <div class="register-card">
        <div class="register-title">用户注册</div>
        <form class="register-form" @submit.prevent="handleRegister">
          <!-- 用户名输入框 -->
          <div class="form-item">
            <label class="form-label">用户名</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="registerForm.username" 
              placeholder="请输入用户名（2-10位）"
              :class="{ error: formError.username }"
            >
            <span class="error-tip" v-if="formError.username">{{ formError.username }}</span>
          </div>

          <!-- 手机号输入框 -->
          <div class="form-item">
            <label class="form-label">手机号</label>
            <input 
              type="tel" 
              class="form-input" 
              v-model="registerForm.phone" 
              placeholder="请输入手机号"
              :class="{ error: formError.phone }"
            >
            <span class="error-tip" v-if="formError.phone">{{ formError.phone }}</span>
          </div>

          <!-- 验证码输入框 -->
          <div class="form-item code-item">
            <div class="code-input-wrap">
              <label class="form-label">验证码</label>
              <input 
                type="text" 
                class="form-input" 
                v-model="registerForm.code" 
                placeholder="请输入验证码"
                :class="{ error: formError.code }"
              >
              <span class="error-tip" v-if="formError.code">{{ formError.code }}</span>
            </div>
            <button 
              type="button" 
              class="get-code-btn" 
              @click="getVerifyCode"
              :disabled="codeCountdown > 0"
            >
              {{ codeCountdown > 0 ? `${codeCountdown}s后重新获取` : '获取验证码' }}
            </button>
          </div>

          <!-- 密码输入框 -->
          <div class="form-item">
            <label class="form-label">设置密码</label>
            <input 
              type="password" 
              class="form-input" 
              v-model="registerForm.password" 
              placeholder="请设置6-16位密码"
              :class="{ error: formError.password }"
            >
            <span class="error-tip" v-if="formError.password">{{ formError.password }}</span>
          </div>

          <!-- 确认密码输入框 -->
          <div class="form-item">
            <label class="form-label">确认密码</label>
            <input 
              type="password" 
              class="form-input" 
              v-model="registerForm.confirmPwd" 
              placeholder="请再次输入密码"
              :class="{ error: formError.confirmPwd }"
            >
            <span class="error-tip" v-if="formError.confirmPwd">{{ formError.confirmPwd }}</span>
          </div>

          <!-- 注册协议 -->
          <div class="form-agreement">
            <label class="checkbox-label">
              <input type="checkbox" v-model="registerForm.agreement"> 
              我已阅读并同意<a href="#" class="agreement-link">《用户注册协议》</a>
            </label>
            <span class="error-tip" v-if="formError.agreement">{{ formError.agreement }}</span>
          </div>

          <!-- 注册按钮 -->
          <button type="submit" class="register-btn" :disabled="isLoading">
            <span v-if="!isLoading">注册</span>
            <span v-if="isLoading">注册中...</span>
          </button>

          <!-- 登录入口 -->
          <div class="login-link">
            已有账号？<a href="/login" class="link-text">立即登录</a>
          </div>
        </form>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="register-footer">
      © 2026 大学生职业规划系统 | 助力大学生精准规划职业方向
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 注册表单数据
const registerForm = ref({
  username: '',
  phone: '',
  code: '',
  password: '',
  confirmPwd: '',
  agreement: false
})

// 表单错误提示
const formError = ref({})

// 加载状态
const isLoading = ref(false)

// 验证码倒计时
const codeCountdown = ref(0)
let countdownTimer = null

// 表单验证
const validateForm = () => {
  let isValid = true
  formError.value = {}
  const regPhone = /^1[3-9]\d{9}$/

  // 验证用户名
  if (!registerForm.value.username.trim()) {
    formError.value.username = '请输入用户名'
    isValid = false
  } else if (registerForm.value.username.length < 2 || registerForm.value.username.length > 10) {
    formError.value.username = '用户名长度需在2-10位之间'
    isValid = false
  }

  // 验证手机号
  if (!registerForm.value.phone.trim()) {
    formError.value.phone = '请输入手机号'
    isValid = false
  } else if (!regPhone.test(registerForm.value.phone)) {
    formError.value.phone = '请输入正确的手机号'
    isValid = false
  }

  // 验证验证码
  if (!registerForm.value.code.trim()) {
    formError.value.code = '请输入验证码'
    isValid = false
  } else if (registerForm.value.code.length !== 6) {
    formError.value.code = '验证码为6位数字'
    isValid = false
  }

  // 验证密码
  if (!registerForm.value.password.trim()) {
    formError.value.password = '请设置密码'
    isValid = false
  } else if (registerForm.value.password.length < 6 || registerForm.value.password.length > 16) {
    formError.value.password = '密码长度需在6-16位之间'
    isValid = false
  }

  // 验证确认密码
  if (!registerForm.value.confirmPwd.trim()) {
    formError.value.confirmPwd = '请再次输入密码'
    isValid = false
  } else if (registerForm.value.confirmPwd !== registerForm.value.password) {
    formError.value.confirmPwd = '两次输入的密码不一致'
    isValid = false
  }

  // 验证协议
  if (!registerForm.value.agreement) {
    formError.value.agreement = '请阅读并同意用户注册协议'
    isValid = false
  }

  return isValid
}

// 获取验证码
const getVerifyCode = async () => {
  // 先验证手机号
  if (!registerForm.value.phone.trim()) {
    formError.value.phone = '请输入手机号'
    return
  }
  const regPhone = /^1[3-9]\d{9}$/
  if (!regPhone.test(registerForm.value.phone)) {
    formError.value.phone = '请输入正确的手机号'
    return
  }

  try {
    // 向后端请求发送验证码
    const res = await fetch('/api/send_code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: registerForm.value.phone })
    })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.error || '发送验证码失败')
    }
    alert(`验证码已发送至手机号 ${registerForm.value.phone}，模拟码：${data.code}`)
  } catch (err) {
    alert(err.message)
  }

  // 开始倒计时
  codeCountdown.value = 60
  countdownTimer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) {
      clearInterval(countdownTimer)
    }
  }, 1000)
}

// 处理注册逻辑
const handleRegister = async () => {
  // 表单验证
  if (!validateForm()) return

  try {
    isLoading.value = true
    // 调用后端注册接口
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: registerForm.value.username,
        phone: registerForm.value.phone,
        password: registerForm.value.password,
        code: registerForm.value.code
      })
    })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.error || '注册失败')
    }

    // 注册成功逻辑
    alert('注册成功！即将跳转到登录页')
    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    alert('注册失败：' + error.message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 全局样式 */
.register-page {
  width: 100%;
  min-height: 100vh;
  font-family: "Microsoft Yahei", sans-serif;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
}

/* 顶部logo */
.register-header {
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

/* 注册主体区 */
.register-main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}
.register-card {
  width: 450px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  padding: 30px;
}
.register-title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 25px;
  color: #333;
}

/* 表单样式 */
.register-form {
  width: 100%;
}
.form-item {
  margin-bottom: 20px;
}
.code-item {
  display: flex;
  gap: 10px;
}
.code-input-wrap {
  flex: 1;
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

/* 验证码按钮 */
.get-code-btn {
  width: 120px;
  height: 40px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  margin-top: 24px;
}
.get-code-btn:disabled {
  background: #85a5ff;
  cursor: not-allowed;
}

/* 注册协议 */
.form-agreement {
  margin-bottom: 25px;
  font-size: 12px;
}
.checkbox-label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  color: #666;
}
.checkbox-label input {
  margin-right: 6px;
  margin-top: 2px;
}
.agreement-link {
  color: #2f54eb;
  text-decoration: none;
}
.agreement-link:hover {
  text-decoration: underline;
}

/* 注册按钮 */
.register-btn {
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
.register-btn:disabled {
  background: #85a5ff;
  cursor: not-allowed;
}
.register-btn:hover:not(:disabled) {
  background: #1d39c4;
}

/* 登录链接 */
.login-link {
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
.register-footer {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 12px;
  color: #999;
  border-top: 1px solid #e8e8e8;
}
</style>
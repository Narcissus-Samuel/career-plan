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
            <li class="menu-item" @click="$router.push('/student-ability')">岗位画像</li>
            <li class="menu-item" @click="$router.push('/career-planning')">职业规划</li>
            <li class="menu-item" @click="$router.push('/resource-library')">资源库</li>
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
              <li class="nav-item" :class="{ active: activeTab === 'collection' }" @click="switchTab('collection')">
                <span class="nav-icon">⭐</span>
                <span class="nav-text">我的收藏</span>
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
          <!-- 基本资料标签页 -->
          <div class="tab-content" v-show="activeTab === 'basic'">
            <div class="content-header">
              <h2 class="content-title">基本资料</h2>
              <button class="edit-btn" @click="isEditingBasic = !isEditingBasic">
                {{ isEditingBasic ? '取消' : '编辑资料' }}
              </button>
            </div>

            <form class="basic-info-form" @submit.prevent="saveBasicInfo">
              <div class="form-row">
                <label class="form-label">用户名</label>
                <input 
                  type="text" 
                  class="form-input" 
                  v-model="editForm.nickname" 
                  :disabled="!isEditingBasic"
                  placeholder="请输入用户名"
                >
              </div>
              
              <div class="form-row">
                <label class="form-label">真实姓名</label>
                <input 
                  type="text" 
                  class="form-input" 
                  v-model="editForm.realName" 
                  :disabled="!isEditingBasic"
                  placeholder="请输入真实姓名"
                >
              </div>
              
              <div class="form-row">
                <label class="form-label">性别</label>
                <div class="radio-group" :class="{ disabled: !isEditingBasic }">
                  <label class="radio-item">
                    <input type="radio" v-model="editForm.gender" value="男" :disabled="!isEditingBasic">
                    男
                  </label>
                  <label class="radio-item">
                    <input type="radio" v-model="editForm.gender" value="女" :disabled="!isEditingBasic">
                    女
                  </label>
                  <label class="radio-item">
                    <input type="radio" v-model="editForm.gender" value="保密" :disabled="!isEditingBasic">
                    保密
                  </label>
                </div>
              </div>
              
              <div class="form-row">
                <label class="form-label">学校</label>
                <input 
                  type="text" 
                  class="form-input" 
                  v-model="editForm.school" 
                  :disabled="!isEditingBasic"
                  placeholder="请输入所在学校"
                >
              </div>
              
              <div class="form-row">
                <label class="form-label">专业</label>
                <input 
                  type="text" 
                  class="form-input" 
                  v-model="editForm.major" 
                  :disabled="!isEditingBasic"
                  placeholder="请输入所学专业"
                >
              </div>
              
              <div class="form-row">
                <label class="form-label">年级</label>
                <select class="form-select" v-model="editForm.grade" :disabled="!isEditingBasic">
                  <option value="">请选择年级</option>
                  <option value="大一">大一</option>
                  <option value="大二">大二</option>
                  <option value="大三">大三</option>
                  <option value="大四">大四</option>
                  <option value="研一">研一</option>
                  <option value="研二">研二</option>
                  <option value="研三">研三</option>
                </select>
              </div>
              
              <div class="form-row">
                <label class="form-label">联系方式</label>
                <input 
                  type="tel" 
                  class="form-input" 
                  v-model="editForm.phone" 
                  :disabled="!isEditingBasic"
                  placeholder="请输入手机号码"
                >
              </div>
              
              <div class="form-row">
                <label class="form-label">邮箱</label>
                <input 
                  type="email" 
                  class="form-input" 
                  v-model="editForm.email" 
                  :disabled="!isEditingBasic"
                  placeholder="请输入邮箱地址"
                >
              </div>
              
              <div class="form-row">
                <label class="form-label">自我介绍</label>
                <textarea 
                  class="form-textarea" 
                  v-model="editForm.introduction" 
                  :disabled="!isEditingBasic"
                  placeholder="请输入自我介绍（选填）"
                  rows="4"
                ></textarea>
              </div>
              
              <div class="form-actions" v-show="isEditingBasic">
                <button type="button" class="cancel-btn" @click="cancelEdit">取消</button>
                <button type="submit" class="save-btn">保存修改</button>
              </div>
            </form>
          </div>

          <!-- 账号安全标签页 -->
          <div class="tab-content" v-show="activeTab === 'security'">
            <div class="content-header">
              <h2 class="content-title">账号安全</h2>
            </div>

            <div class="security-settings">
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
              
              <div class="security-item">
                <div class="item-left">
                  <span class="item-icon">📱</span>
                  <div class="item-text">
                    <span class="item-title">绑定手机号</span>
                    <span class="item-desc" :class="{ unbound: !userInfo.phone }">
                      {{ userInfo.phone || '未绑定' }}
                    </span>
                  </div>
                </div>
                <button class="operate-btn" @click="showBindPhoneModal = true">
                  {{ userInfo.phone ? '更换' : '绑定' }}
                </button>
              </div>
              
              <div class="security-item">
                <div class="item-left">
                  <span class="item-icon">📧</span>
                  <div class="item-text">
                    <span class="item-title">绑定邮箱</span>
                    <span class="item-desc" :class="{ unbound: !userInfo.email }">
                      {{ userInfo.email || '未绑定' }}
                    </span>
                  </div>
                </div>
                <button class="operate-btn" @click="showBindEmailModal = true">
                  {{ userInfo.email ? '更换' : '绑定' }}
                </button>
              </div>
              
              <div class="security-item">
                <div class="item-left">
                  <span class="item-icon">🔔</span>
                  <div class="item-text">
                    <span class="item-title">消息通知</span>
                    <span class="item-desc">设置接收系统消息的方式</span>
                  </div>
                </div>
                <button class="operate-btn" @click="$router.push('/notification-settings')">设置</button>
              </div>
              
              <div class="security-item">
                <div class="item-left">
                  <span class="item-icon">📱</span>
                  <div class="item-text">
                    <span class="item-title">登录设备管理</span>
                    <span class="item-desc">查看并管理登录过的设备</span>
                  </div>
                </div>
                <button class="operate-btn" @click="$router.push('/device-management')">查看</button>
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

          <!-- 我的收藏标签页 -->
          <div class="tab-content" v-show="activeTab === 'collection'">
            <div class="content-header">
              <h2 class="content-title">我的收藏</h2>
              <div class="filter-controls">
                <button class="filter-btn" :class="{ active: collectionFilter === 'all' }" @click="collectionFilter = 'all'">
                  全部
                </button>
                <button class="filter-btn" :class="{ active: collectionFilter === 'job' }" @click="collectionFilter = 'job'">
                  岗位
                </button>
                <button class="filter-btn" :class="{ active: collectionFilter === 'resource' }" @click="collectionFilter = 'resource'">
                  资源
                </button>
              </div>
            </div>

            <div v-if="filteredCollections.length === 0" class="empty-state">
              <div class="empty-icon">⭐</div>
              <div class="empty-text">暂无收藏内容</div>
              <div class="empty-desc">快去收藏你感兴趣的岗位或资源吧</div>
            </div>

            <div class="collection-list" v-else>
              <div class="collection-card" v-for="item in filteredCollections" :key="item.id">
                <div class="card-left">
                  <img :src="item.cover || 'https://picsum.photos/seed/collection/100/100'" alt="" class="collection-cover">
                </div>
                <div class="card-middle">
                  <h3 class="collection-title">{{ item.title }}</h3>
                  <p class="collection-desc">{{ item.desc }}</p>
                  <div class="collection-meta">
                    <span class="meta-item">{{ item.type === 'job' ? '岗位' : '资源' }}</span>
                    <span class="meta-item">{{ formatDate(item.collectTime) }}</span>
                  </div>
                </div>
                <div class="card-right">
                  <button class="view-btn" @click="viewCollection(item)">查看</button>
                  <button class="delete-btn" @click="removeCollection(item.id)">取消收藏</button>
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

    <!-- 绑定手机号弹窗 -->
    <div class="modal-overlay" v-show="showBindPhoneModal" @click="closeModal('phone')">
      <div class="modal-content" @click.stop style="width: 450px;">
        <div class="modal-header">
          <h3 class="modal-title">{{ userInfo.phone ? '更换手机号' : '绑定手机号' }}</h3>
          <button class="close-btn" @click="closeModal('phone')">×</button>
        </div>
        <form class="modal-form" @submit.prevent="bindPhone">
          <!-- 原有手机号验证（更换时显示） -->
          <div class="form-row" v-if="userInfo.phone">
            <label class="form-label">原手机号</label>
            <!-- 修复：移除v-model，只保留value绑定 -->
            <input type="tel" class="form-input" :value="userInfo.phone" disabled>
          </div>
          
          <!-- 新手机号 -->
          <div class="form-row">
            <label class="form-label">{{ userInfo.phone ? '新手机号' : '手机号' }}</label>
            <input 
              type="tel" 
              class="form-input" 
              v-model="phoneForm.newPhone" 
              placeholder="请输入11位手机号码"
              :class="{ 'error-input': phoneForm.phoneError }"
            >
            <div class="error-tip" v-show="phoneForm.phoneError">{{ phoneForm.phoneError }}</div>
          </div>
          
          <!-- 验证码 -->
          <div class="form-row">
            <label class="form-label">验证码</label>
            <div class="code-input-wrap">
              <input 
                type="text" 
                class="form-input code-input" 
                v-model="phoneForm.code" 
                placeholder="请输入6位验证码"
                :class="{ 'error-input': phoneForm.codeError }"
              >
              <button 
                type="button" 
                class="get-code-btn" 
                @click="getPhoneCode"
                :disabled="phoneForm.countdown > 0 || !phoneForm.newPhone"
              >
                {{ phoneForm.countdown > 0 ? `${phoneForm.countdown}秒后重新获取` : '获取验证码' }}
              </button>
            </div>
            <div class="error-tip" v-show="phoneForm.codeError">{{ phoneForm.codeError }}</div>
          </div>
          
          <!-- 密码验证（更换时需要） -->
          <div class="form-row" v-if="userInfo.phone">
            <label class="form-label">登录密码</label>
            <input 
              type="password" 
              class="form-input" 
              v-model="phoneForm.password" 
              placeholder="请输入登录密码验证身份"
              :class="{ 'error-input': phoneForm.pwdError }"
            >
            <div class="error-tip" v-show="phoneForm.pwdError">{{ phoneForm.pwdError }}</div>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal('phone')">取消</button>
            <button type="submit" class="confirm-btn" :disabled="phoneForm.submitting">
              <span v-if="phoneForm.submitting">处理中...</span>
              <span v-else>{{ userInfo.phone ? '确认更换' : '确认绑定' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 绑定邮箱弹窗 -->
    <div class="modal-overlay" v-show="showBindEmailModal" @click="closeModal('email')">
      <div class="modal-content" @click.stop style="width: 450px;">
        <div class="modal-header">
          <h3 class="modal-title">{{ userInfo.email ? '更换邮箱' : '绑定邮箱' }}</h3>
          <button class="close-btn" @click="closeModal('email')">×</button>
        </div>
        <form class="modal-form" @submit.prevent="bindEmail">
          <!-- 原有邮箱验证（更换时显示） -->
          <div class="form-row" v-if="userInfo.email">
            <label class="form-label">原邮箱</label>
            <!-- 修复：移除v-model，只保留value绑定 -->
            <input type="email" class="form-input" :value="userInfo.email" disabled>
          </div>
          
          <!-- 新邮箱 -->
          <div class="form-row">
            <label class="form-label">{{ userInfo.email ? '新邮箱' : '邮箱' }}</label>
            <input 
              type="email" 
              class="form-input" 
              v-model="emailForm.newEmail" 
              placeholder="请输入邮箱地址"
              :class="{ 'error-input': emailForm.emailError }"
            >
            <div class="error-tip" v-show="emailForm.emailError">{{ emailForm.emailError }}</div>
          </div>
          
          <!-- 验证码 -->
          <div class="form-row">
            <label class="form-label">验证码</label>
            <div class="code-input-wrap">
              <input 
                type="text" 
                class="form-input code-input" 
                v-model="emailForm.code" 
                placeholder="请输入6位验证码"
                :class="{ 'error-input': emailForm.codeError }"
              >
              <button 
                type="button" 
                class="get-code-btn" 
                @click="getEmailCode"
                :disabled="emailForm.countdown > 0 || !emailForm.newEmail"
              >
                {{ emailForm.countdown > 0 ? `${emailForm.countdown}秒后重新获取` : '获取验证码' }}
              </button>
            </div>
            <div class="error-tip" v-show="emailForm.codeError">{{ emailForm.codeError }}</div>
          </div>
          
          <!-- 密码验证（更换时需要） -->
          <div class="form-row" v-if="userInfo.email">
            <label class="form-label">登录密码</label>
            <input 
              type="password" 
              class="form-input" 
              v-model="emailForm.password" 
              placeholder="请输入登录密码验证身份"
              :class="{ 'error-input': emailForm.pwdError }"
            >
            <div class="error-tip" v-show="emailForm.pwdError">{{ emailForm.pwdError }}</div>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal('email')">取消</button>
            <button type="submit" class="confirm-btn" :disabled="emailForm.submitting">
              <span v-if="emailForm.submitting">处理中...</span>
              <span v-else>{{ userInfo.email ? '确认更换' : '确认绑定' }}</span>
            </button>
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
const showBindEmailModal = ref(false)

// ========== 模拟数据 ==========
// 用户信息
const userInfo = ref({
  avatar: localStorage.getItem('avatar') || 'https://picsum.photos/seed/avatar/200/200',
  nickname: localStorage.getItem('nickname') || '用户' + Math.floor(Math.random() * 10000),
  realName: '',
  gender: '保密',
  school: '',
  major: '',
  grade: '',
  phone: '',
  email: '',
  introduction: '',
  role: '普通用户',
  joinTime: '2026-01-15'
})

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

// 手机号绑定表单
const phoneForm = ref({
  oldPhone: '',
  newPhone: '',
  code: '',
  password: '',
  phoneError: '',
  codeError: '',
  pwdError: '',
  countdown: 0,
  submitting: false
})

// 邮箱绑定表单
const emailForm = ref({
  oldEmail: '',
  newEmail: '',
  code: '',
  password: '',
  emailError: '',
  codeError: '',
  pwdError: '',
  countdown: 0,
  submitting: false
})

// 用户统计数据
const userStats = ref({
  assessmentCount: 2,
  planCount: 1,
  collectionCount: 8
})

// 职业规划列表
const careerPlans = ref([
  {
    id: 1,
    title: '前端开发工程师职业规划',
    createTime: '2026-02-10',
    targetJob: '前端开发工程师',
    cycle: '3年',
    matchRate: 92
  },
  {
    id: 2,
    title: '产品经理职业规划',
    createTime: '2026-01-20',
    targetJob: '产品经理',
    cycle: '2年',
    matchRate: 85
  }
])

// 收藏列表
const collections = ref([
  {
    id: 1,
    title: '字节跳动-前端开发工程师',
    desc: '负责公司核心产品的前端开发工作',
    cover: 'https://picsum.photos/seed/job1/100/100',
    type: 'job',
    collectTime: '2026-03-01'
  },
  {
    id: 2,
    title: '2026前端面试题大全',
    desc: '包含HTML、CSS、JavaScript、Vue、React等面试题',
    cover: 'https://picsum.photos/seed/resource1/100/100',
    type: 'resource',
    collectTime: '2026-02-28'
  },
  {
    id: 3,
    title: '阿里巴巴-产品经理',
    desc: '负责电商产品的规划和设计',
    cover: 'https://picsum.photos/seed/job2/100/100',
    type: 'job',
    collectTime: '2026-02-20'
  }
])

// 收藏筛选
const collectionFilter = ref('all')
const filteredCollections = computed(() => {
  if (collectionFilter.value === 'all') {
    return collections.value
  }
  return collections.value.filter(item => item.type === collectionFilter.value)
})

// 浏览历史
const browseHistory = ref([
  {
    id: 1,
    title: '数据分析师岗位画像',
    desc: '数据分析师的岗位要求、技能要求、薪资水平等',
    cover: 'https://picsum.photos/seed/history1/80/80',
    browseTime: '2026-03-15'
  },
  {
    id: 2,
    title: 'Python数据分析实战教程',
    desc: '从入门到精通的Python数据分析教程',
    cover: 'https://picsum.photos/seed/history2/80/80',
    browseTime: '2026-03-14'
  }
])

// ========== 方法定义 ==========
// 切换标签页
const switchTab = (tab) => {
  activeTab.value = tab
}

// 编辑资料相关
const cancelEdit = () => {
  isEditingBasic.value = false
  // 重置表单
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
  // 保存用户信息
  userInfo.value = { ...editForm.value, role: userInfo.value.role, joinTime: userInfo.value.joinTime }
  // 更新本地存储
  localStorage.setItem('nickname', editForm.value.nickname)
  // 关闭编辑状态
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
  if (!isImage) {
    ElMessage.error('请选择图片文件')
    return
  }
  
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过5MB')
    return
  }
  
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
  if (!pwdForm.value.oldPwd) {
    ElMessage.warning('请输入原密码')
    return
  }
  if (!pwdForm.value.newPwd) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (pwdForm.value.newPwd !== pwdForm.value.confirmPwd) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  // 模拟修改密码
  showChangePwdModal.value = false
  pwdForm.value = { oldPwd: '', newPwd: '', confirmPwd: '' }
  ElMessage.success('密码修改成功，请重新登录')
  // 这里可以添加退出登录逻辑
}

// 关闭弹窗
const closeModal = (type) => {
  if (type === 'changePwd') {
    showChangePwdModal.value = false
    pwdForm.value = { oldPwd: '', newPwd: '', confirmPwd: '' }
  } else if (type === 'phone') {
    showBindPhoneModal.value = false
    // 重置手机号表单
    phoneForm.value = {
      oldPhone: '',
      newPhone: '',
      code: '',
      password: '',
      phoneError: '',
      codeError: '',
      pwdError: '',
      countdown: 0,
      submitting: false
    }
  } else if (type === 'email') {
    showBindEmailModal.value = false
    // 重置邮箱表单
    emailForm.value = {
      oldEmail: '',
      newEmail: '',
      code: '',
      password: '',
      emailError: '',
      codeError: '',
      pwdError: '',
      countdown: 0,
      submitting: false
    }
  }
}

// 验证码倒计时函数
const startCountdown = (form) => {
  form.countdown = 60
  const timer = setInterval(() => {
    form.countdown--
    if (form.countdown <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 获取手机验证码
const getPhoneCode = () => {
  // 清空之前的错误提示
  phoneForm.value.phoneError = ''
  
  // 验证手机号格式
  const phone = phoneForm.value.newPhone.trim()
  if (!phone) {
    phoneForm.value.phoneError = '请输入手机号码'
    return
  }
  
  const phoneReg = /^1[3-9]\d{9}$/
  if (!phoneReg.test(phone)) {
    phoneForm.value.phoneError = '请输入有效的11位手机号码'
    return
  }
  
  // 模拟发送验证码
  ElMessage.success('验证码已发送，请注意查收')
  startCountdown(phoneForm.value)
}

// 获取邮箱验证码
const getEmailCode = () => {
  // 清空之前的错误提示
  emailForm.value.emailError = ''
  
  // 验证邮箱格式
  const email = emailForm.value.newEmail.trim()
  if (!email) {
    emailForm.value.emailError = '请输入邮箱地址'
    return
  }
  
  const emailReg = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/
  if (!emailReg.test(email)) {
    emailForm.value.emailError = '请输入有效的邮箱地址'
    return
  }
  
  // 模拟发送验证码
  ElMessage.success('验证码已发送至您的邮箱，请注意查收')
  startCountdown(emailForm.value)
}

// 绑定/更换手机号
const bindPhone = () => {
  // 清空之前的错误提示
  phoneForm.value.phoneError = ''
  phoneForm.value.codeError = ''
  phoneForm.value.pwdError = ''
  
  // 验证手机号
  const phone = phoneForm.value.newPhone.trim()
  if (!phone) {
    phoneForm.value.phoneError = '请输入手机号码'
    return
  }
  
  const phoneReg = /^1[3-9]\d{9}$/
  if (!phoneReg.test(phone)) {
    phoneForm.value.phoneError = '请输入有效的11位手机号码'
    return
  }
  
  // 验证验证码
  const code = phoneForm.value.code.trim()
  if (!code) {
    phoneForm.value.codeError = '请输入验证码'
    return
  }
  
  if (!/^\d{6}$/.test(code)) {
    phoneForm.value.codeError = '请输入6位数字验证码'
    return
  }
  
  // 更换手机号时验证密码
  if (userInfo.value.phone) {
    const password = phoneForm.value.password.trim()
    if (!password) {
      phoneForm.value.pwdError = '请输入登录密码'
      return
    }
    
    // 简单密码验证（实际项目中应该调用接口）
    if (password.length < 6) {
      phoneForm.value.pwdError = '密码长度不能少于6位'
      return
    }
  }
  
  // 模拟提交
  phoneForm.value.submitting = true
  
  setTimeout(() => {
    // 更新用户信息
    userInfo.value.phone = phone
    editForm.value.phone = phone
    
    // 更新表单状态
    phoneForm.value.submitting = false
    showBindPhoneModal.value = false
    
    // 重置表单
    phoneForm.value = {
      oldPhone: '',
      newPhone: '',
      code: '',
      password: '',
      phoneError: '',
      codeError: '',
      pwdError: '',
      countdown: 0,
      submitting: false
    }
    
    ElMessage.success(userInfo.value.phone ? '手机号更换成功' : '手机号绑定成功')
  }, 1500)
}

// 绑定/更换邮箱
const bindEmail = () => {
  // 清空之前的错误提示
  emailForm.value.emailError = ''
  emailForm.value.codeError = ''
  emailForm.value.pwdError = ''
  
  // 验证邮箱
  const email = emailForm.value.newEmail.trim()
  if (!email) {
    emailForm.value.emailError = '请输入邮箱地址'
    return
  }
  
  const emailReg = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/
  if (!emailReg.test(email)) {
    emailForm.value.emailError = '请输入有效的邮箱地址'
    return
  }
  
  // 验证验证码
  const code = emailForm.value.code.trim()
  if (!code) {
    emailForm.value.codeError = '请输入验证码'
    return
  }
  
  if (!/^\d{6}$/.test(code)) {
    emailForm.value.codeError = '请输入6位数字验证码'
    return
  }
  
  // 更换邮箱时验证密码
  if (userInfo.value.email) {
    const password = emailForm.value.password.trim()
    if (!password) {
      emailForm.value.pwdError = '请输入登录密码'
      return
    }
    
    // 简单密码验证
    if (password.length < 6) {
      emailForm.value.pwdError = '密码长度不能少于6位'
      return
    }
  }
  
  // 模拟提交
  emailForm.value.submitting = true
  
  setTimeout(() => {
    // 更新用户信息
    userInfo.value.email = email
    editForm.value.email = email
    
    // 更新表单状态
    emailForm.value.submitting = false
    showBindEmailModal.value = false
    
    // 重置表单
    emailForm.value = {
      oldEmail: '',
      newEmail: '',
      code: '',
      password: '',
      emailError: '',
      codeError: '',
      pwdError: '',
      countdown: 0,
      submitting: false
    }
    
    ElMessage.success(userInfo.value.email ? '邮箱更换成功' : '邮箱绑定成功')
  }, 1500)
}

// 职业规划相关
const exportPlan = (id) => {
  ElMessage.success(`规划方案${id}导出成功`)
}

// 收藏相关
const viewCollection = (item) => {
  if (item.type === 'job') {
    router.push(`/job-detail?id=${item.id}`)
  } else {
    router.push(`/resource-detail?id=${item.id}`)
  }
}

const removeCollection = (id) => {
  collections.value = collections.value.filter(item => item.id !== id)
  ElMessage.success('取消收藏成功')
}

// 历史记录相关
const clearHistory = () => {
  browseHistory.value = []
  ElMessage.success('浏览历史已清空')
}

const viewHistory = (item) => {
  // 根据类型跳转对应页面
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
  if (darkMode.value) {
    document.body.classList.add('dark')
  } else {
    document.body.classList.remove('dark')
  }
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
    case '测评':
      router.push('/interest-test')
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
  // 检查登录状态
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

/* 收藏列表 */
.collection-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.collection-card {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}
.card-left {
  width: 80px;
  flex-shrink: 0;
}
.collection-cover {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
}
.card-middle {
  flex: 1;
  padding: 0 15px;
}
.collection-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}
.collection-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.collection-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}
.card-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-right .view-btn {
  padding: 6px 12px;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.card-right .delete-btn {
  padding: 6px 12px;
  background: #fff;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
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
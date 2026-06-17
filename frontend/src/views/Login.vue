<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 左侧品牌区 -->
      <div class="brand-side">
        <h1 class="brand-title">全平台视频 & 音乐 & 图片下载</h1>
        <h2 class="brand-subtitle">一键搞定</h2>
        <p class="brand-desc">
          支持 YouTube、Bilibili、抖音、微博、Apple Music 等
          <strong>3000+</strong> 平台，高清无损，快速下载。
        </p>
        
        <div class="visual-container">
          <div class="cloud-box">
            <span class="cloud-icon">☁️</span>
          </div>
          <div class="logo-orbit">
            <span class="orbit-logo">📺</span>
            <span class="orbit-logo">🎵</span>
            <span class="orbit-logo">🎬</span>
            <span class="orbit-logo">📷</span>
            <span class="orbit-logo">🐦</span>
            <span class="orbit-logo">🎧</span>
            <span class="orbit-logo">💬</span>
            <span class="orbit-logo">📱</span>
          </div>
        </div>
        
        <div class="platform-list">
          <span class="platform-tag">YouTube</span>
          <span class="platform-tag">Bilibili</span>
          <span class="platform-tag">抖音</span>
          <span class="platform-tag">小红书</span>
          <span class="platform-tag">快手</span>
          <span class="platform-tag">微博</span>
          <span class="platform-tag">Twitter</span>
          <span class="platform-tag">Instagram</span>
        </div>
        
        <div class="footer-copyright">© 2026 Bosco Tsang. All rights reserved.</div>
      </div>
      
      <!-- 右侧登录区 -->
      <div class="form-side">
        <div class="login-card">
          <div class="login-header">
            <div class="app-logo">🚀</div>
            <h3 class="welcome-text">欢迎回来</h3>
            <p class="welcome-sub">登录您的账号以继续使用 Bosco Tsang</p>
          </div>
          
          <form @submit.prevent="handleLogin" class="login-form">
            <div class="input-group">
              <span class="input-icon">👤</span>
              <input 
                v-model="username" 
                type="text" 
                placeholder="用户名" 
                class="input"
                required
              />
            </div>
            
            <div class="input-group">
              <span class="input-icon">🔒</span>
              <input 
                v-model="password" 
                :type="showPassword ? 'text' : 'password'" 
                placeholder="密码" 
                class="input"
                required
              />
              <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                {{ showPassword ? '🙈' : '👁️' }}
              </button>
            </div>
            
            <div class="form-options">
              <label class="remember-me">
                <input type="checkbox" v-model="rememberMe" />
                <span>记住我</span>
              </label>
            </div>
            
            <button type="submit" class="btn-submit" :disabled="loading">
              {{ loading ? '正在验证身份...' : '登 录' }}
            </button>
            
            <div v-if="errorMsg" class="error-toast">
              ⚠️ {{ errorMsg }}
            </div>
          </form>
                  
          <!-- Telegram 登录分隔线 -->
          <div v-if="telegramEnabled" class="divider">
            <span>或使用 Telegram 登录</span>
          </div>
                  
          <!-- Telegram 登录按钮 -->
          <div v-if="telegramEnabled" class="telegram-login-container">
            <div id="telegram-login-button"></div>
          </div>
                  
          <!-- Telegram 绑定表单 -->
          <div v-if="showBinding" class="binding-panel">
            <h4>🔗 绑定系统账号</h4>
            <p class="binding-hint">这是您首次使用 Telegram 登录，请先绑定系统账号</p>
            <div class="input-group">
              <span class="input-icon">👤</span>
              <input 
                v-model="bindUsername" 
                type="text" 
                placeholder="系统用户名" 
                class="input"
              />
            </div>
            <div class="input-group">
              <span class="input-icon">🔒</span>
              <input 
                v-model="bindPassword" 
                type="password" 
                placeholder="系统密码" 
                class="input"
              />
            </div>
            <button class="btn-bind" @click="handleBind" :disabled="binding">
              {{ binding ? '绑定中...' : '绑定并登录' }}
            </button>
            <button class="btn-cancel" @click="cancelBinding">取消</button>
          </div>
          
          <div class="register-panel">
            <h4>使用邀请码注册</h4>
            <div class="input-group">
              <span class="input-icon">🎟️</span>
              <input
                v-model="inviteCode"
                type="text"
                placeholder="邀请码"
                class="input"
              />
            </div>
            <button class="btn-secondary" @click="handleRegister" :disabled="registering">
              {{ registering ? '注册中...' : '立即注册' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '@/utils/api.js'

const router = useRouter()

const username = ref('')
const password = ref('')
const inviteCode = ref('')
const rememberMe = ref(true)
const loading = ref(false)
const registering = ref(false)
const errorMsg = ref('')
const showPassword = ref(false)

// Telegram 登录相关
const telegramEnabled = ref(false)
const showBinding = ref(false)
const telegramData = ref(null)
const bindUsername = ref('')
const bindPassword = ref('')
const binding = ref(false)

// 页面加载时检查 Telegram 登录配置
onMounted(async () => {
  try {
    const response = await fetch('/api/admin/telegram/login-url')
    const config = await response.json()
    if (config.enabled) {
      telegramEnabled.value = true
      // 加载 Telegram Widget
      loadTelegramWidget()
    }
  } catch (error) {
    console.error('加载 Telegram 配置失败:', error)
  }
})

// 加载 Telegram Widget 脚本
function loadTelegramWidget() {
  // 检查是否已经加载
  if (document.getElementById('telegram-widget-script')) {
    return
  }
  
  const script = document.createElement('script')
  script.id = 'telegram-widget-script'
  script.src = 'https://telegram.org/js/telegram-widget.js?22'
  script.setAttribute('data-telegram-login', 'BoscoTsangBot')  // 需要替换为实际的 Bot Username
  script.setAttribute('data-size', 'large')
  script.setAttribute('data-radius', '10')
  script.setAttribute('data-request-access', 'write')
  script.setAttribute('data-onauth', 'onTelegramAuth')
  script.async = true
  
  document.getElementById('telegram-login-button').appendChild(script)
}

// Telegram 登录回调（全局函数）
window.onTelegramAuth = async (user) => {
  try {
    errorMsg.value = ''
    telegramData.value = user
    
    const response = await fetch('/api/admin/telegram/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(user)
    })
    
    const data = await response.json()
    
    if (data.status === 'success') {
      // 登录成功
      localStorage.setItem('token', data.token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('role', data.role)
      router.push('/')
    } else if (data.status === 'need_binding') {
      // 需要绑定账号
      showBinding.value = true
    } else {
      errorMsg.value = data.detail || 'Telegram 登录失败'
    }
  } catch (error) {
    errorMsg.value = 'Telegram 登录失败: ' + error.message
  }
}

// 处理绑定账号
async function handleBind() {
  if (!bindUsername.value || !bindPassword.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  
  binding.value = true
  errorMsg.value = ''
  
  try {
    const response = await fetch('/api/admin/telegram/bind', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        telegram_id: telegramData.value.id,
        username: bindUsername.value,
        password: bindPassword.value
      })
    })
    
    const data = await response.json()
    
    if (data.status === 'success') {
      localStorage.setItem('token', data.token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('role', data.role)
      router.push('/')
    } else {
      errorMsg.value = data.detail || '绑定失败'
    }
  } catch (error) {
    errorMsg.value = '绑定失败: ' + error.message
  } finally {
    binding.value = false
  }
}

// 取消绑定
function cancelBinding() {
  showBinding.value = false
  telegramData.value = null
  bindUsername.value = ''
  bindPassword.value = ''
}

async function handleRegister() {
  registering.value = true
  errorMsg.value = ''

  if (!username.value || !password.value || !inviteCode.value) {
    errorMsg.value = '用户名、密码和邀请码均为必填项'
    registering.value = false
    return
  }

  try {
    await auth.register(username.value, password.value, inviteCode.value)
    alert('注册成功，请使用登录信息登录')
  } catch (error) {
    errorMsg.value = error.message || '注册失败，请检查邀请码'
  } finally {
    registering.value = false
  }
}

async function handleLogin() {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const data = await auth.login(username.value, password.value)
    
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('role', data.role)
    
    router.push('/')
  } catch (error) {
    errorMsg.value = error.message || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #1a1c29 0%, #0f111a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 95%;
  max-width: 1100px;
  height: 600px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 24px;
  display: flex;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.brand-side {
  flex: 1.2;
  padding: 50px;
  display: flex;
  flex-direction: column;
  color: #fff;
  position: relative;
}

.brand-title {
  font-size: 32px;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #fff 30%, #a5b4fc);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 28px;
  color: #3b82f6;
  margin: 10px 0;
}

.brand-desc {
  font-size: 15px;
  color: #94a3b8;
  line-height: 1.7;
  max-width: 400px;
  margin-top: 16px;
}

.brand-desc strong {
  color: #60a5fa;
}

.visual-container {
  position: relative;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 30px 0;
}

.cloud-box {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  border-radius: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 20px 40px rgba(37, 99, 235, 0.4);
  animation: float 4s ease-in-out infinite;
  z-index: 2;
}

.cloud-icon {
  font-size: 50px;
}

.logo-orbit {
  position: absolute;
  width: 280px;
  height: 280px;
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: spin 20s linear infinite;
}

.orbit-logo {
  position: absolute;
  font-size: 24px;
  background: rgba(255, 255, 255, 0.05);
  padding: 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.orbit-logo:nth-child(1) { top: -15px; left: 50%; transform: translateX(-50%); }
.orbit-logo:nth-child(2) { bottom: -15px; left: 50%; transform: translateX(-50%); }
.orbit-logo:nth-child(3) { left: -15px; top: 50%; transform: translateY(-50%); }
.orbit-logo:nth-child(4) { right: -15px; top: 50%; transform: translateY(-50%); }
.orbit-logo:nth-child(5) { top: 10%; right: 18%; }
.orbit-logo:nth-child(6) { top: 10%; left: 18%; }
.orbit-logo:nth-child(7) { bottom: 10%; right: 18%; }
.orbit-logo:nth-child(8) { bottom: 10%; left: 18%; }

.platform-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 20px;
}

.platform-tag {
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  font-size: 12px;
  color: #94a3b8;
}

.footer-copyright {
  font-size: 11px;
  color: #475569;
  margin-top: auto;
}

.form-side {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  border-left: 1px solid rgba(255, 255, 255, 0.05);
}

.login-card {
  width: 80%;
  max-width: 380px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.app-logo {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-text {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.welcome-sub {
  font-size: 14px;
  color: #64748b;
  margin: 8px 0 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
}

.input {
  width: 100%;
  padding: 14px 14px 14px 44px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.toggle-password {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #64748b;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.btn-submit {
  width: 100%;
  padding: 14px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-submit:hover {
  background: #1d4ed8;
}

.btn-submit:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.register-panel {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.register-panel h4 {
  margin-bottom: 12px;
  font-size: 14px;
  color: #cbd5e1;
}

.btn-secondary {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.05);
  color: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 12px;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-toast {
  background: #fef2f2;
  color: #991b1b;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid #fca5a5;
  text-align: center;
}

/* Telegram 登录样式 */
.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: #64748b;
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.divider span {
  padding: 0 12px;
}

.telegram-login-container {
  display: flex;
  justify-content: center;
  margin: 16px 0;
}

.telegram-login-container :deep(iframe) {
  border-radius: 10px !important;
}

.binding-panel {
  margin-top: 20px;
  padding: 20px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
}

.binding-panel h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #1e293b;
}

.binding-hint {
  margin: 0 0 16px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

.binding-panel .input-group {
  margin-bottom: 12px;
}

.btn-bind {
  width: 100%;
  padding: 12px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
}

.btn-bind:hover {
  background: #059669;
}

.btn-bind:disabled {
  background: #6ee7b7;
  cursor: not-allowed;
}

.btn-cancel {
  width: 100%;
  padding: 12px;
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.register-hint {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-icon">🚀</span>
          <span class="logo-text">Bosco Tsang</span>
        </div>
      </div>
      
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <span class="nav-icon">🏠</span>
          <span class="nav-text">主页</span>
        </router-link>
        
        <router-link to="/downloads" class="nav-item" :class="{ active: $route.path === '/downloads' }">
          <span class="nav-icon">⬇️</span>
          <span class="nav-text">下载</span>
        </router-link>
        
        <router-link to="/history" class="nav-item" :class="{ active: $route.path === '/history' }">
          <span class="nav-icon">📜</span>
          <span class="nav-text">历史</span>
        </router-link>
        
        <router-link to="/subscriptions" class="nav-item" :class="{ active: $route.path === '/subscriptions' }">
          <span class="nav-icon">📡</span>
          <span class="nav-text">订阅</span>
        </router-link>
        
        <router-link to="/files" class="nav-item" :class="{ active: $route.path === '/files' }">
          <span class="nav-icon">📁</span>
          <span class="nav-text">文件管理</span>
        </router-link>
        
        <router-link to="/logs" class="nav-item" :class="{ active: $route.path === '/logs' }">
          <span class="nav-icon">📋</span>
          <span class="nav-text">日志</span>
        </router-link>
        
        <router-link to="/monitor" class="nav-item" :class="{ active: $route.path === '/monitor' }">
          <span class="nav-icon">📊</span>
          <span class="nav-text">监控</span>
        </router-link>
        
        <router-link to="/settings" class="nav-item" :class="{ active: $route.path.startsWith('/settings') }">
          <span class="nav-icon">⚙️</span>
          <span class="nav-text">设置</span>
        </router-link>
      </nav>
    </aside>
    
    <!-- 主内容区 -->
    <div class="main-wrapper">
      <!-- 顶部栏 -->
      <header class="header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        
        <div class="header-right">
          <!-- 使用说明书 -->
          <button class="header-btn help-btn" @click="showHelpModal = true" title="使用说明书">
            <span>📖</span>
            <span class="btn-text">帮助</span>
          </button>
          
          <!-- 更新日志 -->
          <button class="header-btn changelog-btn" @click="showChangelogModal = true" title="更新日志">
            <span>📝</span>
            <span class="btn-text">更新</span>
          </button>
          
          <!-- 语言切换 -->
          <select v-model="currentLang" class="lang-select" @change="changeLang">
            <option value="zh">中文</option>
            <option value="en">English</option>
          </select>
          
          <!-- 通知 -->
          <button class="header-btn" @click="showNotifications = !showNotifications">
            <span>🔔</span>
          </button>
          
          <!-- 用户 -->
          <div class="user-info" @click="showUserMenu = !showUserMenu">
            <div class="user-avatar">{{ userInitial }}</div>
            <span class="username">{{ username }}</span>
          </div>
          
          <!-- 用户菜单 -->
          <div v-if="showUserMenu" class="user-menu">
            <router-link to="/settings" class="menu-item" @click="showUserMenu = false">
              账户设置
            </router-link>
            <button class="menu-item" @click="logout">退出登录</button>
          </div>
        </div>
      </header>
      
      <!-- 页面内容 -->
      <main class="content">
        <router-view />
      </main>
    </div>
    
    <!-- 使用说明书模态框 -->
    <div v-if="showHelpModal" class="modal-overlay" @click.self="showHelpModal = false">
      <div class="modal-card help-modal">
        <div class="modal-header">
          <h3>📖 使用说明书</h3>
          <button class="btn btn-gray btn-sm" @click="showHelpModal = false">✕</button>
        </div>
        <div class="modal-body">
          <iframe src="/docs/USAGE_MANUAL.html" class="modal-iframe"></iframe>
        </div>
      </div>
    </div>
    
    <!-- 更新日志模态框 -->
    <div v-if="showChangelogModal" class="modal-overlay" @click.self="showChangelogModal = false">
      <div class="modal-card changelog-modal">
        <div class="modal-header">
          <h3>📝 更新日志</h3>
          <button class="btn btn-gray btn-sm" @click="showChangelogModal = false">✕</button>
        </div>
        <div class="modal-body">
          <iframe src="/docs/CHANGELOG.html" class="modal-iframe"></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const username = ref(localStorage.getItem('username') || 'Admin')
const currentLang = ref('zh')
const showNotifications = ref(false)
const showUserMenu = ref(false)
const showHelpModal = ref(false)
const showChangelogModal = ref(false)

const pageTitle = computed(() => {
  const titles = {
    '/': '控制台',
    '/downloads': '下载管理',
    '/history': '下载历史',
    '/subscriptions': '订阅管理',
    '/files': '文件管理',
    '/logs': '运行日志',
    '/monitor': '系统监控',
    '/settings': '系统设置'
  }
  return titles[route.path] || 'Bosco Tsang'
})

const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase()
})

function changeLang() {
  // 语言切换逻辑
}

function logout() {
  localStorage.clear()
  router.push('/login')
}

function handleClickOutside(e) {
  if (showUserMenu.value && !e.target.closest('.user-info')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  position: fixed;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.sidebar-nav {
  padding: 16px 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius);
  color: var(--text-secondary);
  text-decoration: none;
  margin-bottom: 4px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.nav-item.active {
  background: #dbeafe;
  color: var(--primary);
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

.main-wrapper {
  flex: 1;
  margin-left: var(--sidebar-width);
}

.header {
  height: var(--header-height);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.lang-select {
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 13px;
  cursor: pointer;
}

.header-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: var(--bg-primary);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: inherit;
}

.help-btn, .changelog-btn {
  width: auto;
  padding: 0 12px;
  gap: 4px;
}

.btn-text {
  font-size: 13px;
  font-weight: 500;
}

.header-btn:hover {
  opacity: 0.8;
}

.help-btn:hover {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.changelog-btn:hover {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius);
}

.user-info:hover {
  background: var(--bg-primary);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.user-menu {
  position: absolute;
  top: 100%;
  right: 24px;
  margin-top: 8px;
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  min-width: 150px;
  overflow: hidden;
}

.menu-item {
  display: block;
  width: 100%;
  padding: 10px 16px;
  text-align: left;
  border: none;
  background: none;
  font-size: 14px;
  color: var(--text-primary);
  text-decoration: none;
  cursor: pointer;
}

.menu-item:hover {
  background: var(--bg-primary);
}

.content {
  padding: 24px;
  background: var(--bg-primary);
  min-height: calc(100vh - var(--header-height));
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.help-modal, .changelog-modal {
  width: 80vw;
  height: 80vh;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.modal-body {
  flex: 1;
  overflow: hidden;
}

.modal-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: white;
}
</style>

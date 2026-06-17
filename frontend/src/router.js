import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Layout from './views/Layout.vue'
import Dashboard from './views/Dashboard.vue'
import Downloads from './views/Downloads.vue'
import History from './views/History.vue'
import Subscriptions from './views/Subscriptions.vue'
import Logs from './views/Logs.vue'
import Monitor from './views/Monitor.vue'
import Settings from './views/Settings.vue'
import FilesManager from './views/FilesManager.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login },
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', name: 'Dashboard', component: Dashboard },
      { path: 'downloads', name: 'Downloads', component: Downloads },
      { path: 'history', name: 'History', component: History },
      { path: 'subscriptions', name: 'Subscriptions', component: Subscriptions },
      { path: 'logs', name: 'Logs', component: Logs },
      { path: 'files', name: 'Files', component: FilesManager },
      { path: 'monitor', name: 'Monitor', component: Monitor },
      { path: 'settings', name: 'Settings', component: Settings },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router

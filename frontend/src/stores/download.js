import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useDownloadStore = defineStore('download', () => {
  const tasks = ref([])
  const progress = ref({})  // task_id -> progress data
  const loading = ref(false)
  const ws = ref(null)

  const activeTasks = computed(() => tasks.value.filter(t => t.status === 'downloading' || t.status === 'pending'))
  const completedTasks = computed(() => tasks.value.filter(t => t.status === 'completed'))
  const failedTasks = computed(() => tasks.value.filter(t => t.status === 'failed'))

  async function fetchTasks(params = {}) {
    loading.value = true
    try {
      const data = await api.get('/api/downloads', { params })
      tasks.value = data.tasks || []
    } finally {
      loading.value = false
    }
  }

  async function startDownload(url, quality = 'best') {
    const data = await api.post('/api/download', { url, quality })
    // 立即添加到本地列表
    tasks.value.unshift({
      task_id: data.task_id,
      url,
      status: 'pending',
      progress: 0,
      platform: data.platform
    })
    return data
  }

  function updateProgress(taskId, data) {
    progress.value[taskId] = data
    // 同步更新任务列表
    const idx = tasks.value.findIndex(t => t.task_id === taskId)
    if (idx >= 0) {
      tasks.value[idx] = { ...tasks.value[idx], ...data }
    }
  }

  // WebSocket 连接
  function connectWS() {
    const token = localStorage.getItem('token')
    if (!token) return

    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${location.host}/ws?token=${token}`

    ws.value = new WebSocket(wsUrl)

    ws.value.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'download_progress') {
          updateProgress(msg.task_id, msg.data)
        }
      } catch (e) {
        console.error('WebSocket 消息解析失败:', e)
      }
    }

    ws.value.onclose = () => {
      // 自动重连
      setTimeout(connectWS, 3000)
    }

    ws.value.onerror = () => {
      ws.value?.close()
    }

    // 心跳
    setInterval(() => {
      if (ws.value?.readyState === WebSocket.OPEN) {
        ws.value.send('ping')
      }
    }, 30000)
  }

  function disconnectWS() {
    ws.value?.close()
    ws.value = null
  }

  return {
    tasks, progress, loading,
    activeTasks, completedTasks, failedTasks,
    fetchTasks, startDownload, updateProgress,
    connectWS, disconnectWS
  }
})

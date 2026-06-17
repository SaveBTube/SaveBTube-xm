<template>
  <div class="downloads-page">
    <!-- 任务统计 -->
    <div class="stats-row">
      <div class="stat-mini">
        <span class="stat-num downloading">{{ downloadingCount }}</span>
        <span class="stat-lbl">下载中</span>
      </div>
      <div class="stat-mini">
        <span class="stat-num completed">{{ completedCount }}</span>
        <span class="stat-lbl">已完成</span>
      </div>
      <div class="stat-mini">
        <span class="stat-num failed">{{ failedCount }}</span>
        <span class="stat-lbl">失败</span>
      </div>
      <div class="stat-mini">
        <span class="stat-num speed">{{ currentSpeed }}</span>
        <span class="stat-lbl">当前速度</span>
      </div>
    </div>
    
    <!-- 筛选栏 -->
    <div class="filter-bar card">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="搜索标题或链接..." 
        class="search-input"
        @keyup.enter="loadTasks"
      />
      <select v-model="filterPlatform" class="filter-select" @change="loadTasks">
        <option value="">所有平台</option>
        <option value="YouTube">YouTube</option>
        <option value="Bilibili">Bilibili</option>
        <option value="Douyin">抖音</option>
        <option value="Kuaishou">快手</option>
        <option value="Xiaohongshu">小红书</option>
        <option value="X">X</option>
        <option value="QQMusic">QQ音乐</option>
        <option value="Weibo">微博</option>
      </select>
      <select v-model="filterStatus" class="filter-select" @change="loadTasks">
        <option value="">所有状态</option>
        <option value="downloading">下载中</option>
        <option value="completed">已完成</option>
        <option value="failed">失败</option>
      </select>
      <select v-model="filterType" class="filter-select" @change="loadTasks">
        <option value="">所有类型</option>
        <option value="video">视频</option>
        <option value="audio">音频</option>
        <option value="image">图片</option>
      </select>
      <button class="btn btn-gray" @click="loadTasks">🔄 刷新</button>
    </div>

    <!-- 平台说明 -->
    <div class="card platform-card">
      <div class="card-header">
        <h3 class="card-title">🌐 平台说明</h3>
      </div>
      <div class="platform-list">
        <span class="platform-tag">YouTube</span>
        <span class="platform-tag">X</span>
        <span class="platform-tag">QQ音乐</span>
        <span class="platform-tag">小红书</span>
        <span class="platform-tag">抖音</span>
        <span class="platform-tag">Bilibili</span>
        <span class="platform-tag">微博</span>
      </div>
    </div>
    
    <!-- 任务列表 -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">📥 下载任务 ({{ tasks.length }})</h3>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else-if="tasks.length === 0" class="empty-state">
        <div class="empty-state-icon">📭</div>
        <p>暂无下载任务</p>
      </div>
      
      <table v-else class="table">
        <thead>
          <tr>
            <th>任务名</th>
            <th>类型</th>
            <th>平台</th>
            <th>分辨率</th>
            <th>大小</th>
            <th>状态</th>
            <th>进度</th>
            <th>速度</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td class="task-title">{{ task.title || '未知标题' }}</td>
            <td>
              <span class="badge" :class="getTypeBadge(task.resource_type)">
                {{ task.resource_type || '视频' }}
              </span>
            </td>
            <td>{{ task.platform || '-' }}</td>
            <td>{{ task.resolution || '-' }}</td>
            <td>{{ formatSize(task.file_size) }}</td>
            <td>
              <span class="badge" :class="getStatusBadge(task.status)">
                {{ getStatusText(task.status) }}
              </span>
            </td>
            <td>
              <div class="progress-cell">
                <div class="progress" style="width: 80px;">
                  <div class="progress-bar" :style="{ width: task.progress + '%' }"></div>
                </div>
                <span>{{ task.progress || 0 }}%</span>
              </div>
            </td>
            <td>{{ task.speed || '-' }}</td>
            <td>{{ formatTime(task.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button v-if="task.status === 'failed'" class="btn btn-sm btn-primary" @click="retryTask(task)">
                  重试
                </button>
                <button class="btn btn-sm btn-warning" @click="renameTask(task)">
                  重命名
                </button>
                <button class="btn btn-sm btn-danger" @click="deleteTask(task)">
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { downloads } from '@/utils/api.js'

const tasks = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterPlatform = ref('')
const filterStatus = ref('')
const filterType = ref('')
let pollInterval = null

const downloadingCount = computed(() => tasks.value.filter(t => t.status === 'downloading').length)
const completedCount = computed(() => tasks.value.filter(t => t.status === 'completed').length)
const failedCount = computed(() => tasks.value.filter(t => t.status === 'failed').length)
const currentSpeed = computed(() => {
  const downloading = tasks.value.find(t => t.status === 'downloading')
  return downloading?.speed || '0 B/s'
})

function formatSize(bytes) {
  if (!bytes) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(2)} ${units[i]}`
}

function formatTime(time) {
  if (!time) return '-'
  const d = new Date(time)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

function getTypeBadge(type) {
  const map = { video: 'badge-info', audio: 'badge-success', image: 'badge-warning' }
  return map[type] || 'badge-info'
}

function getStatusBadge(status) {
  const map = { downloading: 'badge-info', completed: 'badge-success', failed: 'badge-danger', pending: 'badge-warning' }
  return map[status] || 'badge-warning'
}

function getStatusText(status) {
  const map = { downloading: '下载中', completed: '已完成', failed: '失败', pending: '等待中' }
  return map[status] || status
}

async function loadTasks() {
  loading.value = true
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPlatform.value) params.platform = filterPlatform.value
    if (filterType.value) params.resource_type = filterType.value
    if (searchQuery.value) params.search = searchQuery.value
    
    const data = await downloads.list(params)
    tasks.value = data.tasks || []
  } catch (error) {
    console.error('加载任务失败:', error)
  } finally {
    loading.value = false
  }
}

async function retryTask(task) {
  try {
    await downloads.start(task.url)
    await loadTasks()
  } catch (error) {
    alert(error.message)
  }
}

async function renameTask(task) {
  const newTitle = window.prompt('请输入新的下载名称：', task.title || '')
  if (!newTitle || !newTitle.trim()) return

  try {
    await downloads.rename(task.task_id, newTitle.trim())
    await loadTasks()
  } catch (error) {
    alert('重命名失败: ' + error.message)
  }
}

async function deleteTask(task) {
  if (!confirm('确定删除该任务？')) return
  try {
    await downloads.delete(task.task_id)
    await loadTasks()
  } catch (error) {
    alert('删除失败: ' + error.message)
  }
}

onMounted(() => {
  loadTasks()
  pollInterval = setInterval(loadTasks, 5000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.stat-mini {
  flex: 1;
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
  box-shadow: var(--shadow);
}

.stat-num {
  display: block;
  font-size: 28px;
  font-weight: 700;
}

.stat-num.downloading { color: var(--info); }
.stat-num.completed { color: var(--success); }
.stat-num.failed { color: var(--danger); }
.stat-num.speed { color: var(--warning); }

.stat-lbl {
  font-size: 13px;
  color: var(--text-secondary);
}

.filter-bar {
  display: flex;
  gap: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 14px;
}

.filter-select {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 14px;
  background: white;
  min-width: 120px;
}

.platform-card {
  margin-bottom: 20px;
}

.platform-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 16px;
}

.platform-tag {
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
}

.task-title {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.action-btns {
  display: flex;
  gap: 8px;
}
</style>

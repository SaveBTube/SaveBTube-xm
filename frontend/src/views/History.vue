<template>
  <div class="history-page">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-mini">
        <span class="stat-icon">📋</span>
        <span class="stat-num">{{ history.length }}</span>
        <span class="stat-lbl">显示记录</span>
      </div>
      <div class="stat-mini success">
        <span class="stat-icon">✅</span>
        <span class="stat-num">{{ successCount }}</span>
        <span class="stat-lbl">成功下载</span>
      </div>
      <div class="stat-mini failed">
        <span class="stat-icon">❌</span>
        <span class="stat-num">{{ failedCount }}</span>
        <span class="stat-lbl">失败记录</span>
      </div>
    </div>
    
    <!-- 筛选栏 -->
    <div class="filter-bar card">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="搜索标题或链接..." 
        class="search-input"
        @keyup.enter="loadHistory"
      />
      <select v-model="filterPlatform" class="filter-select" @change="loadHistory">
        <option value="">所有平台</option>
        <option value="YouTube">YouTube</option>
        <option value="Bilibili">Bilibili</option>
        <option value="Douyin">抖音</option>
        <option value="Kuaishou">快手</option>
        <option value="Xiaohongshu">小红书</option>
      </select>
      <select v-model="filterStatus" class="filter-select" @change="loadHistory">
        <option value="">所有状态</option>
        <option value="completed">已完成</option>
        <option value="failed">失败</option>
      </select>
      <select v-model="filterType" class="filter-select" @change="loadHistory">
        <option value="">所有类型</option>
        <option value="video">视频</option>
        <option value="audio">音频</option>
        <option value="image">图片</option>
      </select>
      <button class="btn btn-danger btn-sm" @click="clearAllHistory">🗑️ 清空历史</button>
    </div>
    
    <!-- 历史列表 -->
    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th @click="sortBy('title')" class="sortable">
              任务名 {{ sortField === 'title' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th>类型</th>
            <th @click="sortBy('platform')" class="sortable">
              平台 {{ sortField === 'platform' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th>分辨率</th>
            <th @click="sortBy('file_size')" class="sortable">
              大小 {{ sortField === 'file_size' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th @click="sortBy('status')" class="sortable">
              状态 {{ sortField === 'status' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th @click="sortBy('created_at')" class="sortable">
              下载时间 {{ sortField === 'created_at' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in sortedHistory" :key="item.id">
            <td class="task-title" :title="item.title">{{ item.title || '未知标题' }}</td>
            <td>
              <span class="badge" :class="getTypeBadge(item.resource_type)">
                {{ item.resource_type || '视频' }}
              </span>
            </td>
            <td>{{ item.platform || '-' }}</td>
            <td>{{ item.resolution || '-' }}</td>
            <td>{{ formatSize(item.file_size) }}</td>
            <td>
              <span class="badge" :class="getStatusBadge(item.status)">
                {{ getStatusText(item.status) }}
              </span>
            </td>
            <td>{{ formatTime(item.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button v-if="item.status === 'completed'" class="btn btn-sm btn-primary" @click="redownload(item)">
                  重新下载
                </button>
                <button class="btn btn-sm btn-gray" @click="shareItem(item)">
                  分享
                </button>
                <button class="btn btn-sm btn-danger" @click="deleteItem(item)">
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="history.length === 0">
            <td colspan="8" class="text-center text-muted" style="padding: 40px;">
              暂无下载历史
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { history as historyApi, downloads } from '@/utils/api.js'

const history = ref([])
const searchQuery = ref('')
let pollInterval = null
const filterPlatform = ref('')
const filterStatus = ref('')
const filterType = ref('')
const sortField = ref('created_at')
const sortOrder = ref('desc')

const successCount = computed(() => history.value.filter(h => h.status === 'completed').length)
const failedCount = computed(() => history.value.filter(h => h.status === 'failed').length)

const sortedHistory = computed(() => {
  const sorted = [...history.value]
  sorted.sort((a, b) => {
    let aVal = a[sortField.value] || ''
    let bVal = b[sortField.value] || ''
    
    if (sortField.value === 'file_size') {
      aVal = Number(aVal) || 0
      bVal = Number(bVal) || 0
    }
    
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
  return sorted
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
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function getTypeBadge(type) {
  const map = { video: 'badge-info', audio: 'badge-success', image: 'badge-warning' }
  return map[type] || 'badge-info'
}

function getStatusBadge(status) {
  const map = { completed: 'badge-success', failed: 'badge-danger' }
  return map[status] || 'badge-warning'
}

function getStatusText(status) {
  return status === 'completed' ? '已完成' : '失败'
}

function sortBy(field) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
}

async function loadHistory() {
  try {
    const params = { limit: 200 }
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPlatform.value) params.platform = filterPlatform.value
    if (filterType.value) params.resource_type = filterType.value
    if (searchQuery.value) params.search = searchQuery.value
    
    const data = await historyApi.list(params)
    history.value = data.history || []
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

async function redownload(item) {
  try {
    await downloads.start(item.url)
    alert('已重新创建下载任务')
    await loadHistory()
  } catch (error) {
    alert('重新下载失败: ' + error.message)
  }
}

function shareItem(item) {
  const shareUrl = item.url
  if (navigator.clipboard) {
    navigator.clipboard.writeText(shareUrl)
    alert('链接已复制到剪贴板')
  }
}

async function deleteItem(item) {
  if (!confirm('确定删除该历史记录？')) return
  try {
    await historyApi.delete([item.id])
    await loadHistory()
  } catch (error) {
    alert('删除失败: ' + error.message)
  }
}

async function clearAllHistory() {
  if (!confirm('⚠️ 危险操作！确定要清空所有下载历史吗？')) return
  try {
    await historyApi.clearAll()
    await loadHistory()
  } catch (error) {
    alert('清空失败: ' + error.message)
  }
}

onMounted(() => {
  loadHistory()
  pollInterval = setInterval(loadHistory, 5000)
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

.stat-icon {
  display: block;
  font-size: 24px;
  margin-bottom: 8px;
}

.stat-num {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-mini.success .stat-num { color: var(--success); }
.stat-mini.failed .stat-num { color: var(--danger); }

.stat-lbl {
  font-size: 13px;
  color: var(--text-secondary);
}

.filter-bar {
  display: flex;
  gap: 12px;
  padding: 16px;
  margin-bottom: 20px;
  align-items: center;
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
  min-width: 110px;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  color: var(--primary);
}

.task-title {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-btns {
  display: flex;
  gap: 6px;
}
</style>

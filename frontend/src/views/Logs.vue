<template>
  <div class="logs-page">
    <!-- 操作栏 -->
    <div class="action-bar card">
      <select v-model="logDate" class="filter-select" @change="loadLogs">
        <option v-for="date in availableDates" :key="date" :value="date">
          {{ date }}
        </option>
      </select>
      <select v-model="logLevel" class="filter-select" @change="loadLogs">
        <option value="">全部级别</option>
        <option value="INFO">INFO</option>
        <option value="WARNING">WARNING</option>
        <option value="ERROR">ERROR</option>
      </select>
      <button class="btn btn-gray" @click="loadLogs">🔄 刷新</button>
      <button class="btn btn-gray" @click="clearDisplay">🗑️ 清空显示</button>
    </div>
    
    <!-- 日志显示区 -->
    <div class="log-container card">
      <div class="log-header">
        <span class="log-title">📋 运行日志</span>
        <span class="log-count">{{ filteredLogs.length }} 条</span>
      </div>
      <div class="log-output" ref="logContainer">
        <div 
          v-for="(log, index) in filteredLogs" 
          :key="index" 
          class="log-line"
          :class="getLogClass(log)"
        >
          {{ log }}
        </div>
        <div v-if="filteredLogs.length === 0" class="empty-state">
          暂无日志记录
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { logs as logsApi } from '@/utils/api.js'

const allLogs = ref([])
const logDate = ref('')
const logLevel = ref('')
const availableDates = ref([])
const logContainer = ref(null)

const filteredLogs = computed(() => {
  if (!logLevel.value) return allLogs.value
  return allLogs.value.filter(log => log.includes(`[${logLevel.value}]`))
})

function getLogClass(log) {
  if (log.includes('[ERROR]')) return 'log-error'
  if (log.includes('[WARNING]')) return 'log-warning'
  if (log.includes('[INFO]')) return 'log-info'
  return ''
}

async function loadLogs() {
  try {
    const data = await logsApi.list({ date: logDate.value, limit: 500 })
    allLogs.value = data.logs || []
    
    // 更新可用日期
    const today = new Date().toISOString().slice(0, 10)
    if (!availableDates.value.includes(today)) {
      availableDates.value.unshift(today)
    }
    
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('加载日志失败:', error)
  }
}

function scrollToBottom() {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

function clearDisplay() {
  allLogs.value = []
}

onMounted(() => {
  // 初始化可用日期（最近7天）
  const dates = []
  for (let i = 0; i < 7; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    dates.push(d.toISOString().slice(0, 10))
  }
  availableDates.value = dates
  logDate.value = dates[0]
  
  loadLogs()
  
  // 每10秒自动刷新
  setInterval(loadLogs, 10000)
})
</script>

<style scoped>
.action-bar {
  display: flex;
  gap: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.filter-select {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 14px;
  background: white;
  min-width: 140px;
}

.log-container {
  background: #1e1e1e;
  border-radius: var(--radius);
  overflow: hidden;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #2d2d2d;
  border-bottom: 1px solid #3d3d3d;
}

.log-title {
  color: #e0e0e0;
  font-weight: 500;
}

.log-count {
  color: #888;
  font-size: 13px;
}

.log-output {
  height: calc(100vh - 300px);
  overflow-y: auto;
  padding: 12px 16px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.log-line {
  color: #d4d4d4;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-error { color: #f48771; }
.log-warning { color: #cca700; }
.log-info { color: #89d185; }
</style>

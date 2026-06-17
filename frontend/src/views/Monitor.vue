<template>
  <div class="monitor-page">
    <!-- 实时监控卡片 -->
    <div class="monitor-grid">
      <div class="monitor-card">
        <div class="monitor-header">
          <span class="monitor-icon">💻</span>
          <span class="monitor-title">CPU 使用率</span>
        </div>
        <div class="monitor-value">{{ stats.system?.cpu_percent || 0 }}%</div>
        <div class="monitor-bar">
          <div class="progress">
            <div class="progress-bar" :style="{ width: (stats.system?.cpu_percent || 0) + '%', background: getCpuColor(stats.system?.cpu_percent) }"></div>
          </div>
        </div>
        <div class="monitor-footer">
          <span>空闲: {{ 100 - (stats.system?.cpu_percent || 0) }}%</span>
        </div>
      </div>
      
      <div class="monitor-card">
        <div class="monitor-header">
          <span class="monitor-icon">🧠</span>
          <span class="monitor-title">内存占用</span>
        </div>
        <div class="monitor-value">{{ formatSize(stats.system?.memory_used || 0) }}</div>
        <div class="monitor-bar">
          <div class="progress">
            <div class="progress-bar" :style="{ width: (stats.system?.memory_percent || 0) + '%', background: '#8b5cf6' }"></div>
          </div>
        </div>
        <div class="monitor-footer">
          <span>{{ formatSize(stats.system?.memory_total || 0) }} 总量</span>
          <span>{{ formatSize(stats.system?.memory_total - stats.system?.memory_used) }} 可用</span>
        </div>
      </div>
      
      <div class="monitor-card">
        <div class="monitor-header">
          <span class="monitor-icon">💾</span>
          <span class="monitor-title">存储空间</span>
        </div>
        <div class="monitor-value">{{ formatSize(stats.system?.disk_used || 0) }}</div>
        <div class="monitor-bar">
          <div class="progress">
            <div class="progress-bar" :style="{ width: (stats.system?.disk_percent || 0) + '%', background: getDiskColor(stats.system?.disk_percent) }"></div>
          </div>
        </div>
        <div class="monitor-footer">
          <span>{{ formatSize(stats.system?.disk_total || 0) }} 总量</span>
          <span>{{ formatSize(stats.system?.disk_total - stats.system?.disk_used) }} 可用</span>
        </div>
      </div>
      
      <div class="monitor-card">
        <div class="monitor-header">
          <span class="monitor-icon">🌐</span>
          <span class="monitor-title">实时带宽</span>
        </div>
        <div class="monitor-value">{{ (stats.system?.network_up_mb || 0).toFixed(2) }} MB/s</div>
        <div class="monitor-bar">
          <div class="progress">
            <div class="progress-bar" :style="{ width: Math.min((stats.system?.network_up_mb || 0) * 10, 100) + '%', background: '#10b981' }"></div>
          </div>
        </div>
        <div class="monitor-footer">
          <span>↑ {{ (stats.system?.network_up_mb || 0).toFixed(2) }} MB/s 上传</span>
          <span>↓ {{ (stats.system?.network_down_mb || 0).toFixed(2) }} MB/s 下载</span>
        </div>
      </div>
    </div>
    
    <!-- 下载统计 -->
    <div class="card mt-3">
      <div class="card-header">
        <h3 class="card-title">📊 下载统计</h3>
      </div>
      <div class="stats-detail">
        <div class="stat-row">
          <span class="stat-label">总下载次数</span>
          <span class="stat-value">{{ stats.overview?.total_tasks || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">成功下载</span>
          <span class="stat-value text-success">{{ stats.overview?.success_count || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">失败记录</span>
          <span class="stat-value text-danger">{{ stats.overview?.fail_count || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">当前下载中</span>
          <span class="stat-value text-info">{{ stats.overview?.downloading_count || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">总下载容量</span>
          <span class="stat-value">{{ formatSize(stats.overview?.total_size || 0) }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">视频数量</span>
          <span class="stat-value">{{ stats.overview?.video_count || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">音频数量</span>
          <span class="stat-value">{{ stats.overview?.audio_count || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">图片数量</span>
          <span class="stat-value">{{ stats.overview?.image_count || 0 }}</span>
        </div>
      </div>
    </div>
    
    <!-- 平台分布 -->
    <div class="card mt-3">
      <div class="card-header">
        <h3 class="card-title">📈 平台分布</h3>
      </div>
      <div class="platform-chart">
        <div v-for="(item, index) in stats.platform_dist" :key="index" class="platform-row">
          <div class="platform-info">
            <span class="platform-name">{{ item.platform }}</span>
            <span class="platform-percent">{{ getPlatformPercent(item.count) }}%</span>
          </div>
          <div class="platform-bar">
            <div class="platform-fill" :style="{ width: getPlatformPercent(item.count) + '%' }"></div>
          </div>
          <span class="platform-count">{{ item.count }} 次</span>
        </div>
        <div v-if="!stats.platform_dist?.length" class="empty-state">
          暂无数据
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { statistics } from '@/utils/api.js'

const stats = ref({})
let pollInterval = null

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(2)} ${units[i]}`
}

function getCpuColor(percent) {
  if (percent > 80) return '#ef4444'
  if (percent > 60) return '#f59e0b'
  return '#22c55e'
}

function getDiskColor(percent) {
  if (percent > 90) return '#ef4444'
  if (percent > 70) return '#f59e0b'
  return '#3b82f6'
}

function getPlatformPercent(count) {
  const total = stats.value.platform_dist?.reduce((sum, p) => sum + p.count, 0) || 1
  return ((count / total) * 100).toFixed(1)
}

async function loadStats() {
  try {
    stats.value = await statistics.get(30)
  } catch (error) {
    console.error('加载监控数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
  pollInterval = setInterval(loadStats, 5000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.monitor-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .monitor-grid { grid-template-columns: 1fr; }
}

.monitor-card {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.monitor-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.monitor-icon { font-size: 20px; }
.monitor-title { font-size: 14px; color: var(--text-secondary); }

.monitor-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.monitor-bar { margin-bottom: 12px; }
.monitor-bar .progress { height: 10px; border-radius: 5px; }

.monitor-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-muted);
}

.stats-detail {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .stats-detail { grid-template-columns: repeat(2, 1fr); }
}

.stat-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: var(--radius);
}

.stat-label { font-size: 13px; color: var(--text-secondary); }
.stat-value { font-size: 20px; font-weight: 600; }

.platform-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.platform-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.platform-info {
  width: 120px;
  display: flex;
  justify-content: space-between;
}

.platform-name { font-size: 14px; font-weight: 500; }
.platform-percent { font-size: 13px; color: var(--text-secondary); }

.platform-bar {
  flex: 1;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.platform-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 4px;
  transition: width 0.3s;
}

.platform-count {
  width: 80px;
  text-align: right;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>

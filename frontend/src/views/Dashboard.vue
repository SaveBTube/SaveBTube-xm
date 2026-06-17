<template>
  <div class="dashboard">
    <!-- 快速下载栏 -->
    <div class="quick-download-bar card">
      <input 
        v-model="quickUrl" 
        type="text" 
        placeholder="粘贴 YouTube、X、QQ音乐、小红书、微博 等链接..."
        class="quick-input"
        @keyup.enter="quickDownload"
      />
      <select v-model="downloadQuality" class="quality-select">
        <option value="best">最佳质量</option>
        <option value="1080p">1080p</option>
        <option value="720p">720p</option>
        <option value="audio">仅音频</option>
        <option value="mp3">MP3</option>
        <option value="m4a">M4A</option>
        <option value="mp4">MP4</option>
        <option value="webm">WEBM</option>
        <option value="image">图片</option>
        <option value="jpg">JPG</option>
        <option value="png">PNG</option>
      </select>
      <button class="btn btn-primary" @click="quickDownload" :disabled="!quickUrl">
        ⬇️ 立即下载
      </button>
    </div>

    <!-- 支持平台展示 -->
    <div class="platform-card card">
      <div class="platform-header">
        <h3 class="card-title">支持平台</h3>
        <p class="platform-description">支持 YouTube、X、QQ音乐、小红书、微博、抖音、Bilibili、快手 等平台</p>
      </div>
      <div class="platform-list">
        <div class="platform-badge" v-for="platform in platforms" :key="platform.name">
          <span class="platform-logo">{{ platform.icon }}</span>
          <span class="platform-name">{{ platform.name }}</span>
        </div>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #dbeafe;">
          <span>📥</span>
        </div>
        <div class="stat-value">{{ stats.overview?.total_tasks || 0 }}</div>
        <div class="stat-label">总下载次数</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: #dcfce7;">
          <span>✅</span>
        </div>
        <div class="stat-value text-success">{{ stats.overview?.success_count || 0 }}</div>
        <div class="stat-label">成功下载</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: #fee2e2;">
          <span>❌</span>
        </div>
        <div class="stat-value text-danger">{{ stats.overview?.fail_count || 0 }}</div>
        <div class="stat-label">失败记录</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef3c7;">
          <span>📊</span>
        </div>
        <div class="stat-value">{{ formatSize(stats.overview?.total_size || 0) }}</div>
        <div class="stat-label">累计下载容量</div>
      </div>
    </div>
    
    <!-- 系统资源 -->
    <div class="section-grid">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">💻 系统资源</h3>
        </div>
        <div class="resource-list">
          <div class="resource-item">
            <span class="resource-label">CPU 使用率</span>
            <div class="resource-bar">
              <div class="progress">
                <div class="progress-bar" :style="{ width: stats.system?.cpu_percent + '%' }"></div>
              </div>
              <span class="resource-value">{{ stats.system?.cpu_percent || 0 }}%</span>
            </div>
          </div>
          <div class="resource-item">
            <span class="resource-label">内存占用</span>
            <div class="resource-bar">
              <div class="progress">
                <div class="progress-bar" :style="{ width: stats.system?.memory_percent + '%' }"></div>
              </div>
              <span class="resource-value">{{ stats.system?.memory_percent || 0 }}% ({{ formatSize(stats.system?.memory_used || 0) }})</span>
            </div>
          </div>
          <div class="resource-item">
            <span class="resource-label">存储空间</span>
            <div class="resource-bar">
              <div class="progress">
                <div class="progress-bar" :style="{ width: stats.system?.disk_percent + '%', background: '#f59e0b' }"></div>
              </div>
              <span class="resource-value">{{ stats.system?.disk_percent || 0 }}% ({{ formatSize(stats.system?.disk_used || 0) }} / {{ formatSize(stats.system?.disk_total || 0) }})</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">🎬 内容统计</h3>
        </div>
        <div class="content-stats">
          <div class="content-stat">
            <span class="content-icon">🎥</span>
            <span class="content-count">{{ stats.overview?.video_count || 0 }}</span>
            <span class="content-label">视频</span>
          </div>
          <div class="content-stat">
            <span class="content-icon">🎵</span>
            <span class="content-count">{{ stats.overview?.audio_count || 0 }}</span>
            <span class="content-label">音乐</span>
          </div>
          <div class="content-stat">
            <span class="content-icon">🖼️</span>
            <span class="content-count">{{ stats.overview?.image_count || 0 }}</span>
            <span class="content-label">图片</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 趋势图表 -->
    <div class="charts-grid">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">📈 7天下载趋势</h3>
        </div>
        <div class="chart-container">
          <Line v-if="chartData7d" :data="chartData7d" :options="chartOptions" />
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">📊 平台分布</h3>
        </div>
        <div class="platform-dist">
          <div 
            v-for="(item, index) in stats.platform_dist?.slice(0, 6)" 
            :key="index"
            class="platform-item"
          >
            <div class="platform-info">
              <span class="platform-name">{{ item.platform }}</span>
              <span class="platform-count">{{ item.count }} 次</span>
            </div>
            <div class="platform-bar">
              <div 
                class="platform-fill" 
                :style="{ width: getPlatformPercent(item.count) + '%' }"
              ></div>
            </div>
          </div>
          <div v-if="!stats.platform_dist?.length" class="empty-state">
            暂无数据
          </div>
        </div>
      </div>
    </div>
    
    <!-- 用户排行 -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">🏆 用户下载排行</h3>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>排名</th>
            <th>用户名</th>
            <th>下载次数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in stats.user_ranking" :key="index">
            <td>
              <span class="rank-badge" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
            </td>
            <td>{{ user.username }}</td>
            <td>{{ user.download_count }} 次</td>
          </tr>
          <tr v-if="!stats.user_ranking?.length">
            <td colspan="3" class="text-center text-muted">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 下载消息提示 -->
    <div v-if="downloadMsg" class="toast" :class="toastClass">
      {{ downloadMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { statistics, downloads } from '@/utils/api.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const quickUrl = ref('')
const downloadQuality = ref('best')
const downloadMsg = ref('')
const toastClass = ref('')
const stats = ref({})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: { beginAtZero: true }
  }
}

const platforms = ref([
  { name: 'YouTube', icon: '▶️' },
  { name: 'X', icon: '🐦' },
  { name: 'QQ音乐', icon: '🎧' },
  { name: '小红书', icon: '📸' },
  { name: '微博', icon: '💬' },
  { name: '抖音', icon: '🎵' },
  { name: 'Bilibili', icon: '🎥' },
  { name: '快手', icon: '📹' }
])

const chartData7d = computed(() => {
  const trend = stats.value.trend || []
  return {
    labels: trend.map(t => t.date?.slice(5) || ''),
    datasets: [{
      label: '下载次数',
      data: trend.map(t => t.total_downloads || 0),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.4
    }]
  }
})

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

function getPlatformPercent(count) {
  const max = stats.value.platform_dist?.[0]?.count || 1
  return (count / max) * 100
}

async function quickDownload() {
  if (!quickUrl.value) return
  
  try {
    await downloads.start(quickUrl.value, downloadQuality.value)
    downloadMsg.value = '✅ 下载任务已创建！'
    toastClass.value = 'toast-success'
    quickUrl.value = ''
    setTimeout(() => { downloadMsg.value = '' }, 3000)
  } catch (error) {
    downloadMsg.value = '❌ ' + error.message
    toastClass.value = 'toast-error'
    setTimeout(() => { downloadMsg.value = '' }, 3000)
  }
}

async function loadStats() {
  try {
    stats.value = await statistics.get(30)
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

onMounted(() => {
  loadStats()
  // 每30秒刷新一次
  setInterval(loadStats, 30000)
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.quick-download-bar {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.quick-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 14px;
  outline: none;
}

.quick-input:focus {
  border-color: var(--primary);
}

.quality-select {
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 14px;
  background: white;
}

.platform-card {
  margin-bottom: 24px;
  padding: 20px;
}

.platform-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.platform-description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.platform-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.platform-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: var(--radius);
  background: #f8fafc;
  border: 1px solid rgba(148,163,184,.2);
  min-width: 140px;
  animation: float 6s ease-in-out infinite;
}

.platform-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #eff6ff;
  font-size: 18px;
  animation: rotate 8s linear infinite;
}

.platform-name {
  font-weight: 600;
  color: var(--text-primary);
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 1024px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

.section-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .section-grid { grid-template-columns: 1fr; }
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.resource-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.resource-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.resource-bar .progress {
  flex: 1;
}

.resource-value {
  font-size: 13px;
  color: var(--text-primary);
  min-width: 120px;
}

.content-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.content-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.content-icon {
  font-size: 32px;
}

.content-count {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.content-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.charts-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 1024px) {
  .charts-grid { grid-template-columns: 1fr; }
}

.chart-container {
  height: 250px;
}

.platform-dist {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.platform-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.platform-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.platform-name {
  color: var(--text-primary);
  font-weight: 500;
}

.platform-count {
  color: var(--text-secondary);
}

.platform-bar {
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

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 600;
  background: var(--bg-primary);
}

.rank-1 { background: #fef3c7; color: #92400e; }
.rank-2 { background: #e2e8f0; color: #475569; }
.rank-3 { background: #fed7aa; color: #9a3412; }

.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  box-shadow: var(--shadow-lg);
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

.toast-success {
  background: #22c55e;
  color: white;
}

.toast-error {
  background: #ef4444;
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>

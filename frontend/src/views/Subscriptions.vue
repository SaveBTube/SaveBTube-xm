<template>
  <!-- 保持模板部分不变 -->
  <div class="subscriptions-page">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-mini">
        <span class="stat-icon">📡</span>
        <span class="stat-num">{{ allSubscriptions.length }}</span>
        <span class="stat-lbl">总订阅</span>
      </div>
      <div class="stat-mini success">
        <span class="stat-icon">✅</span>
        <span class="stat-num">{{ activeCount }}</span>
        <span class="stat-lbl">活跃订阅</span>
      </div>
      <div class="stat-mini warning">
        <span class="stat-icon">⏸️</span>
        <span class="stat-num">{{ pausedCount }}</span>
        <span class="stat-lbl">已暂停</span>
      </div>
      <div class="stat-mini info">
        <span class="stat-icon">⬇️</span>
        <span class="stat-num">{{ totalDownloads }}</span>
        <span class="stat-lbl">总下载数</span>
      </div>
    </div>
    
    <!-- 操作栏 -->
    <div class="action-bar card">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="搜索频道名称或链接..." 
        class="search-input"
      />
      <select v-model="filterPlatform" class="filter-select" @change="loadSubscriptions">
        <option value="">所有平台</option>
        <option value="YouTube">YouTube</option>
        <option value="Bilibili">Bilibili</option>
        <option value="Douyin">抖音</option>
      </select>
      <button class="btn btn-primary" @click="showAddModal = true">➕ 添加订阅</button>
    </div>
    
    <!-- 订阅列表 -->
    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>频道名称</th>
            <th>平台</th>
            <th>轮询间隔</th>
            <th>上次检查</th>
            <th>已下载</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sub in filteredSubscriptions" :key="sub.id">
            <td>
              <div class="channel-info">
                <span class="channel-name">{{ sub.channel_name || '未知频道' }}</span>
                <span class="channel-url">{{ sub.channel_url }}</span>
              </div>
            </td>
            <td>{{ sub.platform }}</td>
            <td>{{ formatInterval(sub.poll_interval) }}</td>
            <td>{{ formatTime(sub.last_check) }}</td>
            <td>{{ sub.total_downloads }} 个</td>
            <td>
              <span class="badge" :class="sub.status === 'active' ? 'badge-success' : 'badge-warning'">
                {{ sub.status === 'active' ? '活跃' : '已暂停' }}
              </span>
            </td>
            <td>
              <div class="action-btns">
                <button 
                  class="btn btn-sm" 
                  :class="sub.status === 'active' ? 'btn-warning' : 'btn-success'"
                  @click="toggleStatus(sub)"
                >
                  {{ sub.status === 'active' ? '暂停' : '恢复' }}
                </button>
                <button class="btn btn-sm btn-danger" @click="deleteSub(sub)">
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="allSubscriptions.length === 0">
            <td colspan="7" class="text-center text-muted" style="padding: 40px;">
              暂无订阅
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 添加订阅弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">添加订阅</h3>
          <button class="btn btn-gray btn-sm" @click="showAddModal = false">✕</button>
        </div>
        <form @submit.prevent="addSubscription">
          <div class="form-group">
            <label>订阅链接</label>
            <input v-model="newSub.url" type="text" class="input" placeholder="粘贴频道/UP主链接" required />
          </div>
          <div class="form-group">
            <label>平台</label>
            <select v-model="newSub.platform" class="input" required>
              <option value="YouTube">YouTube</option>
              <option value="Bilibili">Bilibili</option>
              <option value="Douyin">抖音</option>
            </select>
          </div>
          <div class="form-group">
            <label>频道名称（可选）</label>
            <input v-model="newSub.channel_name" type="text" class="input" placeholder="给订阅起个名字" />
          </div>
          <div class="form-group">
            <label>轮询间隔</label>
            <select v-model="newSub.poll_interval" class="input">
              <option :value="1800">30分钟</option>
              <option :value="3600">1小时</option>
              <option :value="7200">2小时</option>
              <option :value="86400">每天</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-gray" @click="showAddModal = false">取消</button>
            <button type="submit" class="btn btn-primary">添加</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { subscriptions as subscriptionApi } from '@/utils/api.js'

// 1. 重命名数据变量，避免与导入的 api 对象冲突
const subscriptionsData = ref([])
const searchQuery = ref('')
const filterPlatform = ref('')
const showAddModal = ref(false)
const newSub = ref({ url: '', platform: 'YouTube', channel_name: '', poll_interval: 3600 })

// 2. 使用重命名后的变量
const allSubscriptions = computed(() => subscriptionsData.value)
const activeCount = computed(() => subscriptionsData.value.filter(s => s.status === 'active').length)
const pausedCount = computed(() => subscriptionsData.value.filter(s => s.status === 'paused').length)
const totalDownloads = computed(() => subscriptionsData.value.reduce((sum, s) => sum + (s.total_downloads || 0), 0))

const filteredSubscriptions = computed(() => {
  return subscriptionsData.value.filter(sub => {
    const matchSearch = !searchQuery.value || 
      (sub.channel_name && sub.channel_name.includes(searchQuery.value)) ||
      (sub.channel_url && sub.channel_url.includes(searchQuery.value))
    const matchPlatform = !filterPlatform.value || sub.platform === filterPlatform.value
    return matchSearch && matchPlatform
  })
})

function formatInterval(seconds) {
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时`
  return '每天'
}

function formatTime(time) {
  if (!time) return '从未'
  const d = new Date(time)
  return `${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function loadSubscriptions() {
  try {
    // 3. 使用重命名后的 api 导入
    const data = await subscriptionApi.list({})
    subscriptionsData.value = data.subscriptions || []
  } catch (error) {
    console.error('加载订阅失败:', error)
  }
}

async function addSubscription() {
  try {
    await subscriptionApi.add(
      newSub.value.url,
      newSub.value.platform,
      newSub.value.channel_name,
      newSub.value.poll_interval
    )
    showAddModal.value = false
    newSub.value = { url: '', platform: 'YouTube', channel_name: '', poll_interval: 3600 }
    await loadSubscriptions()
  } catch (error) {
    alert('添加失败: ' + error.message)
  }
}

async function toggleStatus(sub) {
  try {
    const newStatus = sub.status === 'active' ? 'paused' : 'active'
    // 注意：这里假设 api.update 的参数是 (id, status)
    // 请根据你的实际 api 方法签名调整
    await subscriptionApi.update(sub.sub_id, newStatus)
    await loadSubscriptions()
  } catch (error) {
    alert('更新失败: ' + error.message)
  }
}

async function deleteSub(sub) {
  if (!confirm(`确定删除订阅 "${sub.channel_name || sub.channel_url}" 吗？`)) return
  try {
    await subscriptionApi.delete(sub.sub_id)
    await loadSubscriptions()
  } catch (error) {
    alert('删除失败: ' + error.message)
  }
}

onMounted(() => {
  loadSubscriptions()
})
</script>

<style scoped>
/* 样式部分保持不变 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-mini {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
  box-shadow: var(--shadow);
}

.stat-icon { font-size: 24px; display: block; margin-bottom: 8px; }
.stat-num { display: block; font-size: 28px; font-weight: 700; }
.stat-mini.success .stat-num { color: var(--success); }
.stat-mini.warning .stat-num { color: var(--warning); }
.stat-mini.info .stat-num { color: var(--info); }
.stat-lbl { font-size: 13px; color: var(--text-secondary); }

.action-bar {
  display: flex;
  gap: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.search-input { flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius); font-size: 14px; }
.filter-select { padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius); font-size: 14px; background: white; min-width: 120px; }

.channel-info { display: flex; flex-direction: column; gap: 4px; }
.channel-name { font-weight: 500; }
.channel-url { font-size: 12px; color: var(--text-muted); max-width: 200px; overflow: hidden; text-overflow: ellipsis; }

.action-btns { display: flex; gap: 6px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 14px; font-weight: 500; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
</style>
/**
 * API 工具函数
 */

const API_BASE = '/api'

function getAuthHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
}

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers
    }
  })
  
  if (response.status === 403) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('未授权')
  }
  
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.detail || '请求失败')
  }
  return data
}

// 认证相关
export const auth = {
  login: (username, password) => request('/admin/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  }),
  
  register: (username, password, inviteCode) => request('/admin/register', {
    method: 'POST',
    body: JSON.stringify({ username, password, invite_code: inviteCode })
  }),
  
  getCurrentUser: () => request('/admin/me'),
  
  changePassword: (oldPassword, newPassword) => request('/admin/password', {
    method: 'POST',
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
  }),
  
  uploadAvatar: (avatarData) => {
    const formData = new FormData()
    formData.append('avatar', avatarData)
    return fetch(`${API_BASE}/admin/avatar`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: formData
    })
  }
}

// 下载相关
export const downloads = {
  start: (url, quality = 'best') => request('/download', {
    method: 'POST',
    body: JSON.stringify({ url, quality })
  }),
  quick: (url, quality = 'best') => request('/quick-download', {
    method: 'POST',
    body: JSON.stringify({ url, quality })
  }),
  
  list: (params = {}) => {
    const searchParams = new URLSearchParams(params)
    return request(`/downloads?${searchParams}`)
  },
  
  progress: (taskId) => request(`/progress/${taskId}`),

  rename: (taskId, newTitle) => request(`/tasks/${taskId}/rename`, {
    method: 'POST',
    body: JSON.stringify({ new_title: newTitle })
  }),

  delete: (taskId) => request(`/tasks/${taskId}`, { method: 'DELETE' })
}

// 历史记录
export const history = {
  list: (params = {}) => {
    const searchParams = new URLSearchParams(params)
    return request(`/history?${searchParams}`)
  },
  
  delete: (ids) => request('/history', {
    method: 'DELETE',
    body: JSON.stringify({ ids })
  }),
  
  clearAll: () => request('/history/all', { method: 'DELETE' })
}

// 文件管理
export const files = {
  list: () => request('/files'),
  
  download: async (filename) => {
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE}/files/${encodeURIComponent(filename)}?token=${token}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.detail || '下载失败')
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)
    }, 100)
  },
  
  stream: (filename) => {
    const token = localStorage.getItem('token')
    window.open(`${API_BASE}/files/stream/${encodeURIComponent(filename)}?token=${token}`)
  },
  delete: (filename) => request(`/files/${encodeURIComponent(filename)}`, {
    method: 'DELETE'
  }),
  
  rename: (oldName, newName) => request('/files/rename', {
    method: 'POST',
    body: JSON.stringify({ old_name: oldName, new_name: newName })
  })
}

// 订阅管理
export const subscriptions = {
  list: (params = {}) => {
    const searchParams = new URLSearchParams(params)
    return request(`/subscriptions?${searchParams}`)
  },
  
  add: (url, platform, channelName, pollInterval) => request('/subscriptions', {
    method: 'POST',
    body: JSON.stringify({ url, platform, channel_name: channelName, poll_interval: pollInterval })
  }),
  
  update: (subId, status) => request(`/subscriptions/${subId}`, {
    method: 'PUT',
    body: JSON.stringify({ status })
  }),
  
  delete: (subId) => request(`/subscriptions/${subId}`, { method: 'DELETE' })
}

// 统计
export const statistics = {
  get: (days = 30) => request(`/statistics?days=${days}`)
}

export const settings = {
  get: () => request('/settings'),
  save: (data) => request('/settings', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  savePlatform: (data) => {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未授权，请先登录')
    }
    return fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    }).then(async res => {
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: '保存失败' }))
        if (res.status === 401) {
          localStorage.removeItem('token')
          window.location.href = '/login'
          throw new Error('未授权，请先登录')
        }
        throw new Error(error.detail || '保存失败')
      }
      return res.json()
    })
  }
}

// 日志
export const logs = {
  list: (params = {}) => {
    const searchParams = new URLSearchParams(params)
    return request(`/logs?${searchParams}`)
  }
}

// 用户管理
export const users = {
  list: () => request('/admin/users'),
  create: (username, password, role, isActive) => request('/admin/users', {
    method: 'POST',
    body: JSON.stringify({ username, password, role, is_active: isActive ? 1 : 0 })
  }),
  update: (userId, data) => request(`/admin/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  delete: (userId) => request(`/admin/users/${userId}`, { method: 'DELETE' })
}

// API密钥
export const apiKeys = {
  list: () => request('/admin/api-keys'),
  
  create: (note) => request('/admin/api-keys', {
    method: 'POST',
    body: JSON.stringify({ note })
  }),
  
  toggle: (keyId, status) => request(`/admin/api-keys/${keyId}/status?status=${status}`, {
    method: 'PUT'
  }),
  
  delete: (keyId) => request(`/admin/api-keys/${keyId}`, { method: 'DELETE' })
}

// 邀请码
export const inviteCodes = {
  list: () => request('/admin/invite-codes'),
  
  create: () => request('/admin/invite-codes', { method: 'POST' })
}

// 插件管理
export const plugin = {
  info: () => request('/admin/plugin/info'),
  
  download: () => {
    const token = localStorage.getItem('token')
    return fetch(`${API_BASE}/admin/plugin/download`, {
      headers: { 'Authorization': `Bearer ${token}` }
    }).then(async res => {
      if (!res.ok) {
        let detail = '下载失败'
        try {
          const data = await res.json()
          detail = data.detail || detail
        } catch (_) {}
        throw new Error(detail)
      }
      return res.blob()
    })
  }
}

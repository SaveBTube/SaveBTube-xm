import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/api'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref({})
  const loading = ref(false)

  async function fetchSettings() {
    loading.value = true
    try {
      const data = await api.get('/api/settings')
      settings.value = data
    } finally {
      loading.value = false
    }
  }

  async function saveSettings(data) {
    await api.post('/api/settings', data)
    settings.value = { ...settings.value, ...data }
  }

  async function testProxy(proxyUrl) {
    return await api.post('/api/settings/test-proxy', { proxy_url: proxyUrl })
  }

  return { settings, loading, fetchSettings, saveSettings, testProxy }
})

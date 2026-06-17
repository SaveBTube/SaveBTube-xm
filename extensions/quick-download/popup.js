// Bosco Tsang 快速下载插件 - 交互逻辑 v1.2.0
// 存储键名
const STORAGE_KEY = 'bosco_quick_download_settings'

// ==================== 存储抽象层 ===================
// Chrome 扩展中 localStorage 不可靠，统一使用 chrome.storage.local

function storageGet(key) {
  return new Promise((resolve) => {
    chrome.storage.local.get([key], (result) => {
      resolve(result[key] || null)
    })
  })
}

function storageSet(key, value) {
  return new Promise((resolve) => {
    chrome.storage.local.set({ [key]: value }, () => resolve())
  })
}

// ==================== UI 引用 ===================

const serverUrlInput = document.getElementById('serverUrl')
const apiKeyInput = document.getElementById('apiKey')
const downloadUrlInput = document.getElementById('downloadUrl')
const qualitySelect = document.getElementById('quality')
const downloadBtn = document.getElementById('downloadBtn')
const messageBox = document.getElementById('message')
const toggleKeyBtn = document.getElementById('toggleKey')
const openSettingsBtn = document.getElementById('openSettings')
const saveBtn = document.getElementById('saveBtn')

// ==================== 消息提示 ===================

function setMessage(text, type = 'info') {
  messageBox.textContent = text
  messageBox.className = 'message ' + type
  if (type !== 'info' || !text.includes('正在')) {
    clearTimeout(setMessage._timer)
    setMessage._timer = setTimeout(() => {
      messageBox.textContent = ''
      messageBox.className = 'message'
    }, 4000)
  }
}

function clearMessage() {
  messageBox.textContent = ''
  messageBox.className = 'message'
}

// ==================== 设置持久化 ===================

async function loadSettings() {
  try {
    const data = await storageGet(STORAGE_KEY)
    if (!data) return
    if (data.serverUrl) serverUrlInput.value = data.serverUrl
    if (data.apiKey) apiKeyInput.value = data.apiKey
    if (data.quality) qualitySelect.value = data.quality
    updateSaveStatus(true)
  } catch (e) {
    console.warn('读取设置失败', e)
  }
}

async function saveSettings() {
  const data = {
    serverUrl: serverUrlInput.value.trim(),
    apiKey: apiKeyInput.value.trim(),
    quality: qualitySelect.value,
    savedAt: Date.now()
  }
  try {
    await storageSet(STORAGE_KEY, data)
    updateSaveStatus(true)
    return true
  } catch (e) {
    console.error('保存设置失败', e)
    updateSaveStatus(false)
    return false
  }
}

function updateSaveStatus(isOk) {
  const el = document.getElementById('saveStatus')
  if (!el) return
  if (isOk) {
    storageGet(STORAGE_KEY).then(d => {
      if (d && d.savedAt) {
        const t = new Date(d.savedAt)
        el.textContent = '已保存 ' + t.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
        el.className = 'save-status saved'
      }
    })
  } else {
    el.textContent = '未保存'
    el.className = 'save-status unsaved'
  }
}

// ==================== 密钥显示/隐藏 ===================

let keyVisible = false
if (toggleKeyBtn) {
  toggleKeyBtn.addEventListener('click', () => {
    keyVisible = !keyVisible
    apiKeyInput.type = keyVisible ? 'text' : 'password'
    toggleKeyBtn.textContent = keyVisible ? '🙈' : '👁'
  })
}

// ==================== 打开管理后台 ===================

if (openSettingsBtn) {
  openSettingsBtn.addEventListener('click', () => {
    const url = (serverUrlInput.value || '').trim().replace(/\/$/, '')
    if (url) {
      chrome.tabs.create({ url })
    } else {
      setMessage('请先填写服务地址', 'error')
    }
  })
}

// ==================== 快速下载 ===================

async function quickDownload() {
  clearMessage()
  const serverUrl = serverUrlInput.value.trim().replace(/\/$/, '')
  const apiKey = apiKeyInput.value.trim()
  const url = downloadUrlInput.value.trim()
  const quality = qualitySelect.value

  if (!serverUrl || !apiKey || !url) {
    setMessage('请填写服务地址、API Key 和下载链接', 'error')
    return
  }

  await saveSettings()

  setMessage('⏳ 正在提交任务...', 'info')
  downloadBtn.disabled = true
  const btnText = downloadBtn.querySelector('.btn-text')
  if (btnText) btnText.textContent = '提交中...'

  try {
    const response = await fetch(`${serverUrl}/api/quick-download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey
      },
      body: JSON.stringify({ url, quality })
    })

    if (!response.ok) {
      let detail = `请求失败：${response.status}`
      try {
        const data = await response.json()
        detail = data.detail || detail
      } catch (_) { /* ignore */ }
      throw new Error(detail)
    }

    const data = await response.json()
    setMessage('✅ 任务已提交！ID: ' + data.task_id, 'success')

    downloadBtn.classList.add('success-flash')
    setTimeout(() => {
      downloadBtn.classList.remove('success-flash')
      downloadBtn.disabled = false
      if (btnText) btnText.textContent = '快速下载'
    }, 1500)

  } catch (error) {
    setMessage('❌ ' + (error.message || '快速下载失败'), 'error')
    downloadBtn.disabled = false
    if (btnText) btnText.textContent = '快速下载'
  }
}

// ==================== 填充当前 URL ===================

function tryGetCurrentTabUrl(callback) {
  if (!chrome || !chrome.tabs || !chrome.tabs.query) {
    callback(null)
    return
  }
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs && tabs.length > 0 && tabs[0].url) {
      callback(tabs[0].url)
    } else {
      callback(null)
    }
  })
}

function populateCurrentUrl() {
  if (chrome && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(['quickDownloadPreloadUrl'], ({ quickDownloadPreloadUrl }) => {
      if (quickDownloadPreloadUrl) {
        downloadUrlInput.value = quickDownloadPreloadUrl
        chrome.storage.local.remove('quickDownloadPreloadUrl')
        return
      }
      tryGetCurrentTabUrl((url) => {
        if (url) downloadUrlInput.value = url
      })
    })
  } else {
    tryGetCurrentTabUrl((url) => {
      if (url) downloadUrlInput.value = url
    })
  }
}

// ==================== 事件绑定 ===================

document.getElementById('fillCurrentUrl').addEventListener('click', () => {
  tryGetCurrentTabUrl((url) => {
    if (url) {
      downloadUrlInput.value = url
      clearMessage()
    } else {
      setMessage('无法获取当前标签页 URL', 'error')
    }
  })
})

if (saveBtn) {
  saveBtn.addEventListener('click', async () => {
    const ok = await saveSettings()
    if (ok) {
      setMessage('✅ 设置已保存', 'success')
    } else {
      setMessage('❌ 保存失败', 'error')
    }
  })
}

let saveTimer = null
function debounceSave() {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => saveSettings(), 600)
}

;[
  serverUrlInput,
  apiKeyInput,
  qualitySelect
].forEach((el) => {
  if (!el) return
  el.addEventListener('input', debounceSave)
  el.addEventListener('change', () => saveSettings())
})

downloadBtn.addEventListener('click', quickDownload)

// ==================== 初始化 ===================

loadSettings()
populateCurrentUrl()

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'bosco_quick_download_page',
    title: 'Bosco Tsang 快速下载当前页面',
    contexts: ['page']
  })

  chrome.contextMenus.create({
    id: 'bosco_quick_download_link',
    title: 'Bosco Tsang 快速下载链接',
    contexts: ['link']
  })
})

chrome.contextMenus.onClicked.addListener((info, tab) => {
  const url = info.linkUrl || info.pageUrl || ''
  if (!url) {
    return
  }
  chrome.storage.local.set({ quickDownloadPreloadUrl: url }, () => {
    if (chrome.action && chrome.action.openPopup) {
      chrome.action.openPopup()
    }
  })
})

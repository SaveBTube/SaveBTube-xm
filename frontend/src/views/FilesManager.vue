<template>
  <div class="files-manager">
    <div class="files-card">
      <div class="files-card-header">
        <div>
          <h3>文件管理</h3>
          <p class="subtitle">浏览已下载内容，直接预览、保存到本机、重命名或删除文件。</p>
          <div class="selection-info">已选择 {{ selectedCount }} 个文件</div>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="toggleSelectAll">
            {{ allSelected ? '取消全选' : '全选' }}
          </button>
          <button class="btn btn-danger" @click="batchDelete" :disabled="selectedCount === 0">
            删除选中
          </button>
          <button class="btn btn-secondary" @click="refresh">刷新列表</button>
        </div>
      </div>

      <div class="files-table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th class="checkbox-col"><input type="checkbox" :checked="allSelected" @change.stop="toggleSelectAll" /></th>
              <th>文件名</th>
              <th>大小</th>
              <th>修改时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in files" :key="f.name" @click="selectFile(f)">
              <td class="checkbox-col">
                <input type="checkbox" :checked="isSelected(f.name)" @click.stop @change.stop="toggleSelection(f)" />
              </td>
              <td class="file-name">{{ f.name }}</td>
              <td>{{ f.size_formatted }}</td>
              <td>{{ formatDate(f.modified) }}</td>
              <td>
                <div class="action-btns">
                  <button class="btn btn-sm btn-primary" @click.stop="streamFile(f.name)">在线播放</button>
                  <button class="btn btn-sm btn-success" @click.stop="downloadFile(f.name)">下载</button>
                  <button class="btn btn-sm btn-warning" @click.stop="promptRename(f)">重命名</button>
                  <button class="btn btn-sm btn-danger" @click.stop="deleteFile(f)">删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="files.length === 0">
              <td colspan="4" class="empty-row">暂无文件</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="previewVisible" class="preview-overlay" @click.self="closePreview">
      <div class="preview-card">
        <div class="preview-header">
          <div>
            <h4>{{ selectedFile?.name }}</h4>
            <p class="preview-subtitle">直接在当前页面预览媒体内容</p>
          </div>
          <button class="btn btn-gray btn-sm" @click="closePreview">✕</button>
        </div>
        <div class="preview-body">
          <img v-if="selectedFile && isImage(selectedFile.name)" :src="fileUrl(selectedFile.name)" class="preview-media" />
          <video v-else-if="selectedFile && isVideo(selectedFile.name)" :src="fileUrl(selectedFile.name)" controls autoplay class="preview-media"></video>
          <audio v-else-if="selectedFile && isAudio(selectedFile.name)" :src="fileUrl(selectedFile.name)" controls class="preview-media"></audio>
          <div v-else class="preview-file">
            <p>无法预览此文件类型。可点击下载或在新标签页打开。</p>
            <a :href="fileUrl(selectedFile?.name || '')" target="_blank">在新标签页打开</a>
          </div>
        </div>
      </div>
    </div>

    <div v-if="renaming" class="modal-overlay" @click.self="closeRename">
      <div class="modal-card">
        <div class="modal-header">
          <h3>重命名文件</h3>
          <button class="btn btn-gray btn-sm" @click="closeRename">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>新文件名（不含后缀）</label>
            <input v-model="newName" class="input" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="closeRename">取消</button>
          <button class="btn btn-primary" @click="confirmRename">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { files as filesApi } from '@/utils/api.js'

const files = ref([])
const renaming = ref(false)
const targetFile = ref(null)
const newName = ref('')
const selectedFiles = ref(new Set())

const selectedFile = ref(null)
const previewVisible = ref(false)

const selectedCount = computed(() => selectedFiles.value.size)
const allSelected = computed(() => files.value.length > 0 && selectedFiles.value.size === files.value.length)

function fileUrl(name) {
  const token = localStorage.getItem('token')
  return `/api/files/stream/${encodeURIComponent(name)}?token=${token}`
}

function isImage(name) {
  return /\.(jpe?g|png|gif|bmp|webp)$/i.test(name)
}

function isVideo(name) {
  return /\.(mp4|webm|mkv|mov|ts|flv)$/i.test(name)
}

function isAudio(name) {
  return /\.(mp3|m4a|wav|flac|aac|ogg)$/i.test(name)
}

function formatDate(date) {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

async function loadFiles() {
  try {
    const data = await filesApi.list()
    files.value = data.files || []
  } catch (e) {
    alert('加载文件失败: ' + e.message)
  }
}

function refresh() {
  loadFiles()
}

function streamFile(name) {
  selectedFile.value = { name }
  previewVisible.value = true
}

function selectFile(f) {
  selectedFile.value = f
  previewVisible.value = true
}

function downloadFile(name) {
  filesApi.download(name)
}

function promptRename(f) {
  targetFile.value = f
  const base = f.name.replace(/\.[^/.]+$/, '')
  newName.value = base
  renaming.value = true
}

function closeRename() {
  renaming.value = false
  targetFile.value = null
  newName.value = ''
}

function isSelected(name) {
  return selectedFiles.value.has(name)
}

function toggleSelection(f) {
  const next = new Set(selectedFiles.value)
  if (next.has(f.name)) {
    next.delete(f.name)
  } else {
    next.add(f.name)
  }
  selectedFiles.value = next
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedFiles.value = new Set()
    return
  }
  selectedFiles.value = new Set(files.value.map(file => file.name))
}

async function batchDelete() {
  if (selectedFiles.value.size === 0) return
  if (!confirm(`确定删除 ${selectedCount.value} 个选中文件？`)) return
  const deleteNames = Array.from(selectedFiles.value)
  try {
    await Promise.all(deleteNames.map(name => filesApi.delete(name)))
    selectedFiles.value.clear()
    alert('已删除选中文件')
    loadFiles()
  } catch (e) {
    alert('批量删除失败: ' + e.message)
  }
}

async function confirmRename() {
  if (!targetFile.value) return
  try {
    await filesApi.rename(targetFile.value.name, newName.value)
    alert('重命名成功')
    closeRename()
    loadFiles()
  } catch (e) {
    alert('重命名失败: ' + e.message)
  }
}

async function deleteFile(f) {
  if (!confirm('确定删除 ' + f.name + ' ?')) return
  try {
    await filesApi.delete(f.name)
    selectedFiles.value.delete(f.name)
    alert('已删除')
    loadFiles()
  } catch (e) {
    alert('删除失败: ' + e.message)
  }
}

onMounted(() => {
  loadFiles()
})

function closePreview() {
  previewVisible.value = false
  selectedFile.value = null
}
</script>

<style scoped>
.files-manager {
  padding: 22px;
}
.files-card {
  background: #ffffff;
  border-radius: 22px;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.12);
  padding: 20px;
}
.files-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 18px;
}
.files-card-header h3 {
  margin: 0;
  font-size: 20px;
  color: #111827;
}
.subtitle {
  margin: 6px 0 0;
  color: #6b7280;
  font-size: 14px;
}
.selection-info {
  margin-top: 8px;
  color: #4b5563;
  font-size: 13px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.checkbox-col {
  width: 42px;
  text-align: center;
}
.files-table-wrap {
  overflow-x: auto;
}
.table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
}
.table th,
.table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #eff2f7;
}
.table th {
  color: #374151;
  font-weight: 600;
  font-size: 14px;
}
.table tbody tr:hover {
  background: #f8fafc;
}
.table tbody tr {
  cursor: pointer;
}
.file-name {
  max-width: 420px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.action-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.btn {
  border: none;
  cursor: pointer;
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 13px;
  transition: transform .15s ease, background .15s ease;
}
.btn:hover {
  transform: translateY(-1px);
}
.btn-sm {
  padding: 7px 12px;
}
.btn-primary { background: #2563eb; color: #ffffff }
.btn-success { background: #16a34a; color: #ffffff }
.btn-warning { background: #f59e0b; color: #ffffff }
.btn-danger { background: #dc2626; color: #ffffff }
.btn-secondary { background: #e5e7eb; color: #111827 }
.btn-gray { background: #f3f4f6; color: #111827 }
.empty-row {
  text-align: center;
  color: #9ca3af;
  padding: 28px 0;
}
.preview-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.72);
  padding: 20px;
}
.preview-card {
  width: min(100%, 920px);
  max-width: 920px;
  background: #ffffff;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 36px 80px rgba(15, 23, 42, 0.18);
}
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 24px 26px 18px;
  border-bottom: 1px solid #e5e7eb;
}
.preview-header h4 {
  margin: 0;
  font-size: 18px;
}
.preview-subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  color: #6b7280;
}
.preview-body {
  padding: 20px 24px 28px;
}
.preview-media {
  width: 100%;
  border-radius: 18px;
  background: #111827;
  max-height: 72vh;
}
.preview-file {
  padding: 28px;
  text-align: center;
  color: #4b5563;
}
.preview-file a {
  color: #2563eb;
  text-decoration: none;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(15, 23, 42, 0.62);
  z-index: 1250;
}
.modal-card {
  width: min(100%, 420px);
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.18);
  overflow: hidden;
}
.modal-header,
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 22px;
}
.modal-header h3 {
  margin: 0;
  font-size: 17px;
}
.modal-body {
  padding: 0 22px 18px;
}
.form-item {
  margin-bottom: 14px;
}
.form-item label {
  display: block;
  margin-bottom: 8px;
  color: #4b5563;
  font-size: 13px;
}
.input {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 11px 14px;
  font-size: 14px;
  color: #111827;
}
.modal-footer button {
  min-width: 96px;
}
</style>

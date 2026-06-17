import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const role = ref(localStorage.getItem('role') || '')
  const avatar = ref(localStorage.getItem('avatar') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')

  function setAuth(data) {
    token.value = data.token
    username.value = data.username
    role.value = data.role
    avatar.value = data.avatar || ''
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('role', data.role)
    if (data.avatar) localStorage.setItem('avatar', data.avatar)
  }

  function clearAuth() {
    token.value = ''
    username.value = ''
    role.value = ''
    avatar.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    localStorage.removeItem('avatar')
  }

  async function login(usernameVal, passwordVal) {
    const data = await api.post('/api/admin/login', { username: usernameVal, password: passwordVal })
    setAuth(data)
    return data
  }

  async function register(usernameVal, passwordVal, inviteCode) {
    return await api.post('/api/admin/register', {
      username: usernameVal,
      password: passwordVal,
      invite_code: inviteCode
    })
  }

  async function logout() {
    clearAuth()
  }

  return {
    token, username, role, avatar,
    isLoggedIn, isAdmin,
    setAuth, clearAuth, login, register, logout
  }
})

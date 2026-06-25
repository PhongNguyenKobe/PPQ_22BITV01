import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserProfile } from '~/services/api'

export const useUserStore = defineStore('user', () => {
  // Pre-configured mock accounts:
  // 1. Customer: customer@gmail.com / customer123
  // 2. Admin: admin@cineai.vn / admin123
  // 3. Branch Admin: branch@cineai.vn / branch123
  const registeredUsers = ref<UserProfile[]>([
    { id: 'u1', name: 'Nguyễn Đăng Khách', email: 'customer@gmail.com', role: 'customer' },
    { id: 'u2', name: 'Admin CineAI', email: 'admin@cineai.vn', role: 'admin' },
    { id: 'u3', name: 'Sala Branch Manager', email: 'branch@cineai.vn', role: 'branch-admin', branchId: 'b1' }
  ])

  const currentUser = ref<UserProfile | null>(null)
  const isAuthenticated = ref(false)

  // Initialize from client-side localStorage if available
  if (process.client) {
    const saved = localStorage.getItem('cineai_user')
    if (saved) {
      try {
        currentUser.value = JSON.parse(saved)
        isAuthenticated.value = true
      } catch (e) {
        localStorage.removeItem('cineai_user')
      }
    }
  }

  function login(email: string, role: 'customer' | 'admin' | 'branch-admin'): boolean {
    const matched = registeredUsers.value.find(u => u.email === email && u.role === role)
    if (matched) {
      currentUser.value = matched
      isAuthenticated.value = true
      if (process.client) {
        localStorage.setItem('cineai_user', JSON.stringify(matched))
      }
      return true
    }
    return false
  }

  function register(name: string, email: string): boolean {
    const exists = registeredUsers.value.some(u => u.email === email)
    if (exists) return false

    const newUser: UserProfile = {
      id: `u-${Date.now()}`,
      name,
      email,
      role: 'customer'
    }

    registeredUsers.value.push(newUser)
    currentUser.value = newUser
    isAuthenticated.value = true
    if (process.client) {
      localStorage.setItem('cineai_user', JSON.stringify(newUser))
    }
    return true
  }

  function logout() {
    currentUser.value = null
    isAuthenticated.value = false
    if (process.client) {
      localStorage.removeItem('cineai_user')
    }
  }

  return {
    currentUser,
    isAuthenticated,
    registeredUsers,
    login,
    register,
    logout
  }
})

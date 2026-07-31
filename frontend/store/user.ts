import { defineStore, skipHydrate } from 'pinia'
import { ref } from 'vue'
import { authService, mapBackendUserToProfile, setAuthToken, type UserProfile } from '~/services/api'

export const useUserStore = defineStore('user', () => {
  const registeredUsers = ref<UserProfile[]>([])
  const currentUser = ref<UserProfile | null>(null)
  const isAuthenticated = ref(false)
  const authToken = ref<string | null>(null)
  const authError = ref('')

  function errorMessage(error: any): string {
    const detail = error?.message
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map(item => item?.msg || String(item)).join('. ')
    }
    return 'Đã có lỗi xảy ra. Vui lòng thử lại.'
  }

  function setSession(user: UserProfile | null, token: string | null) {
    currentUser.value = user
    isAuthenticated.value = Boolean(user && token)
    authToken.value = token

    if (process.client) {
      if (user && token) {
        sessionStorage.setItem('cineai_user', JSON.stringify(user))
        sessionStorage.setItem('cineai_token', token)
      } else {
        sessionStorage.removeItem('cineai_user')
        sessionStorage.removeItem('cineai_token')
      }
    }

    setAuthToken(token)
  }

  async function refreshCurrentUser() {
    if (!authToken.value) return
    try {
      const backendUser = await authService.me()
      const mappedUser = mapBackendUserToProfile(backendUser, authToken.value)
      currentUser.value = mappedUser
      registeredUsers.value = [mappedUser]
      isAuthenticated.value = true
      if (process.client) {
        sessionStorage.setItem('cineai_user', JSON.stringify(mappedUser))
      }
    } catch {
      logout()
    }
  }

  // Mỗi tab có một phiên đăng nhập độc lập.
  if (process.client) {
    // Xóa phiên bản cũ dùng chung giữa các tab để tránh rò tài khoản chéo tab.
    localStorage.removeItem('cineai_user')
    localStorage.removeItem('cineai_token')
    const savedToken = sessionStorage.getItem('cineai_token')
    const saved = sessionStorage.getItem('cineai_user')
    if (savedToken) {
      authToken.value = savedToken
      setAuthToken(savedToken)
    }
    if (saved && savedToken) {
      try {
        currentUser.value = JSON.parse(saved)
        isAuthenticated.value = true
        if (currentUser.value) {
          registeredUsers.value = [currentUser.value]
        }
      } catch (e) {
        sessionStorage.removeItem('cineai_user')
        sessionStorage.removeItem('cineai_token')
      }
    }

    if (savedToken) {
      void refreshCurrentUser()
    }
  }

  async function login(identifier: string, password: string): Promise<boolean> {
    authError.value = ''
    try {
      const response = await authService.login({ identifier, password })
      const mappedUser = mapBackendUserToProfile(response.user, response.access_token)
      registeredUsers.value = [mappedUser]
      setSession(mappedUser, response.access_token)
      return true
    } catch (error) {
      authError.value = errorMessage(error)
      return false
    }
  }

  async function register(payload: { name: string; email: string; phone: string; password: string; dateOfBirth?: string; gender?: string }): Promise<boolean> {
    authError.value = ''
    try {
      const response = await authService.register({
        full_name: payload.name,
        email: payload.email,
        phone: payload.phone,
        password: payload.password,
        date_of_birth: payload.dateOfBirth || null,
        gender: payload.gender || null,
      })
      const mappedUser = mapBackendUserToProfile(response.user, response.access_token)
      registeredUsers.value = [mappedUser]
      setSession(mappedUser, response.access_token)
      return true
    } catch (error) {
      authError.value = errorMessage(error)
      return false
    }
  }

  function logout() {
    setSession(null, null)
  }

  return {
    currentUser: skipHydrate(currentUser),
    isAuthenticated: skipHydrate(isAuthenticated),
    registeredUsers,
    authToken: skipHydrate(authToken),
    authError,
    login,
    register,
    refreshCurrentUser,
    logout
  }
})

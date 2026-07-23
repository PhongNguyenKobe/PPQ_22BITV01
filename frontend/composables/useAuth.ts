import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '~/store/user'

export const useAuth = () => {
  const userStore = useUserStore()
  const router = useRouter()
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => userStore.isAuthenticated)
  const currentUser = computed(() => userStore.currentUser)
  const authToken = computed(() => userStore.authToken)

  const login = async (email: string, password: string) => {
    isLoading.value = true
    error.value = null
    try {
      const success = await userStore.login(email, password)
      if (success) {
        await router.push('/products')
      } else {
        error.value = 'Invalid credentials'
      }
      return success
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const register = async (email: string, password: string, fullName: string) => {
    isLoading.value = true
    error.value = null
    try {
      const success = await userStore.register(email, password, fullName)
      if (success) {
        await router.push('/products')
      } else {
        error.value = 'Registration failed'
      }
      return success
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Registration failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    userStore.logout()
    router.push('/login')
  }

  const refreshUser = async () => {
    await userStore.refreshCurrentUser()
  }

  return {
    isLoading,
    error,
    isAuthenticated,
    currentUser,
    authToken,
    login,
    register,
    logout,
    refreshUser
  }
}

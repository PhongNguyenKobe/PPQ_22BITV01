import { ref } from 'vue'

export const useApi = () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const execute = async <T>(
    apiCall: () => Promise<T>,
    errorMessage = 'An error occurred'
  ): Promise<T | null> => {
    isLoading.value = true
    error.value = null
    try {
      const result = await apiCall()
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : errorMessage
      console.error(error.value, err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const reset = () => {
    error.value = null
  }

  return {
    isLoading,
    error,
    execute,
    reset
  }
}

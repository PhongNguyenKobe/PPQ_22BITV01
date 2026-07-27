import { useUserStore } from '~/store/user'

export default defineNuxtRouteMiddleware((to) => {
  const userStore = useUserStore()

  if (!userStore.isAuthenticated) {
    return navigateTo('/login')
  }

  const allow = to.meta.role as string[] | undefined

  if (!allow || allow.length === 0) {
    return
  }

  if (!userStore.currentUser) {
    return navigateTo('/login')
  }

  if (!allow.includes(userStore.currentUser.role)) {
    return navigateTo('/products')
  }
})
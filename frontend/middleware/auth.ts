import { useUserStore } from '~/store/user'

export default defineNuxtRouteMiddleware((to, from) => {
  const userStore = useUserStore()

  console.log('[auth middleware] path:', to.path)
  console.log('[auth middleware] isAuthenticated:', userStore.isAuthenticated, '| role:', userStore.currentUser?.role, '| user:', userStore.currentUser)

  // Routes that require authentication
  const protectedRoutes = [
    '/checkout',
    '/profile',
    '/admin',
    '/branch-admin'
  ]

  // Routes for admins only
  const adminRoutes = ['/admin']
  const branchAdminRoutes = ['/branch-admin']

  const isProtected = protectedRoutes.some(route => to.path.startsWith(route))
  const isAdminRoute = adminRoutes.some(route => to.path.startsWith(route))
  const isBranchAdminRoute = branchAdminRoutes.some(route => to.path.startsWith(route))

  if (isProtected && !userStore.isAuthenticated) {
    return navigateTo('/login')
  }

  if (isAdminRoute && userStore.currentUser?.role !== 'admin') {
    if (userStore.currentUser?.role === 'branch-admin') {
      return navigateTo('/branch-admin/dashboard')
    }
    return navigateTo('/products')
  }

  if (isBranchAdminRoute && userStore.currentUser?.role !== 'branch-admin') {
    if (userStore.currentUser?.role === 'admin') {
      return navigateTo('/admin/dashboard')
    }
    return navigateTo('/products')
  }
})

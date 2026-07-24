import { useUserStore } from '~/store/user'

export default defineRouteMiddleware((to, from) => {
  const userStore = useUserStore()

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

  // Check if user is authenticated
  if (isProtected && !userStore.isAuthenticated) {
    return navigateTo('/login')
  }

  // Check if user has admin role
  if (isAdminRoute && userStore.currentUser?.role !== 'admin') {
    return navigateTo('/products')
  }

  // Check if user has branch admin role
  if (isBranchAdminRoute && userStore.currentUser?.role !== 'branch-admin') {
    return navigateTo('/products')
  }
})

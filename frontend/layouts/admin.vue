<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/store/user'

const userStore = useUserStore()
const { currentUser, isAuthenticated } = storeToRefs(userStore)

function handleLogout() {
  userStore.logout()
  navigateTo('/login')
}

// Redirect if not logged in as admin/branch-admin
onMounted(() => {
  if (!isAuthenticated.value || !currentUser.value || (currentUser.value.role !== 'admin' && currentUser.value.role !== 'branch-admin')) {
    navigateTo('/login')
  }
})
</script>

<template>
  <div class="admin-shell">
    <!-- Sidebar Navigation -->
    <aside class="admin-sidebar">
      <div>
        <!-- Sidebar Brand -->
        <div class="admin-sidebar-brand">
          <NuxtLink to="/products" class="brand-link">
            <span class="material-symbols-outlined">local_activity</span>
            <span>
              CineMe Admin
              <small>Smart cinema ops</small>
            </span>
          </NuxtLink>
        </div>

        <!-- Navigation Links -->
        <nav class="admin-nav">
          <div class="admin-nav-title">
            {{ currentUser?.role === 'admin' ? 'Quản trị hệ thống' : 'Quản lý chi nhánh' }}
          </div>

          <NuxtLink
            v-if="currentUser?.role === 'admin'"
            to="/admin/dashboard"
            class="nav-link"
            active-class="nav-link-active"
          >
            <span class="material-symbols-outlined text-lg">dashboard</span>
            Bảng điều khiển
          </NuxtLink>

          <NuxtLink
            v-if="currentUser?.role === 'branch-admin'"
            to="/branch-admin/dashboard"
            class="nav-link"
            active-class="nav-link-active"
          >
            <span class="material-symbols-outlined text-lg">storefront</span>
            Bảng chi nhánh
          </NuxtLink>

          <NuxtLink
            to="/products"
            class="nav-link"
          >
            <span class="material-symbols-outlined text-lg">movie</span>
            Trang bán vé
          </NuxtLink>
        </nav>
      </div>

      <!-- Sidebar User Section -->
      <div class="sidebar-user">
        <div class="flex items-center gap-3 mb-4">
          <div class="avatar-circle">
            {{ currentUser?.name.substring(0, 2).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <h5 class="text-sm font-semibold truncate text-on-surface">{{ currentUser?.name }}</h5>
            <span class="text-xs text-on-surface-variant capitalize">{{ currentUser?.role }}</span>
          </div>
        </div>
        <button
          @click="handleLogout"
          class="logout-btn"
        >
          <span class="material-symbols-outlined text-sm">logout</span>
          Đăng xuất
        </button>
      </div>
    </aside>

    <!-- Main Dashboard Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Portal Top Header -->
      <header class="admin-header">
        <div>
          <h2 class="text-lg font-bold text-on-surface flex items-center gap-2">
            {{ currentUser?.role === 'admin' ? 'Hệ thống Quản trị Tổng' : 'Hệ thống Quản trị Chi nhánh' }}
          </h2>
          <p class="text-xs text-on-surface-variant mt-0.5">Theo dõi dữ liệu vận hành rạp theo thời gian thực</p>
        </div>
        <div class="flex items-center gap-4">
          <NuxtLink to="/products" class="back-btn">
            <span class="material-symbols-outlined text-sm">home</span>
            Quay về trang bán vé
          </NuxtLink>
        </div>
      </header>

      <!-- Dashboard Pages Scroll -->
      <main class="admin-main">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-shell {
  display: flex;
  height: 100vh;
  background: #121414;
  color: #e2e2e2;
}

.admin-sidebar {
  width: 16.5rem;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  background: #171919;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.admin-sidebar-brand {
  height: 5.2rem;
  display: flex;
  align-items: center;
  padding: 0 1.4rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: #e50914;
  font-weight: 900;
  font-size: 1.1rem;
}

.brand-link small {
  display: block;
  color: #8f949c;
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.admin-nav {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.admin-nav-title {
  padding: 0 0.7rem;
  margin-bottom: 0.2rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 800;
  color: #8f949c;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.72rem 0.82rem;
  border-radius: 0.75rem;
  font-size: 0.86rem;
  color: #b3b3b3;
  font-weight: 600;
  transition: all 0.18s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

.nav-link-active {
  color: #ffffff !important;
  background: linear-gradient(135deg, #e50914, #9f1239);
  box-shadow: 0 14px 24px -18px rgba(229, 9, 20, 0.95);
}

.sidebar-user {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
}

.avatar-circle {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background: linear-gradient(135deg, #e50914, #8b1538);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.82rem;
}

.logout-btn {
  width: 100%;
  border: 1px solid rgba(239, 68, 68, 0.24);
  background: rgba(127, 29, 29, 0.18);
  color: #fda4af;
  padding: 0.55rem 0.8rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.12);
}

.admin-header {
  height: 5.2rem;
  background: #171919;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.8rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.77rem;
  font-weight: 700;
  padding: 0.55rem 0.95rem;
  border-radius: 0.72rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #e2e2e2;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.18);
}

.admin-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
}

@media (max-width: 1024px) {
  .admin-sidebar {
    width: 14.5rem;
  }

  .admin-header {
    padding: 0 1rem;
  }
}
</style>


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
  <div class="flex h-screen bg-[#0d0e0f] text-on-surface">
    <!-- Sidebar Navigation -->
    <aside class="w-64 bg-surface border-r border-glass-stroke flex flex-col justify-between">
      <div>
        <!-- Sidebar Brand -->
        <div class="h-20 flex items-center px-6 border-b border-glass-stroke">
          <NuxtLink to="/movies" class="font-headline-md text-xl font-bold text-primary-container flex items-center gap-2">
            <span class="material-symbols-outlined">shield</span>
            CineAI Portal
          </NuxtLink>
        </div>

        <!-- Navigation Links -->
        <nav class="p-4 space-y-2">
          <div class="px-3 mb-2 text-xs font-bold uppercase tracking-wider text-on-surface-variant">
            {{ currentUser?.role === 'admin' ? 'Quản trị hệ thống' : 'Quản lý chi nhánh' }}
          </div>

          <NuxtLink
            v-if="currentUser?.role === 'admin'"
            to="/admin/dashboard"
            class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-sm transition-colors text-on-surface-variant hover:text-on-surface"
            active-class="bg-primary-container/10 border border-primary-container/20 !text-primary-container font-semibold"
          >
            <span class="material-symbols-outlined text-lg">dashboard</span>
            Bảng điều khiển
          </NuxtLink>

          <NuxtLink
            v-if="currentUser?.role === 'branch-admin'"
            to="/branch-admin/dashboard"
            class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-sm transition-colors text-on-surface-variant hover:text-on-surface"
            active-class="bg-purple-950/20 border border-purple-500/30 !text-purple-400 font-semibold"
          >
            <span class="material-symbols-outlined text-lg">storefront</span>
            Bảng chi nhánh
          </NuxtLink>

          <NuxtLink
            to="/#"
            class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-sm transition-colors text-on-surface-variant hover:text-on-surface"
          >
            <span class="material-symbols-outlined text-lg">movie</span>
            Trang bán vé
          </NuxtLink>
        </nav>
      </div>

      <!-- Sidebar User Section -->
      <div class="p-4 border-t border-glass-stroke bg-surface-container-low/40">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-surface-container-high border border-glass-stroke flex items-center justify-center font-bold text-sm text-primary">
            {{ currentUser?.name.substring(0, 2).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <h5 class="text-sm font-semibold truncate text-on-surface">{{ currentUser?.name }}</h5>
            <span class="text-xs text-on-surface-variant capitalize">{{ currentUser?.role }}</span>
          </div>
        </div>
        <button
          @click="handleLogout"
          class="w-full bg-red-950/20 border border-red-500/20 text-red-400 hover:bg-red-500/10 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2"
        >
          <span class="material-symbols-outlined text-sm">logout</span>
          Đăng xuất
        </button>
      </div>
    </aside>

    <!-- Main Dashboard Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Portal Top Header -->
      <header class="h-20 bg-surface border-b border-glass-stroke flex items-center justify-between px-8">
        <div>
          <h2 class="text-lg font-bold text-on-surface flex items-center gap-2">
            {{ currentUser?.role === 'admin' ? 'Hệ thống Quản trị Tổng' : 'Hệ thống Quản trị Chi nhánh' }}
          </h2>
        </div>
        <div class="flex items-center gap-4">
          <NuxtLink to="/movies" class="text-xs font-bold bg-white/5 border border-glass-stroke hover:bg-white/10 px-4 py-2 rounded-xl text-on-surface flex items-center gap-2">
            <span class="material-symbols-outlined text-sm">home</span>
            Quay về trang bán vé
          </NuxtLink>
        </div>
      </header>

      <!-- Dashboard Pages Scroll -->
      <main class="flex-1 overflow-y-auto p-8">
        <slot />
      </main>
    </div>
  </div>
</template>

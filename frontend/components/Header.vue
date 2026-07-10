<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/store/user'
import { useMoviesStore } from '~/store/movies'

const userStore = useUserStore()
const moviesStore = useMoviesStore()
const { currentUser, isAuthenticated } = storeToRefs(userStore)

const searchVal = ref('')
const showProfileDropdown = ref(false)

function handleSearchSubmit() {
  if (!searchVal.value.trim()) return
  moviesStore.searchMovies(searchVal.value)
  navigateTo('/ai-discovery')
}

function handleLogout() {
  showProfileDropdown.value = false
  userStore.logout()
  navigateTo('/login')
}

function clickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.profile-dropdown-wrap')) {
    showProfileDropdown.value = false
  }
}

onMounted(() => {
  if (process.client) {
    window.addEventListener('click', clickOutside)
  }
})

onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('click', clickOutside)
  }
})
</script>

<template>
  <header class="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 md:px-margin-desktop h-20 bg-surface/80 backdrop-blur-[32px] border-b border-white/10 shadow-[0_8px_32px_0_rgba(229,9,20,0.1)]">
    <div class="flex items-center gap-12">
      <NuxtLink to="/" class="font-headline-lg text-headline-lg font-bold text-primary-container tracking-tighter hover:scale-105 transition-all duration-300">
        CineAI
      </NuxtLink>

      <nav class="hidden md:flex items-center gap-8">

        <NuxtLink to="/ai-discovery" class="font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary-container hover:scale-105 transition-all duration-300" active-class="text-primary-container font-bold border-b-2 border-primary-container pb-1">
          Khám phá AI
        </NuxtLink>
        <NuxtLink to="/showtimes" class="font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary-container hover:scale-105 transition-all duration-300" active-class="text-primary-container font-bold border-b-2 border-primary-container pb-1">
          Lịch chiếu
        </NuxtLink>
        <NuxtLink to="/cinemas" class="font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary-container hover:scale-105 transition-all duration-300" active-class="text-primary-container font-bold border-b-2 border-primary-container pb-1">
          Rạp phim
        </NuxtLink>
      </nav>
    </div>

    <div class="flex items-center gap-6">
      <form @submit.prevent="handleSearchSubmit" class="hidden lg:flex items-center bg-surface-container-low px-4 py-2 rounded-full border border-white/5 focus-within:border-primary-container transition-all w-64">
        <span class="material-symbols-outlined text-on-surface-variant text-[20px]">search</span>
        <input v-model="searchVal" class="bg-transparent border-none focus:ring-0 text-label-md font-label-md placeholder:text-on-surface-variant text-on-surface w-full ml-2 outline-none" placeholder="Tìm phim, rạp..." type="text" />
      </form>

      <template v-if="isAuthenticated && currentUser">
        <div class="relative profile-dropdown-wrap">
          <div @click="showProfileDropdown = !showProfileDropdown" class="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-container cursor-pointer hover:scale-105 active:scale-95 transition-all shadow-[0_0_10px_rgba(229,9,20,0.3)]">
            <img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDAq3Ng_339WB6mfv_mphK39dGLHMFszhx-AgYKMNAvdIBLaztowKDKDJpjtfA1Hc4jtWnPWz-O1b3Xl4xNoHEyMW1Bf6zs9uyhZGSAweY4AhvQFeh3HyIasFX6W2bT7swfWEEUAQj4wOEWFCuLZR-tYeEf6icRjw1AX3rtxEilO1_XTlXh7u73vegugRIYMB-OuZT8VKVaoS3YbMPNSw30Kyi-OSCHogqRKyoYdEVuLlJOEqJo2UTT1aXKfDROvvaMuTmh2lPPsUsn" alt="Profile" />
          </div>
          <transition enter-active-class="transition duration-100 ease-out" enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100" leave-active-class="transition duration-75 ease-in" leave-from-class="transform scale-100 opacity-100" leave-to-class="transform scale-95 opacity-0">
            <div v-if="showProfileDropdown" class="absolute right-0 mt-3 w-64 rounded-2xl border border-white/10 shadow-2xl p-2 z-50" style="background:rgba(18,20,20,0.96);backdrop-filter:blur(12px)">
              <div class="px-4 py-3 border-b border-white/10 mb-2">
                <h5 class="text-xs font-bold text-on-surface truncate">{{ currentUser.name }}</h5>
                <span class="text-[10px] text-on-surface-variant truncate block mt-0.5">{{ currentUser.email }}</span>
              </div>
              <NuxtLink v-if="currentUser.role === 'customer'" to="/profile/tickets" @click="showProfileDropdown = false" class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors">
                <span class="material-symbols-outlined text-sm">confirmation_number</span> Vé của tôi
              </NuxtLink>
              <NuxtLink v-if="currentUser.role === 'admin'" to="/admin/dashboard" @click="showProfileDropdown = false" class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors">
                <span class="material-symbols-outlined text-sm">dashboard</span> Quản trị hệ thống
              </NuxtLink>
              <NuxtLink v-if="currentUser.role === 'branch-admin'" to="/branch-admin/dashboard" @click="showProfileDropdown = false" class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors">
                <span class="material-symbols-outlined text-sm">storefront</span> Quản lý chi nhánh
              </NuxtLink>
              <button @click="handleLogout" class="w-full text-left flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-red-400 hover:bg-red-500/10 transition-colors border-t border-white/10 mt-2 pt-2">
                <span class="material-symbols-outlined text-sm">logout</span> Đăng xuất
              </button>
            </div>
          </transition>
        </div>
      </template>
      <template v-else>
        <NuxtLink to="/login" class="bg-primary-container text-on-primary-container font-label-md text-label-md font-bold px-6 py-2.5 rounded-xl hover:scale-105 active:scale-95 transition-all duration-300 shadow-[0_0_20px_-5px_rgba(229,9,20,0.3)]">
          Đăng nhập
        </NuxtLink>
      </template>
    </div>
  </header>
</template>
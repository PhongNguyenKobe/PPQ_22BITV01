<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/store/user'
import { navigateTo } from 'nuxt/app'

const userStore = useUserStore()
const { currentUser, isAuthenticated } = storeToRefs(userStore)

// State quản lý Dropdown & Modals
const showProfileDropdown = ref(false)
const showBranchDropdown = ref(false)
const showMovieDropdown = ref(false)
const showMobileMenu = ref(false)
const showSearchModal = ref(false)

const searchQuery = ref('')

const branches = [
  { id: 'hung-vuong', name: 'CineAI Hùng Vương' },
  { id: 'sala-q2', name: 'CineAI Sala Q2' },
  { id: 'nguyen-du', name: 'CineAI Nguyễn Du' },
  { id: 'vincom-ba-trieu', name: 'CineAI Vincom Bà Triệu' },
  { id: 'da-nang-plaza', name: 'CineAI Đà Nẵng Plaza' }
]

function handleLogout() {
  showProfileDropdown.value = false
  showMobileMenu.value = false
  userStore.logout()
  navigateTo('/login')
}

function handleSearch() {
  if (!searchQuery.value.trim()) return
  navigateTo(`/movies?search=${encodeURIComponent(searchQuery.value.trim())}`)
  showSearchModal.value = false
  searchQuery.value = ''
}

// Xử lý Click Outside đóng các dropdown
function clickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.profile-dropdown-wrap')) {
    showProfileDropdown.value = false
  }
  if (!target.closest('.branch-dropdown-wrap')) {
    showBranchDropdown.value = false
  }
  if (!target.closest('.movie-dropdown-wrap')) {
    showMovieDropdown.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', clickOutside)
})

onUnmounted(() => {
  window.removeEventListener('click', clickOutside)
})
</script>

<template>
  <header
    class="fixed top-0 left-0 w-full z-50 bg-surface/60 backdrop-blur-[32px] border-b border-glass-stroke h-[82px]">
    <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop h-full flex items-center justify-between">
      <!-- LOGO + MAIN NAVIGATION -->
      <div class="flex items-center gap-8">
        <NuxtLink to="/"
          class="font-headline-md text-headline-md font-bold text-primary-container hover:scale-105 transition-all flex items-center gap-2">
          <span>CineAI</span>
        </NuxtLink>

        <!-- Desktop Navigation -->
        <nav class="hidden lg:flex items-center gap-6 font-body-md text-body-md">
          <!-- LỊCH CHIẾU -->
          <NuxtLink to="/showtimes" class="text-on-surface-variant hover:text-on-surface transition-colors"
            active-class="text-on-surface font-bold border-b-2 border-primary-container pb-1">
            Lịch Chiếu
          </NuxtLink>

          <!-- PHIM: đi thẳng tới /products -->
          <NuxtLink to="/products" class="hover:text-red-500 transition-colors" active-class="text-red-500">
            Phim
          </NuxtLink>

          <!-- RẠP CHIẾU (Dropdown) -->
          <div class="relative branch-dropdown-wrap">
            <button @click.stop="showBranchDropdown = !showBranchDropdown; showMovieDropdown = false"
              class="text-on-surface-variant hover:text-on-surface transition-colors flex items-center gap-1 font-medium focus:outline-none">
              Rạp Chiếu
              <span class="material-symbols-outlined text-xs select-none">
                keyboard_arrow_down
              </span>
            </button>

            <transition enter-active-class="transition duration-100 ease-out"
              enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-in" leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0">
              <div v-if="showBranchDropdown"
                class="absolute left-0 mt-3 w-56 rounded-2xl bg-surface border border-glass-stroke shadow-2xl p-2 z-50 glass-panel">
                <NuxtLink v-for="b in branches" :key="b.id" :to="`/cinemas/${b.id}`" @click="showBranchDropdown = false"
                  class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors">
                  {{ b.name }}
                </NuxtLink>
              </div>
            </transition>
          </div>

          <!-- KHUYẾN MÃI -->
          <NuxtLink to="/promotions" class="text-on-surface-variant hover:text-on-surface transition-colors"
            active-class="text-on-surface font-bold border-b-2 border-primary-container pb-1">
            Khuyến Mãi
          </NuxtLink>

          <!-- TIN TỨC / REVIEW -->
          <NuxtLink to="/news" class="text-on-surface-variant hover:text-on-surface transition-colors"
            active-class="text-on-surface font-bold border-b-2 border-primary-container pb-1">
            Tin Điện Ảnh
          </NuxtLink>

          <!-- KHÁM PHÁ AI -->
          <NuxtLink to="/ai-discovery"
            class="flex items-center gap-1 text-primary-container font-bold hover:opacity-80 transition-opacity">
            <span class="material-symbols-outlined text-sm">auto_awesome</span>
            Khám Phá AI
          </NuxtLink>
        </nav>
      </div>

      <!-- RIGHT ACTIONS (SEARCH, PROFILE, MOBILE MENU BUTTON) -->
      <div class="flex items-center gap-4">
        <!-- Search Button -->
        <button @click="showSearchModal = true"
          class="p-2 text-on-surface-variant hover:text-on-surface transition-colors rounded-full hover:bg-white/5"
          title="Tìm kiếm phim">
          <span class="material-symbols-outlined text-xl">search</span>
        </button>

        <!-- PROFILE / AUTH -->
        <template v-if="isAuthenticated && currentUser">
          <div class="relative profile-dropdown-wrap">
            <div @click.stop="showProfileDropdown = !showProfileDropdown"
              class="w-9 h-9 rounded-full overflow-hidden border-2 border-primary-container cursor-pointer hover:scale-105 active:scale-95 transition-all shadow-[0_0_10px_rgba(229,9,20,0.3)]">
              <img class="w-full h-full object-cover"
                :src="(currentUser as any).avatar || 'https://lh3.googleusercontent.com/aida-public/AB6AXuDAq3Ng_339WB6mfv_mphK39dGLHMFszhx-AgYKMNAvdIBLaztowKDKDJpjtfA1Hc4jtWnPWz-O1b3Xl4xNoHEyMW1Bf6zs9uyhZGSAweY4AhvQFeh3HyIasFX6W2bT7swfWEEUAQj4wOEWFCuLZR-tYeEf6icRjw1AX3rtxEilO1_XTlXh7u73vegugRIYMB-OuZT8VKVaoS3YbMPNSw30Kyi-OSCHogqRKyoYdEVuLlJOEqJo2UTT1aXKfDROvvaMuTmh2lPPsUsn'"
                alt="User Profile Picture" />
            </div>

            <transition enter-active-class="transition duration-100 ease-out"
              enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-in" leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0">
              <div v-if="showProfileDropdown"
                class="absolute right-0 mt-3 w-64 rounded-2xl bg-surface border border-glass-stroke shadow-2xl p-2 z-50 glass-panel">
                <div class="px-4 py-3 border-b border-glass-stroke/40 mb-2">
                  <h5 class="text-xs font-bold text-on-surface truncate">
                    {{ currentUser.name }}
                  </h5>
                  <span class="text-[10px] text-on-surface-variant truncate block mt-0.5">
                    {{ currentUser.email }}
                  </span>
                </div>

                <NuxtLink v-if="currentUser.role === 'customer'" to="/profile/tickets"
                  @click="showProfileDropdown = false"
                  class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:bg-white/5 transition-colors">
                  Vé của tôi
                </NuxtLink>

                <NuxtLink v-if="currentUser.role === 'customer'" to="/profile/settings"
                  @click="showProfileDropdown = false"
                  class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:bg-white/5 transition-colors">
                  Tài khoản & Ưu đãi
                </NuxtLink>

                <NuxtLink v-if="currentUser.role === 'admin'" to="/admin/dashboard" @click="showProfileDropdown = false"
                  class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:bg-white/5 transition-colors">
                  Quản trị hệ thống
                </NuxtLink>

                <NuxtLink v-if="currentUser.role === 'branch-admin'" to="/branch-admin/dashboard"
                  @click="showProfileDropdown = false"
                  class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:bg-white/5 transition-colors">
                  Quản lý chi nhánh
                </NuxtLink>

                <button @click="handleLogout"
                  class="w-full text-left px-4 py-2.5 rounded-xl text-xs text-red-400 hover:bg-red-500/10 border-t border-glass-stroke/40 mt-2 transition-colors">
                  Đăng xuất
                </button>
              </div>
            </transition>
          </div>
        </template>

        <template v-else>
          <NuxtLink to="/login"
            class="bg-primary-container text-on-primary-container px-5 py-2 rounded-xl font-label-md font-bold hover:scale-105 transition-all ai-glow">
            Đăng Nhập
          </NuxtLink>
        </template>

        <!-- Mobile Menu Hamburger Button -->
        <button @click="showMobileMenu = !showMobileMenu"
          class="lg:hidden p-2 text-on-surface-variant hover:text-on-surface focus:outline-none">
          <span class="material-symbols-outlined text-2xl">
            {{ showMobileMenu ? 'close' : 'menu' }}
          </span>
        </button>
      </div>
    </div>

    <!-- MOBILE MENU OVERLAY -->
    <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 -translate-y-4"
      enter-to-class="opacity-100 translate-y-0" leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-4">
      <div v-if="showMobileMenu"
        class="lg:hidden fixed top-[64px] left-0 w-full h-[calc(100vh-64px)] bg-surface/95 backdrop-blur-2xl border-b border-glass-stroke p-6 overflow-y-auto flex flex-col gap-6">
        <div class="flex flex-col gap-4 text-body-md font-medium">
          <NuxtLink to="/showtimes" @click="showMobileMenu = false"
            class="text-on-surface py-2 border-b border-glass-stroke/30">
            Lịch Chiếu
          </NuxtLink>

          <NuxtLink to="/movies/now-showing" @click="showMobileMenu = false"
            class="text-on-surface py-2 border-b border-glass-stroke/30">
            Phim Đang Chiếu
          </NuxtLink>

          <NuxtLink to="/movies/coming-soon" @click="showMobileMenu = false"
            class="text-on-surface py-2 border-b border-glass-stroke/30">
            Phim Sắp Chiếu
          </NuxtLink>

          <NuxtLink to="/promotions" @click="showMobileMenu = false"
            class="text-on-surface py-2 border-b border-glass-stroke/30">
            Khuyến Mãi
          </NuxtLink>

          <NuxtLink to="/news" @click="showMobileMenu = false"
            class="text-on-surface py-2 border-b border-glass-stroke/30">
            Tin Điện Ảnh
          </NuxtLink>

          <NuxtLink to="/ai-discovery" @click="showMobileMenu = false"
            class="text-primary-container font-bold py-2 border-b border-glass-stroke/30 flex items-center gap-2">
            <span class="material-symbols-outlined text-sm">auto_awesome</span>
            Khám Phá AI Gợi Ý
          </NuxtLink>
        </div>

        <div class="mt-auto pt-4 border-t border-glass-stroke">
          <p class="text-xs text-on-surface-variant mb-2 font-bold">Hệ thống Rạp CineAI:</p>
          <div class="grid grid-cols-1 gap-2">
            <NuxtLink v-for="b in branches" :key="b.id" :to="`/cinemas/${b.id}`" @click="showMobileMenu = false"
              class="text-xs text-on-surface-variant hover:text-on-surface py-1">
              • {{ b.name }}
            </NuxtLink>
          </div>
        </div>
      </div>
    </transition>

    <!-- SEARCH MODAL -->
    <transition enter-active-class="transition duration-150 ease-out" enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
      <div v-if="showSearchModal"
        class="fixed inset-0 z-50 bg-black/70 backdrop-blur-md flex items-start justify-center pt-20 px-4"
        @click.self="showSearchModal = false">
        <div class="bg-surface border border-glass-stroke w-full max-w-xl rounded-2xl p-4 shadow-2xl glass-panel">
          <form @submit.prevent="handleSearch" class="flex items-center gap-3">
            <span class="material-symbols-outlined text-on-surface-variant">search</span>
            <input v-model="searchQuery" type="text" placeholder="Nhập tên phim, đạo diễn, diễn viên..."
              class="w-full bg-transparent text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none text-sm"
              autofocus />
            <button type="button" @click="showSearchModal = false"
              class="text-xs text-on-surface-variant hover:text-on-surface px-2 py-1">
              Hủy
            </button>
          </form>
        </div>
      </div>
    </transition>
  </header>
</template>
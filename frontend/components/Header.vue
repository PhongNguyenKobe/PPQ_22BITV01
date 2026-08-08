<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/store/user'
import { useTicketsStore } from '~/store/tickets'
import { navigateTo } from 'nuxt/app'
import { branchesService, type BackendBranch } from '~/services/api'

const userStore = useUserStore()
const ticketsStore = useTicketsStore()
const { currentUser, isAuthenticated } = storeToRefs(userStore)
const route = useRoute()
const isAdminPreview = computed(() => route.query.preview === 'admin' && ['admin', 'branch-admin'].includes(currentUser.value?.role || ''))

// State quản lý Dropdown & Modals
const showProfileDropdown = ref(false)
const showBranchDropdown = ref(false)
const showMovieDropdown = ref(false)
const showMobileMenu = ref(false)
const showTicketNotifications = ref(false)
const reminderNow = ref(Date.now())
let reminderTimer: ReturnType<typeof setInterval> | undefined

const branches = ref<BackendBranch[]>([])
const ticketNotifications = computed(() => ticketsStore.ticketHistory
  .filter(ticket => {
    const count = ticket.perSeatTickets?.length || ticket.seats.length
    const used = (ticket.perSeatTickets || []).filter(item => item.status === 'USED').length
    const starts = new Date(ticket.startsAt).getTime()
    return ticket.status === 'CONFIRMED' && used < count && starts >= reminderNow.value - 3 * 60 * 60 * 1000 && starts <= reminderNow.value + 24 * 60 * 60 * 1000
  })
  .sort((a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime())
  .slice(0, 5))
function reminderText(ticket: typeof ticketNotifications.value[number]) {
  const minutes = Math.ceil((new Date(ticket.startsAt).getTime() - reminderNow.value) / 60000)
  if (minutes <= 0) return 'Suất chiếu đang diễn ra'
  if (minutes <= 60) return `Còn ${minutes} phút · Có thể check-in`
  return `${ticket.time} hôm nay · ${ticket.branchName}`
}
async function refreshTicketReminders() {
  reminderNow.value = Date.now()
  if (currentUser.value?.role === 'customer' && !ticketsStore.historyLoading) await ticketsStore.loadTicketHistory()
}

function handleLogout() {
  showProfileDropdown.value = false
  showMobileMenu.value = false
  userStore.logout()
  navigateTo('/login')
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
  if (!target.closest('.ticket-notification-wrap')) showTicketNotifications.value = false
}

onMounted(async () => {
  window.addEventListener('click', clickOutside)
  try {
    branches.value = await branchesService.getAll()
  } catch {
    branches.value = []
  }
  await refreshTicketReminders()
  reminderTimer = setInterval(() => { if (!document.hidden) void refreshTicketReminders() }, 60000)
})

onUnmounted(() => {
  window.removeEventListener('click', clickOutside)
  if (reminderTimer) clearInterval(reminderTimer)
})
watch(() => currentUser.value?.id, () => { if (process.client) void refreshTicketReminders() })
</script>

<template>
  <header
    class="fixed left-0 top-0 z-50 h-[80px] w-full border-b border-white/10 bg-[#101214]/95 backdrop-blur-[18px]">
    <div class="mx-auto flex h-full w-full max-w-[1280px] items-center justify-between px-6 md:px-10">
      <!-- LOGO + MAIN NAVIGATION -->
      <div class="flex items-center gap-8 xl:gap-10">
        <NuxtLink to="/"
          class="flex items-center gap-2 text-5xl font-black leading-none text-[#f31220] transition-all hover:scale-105">
          <span>CineAI</span>
        </NuxtLink>

        <!-- Desktop Navigation -->
        <nav class="hidden items-center gap-6 text-[1.05rem] font-semibold text-[#aeb2b8] xl:gap-8 xl:text-[1.12rem] lg:flex">
          <!-- LỊCH CHIẾU -->
          <NuxtLink to="/showtimes" class="whitespace-nowrap transition-colors hover:text-white"
            active-class="border-b-2 border-[#f31220] pb-1 text-white">
            Lịch Chiếu
          </NuxtLink>

          <!-- PHIM: đi thẳng tới /products -->
          <NuxtLink to="/products" class="whitespace-nowrap transition-colors hover:text-white" active-class="text-white">
            Phim
          </NuxtLink>

          <!-- RẠP CHIẾU (Dropdown) -->
          <div class="relative branch-dropdown-wrap">
            <button @click.stop="showBranchDropdown = !showBranchDropdown; showMovieDropdown = false"
              class="flex items-center gap-1 whitespace-nowrap font-semibold transition-colors hover:text-white focus:outline-none">
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
          <NuxtLink to="/promotions" class="whitespace-nowrap transition-colors hover:text-white"
            active-class="border-b-2 border-[#f31220] pb-1 text-white">
            Khuyến Mãi
          </NuxtLink>

          <!-- TIN TỨC / REVIEW -->
          <NuxtLink to="/news" class="whitespace-nowrap transition-colors hover:text-white"
            active-class="border-b-2 border-[#f31220] pb-1 text-white">
            Tin Điện Ảnh
          </NuxtLink>

          <!-- KHÁM PHÁ AI -->
          <NuxtLink to="/ai-discovery"
            class="flex items-center gap-1.5 whitespace-nowrap font-black text-[#f31220] transition-opacity hover:opacity-80">
            <span class="material-symbols-outlined text-sm">auto_awesome</span>
            Khám Phá AI
          </NuxtLink>
        </nav>
      </div>

      <!-- RIGHT ACTIONS (SEARCH, PROFILE, MOBILE MENU BUTTON) -->
      <div class="flex items-center gap-3">
        <!-- Search Button -->
        <button @click="navigateTo('/ai-discovery')"
          class="rounded-full p-2 text-[#f31220] transition-colors hover:bg-white/5 hover:text-[#ff4a56]"
          title="Trợ lý AI (đang phát triển)">
          <span class="material-symbols-outlined text-xl">smart_toy</span>
        </button>

        <div v-if="isAuthenticated && currentUser?.role === 'customer'" class="relative ticket-notification-wrap">
          <button class="relative flex h-10 w-10 items-center justify-center rounded-full text-[#aeb2b8] transition-colors hover:bg-white/5 hover:text-white" title="Nhắc lịch chiếu" @click.stop="showTicketNotifications = !showTicketNotifications">
            <span class="material-symbols-outlined">notifications</span>
            <span v-if="ticketNotifications.length" class="absolute right-0.5 top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-600 px-1 text-[9px] font-black text-white">{{ ticketNotifications.length }}</span>
          </button>
          <transition enter-active-class="transition duration-100" enter-from-class="scale-95 opacity-0" enter-to-class="scale-100 opacity-100" leave-active-class="transition duration-75" leave-from-class="scale-100 opacity-100" leave-to-class="scale-95 opacity-0">
            <div v-if="showTicketNotifications" class="glass-panel absolute right-0 z-50 mt-3 w-[min(22rem,calc(100vw-2rem))] rounded-2xl border border-glass-stroke bg-surface p-3 shadow-2xl">
              <div class="flex items-center justify-between border-b border-glass-stroke/40 px-2 pb-3"><div><b class="block text-sm text-white">Nhắc lịch chiếu</b><span class="text-[10px] text-on-surface-variant">Các vé trong 24 giờ tới</span></div><NuxtLink to="/profile/tickets" class="text-xs font-bold text-primary-container" @click="showTicketNotifications = false">Vé của tôi</NuxtLink></div>
              <div v-if="ticketNotifications.length" class="mt-2 space-y-1">
                <NuxtLink v-for="ticket in ticketNotifications" :key="ticket.id" to="/profile/tickets" class="flex gap-3 rounded-xl p-2.5 hover:bg-white/5" @click="showTicketNotifications = false">
                  <img :src="ticket.poster" :alt="ticket.movieTitle" class="h-14 w-10 rounded-md object-cover">
                  <span class="min-w-0"><b class="block truncate text-xs text-white">{{ ticket.movieTitle }}</b><span class="mt-1 block text-[11px] text-violet-300">{{ reminderText(ticket) }}</span><span class="block truncate text-[10px] text-on-surface-variant">Phòng {{ ticket.screenName }} · Ghế {{ ticket.seats.join(', ') }}</span></span>
                </NuxtLink>
              </div>
              <div v-else class="px-3 py-8 text-center"><span class="material-symbols-outlined text-3xl text-gray-600">notifications_none</span><p class="mt-1 text-xs text-on-surface-variant">Không có suất chiếu nào trong 24 giờ tới.</p></div>
            </div>
          </transition>
        </div>

        <!-- PROFILE / AUTH -->
        <template v-if="isAdminPreview">
          <div class="hidden items-center gap-2 rounded-xl border border-amber-300/20 bg-amber-300/10 px-3 py-2 text-xs font-bold text-amber-200 sm:flex">
            <span class="material-symbols-outlined text-base">visibility</span>
            Bản xem trước
          </div>
        </template>

        <template v-else-if="isAuthenticated && currentUser">
          <div class="relative profile-dropdown-wrap">
            <div @click.stop="showProfileDropdown = !showProfileDropdown"
              class="h-9 w-9 cursor-pointer overflow-hidden rounded-full border-2 border-[#f31220] shadow-[0_0_10px_rgba(229,9,20,0.3)] transition-all hover:scale-105 active:scale-95">
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

                <NuxtLink v-if="currentUser.role === 'customer'" to="/profile"
                  @click="showProfileDropdown = false"
                  class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:bg-white/5 transition-colors">
                  Thông tin cá nhân
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
            class="rounded-xl bg-[#f31220] px-5 py-2 font-bold text-white transition-all hover:scale-105 hover:bg-[#d60915]">
            Đăng Nhập
          </NuxtLink>
        </template>

        <!-- Mobile Menu Hamburger Button -->
        <button @click="showMobileMenu = !showMobileMenu"
          class="p-2 text-[#aeb2b8] hover:text-white focus:outline-none lg:hidden">
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

          <NuxtLink :to="{ path: '/products', query: { status: 'NOW_SHOWING' } }" @click="showMobileMenu = false"
            class="text-on-surface py-2 border-b border-glass-stroke/30">
            Phim Đang Chiếu
          </NuxtLink>

          <NuxtLink :to="{ path: '/products', query: { status: 'UPCOMING' } }" @click="showMobileMenu = false"
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

  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/store/user'

const userStore = useUserStore()

const { currentUser, isAuthenticated } = storeToRefs(userStore)

const showProfileDropdown = ref(false)
const showBranchDropdown = ref(false)

const branches = [
  'CineAI Hùng Vương',
  'CineAI Sala Q2',
  'CineAI Nguyễn Du',
  'CineAI Vincom Bà Triệu',
  'CineAI Đà Nẵng Plaza'
]

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
  if (!target.closest('.branch-dropdown-wrap')) {
    showBranchDropdown.value = false
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
class="fixed top-0 left-0 w-full z-50 bg-surface/60 backdrop-blur-[32px] border-b border-glass-stroke h-[64px]"
>
<div
class="max-w-container-max mx-auto px-6 md:px-margin-desktop h-full flex items-center justify-between"
>
<!-- LOGO + MENU -->
<div class="flex items-center gap-8">
<NuxtLink
  to="/"
  class="font-headline-md text-headline-md font-bold text-primary-container hover:scale-105 transition-all"
>
  CineAI
</NuxtLink>

<nav
class="hidden md:flex items-center gap-6 font-body-md text-body-md"
>
<NuxtLink
to="/products"
class="text-on-surface-variant hover:text-on-surface transition-colors"
active-class="text-on-surface font-bold border-b-2 border-primary-container pb-1"
>
Sản phẩm
</NuxtLink>

<!-- RẠP CHIẾU -->
<div
class="relative branch-dropdown-wrap"
>
<button
@click.stop="showBranchDropdown=!showBranchDropdown"
class="text-on-surface-variant hover:text-on-surface transition-colors flex items-center gap-1 font-medium focus:outline-none"
>
Rạp Chiếu
<span class="material-symbols-outlined text-xs select-none">
keyboard_arrow_down
</span>
</button>

<transition
enter-active-class="transition duration-100 ease-out"
enter-from-class="transform scale-95 opacity-0"
enter-to-class="transform scale-100 opacity-100"
leave-active-class="transition duration-75 ease-in"
leave-from-class="transform scale-100 opacity-100"
leave-to-class="transform scale-95 opacity-0"
>
<div
v-if="showBranchDropdown"
class="absolute left-0 mt-3 w-56 rounded-2xl bg-surface border border-glass-stroke shadow-2xl p-2 z-50 glass-panel"
>
<a
v-for="b in branches"
:key="b"
href="#"
@click.prevent="showBranchDropdown=false"
class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors"
>
{{b}}
</a>
</div>
</transition>
</div>

<!-- AI -->
<NuxtLink
to="/ai-discovery"
class="flex items-center gap-1 text-primary-container font-bold hover:opacity-80 transition-opacity"
>
<span class="material-symbols-outlined text-sm">
auto_awesome
</span>
Khám Phá AI
</NuxtLink>
</nav>
</div>

<!-- PROFILE -->
<div
class="flex items-center gap-6"
>
<template v-if="isAuthenticated && currentUser">
<div
class="relative profile-dropdown-wrap"
>
<div
@click.stop="showProfileDropdown=!showProfileDropdown"
class="w-9 h-9 rounded-full overflow-hidden border-2 border-primary-container cursor-pointer hover:scale-105 active:scale-95 transition-all shadow-[0_0_10px_rgba(229,9,20,0.3)]"
>
<img
class="w-full h-full object-cover"
src="https://lh3.googleusercontent.com/aida-public/AB6AXuDAq3Ng_339WB6mfv_mphK39dGLHMFszhx-AgYKMNAvdIBLaztowKDKDJpjtfA1Hc4jtWnPWz-O1b3Xl4xNoHEyMW1Bf6zs9uyhZGSAweY4AhvQFeh3HyIasFX6W2bT7swfWEEUAQj4wOEWFCuLZR-tYeEf6icRjw1AX3rtxEilO1_XTlXh7u73vegugRIYMB-OuZT8VKVaoS3YbMPNSw30Kyi-OSCHogqRKyoYdEVuLlJOEqJo2UTT1aXKfDROvvaMuTmh2lPPsUsn"
alt="User Profile Picture"
/>
</div>

<transition
enter-active-class="transition duration-100 ease-out"
enter-from-class="transform scale-95 opacity-0"
enter-to-class="transform scale-100 opacity-100"
leave-active-class="transition duration-75 ease-in"
leave-from-class="transform scale-100 opacity-100"
leave-to-class="transform scale-95 opacity-0"
>
<div
v-if="showProfileDropdown"
class="absolute right-0 mt-3 w-64 rounded-2xl bg-surface border border-glass-stroke shadow-2xl p-2 z-50 glass-panel"
>
<div
class="px-4 py-3 border-b border-glass-stroke/40 mb-2"
>
<h5 class="text-xs font-bold text-on-surface truncate">
{{currentUser.name}}
</h5>
<span class="text-[10px] text-on-surface-variant truncate block mt-0.5">
{{currentUser.email}}
</span>
</div>

<NuxtLink
v-if="currentUser.role==='customer'"
to="/profile/tickets"
@click="showProfileDropdown=false"
class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:bg-white/5"
>
🎟 Vé của tôi
</NuxtLink>

<NuxtLink
v-if="currentUser.role==='admin'"
to="/admin/dashboard"
@click="showProfileDropdown=false"
class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:bg-white/5"
>
⚙ Quản trị hệ thống
</NuxtLink>

<NuxtLink
v-if="currentUser.role==='branch-admin'"
to="/branch-admin/dashboard"
@click="showProfileDropdown=false"
class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:bg-white/5"
>
🏢 Quản lý chi nhánh
</NuxtLink>

<button
@click="handleLogout"
class="w-full text-left px-4 py-2.5 rounded-xl text-xs text-red-400 hover:bg-red-500/10 border-t border-glass-stroke/40 mt-2"
>
🚪 Đăng xuất
</button>
</div>
</transition>
</div>
</template>

<template v-else>
<NuxtLink
to="/login"
class="bg-primary-container text-on-primary-container px-5 py-2 rounded-xl font-label-md font-bold hover:scale-105 transition-all ai-glow"
>
Đăng Nhập
</NuxtLink>
</template>
</div>
</div>
</header>
</template>


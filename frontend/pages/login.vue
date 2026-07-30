<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'default'
})

const userStore = useUserStore()
const route = useRoute()

const email = ref('customer@gmail.com')
const password = ref('customer123')
const role = ref<'customer' | 'admin'>('customer')
const error = ref('')
const showPassword = ref(false)
const submitting = ref(false)

const credentialsHelp = {
  customer: { email: 'customer@gmail.com', password: 'customer123', desc: 'Tài khoản khách hàng mặc định' },
  admin: { email: 'admin@cineai.vn', password: 'admin123', desc: 'Tài khoản Quản trị viên hệ thống' }
}

async function handleLogin() {
  error.value = ''

  const identifier = email.value.trim()
  const secret = password.value
  if (!identifier || !secret) {
    error.value = 'Vui lòng nhập email/số điện thoại và mật khẩu!'
    return
  }

  submitting.value = true
  const success = await userStore.login(identifier, secret)
  submitting.value = false

  if (success) {
    if (userStore.currentUser?.role === 'admin') {
      navigateTo('/admin/dashboard')
    } else if (userStore.currentUser?.role === 'branch-admin') {
      navigateTo('/branch-admin/dashboard')
    } else {
      const requestedRedirect = Array.isArray(route.query.redirect)
        ? route.query.redirect[0]
        : route.query.redirect
      const safeRedirect = typeof requestedRedirect === 'string'
        && requestedRedirect.startsWith('/')
        && !requestedRedirect.startsWith('//')
        ? requestedRedirect
        : '/products'
      await navigateTo(safeRedirect)
    }
  } else {
    error.value = userStore.authError === 'Invalid credentials'
      ? 'Email, số điện thoại hoặc mật khẩu không chính xác!'
      : userStore.authError || 'Không thể đăng nhập. Vui lòng thử lại!'
  }
}

function selectRole(newRole: 'customer' | 'admin') {
  role.value = newRole
  email.value = credentialsHelp[newRole].email
  password.value = credentialsHelp[newRole].password
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center py-16 px-4">
    <div
      class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat opacity-10 pointer-events-none z-0">
    </div>

    <div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-8 relative z-10 shadow-2xl">
      <div class="text-center mb-8">
        <h1 class="font-headline-xl text-3xl font-bold text-on-surface mb-2">Đăng Nhập</h1>
        <p class="text-xs text-on-surface-variant">Chào mừng đến với hệ thống vé xem phim thông minh CineAI</p>
      </div>

      <!-- Role Selector Tabs -->
      <div class="grid grid-cols-2 gap-2 bg-surface-container-low border border-glass-stroke p-1 rounded-xl mb-6">
        <button type="button" @click="selectRole('customer')"
          class="py-2 text-xs font-semibold rounded-lg transition-all"
          :class="role === 'customer' ? 'bg-primary-container text-white' : 'text-on-surface-variant hover:text-on-surface'">
          Khách hàng
        </button>
        <button type="button" @click="selectRole('admin')" class="py-2 text-xs font-semibold rounded-lg transition-all"
          :class="role === 'admin' ? 'bg-neutral-800 border border-white/10 text-white' : 'text-on-surface-variant hover:text-on-surface'">
          Quản trị viên
        </button>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-5">
        <div v-if="error" class="bg-red-950/20 border border-red-500/20 text-red-400 text-xs px-4 py-2.5 rounded-xl">
          ⚠️ {{ error }}
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Email hoặc số
            điện thoại</label>
          <input v-model="email" type="text" required maxlength="255" autocomplete="username"
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Nhập email hoặc số điện thoại" />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Mật khẩu</label>
          <div class="relative">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" required maxlength="128"
              autocomplete="current-password"
              class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
              placeholder="Nhập mật khẩu" />
            <button type="button" class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
              :aria-label="showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'" @click="showPassword = !showPassword">
              <span class="material-symbols-outlined text-lg">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
            </button>
          </div>
        </div>

        <button type="submit" :disabled="submitting"
          class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-105 active:scale-95 transition-all text-sm shadow-lg red-glow disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:scale-100">
          {{ submitting ? 'Đang đăng nhập...' : 'Đăng Nhập' }}
        </button>
      </form>

      <!-- Registration link for customers -->
      <div v-if="role === 'customer'" class="mt-6 text-center text-xs text-on-surface-variant">
        Chưa có tài khoản?
        <NuxtLink to="/register" class="text-primary-container font-bold hover:underline">Đăng ký ngay</NuxtLink>
      </div>

      <!-- Test Accounts Hint -->
      <div class="mt-8 border-t border-glass-stroke/40 pt-4">
        <div class="bg-surface-container-low/60 rounded-xl p-3 border border-glass-stroke/50">
          <span class="text-[10px] font-bold uppercase text-secondary tracking-wider block mb-1">💡 Tài khoản thử nghiệm
            backend</span>
          <p class="text-[11px] text-on-surface-variant leading-relaxed">
            <span class="font-semibold text-on-surface">{{ credentialsHelp[role].email }}</span>
            <br />{{ credentialsHelp[role].desc }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'default'
})

const userStore = useUserStore()

const name = ref('')
const email = ref('')
const error = ref('')

function handleRegister() {
  error.value = ''
  
  if (!name.value || !email.value) {
    error.value = 'Vui lòng nhập đầy đủ thông tin!'
    return
  }

  const success = userStore.register(name.value, email.value)
  if (success) {
    navigateTo('/movies')
  } else {
    error.value = 'Email này đã tồn tại trên hệ thống!'
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center py-16 px-4">
    <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat opacity-10 pointer-events-none z-0"></div>
    
    <div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-8 relative z-10 shadow-2xl">
      <div class="text-center mb-8">
        <h1 class="font-headline-xl text-3xl font-bold text-on-surface mb-2">Đăng Ký Khách Hàng</h1>
        <p class="text-xs text-on-surface-variant">Tạo tài khoản để nhận các gợi ý phim cá nhân hóa từ AI</p>
      </div>

      <!-- Registration Form -->
      <form @submit.prevent="handleRegister" class="space-y-5">
        <div v-if="error" class="bg-red-950/20 border border-red-500/20 text-red-400 text-xs px-4 py-2.5 rounded-xl">
          ⚠️ {{ error }}
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Họ và tên</label>
          <input
            v-model="name"
            type="text"
            required
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Nhập họ và tên của bạn"
          />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Email cá nhân</label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="example@gmail.com"
          />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Mật khẩu</label>
          <input
            type="password"
            required
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Nhập mật khẩu"
          />
        </div>

        <button
          type="submit"
          class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-105 active:scale-95 transition-all text-sm shadow-lg red-glow"
        >
          Đăng Ký Tài Khoản
        </button>
      </form>

      <!-- Back to login link -->
      <div class="mt-6 text-center text-xs text-on-surface-variant">
        Đã có tài khoản?
        <NuxtLink to="/login" class="text-primary-container font-bold hover:underline">Đăng nhập</NuxtLink>
      </div>
    </div>
  </div>
</template>

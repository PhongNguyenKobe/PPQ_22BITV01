<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'default'
})

const userStore = useUserStore()

const name = ref('')
const phone = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const dateOfBirth = ref('')
const gender = ref('')
const error = ref('')
const successMessage = ref('')

async function handleRegister() {
  error.value = ''
  successMessage.value = ''

  if (!name.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Vui lòng điền đầy đủ thông tin bắt buộc!'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Mật khẩu xác nhận không khớp!'
    return
  }

  const success = await userStore.register({
    name: name.value,
    email: email.value,
    phone: phone.value || undefined,
    password: password.value,
    dateOfBirth: dateOfBirth.value || undefined,
    gender: gender.value || undefined,
  })
  if (success) {
    successMessage.value = 'Đăng ký thành công! Đang chuyển hướng...'
    setTimeout(() => navigateTo('/products'), 1000)
  } else {
    error.value = 'Email này đã tồn tại trên hệ thống!'
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center py-16 px-4">
    <div
      class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat opacity-10 pointer-events-none z-0">
    </div>

    <div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-8 relative z-10 shadow-2xl">
      <div class="text-center mb-8">
        <h1 class="font-headline-xl text-3xl font-bold text-on-surface mb-2">Đăng Ký Khách Hàng</h1>
        <p class="text-xs text-on-surface-variant">Tạo tài khoản để nhận các gợi ý phim cá nhân hóa từ AI</p>
      </div>

      <!-- Registration Form -->
      <form @submit.prevent="handleRegister" class="space-y-5">
        <div v-if="successMessage"
          class="bg-green-950/20 border border-green-500/20 text-green-400 text-xs px-4 py-2.5 rounded-xl">
          ✅ {{ successMessage }}
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Họ và tên</label>
          <input v-model="name" type="text" required
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Nhập họ và tên của bạn" />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Số điện
            thoại</label>
          <input v-model="phone" type="tel"
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Nhập số điện thoại" />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Email cá
            nhân</label>
          <input v-model="email" type="email" required
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="example@gmail.com" />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Mật khẩu</label>
          <input v-model="password" type="password" required
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Nhập mật khẩu" />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Xác nhận mật
            khẩu</label>
          <input v-model="confirmPassword" type="password" required
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Nhập lại mật khẩu" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Ngày
              sinh</label>
            <input v-model="dateOfBirth" type="date"
              class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface" />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Giới
              tính</label>
            <select v-model="gender"
              class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface">
              <option value="">Chọn giới tính</option>
              <option value="male">Nam</option>
              <option value="female">Nữ</option>
              <option value="other">Khác</option>
            </select>
          </div>
        </div>

        <button type="submit"
          class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-105 active:scale-95 transition-all text-sm shadow-lg red-glow">
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


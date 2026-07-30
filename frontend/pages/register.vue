<script setup lang="ts">
import { computed, ref } from 'vue'
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
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const phonePattern = /^0(?:3|5|7|8|9)\d{8}$/
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const passwordChecks = computed(() => [
  { label: 'Từ 8 đến 128 ký tự', valid: password.value.length >= 8 && password.value.length <= 128 },
  { label: 'Có ít nhất một chữ thường', valid: /[a-z]/.test(password.value) },
  { label: 'Có ít nhất một chữ in hoa', valid: /[A-Z]/.test(password.value) },
  { label: 'Có ít nhất một chữ số', valid: /\d/.test(password.value) },
  { label: 'Có ít nhất một ký tự đặc biệt', valid: /[^A-Za-z0-9\s]/.test(password.value) },
  { label: 'Không chứa khoảng trắng', valid: !/\s/.test(password.value) },
])
const isPasswordStrong = computed(() => passwordChecks.value.every(check => check.valid))

function normalizePhone() {
  phone.value = phone.value.replace(/\D/g, '').slice(0, 10)
}

async function handleRegister() {
  error.value = ''
  successMessage.value = ''

  const normalizedName = name.value.trim()
  const normalizedEmail = email.value.trim().toLowerCase()

  if (!normalizedName || !phone.value || !normalizedEmail || !password.value || !confirmPassword.value) {
    error.value = 'Vui lòng điền đầy đủ thông tin bắt buộc!'
    return
  }

  if (normalizedName.length < 2) {
    error.value = 'Họ và tên phải có ít nhất 2 ký tự!'
    return
  }

  if (!phonePattern.test(phone.value)) {
    error.value = 'Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 03, 05, 07, 08 hoặc 09!'
    return
  }

  if (!emailPattern.test(normalizedEmail)) {
    error.value = 'Địa chỉ email không hợp lệ!'
    return
  }

  if (!isPasswordStrong.value) {
    error.value = 'Mật khẩu chưa đáp ứng đầy đủ yêu cầu bảo mật!'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Mật khẩu xác nhận không khớp!'
    return
  }

  const success = await userStore.register({
    name: normalizedName,
    email: normalizedEmail,
    phone: phone.value,
    password: password.value,
    dateOfBirth: dateOfBirth.value || undefined,
    gender: gender.value || undefined,
  })
  if (success) {
    successMessage.value = 'Đăng ký thành công! Đang chuyển hướng...'
    setTimeout(() => navigateTo('/products'), 1000)
  } else {
    error.value = userStore.authError || 'Không thể đăng ký tài khoản. Vui lòng thử lại!'
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
          <input v-model="name" type="text" required minlength="2" maxlength="150" autocomplete="name"
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Nhập họ và tên của bạn" />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Số điện
            thoại</label>
          <input v-model="phone" type="tel" required inputmode="numeric" autocomplete="tel"
            minlength="10" maxlength="10" pattern="0(3|5|7|8|9)[0-9]{8}" @input="normalizePhone"
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="Ví dụ: 0912345678" />
          <p class="mt-1.5 text-[11px]" :class="phone.length === 0 || phonePattern.test(phone) ? 'text-on-surface-variant' : 'text-red-400'">
            Gồm 10 chữ số, bắt đầu bằng 03, 05, 07, 08 hoặc 09.
          </p>
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Email cá
            nhân</label>
          <input v-model="email" type="email" required maxlength="255" autocomplete="email"
            class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
            placeholder="example@gmail.com" />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Mật khẩu</label>
          <div class="relative">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" required minlength="8" maxlength="128"
              autocomplete="new-password"
              class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
              placeholder="Nhập mật khẩu mạnh" />
            <button type="button" class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
              :aria-label="showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'" @click="showPassword = !showPassword">
              <span class="material-symbols-outlined text-lg">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
            </button>
          </div>
          <div class="mt-2 grid grid-cols-1 gap-1 sm:grid-cols-2">
            <p v-for="check in passwordChecks" :key="check.label" class="flex items-center gap-1 text-[11px]"
              :class="check.valid ? 'text-green-400' : 'text-on-surface-variant'">
              <span class="material-symbols-outlined text-sm">{{ check.valid ? 'check_circle' : 'radio_button_unchecked' }}</span>
              {{ check.label }}
            </p>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Xác nhận mật
            khẩu</label>
          <div class="relative">
            <input v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" required minlength="8"
              maxlength="128" autocomplete="new-password"
              class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
              placeholder="Nhập lại mật khẩu" />
            <button type="button" class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
              :aria-label="showConfirmPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
              @click="showConfirmPassword = !showConfirmPassword">
              <span class="material-symbols-outlined text-lg">{{ showConfirmPassword ? 'visibility_off' : 'visibility' }}</span>
            </button>
          </div>
          <p v-if="confirmPassword" class="mt-1.5 text-[11px]"
            :class="password === confirmPassword ? 'text-green-400' : 'text-red-400'">
            {{ password === confirmPassword ? 'Mật khẩu xác nhận đã khớp.' : 'Mật khẩu xác nhận chưa khớp.' }}
          </p>
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


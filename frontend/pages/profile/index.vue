<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { usersApi } from '~/services/api'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const userStore = useUserStore()
const loading = ref(true)
const saving = ref(false)
const profileError = ref('')
const profileSuccess = ref('')
const email = ref('')
const fullName = ref('')
const phone = ref('')
const dateOfBirth = ref('')
const gender = ref('')

const changingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const phonePattern = /^0(?:3|5|7|8|9)\d{8}$/
const today = new Date().toISOString().slice(0, 10)
const passwordChecks = computed(() => [
  { label: 'Từ 8 đến 128 ký tự', valid: newPassword.value.length >= 8 && newPassword.value.length <= 128 },
  { label: 'Có chữ thường', valid: /[a-z]/.test(newPassword.value) },
  { label: 'Có chữ in hoa', valid: /[A-Z]/.test(newPassword.value) },
  { label: 'Có chữ số', valid: /\d/.test(newPassword.value) },
  { label: 'Có ký tự đặc biệt', valid: /[^A-Za-z0-9\s]/.test(newPassword.value) },
  { label: 'Không có khoảng trắng', valid: !/\s/.test(newPassword.value) },
])
const isPasswordStrong = computed(() => passwordChecks.value.every(item => item.valid))

function apiErrorMessage(error: any, fallback: string): string {
  const detail = error?.message
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map(item => item?.msg || String(item)).join('. ')
  return fallback
}

function normalizePhone() {
  phone.value = phone.value.replace(/\D/g, '').slice(0, 10)
}

async function loadProfile() {
  loading.value = true
  profileError.value = ''
  try {
    const profile = await usersApi.getProfile()
    email.value = profile.email
    fullName.value = profile.name
    phone.value = profile.phone || ''
    dateOfBirth.value = profile.dateOfBirth || ''
    gender.value = profile.gender || ''
  } catch (error) {
    profileError.value = apiErrorMessage(error, 'Không thể tải thông tin cá nhân.')
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  profileError.value = ''
  profileSuccess.value = ''
  const normalizedName = fullName.value.trim()
  if (normalizedName.length < 2) {
    profileError.value = 'Họ và tên phải có ít nhất 2 ký tự.'
    return
  }
  if (!phonePattern.test(phone.value)) {
    profileError.value = 'Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 03, 05, 07, 08 hoặc 09.'
    return
  }
  if (dateOfBirth.value && dateOfBirth.value > today) {
    profileError.value = 'Ngày sinh không được ở tương lai.'
    return
  }

  saving.value = true
  try {
    await usersApi.updateProfile({
      full_name: normalizedName,
      phone: phone.value,
      date_of_birth: dateOfBirth.value || null,
      gender: gender.value || null,
    })
    await userStore.refreshCurrentUser()
    profileSuccess.value = 'Thông tin cá nhân đã được cập nhật.'
  } catch (error) {
    profileError.value = apiErrorMessage(error, 'Không thể cập nhật thông tin cá nhân.')
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''
  if (!currentPassword.value) {
    passwordError.value = 'Vui lòng nhập mật khẩu hiện tại.'
    return
  }
  if (!isPasswordStrong.value) {
    passwordError.value = 'Mật khẩu mới chưa đáp ứng yêu cầu bảo mật.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'Mật khẩu xác nhận không khớp.'
    return
  }
  if (newPassword.value === currentPassword.value) {
    passwordError.value = 'Mật khẩu mới phải khác mật khẩu hiện tại.'
    return
  }

  changingPassword.value = true
  try {
    await usersApi.changePassword({
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    passwordSuccess.value = 'Mật khẩu đã được thay đổi thành công.'
  } catch (error) {
    passwordError.value = apiErrorMessage(error, 'Không thể thay đổi mật khẩu.')
  } finally {
    changingPassword.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <main class="mx-auto max-w-6xl px-4 py-10 md:px-8">
    <section class="mb-8 flex flex-col gap-4 border-b border-glass-stroke pb-6 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-primary-container">Tài khoản CineAI</p>
        <h1 class="text-3xl font-black text-on-surface">Thông tin cá nhân</h1>
        <p class="mt-2 text-sm text-on-surface-variant">Quản lý hồ sơ và bảo mật tài khoản của bạn.</p>
      </div>
      <NuxtLink to="/profile/tickets"
        class="inline-flex items-center justify-center gap-2 rounded-xl border border-glass-stroke bg-white/5 px-4 py-2.5 text-sm font-bold text-on-surface hover:bg-white/10">
        <span class="material-symbols-outlined text-lg">confirmation_number</span>
        Vé của tôi
      </NuxtLink>
    </section>

    <div v-if="loading" class="py-24 text-center text-on-surface-variant">
      <span class="material-symbols-outlined animate-spin text-4xl">progress_activity</span>
      <p class="mt-3 text-sm">Đang tải thông tin...</p>
    </div>

    <div v-else class="grid gap-6 lg:grid-cols-5">
      <form class="glass-panel rounded-2xl border border-glass-stroke p-6 lg:col-span-3" @submit.prevent="saveProfile">
        <div class="mb-6 flex items-center gap-4">
          <div class="flex h-14 w-14 items-center justify-center rounded-full bg-primary-container text-xl font-black text-white">
            {{ (fullName || email).slice(0, 2).toUpperCase() }}
          </div>
          <div>
            <h2 class="text-lg font-black text-on-surface">Hồ sơ của bạn</h2>
            <p class="text-xs text-on-surface-variant">Email chỉ dùng để nhận diện tài khoản và chưa thể thay đổi trực tiếp.</p>
          </div>
        </div>

        <div v-if="profileError" class="mb-5 rounded-xl border border-red-500/20 bg-red-950/20 px-4 py-3 text-xs text-red-400">
          {{ profileError }}
        </div>
        <div v-if="profileSuccess" class="mb-5 rounded-xl border border-green-500/20 bg-green-950/20 px-4 py-3 text-xs text-green-400">
          {{ profileSuccess }}
        </div>

        <div class="grid gap-5 sm:grid-cols-2">
          <label class="sm:col-span-2">
            <span class="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Họ và tên</span>
            <input v-model="fullName" required minlength="2" maxlength="150" autocomplete="name"
              class="w-full rounded-xl border border-glass-stroke bg-surface-container px-4 py-3 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary-container" />
          </label>

          <label class="sm:col-span-2">
            <span class="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Email</span>
            <input v-model="email" disabled
              class="w-full cursor-not-allowed rounded-xl border border-glass-stroke bg-white/5 px-4 py-3 text-sm text-on-surface-variant opacity-70" />
          </label>

          <label>
            <span class="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Số điện thoại</span>
            <input v-model="phone" required type="tel" inputmode="numeric" autocomplete="tel" maxlength="10"
              pattern="0(3|5|7|8|9)[0-9]{8}" placeholder="0912345678" @input="normalizePhone"
              class="w-full rounded-xl border border-glass-stroke bg-surface-container px-4 py-3 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary-container" />
          </label>

          <label>
            <span class="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Ngày sinh</span>
            <input v-model="dateOfBirth" type="date" :max="today"
              class="w-full rounded-xl border border-glass-stroke bg-surface-container px-4 py-3 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary-container" />
          </label>

          <label>
            <span class="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Giới tính</span>
            <select v-model="gender"
              class="w-full rounded-xl border border-glass-stroke bg-surface-container px-4 py-3 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary-container">
              <option value="">Không cung cấp</option>
              <option value="male">Nam</option>
              <option value="female">Nữ</option>
              <option value="other">Khác</option>
            </select>
          </label>
        </div>

        <button type="submit" :disabled="saving"
          class="mt-6 rounded-xl bg-primary-container px-6 py-3 text-sm font-black text-white shadow-lg transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-60">
          {{ saving ? 'Đang lưu...' : 'Lưu thay đổi' }}
        </button>
      </form>

      <form class="glass-panel rounded-2xl border border-glass-stroke p-6 lg:col-span-2" @submit.prevent="changePassword">
        <h2 class="text-lg font-black text-on-surface">Đổi mật khẩu</h2>
        <p class="mt-1 text-xs text-on-surface-variant">Bạn cần xác nhận mật khẩu hiện tại trước khi thay đổi.</p>

        <div v-if="passwordError" class="mt-5 rounded-xl border border-red-500/20 bg-red-950/20 px-4 py-3 text-xs text-red-400">
          {{ passwordError }}
        </div>
        <div v-if="passwordSuccess" class="mt-5 rounded-xl border border-green-500/20 bg-green-950/20 px-4 py-3 text-xs text-green-400">
          {{ passwordSuccess }}
        </div>

        <div class="mt-5 space-y-5">
          <label class="block">
            <span class="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Mật khẩu hiện tại</span>
            <div class="relative">
              <input v-model="currentPassword" :type="showCurrentPassword ? 'text' : 'password'" required
                autocomplete="current-password"
                class="w-full rounded-xl border border-glass-stroke bg-surface-container px-4 py-3 pr-12 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary-container" />
              <button type="button" class="absolute inset-y-0 right-0 px-4 text-on-surface-variant"
                @click="showCurrentPassword = !showCurrentPassword">
                <span class="material-symbols-outlined text-lg">{{ showCurrentPassword ? 'visibility_off' : 'visibility' }}</span>
              </button>
            </div>
          </label>

          <label class="block">
            <span class="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Mật khẩu mới</span>
            <div class="relative">
              <input v-model="newPassword" :type="showNewPassword ? 'text' : 'password'" required minlength="8"
                maxlength="128" autocomplete="new-password"
                class="w-full rounded-xl border border-glass-stroke bg-surface-container px-4 py-3 pr-12 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary-container" />
              <button type="button" class="absolute inset-y-0 right-0 px-4 text-on-surface-variant"
                @click="showNewPassword = !showNewPassword">
                <span class="material-symbols-outlined text-lg">{{ showNewPassword ? 'visibility_off' : 'visibility' }}</span>
              </button>
            </div>
          </label>

          <div class="grid grid-cols-2 gap-1">
            <p v-for="check in passwordChecks" :key="check.label" class="flex items-center gap-1 text-[11px]"
              :class="check.valid ? 'text-green-400' : 'text-on-surface-variant'">
              <span class="material-symbols-outlined text-sm">{{ check.valid ? 'check_circle' : 'radio_button_unchecked' }}</span>
              {{ check.label }}
            </p>
          </div>

          <label class="block">
            <span class="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Xác nhận mật khẩu mới</span>
            <div class="relative">
              <input v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" required minlength="8"
                maxlength="128" autocomplete="new-password"
                class="w-full rounded-xl border border-glass-stroke bg-surface-container px-4 py-3 pr-12 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary-container" />
              <button type="button" class="absolute inset-y-0 right-0 px-4 text-on-surface-variant"
                @click="showConfirmPassword = !showConfirmPassword">
                <span class="material-symbols-outlined text-lg">{{ showConfirmPassword ? 'visibility_off' : 'visibility' }}</span>
              </button>
            </div>
            <span v-if="confirmPassword" class="mt-1.5 block text-[11px]"
              :class="newPassword === confirmPassword ? 'text-green-400' : 'text-red-400'">
              {{ newPassword === confirmPassword ? 'Mật khẩu đã khớp.' : 'Mật khẩu chưa khớp.' }}
            </span>
          </label>
        </div>

        <button type="submit" :disabled="changingPassword"
          class="mt-6 w-full rounded-xl border border-primary-container/40 bg-primary-container/10 px-6 py-3 text-sm font-black text-primary-container transition hover:bg-primary-container hover:text-white disabled:cursor-not-allowed disabled:opacity-60">
          {{ changingPassword ? 'Đang cập nhật...' : 'Đổi mật khẩu' }}
        </button>
      </form>
    </div>
  </main>
</template>

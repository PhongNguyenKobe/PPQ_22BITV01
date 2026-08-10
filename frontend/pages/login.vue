<script setup lang="ts">
import { computed, ref, onUnmounted } from 'vue'
import { useUserStore } from '~/store/user'
import { authService } from '~/services/api'

definePageMeta({
  layout: 'default'
})

const userStore = useUserStore()
const route = useRoute()

// Vai trò được chọn: 'customer' | 'admin'
const roleMode = ref<'customer' | 'admin'>('customer')

// Các step cho luồng Khách hàng: 'identifier' | 'login' | 'register_step1' | 'register_step2' | 'otp' | 'forgot_password' | 'forgot_otp' | 'reset_password'
const step = ref<'identifier' | 'login' | 'register_step1' | 'register_step2' | 'otp' | 'forgot_password' | 'forgot_otp' | 'reset_password'>('identifier')

// Form dữ liệu chung
const identifier = ref('')
const password = ref('')
const confirmPassword = ref('')
const name = ref('')
const phone = ref('')
const email = ref('')
const dateOfBirth = ref('')
const gender = ref('')
const address = ref('')
const noMarketingEmails = ref(false) // Checkbox: Không đồng ý nhận email khuyến mãi
const otpCode = ref('')

// Form đăng nhập trực tiếp của Admin
const adminEmail = ref('')
const adminPassword = ref('')

const error = ref('')
const successMessage = ref('')
const submitting = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Logic đếm ngược gửi lại OTP
const countdown = ref(0)
let timerInterval: NodeJS.Timeout | null = null

function startCountdown() {
  countdown.value = 60
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      if (timerInterval) clearInterval(timerInterval)
    }
  }, 1000)
}

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

// Mẫu Regex
const phonePattern = /^0(3|5|7|8|9)\d{8}$/
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// Validate Mật khẩu
const passwordChecks = computed(() => {
  const val = password.value
  return [
    { label: 'Từ 8 đến 16 ký tự', valid: val.length >= 8 && val.length <= 16 },
    { label: 'Có ít nhất một chữ thường', valid: /[a-z]/.test(val) },
    { label: 'Có ít nhất một chữ in hoa', valid: /[A-Z]/.test(val) },
    { label: 'Có ít nhất một chữ số', valid: /\d/.test(val) },
    { label: 'Có ít nhất một ký tự đặc biệt', valid: /[^A-Za-z0-9\s]/.test(val) },
    { label: 'Không chứa khoảng trắng', valid: !/\s/.test(val) },
  ]
})
const isPasswordStrong = computed(() => passwordChecks.value.every(check => check.valid))

// Chuẩn hóa số điện thoại chỉ nhận chữ số
function normalizePhone(field: 'phone' | 'identifier') {
  if (field === 'phone') {
    phone.value = phone.value.replace(/\D/g, '').slice(0, 10)
  } else {
    const val = identifier.value.trim()
    if (/^\d+$/.test(val)) {
      identifier.value = val.slice(0, 10)
    }
  }
}

// Bấm chuyển đổi vai trò (Khách hàng / Quản trị viên)
function switchRole(mode: 'customer' | 'admin') {
  roleMode.value = mode
  error.value = ''
  successMessage.value = ''
  
  if (mode === 'admin') {
    adminEmail.value = ''
    adminPassword.value = ''
  } else {
    identifier.value = ''
    password.value = ''
    step.value = 'identifier'
  }
}

// Gợi ý tài khoản test
const testAccounts = {
  customer: { email: 'customer@gmail.com', password: 'customer123', desc: 'Khách hàng demo' },
  admin: { email: 'admin@cineai.vn', password: 'admin123', desc: 'Quản trị viên hệ thống' }
}

function fillTestAccount(type: 'customer' | 'admin') {
  error.value = ''
  successMessage.value = ''
  if (type === 'admin') {
    adminEmail.value = testAccounts.admin.email
    adminPassword.value = testAccounts.admin.password
  } else {
    identifier.value = testAccounts.customer.email
    step.value = 'identifier'
  }
}

// BƯỚC 1: Kiểm tra identifier (Email / SĐT)
async function handleCheckIdentifier() {
  error.value = ''
  const idValue = identifier.value.trim()

  if (!idValue) {
    error.value = 'Vui lòng nhập email hoặc số điện thoại!'
    return
  }

  const isEmail = idValue.includes('@')
  if (isEmail) {
    if (!emailPattern.test(idValue)) {
      error.value = 'Địa chỉ email không đúng định dạng!'
      return
    }
  } else {
    if (!/^\d+$/.test(idValue) || idValue.length !== 10 || !idValue.startsWith('0')) {
      error.value = 'Số điện thoại phải gồm 10 chữ số và bắt đầu bằng số 0!'
      return
    }
    if (!phonePattern.test(idValue)) {
      error.value = 'Số điện thoại không đúng định dạng nhà mạng Việt Nam!'
      return
    }
  }

  submitting.value = true
  try {
    const res = await authService.checkIdentifier(idValue)
    submitting.value = false

    if (res.exists) {
      step.value = 'login'
    } else {
      if (isEmail) {
        email.value = idValue
        phone.value = ''
      } else {
        phone.value = idValue
        email.value = ''
      }
      step.value = 'register_step1'
    }
  } catch (err: any) {
    submitting.value = false
    error.value = err.message || 'Đã xảy ra lỗi kết nối. Vui lòng thử lại!'
  }
}

// BƯỚC 2 (Đăng nhập Khách hàng): Nhập mật khẩu
async function handleLogin() {
  error.value = ''
  const idValue = identifier.value.trim()
  const pwdValue = password.value

  if (!pwdValue) {
    error.value = 'Vui lòng nhập mật khẩu!'
    return
  }

  submitting.value = true
  const success = await userStore.login(idValue, pwdValue)
  submitting.value = false

  if (success) {
    await redirectAfterAuth()
  } else {
    console.log("DEBUG LOGIN ERROR:", userStore.authError)
    if (userStore.authError === 'USER_NOT_VERIFIED' || userStore.authError.includes('USER_NOT_VERIFIED')) {
      successMessage.value = 'Tài khoản chưa được xác thực. Đang gửi mã OTP đến email của bạn...'
      try {
        await authService.resendOtp(idValue)
        startCountdown()
        setTimeout(() => {
          successMessage.value = ''
          step.value = 'otp'
        }, 1500)
      } catch (err: any) {
        error.value = err.message || 'Không thể gửi mã OTP xác thực. Vui lòng thử lại!'
      }
    } else {
      error.value = userStore.authError === 'Invalid credentials'
        ? 'Mật khẩu không chính xác!'
        : userStore.authError || 'Không thể đăng nhập. Vui lòng thử lại!'
    }
  }
}

// Đăng nhập Admin / Nhân viên trực tiếp
async function handleAdminLogin() {
  error.value = ''
  const idValue = adminEmail.value.trim()
  const pwdValue = adminPassword.value

  if (!idValue || !pwdValue) {
    error.value = 'Vui lòng điền đầy đủ Email và Mật khẩu!'
    return
  }

  submitting.value = true
  const success = await userStore.login(idValue, pwdValue)
  submitting.value = false

  if (success) {
    await redirectAfterAuth()
  } else {
    error.value = userStore.authError === 'Invalid credentials'
      ? 'Email hoặc mật khẩu không chính xác!'
      : userStore.authError || 'Không thể đăng nhập hệ thống quản trị!'
  }
}

// BƯỚC 3 (Đăng ký 1): Nhập Email, SĐT, Mật khẩu
function handleRegisterStep1() {
  error.value = ''

  if (!email.value.trim() || !phone.value.trim() || !password.value || !confirmPassword.value) {
    error.value = 'Vui lòng điền đầy đủ các thông tin bắt buộc!'
    return
  }

  if (!emailPattern.test(email.value.trim().toLowerCase())) {
    error.value = 'Địa chỉ email không hợp lệ!'
    return
  }

  if (!phonePattern.test(phone.value.trim())) {
    error.value = 'Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 03, 05, 07, 08 hoặc 09!'
    return
  }

  if (!isPasswordStrong.value) {
    error.value = 'Mật khẩu chưa đáp ứng đầy đủ yêu cầu bảo mật!'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Mật khẩu xác nhận không trùng khớp!'
    return
  }

  step.value = 'register_step2'
}

// BƯỚC 4 (Đăng ký 2): Nhập Thông tin cá nhân & Submit
async function handleRegisterStep2() {
  error.value = ''
  successMessage.value = ''

  const nameVal = name.value.trim()
  if (!nameVal) {
    error.value = 'Vui lòng nhập họ và tên của bạn!'
    return
  }

  if (nameVal.length < 2) {
    error.value = 'Họ và tên phải có ít nhất 2 ký tự!'
    return
  }

  submitting.value = true
  const success = await userStore.register({
    name: nameVal,
    email: email.value.trim().toLowerCase(),
    phone: phone.value.trim(),
    password: password.value,
    dateOfBirth: dateOfBirth.value || undefined,
    gender: gender.value || undefined,
    address: address.value.trim() || undefined,
    receiveMarketingEmails: !noMarketingEmails.value
  })
  submitting.value = false

  if (success) {
    identifier.value = email.value.trim().toLowerCase()
    successMessage.value = 'Đăng ký thông tin thành công! Một mã xác thực OTP đã được gửi tới email của bạn.'
    startCountdown()
    setTimeout(() => {
      successMessage.value = ''
      step.value = 'otp'
    }, 2000)
  } else {
    error.value = userStore.authError || 'Không thể tạo tài khoản. Vui lòng thử lại!'
  }
}

// BƯỚC 5: Xác thực OTP đăng ký
async function handleVerifyOtp() {
  error.value = ''
  successMessage.value = ''
  const codeVal = otpCode.value.trim()

  if (codeVal.length !== 6) {
    error.value = 'Mã xác thực OTP phải gồm 6 chữ số!'
    return
  }

  submitting.value = true
  const success = await userStore.verifyOtp(identifier.value.trim(), codeVal)
  submitting.value = false

  if (success) {
    successMessage.value = 'Xác thực tài khoản thành công! Đang đăng nhập...'
    setTimeout(async () => {
      await redirectAfterAuth()
    }, 1500)
  } else {
    error.value = userStore.authError || 'Mã xác thực OTP không chính xác hoặc đã hết hạn!'
  }
}

// Gửi lại mã OTP đăng ký
async function handleResendOtp() {
  if (countdown.value > 0) return
  error.value = ''
  successMessage.value = ''

  try {
    const res = await authService.resendOtp(identifier.value.trim())
    successMessage.value = res.message || 'Mã OTP mới đã được gửi tới email của bạn.'
    startCountdown()
  } catch (err: any) {
    error.value = err.message || 'Không thể gửi lại mã OTP. Vui lòng thử lại!'
  }
}

// KHÔI PHỤC MẬT KHẨU - Bước 1: Nhập Email/SĐT để gửi OTP khôi phục
async function handleForgotPassword() {
  error.value = ''
  successMessage.value = ''
  
  const idValue = identifier.value.trim()
  if (!idValue) {
    error.value = 'Vui lòng nhập Email hoặc Số điện thoại để nhận mã khôi phục!'
    return
  }

  submitting.value = true
  const success = await userStore.forgotPassword(idValue)
  submitting.value = false

  if (success) {
    successMessage.value = 'Mã xác thực khôi phục mật khẩu đã được gửi qua email.'
    otpCode.value = ''
    password.value = ''
    confirmPassword.value = ''
    startCountdown()
    setTimeout(() => {
      successMessage.value = ''
      step.value = 'forgot_otp'  // Chuyển qua màn hình nhập OTP trước tiên
    }, 1500)
  } else {
    error.value = userStore.authError || 'Không thể gửi yêu cầu đặt lại mật khẩu. Vui lòng thử lại!'
  }
}

// KHÔI PHỤC MẬT KHẨU - Bước 2: Xác thực mã OTP trước khi cho đổi pass
function handleVerifyForgotOtp() {
  error.value = ''
  const codeVal = otpCode.value.trim()

  if (codeVal.length !== 6) {
    error.value = 'Mã xác thực OTP phải gồm 6 chữ số!'
    return
  }

  // OTP hợp lệ về cấu trúc -> Cho chuyển sang Bước 3 để điền mật khẩu mới
  password.value = ''
  confirmPassword.value = ''
  step.value = 'reset_password'
}

// Gửi lại mã OTP khôi phục mật khẩu
async function handleResendForgotOtp() {
  if (countdown.value > 0) return
  error.value = ''
  successMessage.value = ''

  try {
    await authService.forgotPassword(identifier.value.trim())
    successMessage.value = 'Mã OTP khôi phục mới đã được gửi tới email của bạn.'
    startCountdown()
  } catch (err: any) {
    error.value = err.message || 'Không thể gửi lại mã khôi phục. Vui lòng thử lại!'
  }
}

// KHÔI PHỤC MẬT KHẨU - Bước 3: Đặt mật khẩu mới gửi kèm OTP
async function handleResetPassword() {
  error.value = ''
  successMessage.value = ''

  const idValue = identifier.value.trim()
  const codeVal = otpCode.value.trim()
  const pwdValue = password.value
  const confirmVal = confirmPassword.value

  if (!codeVal || !pwdValue || !confirmVal) {
    error.value = 'Vui lòng điền đầy đủ tất cả các trường!'
    return
  }

  if (!isPasswordStrong.value) {
    error.value = 'Mật khẩu mới chưa đáp ứng đầy đủ yêu cầu bảo mật!'
    return
  }

  if (pwdValue !== confirmVal) {
    error.value = 'Mật khẩu xác nhận không trùng khớp!'
    return
  }

  submitting.value = true
  const success = await userStore.resetPassword({
    identifier: idValue,
    code: codeVal,
    new_password: pwdValue
  })
  submitting.value = false

  if (success) {
    successMessage.value = 'Đặt lại mật khẩu thành công! Vui lòng sử dụng mật khẩu mới để đăng nhập.'
    password.value = ''
    confirmPassword.value = ''
    otpCode.value = ''
    setTimeout(() => {
      successMessage.value = ''
      step.value = 'login'
    }, 2000)
  } else {
    error.value = userStore.authError || 'Đặt lại mật khẩu không thành công. OTP có thể sai hoặc hết hạn.'
  }
}

// Điều hướng sau khi đăng nhập thành công
async function redirectAfterAuth() {
  const role = userStore.currentUser?.role
  if (role === 'admin') {
    await navigateTo('/admin/dashboard')
  } else if (role === 'branch-admin') {
    await navigateTo('/branch-admin/dashboard')
  } else {
    const requestedRedirect = Array.isArray(route.query.redirect)
      ? route.query.redirect[0]
      : route.query.redirect
    const safeRedirect = typeof requestedRedirect === 'string'
      && requestedRedirect.startsWith('/')
      && !requestedRedirect.startsWith('//')
      ? requestedRedirect
      : '/phim'
    await navigateTo(safeRedirect)
  }
}

function goBackToIdentifier() {
  error.value = ''
  step.value = 'identifier'
}

function goBackToRegisterStep1() {
  error.value = ''
  step.value = 'register_step1'
}

function startForgotPassword() {
  error.value = ''
  successMessage.value = ''
  step.value = 'forgot_password'
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center py-16 px-4 relative">
    <div
      class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat opacity-10 pointer-events-none z-0">
    </div>

    <div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-8 relative z-10 shadow-2xl flex flex-col justify-between">
      
      <!-- ROLE SELECTOR TABS -->
      <div 
        v-if="step === 'identifier' || step === 'login'" 
        class="grid grid-cols-2 gap-2 bg-surface-container-low border border-glass-stroke p-1.5 rounded-xl mb-6 w-full"
      >
        <button 
          type="button" 
          @click="switchRole('customer')"
          class="py-2.5 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5"
          :class="roleMode === 'customer' ? 'bg-primary-container text-white shadow' : 'text-on-surface-variant hover:text-on-surface'"
        >
          <span class="material-symbols-outlined text-sm">person</span>
          <span>Khách hàng</span>
        </button>
        <button 
          type="button" 
          @click="switchRole('admin')"
          class="py-2.5 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5"
          :class="roleMode === 'admin' ? 'bg-neutral-800 border border-white/10 text-white shadow' : 'text-on-surface-variant hover:text-on-surface'"
        >
          <span class="material-symbols-outlined text-sm">admin_panel_settings</span>
          <span>Quản trị viên</span>
        </button>
      </div>

      <!-- THÔNG BÁO LỖI HOẶC THÀNH CÔNG -->
      <div v-if="error" class="bg-red-950/20 border border-red-500/20 text-red-400 text-xs px-4 py-2.5 rounded-xl mb-5 flex items-center gap-2">
        <span class="material-symbols-outlined text-sm flex-shrink-0">error</span>
        <span>{{ error }}</span>
      </div>
      <div v-if="successMessage" class="bg-green-950/20 border border-green-500/20 text-green-400 text-xs px-4 py-2.5 rounded-xl mb-5 flex items-center gap-2">
        <span class="material-symbols-outlined text-sm flex-shrink-0">check_circle</span>
        <span>{{ successMessage }}</span>
      </div>

      <!-- ============================================== -->
      <!-- A. LUỒNG KHÁCH HÀNG                            -->
      <!-- ============================================== -->
      <div v-if="roleMode === 'customer'">
        
        <!-- STEP 1: NHẬP SĐT / EMAIL -->
        <div v-if="step === 'identifier'">
          <div class="text-center mb-8">
            <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-2">Đăng nhập hoặc Tạo tài khoản</h1>
            <p class="text-xs text-on-surface-variant">Vui lòng đăng nhập để nhận nhiều ưu đãi</p>
          </div>

          <form @submit.prevent="handleCheckIdentifier" class="space-y-5">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Số điện thoại hoặc Email</label>
              <input 
                v-model="identifier" 
                type="text" 
                required 
                maxlength="255" 
                @input="normalizePhone('identifier')"
                class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="Nhập email hoặc số điện thoại" 
              />
            </div>

            <button 
              type="submit" 
              :disabled="submitting"
              class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg red-glow disabled:cursor-not-allowed disabled:opacity-60"
            >
              {{ submitting ? 'Đang kiểm tra...' : 'Tiếp tục' }}
            </button>
          </form>
        </div>

        <!-- STEP 2: NHẬP MẬT KHẨU ĐỂ ĐĂNG NHẬP -->
        <div v-if="step === 'login'">
          <div class="text-center mb-8">
            <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-2">Nhập Mật Khẩu</h1>
            <p class="text-xs text-on-surface-variant flex items-center justify-center gap-1.5 flex-wrap">
              Tài khoản: <span class="font-semibold text-on-surface">{{ identifier }}</span>
              <button @click="goBackToIdentifier" class="text-primary-container hover:underline text-xs flex items-center ml-0.5">
                (thay đổi)
              </button>
            </p>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-5">
            <div>
              <div class="flex justify-between items-center mb-2">
                <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Mật khẩu</label>
                <button type="button" @click="startForgotPassword" class="text-xs text-primary-container hover:underline font-semibold">
                  Quên mật khẩu?
                </button>
              </div>
              <div class="relative">
                <input 
                  v-model="password" 
                  :type="showPassword ? 'text' : 'password'" 
                  required 
                  maxlength="128"
                  autocomplete="current-password"
                  class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                  placeholder="Nhập mật khẩu của bạn" 
                />
                <button 
                  type="button" 
                  class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
                  @click="showPassword = !showPassword"
                >
                  <span class="material-symbols-outlined text-lg">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
                </button>
              </div>
            </div>

            <div class="flex gap-3 pt-2">
              <button 
                type="button" 
                @click="goBackToIdentifier"
                class="w-1/3 border border-glass-stroke text-on-surface py-3.5 rounded-xl font-bold hover:bg-white/5 active:scale-95 transition-all text-sm"
              >
                Quay lại
              </button>
              <button 
                type="submit" 
                :disabled="submitting"
                class="w-2/3 bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg red-glow disabled:opacity-60"
              >
                {{ submitting ? 'Đang đăng nhập...' : 'Đăng Nhập' }}
              </button>
            </div>
          </form>
        </div>

        <!-- STEP 3: TẠO TÀI KHOẢN (BƯỚC 1/2) -->
        <div v-if="step === 'register_step1'">
          <div class="text-center mb-6">
            <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-1">Đăng ký tài khoản</h1>
            <p class="text-xs text-on-surface-variant">Bước 1/2: Thông tin đăng nhập</p>
          </div>

          <form @submit.prevent="handleRegisterStep1" class="space-y-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Số điện thoại</label>
              <input 
                v-model="phone" 
                type="tel" 
                required 
                @input="normalizePhone('phone')"
                class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="Nhập số điện thoại" 
              />
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Địa chỉ Email</label>
              <input 
                v-model="email" 
                type="email" 
                required 
                class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="example@gmail.com" 
              />
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Mật khẩu</label>
              <div class="relative">
                <input 
                  v-model="password" 
                  :type="showPassword ? 'text' : 'password'" 
                  required 
                  minlength="8" 
                  maxlength="16"
                  class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                  placeholder="Nhập mật khẩu" 
                />
                <button 
                  type="button" 
                  class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
                  @click="showPassword = !showPassword"
                >
                  <span class="material-symbols-outlined text-lg">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
                </button>
              </div>
              
              <!-- Checkbox validations mật khẩu -->
              <div class="mt-2.5 grid grid-cols-1 gap-1 sm:grid-cols-2 bg-surface-container-low/50 p-2.5 rounded-lg border border-glass-stroke/40">
                <p v-for="check in passwordChecks" :key="check.label" class="flex items-center gap-1 text-[10px]"
                  :class="check.valid ? 'text-green-400' : 'text-on-surface-variant'">
                  <span class="material-symbols-outlined text-xs">{{ check.valid ? 'check_circle' : 'radio_button_unchecked' }}</span>
                  {{ check.label }}
                </p>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Xác nhận mật khẩu</label>
              <div class="relative">
                <input 
                  v-model="confirmPassword" 
                  :type="showConfirmPassword ? 'text' : 'password'" 
                  required 
                  minlength="8" 
                  maxlength="16"
                  class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                  placeholder="Xác nhận mật khẩu" 
                />
                <button 
                  type="button" 
                  class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <span class="material-symbols-outlined text-lg">{{ showConfirmPassword ? 'visibility_off' : 'visibility' }}</span>
                </button>
              </div>
              <p v-if="confirmPassword" class="mt-1 text-[11px]" :class="password === confirmPassword ? 'text-green-400' : 'text-red-400'">
                {{ password === confirmPassword ? '✓ Mật khẩu đã khớp.' : '✗ Mật khẩu chưa khớp.' }}
              </p>
            </div>

            <div class="flex gap-3 pt-2">
              <button 
                type="button" 
                @click="goBackToIdentifier"
                class="w-1/3 border border-glass-stroke text-on-surface py-3 rounded-xl font-bold hover:bg-white/5 active:scale-95 transition-all text-sm"
              >
                Quay lại
              </button>
              <button 
                type="submit" 
                class="w-2/3 bg-primary-container text-on-primary-container py-3 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg red-glow"
              >
                Tiếp tục
              </button>
            </div>
          </form>
        </div>

        <!-- STEP 4: TẠO TÀI KHOẢN (BƯỚC 2/2) -->
        <div v-if="step === 'register_step2'">
          <div class="text-center mb-6">
            <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-1">Đăng ký tài khoản</h1>
            <p class="text-xs text-on-surface-variant">Bước 2/2: Thông tin cá nhân</p>
          </div>

          <form @submit.prevent="handleRegisterStep2" class="space-y-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Họ và tên</label>
              <input 
                v-model="name" 
                type="text" 
                required 
                minlength="2" 
                maxlength="150"
                class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="Họ và tên của bạn" 
              />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Ngày sinh</label>
                <input 
                  v-model="dateOfBirth" 
                  type="date"
                  class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface" 
                />
              </div>

              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Giới tính</label>
                <select 
                  v-model="gender"
                  class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                >
                  <option value="">Chọn giới tính</option>
                  <option value="male">Nam</option>
                  <option value="female">Nữ</option>
                  <option value="other">Khác</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Địa chỉ</label>
              <input 
                v-model="address" 
                type="text" 
                class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="Nhập địa chỉ của bạn" 
              />
            </div>

            <!-- Checkbox không nhận email -->
            <div class="flex items-start gap-2 py-1">
              <input 
                v-model="noMarketingEmails" 
                type="checkbox" 
                id="noMarketingEmails"
                class="mt-1 rounded border-glass-stroke bg-surface-container text-primary-container focus:ring-0 cursor-pointer"
              />
              <label for="noMarketingEmails" class="text-xs text-on-surface-variant select-none cursor-pointer">
                Không đồng ý nhận email khuyến mãi
              </label>
            </div>

            <!-- Text đồng ý điều khoản -->
            <p class="text-[11px] text-on-surface-variant/80 leading-relaxed bg-white/5 p-3 rounded-lg border border-glass-stroke/30">
              ℹ️ Bằng việc đăng ký, bạn đã đồng ý với Điều khoản sử dụng & Chính sách bảo mật của CineAI.
            </p>

            <div class="flex gap-3 pt-2">
              <button 
                type="button" 
                @click="goBackToRegisterStep1"
                class="w-1/3 border border-glass-stroke text-on-surface py-3.5 rounded-xl font-bold hover:bg-white/5 active:scale-95 transition-all text-sm"
              >
                Quay lại
              </button>
              <button 
                type="submit" 
                :disabled="submitting"
                class="w-2/3 bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg red-glow disabled:opacity-60"
              >
                {{ submitting ? 'Đang đăng ký...' : 'Đăng Ký' }}
              </button>
            </div>
          </form>
        </div>

        <!-- STEP 5: XÁC THỰC OTP ĐĂNG KÝ -->
        <div v-if="step === 'otp'">
          <div class="text-center mb-6">
            <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-2">Xác thực kích hoạt</h1>
            <p class="text-xs text-on-surface-variant leading-relaxed">
              Chúng tôi đã gửi một mã OTP gồm 6 chữ số tới địa chỉ email của bạn. Vui lòng nhập mã để hoàn tất kích hoạt tài khoản.
            </p>
          </div>

          <form @submit.prevent="handleVerifyOtp" class="space-y-5">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2 text-center">
                Nhập mã xác thực
              </label>
              <input 
                v-model="otpCode" 
                type="text" 
                required 
                maxlength="6"
                class="w-full text-center tracking-[0.5em] font-mono font-bold text-xl bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="------" 
              />
            </div>

            <button 
              type="submit" 
              :disabled="submitting"
              class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg red-glow disabled:opacity-60"
            >
              {{ submitting ? 'Đang xác thực...' : 'Xác nhận' }}
            </button>
          </form>

          <div class="mt-6 text-center text-xs">
            <span class="text-on-surface-variant">Không nhận được mã? </span>
            <button 
              @click="handleResendOtp" 
              :disabled="countdown > 0"
              class="text-primary-container font-bold hover:underline disabled:text-on-surface-variant/40 disabled:no-underline"
            >
              Gửi lại mã {{ countdown > 0 ? `(${countdown}s)` : '' }}
            </button>
          </div>
        </div>

        <!-- STEP 6: QUÊN MẬT KHẨU (NHẬP EMAIL/SĐT) -->
        <div v-if="step === 'forgot_password'">
          <div class="text-center mb-8">
            <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-2">Quên Mật Khẩu?</h1>
            <p class="text-xs text-on-surface-variant">Nhập Email hoặc Số điện thoại để nhận mã OTP thiết lập mật khẩu mới.</p>
          </div>

          <form @submit.prevent="handleForgotPassword" class="space-y-5">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Số điện thoại hoặc Email</label>
              <input 
                v-model="identifier" 
                type="text" 
                required 
                maxlength="255"
                class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="Nhập email hoặc số điện thoại của bạn" 
              />
            </div>

            <div class="flex gap-3">
              <button 
                type="button" 
                @click="goBackToIdentifier"
                class="w-1/3 border border-glass-stroke text-on-surface py-3.5 rounded-xl font-bold hover:bg-white/5 active:scale-95 transition-all text-sm"
              >
                Quay lại
              </button>
              <button 
                type="submit" 
                :disabled="submitting"
                class="w-2/3 bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg red-glow disabled:opacity-60"
              >
                {{ submitting ? 'Đang gửi...' : 'Gửi mã khôi phục' }}
              </button>
            </div>
          </form>
        </div>

        <!-- STEP 7: XÁC THỰC OTP KHÔI PHỤC MẬT KHẨU (BẮT BUỘC NHẬP OTP TRƯỚC) -->
        <div v-if="step === 'forgot_otp'">
          <div class="text-center mb-6">
            <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-2">Xác thực khôi phục</h1>
            <p class="text-xs text-on-surface-variant leading-relaxed">
              Vui lòng nhập mã OTP gồm 6 chữ số đã được gửi tới email của bạn để tiếp tục đặt lại mật khẩu mới.
            </p>
          </div>

          <form @submit.prevent="handleVerifyForgotOtp" class="space-y-5">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2 text-center">
                Nhập mã xác thực
              </label>
              <input 
                v-model="otpCode" 
                type="text" 
                required 
                maxlength="6"
                class="w-full text-center tracking-[0.5em] font-mono font-bold text-xl bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="------" 
              />
            </div>

            <div class="flex gap-3">
              <button 
                type="button" 
                @click="step = 'forgot_password'"
                class="w-1/3 border border-glass-stroke text-on-surface py-3.5 rounded-xl font-bold hover:bg-white/5 active:scale-95 transition-all text-sm"
              >
                Quay lại
              </button>
              <button 
                type="submit" 
                class="w-2/3 bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg red-glow"
              >
                Tiếp tục
              </button>
            </div>
          </form>

          <div class="mt-6 text-center text-xs">
            <span class="text-on-surface-variant">Không nhận được mã? </span>
            <button 
              @click="handleResendForgotOtp" 
              :disabled="countdown > 0"
              class="text-primary-container font-bold hover:underline disabled:text-on-surface-variant/40 disabled:no-underline"
            >
              Gửi lại mã {{ countdown > 0 ? `(${countdown}s)` : '' }}
            </button>
          </div>
        </div>

        <!-- STEP 8: RESET MẬT KHẨU (ĐIỀN MẬT KHẨU MỚI) -->
        <div v-if="step === 'reset_password'">
          <div class="text-center mb-6">
            <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-2">Đặt lại mật khẩu</h1>
            <p class="text-xs text-on-surface-variant">Tạo mật khẩu mới cho tài khoản của bạn.</p>
          </div>

          <form @submit.prevent="handleResetPassword" class="space-y-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Mật khẩu mới</label>
              <div class="relative">
                <input 
                  v-model="password" 
                  :type="showPassword ? 'text' : 'password'" 
                  required 
                  minlength="8" 
                  maxlength="16"
                  class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                  placeholder="Nhập mật khẩu mới" 
                />
                <button 
                  type="button" 
                  class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
                  @click="showPassword = !showPassword"
                >
                  <span class="material-symbols-outlined text-lg">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
                </button>
              </div>
              <div class="mt-2 grid grid-cols-1 gap-1 sm:grid-cols-2 bg-surface-container-low/50 p-2 rounded-lg border border-glass-stroke/40">
                <p v-for="check in passwordChecks" :key="check.label" class="flex items-center gap-1 text-[10px]"
                  :class="check.valid ? 'text-green-400' : 'text-on-surface-variant'">
                  <span class="material-symbols-outlined text-xs">{{ check.valid ? 'check_circle' : 'radio_button_unchecked' }}</span>
                  {{ check.label }}
                </p>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">Xác nhận mật khẩu mới</label>
              <div class="relative">
                <input 
                  v-model="confirmPassword" 
                  :type="showConfirmPassword ? 'text' : 'password'" 
                  required 
                  minlength="8" 
                  maxlength="16"
                  class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                  placeholder="Xác nhận mật khẩu mới" 
                />
                <button 
                  type="button" 
                  class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <span class="material-symbols-outlined text-lg">{{ showConfirmPassword ? 'visibility_off' : 'visibility' }}</span>
                </button>
              </div>
              <p v-if="confirmPassword" class="mt-1 text-[11px]" :class="password === confirmPassword ? 'text-green-400' : 'text-red-400'">
                {{ password === confirmPassword ? '✓ Mật khẩu đã khớp.' : '✗ Mật khẩu chưa khớp.' }}
              </p>
            </div>

            <div class="flex gap-3 pt-2">
              <button 
                type="button" 
                @click="step = 'forgot_otp'"
                class="w-1/3 border border-glass-stroke text-on-surface py-3.5 rounded-xl font-bold hover:bg-white/5 active:scale-95 transition-all text-sm"
              >
                Quay lại
              </button>
              <button 
                type="submit" 
                :disabled="submitting"
                class="w-2/3 bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg red-glow disabled:opacity-60"
              >
                {{ submitting ? 'Đang đặt lại...' : 'Đặt lại mật khẩu' }}
              </button>
            </div>
          </form>
        </div>

      </div>

      <!-- ============================================== -->
      <!-- B. ĐĂNG NHẬP TRỰC TIẾP CHO ADMIN / NHÂN VIÊN   -->
      <!-- ============================================== -->
      <div v-else>
        <div class="text-center mb-8">
          <h1 class="font-headline-xl text-2xl font-bold text-on-surface mb-2">Đăng Nhập Quản Trị</h1>
          <p class="text-xs text-on-surface-variant">Dành cho Quản trị viên và Nhân viên rạp</p>
        </div>

        <form @submit.prevent="handleAdminLogin" class="space-y-5">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Email Quản trị</label>
            <input 
              v-model="adminEmail" 
              type="email" 
              required 
              maxlength="255"
              class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
              placeholder="admin@cineai.vn" 
            />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Mật khẩu</label>
            <div class="relative">
              <input 
                v-model="adminPassword" 
                :type="showPassword ? 'text' : 'password'" 
                required 
                maxlength="128"
                class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface"
                placeholder="Nhập mật khẩu quản trị" 
              />
              <button 
                type="button" 
                class="absolute inset-y-0 right-0 px-4 text-on-surface-variant hover:text-white"
                @click="showPassword = !showPassword"
              >
                <span class="material-symbols-outlined text-lg">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
              </button>
            </div>
          </div>

          <button 
            type="submit" 
            :disabled="submitting"
            class="w-full bg-neutral-800 border border-white/10 text-white py-3.5 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all text-sm shadow-lg disabled:opacity-60"
          >
            {{ submitting ? 'Đang xác thực quản trị...' : 'Đăng Nhập Quản Trị' }}
          </button>
        </form>
      </div>

      <!-- ============================================== -->
      <!-- GỢI Ý TÀI KHOẢN THỬ NGHIỆM                     -->
      <!-- ============================================== -->
      <div class="mt-8 border-t border-glass-stroke/40 pt-4 w-full">
        <div class="bg-surface-container-low/60 rounded-xl p-3 border border-glass-stroke/50">
          <span class="text-[10px] font-bold uppercase text-secondary tracking-wider block mb-1.5">💡 Tài khoản thử nghiệm</span>
          <div class="flex flex-col gap-2">
            <button 
              type="button" 
              @click="fillTestAccount(roleMode)"
              class="text-left text-xs bg-white/5 hover:bg-white/10 border border-glass-stroke/40 p-2 rounded-lg transition-all"
            >
              <div class="font-bold text-on-surface text-[11px] flex justify-between">
                <span>{{ testAccounts[roleMode].desc }}</span>
                <span class="text-primary-container font-medium text-[10px]">Tự động điền</span>
              </div>
              <p class="text-[10px] text-on-surface-variant mt-0.5">
                Email: <span class="text-on-surface select-all">{{ testAccounts[roleMode].email }}</span> <br>
                Mật khẩu: <span class="text-on-surface select-all">{{ testAccounts[roleMode].password }}</span>
              </p>
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

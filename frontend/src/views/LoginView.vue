<template>
  <div class="page-wrapper">
    <main class="relative min-h-screen flex items-center justify-center overflow-hidden px-4 md:px-0">
      <!-- Background -->
      <div class="absolute inset-0 z-0 overflow-hidden">
        <div
          ref="bgRef"
          class="w-full h-full bg-cover bg-center transition-transform duration-300"
          style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuCZuWlTLJ_Br_wwf9lzqgeztuoUSiqw2yUHc2nIlNVrjHKc3YSOdDKFt2NjBsd7RCrI-ur6VT_vKLumAOMf3PGtiKoDekcqciQshK-RqIVL21kak1IKR537wmeFWxc6pgebP0lq0gUYUs-emB6Lk8HwhYdoseCldk6XRHZeFeCsEHp9q-CdGQZCYEowJq4rn_WMeKgLU20-VVS-E70XegXj-od4jP1Tot2-ANn1Fg1ie_qJH5hgIFyRjYNfEfnRGlAoOOyEybvsPQQw')"
        ></div>
        <div class="absolute inset-0 bg-gradient-to-br from-background/95 via-background/80 to-transparent"></div>
        <div class="absolute inset-0 backdrop-blur-[2px]"></div>
      </div>

      <!-- Login Card -->
      <div class="relative z-10 w-full max-w-[480px]">
        <div class="glass-panel p-8 md:p-12 rounded-3xl shadow-2xl flex flex-col gap-8">
          <!-- Logo & Title -->
          <div class="flex flex-col items-center text-center gap-2">
            <div class="w-16 h-16 bg-red-600 rounded-2xl flex items-center justify-center mb-4 red-glow">
              <span class="material-symbols-outlined text-4xl text-white" style="font-variation-settings:'FILL' 1">movie</span>
            </div>
            <h1 class="text-3xl font-bold text-white tracking-tight">Chào mừng quay trở lại</h1>
            <p class="text-gray-400 max-w-[300px]">Đăng nhập để tiếp tục trải nghiệm điện ảnh thông minh</p>
          </div>

          <!-- Form -->
          <form class="flex flex-col gap-6" @submit.prevent="handleLogin">
            <div class="space-y-4">
              <!-- Email -->
              <div class="relative group">
                <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-red-500 transition-colors">mail</span>
                <input
                  v-model="form.email"
                  type="email"
                  placeholder="Email"
                  class="input-field pl-12"
                />
              </div>
              <!-- Password -->
              <div class="relative group">
                <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-red-500 transition-colors">lock</span>
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Mật khẩu"
                  class="input-field pl-12 pr-12"
                />
                <button
                  type="button"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                  @click="showPassword = !showPassword"
                >
                  <span class="material-symbols-outlined">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
                </button>
              </div>
            </div>

            <!-- Remember & Forgot -->
            <div class="flex items-center justify-between px-1">
              <label class="flex items-center gap-2 cursor-pointer group">
                <input v-model="form.remember" type="checkbox" class="w-4 h-4 accent-red-600" />
                <span class="text-sm text-gray-400 group-hover:text-white transition-colors">Ghi nhớ tôi</span>
              </label>
              <a href="#" class="text-sm text-red-500 hover:underline">Quên mật khẩu?</a>
            </div>

            <!-- Error message -->
            <p v-if="errorMsg" class="text-red-400 text-sm text-center">{{ errorMsg }}</p>

            <!-- Submit -->
            <button
              type="submit"
              :disabled="loading"
              class="w-full py-4 bg-red-600 text-white font-semibold rounded-xl red-glow transition-all hover:brightness-110 active:scale-95 flex items-center justify-center gap-2 disabled:opacity-60"
            >
              <span v-if="loading">Đang đăng nhập...</span>
              <span v-else class="flex items-center gap-2">
                Đăng nhập
                <span class="material-symbols-outlined">arrow_forward</span>
              </span>
            </button>
          </form>

          <!-- Divider -->
          <div class="relative flex items-center">
            <div class="flex-grow border-t border-white/10"></div>
            <span class="mx-4 text-xs text-gray-500">Hoặc tiếp tục với</span>
            <div class="flex-grow border-t border-white/10"></div>
          </div>

          <!-- Social Login -->
          <div class="grid grid-cols-2 gap-4">
            <button class="social-btn" @click="loginWithGoogle">
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path d="M12 5.04c1.9 0 3.53.65 4.87 1.92l3.6-3.6C18.18 1.16 15.37 0 12 0 7.31 0 3.25 2.69 1.18 6.64l4.23 3.28C6.4 7.37 8.98 5.04 12 5.04z" fill="#EA4335"/>
                <path d="M23.49 12.27c0-.83-.07-1.63-.2-2.39H12v4.51h6.47c-.28 1.48-1.11 2.73-2.36 3.58l3.71 2.88c2.16-1.99 3.42-4.93 3.42-8.58z" fill="#4285F4"/>
                <path d="M5.41 14.56l-4.23 3.28C3.25 21.31 7.31 24 12 24c3.16 0 5.81-.98 7.82-2.67l-3.71-2.88c-1.05.71-2.4 1.13-4.11 1.13-3.02 0-5.6-2.33-6.59-5.46V14.56z" fill="#FBBC05"/>
                <path d="M1.18 6.64l4.23 3.28c.99-3.13 3.57-5.46 6.59-5.46 1.71 0 3.06.42 4.11 1.13l3.71-2.88C17.81.98 15.16 0 12 0 7.31 0 3.25 2.69 1.18 6.64z" fill="#34A853"/>
              </svg>
              <span class="text-white font-medium">Google</span>
            </button>
            <button class="social-btn" @click="loginWithFacebook">
              <svg class="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              <span class="text-white font-medium">Facebook</span>
            </button>
          </div>

          <!-- Register Link -->
          <div class="text-center">
            <p class="text-gray-400">
              Chưa có tài khoản?
              <router-link to="/register" class="text-red-500 font-bold hover:underline ml-1">Đăng ký ngay</router-link>
            </p>
          </div>
        </div>
      </div>

      <!-- Decorative -->
      <div class="absolute bottom-10 left-10 hidden lg:block opacity-20">
        <span class="material-symbols-outlined text-[120px] text-red-600 blur-sm">movie_filter</span>
      </div>
      <div class="absolute top-10 right-10 hidden lg:block opacity-20">
        <span class="material-symbols-outlined text-[120px] text-purple-500 blur-sm">smart_toy</span>
      </div>
    </main>

    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppFooter from '@/components/AppFooter.vue'

const router = useRouter()
const bgRef = ref(null)

const form = ref({
  email: '',
  password: '',
  remember: false
})
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''
  if (!form.value.email || !form.value.password) {
    errorMsg.value = 'Vui lòng nhập email và mật khẩu.'
    return
  }
  loading.value = true
  try {
    // TODO: gọi API backend
    // const res = await axios.post('/api/auth/login', form.value)
    // router.push('/discover')
    console.log('Login with:', form.value)
    await new Promise(r => setTimeout(r, 1000)) // giả lập delay
    router.push('/')
  } catch (e) {
    errorMsg.value = 'Đăng nhập thất bại. Vui lòng thử lại.'
  } finally {
    loading.value = false
  }
}

function loginWithGoogle() {
  console.log('Login with Google')
  // TODO: implement OAuth
}

function loginWithFacebook() {
  console.log('Login with Facebook')
  // TODO: implement OAuth
}

// Mouse parallax effect
function handleMouseMove(e) {
  if (!bgRef.value) return
  const moveX = (e.clientX - window.innerWidth / 2) / 50
  const moveY = (e.clientY - window.innerHeight / 2) / 50
  bgRef.value.style.transform = `scale(1.1) translate(${moveX}px, ${moveY}px)`
}

onMounted(() => window.addEventListener('mousemove', handleMouseMove))
onUnmounted(() => window.removeEventListener('mousemove', handleMouseMove))
</script>

<style scoped>
.page-wrapper {
  background: #121414;
  min-height: 100vh;
}

.glass-panel {
  background: rgba(31, 31, 31, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.red-glow {
  box-shadow: 0 0 20px -5px rgba(229, 9, 20, 0.4);
}
.red-glow:hover {
  box-shadow: 0 0 30px -2px rgba(229, 9, 20, 0.6);
}

.input-field {
  width: 100%;
  padding: 1rem;
  background: rgba(51, 53, 53, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  outline: none;
  color: white;
  font-size: 16px;
  transition: all 0.2s;
}
.input-field::placeholder {
  color: rgba(226, 226, 226, 0.4);
}
.input-field:focus {
  border-color: transparent;
  box-shadow: 0 0 0 2px #e50914;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(31, 31, 31, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}
.social-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}
.social-btn:active {
  transform: scale(0.95);
}
</style>
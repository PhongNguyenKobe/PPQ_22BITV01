<script setup lang="ts">
import { ref } from 'vue'
import { adminBackendService } from '~/services/api'

const qrData = ref('')
const result = ref<any>(null)
const loading = ref(false)
const error = ref('')

const stateStyle: Record<string, string> = {
  VALID: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
  CHECKED_IN: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
  ALREADY_USED: 'border-amber-500/40 bg-amber-500/10 text-amber-300',
  EXPIRED: 'border-slate-500/40 bg-slate-500/10 text-slate-300',
  CANCELLED: 'border-red-500/40 bg-red-500/10 text-red-300',
  CANCEL_REQUESTED: 'border-orange-500/40 bg-orange-500/10 text-orange-300',
  NOT_CONFIRMED: 'border-red-500/40 bg-red-500/10 text-red-300',
  INVALID: 'border-red-500/40 bg-red-500/10 text-red-300',
  NOT_FOUND: 'border-red-500/40 bg-red-500/10 text-red-300',
}

async function scan(consume = false) {
  if (!qrData.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    result.value = await adminBackendService.scanTicket(qrData.value.trim(), consume)
  } catch (e: any) {
    error.value = e?.message || 'Không thể kiểm tra mã vé.'
  } finally {
    loading.value = false
  }
}

function reset() {
  qrData.value = ''
  result.value = null
  error.value = ''
  nextTick(() => document.querySelector<HTMLInputElement>('#ticket-code-input')?.focus())
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-black text-white">Soát vé QR</h2>
      <p class="mt-1 text-sm text-gray-400">Dùng máy quét QR hoặc nhập mã vé ngắn để kiểm tra trước khi cho khách vào rạp.</p>
    </div>

    <div class="rounded-2xl border border-white/10 bg-white/5 p-6">
      <label for="ticket-code-input" class="mb-2 block text-xs font-bold uppercase tracking-wider text-gray-400">Mã QR / mã vé</label>
      <div class="flex flex-col gap-3 sm:flex-row">
        <input
          id="ticket-code-input"
          v-model="qrData"
          autofocus
          autocomplete="off"
          class="min-w-0 flex-1 rounded-xl border border-white/10 bg-black/30 px-4 py-3 font-mono text-white outline-none focus:border-red-500"
          placeholder="H260805001"
          @keyup.enter="scan(false)"
        >
        <button class="rounded-xl bg-red-600 px-6 py-3 font-bold text-white disabled:opacity-50" :disabled="loading || !qrData.trim()" @click="scan(false)">
          {{ loading ? 'Đang kiểm tra...' : 'Kiểm tra vé' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-300">{{ error }}</div>

    <div v-if="result" class="rounded-2xl border p-6" :class="stateStyle[result.state] || stateStyle.INVALID">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div class="text-xs font-black uppercase tracking-widest">{{ result.state }}</div>
          <h3 class="mt-1 text-xl font-black">{{ result.message }}</h3>
        </div>
        <button class="text-sm font-bold underline" @click="reset">Quét vé khác</button>
      </div>

      <div v-if="result.ticket_code" class="mt-5 grid gap-4 rounded-xl bg-black/20 p-4 sm:grid-cols-2">
        <div><span class="block text-xs opacity-70">Mã vé</span><strong class="font-mono">{{ result.ticket_code }}</strong></div>
        <div><span class="block text-xs opacity-70">Phim</span><strong>{{ result.movie_title }}</strong></div>
        <div><span class="block text-xs opacity-70">Rạp / phòng</span><strong>{{ result.branch_name }} · {{ result.auditorium_name }}</strong></div>
        <div><span class="block text-xs opacity-70">Ghế</span><strong>{{ result.seats?.join(', ') }}</strong></div>
        <div><span class="block text-xs opacity-70">Suất chiếu</span><strong>{{ new Date(result.starts_at).toLocaleString('vi-VN') }}</strong></div>
        <div v-if="result.checked_in_at"><span class="block text-xs opacity-70">Đã sử dụng lúc</span><strong>{{ new Date(result.checked_in_at).toLocaleString('vi-VN') }}</strong></div>
      </div>

      <button
        v-if="result.state === 'VALID'"
        class="mt-5 w-full rounded-xl bg-emerald-600 px-6 py-3 font-black text-white hover:bg-emerald-500"
        :disabled="loading"
        @click="scan(true)"
      >
        Xác nhận cho khách vào rạp
      </button>
    </div>
  </div>
</template>

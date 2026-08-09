<script setup lang="ts">
import { nextTick, onUnmounted, ref } from 'vue'
import { adminBackendService } from '~/services/api'

const qrData = ref('')
const result = ref<any>(null)
const loading = ref(false)
const error = ref('')
const cameraOpen = ref(false)
const videoEl = ref<HTMLVideoElement | null>(null)
let mediaStream: MediaStream | null = null
let cameraFrame = 0

const stateMeta: Record<string, { label: string; icon: string; style: string }> = {
  VALID: { label: 'Vé hợp lệ', icon: 'verified', style: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' },
  CHECKED_IN: { label: 'Đã soát vé', icon: 'how_to_reg', style: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' },
  ALREADY_USED: { label: 'Đã sử dụng', icon: 'event_busy', style: 'border-amber-500/40 bg-amber-500/10 text-amber-300' },
  TOO_EARLY: { label: 'Chưa đến giờ', icon: 'schedule', style: 'border-sky-500/40 bg-sky-500/10 text-sky-300' },
  EXPIRED: { label: 'Đã hết hạn', icon: 'history', style: 'border-slate-500/40 bg-slate-500/10 text-slate-300' },
  CANCELLED: { label: 'Vé đã hủy', icon: 'cancel', style: 'border-red-500/40 bg-red-500/10 text-red-300' },
  CANCEL_REQUESTED: { label: 'Đang yêu cầu hủy', icon: 'pending_actions', style: 'border-orange-500/40 bg-orange-500/10 text-orange-300' },
  NOT_CONFIRMED: { label: 'Chưa thanh toán', icon: 'error', style: 'border-red-500/40 bg-red-500/10 text-red-300' },
  INVALID: { label: 'QR không hợp lệ', icon: 'gpp_bad', style: 'border-red-500/40 bg-red-500/10 text-red-300' },
  NOT_FOUND: { label: 'Không tìm thấy vé', icon: 'search_off', style: 'border-red-500/40 bg-red-500/10 text-red-300' },
}
const fallbackState = stateMeta.INVALID
function meta(state?: string) { return stateMeta[state || ''] || fallbackState }
function dateTime(value?: string | null) { return value ? new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value)) : '—' }

async function scan(consume = false) {
  const value = qrData.value.trim()
  if (!value || loading.value) return
  loading.value = true
  error.value = ''
  try {
    result.value = await adminBackendService.scanTicket(value, consume)
  } catch (cause: any) {
    error.value = cause?.response?.data?.detail || cause?.message || 'Không thể kiểm tra mã vé.'
  } finally { loading.value = false }
}

function stopCamera() {
  cancelAnimationFrame(cameraFrame)
  mediaStream?.getTracks().forEach(track => track.stop())
  mediaStream = null
  cameraOpen.value = false
}

async function startCamera() {
  error.value = ''
  const BarcodeDetectorApi = (window as any).BarcodeDetector
  if (!navigator.mediaDevices?.getUserMedia) {
    error.value = 'Trình duyệt không cho phép mở camera. Bạn vẫn có thể dùng máy quét hoặc nhập mã vé.'
    return
  }
  if (!BarcodeDetectorApi) {
    error.value = 'Trình duyệt này chưa hỗ trợ đọc QR trực tiếp. Hãy dùng Chrome/Edge mới hoặc máy quét QR.'
    return
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false })
    cameraOpen.value = true
    await nextTick()
    if (!videoEl.value) return stopCamera()
    videoEl.value.srcObject = mediaStream
    await videoEl.value.play()
    const detector = new BarcodeDetectorApi({ formats: ['qr_code'] })
    const detect = async () => {
      if (!cameraOpen.value || !videoEl.value) return
      try {
        const codes = await detector.detect(videoEl.value)
        const rawValue = codes?.[0]?.rawValue?.trim()
        if (rawValue) {
          qrData.value = rawValue
          stopCamera()
          await scan(false)
          return
        }
      } catch { /* Camera frame may not be ready yet. */ }
      cameraFrame = requestAnimationFrame(detect)
    }
    cameraFrame = requestAnimationFrame(detect)
  } catch {
    stopCamera()
    error.value = 'Không thể mở camera. Hãy cấp quyền camera cho trình duyệt hoặc nhập mã vé thủ công.'
  }
}

function reset() {
  stopCamera()
  qrData.value = ''
  result.value = null
  error.value = ''
  nextTick(() => document.querySelector<HTMLInputElement>('#ticket-code-input')?.focus())
}
onUnmounted(stopCamera)
</script>

<template>
  <div class="space-y-6">
    <header>
      <div class="flex items-center gap-2"><span class="material-symbols-outlined text-red-500">qr_code_scanner</span><h2 class="text-2xl font-black text-white">Soát vé QR</h2></div>
      <p class="mt-1 text-sm text-gray-400">Quét một mã để kiểm tra và check-in toàn bộ ghế thuộc cùng đơn đặt vé.</p>
    </header>

    <section class="rounded-2xl border border-white/10 bg-white/5 p-5">
      <label for="ticket-code-input" class="mb-2 block text-xs font-bold uppercase tracking-wider text-gray-400">QR hoặc mã đơn vé ngắn</label>
      <div class="flex flex-col gap-3 lg:flex-row">
        <input id="ticket-code-input" v-model="qrData" autofocus autocomplete="off" class="min-w-0 flex-1 rounded-xl border border-white/10 bg-black/30 px-4 py-3 font-mono uppercase text-white outline-none focus:border-red-500" placeholder="Ví dụ: H260805001" @keyup.enter="scan(false)">
        <button class="secondary-btn" :disabled="loading" @click="cameraOpen ? stopCamera() : startCamera()"><span class="material-symbols-outlined text-lg">{{ cameraOpen ? 'videocam_off' : 'photo_camera' }}</span>{{ cameraOpen ? 'Đóng camera' : 'Mở camera' }}</button>
        <button class="rounded-xl bg-red-600 px-6 py-3 font-bold text-white disabled:opacity-40" :disabled="loading || !qrData.trim()" @click="scan(false)">{{ loading ? 'Đang kiểm tra...' : 'Kiểm tra đơn vé' }}</button>
      </div>
      <div v-if="cameraOpen" class="relative mx-auto mt-4 max-w-xl overflow-hidden rounded-2xl border border-red-500/30 bg-black">
        <video ref="videoEl" muted playsinline class="aspect-video w-full object-cover" />
        <div class="pointer-events-none absolute inset-[18%] rounded-xl border-2 border-white/80 shadow-[0_0_0_999px_rgba(0,0,0,.45)]"></div>
        <p class="absolute bottom-3 inset-x-0 text-center text-xs font-bold text-white">Đưa mã QR vào trong khung</p>
      </div>
    </section>

    <div v-if="error" class="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-300">{{ error }}</div>

    <section v-if="result" class="rounded-2xl border p-6" :class="meta(result.state).style">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div class="flex gap-3"><span class="material-symbols-outlined rounded-xl bg-black/20 p-2 text-3xl">{{ meta(result.state).icon }}</span><div><div class="text-xs font-black uppercase tracking-widest">{{ meta(result.state).label }}</div><h3 class="mt-1 text-xl font-black">{{ result.message }}</h3></div></div>
        <button class="text-sm font-bold underline" @click="reset">Quét đơn khác</button>
      </div>

      <div v-if="result.ticket_code" class="mt-5 grid gap-3 rounded-xl bg-black/20 p-4 sm:grid-cols-2 lg:grid-cols-4">
        <div class="info"><span>Khách hàng</span><strong>{{ result.customer_name }}</strong></div>
        <div class="info"><span>Mã đơn vé</span><strong class="font-mono">{{ result.booking_ticket_code }}</strong></div>
        <div class="info"><span>Phim</span><strong>{{ result.movie_title }}</strong></div>
        <div class="info"><span>Rạp / phòng</span><strong>{{ result.branch_name }} · {{ result.auditorium_name }}</strong></div>
        <div class="info"><span>Suất chiếu</span><strong>{{ dateTime(result.starts_at) }}</strong></div>
        <div class="info"><span>Mở check-in</span><strong>{{ dateTime(result.checkin_opens_at) }}</strong></div>
        <div class="info"><span>Số lượng</span><strong>{{ result.ticket_count }} ghế</strong></div>
        <div class="info"><span>Tình trạng</span><strong>{{ result.used_count }}/{{ result.ticket_count }} ghế đã vào</strong></div>
      </div>

      <div v-if="result.ticket_details?.length" class="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        <div v-for="ticket in result.ticket_details" :key="ticket.ticket_code" class="flex items-center justify-between rounded-xl border border-current/15 bg-black/15 p-3">
          <div><span class="text-[10px] uppercase opacity-60">Ghế</span><p class="text-lg font-black">{{ ticket.seat }}</p><p class="font-mono text-[10px] opacity-60">{{ ticket.ticket_code }}</p></div>
          <span class="material-symbols-outlined">{{ ticket.status === 'USED' ? 'check_circle' : 'event_seat' }}</span>
        </div>
      </div>

      <div v-if="result.state === 'TOO_EARLY'" class="mt-4 rounded-xl border border-current/20 bg-black/15 p-3 text-sm">Có thể soát vé từ <b>{{ dateTime(result.checkin_opens_at) }}</b>, tức 60 phút trước giờ chiếu.</div>
      <div v-if="result.checked_in_at" class="mt-4 text-sm">Đã check-in lúc <b>{{ dateTime(result.checked_in_at) }}</b>.</div>
      <button v-if="result.state === 'VALID'" class="mt-5 w-full rounded-xl bg-emerald-600 px-6 py-3 font-black text-white hover:bg-emerald-500 disabled:opacity-40" :disabled="loading" @click="scan(true)">{{ loading ? 'Đang xác nhận...' : `Xác nhận ${result.remaining_count || result.ticket_count} ghế vào rạp` }}</button>
    </section>
  </div>
</template>

<style scoped>
.secondary-btn{display:flex;align-items:center;justify-content:center;gap:.4rem;border:1px solid rgba(255,255,255,.12);border-radius:.75rem;padding:.7rem 1rem;font-weight:700;color:#d1d5db}.secondary-btn:hover{background:rgba(255,255,255,.07);color:#fff}.secondary-btn:disabled{opacity:.4}.info{display:flex;min-width:0;flex-direction:column;gap:.2rem}.info span{font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;opacity:.65}.info strong{overflow-wrap:anywhere;color:currentColor}
</style>

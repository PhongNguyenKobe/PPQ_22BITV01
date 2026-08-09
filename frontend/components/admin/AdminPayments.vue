<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { adminBackendService, type AdminPayment } from '~/services/api'
import { useUserStore } from '~/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isBranchAdmin = computed(() => userStore.currentUser?.role === 'branch-admin')
const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const rows = ref<AdminPayment[]>([])
const total = ref(0)
const summary = ref<Record<string, number>>({})
const loading = ref(false)
const error = ref('')
const notice = ref('')
const search = ref('')
const status = ref('')
const method = ref('')
const verification = ref('')
const startDate = ref('')
const endDate = ref('')
const attentionOnly = ref(false)
const currentPage = ref(1)
const selected = ref<AdminPayment | null>(null)
const history = ref<any[]>([])
const busyId = ref('')
const refundTarget = ref<AdminPayment | null>(null)
const refundReason = ref('')
const lastUpdated = ref<Date | null>(null)
const pageSize = 15

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const visiblePages = computed(() => {
  const pages: number[] = []
  for (let page = Math.max(1, currentPage.value - 2); page <= Math.min(totalPages.value, currentPage.value + 2); page++) pages.push(page)
  return pages
})
const kpis = computed(() => [
  { label: 'Tổng giao dịch', value: total.value, icon: 'receipt_long', tone: 'text-white' },
  { label: 'Thành công', value: summary.value.SUCCESS || 0, icon: 'check_circle', tone: 'text-emerald-400' },
  { label: 'Chờ thanh toán', value: summary.value.PENDING || 0, icon: 'hourglass_top', tone: 'text-amber-400' },
  { label: 'Cần xử lý', value: summary.value.ATTENTION || 0, icon: 'warning', tone: 'text-rose-400' },
  { label: 'Tiền thành công', value: money(summary.value.SUCCESS_VALUE || 0), icon: 'payments', tone: 'text-sky-400' },
])
const statusMeta: Record<string, { label: string; cls: string }> = {
  PENDING: { label: 'Chờ thanh toán', cls: 'border-amber-500/25 bg-amber-500/10 text-amber-300' },
  SUCCESS: { label: 'Thành công', cls: 'border-emerald-500/25 bg-emerald-500/10 text-emerald-300' },
  FAILED: { label: 'Thất bại', cls: 'border-rose-500/25 bg-rose-500/10 text-rose-300' },
  EXPIRED: { label: 'Hết hạn', cls: 'border-zinc-500/25 bg-zinc-500/10 text-zinc-400' },
  CANCELLED: { label: 'Đã hủy', cls: 'border-zinc-500/25 bg-zinc-500/10 text-zinc-300' },
  REFUND_PENDING: { label: 'Chờ hoàn tiền', cls: 'border-violet-500/25 bg-violet-500/10 text-violet-300' },
  REFUNDED: { label: 'Đã hoàn tiền', cls: 'border-sky-500/25 bg-sky-500/10 text-sky-300' },
  REFUND_FAILED: { label: 'Hoàn tiền thất bại', cls: 'border-rose-500/25 bg-rose-500/10 text-rose-300' },
  RECONCILIATION_REQUIRED: { label: 'Cần đối soát', cls: 'border-orange-500/25 bg-orange-500/10 text-orange-300' },
}

function money(value: number) { return `${Number(value || 0).toLocaleString('vi-VN')}đ` }
function dateTime(value?: string | null) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
}
function state(item: AdminPayment) { return statusMeta[item.status] || { label: item.status, cls: 'border-white/10 bg-white/5 text-gray-300' } }
function shortId(value?: string | null) { return value ? `${value.slice(0, 8)}…${value.slice(-6)}` : '—' }
function seats(item: AdminPayment) { return item.seats.map(seat => `${seat.row}${seat.number}`).join(', ') || '—' }
function isVnpay(item: AdminPayment) { return item.payment_method === 'VNPAY' }
function isLegacy(item: AdminPayment) { return !item.provider_ref && !item.provider_transaction_no }
function verificationState(item: AdminPayment) {
  if (!isVnpay(item)) return { label: 'Không áp dụng', icon: 'remove', cls: 'text-gray-500' }
  if (item.signature_valid === true) return { label: 'Hợp lệ', icon: 'verified_user', cls: 'text-emerald-400' }
  if (item.signature_valid === false) return { label: 'Sai chữ ký', icon: 'gpp_bad', cls: 'text-rose-400' }
  if (['PENDING'].includes(item.status)) return { label: 'Chưa phản hồi', icon: 'schedule', cls: 'text-amber-400' }
  return { label: 'Không có callback', icon: 'info', cls: 'text-gray-500' }
}
function canRetryRefund(item: AdminPayment) {
  return isBranchAdmin.value && item.payment_method === 'VNPAY' && item.status === 'REFUND_FAILED'
    && item.signature_valid === true && item.booking_status === 'CANCELLED'
}

async function load() {
  if (startDate.value && endDate.value && startDate.value > endDate.value) {
    error.value = 'Ngày bắt đầu không được lớn hơn ngày kết thúc.'
    return
  }
  loading.value = true; error.value = ''
  try {
    const result = await adminBackendService.getPayments({
      status: status.value || undefined,
      payment_method: method.value || undefined,
      verification: verification.value || undefined,
      attention_only: attentionOnly.value || undefined,
      search: search.value.trim() || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      branch_id: !isBranchAdmin.value && selectedBranch.value !== 'ALL' ? selectedBranch.value : undefined,
      payment_id: String(route.query.payment_id || '') || undefined,
      booking_id: String(route.query.booking_id || '') || undefined,
      limit: pageSize,
      skip: (currentPage.value - 1) * pageSize,
    })
    rows.value = result.payments; total.value = result.total; summary.value = result.summary || {}; lastUpdated.value = new Date()
    if ((route.query.payment_id || route.query.booking_id) && rows.value.length === 1) await showDetails(rows.value[0])
  } catch (cause: any) {
    error.value = cause?.response?.data?.detail || cause?.message || 'Không thể tải danh sách giao dịch.'
  } finally { loading.value = false }
}
function applyFilters() { currentPage.value = 1; void load() }
function resetFilters() {
  search.value = ''; status.value = ''; method.value = ''; verification.value = ''; startDate.value = ''; endDate.value = ''; attentionOnly.value = false; currentPage.value = 1
  if (route.query.payment_id || route.query.booking_id) void router.replace({ query: { tab: 'payments' } }).then(() => load())
  else void load()
}
function quickAttention() { attentionOnly.value = !attentionOnly.value; currentPage.value = 1; void load() }
async function showDetails(item: AdminPayment) {
  selected.value = item; history.value = []
  try { history.value = await adminBackendService.getPaymentHistory(item.id) }
  catch { error.value = 'Không thể tải lịch sử giao dịch.' }
}
async function reconcile(item: AdminPayment) {
  busyId.value = item.id; error.value = ''; notice.value = ''
  try {
    const result = await adminBackendService.reconcilePayment(item.id)
    notice.value = result.matched
      ? `Đối soát thành công: số tiền ${money(result.provider_amount)} và trạng thái VNPAY đều khớp.`
      : result.response_signature_valid === false
        ? 'Không thể tin cậy kết quả đối soát vì chữ ký phản hồi VNPAY không hợp lệ. Dữ liệu thanh toán không bị tự động sửa.'
        : `Phát hiện sai lệch ${result.amount_matches ? 'trạng thái' : 'số tiền'}; giao dịch đã được chuyển sang “Cần đối soát”.`
    await load(); await showDetails(rows.value.find(row => row.id === item.id) || item)
  } catch (cause: any) { error.value = cause?.response?.data?.detail || cause?.message || 'Không thể đối soát VNPAY.' }
  finally { busyId.value = '' }
}
function openRefund(item: AdminPayment) { refundTarget.value = item; refundReason.value = item.refund_error || '' }
async function submitRefund() {
  if (!refundTarget.value || refundReason.value.trim().length < 5) return
  busyId.value = refundTarget.value.id; error.value = ''
  try {
    await adminBackendService.refundPayment(refundTarget.value.id, refundReason.value.trim())
    refundTarget.value = null; refundReason.value = ''; notice.value = 'Đã gửi lại yêu cầu hoàn tiền VNPAY.'; await load()
  } catch (cause: any) { error.value = cause?.response?.data?.detail || cause?.message || 'Không thể gửi lại yêu cầu hoàn tiền.' }
  finally { busyId.value = '' }
}
function goToBooking(item: AdminPayment) { void router.push({ query: { tab: 'bookings', booking_id: item.booking_id } }) }
async function copy(value?: string | null) { if (value) await navigator.clipboard.writeText(value) }

let refreshTimer: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  void load()
  refreshTimer = setInterval(() => {
    if (!document.hidden && !loading.value && !selected.value && !refundTarget.value && !busyId.value) void load()
  }, 45000)
})
onUnmounted(() => { if (refreshTimer) clearInterval(refreshTimer) })
watch(currentPage, () => void load())
watch(selectedBranch, () => { currentPage.value = 1; if (!isBranchAdmin.value) void load() })
</script>

<template>
  <div class="space-y-6">
    <header class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between"><div><div class="flex items-center gap-2"><span class="material-symbols-outlined text-red-500">payments</span><h2 class="text-2xl font-black text-white">{{ isBranchAdmin ? 'Giao dịch & hoàn tiền' : 'Giám sát thanh toán' }}</h2></div><p class="mt-1 text-sm text-gray-400">{{ isBranchAdmin ? 'Đối soát và theo dõi hoàn tiền tại chi nhánh được phân công.' : 'Tra soát giao dịch toàn hệ thống ở chế độ chỉ đọc.' }}</p></div><div class="flex items-center gap-3"><span v-if="lastUpdated" class="text-xs text-gray-500">Cập nhật {{ dateTime(lastUpdated.toISOString()) }}</span><span v-if="!isBranchAdmin" class="rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1 text-xs font-bold text-sky-300">Chế độ giám sát</span></div></header>

    <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5"><article v-for="item in kpis" :key="item.label" class="panel flex items-center gap-3 p-4"><span class="material-symbols-outlined rounded-xl bg-white/5 p-2 text-gray-400">{{ item.icon }}</span><div><p class="text-[11px] font-bold uppercase tracking-wider text-gray-500">{{ item.label }}</p><p class="mt-1 text-xl font-black" :class="item.tone">{{ item.value }}</p></div></article></section>

    <section class="panel space-y-3 p-4"><div class="grid gap-3 lg:grid-cols-[2fr_1fr_1fr_1fr_auto]"><label class="relative"><span class="material-symbols-outlined absolute left-3 top-3 text-lg text-gray-500">search</span><input v-model="search" class="field pl-10" placeholder="Mã giao dịch, mã đơn, khách hàng..." @keyup.enter="applyFilters"></label><select v-model="status" class="field"><option value="">Tất cả trạng thái</option><option v-for="(meta, key) in statusMeta" :key="key" :value="key">{{ meta.label }}</option></select><select v-model="method" class="field"><option value="">Mọi phương thức</option><option value="VNPAY">VNPAY</option><option value="PAYPAL">PayPal</option></select><select v-model="verification" class="field"><option value="">Mọi xác minh</option><option value="VALID">Chữ ký hợp lệ</option><option value="INVALID">Sai chữ ký</option><option value="UNVERIFIED">Chưa xác minh</option></select><div class="flex gap-2"><button class="rounded-xl bg-red-600 px-4 py-2 font-bold text-white hover:bg-red-500 disabled:opacity-50" :disabled="loading" @click="applyFilters">Lọc</button><button class="mini-btn" title="Xóa bộ lọc" @click="resetFilters"><span class="material-symbols-outlined text-lg">filter_alt_off</span></button></div></div><div class="flex flex-wrap items-center gap-3"><input v-model="startDate" type="date" class="field !w-auto" title="Ngày giao dịch từ"><span class="text-xs text-gray-500">đến</span><input v-model="endDate" type="date" class="field !w-auto" title="Ngày giao dịch đến"><button class="rounded-full border px-3 py-1.5 text-xs font-bold" :class="attentionOnly ? 'border-rose-500/40 bg-rose-500/15 text-rose-300' : 'border-white/10 text-gray-400'" @click="quickAttention">Chỉ giao dịch cần xử lý</button><button class="ml-auto mini-btn" :disabled="loading" @click="load"><span class="material-symbols-outlined mr-1 align-middle text-sm">sync</span>Làm mới</button></div></section>

    <div v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm font-medium text-rose-300">{{ error }}</div><div v-if="notice" class="rounded-xl border border-emerald-500/25 bg-emerald-500/10 p-4 text-sm font-medium text-emerald-300">{{ notice }}</div>

    <section class="panel overflow-hidden"><div class="overflow-x-auto"><table class="w-full min-w-[1180px] text-left text-sm"><thead class="border-b border-white/10 bg-white/[.04] text-xs uppercase tracking-wider text-gray-400"><tr><th class="p-4">Giao dịch</th><th class="p-4">Đơn & khách hàng</th><th class="p-4">Phương thức</th><th class="p-4">Số tiền</th><th class="p-4">Trạng thái</th><th class="p-4">Xác minh</th><th class="p-4 text-right">Thao tác</th></tr></thead><tbody><tr v-for="item in rows" :key="item.id" class="border-b border-white/5 hover:bg-white/[.03]"><td class="p-4"><button class="font-mono text-xs font-bold text-white hover:text-red-300" :title="item.id" @click="copy(item.id)">{{ shortId(item.id) }}</button><p class="mt-1 font-mono text-xs text-sky-400" :title="item.provider_transaction_no || item.provider_ref || ''">VNPAY: {{ item.provider_transaction_no || shortId(item.provider_ref) }}</p><span v-if="isLegacy(item)" class="mt-1 inline-block rounded bg-white/5 px-2 py-0.5 text-[9px] font-bold text-gray-500">DỮ LIỆU CŨ/MOCK</span></td><td class="p-4"><button class="font-mono text-xs font-bold text-red-300" @click="goToBooking(item)">{{ item.booking_code || `#${item.booking_id.slice(0, 8).toUpperCase()}` }}</button><p class="mt-1 max-w-52 truncate font-semibold text-white">{{ item.customer_name }}</p><p class="max-w-52 truncate text-xs text-gray-500">{{ item.movie_title }} · {{ item.branch_name }}</p></td><td class="p-4 font-semibold text-gray-300">{{ item.payment_method }}</td><td class="p-4 font-mono font-bold text-white">{{ money(item.amount) }}</td><td class="p-4"><span class="rounded-full border px-2.5 py-1 text-[11px] font-bold" :class="state(item).cls">{{ state(item).label }}</span><p v-if="item.refund_error" class="mt-2 max-w-56 text-xs text-rose-300">{{ item.refund_error }}</p></td><td class="p-4"><div class="flex items-center gap-1.5 text-xs font-bold" :class="verificationState(item).cls"><span class="material-symbols-outlined text-base">{{ verificationState(item).icon }}</span>{{ verificationState(item).label }}</div><p v-if="item.last_verified_at" class="mt-1 text-[10px] text-gray-500">Đối soát {{ dateTime(item.last_verified_at) }}</p></td><td class="p-4"><div class="flex justify-end gap-2"><button class="mini-btn" @click="showDetails(item)">Xem chi tiết</button><button v-if="isBranchAdmin && isVnpay(item) && item.provider_ref" class="mini-btn !border-sky-500/25 !text-sky-300" :disabled="busyId === item.id" @click="reconcile(item)">Đối soát</button><button v-if="canRetryRefund(item)" class="mini-btn !border-rose-500/25 !text-rose-300" @click="openRefund(item)">Thử hoàn lại</button></div></td></tr></tbody></table></div><div v-if="loading" class="p-12 text-center text-gray-400">Đang tải giao dịch...</div><div v-else-if="!rows.length" class="p-12 text-center"><span class="material-symbols-outlined text-4xl text-gray-600">search_off</span><p class="mt-2 font-bold text-gray-300">Không tìm thấy giao dịch phù hợp</p></div><footer v-if="totalPages > 1" class="flex flex-col items-center justify-between gap-3 border-t border-white/10 p-4 sm:flex-row"><span class="text-xs text-gray-400">Trang {{ currentPage }}/{{ totalPages }} · {{ total }} giao dịch</span><div class="flex gap-1"><button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">Trước</button><button v-for="page in visiblePages" :key="page" class="page-btn" :class="{ active: page === currentPage }" @click="currentPage = page">{{ page }}</button><button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">Sau</button></div></footer></section>

    <Teleport to="body"><div v-if="selected" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 p-4" @click.self="selected = null"><div class="max-h-[92vh] w-full max-w-4xl overflow-y-auto rounded-2xl border border-white/10 bg-[#181919] p-6"><div class="flex items-start justify-between"><div><p class="text-xs font-bold uppercase tracking-wider text-red-400">Chi tiết giao dịch</p><h3 class="mt-1 font-mono text-lg font-black text-white">{{ selected.id }}</h3><p class="mt-1 text-sm text-gray-400">Tạo lúc {{ dateTime(selected.created_at) }}</p></div><button class="text-gray-400 hover:text-white" @click="selected = null"><span class="material-symbols-outlined">close</span></button></div><div class="mt-6 grid gap-3 md:grid-cols-3"><div class="detail"><span>Khách hàng</span><strong>{{ selected.customer_name }}</strong><small>{{ selected.customer_email || '—' }}<br>{{ selected.customer_phone || '—' }}</small></div><div class="detail"><span>Đơn đặt vé</span><strong>{{ selected.booking_code || shortId(selected.booking_id) }}</strong><small>{{ selected.movie_title }}<br>{{ dateTime(selected.showtime_starts_at) }} · {{ seats(selected) }}</small></div><div class="detail"><span>Thanh toán</span><strong>{{ selected.payment_method }} · {{ state(selected).label }}</strong><small>{{ money(selected.amount) }}<br>{{ selected.bank_code || 'Không có mã ngân hàng' }}</small></div></div><div class="mt-5 grid gap-5 md:grid-cols-2"><div><h4 class="section-title">Dữ liệu cổng thanh toán</h4><div class="mt-3 space-y-2 text-sm"><p class="line"><span>Mã tham chiếu</span><button class="font-mono text-sky-300" @click="copy(selected.provider_ref)">{{ selected.provider_ref || '—' }}</button></p><p class="line"><span>Mã giao dịch VNPAY</span><b>{{ selected.provider_transaction_no || '—' }}</b></p><p class="line"><span>Mã ngân hàng</span><b>{{ selected.bank_transaction_no || '—' }}</b></p><p class="line"><span>Response / Status</span><b>{{ selected.response_code || '—' }} / {{ selected.provider_status || '—' }}</b></p><p class="line"><span>Thanh toán lúc</span><b>{{ dateTime(selected.paid_at || selected.provider_paid_at) }}</b></p></div></div><div><h4 class="section-title">Hoàn tiền</h4><div class="mt-3 space-y-2 text-sm"><p class="line"><span>Trạng thái</span><b>{{ state(selected).label }}</b></p><p class="line"><span>Số lần thử</span><b>{{ selected.refund_attempts }}</b></p><p class="line"><span>Mã hoàn tiền</span><b>{{ selected.refund_transaction_no || '—' }}</b></p><p v-if="selected.refund_error" class="rounded-lg bg-rose-500/10 p-3 text-rose-300">{{ selected.refund_error }}</p><p v-if="selected.payment_method !== 'VNPAY' && selected.status === 'REFUND_PENDING'" class="rounded-lg bg-amber-500/10 p-3 text-amber-300">Phương thức này cần được hoàn tiền thủ công.</p></div></div></div><div v-if="selected.combos.length" class="mt-5"><h4 class="section-title">Combo</h4><p v-for="combo in selected.combos" :key="combo.name" class="line mt-2 rounded-lg bg-white/[.03] p-3"><span>{{ combo.name }} × {{ combo.quantity }}</span><b>{{ money(combo.line_total) }}</b></p></div><div class="mt-6"><h4 class="section-title">Lịch sử trạng thái</h4><div class="mt-3 space-y-3"><div v-for="entry in history" :key="entry.id" class="relative border-l border-white/10 pl-5"><span class="absolute -left-1.5 top-1 h-3 w-3 rounded-full bg-red-500"></span><div class="flex flex-wrap justify-between gap-2"><b class="text-sm text-white">{{ entry.old_status || 'Khởi tạo' }} → {{ entry.new_status }}</b><span class="text-xs text-gray-500">{{ dateTime(entry.created_at) }}</span></div><p class="mt-1 text-xs text-gray-400">{{ entry.source }}<span v-if="entry.note"> · {{ entry.note }}</span></p></div><p v-if="!history.length" class="text-sm text-gray-500">Chưa có lịch sử thay đổi.</p></div></div><div class="mt-6 flex justify-end"><button class="mini-btn" @click="goToBooking(selected)">Mở đơn đặt vé</button></div></div></div></Teleport>

    <Teleport to="body"><div v-if="refundTarget" class="fixed inset-0 z-[110] flex items-center justify-center bg-black/80 p-4" @click.self="refundTarget = null"><div class="w-full max-w-lg rounded-2xl border border-rose-500/20 bg-[#181919] p-6"><h3 class="text-xl font-black text-white">Thử hoàn tiền VNPAY lại</h3><p class="mt-2 text-sm text-gray-400">Giao dịch {{ shortId(refundTarget.id) }} · {{ money(refundTarget.amount) }}. Thao tác chỉ được phép vì đơn đã hủy và lần hoàn trước thất bại.</p><label class="mt-4 block text-sm font-bold text-gray-300">Lý do/ghi chú<textarea v-model="refundReason" rows="4" class="field mt-2 resize-none" placeholder="Tối thiểu 5 ký tự..."></textarea></label><div class="mt-5 flex justify-end gap-2"><button class="mini-btn" @click="refundTarget = null">Đóng</button><button class="rounded-lg bg-red-600 px-4 py-2 text-sm font-bold text-white disabled:opacity-40" :disabled="busyId === refundTarget.id || refundReason.trim().length < 5" @click="submitRefund">Gửi lại yêu cầu</button></div></div></div></Teleport>
  </div>
</template>

<style scoped>
.panel{border:1px solid rgba(255,255,255,.08);border-radius:1rem;background:rgba(26,28,28,.72)}
.field{width:100%;border:1px solid rgba(255,255,255,.1);border-radius:.75rem;background:rgba(255,255,255,.035);padding:.7rem .85rem;color:#fff;outline:none}.field:focus{border-color:rgba(239,68,68,.7)}
.mini-btn{white-space:nowrap;border:1px solid rgba(255,255,255,.12);border-radius:.55rem;padding:.42rem .68rem;font-size:.75rem;font-weight:700;color:#d1d5db}.mini-btn:hover{background:rgba(255,255,255,.07);color:#fff}.mini-btn:disabled{opacity:.4}
.page-btn{min-width:2rem;border:1px solid rgba(255,255,255,.1);border-radius:.55rem;padding:.4rem .65rem;font-size:.75rem;font-weight:700;color:#d1d5db}.page-btn.active{border-color:#ef4444;background:#dc2626;color:#fff}.page-btn:disabled{opacity:.3}
.detail{display:flex;flex-direction:column;gap:.25rem;border:1px solid rgba(255,255,255,.08);border-radius:.75rem;background:rgba(255,255,255,.03);padding:.85rem}.detail span,.detail small{font-size:.75rem;color:#9ca3af}.detail strong{color:#fff}.section-title{font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:#9ca3af}.line{display:flex;justify-content:space-between;gap:1rem;color:#9ca3af}.line b{color:#e5e7eb}
</style>

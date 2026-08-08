<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { adminBackendService, type AdminBooking } from '~/services/api'
import { useUserStore } from '~/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isBranchAdmin = computed(() => userStore.currentUser?.role === 'branch-admin')
const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const rows = ref<AdminBooking[]>([])
const total = ref(0)
const summary = ref<Record<string, number>>({})
const loading = ref(false)
const error = ref('')
const search = ref('')
const status = ref('')
const startDate = ref('')
const endDate = ref('')
const currentPage = ref(1)
const selected = ref<AdminBooking | null>(null)
const actionMode = ref<'approve' | 'cancel' | 'reject' | null>(null)
const actionReason = ref('')
const pageSize = 15

const movieId = computed(() => String(route.query.movie_id || ''))
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const visiblePages = computed(() => {
  const pages: number[] = []
  for (let page = Math.max(1, currentPage.value - 2); page <= Math.min(totalPages.value, currentPage.value + 2); page++) pages.push(page)
  return pages
})
const kpis = computed(() => [
  { label: 'Tổng đơn', value: total.value, icon: 'receipt_long', tone: 'text-white' },
  { label: 'Đã xác nhận', value: summary.value.CONFIRMED || 0, icon: 'verified', tone: 'text-emerald-400' },
  { label: 'Chờ thanh toán', value: summary.value.PENDING || 0, icon: 'hourglass_top', tone: 'text-amber-400' },
  { label: 'Yêu cầu hủy', value: summary.value.CANCEL_REQUESTED || 0, icon: 'notification_important', tone: 'text-rose-400' },
  { label: 'Giá trị xác nhận', value: money(summary.value.CONFIRMED_VALUE || 0), icon: 'payments', tone: 'text-sky-400' },
])

const statusMeta: Record<string, { label: string; cls: string }> = {
  PENDING: { label: 'Chờ thanh toán', cls: 'border-amber-500/25 bg-amber-500/10 text-amber-300' },
  CONFIRMED: { label: 'Đã xác nhận', cls: 'border-emerald-500/25 bg-emerald-500/10 text-emerald-300' },
  CANCEL_REQUESTED: { label: 'Chờ duyệt hủy', cls: 'border-rose-500/25 bg-rose-500/10 text-rose-300' },
  CANCELLED: { label: 'Đã hủy', cls: 'border-zinc-500/25 bg-zinc-500/10 text-zinc-300' },
  EXPIRED: { label: 'Hết hạn', cls: 'border-zinc-500/25 bg-zinc-500/10 text-zinc-400' },
}

function money(value: number) { return `${Number(value || 0).toLocaleString('vi-VN')}đ` }
function dateTime(value?: string | null) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
}
function bookingCode(item: AdminBooking) { return item.ticket_code || `#${item.id.slice(0, 8).toUpperCase()}` }
function seats(item: AdminBooking) { return item.seats.map(seat => `${seat.row}${seat.number}`).join(', ') || '—' }
function state(item: AdminBooking) { return statusMeta[item.status] || { label: item.status, cls: 'border-white/10 bg-white/5 text-gray-300' } }
const paymentLabels: Record<string, string> = { PENDING: 'Đang chờ', SUCCESS: 'Thành công', FAILED: 'Thất bại', CANCELLED: 'Đã hủy', REFUND_PENDING: 'Chờ hoàn tiền', REFUNDED: 'Đã hoàn tiền' }
const checkinLabels: Record<string, string> = { NOT_ISSUED: 'Chưa phát hành vé', NOT_CHECKED_IN: 'Chưa check-in', PARTIAL: 'Check-in một phần', CHECKED_IN: 'Đã check-in' }
function paymentStatus(value: string) { return paymentLabels[value] || value }
function checkinStatus(item: AdminBooking) { return checkinLabels[item.checkin_status] || 'Chưa check-in' }

async function load() {
  loading.value = true
  error.value = ''
  try {
    const result = await adminBackendService.getBookings({
      branch_id: !isBranchAdmin.value && selectedBranch.value !== 'ALL' ? selectedBranch.value : undefined,
      movie_id: movieId.value || undefined,
      search: search.value.trim() || String(route.query.booking_id || '') || undefined,
      status: status.value || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      limit: pageSize,
      skip: (currentPage.value - 1) * pageSize,
    })
    rows.value = result.bookings
    total.value = result.total
    summary.value = result.summary || {}
  } catch (cause: any) {
    error.value = cause?.response?.data?.detail || cause?.message || 'Không thể tải danh sách đơn đặt vé.'
  } finally {
    loading.value = false
  }
}

function applyFilters() { currentPage.value = 1; void load() }
function resetFilters() {
  search.value = ''; status.value = ''; startDate.value = ''; endDate.value = ''; currentPage.value = 1
  if (movieId.value) { const query = { ...route.query }; delete query.movie_id; void router.replace({ query }) }
  else void load()
}
function openAction(item: AdminBooking, mode: 'approve' | 'cancel' | 'reject') {
  selected.value = item; actionMode.value = mode; actionReason.value = mode === 'approve' ? (item.cancellation_reason || '') : ''
}
async function submitAction() {
  if (!selected.value || !actionMode.value || actionReason.value.trim().length < 5) return
  loading.value = true; error.value = ''
  try {
    if (actionMode.value === 'reject') await adminBackendService.rejectBookingCancellation(selected.value.id, actionReason.value.trim())
    else await adminBackendService.cancelBooking(selected.value.id, actionReason.value.trim())
    selected.value = null; actionMode.value = null; actionReason.value = ''; await load()
  } catch (cause: any) {
    error.value = cause?.response?.data?.detail || cause?.message || 'Không thể xử lý đơn đặt vé.'
  } finally { loading.value = false }
}
function goToPayment(item: AdminBooking) {
  const payment = item.payments[0]
  void router.push({ query: { tab: 'payments', ...(payment ? { payment_id: payment.id } : { booking_id: item.id }) } })
}

let refreshTimer: ReturnType<typeof setInterval> | undefined
onMounted(() => { void load(); refreshTimer = setInterval(() => { if (!document.hidden && !loading.value && !actionMode.value) void load() }, 30000) })
onUnmounted(() => { if (refreshTimer) clearInterval(refreshTimer) })
watch(currentPage, () => void load())
watch(selectedBranch, () => { currentPage.value = 1; if (!isBranchAdmin.value) void load() })
watch(movieId, () => { currentPage.value = 1; void load() })
</script>

<template>
  <div class="space-y-6">
    <header class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <div class="flex items-center gap-2"><span class="material-symbols-outlined text-red-500">confirmation_number</span><h2 class="text-2xl font-black text-white">{{ isBranchAdmin ? 'Quản lý đơn đặt vé' : 'Giám sát đơn đặt vé' }}</h2></div>
        <p class="mt-1 text-sm text-gray-400">{{ isBranchAdmin ? 'Tra cứu và xử lý đơn tại chi nhánh được phân công.' : 'Tra soát đơn trên toàn hệ thống ở chế độ chỉ đọc.' }}</p>
      </div>
      <span v-if="!isBranchAdmin" class="w-fit rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1 text-xs font-bold text-sky-300">Chế độ giám sát</span>
    </header>

    <div v-if="movieId" class="flex items-center justify-between rounded-xl border border-violet-500/25 bg-violet-500/10 px-4 py-3 text-sm text-violet-200"><span>Đang lọc các đơn của phim được chọn từ trang Giám sát lịch chiếu.</span><button class="font-bold hover:text-white" @click="resetFilters">Bỏ lọc phim</button></div>

    <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
      <article v-for="item in kpis" :key="item.label" class="panel flex items-center gap-3 p-4"><span class="material-symbols-outlined rounded-xl bg-white/5 p-2 text-gray-400">{{ item.icon }}</span><div><p class="text-[11px] font-bold uppercase tracking-wider text-gray-500">{{ item.label }}</p><p class="mt-1 text-xl font-black" :class="item.tone">{{ item.value }}</p></div></article>
    </section>

    <section class="panel grid gap-3 p-4 lg:grid-cols-[2fr_1fr_1fr_1fr_auto]">
      <label class="relative"><span class="material-symbols-outlined absolute left-3 top-3 text-lg text-gray-500">search</span><input v-model="search" class="field pl-10" placeholder="Mã đơn, khách hàng, phim..." @keyup.enter="applyFilters"></label>
      <select v-model="status" class="field"><option value="">Tất cả trạng thái</option><option v-for="(meta, key) in statusMeta" :key="key" :value="key">{{ meta.label }}</option></select>
      <input v-model="startDate" type="date" class="field" title="Ngày tạo đơn từ">
      <input v-model="endDate" type="date" class="field" title="Ngày tạo đơn đến">
      <div class="flex gap-2"><button class="rounded-xl bg-red-600 px-4 py-2 font-bold text-white hover:bg-red-500 disabled:opacity-50" :disabled="loading" @click="applyFilters">Lọc</button><button class="rounded-xl border border-white/10 px-3 text-gray-300 hover:bg-white/5" title="Xóa bộ lọc" @click="resetFilters"><span class="material-symbols-outlined text-lg">filter_alt_off</span></button></div>
      <p class="text-xs text-gray-500 lg:col-span-5">Khoảng ngày được tính theo thời điểm khách tạo đơn.</p>
    </section>

    <div v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm font-medium text-rose-300">{{ error }}</div>

    <section class="panel overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1050px] text-left text-sm">
          <thead class="border-b border-white/10 bg-white/[.04] text-xs uppercase tracking-wider text-gray-400"><tr><th class="p-4">Mã đơn / khách hàng</th><th class="p-4">Phim & suất chiếu</th><th class="p-4">Ghế</th><th class="p-4">Tổng tiền</th><th class="p-4">Trạng thái</th><th class="p-4 text-right">Thao tác</th></tr></thead>
          <tbody>
            <tr v-for="item in rows" :key="item.id" class="border-b border-white/5 hover:bg-white/[.03]">
              <td class="p-4"><button class="font-mono text-xs font-bold text-red-300 hover:text-red-200" @click="selected = item">{{ bookingCode(item) }}</button><p class="mt-1 max-w-48 truncate font-semibold text-white">{{ item.customer_name }}</p><p class="max-w-48 truncate text-xs text-gray-500">{{ item.customer_email || item.customer_phone || 'Không có liên hệ' }}</p></td>
              <td class="p-4"><p class="font-bold text-white">{{ item.movie_title }}</p><p class="mt-1 text-xs text-gray-400">{{ item.branch_name }} · {{ item.auditorium_name }}</p><p class="mt-1 text-xs text-red-300">{{ dateTime(item.starts_at) }}</p></td>
              <td class="p-4 font-mono text-gray-300">{{ seats(item) }}</td>
              <td class="p-4"><p class="font-mono font-bold text-white">{{ money(item.total_price) }}</p><p v-if="item.discount_amount" class="text-xs text-emerald-400">Giảm {{ money(item.discount_amount) }}</p></td>
              <td class="p-4"><span class="rounded-full border px-2.5 py-1 text-[11px] font-bold" :class="state(item).cls">{{ state(item).label }}</span><p v-if="item.checkin_status==='CHECKED_IN'||item.checkin_status==='PARTIAL'" class="mt-2 text-[11px] font-bold text-sky-300">{{ checkinStatus(item) }}</p></td>
              <td class="p-4"><div class="flex justify-end gap-2"><button class="mini-btn" @click="selected = item">Xem chi tiết</button><template v-if="isBranchAdmin && item.status === 'CANCEL_REQUESTED'"><button v-if="item.can_cancel" class="mini-btn !border-rose-500/30 !text-rose-300" @click="openAction(item, 'approve')">Duyệt hủy</button><button class="mini-btn" @click="openAction(item, 'reject')">Từ chối</button></template><button v-else-if="isBranchAdmin && ['PENDING','CONFIRMED'].includes(item.status) && item.can_cancel" class="mini-btn !text-rose-300" @click="openAction(item, 'cancel')">Hủy đơn</button></div></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="loading" class="p-12 text-center text-gray-400">Đang tải dữ liệu...</div>
      <div v-else-if="!rows.length" class="p-12 text-center"><span class="material-symbols-outlined text-4xl text-gray-600">search_off</span><p class="mt-2 font-bold text-gray-300">Không tìm thấy đơn phù hợp</p></div>
      <footer v-if="totalPages > 1" class="flex flex-col items-center justify-between gap-3 border-t border-white/10 p-4 sm:flex-row"><span class="text-xs text-gray-400">Trang {{ currentPage }}/{{ totalPages }} · {{ total }} đơn</span><div class="flex gap-1"><button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">Trước</button><button v-for="page in visiblePages" :key="page" class="page-btn" :class="{ active: page === currentPage }" @click="currentPage = page">{{ page }}</button><button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">Sau</button></div></footer>
    </section>

    <Teleport to="body">
      <div v-if="selected" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 p-4" @click.self="selected = null; actionMode = null">
        <div class="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-white/10 bg-[#181919] p-6 shadow-2xl">
          <div class="flex items-start justify-between"><div><p class="text-xs font-bold uppercase tracking-wider text-red-400">{{ bookingCode(selected) }}</p><h3 class="mt-1 text-2xl font-black text-white">{{ selected.movie_title }}</h3><p class="mt-1 text-sm text-gray-400">Đặt lúc {{ dateTime(selected.created_at) }}</p></div><button class="text-gray-400 hover:text-white" @click="selected = null; actionMode = null"><span class="material-symbols-outlined">close</span></button></div>
          <div v-if="!actionMode" class="mt-6 space-y-5">
            <div class="grid gap-3 sm:grid-cols-4"><div class="detail"><span>Khách hàng</span><strong>{{ selected.customer_name }}</strong><small>{{ selected.customer_email || '—' }}<br>{{ selected.customer_phone || '—' }}</small></div><div class="detail"><span>Suất chiếu</span><strong>{{ dateTime(selected.starts_at) }}</strong><small>{{ selected.branch_name }} · Phòng {{ selected.auditorium_name }}</small></div><div class="detail"><span>Ghế</span><strong>{{ seats(selected) }}</strong><small>{{ selected.quantity }} vé · {{ selected.sales_channel }}</small></div><div class="detail"><span>Soát vé</span><strong :class="selected.checkin_status==='CHECKED_IN'?'!text-sky-300':''">{{ checkinStatus(selected) }}</strong><small>{{ selected.checked_in_count || 0 }}/{{ selected.ticket_count || selected.quantity }} vé<template v-if="selected.checked_in_at"><br>{{ dateTime(selected.checked_in_at) }}</template></small></div></div>
            <div class="grid gap-5 sm:grid-cols-2"><div><h4 class="section-title">Chi tiết thanh toán</h4><div class="mt-3 space-y-2 text-sm"><p class="line"><span>Tạm tính</span><b>{{ money(selected.subtotal_price) }}</b></p><p class="line"><span>Khuyến mãi {{ selected.promotion_code || '' }}</span><b class="text-emerald-400">-{{ money(selected.discount_amount) }}</b></p><p class="line border-t border-white/10 pt-2"><span>Tổng cộng</span><b class="text-lg text-white">{{ money(selected.total_price) }}</b></p></div></div><div><h4 class="section-title">Giao dịch</h4><div v-if="selected.payments.length" class="mt-3 space-y-2"><div v-for="payment in selected.payments" :key="payment.id" class="detail"><strong>{{ payment.method }} · {{ paymentStatus(payment.status) }}</strong><small>{{ payment.transaction_no || payment.provider_ref || 'Chưa có mã giao dịch' }}</small><small v-if="payment.refund_error" class="!text-amber-300">{{ payment.refund_error }}</small></div></div><p v-else class="mt-3 text-sm text-gray-500">Chưa phát sinh thanh toán.</p></div></div>
            <div v-if="!selected.can_cancel && ['PENDING','CONFIRMED','CANCEL_REQUESTED'].includes(selected.status)" class="rounded-xl border border-amber-500/20 bg-amber-500/10 p-3 text-sm text-amber-200">Không thể hủy đơn này vì suất chiếu đã bắt đầu hoặc vé đã được check-in.</div>
            <div v-if="selected.combos.length"><h4 class="section-title">Combo bắp nước</h4><div class="mt-2 space-y-2"><p v-for="combo in selected.combos" :key="combo.name" class="line rounded-lg bg-white/[.03] p-3"><span>{{ combo.name }} × {{ combo.quantity }}</span><b>{{ money(combo.line_total) }}</b></p></div></div>
            <div v-if="selected.cancellation_reason || selected.cancellation_review_note" class="rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-200"><p v-if="selected.cancellation_reason"><b>Yêu cầu hủy:</b> {{ selected.cancellation_reason }}</p><p v-if="selected.cancellation_review_note" class="mt-1"><b>Kết quả xử lý:</b> {{ selected.cancellation_review_note }}</p></div>
            <div class="flex justify-end"><button class="mini-btn" @click="goToPayment(selected)">Mở trang thanh toán</button></div>
          </div>
          <div v-else class="mt-6"><div class="rounded-xl border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-200"><b>{{ actionMode === 'reject' ? 'Từ chối yêu cầu hủy' : actionMode === 'approve' ? 'Duyệt hủy và hoàn tiền' : 'Hủy đơn bởi chi nhánh' }}</b><p class="mt-1">{{ actionMode === 'reject' ? 'Đơn sẽ trở lại trạng thái đã xác nhận.' : 'Ghế sẽ được giải phóng, combo được hoàn kho, vé mất hiệu lực và giao dịch thành công được chuyển sang quy trình hoàn tiền.' }}</p></div><label class="mt-4 block text-sm font-bold text-gray-300">Lý do xử lý (ít nhất 5 ký tự)<textarea v-model="actionReason" rows="4" class="field mt-2 resize-none" placeholder="Nhập lý do rõ ràng để lưu lịch sử..."></textarea></label><div class="mt-5 flex justify-end gap-2"><button class="mini-btn" @click="actionMode = null">Quay lại</button><button class="rounded-lg bg-red-600 px-4 py-2 text-sm font-bold text-white disabled:opacity-40" :disabled="loading || actionReason.trim().length < 5" @click="submitAction">Xác nhận xử lý</button></div></div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.panel{border:1px solid rgba(255,255,255,.08);border-radius:1rem;background:rgba(26,28,28,.72)}
.field{width:100%;border:1px solid rgba(255,255,255,.1);border-radius:.75rem;background:rgba(255,255,255,.035);padding:.7rem .85rem;color:#fff;outline:none}.field:focus{border-color:rgba(239,68,68,.7)}
.mini-btn{white-space:nowrap;border:1px solid rgba(255,255,255,.12);border-radius:.55rem;padding:.4rem .65rem;font-size:.75rem;font-weight:700;color:#d1d5db}.mini-btn:hover{background:rgba(255,255,255,.07);color:#fff}
.page-btn{min-width:2rem;border:1px solid rgba(255,255,255,.1);border-radius:.55rem;padding:.4rem .65rem;font-size:.75rem;font-weight:700;color:#d1d5db}.page-btn.active{border-color:#ef4444;background:#dc2626;color:white}.page-btn:disabled{opacity:.3}
.detail{display:flex;flex-direction:column;gap:.25rem;border:1px solid rgba(255,255,255,.08);border-radius:.75rem;background:rgba(255,255,255,.03);padding:.85rem}.detail span,.detail small{font-size:.75rem;color:#9ca3af}.detail strong{color:#fff}
.section-title{font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:#9ca3af}.line{display:flex;justify-content:space-between;gap:1rem;color:#9ca3af}.line b{color:#e5e7eb}
</style>

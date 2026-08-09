<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { adminBackendService } from '~/services/api'

const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const localDate = (date: Date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
const today = new Date()
const endDate = ref(localDate(today))
const startDate = ref(localDate(new Date(today.getFullYear(), today.getMonth(), today.getDate() - 29)))
const groupBy = ref<'day' | 'week' | 'month'>('day')
const revenue = ref<any>({ total: 0, data: [] })
const occupancyReport = ref<any>({ data: [], occupancy_rate: 0, total_capacity: 0, total_sold: 0 })
const movies = ref<any[]>([])
const error = ref('')
const loading = ref(false)
const lastUpdated = ref<Date | null>(null)

const occupancy = computed(() => occupancyReport.value.data || [])
const totalTicketsSold = computed(() => Number(revenue.value.tickets_sold || 0))
const totalMovies = computed(() => Number(movies.value[0]?.total_movies || 0))
const maxMovieRevenue = computed(() => Math.max(...movies.value.map(movie => Number(movie.ticket_revenue || movie.revenue) || 0), 1))
const maxTrendRevenue = computed(() => Math.max(...(revenue.value.data || []).map((item: any) => Number(item.value) || 0), 1))
const podiumMovies = computed(() => [2, 1, 3].map(rank => movies.value.find(movie => movie.rank === rank)).filter(Boolean))
const comparison = computed(() => {
  const change = revenue.value.change_percent
  if (change === null || change === undefined) return { label: 'Chưa có dữ liệu kỳ trước', cls: 'text-gray-500', icon: 'remove' }
  return { label: `${change > 0 ? '+' : ''}${change}% so với kỳ trước`, cls: change >= 0 ? 'text-emerald-400' : 'text-rose-400', icon: change >= 0 ? 'trending_up' : 'trending_down' }
})
const kpis = computed(() => [
  { label: 'Doanh thu xác nhận', value: money(revenue.value.total), note: comparison.value.label, tone: 'text-emerald-400', icon: 'payments', noteTone: comparison.value.cls },
  { label: 'Doanh thu vé (trước giảm)', value: money(revenue.value.ticket_revenue), note: `${totalTicketsSold.value.toLocaleString('vi-VN')} vé`, tone: 'text-sky-400', icon: 'confirmation_number', noteTone: 'text-gray-500' },
  { label: 'Doanh thu combo (trước giảm)', value: money(revenue.value.combo_revenue), note: 'Theo các đơn đã thanh toán', tone: 'text-orange-300', icon: 'fastfood', noteTone: 'text-gray-500' },
  { label: 'Tổng giảm giá', value: money(revenue.value.discount_amount), note: 'Khuyến mãi đã áp dụng', tone: 'text-violet-300', icon: 'sell', noteTone: 'text-gray-500' },
  { label: 'Hoàn tiền trong kỳ', value: money(revenue.value.refunded_amount), note: 'Theo ngày hoàn tiền', tone: 'text-rose-300', icon: 'currency_exchange', noteTone: 'text-gray-500' },
  { label: 'Tỷ lệ lấp đầy', value: `${Number(occupancyReport.value.occupancy_rate || 0).toLocaleString('vi-VN')}%`, note: `${occupancyReport.value.total_sold || 0}/${occupancyReport.value.total_capacity || 0} ghế`, tone: 'text-amber-300', icon: 'event_seat', noteTone: 'text-gray-500' },
])

function money(value: unknown) { return `${Number(value || 0).toLocaleString('vi-VN')}đ` }
function formatDate(value: string) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(`${value}T00:00:00`))
}
function trendLabel(value: string) {
  if (groupBy.value === 'month') return new Intl.DateTimeFormat('vi-VN', { month: '2-digit', year: 'numeric' }).format(new Date(`${value}T00:00:00`))
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit' }).format(new Date(`${value}T00:00:00`))
}
function validateRange() {
  if (!startDate.value || !endDate.value) return 'Vui lòng chọn đầy đủ khoảng ngày.'
  if (startDate.value > endDate.value) return 'Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.'
  return ''
}
async function load() {
  const validation = validateRange()
  if (validation) { error.value = validation; return }
  loading.value = true; error.value = ''
  try {
    const branchId = selectedBranch.value === 'ALL' ? undefined : selectedBranch.value
    const [revenueResult, occupancyResult, movieResult] = await Promise.all([
      adminBackendService.getRevenueReport(startDate.value, endDate.value, groupBy.value, branchId),
      adminBackendService.getOccupancyReport(startDate.value, endDate.value, branchId),
      adminBackendService.getTopMoviesReport(startDate.value, endDate.value, branchId),
    ])
    revenue.value = revenueResult
    occupancyReport.value = occupancyResult
    movies.value = movieResult
    lastUpdated.value = new Date()
  } catch (cause: any) {
    error.value = cause?.response?.data?.detail || cause?.message || 'Không thể tải báo cáo.'
  } finally { loading.value = false }
}
function setPreset(preset: 'today' | '7d' | '30d' | 'month') {
  const end = new Date()
  let start = new Date(end)
  if (preset === '7d') start.setDate(end.getDate() - 6)
  if (preset === '30d') start.setDate(end.getDate() - 29)
  if (preset === 'month') start = new Date(end.getFullYear(), end.getMonth(), 1)
  startDate.value = localDate(start); endDate.value = localDate(end)
  groupBy.value = preset === 'month' ? 'day' : groupBy.value
  void load()
}
function csvCell(value: unknown) { return `"${String(value ?? '').replaceAll('"', '""')}"` }
function exportCsv() {
  if (!revenue.value.data?.length && !movies.value.length && !occupancy.value.length) return
  const rows: unknown[][] = [
    ['BÁO CÁO VẬN HÀNH CINEAI'],
    ['Khoảng ngày', startDate.value, endDate.value],
    ['Múi giờ', revenue.value.timezone || 'Asia/Ho_Chi_Minh'],
    ['Chi nhánh', selectedBranch.value === 'ALL' ? 'Tất cả chi nhánh' : selectedBranch.value],
    [],
    ['CHỈ SỐ TỔNG HỢP', 'Giá trị'],
    ['Doanh thu xác nhận', revenue.value.total],
    ['Doanh thu vé trước giảm', revenue.value.ticket_revenue],
    ['Doanh thu combo trước giảm', revenue.value.combo_revenue],
    ['Giảm giá', revenue.value.discount_amount],
    ['Hoàn tiền trong kỳ', revenue.value.refunded_amount],
    ['Số vé bán', revenue.value.tickets_sold],
    ['Tỷ lệ lấp đầy', `${occupancyReport.value.occupancy_rate || 0}%`],
    [],
    ['XU HƯỚNG DOANH THU', 'Doanh thu'],
    ...(revenue.value.data || []).map((item: any) => [item.label, item.value]),
    [],
    ['XẾP HẠNG PHIM', 'Phim', 'Vé bán', 'Doanh thu vé', 'Giá trị đơn'],
    ...movies.value.map(movie => [movie.rank, movie.title, movie.tickets_sold, movie.ticket_revenue, movie.order_revenue]),
    [],
    ['HIỆU SUẤT CHI NHÁNH', 'Số suất', 'Ghế bán', 'Ghế cung ứng', 'Lấp đầy'],
    ...occupancy.value.map((branch: any) => [branch.branch_name, branch.showtimes, branch.sold, branch.capacity, `${branch.occupancy_rate}%`]),
  ]
  const blob = new Blob([`﻿${rows.map(row => row.map(csvCell).join(',')).join('\n')}`], { type: 'text/csv;charset=utf-8' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `cineai-report-${startDate.value}-${endDate.value}.csv`
  link.click(); URL.revokeObjectURL(link.href)
}

onMounted(load)
watch(selectedBranch, () => void load())
</script>

<template>
  <div class="space-y-6">
    <header class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between"><div><div class="flex items-center gap-2"><span class="material-symbols-outlined text-red-500">analytics</span><h2 class="text-2xl font-black text-white">Báo cáo vận hành</h2></div><p class="mt-1 text-sm text-gray-400">Doanh thu tính theo ngày thanh toán; lấp đầy tính theo ngày diễn ra suất chiếu, múi giờ Việt Nam.</p></div><div class="flex items-center gap-3"><span v-if="lastUpdated" class="text-xs text-gray-500">Cập nhật {{ lastUpdated.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }}</span><button class="mini-btn" :disabled="loading" @click="exportCsv"><span class="material-symbols-outlined mr-1 align-middle text-sm">download</span>Xuất CSV đầy đủ</button></div></header>

    <section class="panel space-y-4 p-4"><div class="flex flex-wrap gap-2"><button class="preset" @click="setPreset('today')">Hôm nay</button><button class="preset" @click="setPreset('7d')">7 ngày</button><button class="preset" @click="setPreset('30d')">30 ngày</button><button class="preset" @click="setPreset('month')">Tháng này</button></div><div class="grid items-end gap-3 md:grid-cols-[1fr_1fr_1fr_auto]"><label class="label">Từ ngày<input v-model="startDate" type="date" class="field mt-1"></label><label class="label">Đến ngày<input v-model="endDate" type="date" class="field mt-1"></label><label class="label">Nhóm biểu đồ<select v-model="groupBy" class="field mt-1"><option value="day">Theo ngày</option><option value="week">Theo tuần</option><option value="month">Theo tháng</option></select></label><button class="rounded-xl bg-red-600 px-6 py-3 text-sm font-bold text-white hover:bg-red-500 disabled:opacity-40" :disabled="loading" @click="load">Áp dụng báo cáo</button></div></section>

    <div v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm font-medium text-rose-300">{{ error }}</div>
    <div v-if="loading" class="panel flex items-center justify-center gap-3 p-14 text-gray-400"><span class="h-8 w-8 animate-spin rounded-full border-4 border-red-500 border-t-transparent"></span>Đang tổng hợp số liệu...</div>

    <template v-else>
      <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3"><article v-for="item in kpis" :key="item.label" class="panel relative overflow-hidden p-5"><span class="material-symbols-outlined absolute -bottom-2 right-1 text-7xl text-white/[.035]">{{ item.icon }}</span><p class="text-[11px] font-bold uppercase tracking-wider text-gray-500">{{ item.label }}</p><p class="mt-2 text-2xl font-black" :class="item.tone">{{ item.value }}</p><p class="mt-1 text-xs" :class="item.noteTone">{{ item.note }}</p></article></section>

      <section class="panel p-5"><div class="flex flex-col gap-2 border-b border-white/5 pb-4 sm:flex-row sm:items-center sm:justify-between"><div><h3 class="font-bold text-white">Xu hướng doanh thu</h3><p class="text-xs text-gray-500">Doanh thu từ giao dịch thành công theo {{ groupBy === 'day' ? 'ngày' : groupBy === 'week' ? 'tuần' : 'tháng' }}.</p></div><div class="flex items-center gap-1 text-xs font-bold" :class="comparison.cls"><span class="material-symbols-outlined text-base">{{ comparison.icon }}</span>{{ comparison.label }}</div></div><div v-if="revenue.data?.length" class="mt-5 flex h-64 items-end gap-2 overflow-x-auto pb-2"><div v-for="item in revenue.data" :key="item.label" class="group flex h-full min-w-[54px] flex-1 flex-col justify-end"><div class="mb-1 text-center text-[10px] font-bold text-emerald-300 opacity-0 transition-opacity group-hover:opacity-100">{{ money(item.value) }}</div><div class="mx-auto w-3/5 min-h-[3px] rounded-t-lg bg-gradient-to-t from-red-600 to-orange-400 transition-all" :style="{ height: `${Math.max((Number(item.value) / maxTrendRevenue) * 88, 2)}%` }" :title="`${formatDate(item.label)}: ${money(item.value)}`"></div><p class="mt-2 truncate text-center text-[10px] text-gray-500">{{ trendLabel(item.label) }}</p></div></div><div v-else class="py-16 text-center text-sm text-gray-500">Chưa phát sinh doanh thu trong khoảng đã chọn.</div></section>

      <section v-if="podiumMovies.length" class="panel relative overflow-hidden p-5 sm:p-7">
        <div class="pointer-events-none absolute inset-x-0 top-0 h-56 bg-[radial-gradient(circle_at_top,rgba(245,158,11,.13),transparent_65%)]"></div>
        <div class="relative text-center"><p class="text-xs font-black uppercase tracking-[.25em] text-amber-400">CineAI Hall of Fame</p><h3 class="mt-2 text-2xl font-black text-white">Bảng vàng phim doanh thu cao nhất</h3><p class="mt-1 text-sm text-gray-500">Xếp hạng theo doanh thu vé trong kỳ báo cáo</p></div>
        <div class="relative mx-auto mt-8 grid max-w-4xl grid-cols-3 items-end gap-2 sm:gap-5">
          <article v-for="movie in podiumMovies" :key="`podium-${movie.movie_id}`" class="flex min-w-0 flex-col items-center" :class="movie.rank === 1 ? 'z-10' : ''">
            <div v-if="movie.rank === 1" class="mb-1 animate-bounce text-3xl sm:text-4xl">👑</div>
            <div class="relative w-full max-w-[170px] overflow-hidden rounded-xl border bg-black/40 shadow-2xl" :class="movie.rank === 1 ? 'border-amber-400/70 shadow-amber-500/20' : movie.rank === 2 ? 'border-slate-300/40' : 'border-orange-500/40'">
              <img :src="movie.poster_url || '/images/movie-placeholder.svg'" :alt="movie.title" class="h-32 w-full object-cover sm:h-52" :class="movie.rank === 1 ? 'sm:h-60' : ''">
              <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black via-black/80 to-transparent p-2 pt-10 text-center sm:p-3 sm:pt-14"><p class="truncate text-xs font-black text-white sm:text-sm" :title="movie.title">{{ movie.title }}</p><p class="mt-1 hidden text-[10px] text-gray-300 sm:block">{{ movie.tickets_sold }} vé · {{ money(movie.ticket_revenue) }}</p></div>
              <span class="absolute left-2 top-2 flex h-8 w-8 items-center justify-center rounded-full border text-sm font-black shadow-lg" :class="movie.rank === 1 ? 'border-yellow-200 bg-amber-400 text-amber-950' : movie.rank === 2 ? 'border-white bg-slate-300 text-slate-900' : 'border-orange-200 bg-orange-600 text-white'">{{ movie.rank }}</span>
            </div>
            <div class="mt-3 flex w-full flex-col items-center justify-center rounded-t-xl border-x border-t text-center shadow-inner" :class="movie.rank === 1 ? 'h-28 border-amber-400/35 bg-gradient-to-b from-amber-400/30 to-amber-700/15 sm:h-36' : movie.rank === 2 ? 'h-20 border-slate-300/25 bg-gradient-to-b from-slate-300/20 to-slate-600/10 sm:h-24' : 'h-14 border-orange-500/25 bg-gradient-to-b from-orange-500/20 to-orange-800/10 sm:h-20'">
              <span class="text-xl sm:text-3xl">{{ movie.rank === 1 ? '🥇' : movie.rank === 2 ? '🥈' : '🥉' }}</span><b class="mt-1 text-xs text-white sm:text-sm">TOP {{ movie.rank }}</b><span class="mt-1 text-[9px] font-bold text-emerald-300 sm:text-xs">{{ money(movie.ticket_revenue) }}</span>
            </div>
          </article>
        </div>
      </section>

      <div class="grid gap-6 xl:grid-cols-2">
        <section class="panel p-5"><div class="border-b border-white/5 pb-4"><h3 class="font-bold text-white">Xếp hạng phim theo doanh thu vé</h3><p class="text-xs text-gray-500">Không bao gồm doanh thu combo; số tiền là giá vé trước giảm giá.</p></div><div class="mt-4 space-y-5"><div v-for="movie in movies" :key="movie.movie_id"><div class="flex items-center justify-between gap-3 text-sm"><span class="min-w-0 truncate font-bold text-white"><b class="mr-2 text-red-400">#{{ movie.rank }}</b>{{ movie.title }}</span><span class="shrink-0 text-xs text-gray-400">{{ movie.tickets_sold }} vé · <b class="text-emerald-400">{{ money(movie.ticket_revenue) }}</b></span></div><div class="mt-2 h-2.5 overflow-hidden rounded-full bg-white/5"><div class="h-full rounded-full bg-gradient-to-r from-red-600 to-orange-400" :style="{ width: `${Number(movie.ticket_revenue) * 100 / maxMovieRevenue}%` }"></div></div><p class="mt-1 text-right text-[10px] text-gray-600">Tổng giá trị đơn gồm combo: {{ money(movie.order_revenue) }}</p></div><p v-if="!movies.length" class="py-14 text-center text-sm text-gray-500">Chưa có phim phát sinh doanh thu.</p></div></section>

        <section class="panel p-5"><div class="border-b border-white/5 pb-4"><h3 class="font-bold text-white">Hiệu suất chi nhánh</h3><p class="text-xs text-gray-500">Ghế cung ứng = sức chứa phòng × số suất chiếu hợp lệ.</p></div><div class="mt-4 space-y-5"><div v-for="branch in occupancy" :key="branch.branch_id"><div class="flex items-center justify-between gap-3 text-sm"><span class="font-bold text-white">{{ branch.branch_name }}</span><span class="text-xs text-gray-400">{{ branch.showtimes }} suất · {{ branch.sold }}/{{ branch.capacity }} ghế · <b :class="branch.occupancy_rate >= 70 ? 'text-emerald-400' : branch.occupancy_rate >= 30 ? 'text-sky-400' : 'text-rose-400'">{{ branch.occupancy_rate }}%</b></span></div><div class="mt-2 h-3 overflow-hidden rounded-full bg-white/5"><div class="h-full rounded-full" :class="branch.occupancy_rate >= 70 ? 'bg-emerald-500' : branch.occupancy_rate >= 30 ? 'bg-sky-500' : 'bg-rose-500'" :style="{ width: `${Math.min(branch.occupancy_rate, 100)}%` }"></div></div></div><p v-if="!occupancy.length" class="py-14 text-center text-sm text-gray-500">Không có suất chiếu trong khoảng đã chọn.</p></div></section>
      </div>
      <p class="text-xs leading-relaxed text-gray-600">Doanh thu xác nhận chỉ gồm giao dịch đang ở trạng thái thành công. Khoản đã hoàn không được tính vào doanh thu xác nhận và được trình bày riêng theo ngày hoàn tiền. Số liệu báo cáo được chốt theo trạng thái hiện tại của hệ thống.</p>
    </template>
  </div>
</template>

<style scoped>
.panel{border:1px solid rgba(255,255,255,.08);border-radius:1rem;background:rgba(26,28,28,.72)}
.field{width:100%;border:1px solid rgba(255,255,255,.1);border-radius:.75rem;background:rgba(255,255,255,.035);padding:.7rem .85rem;color:#fff;outline:none}.field:focus{border-color:rgba(239,68,68,.7)}
.label{font-size:.7rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:#9ca3af}.preset,.mini-btn{white-space:nowrap;border:1px solid rgba(255,255,255,.12);border-radius:.6rem;padding:.45rem .75rem;font-size:.75rem;font-weight:700;color:#d1d5db}.preset:hover,.mini-btn:hover{background:rgba(255,255,255,.07);color:#fff}.mini-btn:disabled{opacity:.4}
</style>

<script setup lang="ts">
import { adminService, type BranchAdminStats } from '~/services/api'

const stats = ref<BranchAdminStats | null>(null)
const loading = ref(true)
const error = ref('')
const period = ref<'today' | '7d' | 'month'>('today')
const lastUpdated = ref<Date | null>(null)

const periodLabel = computed(() => period.value === 'today' ? 'hôm nay' : period.value === '7d' ? '7 ngày gần nhất' : 'tháng này')
const maxChartValue = computed(() => Math.max(...(stats.value?.salesChartData || []).map(item => Number(item.revenue || 0)), 1))
const podiumMovies = computed(() => [2, 1, 3].map(rank => stats.value?.topMovies?.[rank - 1]).filter(Boolean))
const upcomingShowtimes = computed(() => [...(stats.value?.showtimesList || [])].sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime()).slice(0, 8))
const alerts = computed(() => {
  if (!stats.value) return []
  return [
    stats.value.pendingPayments ? { icon: 'hourglass_top', tone: 'amber', title: `${stats.value.pendingPayments} giao dịch đang chờ`, text: 'Kiểm tra phản hồi từ cổng thanh toán.', tab: 'payments' } : null,
    stats.value.refundPending ? { icon: 'currency_exchange', tone: 'rose', title: `${stats.value.refundPending} giao dịch chờ hoàn`, text: 'Cần theo dõi kết quả hoàn tiền.', tab: 'payments' } : null,
    stats.value.attentionCount && !stats.value.pendingPayments && !stats.value.refundPending ? { icon: 'warning', tone: 'amber', title: `${stats.value.attentionCount} mục cần kiểm tra`, text: 'Có suất nháp hoặc suất đã hủy trong kỳ.', tab: 'showtimes' } : null,
  ].filter(Boolean) as Array<{ icon: string; tone: string; title: string; text: string; tab: string }>
})

function money(value: number) { return `${Number(value || 0).toLocaleString('vi-VN')}đ` }
function shortDate(value: string) { return new Date(`${value}T00:00:00`).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }) }
function timeLabel(value: string) { return new Date(value).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }
function showtimeState(item: { status: string; starts_at: string; ends_at: string }) {
  const now = Date.now(); const start = new Date(item.starts_at).getTime(); const end = new Date(item.ends_at).getTime()
  if (item.status === 'CANCELLED') return { label: 'Đã hủy', cls: 'text-rose-300 bg-rose-500/10 border-rose-500/20' }
  if (item.status === 'DRAFT') return { label: 'Bản nháp', cls: 'text-amber-300 bg-amber-500/10 border-amber-500/20' }
  if (start <= now && now < end) return { label: 'Đang chiếu', cls: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/20' }
  if (start > now) return { label: 'Sắp chiếu', cls: 'text-sky-300 bg-sky-500/10 border-sky-500/20' }
  return { label: 'Đã kết thúc', cls: 'text-gray-400 bg-white/5 border-white/10' }
}
function goTo(tab: string) { navigateTo({ path: '/branch-admin/dashboard', query: { tab } }) }
async function load() {
  loading.value = true; error.value = ''
  try { stats.value = await adminService.getBranchAdminStats(undefined, period.value); lastUpdated.value = new Date() }
  catch (cause: any) { error.value = cause?.message || 'Không thể tải tổng quan chi nhánh.' }
  finally { loading.value = false }
}
watch(period, load)
onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <header class="overview-header">
      <div><p class="text-xs font-black uppercase tracking-[.22em] text-red-400">CineAI Branch Operations</p><h2 class="mt-2 text-3xl font-black text-white">Tổng quan {{ stats?.branchName || 'chi nhánh' }}</h2><p class="mt-1 text-sm text-gray-400">Theo dõi bán vé và lịch vận hành trong {{ periodLabel }}.</p></div>
      <div class="flex flex-wrap items-center gap-3"><div class="period-tabs"><button v-for="item in [{ key: 'today', label: 'Hôm nay' }, { key: '7d', label: '7 ngày' }, { key: 'month', label: 'Tháng này' }]" :key="item.key" :class="{ active: period === item.key }" @click="period = item.key as typeof period">{{ item.label }}</button></div><button class="refresh-btn" :disabled="loading" @click="load"><span class="material-symbols-outlined text-lg">refresh</span>Làm mới</button></div>
    </header>

    <div v-if="error" class="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">{{ error }}</div>
    <div v-if="loading" class="panel flex min-h-64 items-center justify-center gap-3 text-gray-400"><span class="h-8 w-8 animate-spin rounded-full border-4 border-red-500 border-t-transparent" />Đang tổng hợp dữ liệu vận hành...</div>

    <template v-else-if="stats">
      <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article v-for="item in [
          { label: 'Doanh thu', value: money(stats.branchRevenue), note: periodLabel, icon: 'payments', tone: 'text-emerald-400' },
          { label: 'Đơn thành công', value: stats.orders, note: `${stats.ticketsSold} vé đã bán`, icon: 'receipt_long', tone: 'text-sky-400' },
          { label: 'Tỷ lệ lấp đầy', value: `${stats.occupancyRate}%`, note: `${stats.ticketsSold} ghế / sức chứa hợp lệ`, icon: 'event_seat', tone: 'text-amber-400' },
          { label: 'Cần xử lý', value: stats.attentionCount || 0, note: (stats.attentionCount || 0) ? 'Nên kiểm tra ngay' : 'Vận hành ổn định', icon: 'notification_important', tone: (stats.attentionCount || 0) ? 'text-rose-400' : 'text-emerald-400' },
        ]" :key="item.label" class="kpi-card"><span class="material-symbols-outlined kpi-watermark">{{ item.icon }}</span><p class="kpi-label">{{ item.label }}</p><strong class="mt-2 block text-3xl font-black" :class="item.tone">{{ item.value }}</strong><p class="mt-2 text-xs text-gray-500">{{ item.note }}</p></article>
      </section>

      <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <button class="operation-card" @click="goTo('showtimes')"><span class="operation-icon bg-violet-500/10 text-violet-300">calendar_month</span><span><b>{{ stats.todayShowtimes || 0 }}</b><small>Suất hôm nay</small></span></button>
        <button class="operation-card" @click="goTo('showtimes')"><span class="operation-icon bg-emerald-500/10 text-emerald-300">play_circle</span><span><b>{{ stats.showingNow || 0 }}</b><small>Đang chiếu</small></span></button>
        <button class="operation-card" @click="goTo('showtimes')"><span class="operation-icon bg-sky-500/10 text-sky-300">schedule</span><span><b>{{ stats.upcomingToday || 0 }}</b><small>Sắp chiếu hôm nay</small></span></button>
        <button class="operation-card" @click="goTo('payments')"><span class="operation-icon bg-amber-500/10 text-amber-300">account_balance_wallet</span><span><b>{{ (stats.pendingPayments || 0) + (stats.refundPending || 0) }}</b><small>Giao dịch cần kiểm tra</small></span></button>
      </section>

      <div class="grid gap-6 xl:grid-cols-[1.45fr_.75fr]">
        <section class="panel p-5"><div class="section-head"><div><h3>Doanh thu theo ngày</h3><p>Giao dịch thành công của các suất diễn ra trong kỳ.</p></div><span v-if="lastUpdated" class="text-[11px] text-gray-600">Cập nhật {{ lastUpdated.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }}</span></div><div class="mt-6 flex h-56 items-end gap-3"><div v-for="point in stats.salesChartData" :key="point.label" class="chart-column"><span>{{ money(point.revenue || 0) }}</span><div class="chart-bar" :style="{ height: `${Math.max(Number(point.revenue || 0) * 100 / maxChartValue, 3)}%` }" /><small>{{ shortDate(point.label) }}</small></div></div></section>
        <section class="panel p-5"><div class="section-head"><div><h3>Cần xử lý</h3><p>Cảnh báo tại riêng chi nhánh.</p></div></div><div v-if="alerts.length" class="mt-4 space-y-3"><button v-for="alert in alerts" :key="alert.title" class="alert-card" @click="goTo(alert.tab)"><span class="material-symbols-outlined" :class="alert.tone === 'rose' ? 'text-rose-400' : 'text-amber-400'">{{ alert.icon }}</span><span><b>{{ alert.title }}</b><small>{{ alert.text }}</small></span><span class="material-symbols-outlined ml-auto text-gray-600">chevron_right</span></button></div><div v-else class="flex min-h-40 flex-col items-center justify-center text-center"><span class="material-symbols-outlined text-5xl text-emerald-400">verified</span><b class="mt-3 text-white">Chi nhánh đang vận hành ổn định</b><p class="mt-1 text-xs text-gray-500">Không có cảnh báo cần xử lý trong kỳ.</p></div></section>
      </div>

      <section v-if="podiumMovies.length" class="panel podium-panel p-5 sm:p-7"><div class="relative text-center"><p class="text-xs font-black uppercase tracking-[.25em] text-amber-400">Branch Hall of Fame</p><h3 class="mt-2 text-2xl font-black text-white">Top phim tại {{ stats.branchName }}</h3><p class="mt-1 text-sm text-gray-500">Xếp hạng theo doanh thu trong {{ periodLabel }}</p></div><div class="relative mx-auto mt-8 grid max-w-4xl grid-cols-3 items-end gap-3 sm:gap-6"><article v-for="(movie, index) in podiumMovies" :key="movie!.movie_id" class="flex min-w-0 flex-col items-center" :class="index === 1 ? 'z-10' : ''"><div v-if="index === 1" class="mb-1 text-4xl">👑</div><div class="podium-poster" :class="index === 1 ? 'winner' : index === 0 ? 'silver' : 'bronze'"><img :src="movie!.poster_url || '/images/movie-placeholder.svg'" :alt="movie!.title"><div><b :title="movie!.title">{{ movie!.title }}</b><small>{{ movie!.tickets_sold }} vé · {{ money(movie!.revenue) }}</small></div></div><div class="podium-step" :class="index === 1 ? 'step-one' : index === 0 ? 'step-two' : 'step-three'"><span>{{ index === 1 ? '🥇' : index === 0 ? '🥈' : '🥉' }}</span><b>TOP {{ index === 1 ? 1 : index === 0 ? 2 : 3 }}</b></div></article></div></section>

      <section class="panel overflow-hidden"><div class="section-head p-5"><div><h3>Lịch vận hành hôm nay</h3><p>Theo dõi nhanh trạng thái các suất tại {{ stats.branchName }}.</p></div><button class="text-xs font-bold text-red-400" @click="goTo('showtimes')">Quản lý suất chiếu →</button></div><div v-if="upcomingShowtimes.length" class="divide-y divide-white/5"><div v-for="item in upcomingShowtimes" :key="item.id" class="schedule-row"><div class="schedule-time">{{ timeLabel(item.starts_at) }}</div><div class="min-w-0 flex-1"><b class="block truncate text-white">{{ item.movie_title }}</b><small class="text-gray-500">{{ item.auditorium_name }} · kết thúc {{ timeLabel(item.ends_at) }}</small></div><span class="rounded-full border px-2.5 py-1 text-[10px] font-black" :class="showtimeState(item).cls">{{ showtimeState(item).label }}</span></div></div><p v-else class="p-12 text-center text-sm text-gray-500">Hôm nay chưa có suất chiếu tại chi nhánh.</p></section>
    </template>
  </div>
</template>

<style scoped>
.panel{border:1px solid rgba(255,255,255,.08);border-radius:1rem;background:rgba(26,28,28,.76)}.overview-header{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;border:1px solid rgba(255,255,255,.08);border-radius:20px;background:linear-gradient(120deg,rgba(69,10,10,.35),rgba(25,27,28,.9) 48%,rgba(35,20,60,.25));padding:24px}.period-tabs{display:flex;border:1px solid rgba(255,255,255,.09);border-radius:12px;background:#111;padding:4px}.period-tabs button{border-radius:9px;padding:9px 12px;font-size:11px;font-weight:800;color:#777}.period-tabs button.active{background:#e50914;color:#fff}.refresh-btn{display:flex;align-items:center;gap:6px;border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:10px 13px;font-size:12px;font-weight:800;color:#ddd}.kpi-card{position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.08);border-radius:16px;background:#1a1c1c;padding:20px}.kpi-label{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:#777}.kpi-watermark{position:absolute;right:5px;bottom:-8px;font-size:76px;color:rgba(255,255,255,.035)}.operation-card{display:flex;align-items:center;gap:13px;border:1px solid rgba(255,255,255,.08);border-radius:15px;background:rgba(26,28,28,.7);padding:15px;text-align:left;transition:.2s}.operation-card:hover{border-color:rgba(229,9,20,.35);transform:translateY(-2px)}.operation-icon{display:flex;height:44px;width:44px;align-items:center;justify-content:center;border-radius:12px;font-family:'Material Symbols Outlined'}.operation-card b{display:block;font-size:22px;color:#fff}.operation-card small{display:block;font-size:11px;color:#777}.section-head{display:flex;align-items:center;justify-content:space-between;gap:14px;border-bottom:1px solid rgba(255,255,255,.06);padding-bottom:14px}.section-head h3{font-weight:800;color:white}.section-head p{margin-top:3px;font-size:11px;color:#666}.chart-column{display:flex;height:100%;min-width:38px;flex:1;flex-direction:column;align-items:center;justify-content:flex-end}.chart-column>span{margin-bottom:4px;font-size:9px;font-weight:700;color:#6ee7b7;opacity:0}.chart-column:hover>span{opacity:1}.chart-bar{width:56%;min-height:4px;border-radius:7px 7px 2px 2px;background:linear-gradient(to top,#dc2626,#fb923c);transition:.3s}.chart-column small{margin-top:7px;font-size:9px;color:#666}.alert-card{display:flex;width:100%;align-items:flex-start;gap:10px;border:1px solid rgba(255,255,255,.07);border-radius:12px;background:rgba(255,255,255,.025);padding:12px;text-align:left}.alert-card b,.alert-card small{display:block}.alert-card b{font-size:12px;color:#fff}.alert-card small{margin-top:3px;font-size:10px;color:#777}.podium-panel{position:relative;overflow:hidden;background:radial-gradient(circle at top,rgba(245,158,11,.12),transparent 55%),rgba(26,28,28,.76)}.podium-poster{position:relative;width:100%;max-width:180px;overflow:hidden;border:1px solid;border-radius:14px;background:#090909;box-shadow:0 22px 40px -25px #000}.podium-poster img{height:190px;width:100%;object-fit:cover}.podium-poster.winner img{height:235px}.podium-poster>div{position:absolute;inset:auto 0 0;background:linear-gradient(transparent,rgba(0,0,0,.95));padding:45px 10px 11px;text-align:center}.podium-poster b,.podium-poster small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.podium-poster b{font-size:12px;color:#fff}.podium-poster small{margin-top:4px;font-size:9px;color:#ccc}.winner{border-color:#fbbf24;box-shadow:0 20px 45px -25px #f59e0b}.silver{border-color:#94a3b8}.bronze{border-color:#c2410c}.podium-step{margin-top:10px;display:flex;width:100%;flex-direction:column;align-items:center;justify-content:center;border:1px solid;border-bottom:0;border-radius:12px 12px 0 0}.podium-step span{font-size:25px}.podium-step b{font-size:11px;color:#fff}.step-one{height:120px;border-color:rgba(251,191,36,.35);background:rgba(245,158,11,.18)}.step-two{height:84px;border-color:rgba(148,163,184,.3);background:rgba(148,163,184,.12)}.step-three{height:62px;border-color:rgba(194,65,12,.3);background:rgba(194,65,12,.12)}.schedule-row{display:flex;align-items:center;gap:16px;padding:14px 20px}.schedule-row:hover{background:rgba(255,255,255,.025)}.schedule-time{width:58px;font-size:17px;font-weight:900;color:#fb7185}@media(max-width:760px){.overview-header{align-items:flex-start;flex-direction:column}.podium-poster img,.podium-poster.winner img{height:135px}.period-tabs{overflow-x:auto}}
</style>

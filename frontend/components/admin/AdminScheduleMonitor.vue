<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { adminBackendService, branchesService, type AdminShowtime, type BackendBranch } from '~/services/api'

const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const route = useRoute()
const router = useRouter()
const branches = ref<BackendBranch[]>([])
const showtimes = ref<AdminShowtime[]>([])
const loading = ref(false)
const error = ref('')
const lastUpdated = ref<Date | null>(null)
const autoRefresh = ref(true)
const search = ref('')
const statusFilter = ref('ALL')
const warningOnly = ref(false)
const rangePreset = ref<'TODAY' | 'NEXT_7' | 'CUSTOM'>('TODAY')
const customDate = ref(new Date().toISOString().slice(0, 10))
const expandedMovies = ref<Record<string, boolean>>({})
let refreshTimer: ReturnType<typeof setInterval> | null = null

const selectedMovieId = computed(() => String(route.query.movie_id || ''))
const branchName = computed(() => selectedBranch.value === 'ALL'
  ? 'Toàn hệ thống'
  : branches.value.find(item => item.id === selectedBranch.value)?.name || 'Chi nhánh đã chọn')

function dayBounds(date: Date) {
  const start = new Date(date)
  start.setHours(0, 0, 0, 0)
  const end = new Date(start)
  end.setDate(end.getDate() + (rangePreset.value === 'NEXT_7' ? 7 : 1))
  return { start: start.toISOString(), end: end.toISOString() }
}

const rangeBounds = computed(() => {
  const base = rangePreset.value === 'CUSTOM'
    ? new Date(`${customDate.value}T00:00:00`)
    : new Date()
  return dayBounds(base)
})

function statusLabel(status: string) {
  return ({
    DRAFT: 'Bản nháp', OPEN: 'Đang mở bán', SALES_CLOSED: 'Đã đóng bán',
    IN_PROGRESS: 'Đang chiếu', FINISHED: 'Đã kết thúc', CANCELLED: 'Đã hủy',
  } as Record<string, string>)[status] || status
}

function statusClass(status: string) {
  if (status === 'OPEN') return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
  if (status === 'IN_PROGRESS') return 'bg-sky-500/15 text-sky-300 border-sky-500/30'
  if (status === 'SALES_CLOSED') return 'bg-amber-500/15 text-amber-300 border-amber-500/30'
  if (status === 'CANCELLED') return 'bg-rose-500/15 text-rose-300 border-rose-500/30'
  return 'bg-zinc-500/15 text-zinc-300 border-zinc-500/30'
}

function warnings(item: AdminShowtime) {
  const result: string[] = []
  const minutes = (new Date(item.starts_at).getTime() - Date.now()) / 60000
  if (!item.branch_is_active || !item.auditorium_is_active) result.push('Chi nhánh hoặc phòng đang tắt')
  if (item.status === 'CANCELLED' && item.sold_seats > 0) result.push('Suất đã hủy nhưng từng bán vé')
  if (item.status === 'OPEN' && minutes > 0 && minutes <= 60) result.push(`Bắt đầu trong ${Math.ceil(minutes)} phút`)
  if (item.status === 'OPEN' && minutes > 0 && item.sold_seats === 0) result.push('Chưa bán được ghế')
  if (item.occupancy_rate >= 80 && ['OPEN', 'SALES_CLOSED'].includes(item.status)) result.push('Sắp đầy ghế')
  return result
}

const filteredShowtimes = computed(() => showtimes.value.filter((item) => {
  if (selectedMovieId.value && item.movie_id !== selectedMovieId.value) return false
  if (statusFilter.value !== 'ALL' && item.status !== statusFilter.value) return false
  if (warningOnly.value && warnings(item).length === 0) return false
  const keyword = search.value.trim().toLocaleLowerCase('vi')
  return !keyword || [item.movie_title, item.auditorium_name, item.branch_name]
    .some(value => value.toLocaleLowerCase('vi').includes(keyword))
}))

const kpis = computed(() => ({
  total: filteredShowtimes.value.length,
  open: filteredShowtimes.value.filter(item => item.status === 'OPEN').length,
  inProgress: filteredShowtimes.value.filter(item => item.status === 'IN_PROGRESS').length,
  cancelled: filteredShowtimes.value.filter(item => item.status === 'CANCELLED').length,
  sold: filteredShowtimes.value.reduce((sum, item) => sum + Number(item.sold_seats || 0), 0),
  revenue: filteredShowtimes.value.reduce((sum, item) => sum + Number(item.revenue || 0), 0),
  warnings: filteredShowtimes.value.filter(item => warnings(item).length > 0).length,
}))

const groupedMovies = computed(() => {
  const groups = new Map<string, { id: string; title: string; showtimes: AdminShowtime[]; sold: number; revenue: number }>()
  for (const item of filteredShowtimes.value) {
    const group = groups.get(item.movie_id) || { id: item.movie_id, title: item.movie_title, showtimes: [], sold: 0, revenue: 0 }
    group.showtimes.push(item)
    group.sold += Number(item.sold_seats || 0)
    group.revenue += Number(item.revenue || 0)
    groups.set(item.movie_id, group)
  }
  return [...groups.values()].sort((a, b) => a.title.localeCompare(b.title, 'vi'))
})

function formatDate(value: string) {
  return new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
}

async function load(silent = false) {
  if (!silent) loading.value = true
  error.value = ''
  try {
    showtimes.value = await adminBackendService.getShowtimes(
      selectedBranch.value === 'ALL' ? undefined : selectedBranch.value,
      rangeBounds.value.start,
      rangeBounds.value.end,
    )
    lastUpdated.value = new Date()
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải lịch chiếu.'
  } finally {
    loading.value = false
  }
}

function restartPolling() {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = autoRefresh.value ? setInterval(() => load(true), 30_000) : null
}

function toggleMovie(movieId: string) { expandedMovies.value[movieId] = !expandedMovies.value[movieId] }
function clearMovieFilter() {
  const query = { ...route.query }
  delete query.movie_id
  router.replace({ query })
}
function openBookings(item: AdminShowtime) {
  router.push({ query: { tab: 'bookings', movie_id: item.movie_id } })
}

onMounted(async () => {
  branches.value = await branchesService.getAll()
  await load()
  if (selectedMovieId.value) expandedMovies.value[selectedMovieId.value] = true
  restartPolling()
})
onBeforeUnmount(() => { if (refreshTimer) clearInterval(refreshTimer) })
watch(selectedBranch, () => load())
watch([rangePreset, customDate], () => load())
watch(autoRefresh, restartPolling)
watch(selectedMovieId, movieId => { if (movieId) expandedMovies.value[movieId] = true })
</script>

<template>
  <div class="space-y-5">
    <section class="panel p-5 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
      <div>
        <div class="flex items-center gap-2"><span class="material-symbols-outlined text-red-400">monitoring</span><h2 class="text-2xl font-black">Giám sát lịch chiếu</h2></div>
        <p class="mt-1 text-sm text-gray-400">{{ branchName }} · tự cập nhật mỗi 30 giây</p>
        <p class="mt-1 text-xs text-gray-500">Cập nhật lần cuối: {{ lastUpdated ? lastUpdated.toLocaleTimeString('vi-VN') : 'Chưa cập nhật' }}</p>
        <button v-if="selectedMovieId" class="mt-2 text-xs font-bold text-red-300 hover:underline" @click="clearMovieFilter">Bỏ lọc phim</button>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <select v-model="rangePreset" class="field-input"><option value="TODAY">Hôm nay</option><option value="NEXT_7">7 ngày tới</option><option value="CUSTOM">Chọn ngày</option></select>
        <input v-if="rangePreset === 'CUSTOM'" v-model="customDate" type="date" class="field-input" />
        <label class="flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-sm"><input v-model="autoRefresh" type="checkbox" /> Tự làm mới</label>
        <button class="action-primary" :disabled="loading" @click="load()"><span class="material-symbols-outlined text-base">refresh</span> Làm mới</button>
      </div>
    </section>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300">{{ error }}</p>

    <section class="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-7">
      <div class="metric"><span>Tổng suất</span><strong>{{ kpis.total }}</strong></div>
      <div class="metric"><span>Mở bán</span><strong class="text-emerald-300">{{ kpis.open }}</strong></div>
      <div class="metric"><span>Đang chiếu</span><strong class="text-sky-300">{{ kpis.inProgress }}</strong></div>
      <div class="metric"><span>Đã hủy</span><strong class="text-rose-300">{{ kpis.cancelled }}</strong></div>
      <div class="metric"><span>Ghế đã bán</span><strong>{{ kpis.sold }}</strong></div>
      <div class="metric"><span>Cảnh báo</span><strong class="text-amber-300">{{ kpis.warnings }}</strong></div>
      <div class="metric"><span>Doanh thu</span><strong class="text-emerald-300 text-base">{{ kpis.revenue.toLocaleString('vi-VN') }}đ</strong></div>
    </section>

    <section class="panel p-4 grid grid-cols-1 gap-3 md:grid-cols-4">
      <input v-model="search" class="field-input md:col-span-2" placeholder="Tìm phim, phòng hoặc chi nhánh..." />
      <select v-model="statusFilter" class="field-input">
        <option value="ALL">Tất cả trạng thái</option><option value="DRAFT">Bản nháp</option><option value="OPEN">Đang mở bán</option><option value="SALES_CLOSED">Đã đóng bán</option><option value="IN_PROGRESS">Đang chiếu</option><option value="FINISHED">Đã kết thúc</option><option value="CANCELLED">Đã hủy</option>
      </select>
      <label class="flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-sm"><input v-model="warningOnly" type="checkbox" /> Chỉ xem cảnh báo</label>
    </section>

    <div v-if="loading" class="panel p-16 text-center text-gray-400">Đang đồng bộ dữ liệu lịch chiếu...</div>
    <section v-else class="space-y-4">
      <article v-for="movie in groupedMovies" :key="movie.id" class="panel overflow-hidden">
        <button class="w-full p-5 flex flex-wrap items-center justify-between gap-4 text-left" @click="toggleMovie(movie.id)">
          <div class="flex items-center gap-3"><span class="material-symbols-outlined text-gray-400">{{ expandedMovies[movie.id] ? 'expand_less' : 'expand_more' }}</span><div><h3 class="font-black text-lg">{{ movie.title }}</h3><p class="text-xs text-gray-400">{{ movie.showtimes.length }} suất · {{ movie.sold }} ghế đã bán</p></div></div>
          <div class="text-right"><span class="text-xs uppercase text-gray-500">Doanh thu trong phạm vi</span><strong class="block text-emerald-300">{{ movie.revenue.toLocaleString('vi-VN') }}đ</strong></div>
        </button>
        <div v-if="expandedMovies[movie.id]" class="overflow-x-auto border-t border-white/10">
          <table class="w-full min-w-[1100px] text-sm">
            <thead><tr class="bg-white/5 text-left text-xs uppercase text-gray-400"><th class="p-3">Chi nhánh / Phòng</th><th class="p-3">Bắt đầu</th><th class="p-3">Trạng thái</th><th class="p-3">Lấp đầy</th><th class="p-3">Doanh thu</th><th class="p-3">Cảnh báo</th><th class="p-3">Xử lý</th></tr></thead>
            <tbody><tr v-for="item in movie.showtimes" :key="item.id" class="border-t border-white/5 hover:bg-white/[0.03]">
              <td class="p-3"><strong>{{ item.branch_name }}</strong><span class="block text-xs text-gray-400">{{ item.auditorium_name }}</span></td>
              <td class="p-3 font-mono">{{ formatDate(item.starts_at) }}</td>
              <td class="p-3"><span class="rounded-full border px-2.5 py-1 text-xs font-bold" :class="statusClass(item.status)">{{ statusLabel(item.status) }}</span></td>
              <td class="p-3"><strong>{{ item.sold_seats }}/{{ item.total_seats }}</strong><div class="mt-1 h-1.5 w-24 rounded bg-white/10"><div class="h-full rounded bg-red-400" :style="{ width: `${Math.min(100, item.occupancy_rate)}%` }"></div></div><span class="text-xs text-gray-500">{{ item.occupancy_rate }}%</span></td>
              <td class="p-3 font-semibold text-emerald-300">{{ Number(item.revenue).toLocaleString('vi-VN') }}đ</td>
              <td class="p-3"><div class="flex max-w-[260px] flex-wrap gap-1"><span v-for="warning in warnings(item)" :key="warning" class="rounded bg-amber-500/15 px-2 py-1 text-xs text-amber-200">{{ warning }}</span><span v-if="!warnings(item).length" class="text-xs text-gray-600">Không có</span></div></td>
              <td class="p-3"><button class="link-button" @click="openBookings(item)">Xem đơn vé</button></td>
            </tr></tbody>
          </table>
        </div>
      </article>
      <div v-if="!groupedMovies.length" class="panel p-16 text-center text-gray-400">Không có suất chiếu phù hợp trong phạm vi đã chọn.</div>
    </section>
  </div>
</template>

<style scoped>
.panel { background: rgba(26, 28, 28, .86); border: 1px solid rgba(255, 255, 255, .08); border-radius: 1rem; }
.metric { min-height: 94px; padding: 1rem; background: rgba(26, 28, 28, .86); border: 1px solid rgba(255, 255, 255, .08); border-radius: 1rem; }
.metric span { display: block; color: #9ca3af; font-size: .7rem; font-weight: 700; text-transform: uppercase; }
.metric strong { display: block; margin-top: .5rem; font-size: 1.4rem; }
.field-input { min-height: 42px; border-radius: .75rem; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.04); padding: .6rem .8rem; color: white; }
.action-primary { display: inline-flex; align-items: center; gap: .4rem; border-radius: .75rem; background: #e50914; padding: .65rem 1rem; font-weight: 800; }
.link-button { border-radius: .5rem; background: rgba(56,189,248,.1); padding: .4rem .65rem; color: #7dd3fc; font-size: .75rem; font-weight: 700; }
</style>

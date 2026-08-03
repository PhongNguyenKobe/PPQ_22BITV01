<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { adminBackendService } from '~/services/api'

const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const today = new Date()
const endDate = ref(today.toISOString().slice(0, 10))
const startDate = ref(new Date(today.getTime() - 29 * 86400000).toISOString().slice(0, 10))
const revenue = ref<any>({ total: 0, data: [] })
const occupancy = ref<any[]>([])
const movies = ref<any[]>([])
const error = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const branchId = selectedBranch.value === 'ALL' ? undefined : selectedBranch.value
    const [r, o, m] = await Promise.all([
      adminBackendService.getRevenueReport(startDate.value, endDate.value, 'day', branchId),
      adminBackendService.getOccupancyReport(startDate.value, endDate.value, branchId),
      adminBackendService.getTopMoviesReport(startDate.value, endDate.value, branchId),
    ])
    revenue.value = r
    occupancy.value = o.data
    movies.value = m
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải báo cáo.'
  } finally {
    loading.value = false
  }
}

function exportCsv() {
  const lines = [
    ['Loại', 'Tên', 'Vé/Đã bán', 'Doanh thu/Tỷ lệ'],
    ...movies.value.map(x => ['Phim', x.title, x.tickets_sold, x.revenue]),
    ...occupancy.value.map(x => ['Chi nhánh', x.branch_name, x.sold, `${x.occupancy_rate}%`])
  ]
  const blob = new Blob(
    ['\ufeff' + lines.map(row => row.map(String).map(v => `"${v.replaceAll('"', '""')}"`).join(',')).join('\n')],
    { type: 'text/csv;charset=utf-8' }
  )
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `cineai-report-${startDate.value}-${endDate.value}.csv`
  a.click()
  URL.revokeObjectURL(a.href)
}

// Calculate max revenue among top movies for relative graph bar scale
const maxMovieRevenue = computed(() => {
  if (!movies.value.length) return 1
  return Math.max(...movies.value.map(m => Number(m.revenue) || 0), 1)
})

const totalTicketsSold = computed(() => Number(movies.value[0]?.total_tickets_sold || 0))
const totalMovies = computed(() => Number(movies.value[0]?.total_movies || 0))
const topThreeMovies = computed(() => movies.value.slice(0, 3))
const rankStyles: Record<number, string> = {
  1: 'border-amber-400/40 bg-amber-400/10 text-amber-300',
  2: 'border-slate-300/30 bg-slate-300/10 text-slate-200',
  3: 'border-orange-500/30 bg-orange-500/10 text-orange-300',
}
const rankClass = (rank: number) => rankStyles[rank] || 'border-white/10 bg-white/5 text-gray-300'

onMounted(load)
watch(selectedBranch, load)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-red-500 text-2xl">analytics</span>
          <h2 class="text-xl font-black text-white tracking-tight">Báo cáo vận hành</h2>
        </div>
        <p class="text-sm text-gray-400 mt-1">Phân tích doanh thu, sản lượng phim và tỷ lệ lấp đầy phòng chiếu.</p>
      </div>
      <button class="action-btn-secondary px-5 py-2.5 bg-white/5 hover:bg-white/10 text-white font-bold text-xs rounded-xl transition-all border border-white/10 flex items-center gap-1.5 self-start sm:self-auto shadow-md" @click="exportCsv">
        <span class="material-symbols-outlined text-sm">download</span>
        Xuất file CSV
      </button>
    </div>

    <!-- Filters Control -->
    <div class="panel-glass grid gap-4 p-5 md:grid-cols-3 items-end shadow-md">
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Từ ngày</label>
        <input v-model="startDate" type="date" class="field-input w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-red-500">
      </div>
      
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Đến ngày</label>
        <input v-model="endDate" type="date" class="field-input w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-red-500">
      </div>

      <button class="action-btn-primary w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold text-sm rounded-xl transition-all shadow-md flex items-center justify-center gap-2" @click="load" :disabled="loading">
        <span class="material-symbols-outlined text-sm">dashboard</span>
        Áp dụng lọc
      </button>
    </div>

    <!-- Error/Loading -->
    <div v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-400 flex items-center gap-2">
      <span class="material-symbols-outlined text-xl">error</span>
      <span class="font-medium">{{ error }}</span>
    </div>

    <div v-if="loading" class="panel-glass p-16 text-center text-gray-400 flex flex-col items-center justify-center gap-3">
      <div class="w-10 h-10 border-4 border-red-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="font-medium animate-pulse">Đang kết xuất báo cáo...</p>
    </div>

    <template v-else>
      <!-- KPI Stats Grid -->
      <div class="grid gap-6 sm:grid-cols-3">
        <div class="panel-glass p-6 relative overflow-hidden shadow-lg">
          <div class="absolute right-0 bottom-0 translate-x-2 translate-y-2 opacity-5 pointer-events-none">
            <span class="material-symbols-outlined text-7xl">payments</span>
          </div>
          <p class="text-xs font-bold text-gray-400 uppercase tracking-wider">Tổng doanh thu</p>
          <div class="text-2xl text-emerald-400 mt-2 font-mono font-black tracking-tight drop-shadow-[0_0_15px_rgba(16,185,129,0.2)]">
            {{ Number(revenue.total).toLocaleString('vi-VN') }}đ
          </div>
        </div>
        
        <div class="panel-glass p-6 relative overflow-hidden shadow-lg">
          <div class="absolute right-0 bottom-0 translate-x-2 translate-y-2 opacity-5 pointer-events-none">
            <span class="material-symbols-outlined text-7xl">movie</span>
          </div>
          <p class="text-xs font-bold text-gray-400 uppercase tracking-wider">Phim phát sinh doanh thu</p>
          <div class="text-2xl text-white mt-2 font-mono font-black tracking-tight">
            {{ totalMovies }} phim
          </div>
        </div>
        
        <div class="panel-glass p-6 relative overflow-hidden shadow-lg">
          <div class="absolute right-0 bottom-0 translate-x-2 translate-y-2 opacity-5 pointer-events-none">
            <span class="material-symbols-outlined text-7xl">storefront</span>
          </div>
          <p class="text-xs font-bold text-gray-400 uppercase tracking-wider">Tổng số vé bán ra</p>
          <div class="text-2xl text-sky-400 mt-2 font-mono font-black tracking-tight">
            {{ totalTicketsSold.toLocaleString('vi-VN') }} vé
          </div>
        </div>
      </div>

      <!-- Graph and Detailed Reports -->
      <div class="grid gap-6 lg:grid-cols-2">
        <!-- Top Movies card -->
        <div class="panel-glass p-6 flex flex-col shadow-lg">
          <div class="flex items-center gap-2 mb-5 pb-3 border-b border-white/5">
            <span class="material-symbols-outlined text-red-500">hotel_class</span>
            <h3 class="font-bold text-white text-base">Top 1–3 phim theo doanh thu</h3>
          </div>
          <div v-if="topThreeMovies.length" class="grid gap-3 mb-5 sm:grid-cols-3">
            <div
              v-for="m in topThreeMovies"
              :key="`rank-${m.movie_id}`"
              class="rounded-xl border p-3"
              :class="rankClass(m.rank)"
            >
              <div class="text-xs font-black uppercase">Top {{ m.rank }}</div>
              <div class="mt-1 truncate text-sm font-bold text-white" :title="m.title">{{ m.title }}</div>
              <div class="mt-2 font-mono text-xs">{{ m.tickets_sold }} vé</div>
              <div class="font-mono text-xs font-black">{{ Number(m.revenue).toLocaleString('vi-VN') }}đ</div>
            </div>
          </div>
          <div class="space-y-5 flex-1 max-h-[400px] overflow-y-auto pr-2">
            <div v-for="m in movies" :key="m.movie_id" class="space-y-1.5">
              <div class="flex justify-between items-center text-sm">
                <span class="text-white font-bold"><span class="text-red-400 mr-2">#{{ m.rank }}</span>{{ m.title }}</span>
                <span class="text-gray-400 text-xs font-semibold font-mono">{{ m.tickets_sold }} vé</span>
              </div>
              <div class="flex items-center gap-3">
                <!-- Relative Graph Bar -->
                <div class="flex-1 h-3 rounded-full bg-white/5 overflow-hidden">
                  <div class="h-3 rounded-full bg-gradient-to-r from-red-600 to-orange-500 shadow-[0_0_10px_rgba(239,68,68,0.3)] transition-all duration-500"
                    :style="{ width: `${(Number(m.revenue) / maxMovieRevenue) * 100}%` }">
                  </div>
                </div>
                <strong class="font-mono text-emerald-400 text-sm whitespace-nowrap min-w-[100px] text-right">{{ Number(m.revenue).toLocaleString('vi-VN') }}đ</strong>
              </div>
            </div>
            
            <div v-if="!movies.length" class="text-center py-10 text-gray-500 text-sm">
              Không có dữ liệu phim phát sinh.
            </div>
          </div>
        </div>

        <!-- Occupancy rate card -->
        <div class="panel-glass p-6 flex flex-col shadow-lg">
          <div class="flex items-center gap-2 mb-5 pb-3 border-b border-white/5">
            <span class="material-symbols-outlined text-sky-400">percent</span>
            <h3 class="font-bold text-white text-base">Tỷ lệ lấp đầy theo chi nhánh</h3>
          </div>
          <div class="space-y-5 flex-1 max-h-[400px] overflow-y-auto pr-2">
            <div v-for="b in occupancy" :key="b.branch_id" class="space-y-2">
              <div class="flex justify-between items-center text-sm">
                <div class="flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-xs text-gray-400">location_on</span>
                  <span class="text-white font-semibold">{{ b.branch_name }}</span>
                </div>
                <div class="flex items-center gap-2 text-xs font-semibold text-gray-400">
                  <span>{{ b.sold }} ghế bán</span>
                  <span class="w-1 h-1 rounded-full bg-white/10"></span>
                  <strong :class="{
                    'text-emerald-400 font-bold': b.occupancy_rate >= 70,
                    'text-sky-400': b.occupancy_rate >= 30 && b.occupancy_rate < 70,
                    'text-rose-400': b.occupancy_rate < 30
                  }">{{ b.occupancy_rate }}%</strong>
                </div>
              </div>
              <!-- Progress Bar -->
              <div class="h-3.5 rounded-full bg-white/5 overflow-hidden p-[2px]">
                <div class="h-full rounded-full transition-all duration-500"
                  :class="{
                    'bg-gradient-to-r from-emerald-600 to-green-400 shadow-[0_0_8px_rgba(16,185,129,0.3)]': b.occupancy_rate >= 70,
                    'bg-gradient-to-r from-sky-600 to-blue-400 shadow-[0_0_8px_rgba(14,165,233,0.3)]': b.occupancy_rate >= 30 && b.occupancy_rate < 70,
                    'bg-gradient-to-r from-rose-600 to-orange-400 shadow-[0_0_8px_rgba(244,63,94,0.3)]': b.occupancy_rate < 30
                  }"
                  :style="{ width: `${Math.min(b.occupancy_rate, 100)}%` }">
                </div>
              </div>
            </div>
            
            <div v-if="!occupancy.length" class="text-center py-10 text-gray-500 text-sm">
              Không có dữ liệu lấp đầy phòng chiếu.
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.panel-glass {
  background: rgba(26, 28, 28, 0.6);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
}
.field-input {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease-in-out;
}
.field-input:focus {
  border-color: #ef4444;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}
.action-btn-primary:hover:not(:disabled),
.action-btn-secondary:hover:not(:disabled) {
  transform: translateY(-1px);
}
.action-btn-primary:active:not(:disabled),
.action-btn-secondary:active:not(:disabled) {
  transform: translateY(0);
}
</style>

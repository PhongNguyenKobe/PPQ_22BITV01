<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  adminBackendService,
  branchesService,
  type AdminShowtime,
  type BackendBranch,
} from '~/services/api'

const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const branches = ref<BackendBranch[]>([])
const showtimes = ref<AdminShowtime[]>([])
const loading = ref(false)
const error = ref('')

const expandedMovies = ref<Record<string, boolean>>({})

function toggleMovie(movieId: string) {
  expandedMovies.value[movieId] = !expandedMovies.value[movieId]
}

const branchName = computed(() =>
  selectedBranch.value === 'ALL'
    ? 'toàn hệ thống'
    : branches.value.find(item => item.id === selectedBranch.value)?.name || 'chi nhánh đã chọn',
)

const groupedMovies = computed(() => {
  const groups = new Map<string, {
    id: string
    title: string
    showtimes: AdminShowtime[]
    sold: number
    revenue: number
  }>()
  for (const item of showtimes.value) {
    const current = groups.get(item.movie_id) || {
      id: item.movie_id,
      title: item.movie_title,
      showtimes: [],
      sold: 0,
      revenue: 0,
    }
    current.showtimes.push(item)
    current.sold += Number(item.sold_seats || 0)
    current.revenue += Number(item.revenue || 0)
    groups.set(item.movie_id, current)
  }
  return [...groups.values()].sort((a, b) => a.title.localeCompare(b.title, 'vi'))
})

function formatDate(value: string) {
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    showtimes.value = await adminBackendService.getShowtimes(
      selectedBranch.value === 'ALL' ? undefined : selectedBranch.value,
    )
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải lịch chiếu.'
    showtimes.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    branches.value = await branchesService.getAll()
    if (selectedBranch.value !== 'ALL' && !branches.value.some(item => item.id === selectedBranch.value)) {
      selectedBranch.value = 'ALL'
    }
  } finally {
    await load()
  }
})

watch(selectedBranch, load)
</script>

<template>
  <div class="space-y-6">
    <!-- Header Controls -->
    <div class="panel-glass flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-red-500/10 to-transparent pointer-events-none"></div>
      <div class="relative z-10">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-red-500">calendar_view_week</span>
          <h2 class="text-xl font-black text-white tracking-tight">Giám sát lịch chiếu</h2>
        </div>
        <p class="text-sm text-gray-400 mt-1">
          Chế độ giám sát thời gian thực hệ thống suất chiếu · <span class="text-red-400 font-semibold">{{ branchName }}</span>
        </p>
      </div>
      <div class="relative min-w-[280px]">
        <select v-model="selectedBranch" class="field-input w-full pl-4 pr-10 py-3 bg-white/5 border border-white/10 rounded-xl text-sm font-semibold text-white focus:outline-none focus:border-red-500 hover:bg-white/10 transition-all cursor-pointer appearance-none">
          <option value="ALL">Tất cả chi nhánh</option>
          <option v-for="branch in branches" :key="branch.id" :value="branch.id">
            {{ branch.name }} ({{ branch.city }})
          </option>
        </select>
        <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none text-sm">expand_more</span>
      </div>
    </div>

    <!-- Error/Loading -->
    <div v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-400 flex items-center gap-2">
      <span class="material-symbols-outlined text-xl">error</span>
      <span class="font-medium">{{ error }}</span>
    </div>
    
    <div v-if="loading" class="panel-glass p-16 text-center text-gray-400 flex flex-col items-center justify-center gap-3">
      <div class="w-10 h-10 border-4 border-red-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="font-medium animate-pulse">Đang đồng bộ dữ liệu lịch chiếu...</p>
    </div>

    <!-- Movies Grid -->
    <div v-else class="grid gap-6">
      <article v-for="movie in groupedMovies" :key="movie.id" class="panel-glass p-6 hover:border-white/15 transition-all duration-300 group shadow-lg">
        <div @click="toggleMovie(movie.id)" class="flex flex-wrap items-center justify-between gap-4 cursor-pointer select-none pb-4 border-b border-white/5 last:border-b-0 last:pb-0">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-gray-400 group-hover:text-red-400 transition-colors">
              {{ expandedMovies[movie.id] ? 'expand_less' : 'expand_more' }}
            </span>
            <div>
              <h3 class="text-lg font-black text-white group-hover:text-red-400 transition-colors">{{ movie.title }}</h3>
              <div class="flex items-center gap-3 mt-1.5">
                <span class="inline-flex items-center gap-1 text-xs text-gray-400">
                  <span class="material-symbols-outlined text-sm">confirmation_number</span>
                  {{ movie.showtimes.length }} suất chiếu
                </span>
                <span class="w-1.5 h-1.5 rounded-full bg-white/10"></span>
                <span class="inline-flex items-center gap-1 text-xs text-gray-400">
                  <span class="material-symbols-outlined text-sm">event_seat</span>
                  {{ movie.sold }} ghế đã bán
                </span>
              </div>
            </div>
          </div>
          <div class="flex flex-col items-end">
            <span class="text-xs text-gray-400 font-semibold uppercase tracking-wider">Doanh thu suất</span>
            <strong class="text-xl text-emerald-400 mt-1 font-mono">{{ movie.revenue.toLocaleString('vi-VN') }}đ</strong>
          </div>
        </div>
        
        <div v-if="expandedMovies[movie.id]" class="mt-5 overflow-x-auto rounded-xl border border-white/5 bg-black/20">
          <table class="w-full min-w-[760px] text-left text-sm border-collapse">
            <thead>
              <tr class="border-b border-white/10 bg-white/5 text-gray-300 font-bold">
                <th class="py-3 px-4 text-xs uppercase tracking-wider">Chi nhánh</th>
                <th class="py-3 px-4 text-xs uppercase tracking-wider">Phòng chiếu</th>
                <th class="py-3 px-4 text-xs uppercase tracking-wider">Thời gian bắt đầu</th>
                <th class="py-3 px-4 text-xs uppercase tracking-wider">Trạng thái</th>
                <th class="py-3 px-4 text-xs uppercase tracking-wider">Giá vé cơ bản</th>
                <th class="py-3 px-4 text-xs uppercase tracking-wider">Đã bán</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in movie.showtimes" :key="item.id" class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="py-3.5 px-4 font-semibold text-white">{{ item.branch_name }}</td>
                <td class="py-3.5 px-4 text-gray-300">{{ item.auditorium_name }}</td>
                <td class="py-3.5 px-4 text-gray-300 font-mono">{{ formatDate(item.starts_at) }}</td>
                <td class="py-3.5 px-4">
                  <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase border"
                    :class="{
                      'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-[0_0_8px_rgba(16,185,129,0.1)]': item.status === 'OPEN',
                      'bg-rose-500/10 text-rose-400 border-rose-500/20': item.status === 'CLOSED',
                      'bg-zinc-500/10 text-zinc-400 border-zinc-500/20': item.status === 'FINISHED' || item.status === 'COMPLETED'
                    }">
                    {{ item.status }}
                  </span>
                </td>
                <td class="py-3.5 px-4 font-mono text-gray-300">{{ Number(item.base_price).toLocaleString('vi-VN') }}đ</td>
                <td class="py-3.5 px-4 font-semibold text-white font-mono">
                  <div class="flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-xs text-gray-500">group</span>
                    {{ item.sold_seats }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
      
      <div v-if="!groupedMovies.length" class="panel-glass p-16 text-center text-gray-400 flex flex-col items-center justify-center gap-2">
        <span class="material-symbols-outlined text-4xl text-gray-600">calendar_today</span>
        <p class="font-bold text-base">Chi nhánh này chưa có suất chiếu</p>
        <p class="text-xs text-gray-500">Vui lòng kiểm tra lại cấu hình lịch hoặc thêm suất chiếu mới.</p>
      </div>
    </div>
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
</style>

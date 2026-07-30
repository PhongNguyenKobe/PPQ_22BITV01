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
  <div class="space-y-5">
    <div class="panel flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between">
      <div>
        <h2 class="text-xl font-black">Giám sát lịch chiếu</h2>
        <p class="text-sm text-on-surface-variant">
          Chế độ chỉ đọc dành cho Super Admin · {{ branchName }}.
        </p>
      </div>
      <select v-model="selectedBranch" class="field-input min-w-64">
        <option value="ALL">Tất cả chi nhánh</option>
        <option v-for="branch in branches" :key="branch.id" :value="branch.id">
          {{ branch.name }} ({{ branch.city }})
        </option>
      </select>
    </div>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-400">{{ error }}</p>
    <p v-if="loading" class="panel p-10 text-center text-on-surface-variant">Đang tải lịch chiếu...</p>

    <div v-else class="grid gap-4">
      <article v-for="movie in groupedMovies" :key="movie.id" class="panel p-5">
        <div class="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 class="text-lg font-black">{{ movie.title }}</h3>
            <p class="text-xs text-on-surface-variant">{{ movie.showtimes.length }} suất · {{ movie.sold }} ghế đã bán</p>
          </div>
          <strong class="text-emerald-400">{{ movie.revenue.toLocaleString('vi-VN') }}đ</strong>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[760px] text-left text-sm">
            <thead class="border-b border-white/10 text-on-surface-variant">
              <tr><th class="py-3">Chi nhánh</th><th>Phòng</th><th>Bắt đầu</th><th>Trạng thái</th><th>Giá vé</th><th>Đã bán</th></tr>
            </thead>
            <tbody>
              <tr v-for="item in movie.showtimes" :key="item.id" class="border-b border-white/5">
                <td class="py-3 font-bold">{{ item.branch_name }}</td>
                <td>{{ item.auditorium_name }}</td>
                <td>{{ formatDate(item.starts_at) }}</td>
                <td>{{ item.status }}</td>
                <td>{{ Number(item.base_price).toLocaleString('vi-VN') }}đ</td>
                <td>{{ item.sold_seats }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
      <p v-if="!groupedMovies.length" class="panel p-10 text-center text-on-surface-variant">
        Chi nhánh này chưa có suất chiếu.
      </p>
    </div>
  </div>
</template>

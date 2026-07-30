<script setup lang="ts">
import { adminBackendService } from '~/services/api'
const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const today = new Date()
const endDate = ref(today.toISOString().slice(0, 10))
const startDate = ref(new Date(today.getTime() - 29 * 86400000).toISOString().slice(0, 10))
const revenue = ref<any>({ total: 0, data: [] })
const occupancy = ref<any[]>([])
const movies = ref<any[]>([])
const error = ref('')
async function load() {
  try {
    const branchId = selectedBranch.value === 'ALL' ? undefined : selectedBranch.value
    const [r, o, m] = await Promise.all([
      adminBackendService.getRevenueReport(startDate.value, endDate.value, 'day', branchId),
      adminBackendService.getOccupancyReport(startDate.value, endDate.value, branchId),
      adminBackendService.getTopMoviesReport(startDate.value, endDate.value, branchId),
    ])
    revenue.value = r; occupancy.value = o.data; movies.value = m
  } catch (e: any) { error.value = e?.message || 'Không thể tải báo cáo.' }
}
function exportCsv() {
  const lines = [['Loại','Tên','Vé/Đã bán','Doanh thu/Tỷ lệ'], ...movies.value.map(x => ['Phim', x.title, x.tickets_sold, x.revenue]), ...occupancy.value.map(x => ['Chi nhánh', x.branch_name, x.sold, `${x.occupancy_rate}%`])]
  const blob = new Blob(['\ufeff' + lines.map(row => row.map(String).map(v => `"${v.replaceAll('"','""')}"`).join(',')).join('\n')], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `cineai-report-${startDate.value}-${endDate.value}.csv`; a.click(); URL.revokeObjectURL(a.href)
}
onMounted(load)
watch(selectedBranch, load)
</script>
<template>
  <div class="space-y-5">
    <div class="flex justify-between"><div><h2 class="text-xl font-black">Báo cáo vận hành</h2><p class="text-sm text-on-surface-variant">Doanh thu, phim và tỷ lệ lấp đầy.</p></div><button class="action-ghost" @click="exportCsv">Xuất CSV</button></div>
    <div class="panel grid gap-3 p-4 md:grid-cols-3"><input v-model="startDate" type="date" class="field-input"><input v-model="endDate" type="date" class="field-input"><button class="action-primary" @click="load">Áp dụng</button></div>
    <p v-if="error" class="text-rose-400">{{ error }}</p>
    <div class="grid gap-4 md:grid-cols-3"><div class="panel p-5"><p class="text-sm text-on-surface-variant">Tổng doanh thu</p><b class="text-2xl text-emerald-400">{{ Number(revenue.total).toLocaleString('vi-VN') }}đ</b></div><div class="panel p-5"><p class="text-sm text-on-surface-variant">Phim có doanh thu</p><b class="text-2xl">{{ movies.length }}</b></div><div class="panel p-5"><p class="text-sm text-on-surface-variant">Chi nhánh hoạt động</p><b class="text-2xl">{{ occupancy.length }}</b></div></div>
    <div class="grid gap-4 lg:grid-cols-2"><div class="panel p-5"><h3 class="mb-4 font-bold">Top phim</h3><div v-for="m in movies" :key="m.movie_id" class="flex justify-between border-b border-white/5 py-3"><span>{{ m.title }} · {{ m.tickets_sold }} vé</span><b>{{ Number(m.revenue).toLocaleString('vi-VN') }}đ</b></div></div><div class="panel p-5"><h3 class="mb-4 font-bold">Lấp đầy theo chi nhánh</h3><div v-for="b in occupancy" :key="b.branch_id" class="py-3"><div class="flex justify-between"><span>{{ b.branch_name }}</span><b>{{ b.occupancy_rate }}%</b></div><div class="mt-2 h-2 rounded bg-white/10"><div class="h-2 rounded bg-sky-500" :style="{ width: `${Math.min(b.occupancy_rate, 100)}%` }"></div></div></div></div></div>
  </div>
</template>

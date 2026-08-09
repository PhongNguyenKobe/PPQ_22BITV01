<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { adminService, type SuperAdminStats } from '~/services/api'

const superStats = ref<SuperAdminStats | null>(null)
const loading = ref(true)
const error = ref('')
const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    superStats.value = await adminService.getSuperAdminStats(
      selectedBranch.value !== 'ALL' ? selectedBranch.value : undefined
    )
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải dữ liệu tổng quan.'
  } finally {
    loading.value = false
  }
}

function fmtCurrency(value: number) {
  return Number(value).toLocaleString('vi-VN') + 'đ'
}

onMounted(() => {
  loadData()
})

watch(selectedBranch, () => loadData())

const updatedAt = computed(() => {
  if (!superStats.value?.generatedAt) return ''
  return new Intl.DateTimeFormat('vi-VN', {
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    day: '2-digit', month: '2-digit', year: 'numeric',
    timeZone: 'Asia/Ho_Chi_Minh'
  }).format(new Date(superStats.value.generatedAt))
})

const monthPeriod = computed(() => {
  const now = new Date()
  return `01/${String(now.getMonth() + 1).padStart(2, '0')} – ${String(now.getDate()).padStart(2, '0')}/${String(now.getMonth() + 1).padStart(2, '0')}`
})

const maxChartValue = () => {
  if (!superStats.value?.revenueChartData?.length) return 1
  return Math.max(...superStats.value.revenueChartData.map(item => item.value), 1)
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 panel bg-black/40 border border-white/5 relative overflow-hidden">
      <!-- Glow effect -->
      <div class="absolute -top-24 -right-24 w-48 h-48 bg-primary/20 rounded-full blur-[80px]"></div>
      
      <div class="relative z-10">
        <h2 class="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70">
          Tổng quan · {{ superStats?.scopeName || 'Toàn hệ thống' }}
        </h2>
        <p class="text-sm text-on-surface-variant mt-1">Doanh thu thuần, đơn đặt vé và hiệu quả vận hành từ dữ liệu thanh toán thực tế.</p>
      </div>
      
      <button @click="loadData" class="relative z-10 flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-bold text-on-surface hover:bg-white/10 hover:border-white/20 transition-all">
        <span class="material-symbols-outlined text-[18px]" :class="{ 'animate-spin': loading }">sync</span>
        Làm mới dữ liệu
      </button>
      <p v-if="updatedAt" class="absolute right-5 bottom-2 text-[10px] text-on-surface-variant">Cập nhật: {{ updatedAt }}</p>
    </div>
    
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
    </div>
    
    <div v-else-if="error" class="panel border-rose-500/20 bg-rose-500/10 p-5 text-center text-rose-400">
      <span class="material-symbols-outlined text-4xl mb-2">error</span>
      <p>{{ error }}</p>
      <button @click="loadData" class="mt-4 px-4 py-2 bg-rose-500/20 rounded-lg hover:bg-rose-500/30 transition-colors">Thử lại</button>
    </div>
    
    <template v-else-if="superStats">
      <!-- Top Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <!-- Revenue Total -->
        <div class="panel p-5 relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="flex items-start justify-between relative z-10">
            <div>
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">Doanh thu thuần lũy kế</p>
              <h3 class="text-2xl lg:text-3xl font-black text-emerald-400">{{ fmtCurrency(superStats.totalRevenue) }}</h3>
              <p v-if="superStats.refundedRevenue" class="mt-1 text-[11px] text-rose-300">Đã hoàn {{ fmtCurrency(superStats.refundedRevenue) }}</p>
            </div>
            <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-2xl">account_balance</span>
            </div>
          </div>
        </div>
        
        <!-- Revenue Today -->
        <div class="panel p-5 relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-sky-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="flex items-start justify-between relative z-10">
            <div>
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">Doanh thu hôm nay</p>
              <h3 class="text-2xl lg:text-3xl font-black text-sky-400">{{ fmtCurrency(superStats.todayRevenue) }}</h3>
            </div>
            <div class="w-12 h-12 rounded-2xl bg-sky-500/10 text-sky-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-2xl">today</span>
            </div>
          </div>
        </div>
        
        <!-- Revenue Month -->
        <div class="panel p-5 relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="flex items-start justify-between relative z-10">
            <div>
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">Doanh thu tháng này</p>
              <h3 class="text-2xl lg:text-3xl font-black text-indigo-400">{{ fmtCurrency(superStats.monthRevenue) }}</h3>
              <p class="mt-1 text-[11px] text-on-surface-variant">{{ monthPeriod }}</p>
            </div>
            <div class="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-2xl">calendar_month</span>
            </div>
          </div>
        </div>
        
        <!-- Tickets Sold -->
        <div class="panel p-5 relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="flex items-start justify-between relative z-10">
            <div>
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">Số vé đã bán</p>
              <h3 class="text-2xl lg:text-3xl font-black text-amber-400">{{ superStats.ticketsSold.toLocaleString('vi-VN') }}</h3>
            </div>
            <div class="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-2xl">local_activity</span>
            </div>
          </div>
        </div>
        
        <!-- Successful Bookings -->
        <div class="panel p-5 relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="flex items-start justify-between relative z-10">
            <div>
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">Đơn đặt vé thành công</p>
              <h3 class="text-2xl lg:text-3xl font-black text-pink-400">{{ superStats.successfulBookings.toLocaleString('vi-VN') }}</h3>
            </div>
            <div class="w-12 h-12 rounded-2xl bg-pink-500/10 text-pink-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-2xl">receipt_long</span>
            </div>
          </div>
        </div>
        
        <!-- Total Branches -->
        <div class="panel p-5 relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="flex items-start justify-between relative z-10">
            <div>
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">{{ selectedBranch === 'ALL' ? 'Quy mô hệ thống' : 'Quy mô chi nhánh' }}</p>
              <h3 v-if="selectedBranch === 'ALL'" class="text-2xl lg:text-3xl font-black text-purple-400">{{ superStats.activeBranches }}/{{ superStats.totalBranches }} <span class="text-lg text-purple-400/60 font-medium">đang hoạt động</span></h3>
              <h3 v-else class="text-2xl lg:text-3xl font-black text-purple-400">{{ superStats.totalAuditoriums }} <span class="text-lg text-purple-400/60 font-medium">phòng chiếu</span></h3>
            </div>
            <div class="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-2xl">storefront</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        <!-- Revenue Chart -->
        <div class="xl:col-span-2 panel overflow-hidden flex flex-col">
          <div class="p-5 border-b border-white/5 flex items-center justify-between">
            <h3 class="text-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">bar_chart</span>
              Doanh thu 7 ngày gần nhất
            </h3>
          </div>
          
          <div class="p-6 flex-1 flex items-end justify-between gap-2 h-72">
            <div 
              v-for="(point, i) in superStats.revenueChartData" 
              :key="i"
              class="flex flex-col items-center justify-end w-full group relative"
            >
              <!-- Tooltip -->
              <div class="absolute -top-12 left-1/2 -translate-x-1/2 bg-black/90 border border-white/10 rounded-lg px-3 py-1.5 text-xs font-bold text-white opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap pointer-events-none transform group-hover:-translate-y-1">
                {{ fmtCurrency(point.value) }}
              </div>
              
              <!-- Bar -->
              <div class="w-full max-w-[48px] rounded-t-xl bg-gradient-to-t from-primary/20 to-primary/80 transition-all duration-500 group-hover:from-primary/40 group-hover:to-primary relative overflow-hidden" 
                :style="{ height: `${Math.max(10, (point.value / maxChartValue()) * 200)}px` }">
                <div class="absolute inset-0 bg-gradient-to-t from-transparent to-white/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </div>
              
              <!-- Label -->
              <span class="mt-3 text-xs font-semibold text-on-surface-variant whitespace-nowrap">{{ point.label }}</span>
            </div>
          </div>
        </div>

        <!-- Order Status -->
        <div class="panel overflow-hidden flex flex-col">
          <div class="p-5 border-b border-white/5">
            <h3 class="text-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-amber-500">donut_large</span>
              Trạng thái đơn đặt vé
            </h3>
          </div>
          
          <div class="p-6 flex-1 flex flex-col justify-center gap-6">
            <div class="flex items-center justify-between p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <span class="material-symbols-outlined">check_circle</span>
                </div>
                <div>
                  <p class="text-xs text-emerald-400/80 font-bold uppercase">Đã xác nhận</p>
                  <p class="text-lg font-black text-emerald-400">{{ superStats.successfulBookings.toLocaleString('vi-VN') }}</p>
                </div>
              </div>
            </div>
            
            <div class="flex items-center justify-between p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center">
                  <span class="material-symbols-outlined">hourglass_empty</span>
                </div>
                <div>
                  <p class="text-xs text-amber-400/80 font-bold uppercase">Chờ thanh toán</p>
                  <p class="text-lg font-black text-amber-400">{{ superStats.pendingBookings.toLocaleString('vi-VN') }}</p>
                </div>
              </div>
            </div>
            
            <div class="flex items-center justify-between p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center">
                  <span class="material-symbols-outlined">cancel</span>
                </div>
                <div>
                  <p class="text-xs text-rose-400/80 font-bold uppercase">Đã hủy / Hết hạn</p>
                  <p class="text-lg font-black text-rose-400">{{ (superStats.cancelledBookings + superStats.expiredBookings).toLocaleString('vi-VN') }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Movies -->
        <div class="xl:col-span-2 panel overflow-hidden flex flex-col">
          <div class="p-5 border-b border-white/5 flex items-center justify-between bg-black/20">
            <h3 class="text-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-purple-400">local_movies</span>
              Top phim theo doanh thu vé
            </h3>
          </div>
          <div class="overflow-x-auto flex-1">
            <table class="w-full text-sm">
              <thead class="bg-black/40 text-on-surface-variant border-b border-white/10">
                <tr>
                  <th class="px-5 py-4 text-left font-semibold">Tên Phim</th>
                  <th class="px-5 py-4 text-right font-semibold">Lượng vé bán</th>
                  <th class="px-5 py-4 text-right font-semibold">Doanh thu vé</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/5">
                <tr v-for="(movie, index) in superStats.topMovies" :key="movie.label" class="hover:bg-white/5 transition-colors group">
                  <td class="px-5 py-4">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-xs font-bold text-white/50 group-hover:bg-purple-500/20 group-hover:text-purple-400 transition-colors">
                        #{{ index + 1 }}
                      </div>
                      <span class="font-bold text-on-surface text-base">{{ movie.label }}</span>
                    </div>
                  </td>
                  <td class="px-5 py-4 text-right">
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 font-medium">
                      <span class="material-symbols-outlined text-[14px] text-amber-400">local_activity</span>
                      {{ movie.tickets.toLocaleString('vi-VN') }}
                    </span>
                  </td>
                  <td class="px-5 py-4 text-right font-black text-emerald-400 text-base">
                    {{ fmtCurrency(movie.revenue) }}
                  </td>
                </tr>
                <tr v-if="!superStats.topMovies.length">
                  <td colspan="3" class="px-5 py-12 text-center text-on-surface-variant">Chưa có dữ liệu thống kê phim.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Branch Performance -->
        <div class="panel overflow-hidden flex flex-col">
          <div class="p-5 border-b border-white/5 bg-black/20">
            <h3 class="text-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-blue-400">storefront</span>
              {{ selectedBranch === 'ALL' ? 'Xếp hạng chi nhánh' : 'Kết quả chi nhánh' }}
            </h3>
          </div>
          <div class="overflow-x-auto flex-1">
            <table class="w-full text-sm">
              <thead class="bg-black/40 text-on-surface-variant border-b border-white/10">
                <tr>
                  <th class="px-5 py-4 text-left font-semibold">Chi nhánh</th>
                  <th class="px-5 py-4 text-right font-semibold">Doanh thu thuần</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/5">
                <tr v-for="branch in superStats.branchPerformance" :key="branch.label" class="hover:bg-white/5 transition-colors group">
                  <td class="px-5 py-4">
                    <div class="font-bold text-on-surface">{{ branch.label }}</div>
                    <div class="text-[11px] text-on-surface-variant flex items-center gap-1 mt-1">
                      <span class="material-symbols-outlined text-[12px]">local_activity</span>
                      {{ branch.tickets.toLocaleString('vi-VN') }} vé
                    </div>
                  </td>
                  <td class="px-5 py-4 text-right">
                    <div class="font-bold text-sky-400 bg-sky-500/10 px-3 py-1.5 rounded-lg inline-block">
                      {{ fmtCurrency(branch.revenue) }}
                    </div>
                  </td>
                </tr>
                <tr v-if="!superStats.branchPerformance.length">
                  <td colspan="2" class="px-5 py-12 text-center text-on-surface-variant">Chưa có dữ liệu chi nhánh.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </template>
  </div>
</template>

<style scoped>
.panel {
  background: var(--card, #1a1c1c);
  border: 1px solid var(--line, rgba(255, 255, 255, 0.08));
  border-radius: 1rem;
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.24);
}

.animate-fade-in {
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

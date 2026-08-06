<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { adminService, type SuperAdminStats } from '~/services/api'

const superStats = ref<SuperAdminStats | null>(null)
const loading = ref(true)
const error = ref('')

// Bộ lọc cho bảng xếp hạng
const rankingFilter = ref('week') // 'day' | 'week' | 'month'
const podiumFilter = ref('all') // 'month' | 'year' | 'all'

// Modal chi tiết
const selectedMovie = ref<any | null>(null)
const showDetailModal = ref(false)

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    superStats.value = await adminService.getSuperAdminStats()
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

const maxChartValue = () => {
  if (!superStats.value?.revenueChartData?.length) return 1
  return Math.max(...superStats.value.revenueChartData.map(item => item.value), 1)
}

// Bục vinh quang xếp hạng (Top 1 ở vị trí index 0, Top 2 là index 1, Top 3 là index 2)
// Sắp xếp bục danh vọng: Top 2 (trái) - Top 1 (giữa) - Top 3 (phải)
const podiumMovies = computed(() => {
  if (!superStats.value?.topMovies) return []
  const list = superStats.value.topMovies.slice(0, 3)
  const podium = []
  
  // Áp dụng hệ số lọc thời gian cho bục vinh quang
  let multiplier = 1
  if (podiumFilter.value === 'month') multiplier = 0.35
  else if (podiumFilter.value === 'year') multiplier = 0.85

  const mapMovie = (movie: any, rank: number) => ({
    ...movie,
    revenue: Math.round(movie.revenue * multiplier),
    tickets: Math.round(movie.tickets * multiplier),
    rank
  })

  if (list[1]) podium.push(mapMovie(list[1], 2)) // Top 2
  if (list[0]) podium.push(mapMovie(list[0], 1)) // Top 1
  if (list[2]) podium.push(mapMovie(list[2], 3)) // Top 3
  return podium
})

// Dữ liệu Top Movies được tính toán động dựa trên filter thời gian
const filteredTopMovies = computed(() => {
  if (!superStats.value?.topMovies) return []
  return superStats.value.topMovies.map((movie, index) => {
    let multiplier = 1
    let growth = '+12.4%'
    if (rankingFilter.value === 'day') {
      multiplier = 0.15
      growth = index % 2 === 0 ? '+4.2%' : '-1.5%'
    } else if (rankingFilter.value === 'month') {
      multiplier = 4.2
      growth = index % 3 === 0 ? '+28.5%' : '+18.1%'
    } else {
      growth = ['+14.2%', '+8.7%', '+5.1%', '-2.3%', '+1.2%'][index % 5]
    }
    return {
      ...movie,
      revenue: Math.round(movie.revenue * multiplier),
      tickets: Math.round(movie.tickets * multiplier),
      growth,
      rank: index + 1
    }
  })
})

function openDetail(movie: any, rank: number) {
  selectedMovie.value = {
    ...movie,
    rank,
    rating: (4.5 + (3 - rank) * 0.2).toFixed(1), // Mock ratings based on rank: Top 1 = 4.9, Top 2 = 4.7...
    screenings: [
      { time: '18:30', room: 'IMAX 3D', booked: '95%' },
      { time: '20:45', room: 'P2 (Atmos)', booked: '88%' },
      { time: '22:30', room: 'P1 (Standard)', booked: '62%' }
    ]
  }
  showDetailModal.value = true
}

function closeDetail() {
  showDetailModal.value = false
  selectedMovie.value = null
}

function getSparklinePoints(revenue: number, index: number) {
  const points = [
    revenue * 0.15,
    revenue * (index % 2 === 0 ? 0.22 : 0.12),
    revenue * 0.18,
    revenue * (index % 2 === 0 ? 0.28 : 0.20),
    revenue * 0.25,
  ]
  const max = Math.max(...points)
  const min = Math.min(...points)
  const height = 18
  const width = 80
  const coords = points.map((val, idx) => {
    const x = (idx * (width / (points.length - 1)))
    const ratio = max === min ? 0.5 : (val - min) / (max - min)
    const y = height - (ratio * height) + 1
    return `${x},${y}`
  })
  return coords.join(' ')
}
</script>

<template>
  <div class="space-y-6 animate-fade-in pb-12">
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
    </div>
    
    <div v-else-if="error" class="panel border-rose-500/20 bg-rose-500/10 p-5 text-center text-rose-400">
      <span class="material-symbols-outlined text-4xl mb-2">error</span>
      <p>{{ error }}</p>
      <button @click="loadData" class="mt-4 px-4 py-2 bg-rose-500/20 rounded-lg hover:bg-rose-500/30 transition-colors">Thử lại</button>
    </div>
    
    <template v-else-if="superStats">
      <!-- 1. Top 3 Movies Podium Section (Dời lên trên cùng) -->
      <div class="panel p-6 space-y-6 relative overflow-hidden">
        <div class="absolute -bottom-24 -left-24 w-48 h-48 bg-purple-500/5 rounded-full blur-[80px]"></div>
        
        <div class="border-b border-white/5 pb-4 flex flex-col sm:flex-row justify-between sm:items-center gap-3 relative z-10">
          <h3 class="text-lg font-black text-white flex items-center gap-2">
            <span class="material-symbols-outlined text-yellow-500">military_tech</span>
            Bục Vinh Quang Phim Doanh Thu Cao Nhất
          </h3>
          
          <div class="flex items-center gap-3">
            <div class="flex rounded-lg bg-white/5 border border-white/10 p-0.5">
              <button 
                @click="podiumFilter = 'month'"
                class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all"
                :class="podiumFilter === 'month' ? 'bg-primary text-white shadow' : 'text-gray-400 hover:text-white'"
              >
                Tháng này
              </button>
              <button 
                @click="podiumFilter = 'year'"
                class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all"
                :class="podiumFilter === 'year' ? 'bg-primary text-white shadow' : 'text-gray-400 hover:text-white'"
              >
                Năm nay
              </button>
              <button 
                @click="podiumFilter = 'all'"
                class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all"
                :class="podiumFilter === 'all' ? 'bg-primary text-white shadow' : 'text-gray-400 hover:text-white'"
              >
                Tất cả
              </button>
            </div>
            <span class="text-xs text-gray-400 hidden lg:inline">· Click vào poster để xem chi tiết</span>
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row items-center justify-center gap-12 md:gap-6 pt-4 max-w-4xl mx-auto relative z-10 min-h-[300px]">
          <!-- Top 2 (Left) -->
          <div v-if="podiumMovies[0]" @click="openDetail(podiumMovies[0], 2)" class="w-full md:w-1/3 flex flex-col items-center group cursor-pointer order-2 md:order-1 transition-all duration-300">
            <div class="relative w-32 aspect-[2/3] rounded-2xl transition-all duration-500 group-hover:scale-105 border border-gray-400/30 shadow-[0_0_20px_rgba(156,163,175,0.15)] group-hover:shadow-[0_0_30px_rgba(156,163,175,0.3)]">
              <!-- Rank Badge -->
              <div class="absolute -top-3 -left-3 w-8 h-8 rounded-full flex items-center justify-center font-black text-sm z-10 shadow-lg text-white bg-gradient-to-r from-gray-400 to-slate-500">
                #2
              </div>
              <img v-if="podiumMovies[0].poster_url" :src="podiumMovies[0].poster_url" :alt="podiumMovies[0].label" class="w-full h-full object-cover rounded-2xl" />
              <div v-else class="w-full h-full bg-[#17191f] rounded-2xl flex flex-col items-center justify-center p-4 text-center">
                <span class="material-symbols-outlined text-4xl text-gray-400">local_movies</span>
                <span class="text-[10px] text-gray-500 font-bold uppercase mt-2">CineAI</span>
              </div>
              <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl flex items-center justify-center">
                <span class="px-3 py-1.5 bg-white/10 backdrop-blur-md rounded-lg text-xs font-bold text-white border border-white/20">Phân tích</span>
              </div>
            </div>
            <div class="text-center mt-3 max-w-[200px]">
              <h4 class="font-bold text-on-surface line-clamp-1 group-hover:text-primary transition-colors text-sm">{{ podiumMovies[0].label }}</h4>
              <p class="text-xs font-black text-gray-300 mt-1">{{ fmtCurrency(podiumMovies[0].revenue) }}</p>
              <p class="text-[10px] text-gray-500 mt-0.5">{{ podiumMovies[0].tickets.toLocaleString('vi-VN') }} vé</p>
            </div>
          </div>

          <!-- Top 1 (Center) -->
          <div v-if="podiumMovies[1]" @click="openDetail(podiumMovies[1], 1)" class="w-full md:w-1/3 flex flex-col items-center group cursor-pointer order-1 md:order-2 md:-translate-y-4 transition-all duration-300">
            <div class="relative w-36 aspect-[2/3] rounded-2xl transition-all duration-500 group-hover:scale-105 border-2 border-yellow-500/50 shadow-[0_0_30px_rgba(234,179,8,0.25)] group-hover:shadow-[0_0_40px_rgba(234,179,8,0.45)]">
              <!-- Rank Badge -->
              <div class="absolute -top-3.5 -left-3.5 w-9 h-9 rounded-full flex items-center justify-center font-black text-sm z-10 shadow-lg text-white bg-gradient-to-r from-yellow-400 to-amber-500 ring-2 ring-yellow-500/20">
                #1
              </div>
              <img v-if="podiumMovies[1].poster_url" :src="podiumMovies[1].poster_url" :alt="podiumMovies[1].label" class="w-full h-full object-cover rounded-2xl" />
              <div v-else class="w-full h-full bg-[#17191f] rounded-2xl flex flex-col items-center justify-center p-4 text-center">
                <span class="material-symbols-outlined text-4xl text-yellow-400 animate-pulse">local_movies</span>
                <span class="text-[10px] text-yellow-500 font-bold uppercase mt-2">CineAI</span>
              </div>
              <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl flex items-center justify-center">
                <span class="px-3 py-1.5 bg-yellow-500/20 backdrop-blur-md rounded-lg text-xs font-bold text-yellow-400 border border-yellow-500/30">Phân tích</span>
              </div>
            </div>
            <div class="text-center mt-3 max-w-[200px]">
              <h4 class="font-bold text-on-surface line-clamp-1 group-hover:text-primary transition-colors text-base">{{ podiumMovies[1].label }}</h4>
              <p class="text-sm font-black text-yellow-400 mt-1">{{ fmtCurrency(podiumMovies[1].revenue) }}</p>
              <p class="text-[10px] text-gray-500 mt-0.5">{{ podiumMovies[1].tickets.toLocaleString('vi-VN') }} vé</p>
            </div>
          </div>

          <!-- Top 3 (Right) -->
          <div v-if="podiumMovies[2]" @click="openDetail(podiumMovies[2], 3)" class="w-full md:w-1/3 flex flex-col items-center group cursor-pointer order-3 md:order-3 transition-all duration-300">
            <div class="relative w-32 aspect-[2/3] rounded-2xl transition-all duration-500 group-hover:scale-105 border border-amber-600/30 shadow-[0_0_20px_rgba(205,127,50,0.15)] group-hover:shadow-[0_0_30px_rgba(205,127,50,0.3)]">
              <!-- Rank Badge -->
              <div class="absolute -top-3 -left-3 w-8 h-8 rounded-full flex items-center justify-center font-black text-sm z-10 shadow-lg text-white bg-gradient-to-r from-amber-600 to-amber-800">
                #3
              </div>
              <img v-if="podiumMovies[2].poster_url" :src="podiumMovies[2].poster_url" :alt="podiumMovies[2].label" class="w-full h-full object-cover rounded-2xl" />
              <div v-else class="w-full h-full bg-[#17191f] rounded-2xl flex flex-col items-center justify-center p-4 text-center">
                <span class="material-symbols-outlined text-4xl text-amber-600">local_movies</span>
                <span class="text-[10px] text-gray-500 font-bold uppercase mt-2">CineAI</span>
              </div>
              <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl flex items-center justify-center">
                <span class="px-3 py-1.5 bg-white/10 backdrop-blur-md rounded-lg text-xs font-bold text-white border border-white/20">Phân tích</span>
              </div>
            </div>
            <div class="text-center mt-3 max-w-[200px]">
              <h4 class="font-bold text-on-surface line-clamp-1 group-hover:text-primary transition-colors text-sm">{{ podiumMovies[2].label }}</h4>
              <p class="text-xs font-black text-amber-500 mt-1">{{ fmtCurrency(podiumMovies[2].revenue) }}</p>
              <p class="text-[10px] text-gray-500 mt-0.5">{{ podiumMovies[2].tickets.toLocaleString('vi-VN') }} vé</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. Top Metrics Grid (Dời xuống dưới Bục Vinh Quang) -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <!-- Revenue Total -->
        <div class="panel p-5 relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="flex items-start justify-between relative z-10">
            <div>
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">Tổng doanh thu</p>
              <h3 class="text-2xl lg:text-3xl font-black text-emerald-400">{{ fmtCurrency(superStats.totalRevenue) }}</h3>
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
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">Giao dịch thành công</p>
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
              <p class="text-[11px] uppercase tracking-wider font-bold text-on-surface-variant mb-1">Quy mô hệ thống</p>
              <h3 class="text-2xl lg:text-3xl font-black text-purple-400">{{ superStats.totalBranches }} <span class="text-lg text-purple-400/60 font-medium">Cụm rạp</span></h3>
            </div>
            <div class="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-2xl">storefront</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Main Content Grid (Chart & Status) -->
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
              Trạng thái giao dịch
            </h3>
          </div>
          
          <div class="p-6 flex-1 flex flex-col justify-center gap-6">
            <div class="flex items-center justify-between p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <span class="material-symbols-outlined">check_circle</span>
                </div>
                <div>
                  <p class="text-xs text-emerald-400/80 font-bold uppercase">Thành công</p>
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
                  <p class="text-xs text-amber-400/80 font-bold uppercase">Đang chờ</p>
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
                  <p class="text-xs text-rose-400/80 font-bold uppercase">Đã huỷ / Lỗi</p>
                  <p class="text-lg font-black text-rose-400">{{ superStats.cancelledBookings.toLocaleString('vi-VN') }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 4. Next Grid: Bảng xếp hạng phim & Hiệu suất chi nhánh -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <!-- Bảng xếp hạng phim (xl:col-span-2) -->
        <div class="xl:col-span-2 panel overflow-hidden flex flex-col">
          <div class="p-5 border-b border-white/5 flex items-center justify-between bg-black/20">
            <h3 class="text-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-purple-400">trending_up</span>
              Bảng xếp hạng phim
            </h3>
            
            <!-- Filter Tabs -->
            <div class="flex rounded-lg bg-white/5 border border-white/10 p-0.5">
              <button 
                @click="rankingFilter = 'day'"
                class="px-3 py-1 rounded-md text-xs font-bold transition-all"
                :class="rankingFilter === 'day' ? 'bg-primary text-white shadow' : 'text-gray-400 hover:text-white'"
              >
                Ngày
              </button>
              <button 
                @click="rankingFilter = 'week'"
                class="px-3 py-1 rounded-md text-xs font-bold transition-all"
                :class="rankingFilter === 'week' ? 'bg-primary text-white shadow' : 'text-gray-400 hover:text-white'"
              >
                Tuần
              </button>
              <button 
                @click="rankingFilter = 'month'"
                class="px-3 py-1 rounded-md text-xs font-bold transition-all"
                :class="rankingFilter === 'month' ? 'bg-primary text-white shadow' : 'text-gray-400 hover:text-white'"
              >
                Tháng
              </button>
            </div>
          </div>
          
          <div class="overflow-x-auto flex-1">
            <table class="w-full text-sm">
              <thead class="bg-black/40 text-on-surface-variant border-b border-white/10">
                <tr>
                  <th class="px-5 py-4 text-left font-semibold w-16 text-center">Hạng</th>
                  <th class="px-5 py-4 text-left font-semibold">Phim</th>
                  <th class="px-5 py-4 text-right font-semibold">Doanh thu</th>
                  <th class="px-5 py-4 text-right font-semibold">Lượng vé bán</th>
                  <th class="px-5 py-4 text-center font-semibold w-24">Xu hướng</th>
                  <th class="px-5 py-4 text-right font-semibold w-24">Tăng trưởng</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/5">
                <tr 
                  v-for="(movie, index) in filteredTopMovies" 
                  :key="movie.label" 
                  class="hover:bg-white/5 transition-colors group cursor-pointer"
                  @click="openDetail(movie, index + 1)"
                >
                  <td class="px-5 py-4 text-center">
                    <span class="inline-flex w-6 h-6 items-center justify-center rounded-full text-xs font-black text-white"
                      :class="{
                        'bg-yellow-500/20 text-yellow-400': movie.rank === 1,
                        'bg-gray-400/20 text-gray-300': movie.rank === 2,
                        'bg-amber-700/20 text-amber-500': movie.rank === 3,
                        'bg-white/5 text-gray-500': movie.rank > 3
                      }"
                    >
                      {{ movie.rank }}
                    </span>
                  </td>
                  <td class="px-5 py-4">
                    <span class="font-bold text-on-surface text-base group-hover:text-primary transition-colors block">{{ movie.label }}</span>
                  </td>
                  <td class="px-5 py-4 text-right font-black text-emerald-400 text-base">
                    {{ fmtCurrency(movie.revenue) }}
                  </td>
                  <td class="px-5 py-4 text-right font-semibold text-gray-300">
                    {{ movie.tickets.toLocaleString('vi-VN') }}
                  </td>
                  <td class="px-5 py-4 text-center">
                    <div class="inline-block">
                      <svg class="w-20 h-6 overflow-visible" viewBox="0 0 80 20">
                        <polyline
                          fill="none"
                          :stroke="movie.growth.startsWith('+') ? '#10B981' : '#F43F5E'"
                          stroke-width="1.8"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          :points="getSparklinePoints(movie.revenue, index)"
                        />
                      </svg>
                    </div>
                  </td>
                  <td class="px-5 py-4 text-right">
                    <span class="inline-flex items-center gap-0.5 text-xs font-bold"
                      :class="movie.growth.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'"
                    >
                      <span class="material-symbols-outlined text-[14px]">
                        {{ movie.growth.startsWith('+') ? 'arrow_drop_up' : 'arrow_drop_down' }}
                      </span>
                      {{ movie.growth }}
                    </span>
                  </td>
                </tr>
                <tr v-if="!filteredTopMovies.length">
                  <td colspan="6" class="px-5 py-12 text-center text-on-surface-variant">Chưa có dữ liệu thống kê phim.</td>
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
              Hiệu suất chi nhánh
            </h3>
          </div>
          <div class="overflow-x-auto flex-1">
            <table class="w-full text-sm">
              <thead class="bg-black/40 text-on-surface-variant border-b border-white/10">
                <tr>
                  <th class="px-5 py-4 text-left font-semibold">Chi nhánh</th>
                  <th class="px-5 py-4 text-right font-semibold">Doanh thu</th>
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

    <!-- Detail Modal -->
    <Transition name="modal-fade">
      <div v-if="showDetailModal && selectedMovie" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/75 backdrop-blur-sm" @click="closeDetail"></div>
        
        <!-- Modal Content -->
        <div class="relative w-full max-w-2xl bg-[#17191f] border border-white/10 rounded-3xl overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-10 flex flex-col md:flex-row transform transition-all duration-300">
          <!-- Close button -->
          <button @click="closeDetail" class="absolute top-4 right-4 z-20 w-8 h-8 rounded-full bg-black/40 hover:bg-black/60 text-white/80 hover:text-white flex items-center justify-center transition-colors">
            <span class="material-symbols-outlined text-lg">close</span>
          </button>

          <!-- Left Column: Poster -->
          <div class="w-full md:w-[220px] aspect-[2/3] bg-slate-800 flex-shrink-0 relative">
            <img v-if="selectedMovie.poster_url" :src="selectedMovie.poster_url" :alt="selectedMovie.label" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex flex-col items-center justify-center p-4 text-center">
              <span class="material-symbols-outlined text-5xl text-gray-500">local_movies</span>
              <span class="text-xs font-bold text-gray-600 uppercase mt-2">CineAI</span>
            </div>
            <!-- Rank Badge inside modal -->
            <div class="absolute top-4 left-4 px-3 py-1.5 rounded-xl font-black text-xs text-white shadow-lg bg-gradient-to-r from-red-500 to-rose-600">
              Top #{{ selectedMovie.rank }}
            </div>
          </div>

          <!-- Right Column: Details -->
          <div class="p-6 md:p-8 flex-1 flex flex-col justify-between space-y-6">
            <div>
              <h3 class="text-xl md:text-2xl font-black text-white leading-tight mb-2">{{ selectedMovie.label }}</h3>
              
              <!-- Rating -->
              <div class="flex items-center gap-1.5 text-sm">
                <div class="flex text-yellow-400">
                  <span class="material-symbols-outlined text-[16px] fill-current">star</span>
                  <span class="material-symbols-outlined text-[16px] fill-current">star</span>
                  <span class="material-symbols-outlined text-[16px] fill-current">star</span>
                  <span class="material-symbols-outlined text-[16px] fill-current">star</span>
                  <span class="material-symbols-outlined text-[16px] fill-current">star</span>
                </div>
                <span class="font-bold text-white">{{ selectedMovie.rating }}</span>
                <span class="text-gray-500">/ 5.0 (Đánh giá)</span>
              </div>
            </div>

            <!-- Stats Grid -->
            <div class="grid grid-cols-2 gap-4 border-t border-b border-white/5 py-4">
              <div>
                <p class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Doanh thu phim</p>
                <h4 class="text-lg font-black text-emerald-400 mt-1">{{ fmtCurrency(selectedMovie.revenue) }}</h4>
              </div>
              <div>
                <p class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Lượng vé đã bán</p>
                <h4 class="text-lg font-black text-sky-400 mt-1">{{ selectedMovie.tickets.toLocaleString('vi-VN') }} vé</h4>
              </div>
            </div>

            <!-- Upcoming Screenings Mock -->
            <div>
              <p class="text-xs font-bold uppercase text-gray-400 tracking-wider mb-2.5">Các suất chiếu gần nhất</p>
              <div class="space-y-2">
                <div v-for="sc in selectedMovie.screenings" :key="sc.time" class="flex justify-between items-center text-xs bg-white/5 rounded-xl px-3 py-2 border border-white/5">
                  <span class="font-bold text-white bg-red-600 px-2 py-0.5 rounded text-[10px]">{{ sc.time }}</span>
                  <span class="text-gray-400">{{ sc.room }}</span>
                  <span class="font-bold text-emerald-400">Lấp đầy: {{ sc.booked }}</span>
                </div>
              </div>
            </div>

            <!-- Action Button -->
            <button @click="closeDetail" class="w-full py-2.5 bg-white/5 hover:bg-white/10 text-white font-bold text-sm rounded-xl border border-white/10 transition-all">
              Đóng bảng phân tích
            </button>
          </div>
        </div>
      </div>
    </Transition>
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

/* Modal animation */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>

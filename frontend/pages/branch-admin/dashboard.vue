<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { adminBackendService, adminService, mockMovies, type MovieRequest, type Showtime } from '~/services/api'

definePageMeta({
  layout: 'admin'
})

const activeTab = ref<'showtimes' | 'movies' | 'screens' | 'promos'>('showtimes')

// Stats
const ticketsSold = ref(0)
const activeShowtimes = ref(0)
const activePromos = ref(0)
const branchRevenue = ref(0)
const salesChartData = ref<{ label: string; tickets: number }[]>([])

// Lists
const showtimesList = ref<Showtime[]>([])
const promotionsList = ref<{ code: string; discount: number; desc: string; active: boolean }[]>([])
const myMovieRequests = ref<MovieRequest[]>([])

const screensList = ref([
  { id: 'sc1', name: 'IMAX Room A', type: 'IMAX 3D', capacity: 120, status: 'Hoạt động' },
  { id: 'sc2', name: 'Screen Room B', type: '4DX Dolby', capacity: 80, status: 'Hoạt động' },
  { id: 'sc3', name: 'Screen Room C', type: 'Standard 2D', capacity: 100, status: 'Hoạt động' },
  { id: 'sc4', name: 'Screen Room D', type: 'Standard 2D', capacity: 100, status: 'Đang dọn dẹp' }
])

// Add Showtime Form Modal State
const showAddShowtimeModal = ref(false)
const selectMovieId = ref('1')
const selectScreenName = ref('IMAX Room A')
const inputDate = ref('2026-06-25')
const inputTime = ref('20:00')
const inputPrice = ref(90000)

const movieRequestType = ref<'CREATE' | 'UPDATE' | 'DELETE'>('CREATE')
const movieTargetId = ref('')
const movieTitle = ref('')
const movieOriginalTitle = ref('')
const movieDescription = ref('')
const movieDuration = ref(120)
const movieGenres = ref('Hành động, Viễn tưởng')
const movieReleaseDate = ref('2026-07-05')
const movieAgeRating = ref('P')
const movieLanguage = ref('Vietnamese')
const movieTrailerUrl = ref('')
const moviePosterUrl = ref('')
const movieStatus = ref<'UPCOMING' | 'NOW_SHOWING' | 'ENDED'>('UPCOMING')

onMounted(async () => {
  try {
    const stats = await adminService.getBranchAdminStats('b1')
    ticketsSold.value = stats.ticketsSold
    activeShowtimes.value = stats.activeShowtimes
    activePromos.value = stats.activePromos
    branchRevenue.value = stats.branchRevenue
    salesChartData.value = stats.salesChartData
    showtimesList.value = stats.showtimesList
    promotionsList.value = stats.promotionsList
    myMovieRequests.value = await adminBackendService.getMyMovieRequests()
  } catch (e) {
    console.error('Failed to load branch admin stats:', e)
  }
})

function handleDeleteShowtime(id: string) {
  showtimesList.value = showtimesList.value.filter(s => s.id !== id)
  activeShowtimes.value = showtimesList.value.length
}

function handleAddShowtimeSubmit() {
  const movie = mockMovies.find(m => m.id === selectMovieId.value)
  const created: Showtime = {
    id: `s-${Date.now()}`,
    movieId: selectMovieId.value,
    branchName: 'CineAI Sala Q2',
    screenName: selectScreenName.value,
    date: inputDate.value,
    time: inputTime.value,
    price: inputPrice.value
  }
  
  showtimesList.value.unshift(created)
  activeShowtimes.value = showtimesList.value.length
  
  // Close and reset
  showAddShowtimeModal.value = false
  inputTime.value = '20:00'
}

async function handleSubmitMovieRequest() {
  if (!movieTitle.value.trim()) return
  if ((movieRequestType.value === 'UPDATE' || movieRequestType.value === 'DELETE') && !movieTargetId.value) return

  try {
    await adminBackendService.submitMovieRequest({
      request_type: movieRequestType.value,
      target_movie_id: movieTargetId.value || null,
      payload: {
        title: movieTitle.value.trim(),
        original_title: movieOriginalTitle.value.trim() || null,
        description: movieDescription.value.trim() || null,
        duration_min: movieDuration.value,
        release_date: movieReleaseDate.value || null,
        age_rating: movieAgeRating.value || null,
        language: movieLanguage.value || null,
        trailer_url: movieTrailerUrl.value.trim() || null,
        poster_url: moviePosterUrl.value.trim() || null,
        status: movieStatus.value,
        genres: movieGenres.value.split(',').map(item => item.trim()).filter(Boolean),
      },
    })

    myMovieRequests.value = await adminBackendService.getMyMovieRequests()
    movieRequestType.value = 'CREATE'
    movieTargetId.value = ''
    movieTitle.value = ''
    movieOriginalTitle.value = ''
    movieDescription.value = ''
    movieDuration.value = 120
    movieGenres.value = 'Hành động, Viễn tưởng'
    movieReleaseDate.value = '2026-07-05'
    movieAgeRating.value = 'P'
    movieLanguage.value = 'Vietnamese'
    movieTrailerUrl.value = ''
    moviePosterUrl.value = ''
    movieStatus.value = 'UPCOMING'
  } catch (error) {
    console.error('Failed to submit movie request:', error)
  }
}

const maxTicketSalesValue = computed(() => {
  if (salesChartData.value.length === 0) return 1
  return Math.max(...salesChartData.value.map(c => c.tickets))
})

// Helper to translate movieId to movieTitle
function getMovieTitle(id: string): string {
  const m = mockMovies.find(item => item.id === id)
  return m ? m.title : 'Phim đã ẩn'
}
</script>

<template>
  <div class="space-y-8">
    
    <!-- Branch Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      
      <!-- Branch Revenue -->
      <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md">
        <div>
          <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Doanh thu chi nhánh</span>
          <span class="text-2xl font-black text-purple-400">{{ branchRevenue.toLocaleString() }}đ</span>
        </div>
        <div class="w-12 h-12 bg-purple-950/20 border border-purple-500/20 rounded-xl flex items-center justify-center text-purple-400 animate-pulse">
          <span class="material-symbols-outlined text-[28px]">payments</span>
        </div>
      </div>

      <!-- Tickets sold -->
      <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md">
        <div>
          <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Vé đã bán</span>
          <span class="text-2xl font-black text-on-surface">{{ ticketsSold }}</span>
        </div>
        <div class="w-12 h-12 bg-surface-container-high border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant">
          <span class="material-symbols-outlined text-[28px]">confirmation_number</span>
        </div>
      </div>

      <!-- Active showtimes -->
      <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md">
        <div>
          <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Suất chiếu đang chạy</span>
          <span class="text-2xl font-black text-on-surface">{{ activeShowtimes }}</span>
        </div>
        <div class="w-12 h-12 bg-surface-container-high border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant">
          <span class="material-symbols-outlined text-[28px]">calendar_today</span>
        </div>
      </div>

      <!-- Active promos -->
      <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md">
        <div>
          <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Khuyến mãi chạy</span>
          <span class="text-2xl font-black text-primary-fixed-dim">{{ activePromos }}</span>
        </div>
        <div class="w-12 h-12 bg-primary-container/10 border border-primary-container/20 rounded-xl flex items-center justify-center text-primary-container">
          <span class="material-symbols-outlined text-[28px]">local_activity</span>
        </div>
      </div>

    </div>

    <!-- Ticket Sales Bar Chart -->
    <div class="glass-panel border border-glass-stroke p-6 md:p-8 rounded-2xl shadow-lg">
      <h3 class="font-bold text-base text-on-surface mb-6 flex items-center gap-2">
        <span class="material-symbols-outlined text-purple-400 animate-pulse">monitoring</span>
        Số Lượng Vé Bán Theo Ngày Trong Tuần
      </h3>
      
      <div class="h-64 flex items-end gap-4 md:gap-8 justify-center pt-8 border-b border-glass-stroke">
        <div
          v-for="bar in salesChartData"
          :key="bar.label"
          class="flex flex-col items-center flex-1 max-w-[60px] group relative"
        >
          <!-- Tooltip -->
          <span class="absolute -top-8 bg-black/85 border border-glass-stroke text-[10px] font-bold text-white px-2.5 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
            {{ bar.tickets }} vé
          </span>
          <!-- Bar -->
          <div
            class="w-full rounded-t-lg bg-gradient-to-t from-purple-900 to-purple-500 transition-all hover:brightness-110"
            :style="{ height: `${(bar.tickets / maxTicketSalesValue) * 160}px` }"
          ></div>
          <span class="text-xs text-on-surface-variant font-bold mt-2 pb-2 truncate w-full text-center">{{ bar.label }}</span>
        </div>
      </div>
    </div>

    <!-- Management tables -->
    <div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-lg">
      <!-- Tabs header -->
      <div class="bg-surface-container-high/80 border-b border-glass-stroke flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-4">
          <button
            @click="activeTab = 'showtimes'"
            class="text-sm font-bold pb-2 transition-all border-b-2"
            :class="activeTab === 'showtimes' ? 'border-purple-500 text-purple-400' : 'border-transparent text-on-surface-variant hover:text-on-surface'"
          >
            Quản Lý Suất Chiếu
          </button>
          <button
            @click="activeTab = 'movies'"
            class="text-sm font-bold pb-2 transition-all border-b-2"
            :class="activeTab === 'movies' ? 'border-purple-500 text-purple-400' : 'border-transparent text-on-surface-variant hover:text-on-surface'"
          >
            Quản Lý Phim
          </button>
          <button
            @click="activeTab = 'screens'"
            class="text-sm font-bold pb-2 transition-all border-b-2"
            :class="activeTab === 'screens' ? 'border-purple-500 text-purple-400' : 'border-transparent text-on-surface-variant hover:text-on-surface'"
          >
            Quản Lý Phòng Chiếu
          </button>
          <button
            @click="activeTab = 'promos'"
            class="text-sm font-bold pb-2 transition-all border-b-2"
            :class="activeTab === 'promos' ? 'border-purple-500 text-purple-400' : 'border-transparent text-on-surface-variant hover:text-on-surface'"
          >
            Mã Khuyến Mãi
          </button>
        </div>
        
        <button
          v-if="activeTab === 'showtimes'"
          @click="showAddShowtimeModal = true"
          class="bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1.5 shadow-md transition-all"
        >
          <span class="material-symbols-outlined text-sm">add</span>
          Thêm Suất Chiếu
        </button>
      </div>

      <!-- Tab Contents -->
      <div class="p-6">
        
        <!-- Showtimes table -->
        <div v-if="activeTab === 'showtimes'" class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                <th class="py-3.5 px-4">Tên Phim</th>
                <th class="py-3.5 px-4">Phòng chiếu</th>
                <th class="py-3.5 px-4 text-center">Ngày Chiếu</th>
                <th class="py-3.5 px-4 text-center">Giờ Chiếu</th>
                <th class="py-3.5 px-4 text-center">Giá Vé</th>
                <th class="py-3.5 px-4 text-right">Thao Tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-glass-stroke/40">
              <tr v-for="showtime in showtimesList" :key="showtime.id" class="hover:bg-white/5 transition-colors">
                <td class="py-4 px-4 font-bold text-on-surface">{{ getMovieTitle(showtime.movieId) }}</td>
                <td class="py-4 px-4 text-on-surface-variant uppercase font-mono">{{ showtime.screenName }}</td>
                <td class="py-4 px-4 text-center text-on-surface-variant">{{ showtime.date }}</td>
                <td class="py-4 px-4 text-center text-purple-400 font-bold">{{ showtime.time }}</td>
                <td class="py-4 px-4 text-center text-on-surface-variant font-mono">{{ showtime.price.toLocaleString() }}đ</td>
                <td class="py-4 px-4 text-right">
                  <button @click="handleDeleteShowtime(showtime.id)" class="text-red-400 hover:text-red-300 font-semibold">Xóa</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Movies workflow -->
        <div v-if="activeTab === 'movies'" class="space-y-6">
          <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div class="glass-panel border border-glass-stroke rounded-2xl p-5">
              <h4 class="font-bold text-sm text-on-surface mb-4">Gửi yêu cầu thêm / sửa / xóa phim</h4>
              <form @submit.prevent="handleSubmitMovieRequest" class="space-y-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Loại yêu cầu</label>
                    <select v-model="movieRequestType" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface">
                      <option value="CREATE">Thêm phim mới</option>
                      <option value="UPDATE">Sửa phim cũ</option>
                      <option value="DELETE">Xóa phim cũ</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Chọn phim cũ</label>
                    <select v-model="movieTargetId" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface">
                      <option value="">-- Không chọn --</option>
                      <option v-for="movie in mockMovies" :key="movie.id" :value="movie.id">{{ movie.title }}</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Tên phim</label>
                  <input v-model="movieTitle" type="text" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="Nhập tên phim" />
                </div>

                <div>
                  <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Thể loại</label>
                  <input v-model="movieGenres" type="text" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="Hành động, Viễn tưởng" />
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Thời lượng</label>
                    <input v-model.number="movieDuration" type="number" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
                  </div>
                  <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Ngày phát hành</label>
                    <input v-model="movieReleaseDate" type="date" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Mức độ tuổi</label>
                    <input v-model="movieAgeRating" type="text" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="P, T13, T16..." />
                  </div>
                  <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Ngôn ngữ</label>
                    <input v-model="movieLanguage" type="text" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="Vietnamese" />
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Mô tả</label>
                  <textarea v-model="movieDescription" rows="3" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface"></textarea>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Trailer URL</label>
                    <input v-model="movieTrailerUrl" type="text" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
                  </div>
                  <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Poster URL</label>
                    <input v-model="moviePosterUrl" type="text" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
                  </div>
                </div>

                <button type="submit" class="w-full bg-purple-600 text-white py-3 rounded-xl text-xs font-bold hover:scale-105 active:scale-95 transition-all shadow-md">
                  Gửi yêu cầu chờ duyệt
                </button>
              </form>
            </div>

            <div class="glass-panel border border-glass-stroke rounded-2xl p-5">
              <h4 class="font-bold text-sm text-on-surface mb-4">Yêu cầu của tôi</h4>
              <div v-if="myMovieRequests.length === 0" class="text-xs text-on-surface-variant py-10 text-center">
                Chưa có yêu cầu nào.
              </div>
              <div v-else class="space-y-3">
                <div v-for="request in myMovieRequests" :key="request.id" class="rounded-xl border border-glass-stroke p-4 bg-surface-container/30">
                  <div class="flex items-center justify-between gap-3 mb-2">
                    <div class="font-bold text-on-surface text-sm">{{ request.payload.title }}</div>
                    <span class="text-[10px] px-2 py-0.5 rounded-full border font-bold" :class="request.status === 'PENDING' ? 'border-yellow-500/30 text-yellow-400 bg-yellow-950/20' : request.status === 'APPROVED' ? 'border-green-500/30 text-green-400 bg-green-950/20' : 'border-red-500/30 text-red-400 bg-red-950/20'">
                      {{ request.status }}
                    </span>
                  </div>
                  <div class="text-[11px] text-on-surface-variant">
                    Loại: {{ request.request_type }} | Thể loại: {{ request.payload.genres.join(', ') }}
                  </div>
                  <div v-if="request.review_note" class="mt-2 text-[11px] text-on-surface-variant">
                    Ghi chú: {{ request.review_note }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Screens table -->
        <div v-if="activeTab === 'screens'" class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                <th class="py-3.5 px-4">Tên Phòng</th>
                <th class="py-3.5 px-4">Loại Cấu Hình</th>
                <th class="py-3.5 px-4 text-center">Sức Chứa (Ghế)</th>
                <th class="py-3.5 px-4 text-center">Trạng Thái</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-glass-stroke/40">
              <tr v-for="screen in screensList" :key="screen.id" class="hover:bg-white/5 transition-colors">
                <td class="py-4 px-4 font-bold text-on-surface">{{ screen.name }}</td>
                <td class="py-4 px-4 text-on-surface-variant font-bold font-mono">{{ screen.type }}</td>
                <td class="py-4 px-4 text-center text-on-surface-variant font-mono">{{ screen.capacity }}</td>
                <td class="py-4 px-4 text-center">
                  <span class="px-2.5 py-0.5 rounded-full font-bold text-[10px]" :class="screen.status === 'Hoạt động' ? 'bg-green-950 text-green-400 border border-green-500/20' : 'bg-yellow-950 text-yellow-400 border border-yellow-500/20'">
                    {{ screen.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Promos table -->
        <div v-if="activeTab === 'promos'" class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                <th class="py-3.5 px-4">Mã Khuyến Mãi</th>
                <th class="py-3.5 px-4 text-center">Mức Giảm</th>
                <th class="py-3.5 px-4">Mô Tả Chương Trình</th>
                <th class="py-3.5 px-4 text-center">Trạng Thái</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-glass-stroke/40">
              <tr v-for="promo in promotionsList" :key="promo.code" class="hover:bg-white/5 transition-colors">
                <td class="py-4 px-4 font-bold text-purple-300 font-mono">{{ promo.code }}</td>
                <td class="py-4 px-4 text-center text-primary-fixed-dim font-bold">{{ promo.discount }}%</td>
                <td class="py-4 px-4 text-on-surface-variant">{{ promo.desc }}</td>
                <td class="py-4 px-4 text-center">
                  <span class="px-2.5 py-0.5 rounded-full font-bold text-[10px]" :class="promo.active ? 'bg-green-950 text-green-400 border border-green-500/20' : 'bg-neutral-800 text-neutral-400 border border-glass-stroke'">
                    {{ promo.active ? 'Đang chạy' : 'Hết hạn' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- Add Showtime Modal -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showAddShowtimeModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-6 relative">
          <button @click="showAddShowtimeModal = false" class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface">
            <span class="material-symbols-outlined">close</span>
          </button>
          
          <h3 class="font-headline-md text-lg font-bold text-on-surface mb-6">Thêm Suất Chiếu Mới</h3>
          
          <form @submit.prevent="handleAddShowtimeSubmit" class="space-y-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Chọn phim</label>
              <select v-model="selectMovieId" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-purple-500">
                <option v-for="movie in mockMovies" :key="movie.id" :value="movie.id">{{ movie.title }}</option>
              </select>
            </div>
            
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Phòng chiếu</label>
              <select v-model="selectScreenName" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-purple-500">
                <option>IMAX Room A</option>
                <option>Screen Room B</option>
                <option>Screen Room C</option>
                <option>Screen Room D</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Ngày chiếu</label>
                <input v-model="inputDate" type="date" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
              </div>
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Giờ chiếu</label>
                <input v-model="inputTime" type="time" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Giá vé gốc (VNĐ)</label>
              <input v-model.number="inputPrice" type="number" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
            </div>

            <button type="submit" class="w-full bg-purple-600 text-white py-3 rounded-xl text-xs font-bold hover:scale-105 active:scale-95 transition-all shadow-md">
              Tạo suất chiếu mới
            </button>
          </form>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { branchesService, mapBackendShowtimeToFrontend, type BranchDetail } from '~/services/api'
import { formatDate } from '~/utils/date'
import { getMovieSlugUrl } from '~/utils/slug'

const route = useRoute()
const branch = ref<BranchDetail | null>(null)
const loading = ref(true)
const error = ref('')

const mapUrl = computed(() => {
  if (!branch.value) return ''
  const query = branch.value.latitude && branch.value.longitude
    ? `${branch.value.latitude},${branch.value.longitude}`
    : `${branch.value.address_line}, ${branch.value.city}`
  return `https://www.google.com/maps?q=${encodeURIComponent(query)}&output=embed`
})

const selectedDay = ref(0)

// Compute list of days from showtimes
const days = computed(() => {
  if (!branch.value || !branch.value.showtimes) return []
  
  const mappedShowtimes = branch.value.showtimes.map(mapBackendShowtimeToFrontend)
  const dateSet = new Set<string>()
  mappedShowtimes.forEach(st => {
    if (st.date) dateSet.add(st.date)
  })

  // Nếu API chưa có dữ liệu ngày, phát sinh tự động 14 ngày bắt đầu từ HÔM NAY
  if (dateSet.size === 0) {
    const today = new Date()
    for (let i = 0; i < 14; i++) {
      const d = new Date(today)
      d.setDate(today.getDate() + i)
      const yyyy = d.getFullYear()
      const mm = String(d.getMonth() + 1).padStart(2, '0')
      const dd = String(d.getDate()).padStart(2, '0')
      dateSet.add(`${yyyy}-${mm}-${dd}`)
    }
  }

  const sortedDates = Array.from(dateSet).sort()
  const todayStr = new Date().toISOString().split('T')[0]

  return sortedDates.map((dateStr) => {
    const parts = dateStr.split("-").map(Number)
    const dateObj = new Date(parts[0], parts[1] - 1, parts[2])

    const dayOfWeekNames = ["Chủ Nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
    const dayOfWeek = dayOfWeekNames[dateObj.getDay()]
    const dayNum = String(parts[2]).padStart(2, '0')
    const monthNum = String(parts[1]).padStart(2, '0')
    const isToday = dateStr === todayStr

    return {
      dayOfWeek: isToday ? "Hôm nay" : dayOfWeek,
      dateNum: dayNum,
      monthLabel: `Thg ${monthNum}`,
      fullDate: dateStr,
      isToday
    }
  })
})

// Group showtimes by movie, filtered by selected date
const groupedMovies = computed(() => {
  if (!branch.value || !branch.value.showtimes) return []
  
  const mappedShowtimes = branch.value.showtimes.map(mapBackendShowtimeToFrontend)
  const selectedDateStr = days.value[selectedDay.value]?.fullDate || ''
  
  const filteredSts = selectedDateStr
    ? mappedShowtimes.filter(st => st.date === selectedDateStr)
    : mappedShowtimes
  
  // Group by movieId
  const map = new Map<string, typeof filteredSts>()
  filteredSts.forEach(st => {
    const list = map.get(st.movieId) || []
    list.push(st)
    map.set(st.movieId, list)
  })
  
  const result: { movie: any; showtimes: typeof filteredSts }[] = []
  map.forEach((sts, movieId) => {
    const movie = branch.value?.movies.find(m => String(m.id) === movieId)
    if (movie) {
      sts.sort((a, b) => `${a.date}T${a.time}`.localeCompare(`${b.date}T${b.time}`))
      result.push({ movie, showtimes: sts })
    }
  })
  
  return result
})

// Pagination
const currentPage = ref(1)
const pageSize = 4

const paginatedMovies = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return groupedMovies.value.slice(start, start + pageSize)
})

const totalPages = computed(() => Math.ceil(groupedMovies.value.length / pageSize))

watch(branch, () => {
  currentPage.value = 1
  selectedDay.value = 0
})

watch(selectedDay, () => {
  currentPage.value = 1
})

function handleSelectShowtime(showtime: any) {
  navigateTo(`/checkout/seat?showtimeId=${showtime.id}`)
}

onMounted(async () => {
  try {
    branch.value = await branchesService.getById(String(route.params.id))
  } catch {
    error.value = 'Không tìm thấy thông tin rạp chiếu.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="mx-auto max-w-7xl px-6 py-10 text-white">
    <p v-if="loading" class="py-20 text-center">Đang tải thông tin rạp...</p>
    <p v-else-if="error" class="py-20 text-center text-red-400">{{ error }}</p>
    <template v-else-if="branch">
      <!-- Cinema Header -->
      <section class="mb-8 rounded-3xl border border-white/10 bg-white/5 p-7">
        <p class="text-sm uppercase tracking-widest text-orange-300">CineAI Cinema</p>
        <h1 class="mt-2 text-4xl font-black">{{ branch.name }}</h1>
        <p class="mt-3 text-gray-300">{{ branch.address_line }}, {{ branch.district }}, {{ branch.city }}</p>
        <p v-if="branch.phone" class="mt-1 text-gray-400">Hotline: {{ branch.phone }}</p>
      </section>

      <!-- Map Embed -->
      <iframe :src="mapUrl" class="mb-10 h-80 w-full rounded-3xl border-0" loading="lazy" title="Bản đồ rạp"></iframe>

      <!-- Phim đang chiếu tại rạp (Grid Poster) -->
      <h2 class="mb-5 text-2xl font-bold">Phim đang chiếu tại rạp</h2>
      <div class="mb-10 grid grid-cols-2 gap-5 md:grid-cols-4 lg:grid-cols-5">
        <NuxtLink v-for="movie in branch.movies" :key="movie.id" :to="getMovieSlugUrl(movie)" class="overflow-hidden rounded-2xl bg-white/5 hover:scale-[1.03] transition-transform duration-200 border border-white/5 hover:border-orange-500/30">
          <img :src="movie.poster" :alt="movie.title" class="aspect-[2/3] w-full object-cover">
          <h3 class="p-3 font-bold text-sm truncate">{{ movie.title }}</h3>
        </NuxtLink>
      </div>

      <!-- Toàn bộ lịch chiếu (Grouped & Paginated) -->
      <h2 class="mb-5 text-2xl font-bold">Toàn bộ lịch chiếu</h2>

      <!-- Horizontal Date Picker Bar (Thanh Chọn Thứ / Ngày) -->
      <div v-if="days && days.length" class="relative mb-8">
        <div class="flex items-center gap-3 overflow-x-auto pb-4 scrollbar-none snap-x">
          <button v-for="(d, i) in days" :key="d.fullDate" @click="selectedDay = i"
            class="flex-none snap-start min-w-[100px] py-3.5 px-4 rounded-2xl border transition-all duration-300 flex flex-col items-center justify-center group relative overflow-hidden"
            :class="selectedDay === i
              ? 'bg-orange-500 border-orange-500 text-white shadow-[0_0_20px_rgba(249,115,22,0.5)] scale-105'
              : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/30 hover:text-white hover:bg-white/10'">
            <!-- Label Thứ / Hôm Nay -->
            <span class="text-[11px] uppercase font-bold tracking-wider mb-1 transition-colors"
              :class="selectedDay === i ? 'text-white' : d.isToday ? 'text-orange-400 font-extrabold' : 'text-gray-400'">
              {{ d.dayOfWeek }}
            </span>

            <!-- Ngày -->
            <span class="text-2xl font-black leading-none">{{ d.dateNum }}</span>

            <!-- Tháng -->
            <span class="text-[10px] opacity-70 mt-1 font-medium">{{ d.monthLabel }}</span>
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="groupedMovies.length === 0" class="py-20 text-center bg-white/5 rounded-3xl border border-white/10">
        <span class="material-symbols-outlined text-5xl text-gray-500 mb-3">movie_off</span>
        <p class="text-gray-300 text-base font-semibold">Rạp chưa có suất chiếu đang mở bán.</p>
      </div>

      <!-- Movie List with Showtimes (Grouped & Styled) -->
      <div v-else class="space-y-8">
        <div v-for="{ movie, showtimes } in paginatedMovies" :key="movie.id"
          class="bg-gradient-to-r from-[#14161d] to-[#0d0e12] border border-white/10 rounded-3xl p-6 md:p-8 hover:border-white/20 transition-all shadow-2xl">
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-[200px_minmax(0,1fr)] lg:gap-8">

            <!-- Left: Movie Poster & Detail -->
            <div class="flex flex-row lg:flex-col gap-5 items-start">
              <img :src="movie.poster || 'https://via.placeholder.com/300x450'" :alt="movie.title"
                class="w-24 sm:w-32 lg:w-[200px] aspect-[2/3] object-cover rounded-2xl shadow-2xl border border-white/10 flex-shrink-0"
                @error="($event.target as HTMLImageElement).src = '/images/movie-placeholder.svg'" />
              <div>
                <NuxtLink :to="getMovieSlugUrl(movie)" class="text-lg md:text-xl font-black text-white leading-tight mb-2 hover:text-orange-500 transition-colors block">
                  {{ movie.title }}
                </NuxtLink>

                <div class="flex flex-wrap items-center gap-2 mb-3">
                  <span v-for="g in (Array.isArray(movie.genre) ? movie.genre.slice(0, 2) : [movie.genre])" :key="g"
                    class="px-2.5 py-0.5 bg-white/10 rounded-md text-[10px] font-semibold text-gray-300">
                    {{ g }}
                  </span>
                  <span class="text-xs text-gray-400 font-medium flex items-center gap-1">
                    <span class="material-symbols-outlined text-sm text-gray-400">schedule</span>
                    {{ movie.duration }} phút
                  </span>
                </div>

                <p class="text-xs text-gray-400 leading-relaxed hidden lg:block font-light">
                  {{ movie.description ? (movie.description.length > 120 ? movie.description.slice(0, 120) + '...' : movie.description) : 'Chưa có mô tả phim.' }}
                </p>
              </div>
            </div>

            <!-- Right: Grouped Showtimes by Date & Screen Type -->
            <div class="min-w-0 space-y-6">
              <!-- Group by Date first, then Screen Type -->
              <template v-for="dateShowtimes in (() => {
                const grouped: Record<string, typeof showtimes> = {}
                showtimes.forEach(st => {
                  if (!grouped[st.date]) grouped[st.date] = []
                  grouped[st.date].push(st)
                })
                return Object.entries(grouped)
              })()" :key="dateShowtimes[0]">
                <div class="bg-black/40 border border-white/5 rounded-2xl p-5 backdrop-blur-sm">
                  <!-- Date Title -->
                  <div class="flex items-center gap-2 mb-4 pb-2 border-b border-white/5">
                    <span class="material-symbols-outlined text-orange-400 text-sm">calendar_month</span>
                    <h4 class="text-sm font-bold text-white tracking-wide">
                      Ngày chiếu: {{ formatDate(dateShowtimes[0]) }}
                    </h4>
                  </div>

                  <!-- Group by Screen Type -->
                  <div class="space-y-4">
                    <template v-for="(groupedByScreen, screenType) in (() => {
                      const byScreen: Record<string, typeof showtimes> = {}
                      dateShowtimes[1].forEach(st => {
                        const type = st.screenName.includes('IMAX') ? 'IMAX 3D' : st.screenName.includes('4DX') ? '4DX' : '2D Phụ Đề'
                        if (!byScreen[type]) byScreen[type] = []
                        byScreen[type].push(st)
                      })
                      return byScreen
                    })()" :key="screenType">
                      <div class="border-t border-white/5 pt-3 first:border-0 first:pt-0">
                        <div class="flex items-center gap-2 mb-3">
                          <span class="px-2 py-0.5 rounded text-[9px] font-black tracking-widest bg-orange-500/20 text-orange-400 border border-orange-500/30 uppercase">
                            {{ screenType }}
                          </span>
                          <span class="text-xs text-gray-400 font-medium">({{ groupedByScreen[0].screenName }})</span>
                        </div>

                        <!-- Time Buttons -->
                        <div class="flex flex-wrap gap-3">
                          <button v-for="st in groupedByScreen" :key="st.id" @click="handleSelectShowtime(st)"
                            class="group relative bg-white/5 hover:bg-orange-500 border border-white/10 hover:border-orange-500 rounded-xl px-4 py-2 transition-all duration-200 text-left hover:scale-105 shadow-md">
                            <span class="block text-xs font-black text-white group-hover:text-white">
                              {{ st.time }}
                            </span>
                            <span class="block text-[9px] text-gray-400 group-hover:text-orange-100 mt-0.5 font-medium">
                              {{ st.price.toLocaleString('vi-VN') }}đ
                            </span>
                          </button>
                        </div>
                      </div>
                    </template>
                  </div>
                </div>
              </template>
            </div>

          </div>
        </div>

        <!-- Pagination Controls -->
        <div v-if="totalPages > 1" class="mt-8 flex justify-center items-center gap-2">
          <button 
            :disabled="currentPage === 1" 
            @click="currentPage--"
            class="px-4 py-2 rounded-xl bg-white/5 hover:bg-orange-500 border border-white/10 disabled:opacity-30 disabled:hover:bg-white/5 transition-all text-xs font-bold"
          >
            Trước
          </button>
          <button 
            v-for="page in totalPages" 
            :key="page"
            @click="currentPage = page"
            class="w-8 h-8 rounded-xl text-xs font-bold transition-all border flex items-center justify-center"
            :class="currentPage === page ? 'bg-orange-500 border-orange-500 text-white' : 'bg-white/5 border-white/10 hover:bg-white/10 text-gray-300'"
          >
            {{ page }}
          </button>
          <button 
            :disabled="currentPage === totalPages" 
            @click="currentPage++"
            class="px-4 py-2 rounded-xl bg-white/5 hover:bg-orange-500 border border-white/10 disabled:opacity-30 disabled:hover:bg-white/5 transition-all text-xs font-bold"
          >
            Sau
          </button>
        </div>
      </div>
    </template>
  </main>
</template>

<style scoped>
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
.scrollbar-none {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

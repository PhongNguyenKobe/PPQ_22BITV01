<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { movieService, type Movie, type Showtime } from "~/services/api"
import { useTicketsStore } from "~/store/tickets"
import { getMovieSlugUrl } from "~/utils/slug"

const ticketsStore = useTicketsStore()

definePageMeta({ layout: "default" })

// State
const movies = ref<Movie[]>([])
const showtimesMap = ref<Record<string, Showtime[]>>({})
const loading = ref(true)
const error = ref("")

const selectedBranch = ref("Tất cả rạp")
const selectedDay = ref(0) // Index của ngày được chọn

// =========================================================================
// 1. TÍNH TOÁN DANH SÁCH NGÀY (CÓ THỨ TRONG TUẦN & TỰ ĐỘNG BỔ SUNG NGÀY)
// =========================================================================
const days = computed(() => {
  // Lấy các ngày duy nhất có từ dữ liệu API
  const dateSet = new Set<string>()
  Object.values(showtimesMap.value).forEach((sts) =>
    sts.forEach((st) => {
      if (st.date) dateSet.add(st.date)
    })
  )

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
    // Parse date an toàn không bị lệch timezone
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

// =========================================================================
// 2. COMPUTED FILTERS & DROPDOWNS
// =========================================================================
const branches = computed(() => {
  const branchSet = new Set<string>()
  Object.values(showtimesMap.value).forEach((sts) =>
    sts.forEach((st) => {
      if (st.branchName) branchSet.add(st.branchName)
    })
  )
  const list = Array.from(branchSet).sort()
  return ["Tất cả rạp", ...list]
})

// Helper format ngày hiển thị đẹp: ví dụ "Thứ 6, 27/07"
function formatVietnameseDate(dateStr: string) {
  if (!dateStr) return ""
  const [y, m, d] = dateStr.split("-").map(Number)
  const date = new Date(y, m - 1, d)
  const days = ["Chủ Nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
  const dayName = days[date.getDay()]
  return `${dayName}, ${String(d).padStart(2, '0')}/${String(m).padStart(2, '0')}`
}

// =========================================================================
// 3. SUẤT CHIẾU NỔI BẬT TỪ DỮ LIỆU ĐANG MỞ BÁN
// =========================================================================
const aiCards = computed(() => {
  const selectedDate = days.value[selectedDay.value]?.fullDate
  const featured = movies.value.filter((m) => m.isFeatured).slice(0, 3)
  return featured.map((movie) => {
    const sts = (showtimesMap.value[movie.id] || []).filter((showtime) =>
      (!selectedDate || showtime.date === selectedDate)
      && (selectedBranch.value === "Tất cả rạp" || showtime.branchName === selectedBranch.value)
    )
    const first = sts[0]
    return {
      badge: "Phim nổi bật",
      movie: movie.title,
      poster: movie.poster || 'https://via.placeholder.com/300x450',
      desc: movie.description?.slice(0, 70) + "..." || "Bộ phim cực HOT không thể bỏ qua.",
      time: first ? `${formatVietnameseDate(first.date)} • ${first.time}` : "Đang cập nhật lịch",
      theater: first?.branchName || "CineAI Cinema",
      movieId: movie.id,
    }
  }).filter(card => card.time !== "Đang cập nhật lịch")
})

// =========================================================================
// 4. FETCH DATA
// =========================================================================
onMounted(async () => {
  try {
    loading.value = true
    const allMovies = await movieService.getPublic()
    movies.value = allMovies

    const showtimePromises = allMovies.map(async (m) => {
      try {
        const sts = await movieService.getShowtimes(m.id)
        return { movieId: m.id, showtimes: sts }
      } catch {
        return { movieId: m.id, showtimes: [] }
      }
    })

    const results = await Promise.all(showtimePromises)
    results.forEach((r) => {
      showtimesMap.value[r.movieId] = r.showtimes
    })
  } catch (e) {
    console.error("Failed to load showtimes page data:", e)
    error.value = "Không thể tải dữ liệu lịch chiếu. Vui lòng thử lại sau."
  } finally {
    loading.value = false
  }
})

// =========================================================================
// 5. LỌC PHIM VÀ SUẤT CHIẾU THEO NGÀY ĐƯỢC CHỌN
// =========================================================================
const filteredShowtimes = computed(() => {
  let movieIds = movies.value.map((m) => m.id)

  // Lấy ngày đang được chọn trên Thanh chọn ngày
  const selectedDateStr = days.value[selectedDay.value]?.fullDate || ""

  const result: { movie: Movie; showtimes: Showtime[] }[] = []

  movieIds.forEach((movieId) => {
    const movie = movies.value.find((m) => m.id === movieId)
    if (!movie) return

    let sts = showtimesMap.value[movieId] || []

    // Lọc theo Rạp
    if (selectedBranch.value !== "Tất cả rạp") {
      sts = sts.filter((st) => st.branchName === selectedBranch.value)
    }

    // Lọc theo Ngày chọn
    if (selectedDateStr) {
      sts = sts.filter((st) => st.date === selectedDateStr)
    }

    // Chỉ đưa phim vào danh sách hiển thị nếu có suất chiếu thỏa mãn
    if (sts.length > 0) {
      result.push({ movie, showtimes: sts })
    }
  })

  return result
})

function handleSelectShowtime(movie: any, showtime: Showtime) {
  ticketsStore.selectMovie({
    id: movie.id,
    name: movie.title,
    title: movie.title,
    imageUrl: movie.poster,
    category: movie.category,
    rating: movie.rating,
    price: showtime.price / 1000,
    backendMovieId: movie.id,
  })
  ticketsStore.selectCinema(showtime.branchName)
  ticketsStore.selectShowtime(showtime)
  navigateTo('/checkout/seat')
}
</script>

<template>
  <div class="min-h-screen bg-[#0b0c10] text-gray-100 pt-20 pb-24 selection:bg-red-600 selection:text-white">

    <!-- Loading State -->
    <div v-if="loading" class="min-h-[60vh] flex flex-col items-center justify-center gap-4">
      <div class="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-400 font-medium animate-pulse">Đang tối ưu lịch chiếu cho bạn...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="min-h-[50vh] flex flex-col items-center justify-center text-center px-4">
      <span class="material-symbols-outlined text-6xl text-red-500 mb-2">error</span>
      <p class="text-lg font-bold text-red-400">{{ error }}</p>
    </div>

    <template v-else>

      <!-- 1. HEADER & THANH CHỌN NGÀY / BỘ LỌC -->
      <section
        class="relative border-b border-white/10 bg-gradient-to-b from-black/80 via-black/40 to-[#0b0c10] backdrop-blur-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div>
              <span class="text-xs font-bold text-red-500 tracking-widest uppercase">CineAI Showtimes</span>
              <h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Lịch Chiếu Phim</h1>
            </div>

            <!-- Fast Filters Dropdowns -->
            <div class="flex flex-wrap items-center gap-3">
              <!-- Branch Select -->
              <div class="relative min-w-[180px]">
                <label for="showtimes-branch" class="sr-only">Chọn rạp đang có suất mở bán</label>
                <select id="showtimes-branch" v-model="selectedBranch"
                  class="w-full bg-white/5 border border-white/10 text-xs font-semibold text-white rounded-xl py-3 pl-4 pr-10 appearance-none focus:outline-none focus:border-red-500 hover:bg-white/10 transition-all cursor-pointer">
                  <option v-for="b in branches" :key="b" class="bg-gray-900 text-white">
                    {{ b === 'Tất cả rạp' ? 'Toàn bộ rạp đang mở bán' : b }}
                  </option>
                </select>
                <span
                  class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none text-sm">expand_more</span>
              </div>

            </div>
          </div>

          <p class="-mt-5 mb-7 text-xs text-gray-500 md:text-right">
            Danh sách chỉ gồm chi nhánh có suất tương lai, trạng thái mở bán và còn thời gian đặt vé.
            <span v-if="branches.length === 2" class="text-red-300">
              Hiện chỉ có {{ branches[1] }} đáp ứng điều kiện.
            </span>
          </p>

          <!-- Horizontal Date Picker Bar (Thanh Chọn Thứ / Ngày) -->
          <div class="relative">
            <div class="flex items-center gap-3 overflow-x-auto pb-4 scrollbar-none snap-x">
              <button v-for="(d, i) in days" :key="d.fullDate" @click="selectedDay = i"
                class="flex-none snap-start min-w-[100px] py-3.5 px-4 rounded-2xl border transition-all duration-300 flex flex-col items-center justify-center group relative overflow-hidden"
                :class="selectedDay === i
                  ? 'bg-red-600 border-red-500 text-white shadow-[0_0_20px_rgba(229,9,20,0.5)] scale-105'
                  : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/30 hover:text-white hover:bg-white/10'">
                <!-- Label Thứ / Hôm Nay -->
                <span class="text-[11px] uppercase font-bold tracking-wider mb-1 transition-colors"
                  :class="selectedDay === i ? 'text-white' : d.isToday ? 'text-red-400 font-extrabold' : 'text-gray-400'">
                  {{ d.dayOfWeek }}
                </span>

                <!-- Ngày -->
                <span class="text-2xl font-black leading-none">{{ d.dateNum }}</span>

                <!-- Tháng -->
                <span class="text-[10px] opacity-70 mt-1 font-medium">{{ d.monthLabel }}</span>
              </button>
            </div>
          </div>

        </div>
      </section>

      <!-- 2. FEATURED SHOWTIMES FROM LIVE DATA -->
      <section v-if="aiCards.length > 0" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="flex items-center gap-2 mb-6">
          <span class="material-symbols-outlined text-red-500 animate-pulse">auto_awesome</span>
          <h2 class="text-lg font-bold text-white tracking-wide uppercase">Suất Chiếu Nổi Bật</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="c in aiCards" :key="c.movie"
            class="group relative bg-gradient-to-br from-white/10 via-white/5 to-transparent border border-white/10 hover:border-red-500/50 rounded-2xl p-4 transition-all duration-300 hover:-translate-y-1 flex gap-4 backdrop-blur-md overflow-hidden">
            <img :src="c.poster" :alt="c.movie"
              class="w-20 h-28 object-cover rounded-xl shadow-lg border border-white/10 group-hover:scale-105 transition-transform duration-300" />

            <div class="flex-1 flex flex-col justify-between">
              <div>
                <span
                  class="text-[9px] font-extrabold bg-red-600/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded-full uppercase tracking-wider inline-block mb-1.5">
                  {{ c.badge }}
                </span>
                <h3 class="font-bold text-sm text-white line-clamp-1 group-hover:text-red-400 transition-colors">
                  {{ c.movie }}
                </h3>
                <p class="text-xs text-gray-400 mt-1 line-clamp-2 leading-relaxed font-light">{{ c.desc }}</p>
              </div>

              <div class="flex items-center justify-between mt-3 pt-2 border-t border-white/5">
                <div class="text-[11px] text-gray-300 font-medium truncate">
                  <p class="text-red-400 font-bold truncate">{{ c.theater }}</p>
                  <p class="text-[10px] text-gray-400">{{ c.time }}</p>
                </div>
                <NuxtLink :to="getMovieSlugUrl({ id: c.movieId, title: c.movie })"
                  class="w-8 h-8 rounded-full bg-white/10 hover:bg-red-600 text-white flex items-center justify-center transition-colors">
                  <span class="material-symbols-outlined text-sm">arrow_forward</span>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 3. MAIN SHOWTIMES LIST (DANH SÁCH CHI TIẾT THEO NGÀY CHỌN) -->
      <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

        <!-- Banner thông báo ngày đang chọn -->
        <div class="flex items-center justify-between mb-6 pb-2 border-b border-white/10">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-red-500">calendar_month</span>
            <span class="text-sm font-bold text-gray-300">
              Lịch chiếu ngày: <strong class="text-white text-base ml-1">{{
                formatVietnameseDate(days[selectedDay]?.fullDate) }}</strong>
            </span>
          </div>
          <span class="text-xs text-gray-400">Tìm thấy {{ filteredShowtimes.length }} phim có suất chiếu</span>
        </div>

        <!-- Empty Filter Result -->
        <div v-if="filteredShowtimes.length === 0"
          class="py-20 text-center bg-white/5 rounded-3xl border border-white/10">
          <span class="material-symbols-outlined text-5xl text-gray-500 mb-3">movie_off</span>
          <p class="text-gray-300 text-base font-semibold">Rất tiếc, không có phim nào chiếu vào {{
            formatVietnameseDate(days[selectedDay]?.fullDate) }}.</p>
          <p class="text-gray-500 text-xs mt-1">Vui lòng chọn ngày khác hoặc đổi rạp chiếu!</p>
        </div>

        <!-- Movie List with Showtimes -->
        <div v-else class="space-y-8">
          <div v-for="{ movie, showtimes } in filteredShowtimes" :key="movie.id"
            class="bg-gradient-to-r from-[#14161d] to-[#0d0e12] border border-white/10 rounded-3xl p-6 md:p-8 hover:border-white/20 transition-all shadow-2xl">
            <div class="grid grid-cols-1 gap-6 lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-8">

              <!-- Left: Movie Poster & Detail -->
              <div class="flex flex-row lg:flex-col gap-5 items-start">
                <img :src="movie.poster || 'https://via.placeholder.com/300x450'" :alt="movie.title"
                  class="w-28 sm:w-36 lg:w-[220px] aspect-[2/3] object-cover rounded-2xl shadow-2xl border border-white/10 flex-shrink-0"
                  @error="($event.target as HTMLImageElement).src = '/images/movie-placeholder.svg'" />
                <div>
                  <h2
                    class="text-xl md:text-2xl font-black text-white leading-tight mb-2 hover:text-red-500 transition-colors cursor-pointer">
                    {{ movie.title }}
                  </h2>

                  <div class="flex flex-wrap items-center gap-2 mb-3">
                    <span v-for="g in (Array.isArray(movie.genre) ? movie.genre.slice(0, 2) : [movie.genre])" :key="g"
                      class="px-2.5 py-0.5 bg-white/10 rounded-md text-[11px] font-semibold text-gray-300">
                      {{ g }}
                    </span>
                    <span class="text-xs text-gray-400 font-medium flex items-center gap-1">
                      <span class="material-symbols-outlined text-sm text-gray-400">schedule</span>
                      {{ movie.duration }} phút
                    </span>
                  </div>

                  <p class="text-xs text-gray-400 leading-relaxed hidden lg:block font-light line-clamp-2">
                    {{ movie.description || '' }}
                  </p>
                </div>
              </div>

              <!-- Right: Grouped Showtimes by Branch -->
              <div class="min-w-0 space-y-6">
                <template v-for="branchShowtimes in (() => {
                  const grouped: Record<string, Showtime[]> = {}
                  showtimes.forEach(st => {
                    if (!grouped[st.branchName]) grouped[st.branchName] = []
                    grouped[st.branchName].push(st)
                  })
                  return Object.entries(grouped)
                })()" :key="branchShowtimes[0]">
                  <div class="bg-black/40 border border-white/5 rounded-2xl p-5 md:p-6 backdrop-blur-sm">
                    <!-- Branch Title -->
                    <div class="flex items-center gap-2 mb-4">
                      <span class="material-symbols-outlined text-red-500">location_on</span>
                      <h3 class="text-base font-bold text-white tracking-wide">{{ branchShowtimes[0] }}</h3>
                    </div>

                    <!-- Group by screen type (IMAX, 4DX, 2D...) -->
                    <div class="space-y-4">
                      <template v-for="(groupedByScreen, screenType) in (() => {
                        const byScreen: Record<string, Showtime[]> = {}
                        branchShowtimes[1].forEach(st => {
                          const type = st.screenName.includes('IMAX') ? 'IMAX 3D' : st.screenName.includes('4DX') ? '4DX' : '2D Phụ Đề'
                          if (!byScreen[type]) byScreen[type] = []
                          byScreen[type].push(st)
                        })
                        return byScreen
                      })()" :key="screenType">
                        <div class="border-t border-white/5 pt-3 first:border-0 first:pt-0">
                          <div class="flex items-center gap-2 mb-3">
                            <span
                              class="px-2 py-0.5 rounded text-[10px] font-black tracking-widest bg-red-600/20 text-red-400 border border-red-500/30 uppercase">
                              {{ screenType }}
                            </span>
                            <span class="text-xs text-gray-400 font-medium">({{ groupedByScreen[0].screenName }})</span>
                          </div>

                          <!-- Time Buttons -->
                          <div class="flex flex-wrap gap-3">
                            <button v-for="st in groupedByScreen" :key="st.id" @click="handleSelectShowtime(movie, st)"
                              class="group relative bg-white/5 hover:bg-red-600 border border-white/10 hover:border-red-500 rounded-xl px-4 py-2.5 transition-all duration-200 text-left hover:scale-105 shadow-md">
                              <span class="block text-sm font-black text-white group-hover:text-white">
                                {{ st.time }}
                              </span>
                              <span class="block text-[10px] text-gray-400 group-hover:text-red-100 mt-0.5 font-medium">
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
        </div>

      </section>

    </template>
  </div>
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

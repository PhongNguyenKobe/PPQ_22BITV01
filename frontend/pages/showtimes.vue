<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { movieService, type Movie, type Showtime } from "~/services/api"

definePageMeta({ layout: "default" })

// State
const movies = ref<Movie[]>([])
const showtimesMap = ref<Record<string, Showtime[]>>({})
const loading = ref(true)
const error = ref("")

const selectedBranch = ref("Tất cả rạp")
const selectedMovie = ref("Tất cả phim")
const selectedDay = ref(0)

// Computed: unique branches from all showtimes
const branches = computed(() => {
  const branchSet = new Set<string>()
  Object.values(showtimesMap.value).forEach((sts) =>
    sts.forEach((st) => branchSet.add(st.branchName))
  )
  const list = Array.from(branchSet).sort()
  return ["Tất cả rạp", ...list]
})

// Computed: unique movie titles
const movieTitles = computed(() => {
  return ["Tất cả phim", ...movies.value.map((m) => m.title)]
})

// Computed: available days (next 7 days from showtimes dates)
const availableDays = computed(() => {
  const dateSet = new Set<string>()
  Object.values(showtimesMap.value).forEach((sts) =>
    sts.forEach((st) => dateSet.add(st.date))
  )
  return Array.from(dateSet).sort()
})

const days = computed(() => {
  return availableDays.value.map((dateStr) => {
    const [y, m, d] = dateStr.split("-").map(Number)
    const date = new Date(y, m - 1, d)
    const dayOfWeek = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"][date.getDay()]
    return { label: dayOfWeek, date: d, fullDate: dateStr }
  })
})

// AI recommendation cards
const aiCards = computed(() => {
  // Pick featured movies with their first showtime
  const featured = movies.value.filter((m) => m.isFeatured).slice(0, 3)
  return featured.map((movie) => {
    const sts = showtimesMap.value[movie.id] || []
    const first = sts[0]
    return {
      badge: "Phim nổi bật",
      badgeColor: "bg-primary-container/10 text-primary-container",
      match: "AI",
      movie: movie.title,
      desc: movie.description?.slice(0, 80) + "..." || "Phim hot nhất hệ thống CineAI.",
      time: first ? `${first.date}, ${first.time}` : "Sắp chiếu",
      theater: first?.branchName || "CineAI",
      movieId: movie.id,
    }
  })
})

// Fetch data
onMounted(async () => {
  try {
    loading.value = true
    const allMovies = await movieService.getAll()
    movies.value = allMovies

    // Fetch showtimes for all movies in parallel
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
    error.value = "Không thể tải dữ liệu lịch chiếu."
  } finally {
    loading.value = false
  }
})

// Filtered showtimes based on user selection
const filteredShowtimes = computed(() => {
  // Determine selected movie IDs
  let movieIds = movies.value.map((m) => m.id)
  if (selectedMovie.value !== "Tất cả phim") {
    const found = movies.value.find((m) => m.title === selectedMovie.value)
    if (found) movieIds = [found.id]
    else return []
  }

  // Determine selected date
  let selectedDate = ""
  if (days.value.length > 0) {
    selectedDate = days.value[selectedDay.value]?.fullDate || ""
  }

  const result: { movie: Movie; showtimes: Showtime[] }[] = []

  movieIds.forEach((movieId) => {
    const movie = movies.value.find((m) => m.id === movieId)
    if (!movie) return

    let sts = showtimesMap.value[movieId] || []

    // Filter by branch
    if (selectedBranch.value !== "Tất cả rạp") {
      sts = sts.filter((st) => st.branchName === selectedBranch.value)
    }

    // Filter by date
    if (selectedDate) {
      sts = sts.filter((st) => st.date === selectedDate)
    }

    if (sts.length > 0) {
      result.push({ movie, showtimes: sts })
    }
  })

  return result
})

// Select showtime button handler
function handleSelectShowtime(showtime: Showtime) {
  navigateTo(`/checkout/seat`)
}
</script>

<template>
  <div class="min-h-screen pt-20">
    <!-- Loading -->
    <div v-if="loading" class="py-24 text-center animate-pulse text-on-surface-variant">
      Đang tải lịch chiếu...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="py-24 text-center text-red-500">
      {{ error }}
    </div>

    <template v-else>
      <!-- Hero Filter -->
      <section class="relative pt-12 pb-8 px-6 md:px-margin-desktop bg-gradient-to-b from-surface-container-lowest to-surface">
        <div class="max-w-container-max mx-auto">
          <h1 class="font-headline-xl text-headline-xl mb-10 text-on-surface">Lịch Chiếu</h1>

          <!-- Filters Panel -->
          <div class="flex flex-col md:flex-row items-start md:items-center gap-6 p-6 rounded-2xl mb-8" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
            <!-- Theater Filter -->
            <div class="w-full md:w-1/4">
              <label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1">Chọn Rạp</label>
              <div class="relative">
                <select v-model="selectedBranch" class="w-full bg-surface-container-high border-white/10 text-on-surface rounded-lg py-3 px-4 appearance-none focus:ring-primary-container focus:border-primary-container font-label-md text-label-md cursor-pointer outline-none border border-white/10">
                  <option v-for="b in branches" :key="b">{{ b }}</option>
                </select>
                <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
              </div>
            </div>

            <!-- Movie Filter -->
            <div class="w-full md:w-1/4">
              <label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1">Chọn Phim</label>
              <div class="relative">
                <select v-model="selectedMovie" class="w-full bg-surface-container-high border-white/10 text-on-surface rounded-lg py-3 px-4 appearance-none focus:ring-primary-container focus:border-primary-container font-label-md text-label-md cursor-pointer outline-none border border-white/10">
                  <option v-for="title in movieTitles" :key="title">{{ title }}</option>
                </select>
                <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
              </div>
            </div>

            <!-- Date Timeline -->
            <div class="w-full md:w-2/4">
              <label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1">Chọn Ngày</label>
              <div class="flex gap-3 overflow-x-auto pb-2" style="scrollbar-width:none">
                <button
                  v-for="(d, i) in days" :key="i"
                  @click="selectedDay = i"
                  class="flex-shrink-0 flex flex-col items-center justify-center min-w-[70px] h-[70px] rounded-xl transition-all"
                  :class="selectedDay === i ? 'bg-primary-container text-white shadow-[0_0_20px_-5px_rgba(229,9,20,0.3)]' : 'bg-surface-container-high border border-white/5 hover:border-primary-container text-on-surface'"
                >
                  <span class="text-label-sm font-label-sm opacity-80">{{ d.label }}</span>
                  <span class="text-headline-md font-bold">{{ d.date }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- AI Recommendations -->
      <section v-if="aiCards.length > 0" class="px-6 md:px-margin-desktop py-12">
        <div class="max-w-container-max mx-auto">
          <div class="flex items-center gap-3 mb-8">
            <span class="material-symbols-outlined text-primary-container text-[32px]" style="font-variation-settings:'FILL' 1">psychology</span>
            <h2 class="font-headline-lg text-headline-lg text-on-surface">Gợi ý suất chiếu</h2>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div v-for="c in aiCards" :key="c.movie" class="overflow-hidden rounded-xl" style="position:relative;background:rgba(31,31,31,0.8);border-radius:12px;padding:1px">
              <div class="absolute inset-0 rounded-xl" style="padding:1.5px;background:linear-gradient(45deg,#e50914,#8a2be2,#e50914);background-size:200% 200%;animation:gradient-move 4s linear infinite;-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);-webkit-mask-composite:xor;mask-composite:exclude"></div>
              <div class="p-6 rounded-[11px] flex flex-col justify-between h-full" style="background:#1e2020">
                <div>
                  <div class="flex justify-between items-start mb-4">
                    <div :class="c.badgeColor" class="px-3 py-1 rounded-full text-label-sm font-bold uppercase tracking-wider">{{ c.badge }}</div>
                    <span class="text-on-surface-variant text-label-sm">Đề xuất</span>
                  </div>
                  <h3 class="font-headline-md text-headline-md text-on-surface mb-2">{{ c.movie }}</h3>
                  <p class="text-on-surface-variant font-body-md mb-6">{{ c.desc }}</p>
                </div>
                <div class="flex items-center justify-between">
                  <div class="flex flex-col">
                    <span class="text-label-sm text-on-surface-variant">{{ c.time }}</span>
                    <span class="text-label-md font-bold text-on-surface">{{ c.theater }}</span>
                  </div>
                  <NuxtLink :to="`/movies/${c.movieId}`" class="bg-primary-container text-on-primary-container p-3 rounded-full hover:scale-110 transition-transform">
                    <span class="material-symbols-outlined">confirmation_number</span>
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Showtimes List -->
      <section class="px-6 md:px-margin-desktop py-12 pb-24">
        <div class="max-w-container-max mx-auto">
          <div class="flex justify-between items-end mb-10 border-b border-white/10 pb-4">
            <h2 class="font-headline-lg text-headline-lg text-on-surface">Danh Sách Rạp & Suất Chiếu</h2>
          </div>

          <div v-if="filteredShowtimes.length === 0" class="py-12 text-center text-on-surface-variant">
            Không có suất chiếu nào phù hợp.
          </div>

          <div v-else class="space-y-12">
            <!-- Each movie block -->
            <div v-for="{ movie, showtimes } in filteredShowtimes" :key="movie.id" class="flex flex-col lg:flex-row gap-8">
              <div class="lg:w-1/3">
                <div class="sticky top-24">
                  <h3 class="font-headline-md text-headline-md text-on-surface mb-2">{{ movie.title }}</h3>
                  <div class="flex gap-3">
                    <span v-for="g in movie.genre.slice(0, 3)" :key="g" class="px-3 py-1 bg-surface-container-high rounded-full text-label-sm font-label-sm border border-white/5">{{ g }}</span>
                  </div>
                  <p class="text-on-surface-variant text-body-md mt-3">{{ movie.duration }} phút</p>
                </div>
              </div>
              <div class="lg:w-2/3 space-y-8">
                <!-- Group showtimes by branch -->
                <template v-for="branchShowtimes in (() => {
                  const grouped: Record<string, Showtime[]> = {}
                  showtimes.forEach(st => {
                    if (!grouped[st.branchName]) grouped[st.branchName] = []
                    grouped[st.branchName].push(st)
                  })
                  return Object.entries(grouped)
                })()" :key="branchShowtimes[0]">
                  <div class="p-6 rounded-2xl flex flex-col sm:flex-row gap-6" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
                    <div class="flex-grow">
                      <h4 class="font-headline-md text-headline-md text-on-surface mb-4">{{ branchShowtimes[0] }}</h4>
                      <!-- Group by screen type -->
                      <template v-for="(groupedByScreen, screenType) in (() => {
                        const byScreen: Record<string, Showtime[]> = {}
                        branchShowtimes[1].forEach(st => {
                          const type = st.screenName.includes('IMAX') ? 'IMAX' : st.screenName.includes('4DX') ? '4DX' : '2D'
                          if (!byScreen[type]) byScreen[type] = []
                          byScreen[type].push(st)
                        })
                        return byScreen
                      })()" :key="screenType">
                        <div class="mb-4">
                          <p class="text-label-sm font-label-sm text-primary-container mb-3 uppercase tracking-tighter font-bold">{{ screenType }} - {{ branchShowtimes[1][0].screenName }}</p>
                          <div class="flex flex-wrap gap-3">
                            <button
                              v-for="st in groupedByScreen"
                              :key="st.id"
                              @click="handleSelectShowtime(st)"
                              class="px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 hover:border-primary-container hover:bg-primary-container/10 transition-all font-label-md text-label-md text-on-surface"
                            >
                              {{ st.time }}
                              <span class="block text-[10px] text-on-surface-variant">{{ st.price.toLocaleString('vi-VN') }}đ</span>
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
@keyframes gradient-move {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
</style>


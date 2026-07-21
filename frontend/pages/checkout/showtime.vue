<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { mockShowtimes, type Showtime } from '~/services/api'

definePageMeta({
  layout: 'default'
})

const router = useRouter()
const ticketsStore = useTicketsStore()
const { selectedMovie, selectedCinema, selectedShowtime } = storeToRefs(ticketsStore)

// Redirect if no movie/cinema selected
onMounted(() => {
  if (!selectedMovie.value || !selectedCinema.value) {
    return router.push('/products')
  }
})

// Get showtimes for selected movie + cinema, grouped by date
const showtimesByDate = computed(() => {
  // Map TMDB movie ID to mock movieId (1-5)
  const mockMovieId = String((selectedMovie.value!.id % 5) + 1)
  
  const filtered = mockShowtimes.filter(
    st => st.movieId === mockMovieId &&
          st.branchName === selectedCinema.value
  )

  // Group by date
  const grouped: { [key: string]: Showtime[] } = {}
  filtered.forEach(st => {
    if (!grouped[st.date]) {
      grouped[st.date] = []
    }
    grouped[st.date].push(st)
  })

  // Sort dates
  return Object.keys(grouped)
    .sort()
    .reduce((acc, date) => {
      acc[date] = grouped[date].sort((a, b) => a.time.localeCompare(b.time))
      return acc
    }, {} as { [key: string]: Showtime[] })
})

// Format date for display
const formatDate = (dateStr: string) => {
  const [year, month, day] = dateStr.split('-')
  const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
  const dayOfWeek = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'][date.getDay()]
  return `${dayOfWeek} ${day}/${month}`
}

// Get screen type from screenName
const getScreenType = (screenName: string) => {
  if (screenName.includes('IMAX')) return 'IMAX'
  if (screenName.includes('4DX')) return '4DX'
  if (screenName.includes('3D')) return '3D'
  return '2D'
}

// Select showtime and navigate
function handleSelectShowtime(showtime: Showtime) {
  ticketsStore.selectShowtime(showtime)
  router.push('/checkout/seat')
}
</script>

<template>
  <section class="py-16 max-w-container-max mx-auto px-6 md:px-margin-desktop">
    <!-- Breadcrumb -->
    <div class="mb-8 flex items-center gap-2 text-sm text-on-surface-variant overflow-auto">
      <NuxtLink to="/products" class="hover:text-primary whitespace-nowrap">Sản phẩm</NuxtLink>
      <span class="material-symbols-outlined text-base shrink-0">chevron_right</span>
      <span class="hover:text-primary cursor-pointer whitespace-nowrap" @click="$router.back()">
        {{ selectedMovie?.name }}
      </span>
      <span class="material-symbols-outlined text-base shrink-0">chevron_right</span>
      <span class="hover:text-primary cursor-pointer whitespace-nowrap" @click="$router.back()">
        {{ selectedCinema }}
      </span>
      <span class="material-symbols-outlined text-base shrink-0">chevron_right</span>
      <span class="text-on-surface whitespace-nowrap">Chọn Suất</span>
    </div>

    <!-- Header -->
    <div class="mb-12">
      <h1 class="text-3xl md:text-4xl font-bold text-on-surface mb-2">
        Chọn Suất Chiếu
      </h1>
      <p class="text-on-surface-variant">
        <span class="font-semibold">{{ selectedMovie?.name }}</span>
        tại <span class="font-semibold">{{ selectedCinema }}</span>
      </p>
    </div>

    <!-- Stepper indicator -->
    <div class="mb-12 flex items-center justify-center gap-3 text-xs font-bold">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">1</div>
        <span>Chọn Rạp</span>
      </div>
      <div class="w-8 h-0.5 bg-surface-container-highest"></div>
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center">2</div>
        <span>Chọn Suất</span>
      </div>
      <div class="w-8 h-0.5 bg-surface-container-highest"></div>
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">3</div>
        <span>Chọn Ghế</span>
      </div>
      <div class="w-8 h-0.5 bg-surface-container-highest"></div>
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">4</div>
        <span>Thanh Toán</span>
      </div>
    </div>

    <!-- Showtimes by date -->
    <div class="space-y-8">
      <div v-for="(showtimes, date) in showtimesByDate" :key="date">
        <!-- Date header -->
        <div class="mb-4">
          <h3 class="text-lg font-bold text-on-surface">
            {{ formatDate(date) }}
          </h3>
        </div>

        <!-- Showtimes grid -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <button
            v-for="showtime in showtimes"
            :key="showtime.id"
            @click="handleSelectShowtime(showtime)"
            :class="[
              'group relative overflow-hidden rounded-xl p-4 border-2 transition-all duration-300 text-left',
              selectedShowtime?.id === showtime.id
                ? 'border-primary bg-primary-container/10'
                : 'border-outline-variant bg-surface-container-high hover:border-primary/50 hover:bg-surface-container-highest'
            ]"
          >
            <!-- Background -->
            <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

            <!-- Content -->
            <div class="relative z-10 space-y-3">
              <!-- Time (largest) -->
              <div class="flex items-baseline justify-between">
                <span class="text-2xl font-black text-on-surface">
                  {{ showtime.time }}
                </span>
                <span v-if="selectedShowtime?.id === showtime.id" class="material-symbols-outlined text-primary">
                  check_circle
                </span>
              </div>

              <!-- Screen type -->
              <div class="flex items-center gap-1">
                <span class="px-2 py-1 bg-primary-container/20 text-primary text-xs font-bold rounded">
                  {{ getScreenType(showtime.screenName) }}
                </span>
              </div>

              <!-- Screen name -->
              <p class="text-xs text-on-surface-variant line-clamp-1">
                {{ showtime.screenName }}
              </p>

              <!-- Price -->
              <div class="pt-2 border-t border-outline-variant">
                <p class="text-sm font-bold text-primary">
                  {{ showtime.price.toLocaleString('vi-VN') }}đ
                </p>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- No showtimes -->
    <div v-if="Object.keys(showtimesByDate).length === 0" class="py-12 text-center">
      <p class="text-on-surface-variant mb-4">Không có suất chiếu nào khả dụng</p>
      <button
        @click="$router.back()"
        class="inline-block px-6 py-3 rounded-lg bg-surface-container-high border border-outline-variant text-on-surface font-bold hover:bg-surface-container-highest transition"
      >
        ← Chọn rạp khác
      </button>
    </div>
  </section>
</template>

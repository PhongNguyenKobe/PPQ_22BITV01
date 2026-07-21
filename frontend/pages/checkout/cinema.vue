<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { mockShowtimes } from '~/services/api'

definePageMeta({
  layout: 'default'
})

const router = useRouter()
const ticketsStore = useTicketsStore()
const { selectedMovie, selectedCinema } = storeToRefs(ticketsStore)

// Redirect if no movie selected
onMounted(() => {
  if (!selectedMovie.value) {
    return router.push('/products')
  }
})

// Get available cinemas for selected movie
const availableCinemas = computed(() => {
  if (!selectedMovie.value) return []
  
  // Map TMDB movie ID to mock movieId (1-5)
  const mockMovieId = String((selectedMovie.value.id % 5) + 1)
  
  const showtimesForMovie = mockShowtimes.filter(
    st => st.movieId === mockMovieId
  )
  
  // Get unique cinema names
  const cinemaSet = new Set<string>()
  showtimesForMovie.forEach(st => cinemaSet.add(st.branchName))
  
  return Array.from(cinemaSet).sort()
})

// Show count of showtimes per cinema
const getShowtimeCount = (cinema: string) => {
  const mockMovieId = String((selectedMovie.value!.id % 5) + 1)
  return mockShowtimes.filter(
    st => st.branchName === cinema && st.movieId === mockMovieId
  ).length
}

// Select cinema and navigate to showtime
function handleSelectCinema(cinema: string) {
  ticketsStore.selectCinema(cinema)
  router.push('/checkout/showtime')
}
</script>

<template>
  <section class="py-16 max-w-container-max mx-auto px-6 md:px-margin-desktop">
    <!-- Breadcrumb -->
    <div class="mb-8 flex items-center gap-2 text-sm text-on-surface-variant">
      <NuxtLink to="/products" class="hover:text-primary">Sản phẩm</NuxtLink>
      <span class="material-symbols-outlined text-base">chevron_right</span>
      <span v-if="selectedMovie" class="hover:text-primary cursor-pointer" @click="$router.back()">
        {{ selectedMovie.name }}
      </span>
      <span class="material-symbols-outlined text-base">chevron_right</span>
      <span class="text-on-surface">Chọn Rạp</span>
    </div>

    <!-- Header -->
    <div class="mb-12">
      <h1 class="text-3xl md:text-4xl font-bold text-on-surface mb-2">
        Chọn Rạp Chiếu
      </h1>
      <p class="text-on-surface-variant">
        <span v-if="selectedMovie" class="font-semibold">{{ selectedMovie.name }}</span>
        <span v-else>Phim</span>
        có sẵn tại các rạp dưới đây
      </p>
    </div>

    <!-- Stepper indicator -->
    <div class="mb-12 flex items-center justify-center gap-3 text-xs font-bold">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center">1</div>
        <span>Chọn Rạp</span>
      </div>
      <div class="w-8 h-0.5 bg-surface-container-highest"></div>
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">2</div>
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

    <!-- Cinema list -->
    <div v-if="availableCinemas.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <button
        v-for="cinema in availableCinemas"
        :key="cinema"
        @click="handleSelectCinema(cinema)"
        :class="[
          'group relative overflow-hidden rounded-2xl p-6 text-left border-2 transition-all duration-300',
          selectedCinema === cinema
            ? 'border-primary bg-primary-container/10'
            : 'border-outline-variant bg-surface-container-high hover:border-primary/50'
        ]"
      >
        <!-- Background gradient -->
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

        <!-- Content -->
        <div class="relative z-10">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="text-lg font-bold text-on-surface">{{ cinema }}</h3>
              <p class="text-sm text-on-surface-variant mt-1">
                <span class="material-symbols-outlined text-sm align-text-bottom">schedule</span>
                {{ getShowtimeCount(cinema) }} suất chiếu
              </p>
            </div>
            <div
              :class="[
                'w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all',
                selectedCinema === cinema
                  ? 'border-primary bg-primary'
                  : 'border-outline-variant group-hover:border-primary'
              ]"
            >
              <span class="material-symbols-outlined text-white text-sm" v-if="selectedCinema === cinema">
                check
              </span>
            </div>
          </div>

          <!-- Location info -->
          <div class="flex items-center gap-2 text-xs text-on-surface-variant">
            <span class="material-symbols-outlined text-sm">location_on</span>
            <span>Quận Hoàn Kiếm, Hà Nội</span>
          </div>

          <!-- Amenities -->
          <div class="flex flex-wrap gap-2 mt-4">
            <span class="px-2 py-1 bg-surface-container rounded text-xs font-semibold text-on-surface-variant">
              IMAX
            </span>
            <span class="px-2 py-1 bg-surface-container rounded text-xs font-semibold text-on-surface-variant">
              4DX
            </span>
            <span class="px-2 py-1 bg-surface-container rounded text-xs font-semibold text-on-surface-variant">
              2D
            </span>
          </div>
        </div>

        <!-- Hover arrow -->
        <div
          class="absolute right-6 bottom-6 text-primary opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <span class="material-symbols-outlined text-2xl">arrow_forward</span>
        </div>
      </button>
    </div>

    <!-- No cinemas available -->
    <div v-else class="py-12 text-center">
      <p class="text-on-surface-variant mb-4">Không có rạp chiếu nào cho phim này</p>
      <NuxtLink to="/products" class="inline-block px-6 py-3 rounded-lg bg-primary text-on-primary font-bold hover:brightness-110 transition">
        Quay lại sản phẩm
      </NuxtLink>
    </div>
  </section>
</template>

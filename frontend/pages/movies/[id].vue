<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { tmdbService, movieService, type Showtime, type TmdbMovieDetail } from '~/services/api'

definePageMeta({
  layout: 'default'
})

const route = useRoute()
const ticketsStore = useTicketsStore()
const cartStore = useCartStore()

// State
const tmdbDetail = ref<TmdbMovieDetail | null>(null)
const showtimes = ref<Showtime[]>([])
const loading = ref(true)
const error = ref('')

const selectedBranch = ref('')
const selectedDate = ref('')

onMounted(async () => {
  const id = route.params.id as string
  if (!id) return

  loading.value = true
  try {
    // 1. Fetch movie metadata from TMDB (poster, trailer, cast, director, rating, genres)
    tmdbDetail.value = await tmdbService.getMovieDetail(id)
  } catch (e) {
    console.error('TMDB fetch failed, falling back to movieService:', e)
    // Fallback: try backend/mock
    try {
      const movie = await movieService.getById(id)
      tmdbDetail.value = {
        id: movie.id,
        title: movie.title,
        description: movie.description,
        poster: movie.poster,
        rating: movie.rating,
        duration: movie.duration,
        releaseDate: movie.releaseDate,
        genre: movie.genre,
        director: movie.director,
        cast: movie.cast,
        trailerUrl: movie.trailer,
      }
    } catch (e2) {
      error.value = 'Không thể tải thông tin phim.'
      loading.value = false
      return
    }

    // 2. Fetch showtimes from backend/mock (not from TMDB)
    try {
      showtimes.value = await movieService.getShowtimes(id)
      if (showtimes.value.length > 0) {
        selectedBranch.value = showtimes.value[0].branchName
        selectedDate.value = showtimes.value[0].date
      }
    } catch (e) {
      console.error('Failed to load showtimes:', e)
    } finally {
      loading.value = false
    }
  })

// Unique branches for the active movie showtimes
const branches = computed(() => {
  const list = showtimes.value.map(s => s.branchName)
  return [...new Set(list)]
})

// Unique dates for the active movie showtimes
const dates = computed(() => {
  const list = showtimes.value
    .filter(s => s.branchName === selectedBranch.value)
    .map(s => s.date)
  return [...new Set(list)]
})

// Filtered showtimes based on selected branch and date
const filteredShowtimes = computed(() => {

  return showtimes.value.filter(s =>
    s.branchName === selectedBranch.value &&
    s.date === selectedDate.value
  )
})

function selectShowtimeSlot(showtime: Showtime) {
  ticketsStore.selectShowtime(showtime)
  navigateTo('/checkout/seat')
}

function changeBranch(branch: string) {
  selectedBranch.value = branch
  const availableDates = showtimes.value
    .filter(s => s.branchName === branch)
    .map(s => s.date)

  if (availableDates.length > 0) {
    selectedDate.value = availableDates[0]
  }
}

function addMovieDetailToCart() {
  if (!activeMovie.value) return

  const showtime = filteredShowtimes.value[0]
  cartStore.addToCart({
    id: activeMovie.value.id,
    title: activeMovie.value.title,
    poster: activeMovie.value.poster,
    price: showtime ? showtime.price : 120000,
    showtime: showtime
      ? `${showtime.branchName} • ${showtime.date} ${showtime.time}`
      : 'Giá vé chuẩn'
  })
}
</script>

<template>
  <div class="pb-16">
    <!-- Loading State -->
    <div v-if="loading" class="py-24 text-center animate-pulse text-on-surface-variant">
      <span class="material-symbols-outlined text-4xl animate-spin block mb-4"
        style="animation-duration:1200ms">progress_activity</span>
      Đang tải chi tiết phim và lịch chiếu...
    </div>

    <!-- Error State -->
    <div v-else-if="error || !tmdbDetail" class="py-24 text-center text-on-surface-variant">
      ⚠️ Không tìm thấy thông tin bộ phim này trên hệ thống.
      <div class="mt-4">
        <NuxtLink to="/ai-discovery" class="text-primary-container font-bold hover:underline">Quay lại danh mục
        </NuxtLink>
      </div>
    </div>

    <!-- Movie Detail Content -->
    <div v-else>
      <!-- Hero backdrop banner with TMDB backdrop -->
      <section class="relative w-full h-[40vh] md:h-[50vh] overflow-hidden">
        <div class="absolute inset-0 z-0">

          <img :src="tmdbDetail.poster" :alt="tmdbDetail.title"
            class="w-full h-full object-cover blur-[8px] scale-105 opacity-30" />

          <div class="absolute inset-0 bg-background/80"></div>
          <div class="absolute inset-0 gradient-fade-bottom"></div>
        </div>

        <div class="relative z-10 max-w-container-max mx-auto px-6 md:px-margin-desktop h-full flex items-end pb-12">
          <div class="flex flex-col md:flex-row items-center md:items-end gap-8 w-full">
            <!-- Movie Poster -->
            <div
              class="w-48 md:w-56 aspect-[2/3] rounded-2xl overflow-hidden border border-glass-stroke shadow-2xl relative -mb-16 md:-mb-24 flex-shrink-0 z-20">
              <img :src="activeMovie.poster" :alt="activeMovie.title" class="w-full h-full object-cover" />
              <!-- Movie Poster from TMDB -->
              <div
                class="w-48 md:w-56 aspect-[2/3] rounded-2xl overflow-hidden border border-glass-stroke shadow-2xl relative -mb-16 md:-mb-24 flex-shrink-0 z-20">
                <img :src="tmdbDetail.poster" :alt="tmdbDetail.title" class="w-full h-full object-cover" />

              </div>

              <!-- Movie Title & Metadata -->
              <div class="text-center md:text-left flex-grow">


                <h1 class="font-headline-xl text-3xl md:text-5xl font-black text-on-surface tracking-tight mb-4">
                  {{ tmdbDetail.title }}
                </h1>

                <div
                  class="flex flex-wrap items-center justify-center md:justify-start gap-4 text-xs font-semibold text-on-surface-variant">
                  <!-- TMDB Rating -->
                  <span class="flex items-center gap-1">
                    <span class="material-symbols-outlined text-sm text-yellow-500"
                      style="font-variation-settings: 'FILL' 1;">star</span>
                    {{ tmdbDetail.rating.toFixed(1) }}
                  </span>
                  <span>•</span>
                  <!-- Duration -->
                  <span>{{ tmdbDetail.duration }} phút</span>
                  <span>•</span>
                  <!-- Genres -->
                  <span>{{ tmdbDetail.genre.join(', ') }}</span>
                  <span>•</span>
                  <!-- Release Date -->
                  <span>Khởi chiếu: {{ tmdbDetail.releaseDate }}</span>
                </div>
                <div class="mt-6 flex flex-col sm:flex-row gap-3 justify-center md:justify-start">
                  <button @click="addMovieDetailToCart"
                    class="inline-flex items-center justify-center rounded-3xl bg-primary-container text-on-primary-container px-5 py-3 font-bold hover:scale-105 transition-all">
                    <span class="material-symbols-outlined text-base">add_shopping_cart</span>
                    <span class="ml-2">Thêm vào giỏ</span>
                  </button>
                  <NuxtLink to="/cart"
                    class="inline-flex items-center justify-center rounded-3xl border border-white/10 bg-surface px-5 py-3 text-sm font-semibold text-on-surface hover:bg-white/5 transition-all">
                    Xem giỏ hàng
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>
      </section>

      <!-- Movie Details and Showtimes grid -->
      <section
        class="max-w-container-max mx-auto px-6 md:px-margin-desktop pt-24 md:pt-32 grid grid-cols-1 lg:grid-cols-12 gap-12">

        <!-- Left: Trailer, Description, Cast from TMDB (7 cols) -->
        <div class="lg:col-span-7 space-y-8">

          <!-- Embedded YouTube Trailer from TMDB -->
          <div v-if="tmdbDetail.trailerUrl">
            <h3 class="font-headline-md text-xl font-bold mb-4 flex items-center gap-2">
              <span class="material-symbols-outlined text-primary-container">play_circle</span>
              Official Trailer
            </h3>
            <div class="aspect-video w-full rounded-2xl overflow-hidden border border-glass-stroke bg-black shadow-lg">
              <iframe :src="tmdbDetail.trailerUrl" title="Movie Trailer" frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerpolicy="strict-origin-when-cross-origin" allowfullscreen class="w-full h-full"></iframe>
            </div>
          </div>

          <!-- No trailer placeholder -->
          <div v-else>
            <h3 class="font-headline-md text-xl font-bold mb-4 flex items-center gap-2">
              <span class="material-symbols-outlined text-primary-container">play_circle</span>
              Official Trailer
            </h3>
            <div
              class="aspect-video w-full rounded-2xl overflow-hidden border border-glass-stroke bg-surface-container-high flex items-center justify-center">
              <p class="text-on-surface-variant text-sm">Trailer chưa có sẵn</p>
            </div>
          </div>

          <!-- Description / Synopsis from TMDB -->
          <div>
            <h3 class="font-headline-md text-xl font-bold mb-3">Tóm tắt phim</h3>
            <p class="text-sm text-on-surface-variant leading-relaxed whitespace-pre-line">
              {{ tmdbDetail.description }}
            </p>
          </div>


          <!-- Director and Cast from TMDB -->
          <div
            class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-surface-container/30 border border-glass-stroke/40 p-6 rounded-2xl">
            <div v-if="tmdbDetail.director">
              <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Đạo
                diễn</span>
              <span class="text-sm font-semibold text-on-surface">{{ tmdbDetail.director }}</span>
            </div>
            <div v-if="tmdbDetail.cast.length > 0">
              <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Diễn viên
                chính</span>
              <span class="text-sm font-semibold text-on-surface">{{ tmdbDetail.cast.join(', ') }}</span>
            </div>
          </div>
        </div>

        <!-- Right: Showtimes from Backend/Mock (5 cols) -->
        <div class="lg:col-span-5 space-y-6">
          <div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8">
            <h3 class="font-headline-md text-xl font-bold mb-6 flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary">schedule</span>
              Lịch Chiếu & Đặt Vé
            </h3>

            <!-- Branch Selection -->
            <div class="space-y-4 mb-6">
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Chọn Cụm
                Rạp</label>

              <div v-if="branches.length === 0" class="text-sm text-on-surface-variant py-4 text-center">
                Không có lịch chiếu khả dụng cho phim này.
              </div>

              <div v-else class="flex flex-col gap-2">
                <button v-for="branch in branches" :key="branch" @click="changeBranch(branch)"
                  class="w-full text-left px-4 py-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-between"
                  :class="selectedBranch === branch
                    ? 'bg-purple-950 border-purple-500 text-purple-200'
                    : 'bg-surface border-glass-stroke text-on-surface-variant hover:text-on-surface hover:bg-white/5'">
                  <span>{{ branch }}</span>
                  <span class="material-symbols-outlined text-sm">chevron_right</span>
                </button>
              </div>
            </div>

            <!-- Date Selection -->
            <div v-if="branches.length > 0" class="space-y-4 mb-6">
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Chọn Ngày</label>
              <div class="flex items-center gap-2 overflow-x-auto hide-scrollbar pb-2">
                <button v-for="date in dates" :key="date" @click="selectedDate = date"
                  class="flex-shrink-0 px-4 py-2.5 rounded-xl border text-xs font-bold transition-all" :class="selectedDate === date
                    ? 'bg-primary-container border-primary-container text-white'
                    : 'bg-surface border-glass-stroke text-on-surface-variant hover:text-on-surface'">
                  {{ date }}
                </button>
              </div>
            </div>

            <!-- Showtime Slots -->
            <div v-if="branches.length > 0" class="space-y-4">
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Suất Chiếu Khả
                Dụng</label>

              <div class="grid grid-cols-2 gap-3">
                <button v-for="showtime in filteredShowtimes" :key="showtime.id" @click="selectShowtimeSlot(showtime)"
                  class="bg-surface-container border border-glass-stroke rounded-xl p-4 hover:border-primary-container hover:scale-[1.02] active:scale-95 transition-all text-left">
                  <span class="block text-lg font-black text-on-surface tracking-tight">{{ showtime.time }}</span>
                  <span class="text-[10px] font-bold text-on-surface-variant block mt-1 uppercase">{{
                    showtime.screenName }}</span>
                  <span class="text-xs text-primary-fixed-dim block mt-1.5 font-bold">{{ showtime.price.toLocaleString()
                  }} VNĐ</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

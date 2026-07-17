<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useMoviesStore } from '~/store/movies'
import { useTicketsStore } from '~/store/tickets'
import { useCartStore } from '~/store/cart'
import type { Showtime } from '~/services/api'

definePageMeta({
  layout: 'default'
})

const route = useRoute()
const moviesStore = useMoviesStore()
const ticketsStore = useTicketsStore()
const cartStore = useCartStore()

const { activeMovie, activeShowtimes, loading } = storeToRefs(moviesStore)

const selectedBranch = ref('')
const selectedDate = ref('')

onMounted(async () => {
  const id = route.params.id as string
  if (id) {
    await moviesStore.fetchMovieDetails(id)

    // Auto select first branch and date if available
    if (activeShowtimes.value.length > 0) {
      selectedBranch.value = activeShowtimes.value[0].branchName
      selectedDate.value = activeShowtimes.value[0].date
    }
  }
})

// Unique branches for the active movie showtimes
const branches = computed(() => {
  const list = activeShowtimes.value.map(s => s.branchName)
  return [...new Set(list)]
})

// Unique dates for the active movie showtimes
const dates = computed(() => {
  const list = activeShowtimes.value
    .filter(s => s.branchName === selectedBranch.value)
    .map(s => s.date)
  return [...new Set(list)]
})

// Filtered showtimes based on selected branch and date
const filteredShowtimes = computed(() => {
  return activeShowtimes.value.filter(s =>
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
  // Reset date if not available in new branch
  const availableDates = activeShowtimes.value
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
    <div v-if="loading" class="py-24 text-center animate-pulse text-on-surface-variant">
      Đang tải chi tiết phim và lịch chiếu...
    </div>

    <div v-else-if="!activeMovie" class="py-24 text-center text-on-surface-variant">
      ⚠️ Không tìm thấy thông tin bộ phim này trên hệ thống.
      <div class="mt-4">
        <NuxtLink to="/movies" class="text-primary-container font-bold hover:underline">Quay lại danh mục</NuxtLink>
      </div>
    </div>

    <div v-else>
      <!-- Hero backdrop banner -->
      <section class="relative w-full h-[40vh] md:h-[50vh] overflow-hidden">
        <div class="absolute inset-0 z-0">
          <img :src="activeMovie.poster" :alt="activeMovie.title"
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
            </div>

            <!-- Movie Title details -->
            <div class="text-center md:text-left flex-grow">
              <span
                class="bg-primary-container/10 border border-primary-container/20 text-primary-container text-xs font-bold px-3.5 py-1 rounded-full inline-block mb-3">
                {{ activeMovie.format.join(' | ') }}
              </span>

              <h1 class="font-headline-xl text-3xl md:text-5xl font-black text-on-surface tracking-tight mb-4">
                {{ activeMovie.title }}
              </h1>

              <div
                class="flex flex-wrap items-center justify-center md:justify-start gap-4 text-xs font-semibold text-on-surface-variant">
                <span class="flex items-center gap-1">
                  <span class="material-symbols-outlined text-sm text-yellow-500"
                    style="font-variation-settings: 'FILL' 1;">star</span>
                  {{ activeMovie.rating.toFixed(1) }}
                </span>
                <span>•</span>
                <span>{{ activeMovie.duration }} phút</span>
                <span>•</span>
                <span>{{ activeMovie.genre.join(', ') }}</span>
                <span>•</span>
                <span>Khởi chiếu: {{ activeMovie.releaseDate }}</span>
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

        <!-- Left details and trailer (7 cols) -->
        <div class="lg:col-span-7 space-y-8">

          <!-- Embedded YouTube Trailer -->
          <div>
            <h3 class="font-headline-md text-xl font-bold mb-4 flex items-center gap-2">
              <span class="material-symbols-outlined text-primary-container">play_circle</span>
              Official Trailer
            </h3>
            <div class="aspect-video w-full rounded-2xl overflow-hidden border border-glass-stroke bg-black shadow-lg">
              <iframe :src="activeMovie.trailer" title="Movie Trailer" frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerpolicy="strict-origin-when-cross-origin" allowfullscreen class="w-full h-full"></iframe>
            </div>
          </div>

          <!-- Description / Synopsis -->
          <div>
            <h3 class="font-headline-md text-xl font-bold mb-3">Tóm tắt phim</h3>
            <p class="text-sm text-on-surface-variant leading-relaxed whitespace-pre-line">
              {{ activeMovie.description }}
            </p>
          </div>

          <!-- Director and Cast info -->
          <div
            class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-surface-container/30 border border-glass-stroke/40 p-6 rounded-2xl">
            <div>
              <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Đạo
                diễn</span>
              <span class="text-sm font-semibold text-on-surface">{{ activeMovie.director }}</span>
            </div>
            <div>
              <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Diễn viên
                chính</span>
              <span class="text-sm font-semibold text-on-surface">{{ activeMovie.cast.join(', ') }}</span>
            </div>
          </div>
        </div>

        <!-- Right side showtimes selectors (5 cols) -->
        <div class="lg:col-span-5 space-y-6">
          <div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8">
            <h3 class="font-headline-md text-xl font-bold mb-6 flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary">schedule</span>
              Lịch Chiếu & Đặt Vé
            </h3>

            <!-- Showtimes Branch Selection Tab -->
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

            <!-- Showtimes Date Selection -->
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

            <!-- Showtime Slots Grid -->
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

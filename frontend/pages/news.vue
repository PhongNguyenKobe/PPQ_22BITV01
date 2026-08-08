<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductsStore } from '~/store/products'
import { movieService, type Showtime } from '~/services/api'
import { getProductSlugUrl } from '~/utils/slug'

definePageMeta({ layout: 'default' })

const productsStore = useProductsStore()
const { products, loading, error: storeError } = storeToRefs(productsStore)
const showtimes = ref<Record<string, Showtime[]>>({})
const scheduleLoading = ref(false)
const search = ref('')
const selectedStatus = ref<'ALL' | 'NOW_SHOWING' | 'UPCOMING'>('ALL')

const normalizedSearch = computed(() => search.value.trim().toLocaleLowerCase('vi'))
const filteredMovies = computed(() => products.value.filter(movie => {
  if (selectedStatus.value !== 'ALL' && movie.status !== selectedStatus.value) return false
  if (!normalizedSearch.value) return true
  return `${movie.name} ${movie.originalTitle || ''} ${movie.director || ''} ${movie.genres.join(' ')}`
    .toLocaleLowerCase('vi')
    .includes(normalizedSearch.value)
}))

const nowShowing = computed(() => products.value.filter(movie => movie.status === 'NOW_SHOWING'))
const upcoming = computed(() => [...products.value]
  .filter(movie => movie.status === 'UPCOMING')
  .sort((a, b) => new Date(a.releaseDate || 0).getTime() - new Date(b.releaseDate || 0).getTime()))
const featuredMovie = computed(() => [...nowShowing.value]
  .sort((a, b) => (showtimes.value[String(b.backendMovieId || b.id)]?.length || 0) - (showtimes.value[String(a.backendMovieId || a.id)]?.length || 0))[0]
  || upcoming.value[0]
  || products.value[0])
const secondaryStories = computed(() => products.value.filter(movie => movie.id !== featuredMovie.value?.id).slice(0, 4))
const totalOpenShowtimes = computed(() => Object.values(showtimes.value).reduce((sum, items) => sum + items.length, 0))

function movieShowtimeCount(movie: any) {
  return showtimes.value[String(movie.backendMovieId || movie.id)]?.length || 0
}

function formatReleaseDate(value: string) {
  if (!value) return 'Đang cập nhật'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Đang cập nhật'
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(date)
}

function excerpt(value: string, length = 150) {
  const text = value?.trim() || 'Thông tin nội dung phim đang được cập nhật từ hệ thống.'
  return text.length > length ? `${text.slice(0, length).trim()}…` : text
}

onMounted(async () => {
  await productsStore.fetchProducts(true)
  scheduleLoading.value = true
  const movies = products.value.filter(movie => movie.status === 'NOW_SHOWING' && movie.backendMovieId)
  const results = await Promise.all(movies.map(async movie => {
    const items = await movieService.getShowtimes(String(movie.backendMovieId)).catch(() => [])
    return [String(movie.backendMovieId), items] as const
  }))
  showtimes.value = Object.fromEntries(results)
  scheduleLoading.value = false
})
</script>

<template>
  <main class="min-h-[75vh] bg-[#0f1111] px-5 py-10 md:px-10 md:py-14">
    <div class="mx-auto max-w-6xl">
      <header class="flex flex-col gap-6 border-b border-white/10 pb-8 md:flex-row md:items-end md:justify-between">
        <div>
          <div class="flex items-center gap-2 text-xs font-black uppercase tracking-[0.2em] text-red-500">
            <span class="material-symbols-outlined text-lg">newspaper</span>
            CineAI Magazine
          </div>
          <h1 class="mt-3 text-4xl font-black text-white md:text-5xl">Tin điện ảnh</h1>
          <p class="mt-3 max-w-2xl text-sm leading-6 text-gray-400">Khám phá phim đang chiếu, lịch phát hành và những gương mặt điện ảnh nổi bật từ kho phim CineAI.</p>
        </div>
        <div class="flex gap-6 text-right">
          <div><strong class="block text-2xl text-white">{{ products.length }}</strong><span class="text-xs text-gray-500">phim trong hệ thống</span></div>
          <div><strong class="block text-2xl text-white">{{ totalOpenShowtimes }}</strong><span class="text-xs text-gray-500">suất đang mở</span></div>
        </div>
      </header>

      <div v-if="loading" class="py-24 text-center text-gray-400">
        <span class="material-symbols-outlined animate-spin text-4xl text-red-500">progress_activity</span>
        <p class="mt-3">Đang tổng hợp dữ liệu điện ảnh...</p>
      </div>
      <div v-else-if="storeError" class="my-8 rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-red-300">{{ storeError }}</div>

      <template v-else-if="featuredMovie">
        <section class="mt-8 grid overflow-hidden rounded-3xl border border-white/10 bg-[#1a1c1c] shadow-2xl lg:grid-cols-[1.4fr_0.6fr]">
          <NuxtLink :to="getProductSlugUrl(featuredMovie)" class="group relative min-h-[430px] overflow-hidden">
            <img :src="featuredMovie.imageUrl" :alt="featuredMovie.name" class="absolute inset-0 h-full w-full object-cover transition duration-700 group-hover:scale-105">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent"></div>
            <div class="absolute inset-x-0 bottom-0 p-7 md:p-10">
              <div class="mb-3 flex flex-wrap items-center gap-2">
                <span class="rounded-full bg-red-600 px-3 py-1 text-xs font-black uppercase text-white">Tiêu điểm</span>
                <span v-if="featuredMovie.status === 'NOW_SHOWING'" class="rounded-full border border-white/20 bg-black/40 px-3 py-1 text-xs font-bold text-white">Đang chiếu</span>
                <span v-else class="rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs font-bold text-amber-300">Sắp chiếu</span>
              </div>
              <h2 class="max-w-3xl text-3xl font-black leading-tight text-white md:text-5xl">{{ featuredMovie.name }}</h2>
              <p class="mt-4 max-w-2xl text-sm leading-6 text-gray-200 md:text-base">{{ excerpt(featuredMovie.description, 200) }}</p>
              <div class="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-xs font-semibold text-gray-300">
                <span>{{ featuredMovie.genres.join(' · ') || 'Điện ảnh' }}</span>
                <span>{{ featuredMovie.duration }} phút</span>
                <span v-if="movieShowtimeCount(featuredMovie)">{{ movieShowtimeCount(featuredMovie) }} suất đang mở</span>
              </div>
            </div>
          </NuxtLink>

          <aside class="divide-y divide-white/10">
            <NuxtLink v-for="movie in secondaryStories" :key="movie.id" :to="getProductSlugUrl(movie)" class="group flex gap-4 p-5 transition hover:bg-white/[0.04]">
              <img :src="movie.imageUrl" :alt="movie.name" class="h-24 w-16 flex-none rounded-lg object-cover">
              <div class="min-w-0">
                <span class="text-[10px] font-black uppercase tracking-wider" :class="movie.status === 'NOW_SHOWING' ? 'text-red-400' : 'text-amber-400'">{{ movie.status === 'NOW_SHOWING' ? 'Đang chiếu' : 'Sắp chiếu' }}</span>
                <h3 class="mt-1 line-clamp-2 font-bold leading-5 text-white group-hover:text-red-300">{{ movie.name }}</h3>
                <p class="mt-2 text-xs text-gray-500">{{ movie.genres.slice(0, 2).join(' · ') }} · {{ movie.duration }} phút</p>
              </div>
            </NuxtLink>
          </aside>
        </section>

        <section class="mt-12">
          <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p class="text-xs font-black uppercase tracking-[0.18em] text-red-500">Hồ sơ điện ảnh</p>
              <h2 class="mt-1 text-2xl font-black text-white">Khám phá kho phim</h2>
            </div>
            <div class="flex flex-col gap-3 sm:flex-row">
              <div class="flex rounded-xl border border-white/10 bg-white/[0.03] p-1">
                <button v-for="tab in [{ value: 'ALL', label: 'Tất cả' }, { value: 'NOW_SHOWING', label: 'Đang chiếu' }, { value: 'UPCOMING', label: 'Sắp chiếu' }]" :key="tab.value" class="rounded-lg px-4 py-2 text-xs font-bold transition" :class="selectedStatus === tab.value ? 'bg-red-600 text-white' : 'text-gray-400 hover:text-white'" @click="selectedStatus = tab.value as any">{{ tab.label }}</button>
              </div>
              <div class="relative">
                <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-lg text-gray-500">search</span>
                <input v-model="search" class="w-full rounded-xl border border-white/10 bg-white/[0.03] py-2.5 pl-10 pr-4 text-sm text-white outline-none focus:border-red-500 sm:w-64" placeholder="Tìm phim, đạo diễn...">
              </div>
            </div>
          </div>

          <div v-if="filteredMovies.length" class="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <NuxtLink v-for="movie in filteredMovies" :key="movie.id" :to="getProductSlugUrl(movie)" class="group grid grid-cols-[110px_1fr] overflow-hidden rounded-2xl border border-white/10 bg-[#1a1c1c] transition hover:-translate-y-1 hover:border-red-500/40">
              <img :src="movie.imageUrl" :alt="movie.name" class="h-full min-h-48 w-full object-cover">
              <div class="flex min-w-0 flex-col p-4">
                <span class="text-[10px] font-black uppercase tracking-wider" :class="movie.status === 'NOW_SHOWING' ? 'text-red-400' : 'text-amber-400'">{{ movie.status === 'NOW_SHOWING' ? 'Đang chiếu' : 'Sắp chiếu' }}</span>
                <h3 class="mt-1 line-clamp-2 text-lg font-black text-white group-hover:text-red-300">{{ movie.name }}</h3>
                <p class="mt-2 line-clamp-3 text-xs leading-5 text-gray-400">{{ excerpt(movie.description, 105) }}</p>
                <div class="mt-auto pt-3 text-[11px] text-gray-500">
                  <p v-if="movie.director">Đạo diễn: {{ movie.director }}</p>
                  <p class="mt-1">Khởi chiếu: {{ formatReleaseDate(movie.releaseDate) }}</p>
                </div>
              </div>
            </NuxtLink>
          </div>
          <div v-else class="mt-6 rounded-2xl border border-white/10 py-14 text-center text-gray-500">Không tìm thấy phim phù hợp.</div>
        </section>

        <section v-if="upcoming.length" class="mt-12 border-t border-white/10 pt-10">
          <div class="flex items-end justify-between">
            <div><p class="text-xs font-black uppercase tracking-[0.18em] text-amber-400">Lịch phát hành</p><h2 class="mt-1 text-2xl font-black text-white">Sắp ra mắt tại CineAI</h2></div>
            <span class="text-xs text-gray-500">Dữ liệu từ lịch phim hệ thống</span>
          </div>
          <div class="mt-6 grid gap-3 md:grid-cols-2">
            <NuxtLink v-for="movie in upcoming.slice(0, 6)" :key="movie.id" :to="getProductSlugUrl(movie)" class="flex items-center gap-4 rounded-xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-amber-400/30 hover:bg-amber-400/[0.04]">
              <div class="min-w-20 rounded-lg bg-amber-400/10 px-3 py-2 text-center text-xs font-black text-amber-300">{{ formatReleaseDate(movie.releaseDate) }}</div>
              <div class="min-w-0"><h3 class="truncate font-bold text-white">{{ movie.name }}</h3><p class="mt-1 truncate text-xs text-gray-500">{{ movie.genres.join(' · ') || 'Đang cập nhật thể loại' }}</p></div>
              <span class="material-symbols-outlined ml-auto text-gray-600">arrow_forward</span>
            </NuxtLink>
          </div>
        </section>
      </template>

      <div v-else class="py-24 text-center text-gray-500">
        <span class="material-symbols-outlined text-5xl">movie_off</span>
        <p class="mt-3">Chưa có dữ liệu phim để hiển thị.</p>
      </div>

      <p v-if="scheduleLoading" class="mt-8 text-center text-xs text-gray-600">Đang cập nhật số suất chiếu...</p>
    </div>
  </main>
</template>

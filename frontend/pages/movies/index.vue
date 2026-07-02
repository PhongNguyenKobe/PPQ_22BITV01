<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useMoviesStore } from '~/store/movies'

definePageMeta({ layout: 'default' })

const moviesStore = useMoviesStore()
const { movies, loading } = storeToRefs(moviesStore)

const searchKeyword = ref('')
const selectedGenre = ref('Tất cả')
const selectedYear = ref('Tất cả')
const selectedCountry = ref('Tất cả')
const activeSort = ref('Mới nhất')

const genresList = ['Tất cả', 'Hành động', 'Viễn tưởng', 'Kinh dị', 'Hoạt hình', 'Lãng mạn', 'Hài hước', 'Tâm lý', 'Tài liệu']
const yearsList = ['Tất cả', '2026', '2025', '2024', '2023']
const countriesList = ['Tất cả', 'Việt Nam', 'Mỹ', 'Hàn Quốc', 'Nhật Bản']
const sortsList = ['Mới nhất', 'Đánh giá cao nhất', 'Tên A-Z', 'Tên Z-A']

// Since pinia store mock only has 10 movies, we'll map existing fields for demo purposes
const filteredMovies = computed(() => {
  let result = movies.value

  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(m => m.title.toLowerCase().includes(kw))
  }

  if (selectedGenre.value !== 'Tất cả') {
    result = result.filter(m => m.genre.some(g => g.toLowerCase().includes(selectedGenre.value.toLowerCase())))
  }

  // Simulate sorting
  if (activeSort.value === 'Đánh giá cao nhất') {
    result = [...result].sort((a, b) => (parseFloat(b.rating || '0') - parseFloat(a.rating || '0')))
  } else if (activeSort.value === 'Tên A-Z') {
    result = [...result].sort((a, b) => a.title.localeCompare(b.title))
  } else if (activeSort.value === 'Tên Z-A') {
    result = [...result].sort((a, b) => b.title.localeCompare(a.title))
  }

  return result
})
</script>

<template>
  <div class="min-h-screen pt-20">
    <!-- Traditional Filter Hero -->
    <section class="bg-surface-container-low border-b border-white/10 py-12">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div>
            <h1 class="font-headline-xl text-headline-xl text-on-surface mb-2">Danh mục phim</h1>
            <p class="text-on-surface-variant">Duyệt qua hàng ngàn bộ phim đang chiếu và sắp chiếu tại các cụm rạp.</p>
          </div>
          <div class="relative w-full md:w-80">
            <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
            <input 
              v-model="searchKeyword" 
              type="text" 
              placeholder="Tìm tên phim..." 
              class="w-full bg-surface-container border border-white/10 rounded-xl py-3 pl-12 pr-4 text-on-surface placeholder:text-on-surface-variant outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-all"
            >
          </div>
        </div>

        <!-- Filter Grid -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-2xl border border-white/10 bg-surface">
          <!-- Genre -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider px-2">Thể loại</label>
            <div class="relative">
              <select v-model="selectedGenre" class="w-full bg-surface-container-high border-none rounded-lg py-2.5 px-3 text-sm text-on-surface appearance-none outline-none cursor-pointer">
                <option v-for="g in genresList" :key="g">{{ g }}</option>
              </select>
              <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">expand_more</span>
            </div>
          </div>
          <!-- Country -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider px-2">Quốc gia</label>
            <div class="relative">
              <select v-model="selectedCountry" class="w-full bg-surface-container-high border-none rounded-lg py-2.5 px-3 text-sm text-on-surface appearance-none outline-none cursor-pointer">
                <option v-for="c in countriesList" :key="c">{{ c }}</option>
              </select>
              <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">expand_more</span>
            </div>
          </div>
          <!-- Year -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider px-2">Năm</label>
            <div class="relative">
              <select v-model="selectedYear" class="w-full bg-surface-container-high border-none rounded-lg py-2.5 px-3 text-sm text-on-surface appearance-none outline-none cursor-pointer">
                <option v-for="y in yearsList" :key="y">{{ y }}</option>
              </select>
              <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">expand_more</span>
            </div>
          </div>
          <!-- Sort -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider px-2">Sắp xếp</label>
            <div class="relative">
              <select v-model="activeSort" class="w-full bg-surface-container-high border-none rounded-lg py-2.5 px-3 text-sm text-on-surface appearance-none outline-none cursor-pointer">
                <option v-for="s in sortsList" :key="s">{{ s }}</option>
              </select>
              <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">expand_more</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Movie Grid -->
    <section class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-12 pb-24">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-on-surface font-headline-md text-headline-md">Tìm thấy <span class="text-primary-container">{{ filteredMovies.length }}</span> phim</h2>
        <div class="flex gap-2 text-on-surface-variant">
          <button class="w-8 h-8 rounded bg-surface-container flex items-center justify-center text-primary-container"><span class="material-symbols-outlined text-[20px]">grid_view</span></button>
          <button class="w-8 h-8 rounded bg-surface-container flex items-center justify-center hover:text-white transition-colors"><span class="material-symbols-outlined text-[20px]">view_list</span></button>
        </div>
      </div>

      <div v-if="filteredMovies.length === 0" class="py-20 text-center flex flex-col items-center">
        <span class="material-symbols-outlined text-6xl text-white/10 mb-4">movie_off</span>
        <p class="text-on-surface-variant text-lg">Không tìm thấy phim nào khớp với bộ lọc.</p>
        <button @click="selectedGenre = 'Tất cả'; searchKeyword = ''" class="mt-4 text-primary-container hover:underline font-bold">Xóa bộ lọc</button>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
        <div v-for="m in filteredMovies" :key="m.id" class="flex flex-col group cursor-pointer">
          <div class="relative aspect-[2/3] rounded-xl overflow-hidden mb-4 bg-surface-container">
            <img class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" :src="m.poster" :alt="m.title">
            <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-6 text-center">
              <NuxtLink :to="`/movies/${m.id}`" class="bg-primary-container text-white px-4 py-2 rounded-lg font-label-sm text-label-sm font-bold hover:shadow-[0_0_25px_-5px_rgba(229,9,20,0.5)] transition-all">Chi tiết</NuxtLink>
            </div>
            <div class="absolute top-2 right-2 px-2 py-1 rounded text-label-sm text-white flex items-center gap-1 font-bold" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
              <span class="material-symbols-outlined text-[14px] text-primary" style="font-variation-settings:'FILL' 1">star</span> {{ m.rating || '4.5' }}
            </div>
            <div class="absolute top-2 left-2 px-2 py-1 bg-surface-container-highest rounded text-[10px] text-white font-bold border border-white/5 uppercase">
              {{ m.format || '2D' }}
            </div>
          </div>
          <h4 class="font-label-md text-label-md group-hover:text-primary-container transition-colors text-on-surface">{{ m.title }}</h4>
          <p class="text-on-surface-variant font-label-sm text-label-sm truncate">{{ m.genre.join(', ') }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useMoviesStore } from '~/store/movies'

definePageMeta({
  layout: 'default'
})

const moviesStore = useMoviesStore()
const { movies, loading } = storeToRefs(moviesStore)

const selectedGenre = ref('Tất Cả Phim')
const activeSort = ref('Độ Phù Hợp AI')

const genresList = [
  'Tất Cả Phim',
  'Hành Động',
  'Viễn Tưởng',
  'Kịch Tính',
  'Tâm Lý',
  'Cyberpunk',
  'Neon-Noir'
]

onMounted(async () => {
  await moviesStore.fetchMovies()
})

// Filter movies based on selected genre tag
const filteredMovies = computed(() => {
  if (selectedGenre.value === 'Tất Cả Phim') {
    return movies.value
  }
  return movies.value.filter(movie => 
    movie.genre.some(g => g.toLowerCase() === selectedGenre.value.toLowerCase())
  )
})

function filterByGenre(genre: string) {
  selectedGenre.value = genre
}
</script>

<template>
  <div class="pb-16">
    <!-- Hero Search Section -->
    <section class="relative py-12 flex items-center overflow-hidden bg-gradient-to-b from-[#161718] to-background">
      <div class="relative z-10 max-w-container-max mx-auto px-6 md:px-margin-desktop w-full text-center">
        <h1 class="font-headline-xl text-3xl md:text-5xl font-bold mb-4 text-on-surface">
          Trải Nghiệm Trí Tuệ <span class="text-primary-container">Điện Ảnh</span>
        </h1>
        <p class="text-xs md:text-sm text-on-surface-variant max-w-lg mx-auto mb-6">
          Tìm kiếm lịch chiếu bằng ngôn ngữ tự nhiên thông qua AI và nhận ngay suất chiếu phù hợp nhất.
        </p>
        
        <!-- Advanced Semantic Search bar -->
        <AiSemanticSearch />
      </div>
    </section>

    <!-- AI Personalized Recommendations Section -->
    <section class="bg-surface-container-lowest/30 border-y border-glass-stroke/50 py-8">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
        <AiRecommendation />
      </div>
    </section>

    <!-- Movie Catalog List & Filters -->
    <section class="py-12">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
        <!-- Filters sticky tab -->
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-glass-stroke pb-6 mb-8">
          <!-- Genre filter tabs -->
          <div class="flex items-center gap-2 overflow-x-auto hide-scrollbar w-full md:w-auto pb-2 md:pb-0">
            <button
              v-for="genre in genresList"
              :key="genre"
              @click="filterByGenre(genre)"
              class="flex-shrink-0 px-4 py-2 rounded-xl text-xs font-bold transition-all"
              :class="selectedGenre === genre
                ? 'bg-primary-container text-on-primary-container shadow-md red-glow'
                : 'bg-surface-container border border-glass-stroke text-on-surface-variant hover:text-on-surface hover:bg-white/5'"
            >
              {{ genre }}
            </button>
          </div>

          <!-- Sorter dropdown -->
          <div class="flex items-center gap-2 self-end md:self-auto flex-shrink-0">
            <span class="text-xs text-on-surface-variant font-medium">Sắp xếp:</span>
            <select
              v-model="activeSort"
              class="bg-surface-container border border-glass-stroke rounded-xl text-on-surface font-label-md text-xs py-2 px-4 outline-none focus:ring-1 focus:ring-primary-container"
            >
              <option>Độ Phù Hợp AI</option>
              <option>Ngày Phát Hành</option>
              <option>Điểm Đánh Giá</option>
            </select>
          </div>
        </div>

        <!-- Movie Catalog Grid -->
        <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          <div v-for="n in 4" :key="n" class="animate-pulse bg-surface-container h-[350px] rounded-2xl border border-glass-stroke"></div>
        </div>

        <div v-else-if="filteredMovies.length === 0" class="py-16 text-center text-on-surface-variant">
          <span class="material-symbols-outlined text-[48px] mb-2 text-on-surface-variant">search_off</span>
          <p class="text-sm font-medium">Không tìm thấy bộ phim nào phù hợp với bộ lọc hiện tại.</p>
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          <MovieCard
            v-for="movie in filteredMovies"
            :key="movie.id"
            :movie="movie"
          />
        </div>
      </div>
    </section>
  </div>
</template>

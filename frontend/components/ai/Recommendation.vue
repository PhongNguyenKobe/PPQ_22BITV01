<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useMoviesStore } from '~/store/movies'

const moviesStore = useMoviesStore()
const { recommendations, loading } = storeToRefs(moviesStore)

onMounted(async () => {
  if (recommendations.value.length === 0) {
    await moviesStore.fetchRecommendations()
  }
})
</script>

<template>
  <div class="my-12">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="font-headline-lg text-2xl md:text-3xl text-on-surface flex items-center gap-3">
          <span class="material-symbols-outlined text-secondary" style="font-variation-settings: 'FILL' 1;">
            auto_awesome
          </span>
          Gợi Ý Phim Từ CineAI
        </h2>
        <p class="text-on-surface-variant text-sm mt-1">Các tác phẩm được phân tích và đề xuất theo thói quen xem phim của bạn.</p>
      </div>
    </div>

    <!-- Recommendations Grid -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="n in 2" :key="n" class="animate-pulse bg-surface-container h-[200px] rounded-2xl border border-glass-stroke"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div
        v-for="movie in recommendations"
        :key="movie.id"
        class="group relative rounded-2xl overflow-hidden aspect-[16/9] border border-glass-stroke hover:border-primary-container/40 transition-all duration-300 shadow-lg"
      >
        <!-- Movie Poster Backdrop -->
        <img
          :src="movie.poster"
          :alt="movie.title"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        
        <!-- Gradient Overlay -->
        <div class="absolute inset-0 bg-gradient-to-t from-surface via-surface/60 to-transparent p-6 flex flex-col justify-end">
          <div class="mb-4">
            <span class="bg-secondary-container/20 border border-secondary-container/30 text-secondary text-[11px] font-bold px-3 py-1 rounded-full inline-flex items-center gap-1.5 backdrop-blur-md mb-3">
              <span class="material-symbols-outlined text-xs">psychology</span>
              AI Match
            </span>
            
            <h3 class="font-headline-md text-xl md:text-2xl font-bold text-on-surface mb-2">
              {{ movie.title }}
            </h3>
            
            <p class="text-xs md:text-sm text-on-surface-variant line-clamp-2 leading-relaxed">
              {{ movie.description }}
            </p>
          </div>

          <div class="flex items-center justify-between border-t border-glass-stroke/40 pt-4 mt-1">
            <div class="flex items-center gap-4 text-xs font-semibold text-on-surface-variant">
              <span class="flex items-center gap-1">
                <span class="material-symbols-outlined text-sm text-yellow-500" style="font-variation-settings: 'FILL' 1;">star</span>
                {{ movie.rating.toFixed(1) }}
              </span>
              <span>{{ movie.genre.join(', ') }}</span>
            </div>
            
            <NuxtLink
              :to="`/products/${movie.id}`"
              class="bg-primary-container hover:bg-opacity-90 text-on-primary-container px-5 py-2 rounded-xl text-xs font-bold transition-all hover:scale-105 active:scale-95 flex items-center gap-1.5 red-glow"
            >
              Đặt Vé
              <span class="material-symbols-outlined text-xs">arrow_forward</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Floating AI Reason Tag -->
        <div class="absolute top-4 left-4 right-4 bg-black/50 backdrop-blur-md border border-glass-stroke/50 p-2.5 rounded-xl text-xs text-secondary-fixed opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
          💡 {{ movie.aiMatchReason }}
        </div>
      </div>
    </div>
  </div>
</template>

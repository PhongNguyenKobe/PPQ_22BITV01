<script setup lang="ts">
import type { Movie } from '~/services/api'

defineProps<{
  movie: Movie
}>()
</script>

<template>
  <div class="group relative bg-surface-container-low border border-glass-stroke rounded-2xl overflow-hidden shadow-lg hover:border-primary-container/30 transition-all duration-300 flex flex-col h-full">
    <!-- Poster Image Wrap -->
    <div class="relative overflow-hidden aspect-[2/3] w-full bg-surface-container-high">
      <img
        :src="movie.poster"
        :alt="movie.title"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
      
      <!-- Hover overlay content -->
      <div class="absolute inset-0 bg-black/80 p-4 opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col justify-between">
        <div>
          <span class="text-xs text-secondary font-bold flex items-center gap-1 mb-2">
            <span class="material-symbols-outlined text-xs">auto_awesome</span>
            CineAI Match
          </span>
          <p class="text-xs text-on-surface-variant line-clamp-6 leading-relaxed">
            {{ movie.description }}
          </p>
        </div>
        <div class="space-y-2">
          <div class="text-xs text-on-surface-variant flex flex-wrap gap-1">
            <span class="text-white font-semibold">Đạo diễn:</span>
            <span>{{ movie.director }}</span>
          </div>
          <NuxtLink
            :to="`/products/${movie.id}`"
            class="w-full bg-primary-container text-on-primary-container py-2.5 rounded-xl font-bold text-center block text-sm transition-all hover:scale-105 active:scale-95 red-glow"
          >
            Xem Chi Tiết
          </NuxtLink>
        </div>
      </div>

      <!-- Format badges (e.g. IMAX, 4DX) -->
      <div class="absolute top-3 left-3 flex flex-col gap-1 z-10">
        <span
          v-for="fmt in movie.format"
          :key="fmt"
          class="bg-black/60 border border-white/20 text-[10px] font-bold px-2.5 py-0.5 rounded text-white tracking-wide uppercase backdrop-blur-sm"
        >
          {{ fmt }}
        </span>
      </div>

      <!-- Rating badge -->
      <div class="absolute top-3 right-3 bg-yellow-500/90 text-black font-bold text-xs px-2.5 py-1 rounded-lg flex items-center gap-1 z-10 backdrop-blur-sm">
        <span class="material-symbols-outlined text-xs text-black" style="font-variation-settings: 'FILL' 1;">star</span>
        {{ movie.rating.toFixed(1) }}
      </div>
    </div>

    <!-- Metadata Details -->
    <div class="p-4 flex-1 flex flex-col justify-between bg-surface-container/30">
      <div>
        <h3 class="font-bold text-base text-on-surface line-clamp-1 mb-1 group-hover:text-primary-container transition-colors">
          {{ movie.title }}
        </h3>
        <p class="text-xs text-on-surface-variant line-clamp-1">
          {{ movie.genre.join(' | ') }}
        </p>
      </div>

      <div class="flex items-center justify-between border-t border-glass-stroke/40 pt-3 mt-3">
        <span class="text-xs text-on-surface-variant">
          ⏱️ {{ movie.duration }} phút
        </span>
        <NuxtLink
          :to="`/products/${movie.id}`"
          class="text-xs font-bold text-primary-container hover:underline flex items-center gap-1"
        >
          Đặt Vé
          <span class="material-symbols-outlined text-xs">chevron_right</span>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

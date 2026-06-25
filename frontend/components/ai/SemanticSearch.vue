<script setup lang="ts">
import { ref } from 'vue'
import { useMoviesStore } from '~/store/movies'

const searchInput = ref('')
const moviesStore = useMoviesStore()

const suggestions = [
  'Phim viễn tưởng vũ trụ hoành tráng',
  'Hành động kịch tính nghẹt thở',
  'Cyberpunk neon đen tối mới nhất',
  'Phim của đạo diễn Christopher Nolan'
]

async function triggerSearch() {
  await moviesStore.searchMovies(searchInput.value)
}

async function useSuggestion(text: string) {
  searchInput.value = text
  await triggerSearch()
}

function clearSearch() {
  searchInput.value = ''
  triggerSearch()
}
</script>

<template>
  <div class="w-full max-w-3xl mx-auto my-8">
    <div class="relative group">
      <!-- Glow background -->
      <div class="absolute -inset-1 bg-gradient-to-r from-primary-container to-secondary-container rounded-full blur opacity-25 group-hover:opacity-40 transition duration-500"></div>
      
      <!-- Input Box -->
      <div class="relative flex items-center glass-panel rounded-full p-2 border border-glass-stroke">
        <span class="material-symbols-outlined ml-4 text-primary-container animate-pulse" style="font-variation-settings: 'FILL' 1;">
          psychology
        </span>
        
        <input
          v-model="searchInput"
          @keydown.enter="triggerSearch"
          type="text"
          class="bg-transparent border-none focus:ring-0 w-full text-on-surface px-4 py-3 placeholder:text-on-surface-variant text-base"
          placeholder="Thử nhập: 'phim viễn tưởng vũ trụ' hoặc 'hành động kịch tính tối nay'..."
        />
        
        <!-- Action Buttons -->
        <button
          v-if="searchInput"
          @click="clearSearch"
          type="button"
          class="p-2 text-on-surface-variant hover:text-on-surface mr-2"
        >
          <span class="material-symbols-outlined">close</span>
        </button>

        <button
          @click="triggerSearch"
          class="bg-primary-container text-on-primary-container px-8 py-3 rounded-full font-bold hover:scale-105 active:scale-95 transition-all flex items-center gap-2 red-glow"
        >
          <span class="material-symbols-outlined text-sm">search</span>
          Khám Phá AI
        </button>
      </div>
    </div>

    <!-- Suggested Search Chips -->
    <div class="mt-4 flex flex-wrap justify-center gap-2">
      <span class="text-xs text-on-surface-variant flex items-center gap-1 py-1">
        <span class="material-symbols-outlined text-xs">auto_awesome</span>
        Gợi ý khẩu lệnh:
      </span>
      <button
        v-for="sug in suggestions"
        :key="sug"
        @click="useSuggestion(sug)"
        class="px-3.5 py-1 rounded-full bg-surface-container border border-glass-stroke text-on-surface-variant hover:text-primary-container hover:border-primary-container text-xs transition-colors"
      >
        {{ sug }}
      </button>
    </div>
  </div>
</template>

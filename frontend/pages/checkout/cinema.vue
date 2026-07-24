<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { useBooking } from '~/composables/useBooking'
import { movieService, type Showtime } from '~/services/api'
import { formatDate, formatTime, formatPrice } from '~/utils/format'

definePageMeta({
  layout: 'checkout',
  middleware: 'auth'
})

const ticketsStore = useTicketsStore()
const { selectedMovie } = storeToRefs(ticketsStore)
const { selectShowtime } = useBooking()

const showtimes = ref<Showtime[]>([])
const loading = ref(false)
const error = ref('')
const selectedShowtimeId = ref<string>('')

onMounted(async () => {
  if (!selectedMovie.value) {
    await navigateTo('/products')
    return
  }

  loading.value = true
  try {
    const response = await movieService.getShowtimes(String(selectedMovie.value.id))
    showtimes.value = response
  } catch (err) {
    error.value = 'Failed to load showtimes'
  } finally {
    loading.value = false
  }
})

const proceedToSeats = () => {
  const showtime = showtimes.value.find(s => s.id === selectedShowtimeId.value)
  if (showtime) {
    selectShowtime(showtime)
    navigateTo('/checkout/seat')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-on-surface mb-2">Chọn Rạp & Suất Chiếu</h2>
      <p class="text-sm text-on-surface-variant">{{ selectedMovie?.name }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin">
        <span class="material-symbols-outlined text-4xl text-primary-container">hourglass_empty</span>
      </div>
      <p class="text-sm text-on-surface-variant mt-2">Loading showtimes...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-error/10 border border-error/30 rounded-xl p-4 text-error text-sm">
      {{ error }}
    </div>

    <!-- Showtimes List -->
    <div v-else class="space-y-3">
      <label
        v-for="showtime of showtimes"
        :key="showtime.id"
        class="block cursor-pointer"
      >
        <input
          v-model="selectedShowtimeId"
          type="radio"
          :value="showtime.id"
          class="sr-only"
        />
        <div
          class="p-4 border-2 rounded-xl transition-all"
          :class="selectedShowtimeId === showtime.id
            ? 'border-primary-container bg-primary-container/10'
            : 'border-glass-stroke hover:border-primary-container/50'
          "
        >
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold text-on-surface">{{ showtime.branch_name }}</p>
              <p class="text-sm text-on-surface-variant">{{ showtime.screen_name }}</p>
            </div>
            <div class="text-right">
              <p class="font-bold text-primary-container">{{ formatTime(showtime.starts_at) }}</p>
              <p class="text-xs text-on-surface-variant">{{ formatDate(showtime.starts_at) }}</p>
            </div>
          </div>
          <div class="mt-3 flex items-center justify-between">
            <p class="text-xs text-on-surface-variant">Giá: <span class="font-semibold text-on-surface">{{ formatPrice(Number(showtime.base_price)) }}</span></p>
            <span v-if="showtime.status === 'OPEN'" class="text-xs font-semibold text-green-600 bg-green-100 px-2 py-1 rounded">Còn vé</span>
          </div>
        </div>
      </label>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-3 pt-4">
      <NuxtLink to="/products" class="flex-1 bg-surface-variant text-on-surface px-4 py-3 rounded-xl font-semibold hover:bg-surface-variant/80 transition-colors text-center">
        ← Quay Lại
      </NuxtLink>
      <button
        @click="proceedToSeats"
        :disabled="!selectedShowtimeId"
        class="flex-1 bg-primary-container text-white px-4 py-3 rounded-xl font-semibold hover:bg-primary-container/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Chọn Ghế →
      </button>
    </div>

    <!-- Summary -->
    <template #summary>
      <div class="space-y-4 text-sm">
        <div>
          <p class="text-on-surface-variant text-xs">Phim</p>
          <p class="font-semibold text-on-surface line-clamp-2">{{ selectedMovie?.name }}</p>
        </div>
        <div v-if="selectedShowtimeId" class="border-t border-glass-stroke pt-3">
          <p class="text-on-surface-variant text-xs mb-2">Suất Chiếu Chọn</p>
          <p class="font-semibold text-on-surface">
            {{ showtimes.find(s => s.id === selectedShowtimeId)?.branch_name }}
          </p>
          <p class="text-xs text-on-surface-variant">
            {{ formatTime(showtimes.find(s => s.id === selectedShowtimeId)?.starts_at || '') }}
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

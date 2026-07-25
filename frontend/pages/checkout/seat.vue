<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { useBooking } from '~/composables/useBooking'
import { movieService } from '~/services/api'
import { formatSeatLabel, formatPrice } from '~/utils/format'

definePageMeta({
  layout: 'checkout',
  middleware: 'auth'
})

const ticketsStore = useTicketsStore()
const { selectedShowtime, selectedSeats } = storeToRefs(ticketsStore)
const { toggleSeat } = useBooking()

// Interface chuẩn cho Seat
interface Seat {
  id: string
  row: string
  number: number
  type: 'standard' | 'vip' | 'couple'
  status: 'available' | 'selected' | 'occupied'
  price: number
}

const seats = ref<Seat[]>([])
const loading = ref(false)
const error = ref('')

interface SeatRow {
  row: string
  seats: Seat[]
}

const seatRows = computed(() => {
  const rows = new Map<string, Seat[]>()
  seats.value.forEach(seat => {
    if (!rows.has(seat.row)) {
      rows.set(seat.row, [])
    }
    rows.get(seat.row)!.push(seat)
  })
  const result: SeatRow[] = []
  rows.forEach((rowSeats, rowKey) => {
    result.push({ row: rowKey, seats: rowSeats })
  })
  return result
})

onMounted(async () => {
  if (!selectedShowtime.value) {
    await navigateTo('/checkout/cinema')
    return
  }

  loading.value = true
  try {
    const response = await movieService.getSeats(selectedShowtime.value.id)
    seats.value = response
  } catch (err) {
    error.value = 'Failed to load seats'
  } finally {
    loading.value = false
  }
})

const isSeatSelected = (seat: Seat) => {
  return selectedSeats.value.some(s => s.id === seat.id)
}

const handleSeatClick = (seat: Seat) => {
  toggleSeat(seat)
}

const proceedToCombo = () => {
  navigateTo('/checkout/combo')
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-on-surface mb-2">Chọn Ghế Ngồi</h2>
      <p class="text-sm text-on-surface-variant">
        {{ selectedShowtime?.branchName }} - {{ selectedShowtime?.screenName }}
      </p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin">
        <span class="material-symbols-outlined text-4xl text-primary-container">hourglass_empty</span>
      </div>
      <p class="text-sm text-on-surface-variant mt-2">Loading seats...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-error/10 border border-error/30 rounded-xl p-4 text-error text-sm">
      {{ error }}
    </div>

    <!-- Seat Grid -->
    <div v-else class="space-y-4">
      <!-- Screen -->
      <div class="text-center">
        <div class="inline-block bg-surface-variant text-on-surface-variant px-6 py-1 rounded-full text-xs font-semibold">
          Màn Hình
        </div>
      </div>

      <!-- Seats -->
      <div class="space-y-3">
        <div
          v-for="seatRow of seatRows"
          :key="seatRow.row"
          class="flex items-center justify-center gap-2"
        >
          <span class="w-6 text-center text-xs font-bold text-on-surface-variant">{{ seatRow.row }}</span>
          <div class="flex gap-1 flex-wrap justify-center">
            <button
              v-for="seat of seatRow.seats"
              :key="seat.id"
              @click="handleSeatClick(seat)"
              class="w-8 h-8 rounded text-xs font-bold transition-all"
              :class="isSeatSelected(seat)
                ? 'bg-primary-container text-white shadow-lg'
                : 'bg-surface-variant text-on-surface-variant hover:bg-primary-container/30'"
            >
              {{ seat.number }}
            </button>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="flex justify-center gap-6 text-xs mt-6 pt-4 border-t border-glass-stroke">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 bg-surface-variant rounded"></div>
          <span>Trống</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 bg-primary-container rounded"></div>
          <span>Chọn</span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-3 pt-4">
      <NuxtLink
        to="/checkout/cinema"
        class="flex-1 bg-surface-variant text-on-surface px-4 py-3 rounded-xl font-semibold hover:bg-surface-variant/80 transition-colors text-center"
      >
        ← Quay Lại
      </NuxtLink>
      <button
        @click="proceedToCombo"
        :disabled="selectedSeats.length === 0"
        class="flex-1 bg-primary-container text-white px-4 py-3 rounded-xl font-semibold hover:bg-primary-container/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Tiếp Tục ({{ selectedSeats.length }}) →
      </button>
    </div>

    <!-- Summary -->
     <NuxtLayout name="checkout">
    <template #summary>
      <div class="space-y-4 text-sm">
        <div>
          <p class="text-on-surface-variant text-xs">Suất Chiếu</p>
          <p class="font-semibold text-on-surface">{{ formatPrice(selectedShowtime?.price || 0) }}/vé</p>
        </div>
        <div>
          <p class="text-on-surface-variant text-xs">Số Ghế Chọn</p>
          <p class="font-semibold text-on-surface">{{ selectedSeats.length }} ghế</p>
        </div>
        <div v-if="selectedSeats.length > 0" class="border-t border-glass-stroke pt-3">
          <p class="text-on-surface-variant text-xs mb-2">Ghế Đã Chọn</p>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="seat of selectedSeats"
              :key="seat.id"
              class="bg-primary-container/20 text-primary-container text-xs px-2 py-1 rounded"
            >
              {{ formatSeatLabel(seat.row, seat.number) }}
            </span>
          </div>
        </div>
      </div>
    </template>
    </NuxtLayout>
  </div>
</template>


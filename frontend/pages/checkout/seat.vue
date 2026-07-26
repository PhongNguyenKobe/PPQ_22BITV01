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
<<<<<<< HEAD
const { selectedShowtime, selectedSeats } = storeToRefs(ticketsStore)
const { toggleSeat } = useBooking()
=======
const { selectedMovie, selectedCinema, selectedShowtime, selectedSeats, totalAmount } = storeToRefs(ticketsStore)

const backgroundStyle = computed(() => {
  if (!selectedMovie.value?.imageUrl) return {}
  return {
    backgroundImage: `linear-gradient(90deg, rgba(18,20,20,0.95) 0%, rgba(18,20,20,0.82) 24%, rgba(18,20,20,0.68) 56%, rgba(18,20,20,0.92) 100%), url('${selectedMovie.value.imageUrl}')`,
  }
})

const formattedMoviePrice = computed(() => {
  if (!selectedMovie.value?.price) return 'Đang cập nhật'
  return new Intl.NumberFormat('vi-VN').format(Number(selectedMovie.value.price) * 1000) + 'đ'
})
>>>>>>> f220d3b (SS12)

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
<<<<<<< HEAD
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
=======
  <section class="checkout-shell py-6 px-3 sm:px-5 md:px-8">
    <div class="checkout-hero max-w-[1500px] mx-auto" :style="backgroundStyle">
      <div class="checkout-overlay"></div>

      <div class="checkout-grid">
        <aside class="movie-column" v-if="selectedMovie">
          <img :src="selectedMovie.imageUrl" :alt="selectedMovie.name" class="movie-poster" />

          <div class="movie-meta">
            <h2 class="movie-title">{{ selectedMovie.name }}</h2>
            <div class="movie-badges">
              <span v-if="selectedMovie.rating" class="movie-rating">
                <span class="material-symbols-outlined text-sm text-yellow-400">star</span>
                {{ Number(selectedMovie.rating).toFixed(1) }}
              </span>
              <span class="movie-dot">•</span>
              <span>{{ selectedMovie.category || '2D' }}</span>
            </div>
            <p class="movie-price">Giá từ {{ formattedMoviePrice }}</p>
          </div>
        </aside>

        <main class="selection-column">
          <div class="booking-stepper">
            <div class="step done"><span>1</span><small>Chọn rạp</small></div>
            <div class="step-line active"></div>
            <div class="step done"><span>2</span><small>Chọn suất</small></div>
            <div class="step-line active"></div>
            <div class="step active"><span>3</span><small>Chọn ghế</small></div>
            <div class="step-line"></div>
            <div class="step"><span>4</span><small>Thanh toán</small></div>
          </div>

          <div class="selection-panel">
            <div class="selection-header">
              <h1>Chọn Ghế Ngồi</h1>
              <p>Chọn vị trí phù hợp trong phòng chiếu để tiếp tục thanh toán.</p>
            </div>
            <SeatSelection />
          </div>
        </main>

        <aside class="summary-column" v-if="selectedShowtime">
          <div class="summary-card">
            <h3>Vé Xem Phim</h3>

            <div class="summary-block">
              <div class="summary-row">
                <span>Rạp</span>
                <strong>{{ selectedCinema || selectedShowtime.branchName }}</strong>
              </div>
              <div class="summary-row">
                <span>Suất chiếu</span>
                <strong>{{ selectedShowtime.time }} • {{ selectedShowtime.date }}</strong>
              </div>
              <div class="summary-row">
                <span>Phòng</span>
                <strong>{{ selectedShowtime.screenName }}</strong>
              </div>
            </div>

            <div class="summary-seats">
              <p>Ghế đã chọn</p>
              <div v-if="selectedSeats.length > 0" class="seat-tags">
                <span v-for="seat in selectedSeats" :key="seat.id">{{ seat.row }}{{ seat.number }}</span>
              </div>
              <p v-else class="seat-empty">Chưa chọn ghế</p>
            </div>

            <div class="summary-total">
              <span>Tổng cộng</span>
              <strong>{{ totalAmount.toLocaleString() }} VNĐ</strong>
            </div>

            <button
              @click="handleProceedToPayment"
              :disabled="selectedSeats.length === 0"
              class="summary-next"
            >
              Tiếp tục thanh toán
>>>>>>> f220d3b (SS12)
            </button>
          </div>
        </aside>
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
<<<<<<< HEAD

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

=======
  </section>
</template>

<style scoped>
.checkout-shell { min-height: calc(100vh - 72px); }

.checkout-hero {
  position: relative;
  overflow: hidden;
  border-radius: 1.35rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background-color: #1a1c1c;
  background-position: center;
  background-size: cover;
}

.checkout-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(18, 20, 20, 0.1) 0%, rgba(18, 20, 20, 0.28) 100%);
}

.checkout-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 250px minmax(0, 1fr) 280px;
  gap: 1.5rem;
  padding: 1.5rem;
  align-items: start;
}

.movie-column,
.summary-card,
.selection-panel {
  background: rgba(31, 31, 31, 0.74);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.2rem;
}

.movie-column { padding: 1rem; }

.movie-poster {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
  border-radius: 1rem;
}

.movie-meta { margin-top: 1rem; }
.movie-title { font-size: 1.45rem; line-height: 1.08; font-weight: 900; color: #fff; }

.movie-badges {
  margin-top: 0.7rem;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: #d6d6d6;
  font-size: 0.88rem;
}

.movie-dot { color: rgba(255,255,255,0.45); }
.movie-rating { display: inline-flex; align-items: center; gap: 0.18rem; }
.movie-price { margin-top: 0.75rem; color: #fbbf24; font-weight: 800; }

.booking-stepper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin: 0.25rem 0 1rem;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  color: #9ca3af;
  font-size: 0.68rem;
  font-weight: 700;
}

.step span {
  width: 1.9rem;
  height: 1.9rem;
  border-radius: 9999px;
  background: rgba(255,255,255,0.12);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.step.active,
.step.done { color: #ffb4aa; }
.step.active span,
.step.done span { background: #ff7a1a; color: #fff; }

.step-line { width: 72px; height: 2px; background: rgba(255,255,255,0.14); }
.step-line.active { background: linear-gradient(90deg, #ff7a1a, #f59e0b); }

.selection-panel { padding: 1.35rem; }
.selection-header h1 { font-size: 2rem; line-height: 1.05; font-weight: 900; color: #fff; }
.selection-header p { margin-top: 0.45rem; color: #c8c8c8; font-size: 0.95rem; margin-bottom: 0.9rem; }

.summary-card { padding: 1.2rem; }
.summary-card h3 { color: #fff; font-size: 1.5rem; font-weight: 900; text-transform: uppercase; }

.summary-block {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed rgba(255,255,255,0.14);
  display: grid;
  gap: 0.85rem;
}

.summary-row { display: flex; flex-direction: column; gap: 0.3rem; }
.summary-row span { color: #aeb3bb; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
.summary-row strong { color: #fff; font-size: 0.92rem; }

.summary-seats { margin-top: 1rem; }
.summary-seats p { color: #aeb3bb; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }

.seat-tags { margin-top: 0.5rem; display: flex; flex-wrap: wrap; gap: 0.45rem; }
.seat-tags span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  border-radius: 0.6rem;
  padding: 0 0.6rem;
  background: rgba(255,122,26,0.14);
  color: #ffd1a8;
  font-size: 0.76rem;
  font-weight: 700;
}

.seat-empty { margin-top: 0.55rem; color: #c7cad0; font-size: 0.9rem; text-transform: none; letter-spacing: normal; }

.summary-total {
  margin-top: 1.1rem;
  border-top: 1px dashed rgba(255,255,255,0.14);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.summary-total span { color: #aeb3bb; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
.summary-total strong { color: #fff; font-size: 1.2rem; font-weight: 900; }

.summary-next {
  margin-top: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 44px;
  border-radius: 0.8rem;
  background: #ff7a1a;
  color: #fff;
  font-weight: 800;
  transition: all 0.2s ease;
}

.summary-next:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

@media (max-width: 1200px) {
  .checkout-grid { grid-template-columns: 240px minmax(0, 1fr); }
  .summary-column { grid-column: 1 / -1; }
}

@media (max-width: 992px) {
  .checkout-grid { grid-template-columns: 1fr; }
  .booking-stepper { overflow-x: auto; justify-content: flex-start; padding-bottom: 0.3rem; }
  .step-line { min-width: 44px; }
}
</style>
>>>>>>> f220d3b (SS12)

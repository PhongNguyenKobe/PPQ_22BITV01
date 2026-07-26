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
const { selectedMovie, selectedCinema, selectedShowtime, selectedSeats, totalAmount } = storeToRefs(ticketsStore)
const { toggleSeat } = useBooking()

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
  error.value = ''
  try {
    const response = await movieService.getSeats(selectedShowtime.value.id)
    seats.value = response
  } catch (err) {
    console.error('Failed to load seats:', err)
    error.value = 'Không thể tải sơ đồ ghế. Vui lòng thử lại.'
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

const handleProceedToPayment = () => {
  if (selectedSeats.value.length === 0) return
  navigateTo('/checkout/combo')
}
</script>

<template>
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

            <!-- Loading -->
            <div v-if="loading" class="selection-empty">Đang tải sơ đồ ghế...</div>

            <!-- Error -->
            <div v-else-if="error" class="selection-empty">
              <p>{{ error }}</p>
            </div>

            <!-- Seat Grid -->
            <div v-else class="seat-map">
              <div class="screen-indicator">
                <div class="screen-label">Màn Hình</div>
              </div>

              <div class="seat-rows">
                <div
                  v-for="seatRow of seatRows"
                  :key="seatRow.row"
                  class="seat-row"
                >
                  <span class="row-label">{{ seatRow.row }}</span>
                  <div class="row-seats">
                    <button
                      v-for="seat of seatRow.seats"
                      :key="seat.id"
                      @click="handleSeatClick(seat)"
                      class="seat-btn"
                      :class="isSeatSelected(seat) ? 'seat-selected' : 'seat-available'"
                    >
                      {{ seat.number }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="seat-legend">
                <div class="legend-item">
                  <span class="legend-swatch seat-available"></span>
                  <span>Trống</span>
                </div>
                <div class="legend-item">
                  <span class="legend-swatch seat-selected"></span>
                  <span>Đang chọn</span>
                </div>
              </div>
            </div>
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
                <span v-for="seat in selectedSeats" :key="seat.id">
                  {{ formatSeatLabel(seat.row, seat.number) }}
                </span>
              </div>
              <p v-else class="seat-empty">Chưa chọn ghế</p>
            </div>

            <div class="summary-total">
              <span>Tổng cộng</span>
              <strong>{{ formatPrice(totalAmount) }}</strong>
            </div>

            <button
              @click="handleProceedToPayment"
              :disabled="selectedSeats.length === 0"
              class="summary-next"
            >
              Tiếp tục thanh toán
            </button>

            <NuxtLink to="/checkout/cinema" class="summary-back-link">
              ← Đổi rạp / suất chiếu
            </NuxtLink>
          </div>
        </aside>
      </div>
    </div>
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

.selection-empty {
  margin-top: 1rem;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #c7cad0;
}

.seat-map { margin-top: 0.5rem; }

.screen-indicator { display: flex; justify-content: center; margin-bottom: 1.5rem; }
.screen-label {
  background: rgba(255,255,255,0.08);
  color: #e5e7eb;
  padding: 0.35rem 1.5rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.seat-rows { display: flex; flex-direction: column; gap: 0.6rem; }

.seat-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
}

.row-label {
  width: 1.5rem;
  text-align: center;
  font-size: 0.72rem;
  font-weight: 800;
  color: #9ca3af;
}

.row-seats { display: flex; gap: 0.3rem; flex-wrap: wrap; justify-content: center; }

.seat-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 0.4rem;
  font-size: 0.72rem;
  font-weight: 700;
  transition: all 0.15s ease;
}

.seat-available {
  background: rgba(255,255,255,0.08);
  color: #d6d6d6;
}

.seat-available:hover {
  background: rgba(255,122,26,0.22);
}

.seat-selected {
  background: #ff7a1a;
  color: #fff;
  box-shadow: 0 0 0 2px rgba(255,122,26,0.35);
}

.seat-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px dashed rgba(255,255,255,0.14);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #c7cad0;
}

.legend-swatch {
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 0.3rem;
  display: inline-block;
}

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

.summary-back-link {
  margin-top: 0.9rem;
  display: block;
  text-align: center;
  color: #c7cad0;
  font-size: 0.82rem;
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
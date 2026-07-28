<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const ticketsStore = useTicketsStore()
const { selectedMovie, selectedCinema, selectedShowtime, selectedSeats, totalAmount } = storeToRefs(ticketsStore)
const showtimeExpired = computed(() => isShowtimeExpired(selectedShowtime.value))

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

onMounted(() => {
  // Redirect back to cinema selection if no showtime has been selected
  if (!selectedShowtime.value) {
    navigateTo('/checkout/cinema')
  }
})

function handleProceedToPayment() {
  if (selectedSeats.value.length === 0 || showtimeExpired.value) return
  navigateTo('/checkout/payment')
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
            <div v-if="showtimeExpired" class="mb-4 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-300">
              <strong>Đã hết thời gian mua vé</strong>
              <p class="mt-1 text-sm">Suất chiếu này đã bắt đầu hoặc ngừng bán. Vui lòng quay lại chọn suất khác.</p>
              <NuxtLink to="/checkout/showtime" class="mt-3 inline-block font-bold underline">Chọn suất khác</NuxtLink>
            </div>
            <div class="selection-header">
              <h1>Chọn Ghế Ngồi</h1>
              <p>Chọn vị trí phù hợp trong phòng chiếu để tiếp tục thanh toán.</p>
            </div>
            <SeatSelection v-if="!showtimeExpired" />
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
              :disabled="selectedSeats.length === 0 || showtimeExpired"
              class="summary-next"
            >
              Tiếp tục thanh toán
            </button>
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
  grid-template-columns: 220px minmax(520px, 1fr) 280px;
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
.selection-column { min-width: 0; }
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

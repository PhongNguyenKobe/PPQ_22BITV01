<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { movieService, type Showtime } from '~/services/api'

definePageMeta({
  layout: 'default'
})

const router = useRouter()
const ticketsStore = useTicketsStore()
const { selectedMovie, selectedCinema, selectedShowtime } = storeToRefs(ticketsStore)

const showtimes = ref<Showtime[]>([])
const loading = ref(false)

// Redirect if no movie/cinema selected
onMounted(async () => {
  if (!selectedMovie.value || !selectedCinema.value) {
    return router.push('/products')
  }
  
  // Fetch showtimes from API
  loading.value = true
  try {
    const targetMovieId = selectedMovie.value.backendMovieId || selectedMovie.value.id
    const allShowtimes = await movieService.getShowtimes(String(targetMovieId))
    // Filter by selected cinema
    showtimes.value = allShowtimes.filter(st => st.branchName === selectedCinema.value)
  } catch (e) {
    console.error('Failed to load showtimes:', e)
    showtimes.value = []
  } finally {
    loading.value = false
  }
})

// Get showtimes for selected movie + cinema, grouped by date
const showtimesByDate = computed(() => {
  const filtered = showtimes.value

  // Group by date
  const grouped: { [key: string]: Showtime[] } = {}
  filtered.forEach(st => {
    if (!grouped[st.date]) {
      grouped[st.date] = []
    }
    grouped[st.date].push(st)
  })

  // Sort dates
  return Object.keys(grouped)
    .sort()
    .reduce((acc, date) => {
      acc[date] = grouped[date].sort((a, b) => a.time.localeCompare(b.time))
      return acc
    }, {} as { [key: string]: Showtime[] })
})

const totalShowtimes = computed(() => showtimes.value.length)

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

// Format date for display
const formatDate = (dateStr: string) => {
  const [year, month, day] = dateStr.split('-')
  const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
  const dayOfWeek = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'][date.getDay()]
  return `${dayOfWeek} ${day}/${month}`
}

// Get screen type from screenName
const getScreenType = (screenName: string) => {
  if (screenName.includes('IMAX')) return 'IMAX'
  if (screenName.includes('4DX')) return '4DX'
  if (screenName.includes('3D')) return '3D'
  return '2D'
}

// Select showtime and navigate
function handleSelectShowtime(showtime: Showtime) {
  ticketsStore.selectShowtime(showtime)
  router.push('/checkout/seat')
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
            <div class="step active"><span>2</span><small>Chọn suất</small></div>
            <div class="step-line"></div>
            <div class="step"><span>3</span><small>Chọn ghế</small></div>
            <div class="step-line"></div>
            <div class="step"><span>4</span><small>Thanh toán</small></div>
          </div>

          <div class="selection-panel">
            <div class="selection-header">
              <h1>Chọn Suất Chiếu</h1>
              <p>{{ selectedCinema }} có {{ totalShowtimes }} suất chiếu cho phim này.</p>
            </div>

            <div v-if="loading" class="selection-empty">Đang tải suất chiếu...</div>

            <div v-else-if="Object.keys(showtimesByDate).length > 0" class="showtime-groups">
              <div v-for="(group, date) in showtimesByDate" :key="date" class="group-block">
                <h3>{{ formatDate(date) }}</h3>
                <div class="showtime-list">
                  <button
                    v-for="showtime in group"
                    :key="showtime.id"
                    @click="handleSelectShowtime(showtime)"
                    class="showtime-chip"
                    :class="selectedShowtime?.id === showtime.id ? 'chip-active' : ''"
                  >
                    <strong>{{ showtime.time }}</strong>
                    <span>{{ getScreenType(showtime.screenName) }} • {{ showtime.screenName }}</span>
                    <em>{{ showtime.price.toLocaleString('vi-VN') }}đ</em>
                  </button>
                </div>
              </div>
            </div>

            <div v-else class="selection-empty">
              <p>Không có suất chiếu nào khả dụng.</p>
              <button @click="$router.back()" class="summary-back mt-2">Chọn rạp khác</button>
            </div>
          </div>
        </main>

        <aside class="summary-column">
          <div class="summary-card">
            <h3>Vé Xem Phim</h3>

            <div class="summary-block">
              <div class="summary-row">
                <span>Phim</span>
                <strong>{{ selectedMovie?.name || 'Đang chọn' }}</strong>
              </div>
              <div class="summary-row">
                <span>Rạp</span>
                <strong>{{ selectedCinema || 'Chưa chọn' }}</strong>
              </div>
              <div class="summary-row">
                <span>Suất hiện tại</span>
                <strong>{{ selectedShowtime ? `${selectedShowtime.time} - ${selectedShowtime.date}` : 'Chưa chọn' }}</strong>
              </div>
            </div>

            <div class="summary-note">
              Chọn một suất chiếu ở giữa để tiếp tục sang bước chọn ghế.
            </div>

            <NuxtLink to="/checkout/cinema" class="summary-back">
              Đổi rạp
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

.movie-title {
  font-size: 1.45rem;
  line-height: 1.08;
  font-weight: 900;
  color: #fff;
}

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

.selection-header h1 {
  font-size: 2rem;
  line-height: 1.05;
  font-weight: 900;
  color: #fff;
}

.selection-header p {
  margin-top: 0.45rem;
  color: #c8c8c8;
  font-size: 0.95rem;
}

.showtime-groups { margin-top: 1rem; display: grid; gap: 1rem; }
.group-block h3 { color: #fff; font-weight: 800; margin-bottom: 0.65rem; }

.showtime-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.showtime-chip {
  text-align: left;
  border-radius: 0.9rem;
  border: 1px solid rgba(255, 122, 26, 0.26);
  background: rgba(255,255,255,0.03);
  padding: 0.8rem;
  display: grid;
  gap: 0.35rem;
  transition: all 0.2s ease;
}

.showtime-chip:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 122, 26, 0.5);
}

.showtime-chip strong { color: #fff; font-size: 1.25rem; }
.showtime-chip span { color: #c7cad0; font-size: 0.8rem; }
.showtime-chip em { color: #ffd1a8; font-size: 0.8rem; font-style: normal; font-weight: 700; }

.chip-active {
  border-color: rgba(255, 122, 26, 0.65);
  background: rgba(255, 122, 26, 0.12);
}

.summary-card { padding: 1.2rem; }

.summary-card h3 {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 900;
  text-transform: uppercase;
}

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

.summary-note {
  margin-top: 1.1rem;
  color: #c7cad0;
  font-size: 0.9rem;
  line-height: 1.7;
}

.summary-back {
  margin-top: 1.2rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 44px;
  border-radius: 0.8rem;
  background: #ff7a1a;
  color: #fff;
  font-weight: 800;
}

.selection-empty {
  margin-top: 1rem;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  text-align: center;
  color: #c7cad0;
}

@media (max-width: 1200px) {
  .checkout-grid { grid-template-columns: 240px minmax(0, 1fr); }
  .summary-column { grid-column: 1 / -1; }
}

@media (max-width: 992px) {
  .checkout-grid { grid-template-columns: 1fr; }
  .showtime-list { grid-template-columns: 1fr; }
  .booking-stepper { overflow-x: auto; justify-content: flex-start; padding-bottom: 0.3rem; }
  .step-line { min-width: 44px; }
}
</style>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { movieService, type Showtime } from '~/services/api'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const router = useRouter()
const ticketsStore = useTicketsStore()
const { selectedMovie, selectedCinema } = storeToRefs(ticketsStore)

const showtimes = ref<Showtime[]>([])
const loading = ref(false)
const requiresCatalogMapping = ref(false)

// Redirect if no movie selected
onMounted(async () => {
  if (!selectedMovie.value) {
    return router.push('/products')
  }
  
  // Fetch showtimes for the selected movie from API
  if (selectedMovie.value) {
    loading.value = true
    try {
      let targetMovieId = selectedMovie.value.backendMovieId || selectedMovie.value.id
      if (!selectedMovie.value.backendMovieId) {
        const movieIdAsString = String(selectedMovie.value.id)
        const backendMovies = await movieService.getPublic()
        const byTmdbId = backendMovies.find((movie) => {
          const match = movie.trailer?.match(/themoviedb\.org\/movie\/(\d+)/i)
          return match ? match[1] === movieIdAsString : false
        })
        const selectedTitle = String(selectedMovie.value.name || selectedMovie.value.title || '')
          .trim()
          .toLocaleLowerCase()
        const byTitle = backendMovies.find((movie) => movie.title.trim().toLocaleLowerCase() === selectedTitle)
        const mappedMovie = byTmdbId || byTitle

        if (mappedMovie) {
          targetMovieId = mappedMovie.id
          ticketsStore.selectMovie({
            ...selectedMovie.value,
            backendMovieId: mappedMovie.id,
          })
        } else {
          requiresCatalogMapping.value = true
        }
      }

      let allShowtimes = await movieService.getShowtimes(String(targetMovieId))
      // A saved checkout can point at a movie record from an earlier catalog.
      // Retry against the current backend catalog by title before declaring no showtimes.
      if (!allShowtimes.length) {
        const backendMovies = await movieService.getAll()
        const selectedTitle = String(selectedMovie.value.name || selectedMovie.value.title || '')
          .trim()
          .toLocaleLowerCase()
        const currentMovie = backendMovies.find((movie) => movie.title.trim().toLocaleLowerCase() === selectedTitle)
        if (currentMovie && currentMovie.id !== targetMovieId) {
          targetMovieId = currentMovie.id
          ticketsStore.selectMovie({
            ...selectedMovie.value,
            backendMovieId: currentMovie.id,
          })
          allShowtimes = await movieService.getShowtimes(String(targetMovieId))
        }
      }
      showtimes.value = allShowtimes
      if (allShowtimes.length > 0) {
        requiresCatalogMapping.value = false
        const minimumPrice = Math.min(...allShowtimes.map((showtime) => showtime.price))
        selectedMovie.value = {
          ...selectedMovie.value,
          price: minimumPrice / 1000,
        }
      }
    } catch (e) {
      console.error('Failed to load showtimes for cinema selection:', e)
      showtimes.value = []
    } finally {
      loading.value = false
    }
  }
})

// Get available cinemas for selected movie
const availableCinemas = computed(() => {
  if (!showtimes.value.length) return []
  
  const cinemaSet = new Set<string>()
  showtimes.value.forEach(st => cinemaSet.add(st.branchName))
  
  return Array.from(cinemaSet).sort()
})

const cinemaCards = computed(() =>
  availableCinemas.value.map((cinema) => {
    const items = showtimes.value.filter((st) => st.branchName === cinema)
    const formats = Array.from(
      new Set(
        items.map((st) => {
          if (st.screenName.includes('IMAX')) return 'IMAX'
          if (st.screenName.includes('4DX')) return '4DX'
          if (st.screenName.includes('3D')) return '3D'
          return '2D'
        }),
      ),
    )

    return {
      name: cinema,
      count: items.length,
      previewTimes: items.slice(0, 4).map((st) => st.time),
      formats,
    }
  }),
)

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

// Show count of showtimes per cinema
// Select cinema and navigate to showtime
function handleSelectCinema(cinema: string) {
  ticketsStore.selectCinema(cinema)
  router.push('/checkout/showtime')
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
            <div class="step active"><span>1</span><small>Chọn rạp</small></div>
            <div class="step-line active"></div>
            <div class="step"><span>2</span><small>Chọn suất</small></div>
            <div class="step-line"></div>
            <div class="step"><span>3</span><small>Chọn ghế</small></div>
            <div class="step-line"></div>
            <div class="step"><span>4</span><small>Thanh toán</small></div>
          </div>

          <div class="selection-panel">
            <div class="selection-header">
              <h1>Chọn Rạp Chiếu</h1>
              <p>
                <span v-if="selectedMovie">{{ selectedMovie.name }}</span>
                <span v-else>Phim đã chọn</span>
                có {{ totalShowtimes }} suất chiếu khả dụng trong hệ thống.
              </p>
            </div>

            <div v-if="loading" class="selection-empty">Đang tải danh sách rạp...</div>

            <div v-else-if="cinemaCards.length > 0" class="cinema-list">
              <button
                v-for="cinema in cinemaCards"
                :key="cinema.name"
                @click="handleSelectCinema(cinema.name)"
                class="cinema-card"
              >
                <div class="cinema-card-top">
                  <div>
                    <h3>{{ cinema.name }}</h3>
                    <p>{{ cinema.count }} suất chiếu</p>
                  </div>
                  <span class="material-symbols-outlined">arrow_forward</span>
                </div>

                <div class="cinema-times">
                  <span v-for="time in cinema.previewTimes" :key="time">{{ time }}</span>
                </div>

                <div class="cinema-formats">
                  <span v-for="format in cinema.formats" :key="format">{{ format }}</span>
                </div>
              </button>
            </div>

            <div v-else class="selection-empty">
              <p>Không có rạp chiếu nào cho phim này.</p>
              <p v-if="requiresCatalogMapping" class="mapping-note">
                Phim này đang lấy từ TMDB, nhưng chưa được map vào catalog nội bộ để mở suất chiếu.
              </p>
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
                <span>Suất chiếu</span>
                <strong>{{ totalShowtimes }} lựa chọn</strong>
              </div>
            </div>

            <div class="summary-note">
              Chọn một rạp ở giữa để tiếp tục sang bước chọn suất chiếu.
            </div>

            <NuxtLink to="/products" class="summary-back">
              Đổi phim khác
            </NuxtLink>
          </div>
        </aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
.checkout-shell {
  min-height: calc(100vh - 72px);
}

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

.movie-column {
  padding: 1rem;
}

.movie-poster {
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  border-radius: 1rem;
}

.movie-meta {
  margin-top: 1rem;
}

.movie-title {
  font-size: 1.65rem;
  line-height: 1.05;
  font-weight: 900;
  color: #fff;
}

.movie-badges {
  margin-top: 0.7rem;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: #d6d6d6;
  font-size: 0.9rem;
}

.movie-rating {
  display: inline-flex;
  align-items: center;
  gap: 0.18rem;
}

.movie-dot {
  color: rgba(255, 255, 255, 0.45);
}

.movie-price {
  margin-top: 0.75rem;
  color: #fbbf24;
  font-weight: 800;
}

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
  background: rgba(255, 255, 255, 0.12);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.step.active {
  color: #ffb4aa;
}

.step.active span {
  background: #ff7a1a;
  color: #fff;
}

.step-line {
  width: 72px;
  height: 2px;
  background: rgba(255, 255, 255, 0.14);
}

.step-line.active {
  background: linear-gradient(90deg, #ff7a1a, #f59e0b);
}

.selection-panel {
  padding: 1.35rem;
}

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

.cinema-list {
  margin-top: 1.1rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.cinema-card {
  text-align: left;
  border-radius: 1rem;
  border: 1px solid rgba(255, 122, 26, 0.28);
  background: rgba(255, 255, 255, 0.03);
  padding: 1rem;
  transition: all 0.2s ease;
}

.cinema-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 122, 26, 0.58);
  background: rgba(255, 122, 26, 0.08);
}

.cinema-card-top {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
}

.cinema-card h3 {
  color: #fff;
  font-size: 1rem;
  font-weight: 800;
}

.cinema-card p {
  margin-top: 0.3rem;
  font-size: 0.85rem;
  color: #c7cad0;
}

.cinema-card .material-symbols-outlined {
  color: #ffb4aa;
}

.cinema-times,
.cinema-formats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.9rem;
}

.cinema-times span,
.cinema-formats span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  border-radius: 0.65rem;
  padding: 0 0.7rem;
  font-size: 0.76rem;
  font-weight: 700;
}

.cinema-times span {
  background: rgba(255, 122, 26, 0.14);
  color: #ffd1a8;
}

.cinema-formats span {
  background: rgba(255, 255, 255, 0.08);
  color: #e5e7eb;
}

.summary-card {
  padding: 1.2rem;
}

.summary-card h3 {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 900;
  text-transform: uppercase;
}

.summary-block {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.14);
  display: grid;
  gap: 0.85rem;
}

.summary-row {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.summary-row span {
  color: #aeb3bb;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-row strong {
  color: #fff;
  font-size: 0.92rem;
}

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
  text-align: center;
  color: #c7cad0;
  gap: 0.55rem;
}

.mapping-note {
  font-size: 0.8rem;
  max-width: 420px;
}

@media (max-width: 1200px) {
  .checkout-grid {
    grid-template-columns: 240px minmax(0, 1fr);
  }

  .summary-column {
    grid-column: 1 / -1;
  }
}

@media (max-width: 992px) {
  .checkout-grid {
    grid-template-columns: 1fr;
  }

  .cinema-list {
    grid-template-columns: 1fr;
  }

  .booking-stepper {
    overflow-x: auto;
    justify-content: flex-start;
    padding-bottom: 0.3rem;
  }

  .step-line {
    min-width: 44px;
  }
}
</style>

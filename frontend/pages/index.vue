<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductsStore } from '~/store/products'
import { movieService, youtubeTrailerLink, type Showtime } from '~/services/api'
import { useRouter } from 'vue-router'
import { useTicketsStore } from '~/store/tickets'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'default'
})

const productsStore = useProductsStore()
const { products } = storeToRefs(productsStore)
const router = useRouter()
const ticketsStore = useTicketsStore()
const userStore = useUserStore()
const movieShowtimes = ref<Record<string, Showtime[]>>({})
const showtimesLoaded = ref(false)

// Gọi fetchProducts không cần await top-level để tránh block render SSR/Client
onMounted(() => {
  if (!products.value || products.value.length === 0) {
    productsStore.fetchProducts()
  }
})

watch(products, async (items) => {
  showtimesLoaded.value = false
  const nowShowing = items.filter((movie) => movie.status === 'NOW_SHOWING' && movie.backendMovieId)
  const entries = await Promise.all(
    nowShowing.map(async (movie) => [
      String(movie.id),
      await movieService.getShowtimes(String(movie.backendMovieId)).catch(() => []),
    ] as const),
  )
  const now = Date.now()
  movieShowtimes.value = Object.fromEntries(
    entries.map(([movieId, showtimes]) => [
      movieId,
      showtimes.filter((showtime) => {
        const startsAt = new Date(`${showtime.date}T${showtime.time}:00`).getTime()
        const closesAt = showtime.bookingClosesAt ? new Date(showtime.bookingClosesAt).getTime() : startsAt
        return startsAt > now && closesAt > now
      }),
    ]),
  )
  showtimesLoaded.value = true
}, { immediate: true })

// =========================================================================
// HERO SECTION LOGIC & AUTOPLAY
// =========================================================================
const activeHeroIndex = ref(0)
const AUTOPLAY_INTERVAL = 5000
let heroTimer: ReturnType<typeof setInterval> | null = null

const heroMovies = computed(() => {
  if (!products.value || !Array.isArray(products.value)) return []
  const clean = products.value.filter((movie) =>
    showtimesLoaded.value
    && movie.status === 'NOW_SHOWING'
    && movie.name.trim().length >= 3
    && movie.imageUrl
    && !movie.imageUrl.includes('movie-placeholder')
    && (movieShowtimes.value[String(movie.id)]?.length || 0) > 0
  )
  
  const sorted = [...clean].sort((a, b) => {
    const countA = movieShowtimes.value[String(a.id)]?.length || 0
    const countB = movieShowtimes.value[String(b.id)]?.length || 0
    if (countA !== countB) return countB - countA
    const nearestA = new Date(`${movieShowtimes.value[String(a.id)]![0]!.date}T${movieShowtimes.value[String(a.id)]![0]!.time}:00`).getTime()
    const nearestB = new Date(`${movieShowtimes.value[String(b.id)]![0]!.date}T${movieShowtimes.value[String(b.id)]![0]!.time}:00`).getTime()
    return nearestA - nearestB
  })

  return sorted.slice(0, 5)
})

const currentHeroMovie = computed(() => {
  if (!heroMovies.value.length) return null
  return heroMovies.value[activeHeroIndex.value] || heroMovies.value[0]
})

const currentHeroShowtimes = computed(() =>
  currentHeroMovie.value ? movieShowtimes.value[String(currentHeroMovie.value.id)] || [] : [],
)

const nearestHeroShowtimeLabel = computed(() => {
  const nearest = currentHeroShowtimes.value[0]
  return nearest ? showtimeLabel(nearest) : ''
})

const upcomingMovies = computed(() => {
  return products.value.filter((movie) => movie.status === 'UPCOMING').slice(0, 8)
})

function setHeroMovie(index: number) {
  activeHeroIndex.value = index
  restartHeroAutoplay()
}

function nextHeroMovie() {
  if (!heroMovies.value.length) return
  activeHeroIndex.value = (activeHeroIndex.value + 1) % heroMovies.value.length
}

function startHeroAutoplay() {
  stopHeroAutoplay()
  if (heroMovies.value.length > 1) {
    heroTimer = setInterval(nextHeroMovie, AUTOPLAY_INTERVAL)
  }
}

function stopHeroAutoplay() {
  if (heroTimer) {
    clearInterval(heroTimer)
    heroTimer = null
  }
}

function restartHeroAutoplay() {
  stopHeroAutoplay()
  startHeroAutoplay()
}

watch(heroMovies, (newVal) => {
  if (activeHeroIndex.value >= newVal.length) {
    activeHeroIndex.value = 0
  }
  if (newVal.length > 1 && !heroTimer) {
    startHeroAutoplay()
  }
}, { immediate: true })

// Helper lấy dữ liệu an toàn
function getMovieTitle(movie: any) {
  return movie?.title || movie?.name || 'SIÊU PHẨM CÔNG CHIẾU'
}

function getMovieDesc(movie: any) {
  return movie?.description || 'Thưởng thức trải nghiệm điện ảnh chân thực với chuẩn âm thanh Dolby Atmos và màn hình IMAX thế hệ mới.'
}

function getMovieImage(movie: any) {
  const image = movie?.image || movie?.imageUrl
  return image && !image.includes('movie-placeholder')
    ? image
    : '/images/movie-placeholder.svg'
}

function bookMovie(movie: any) {
  if (!movie) return
  ticketsStore.selectMovie({
    id: movie.id,
    name: movie.name,
    backendMovieId: movie.backendMovieId || null,
    imageUrl: movie.imageUrl,
    category: movie.category,
    price: movie.price,
    rating: movie.rating || null,
    description: movie.description,
    trailerUrl: movie.trailerUrl || null,
  })
  router.push('/checkout/cinema')
}

function bookHeroMovie() {
  bookMovie(currentHeroMovie.value)
}

function movieSchedule(movieId: string | number) {
  return (movieShowtimes.value[String(movieId)] || []).slice(0, 4)
}

function moviePrice(movie: any) {
  const prices = (movieShowtimes.value[String(movie.id)] || [])
    .map((showtime) => showtime.price)
    .filter((price) => Number.isFinite(price) && price > 0)
  const price = prices.length ? Math.min(...prices) : Number(movie.price) * 1000
  return new Intl.NumberFormat('vi-VN').format(price)
}

function showtimeLabel(showtime: Showtime) {
  const date = new Date(`${showtime.date}T${showtime.time}:00`)
  const today = new Date()
  const isToday = date.toDateString() === today.toDateString()
  return `${isToday ? 'Hôm nay' : date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })} · ${showtime.time}`
}

function openHeroTrailer() {
  const movie = currentHeroMovie.value
  if (!movie || !import.meta.client) return
  window.open(youtubeTrailerLink(movie.trailerUrl, movie.name), '_blank', 'noopener,noreferrer')
}

// =========================================================================
// SCROLL REVEAL ANIMATION & LIFECYCLE
// =========================================================================
let observer: IntersectionObserver | null = null

onMounted(() => {
  startHeroAutoplay()

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-active')
        }
      })
    },
    { threshold: 0.15 }
  )
  document.querySelectorAll('.reveal').forEach((el) => observer?.observe(el))
})

onUnmounted(() => {
  stopHeroAutoplay()
  if (observer) observer.disconnect()
})

const nowShowingMovies = computed(() => {
  return products.value.filter(
    (movie) => movie.status === 'NOW_SHOWING' && movie.name.trim().length >= 3,
  ).slice(0, 8)
})

// =========================================================================
// 2. XOAY VÒNG VÔ TẬN: COMBO BẮP NƯỚC
// =========================================================================
const comboIndex = ref(0)
const comboPromotions = [
  {
    id: 'combo-1',
    name: 'Combo Solo Classic',
    tag: 'TIẾT KIỆM',
    price: '79.000đ',
    originalPrice: '110.000đ',
    desc: '1 Bắp Rang Bơ giòn rụm + 1 Nước Ngọt mát lạnh.',
    image: 'https://images.unsplash.com/photo-1578844251758-2f71da64c96f?q=80&w=1000&auto=format&fit=crop'
  },
  {
    id: 'combo-2',
    name: 'Combo AI Cinema Couple',
    tag: 'BÁN CHẠY NHẤT',
    price: '139.000đ',
    originalPrice: '190.000đ',
    desc: '2 Bắp Lớn vị tự chọn + 2 Nước Lớn + 1 Quà tặng Phim độc quyền.',
    image: 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?q=80&w=1000&auto=format&fit=crop'
  },
  {
    id: 'combo-3',
    name: 'Combo Party Family Pass',
    tag: 'ƯU ĐÃI NHÓM',
    price: '229.000đ',
    originalPrice: '310.000đ',
    desc: '3 Bắp Size L + 4 Nước Lớn + Phần Hotdog Nóng Hổi giòn rụm.',
    image: 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=1000&auto=format&fit=crop'
  }
]

function nextCombo() {
  comboIndex.value = (comboIndex.value + 1) % comboPromotions.length
}

function prevCombo() {
  comboIndex.value = (comboIndex.value - 1 + comboPromotions.length) % comboPromotions.length
}

const visibleCombos = computed(() => {
  const list = comboPromotions
  const len = list.length
  if (!len) return []

  const prevIdx = (comboIndex.value - 1 + len) % len
  const currIdx = comboIndex.value % len
  const nextIdx = (comboIndex.value + 1) % len

  return [
    { ...list[prevIdx], position: 'left' },
    { ...list[currIdx], position: 'center' },
    { ...list[nextIdx], position: 'right' }
  ]
})

// =========================================================================
// 3. DỮ LIỆU ĐẶT VÉ NHANH & TỰ ĐỘNG TÍNH NGÀY CHIẾU
// =========================================================================
const selectedCinema = ref('')
const selectedDate = ref('')
const allOpenShowtimes = computed(() => Object.values(movieShowtimes.value).flat())
const cinemas = computed(() =>
  [...new Set(allOpenShowtimes.value.map(item => item.branchName).filter(Boolean))].sort(),
)

// Tạo danh sách 3 ngày chiếu gần nhất tự động
const dates = computed(() => {
  return [...new Set(
    allOpenShowtimes.value
      .filter(item => !selectedCinema.value || item.branchName === selectedCinema.value)
      .map(item => item.date),
  )].sort().slice(0, 7).map(value => {
    const date = new Date(`${value}T00:00:00`)
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(today.getDate() + 1)
    const prefix = date.toDateString() === today.toDateString()
      ? 'Hôm nay'
      : date.toDateString() === tomorrow.toDateString()
        ? 'Ngày mai'
        : date.toLocaleDateString('vi-VN', { weekday: 'short' })
    return {
      value,
      label: `${prefix} (${date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })})`,
    }
  })
})

watch(cinemas, value => {
  if (!value.includes(selectedCinema.value)) selectedCinema.value = value[0] || ''
}, { immediate: true })
watch([dates, selectedCinema], ([value]) => {
  if (!value.some(item => item.value === selectedDate.value)) selectedDate.value = value[0]?.value || ''
}, { immediate: true })

const quickBookingMovies = computed(() =>
  nowShowingMovies.value
    .map(movie => ({
      movie,
      schedules: (movieShowtimes.value[String(movie.id)] || [])
        .filter(item => item.branchName === selectedCinema.value && item.date === selectedDate.value)
        .sort((a, b) => a.time.localeCompare(b.time)),
    }))
    .filter(item => item.schedules.length > 0)
    .slice(0, 6),
)

function chooseQuickShowtime(movie: any, showtime: Showtime) {
  ticketsStore.selectMovie({
    id: movie.id,
    name: movie.name,
    backendMovieId: movie.backendMovieId || null,
    imageUrl: movie.imageUrl,
    category: movie.category,
    price: showtime.price / 1000,
    rating: movie.rating || null,
    description: movie.description,
    trailerUrl: movie.trailerUrl || null,
  })
  ticketsStore.selectCinema(showtime.branchName)
  ticketsStore.selectShowtime(showtime)
  if (!userStore.isAuthenticated) {
    router.push({ path: '/login', query: { redirect: '/checkout/seat' } })
    return
  }
  router.push('/checkout/seat')
}
</script>

<template>
  <div
    class="relative w-full bg-[#121414] text-[#e3e2e2] font-sans overflow-x-hidden selection:bg-[#e50914] selection:text-white">

    <!-- HERO SECTION -->
    <section
      class="relative w-full h-[88vh] min-h-[650px] flex items-center overflow-hidden border-b border-[#5e3f3b]/30 bg-[#121414] select-none"
      @mouseenter="stopHeroAutoplay" @mouseleave="startHeroAutoplay">
      <div v-for="(movie, idx) in heroMovies" :key="'bg-' + (movie.id || idx)"
        class="absolute inset-0 z-0 transition-all duration-1000 ease-in-out pointer-events-none"
        :class="idx === activeHeroIndex ? 'opacity-100 scale-100' : 'opacity-0 scale-105'">
        <img :src="getMovieImage(movie)" :alt="getMovieTitle(movie)"
          class="w-full h-full object-cover filter brightness-[0.3] contrast-125" />
        <div class="absolute inset-0 bg-gradient-to-t from-[#121414] via-[#121414]/50 to-[#121414]/80"></div>
        <div class="absolute inset-0 bg-gradient-to-r from-[#121414] via-[#121414]/60 to-transparent"></div>
      </div>

      <div
        class="absolute -top-20 left-1/4 w-[600px] h-[500px] bg-[#e50914]/20 rounded-full blur-[150px] pointer-events-none z-0">
      </div>

      <div class="relative z-10 w-full max-w-[1280px] mx-auto px-6 md:px-[48px] py-12">
        <div v-if="currentHeroMovie" class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">

          <div class="lg:col-span-7 space-y-6 text-left">
            <div
              class="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#1e2020]/90 border border-[#5e3f3b]/60 shadow-[0_0_20px_rgba(229,9,20,0.3)] backdrop-blur-md">
              <span class="w-2.5 h-2.5 rounded-full bg-[#e50914] animate-ping"></span>
              <span class="text-[12px] font-bold tracking-widest uppercase text-[#ffb4aa] font-sans">
                PHIM ĐANG MỞ BÁN
              </span>
            </div>

            <Transition name="fade-text" mode="out-in">
              <div :key="activeHeroIndex" class="space-y-4">
                <h1
                  class="font-montserrat text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.15]">
                  {{ getMovieTitle(currentHeroMovie) }}
                </h1>

                <p class="font-sans text-sm sm:text-base text-[#c8c6c5] max-w-xl line-clamp-3 leading-relaxed">
                  {{ getMovieDesc(currentHeroMovie) }}
                </p>
              </div>
            </Transition>

            <div class="flex flex-wrap items-center gap-4 text-xs font-semibold text-[#ffb4aa]">
              <span class="px-2.5 py-1 rounded bg-[#e50914] text-white font-bold">
                Còn {{ currentHeroShowtimes.length }} suất
              </span>
              <span class="flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">schedule</span>
                Gần nhất {{ nearestHeroShowtimeLabel }}
              </span>
              <span class="flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">movie</span>
                {{ currentHeroMovie.duration }} phút
              </span>
            </div>

            <div class="flex flex-wrap items-center gap-4 pt-2">
              <button type="button" @click="bookHeroMovie"
                class="bg-[#e50914] hover:bg-[#c0000c] text-white font-bold text-sm px-8 py-3.5 rounded-xl flex items-center gap-2 transition-all duration-300 hover:scale-105 active:scale-95 shadow-[0_0_25px_rgba(229,9,20,0.5)] border border-[#ffb4aa]/30">
                <span class="material-symbols-outlined text-xl">confirmation_number</span>
                <span class="uppercase tracking-wider">Đặt Vé Ngay</span>
              </button>

              <button type="button" @click="openHeroTrailer"
                class="bg-[#1e2020]/80 backdrop-blur-md text-[#ffb4aa] border border-[#5e3f3b] font-semibold text-sm px-6 py-3.5 rounded-xl flex items-center gap-2 hover:bg-[#343535] hover:text-white transition-all duration-300">
                <span class="material-symbols-outlined text-xl">play_circle</span>
                <span>Xem Trailer</span>
              </button>
            </div>
          </div>

          <div class="lg:col-span-5 flex flex-col items-center justify-center">
            <div
              class="relative w-[260px] sm:w-[300px] h-[380px] sm:h-[430px] rounded-2xl overflow-hidden border-2 border-[#e50914] shadow-[0_0_35px_rgba(229,9,20,0.45)] group transition-all duration-500">
              <Transition name="fade-poster" mode="out-in">
                <img :key="activeHeroIndex" :src="getMovieImage(currentHeroMovie)"
                  :alt="getMovieTitle(currentHeroMovie)"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out" />
              </Transition>
              <div
                class="absolute inset-0 bg-gradient-to-t from-[#121414] via-transparent to-transparent opacity-80 pointer-events-none">
              </div>
              <div class="absolute bottom-4 left-4 right-4 text-center">
                <span
                  class="text-[11px] font-bold text-[#ffb4aa] tracking-widest uppercase bg-[#121414]/80 px-3 py-1 rounded-full border border-[#5e3f3b]">
                  Phim đang mở bán
                </span>
              </div>
            </div>

            <div class="flex items-center gap-2.5 mt-5">
              <button v-for="(m, idx) in heroMovies" :key="'thumb-' + (m.id || idx)" @click="setHeroMovie(idx)"
                class="w-10 h-14 rounded-lg overflow-hidden border-2 transition-all duration-300 relative focus:outline-none"
                :class="idx === activeHeroIndex ? 'border-[#e50914] scale-110 shadow-[0_0_12px_rgba(229,9,20,0.6)]' : 'border-[#343535] opacity-50 hover:opacity-100'">
                <img :src="getMovieImage(m)" :alt="getMovieTitle(m)" class="w-full h-full object-cover" />
              </button>
            </div>
          </div>

        </div>
        <div v-else class="flex min-h-[420px] items-center justify-center text-center">
          <div>
            <span class="material-symbols-outlined text-5xl text-[#737272]">movie_filter</span>
            <p class="mt-3 font-bold text-white">
              {{ showtimesLoaded ? 'Hiện chưa có phim nào đang mở bán' : 'Đang kiểm tra lịch chiếu...' }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- PHIM ĐANG CHIẾU -->
    <section id="now-showing"
      class="py-16 sm:py-24 relative z-10 border-b border-[#1a1c1c] bg-[#0d0e0f] overflow-hidden">
      <div class="max-w-[1280px] mx-auto px-6 md:px-[48px] reveal">

        <div class="text-center max-w-2xl mx-auto mb-10">
          <span class="text-[12px] font-semibold text-[#ffb4aa] uppercase tracking-widest block mb-1">Cập Nhật Liên
            Tục</span>
          <h2 class="font-montserrat text-2xl sm:text-3xl md:text-[32px] font-bold text-[#e3e2e2]">Phim Đang Chiếu Tại
            Rạp</h2>
        </div>

        <div v-if="nowShowingMovies.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <article v-for="movie in nowShowingMovies" :key="'mov-' + movie.id"
            class="group overflow-hidden rounded-2xl border border-[#343535] bg-[#181a1a] hover:border-[#e50914]/70 hover:-translate-y-1 transition-all duration-300">
            <NuxtLink :to="`/products/${movie.id}`" class="block relative aspect-[2/3] overflow-hidden bg-[#202222]">
              <img :src="getMovieImage(movie)" :alt="getMovieTitle(movie)"
                class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
              <div class="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-[#181a1a] to-transparent"></div>
              <span class="absolute top-3 left-3 rounded-md bg-[#e50914] px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-white">
                Đang bán vé
              </span>
            </NuxtLink>

            <div class="p-4">
              <h3 class="font-montserrat text-base font-bold text-white line-clamp-1">{{ movie.name }}</h3>
              <p class="mt-1 text-xs text-[#aaa8a7]">{{ movie.category }} · Giá từ {{ moviePrice(movie) }}đ</p>

              <div class="mt-4 min-h-[72px]">
                <p class="mb-2 text-[10px] font-bold uppercase tracking-widest text-[#ffb4aa]">Suất chiếu gần nhất</p>
                <div v-if="movieSchedule(movie.id).length" class="flex flex-wrap gap-2">
                  <button v-for="showtime in movieSchedule(movie.id)" :key="showtime.id" type="button"
                    @click="bookMovie(movie)"
                    class="rounded-lg border border-[#5e3f3b] bg-[#242626] px-2.5 py-1.5 text-[11px] font-semibold text-white hover:border-[#e50914] hover:bg-[#e50914] transition-colors">
                    {{ showtimeLabel(showtime) }}
                  </button>
                </div>
                <p v-else class="text-xs text-[#777]">Đang cập nhật giờ chiếu</p>
              </div>

              <button type="button" @click="bookMovie(movie)"
                class="mt-4 w-full rounded-xl bg-[#e50914] px-4 py-3 text-sm font-bold text-white hover:bg-[#c0000c] transition-colors">
                Chọn suất & đặt vé
              </button>
            </div>
          </article>
        </div>

        <div v-else class="rounded-2xl border border-dashed border-[#343535] bg-[#181a1a] px-6 py-14 text-center">
          <span class="material-symbols-outlined text-4xl text-[#777]">event_busy</span>
          <p class="mt-3 font-semibold text-white">Hiện chưa có suất chiếu đang mở bán</p>
          <p class="mt-1 text-sm text-[#aaa8a7]">Danh sách sẽ xuất hiện khi rạp mở suất chiếu mới.</p>
        </div>

      </div>
    </section>

    <!-- PHIM SẮP CHIẾU -->
    <section class="py-16 sm:py-24 relative z-10 border-b border-[#1a1c1c] bg-[#121414]">
      <div class="max-w-[1280px] mx-auto px-6 md:px-[48px] reveal">
        <div class="text-center max-w-2xl mx-auto mb-12">
          <span class="text-[12px] font-semibold text-[#ffb4aa] uppercase tracking-widest block mb-1">Sắp Ra Mắt</span>
          <h2 class="font-montserrat text-2xl sm:text-3xl md:text-[32px] font-bold text-[#e3e2e2]">Siêu Phẩm Điện Ảnh
            Sắp Chiếu</h2>
        </div>

        <div v-if="upcomingMovies.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
          <ProductCard v-for="product in upcomingMovies" :key="'coming-' + product.id" v-bind="product" />
        </div>
        <div v-else class="rounded-2xl border border-dashed border-[#343535] bg-[#181a1a] px-6 py-12 text-center">
          <p class="font-semibold text-white">Chưa có phim sắp chiếu được Super Admin công bố</p>
          <p class="mt-1 text-sm text-[#aaa8a7]">Phim sẽ xuất hiện ở đây ngay khi được đặt trạng thái “Sắp chiếu”.</p>
        </div>
      </div>
    </section>

    <!-- COMBO BẮP NƯỚC -->
    <section class="py-16 sm:py-24 relative z-10 border-b border-[#1a1c1c] bg-[#1a1c1c]/40">
      <div class="absolute inset-0 z-50 flex items-center justify-center bg-[#121414]/75 backdrop-blur-[2px]">
        <div class="rounded-2xl border border-white/10 bg-[#1a1c1c] px-8 py-6 text-center shadow-2xl">
          <span class="material-symbols-outlined text-4xl text-[#ffb4aa]">fastfood</span>
          <h3 class="mt-2 text-xl font-bold text-white">Combo bắp nước</h3>
          <p class="mt-1 text-sm text-[#c8c6c5]">Tạm thời chưa phát triển xong</p>
        </div>
      </div>
      <div class="max-w-[1280px] mx-auto px-6 md:px-[48px] reveal">
        <div class="text-center max-w-xl mx-auto mb-10">
          <span class="text-[12px] font-semibold text-[#ffb4aa] uppercase tracking-widest block mb-1">Thưởng Thức Tại
            Rạp</span>
          <h2 class="font-montserrat text-2xl sm:text-3xl md:text-[32px] font-bold text-[#e3e2e2]">Combo Bắp Nước Khuyến
            Mãi</h2>
        </div>

        <div class="relative flex items-center justify-center max-w-5xl mx-auto min-h-[380px]">
          <button @click="prevCombo" aria-label="Combo trước"
            class="absolute left-0 sm:-left-4 z-40 w-12 h-12 rounded-full bg-[#1e2020]/90 border border-[#e50914]/60 text-[#ffb4aa] flex items-center justify-center hover:bg-[#e50914] hover:text-white hover:scale-110 active:scale-95 transition-all duration-300 shadow-[0_0_15px_rgba(229,9,20,0.4)] backdrop-blur-md">
            <span class="material-symbols-outlined text-2xl">chevron_left</span>
          </button>

          <button @click="nextCombo" aria-label="Combo tiếp"
            class="absolute right-0 sm:-right-4 z-40 w-12 h-12 rounded-full bg-[#1e2020]/90 border border-[#e50914]/60 text-[#ffb4aa] flex items-center justify-center hover:bg-[#e50914] hover:text-white hover:scale-110 active:scale-95 transition-all duration-300 shadow-[0_0_15px_rgba(229,9,20,0.4)] backdrop-blur-md">
            <span class="material-symbols-outlined text-2xl">chevron_right</span>
          </button>

          <div class="flex items-center justify-center gap-6 w-full">
            <div v-for="combo in visibleCombos" :key="'cmb-' + combo.id"
              @click="combo.position === 'left' ? prevCombo() : combo.position === 'right' ? nextCombo() : null"
              class="smooth-card rounded-xl bg-[#1e2020] border overflow-hidden flex flex-col cursor-pointer" :class="[
                combo.position === 'center'
                  ? 'w-[320px] sm:w-[350px] scale-105 z-30 border-[#e50914] shadow-[0_0_25px_rgba(229,9,20,0.35)] opacity-100'
                  : 'w-[240px] sm:w-[260px] scale-90 z-10 border-[#343535] opacity-40 blur-[0.5px] hidden sm:flex'
              ]">
              <div class="relative h-44 w-full overflow-hidden">
                <img :src="combo.image" :alt="combo.name" class="w-full h-full object-cover" />
                <span
                  class="absolute top-3 left-3 bg-[#e50914] text-white px-2.5 py-1 text-[10px] font-semibold uppercase rounded">
                  {{ combo.tag }}
                </span>
              </div>
              <div class="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <h3 class="font-montserrat font-bold text-base text-[#e3e2e2] mb-1"
                    :class="{ 'text-[#ffb4aa]': combo.position === 'center' }">
                    {{ combo.name }}
                  </h3>
                  <p class="font-sans text-xs text-[#c8c6c5] leading-relaxed">{{ combo.desc }}</p>
                </div>
                <div class="flex items-center justify-between pt-4 mt-4 border-t border-[#343535]">
                  <div>
                    <span class="font-montserrat text-lg font-bold text-[#ffb4aa]">{{ combo.price }}</span>
                    <span class="text-xs text-[#737272] line-through ml-1.5">{{ combo.originalPrice }}</span>
                  </div>
                  <button
                    class="bg-[#e50914] hover:bg-[#c0000c] text-white px-4 py-2 text-xs font-semibold rounded-lg uppercase transition-all">
                    Thêm
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- ĐẶT VÉ NHANH -->
    <section id="quick-booking" class="py-16 sm:py-24 relative z-10 bg-[#121414]">
      <div class="max-w-[1280px] mx-auto px-6 md:px-[48px] reveal">

        <div class="text-center max-w-xl mx-auto mb-10">
          <span class="text-[12px] font-semibold text-[#ffb4aa] uppercase tracking-widest block mb-1">Trải Nghiệm Tiện
            Lợi</span>
          <h2 class="font-montserrat text-2xl sm:text-3xl md:text-[32px] font-bold text-[#e3e2e2]">Lịch Chiếu & Đặt Vé
            Trực Tuyến</h2>
        </div>

        <div class="p-6 sm:p-8 rounded-2xl bg-[#1a1c1c] border border-[#343535] shadow-2xl mb-12">
          <div
            class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 mb-6 border-b border-[#343535]">
            <div class="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
              <label for="quick-booking-cinema"
                class="text-xs font-bold uppercase text-[#ffb4aa] mr-2 flex items-center gap-1 whitespace-nowrap">
                <span class="material-symbols-outlined text-base">location_on</span> Rạp có suất mở bán:
              </label>
              <div class="relative min-w-0 sm:min-w-[240px]">
                <select id="quick-booking-cinema" v-model="selectedCinema"
                  class="w-full appearance-none rounded-xl border border-[#5e3f3b]/60 bg-[#1e2020] px-4 py-2.5 pr-10 text-sm font-semibold text-white outline-none transition focus:border-[#ffb4aa]">
                  <option v-for="cName in cinemas" :key="cName" :value="cName">
                    {{ cName }}
                  </option>
                </select>
                <span
                  class="material-symbols-outlined pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-base text-[#ffb4aa]">
                  expand_more
                </span>
              </div>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-bold uppercase text-[#ffb4aa] mr-2 flex items-center gap-1">
                <span class="material-symbols-outlined text-base">calendar_today</span> Ngày:
              </span>
              <button v-for="d in dates" :key="d.value" @click="selectedDate = d.value"
                class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all"
                :class="selectedDate === d.value ? 'bg-[#ffb4aa] text-[#121414] font-bold' : 'bg-[#1e2020] text-[#c8c6c5] border border-[#343535] hover:border-[#ffb4aa]/50'">
                {{ d.label }}
              </button>
            </div>
          </div>

          <div class="-mt-2 mb-6 rounded-xl border border-[#343535] bg-[#121414]/70 px-4 py-3 text-xs text-[#aaa8a7]">
            Chỉ hiển thị chi nhánh có suất chiếu tương lai, đã mở bán và vẫn còn thời gian đặt vé.
            <span v-if="cinemas.length === 1" class="ml-1 text-[#ffb4aa]">
              Hiện tại chỉ có {{ cinemas[0] }} đáp ứng điều kiện.
            </span>
          </div>

          <div v-if="quickBookingMovies.length" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="{ movie, schedules } in quickBookingMovies" :key="'book-' + movie.id"
              class="p-5 rounded-xl bg-[#121414] border border-[#343535] flex gap-4 hover:border-[#5e3f3b] transition-all">
              <img :src="getMovieImage(movie)" :alt="getMovieTitle(movie)"
                class="w-20 h-28 object-cover rounded-lg shadow-md" />
              <div class="flex-1 flex flex-col justify-between">
                <div>
                  <h4 class="font-montserrat font-bold text-[#e3e2e2] text-base mb-1 line-clamp-1">
                    {{ getMovieTitle(movie) }}
                  </h4>
                  <p class="font-sans text-xs text-[#c8c6c5] mb-3">
                    {{ movie.category }} • {{ movie.duration }} phút
                  </p>
                </div>

                <div class="flex flex-wrap gap-2">
                  <button v-for="schedule in schedules.slice(0, 6)" :key="schedule.id" type="button"
                    @click="chooseQuickShowtime(movie, schedule)"
                    class="px-3 py-1.5 rounded-lg bg-[#1e2020] hover:bg-[#e50914] border border-[#5e3f3b]/40 hover:border-[#ffb4aa] text-[#ffb4aa] hover:text-white text-xs font-semibold transition-all">
                    {{ schedule.time }} · {{ new Intl.NumberFormat('vi-VN').format(schedule.price) }}đ
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="rounded-xl border border-dashed border-[#343535] bg-[#121414] px-6 py-12 text-center">
            <p class="font-semibold text-white">Không có suất chiếu đang mở bán cho rạp và ngày này</p>
            <p class="mt-1 text-xs text-[#aaa8a7]">Hãy chọn rạp hoặc ngày khác.</p>
          </div>
        </div>

        <div class="mb-4 rounded-xl border border-amber-400/20 bg-amber-400/10 px-5 py-3 text-center text-sm font-bold text-amber-300">
          Thành viên CineAI Pass và đổi mã giảm giá tạm thời chưa phát triển xong.
        </div>
        <div class="pointer-events-none grid grid-cols-1 md:grid-cols-2 gap-6 opacity-50">
          <div class="p-6 sm:p-8 rounded-xl bg-[#1a1c1c] border border-[#5e3f3b]/40 flex justify-between items-center">
            <div>
              <span class="text-[12px] font-semibold text-[#ffb4aa] uppercase tracking-widest">Đặc Quyền VIP</span>
              <h3 class="font-montserrat text-xl font-bold text-[#e3e2e2] mt-1 mb-1">Thành Viên CineAI Pass</h3>
              <p class="font-sans text-xs text-[#c8c6c5] max-w-xs">Tích điểm đổi vé 0đ, nhận ưu đãi Combo bắp nước độc
                quyền.</p>
            </div>
            <button
              class="shrink-0 bg-[#e50914] hover:bg-[#c0000c] text-white px-5 py-2.5 rounded-xl font-semibold text-xs uppercase transition-all shadow-md">
              Đăng Ký
            </button>
          </div>

          <div class="p-6 sm:p-8 rounded-xl bg-[#1a1c1c] border border-[#5e3f3b]/40 flex justify-between items-center">
            <div>
              <span class="text-[12px] font-semibold text-[#ffb4aa] uppercase tracking-widest">Khuyến Mãi</span>
              <h3 class="font-montserrat text-xl font-bold text-[#e3e2e2] mt-1 mb-1">Đổi Mã Giảm Giá</h3>
              <p class="font-sans text-xs text-[#c8c6c5] max-w-xs">Nhập voucher từ đối tác để nhận vé ưu đãi tức thì.
              </p>
            </div>
            <button
              class="shrink-0 bg-[#1e2020] hover:bg-[#343535] text-[#ffb4aa] border border-[#5e3f3b] px-5 py-2.5 rounded-xl font-semibold text-xs uppercase transition-all">
              Nhập Mã
            </button>
          </div>
        </div>

      </div>
    </section>

  </div>
</template>

<style scoped>
.fade-text-enter-active,
.fade-text-leave-active,
.fade-poster-enter-active,
.fade-poster-leave-active {
  transition: all 0.6s ease-in-out;
}

.fade-text-enter-from {
  opacity: 0;
  transform: translateY(15px);
}

.fade-text-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}

.fade-poster-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.fade-poster-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

.reveal {
  opacity: 0;
  transform: translateY(35px);
  will-change: opacity, transform;
  transition: opacity 1.2s cubic-bezier(0.16, 1, 0.3, 1), transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.reveal-active {
  opacity: 1;
  transform: translateY(0);
}

.smooth-card {
  will-change: transform, opacity;
  transition: all 1s cubic-bezier(0.25, 1, 0.5, 1);
}
</style>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductsStore } from '~/store/products'

definePageMeta({
  layout: 'default'
})

const productsStore = useProductsStore()
const { products } = storeToRefs(productsStore)

// Gọi fetchProducts không cần await top-level để tránh block render SSR/Client
onMounted(() => {
  if (!products.value || products.value.length === 0) {
    productsStore.fetchProducts()
  }
})

// =========================================================================
// HERO SECTION LOGIC & AUTOPLAY
// =========================================================================
const activeHeroIndex = ref(0)
const AUTOPLAY_INTERVAL = 3000
let heroTimer: ReturnType<typeof setInterval> | null = null

const heroMovies = computed(() => {
  if (!products.value || !Array.isArray(products.value)) return []
  const clean = products.value.filter((movie) =>
    movie.status === 'NOW_SHOWING'
    && movie.name.trim().length >= 3
    && movie.imageUrl
    && !movie.imageUrl.includes('movie-placeholder'),
  )
  return clean.slice(0, 5)
})

const currentHeroMovie = computed(() => {
  if (!heroMovies.value.length) return null
  return heroMovies.value[activeHeroIndex.value] || heroMovies.value[0]
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

// =========================================================================
// 1. XOAY VÒNG VÔ TẬN: PHIM ĐANG CHIẾU
// =========================================================================
const movieIndex = ref(0)
const nowShowingMovies = computed(() =>
  products.value
    ? products.value.filter((movie) => movie.status === 'NOW_SHOWING' && movie.name.trim().length >= 3).slice(0, 5)
    : [],
)

function nextMovie() {
  if (!nowShowingMovies.value.length) return
  movieIndex.value = (movieIndex.value + 1) % nowShowingMovies.value.length
}

function prevMovie() {
  if (!nowShowingMovies.value.length) return
  movieIndex.value = (movieIndex.value - 1 + nowShowingMovies.value.length) % nowShowingMovies.value.length
}

const visibleMovies = computed(() => {
  const list = nowShowingMovies.value
  const len = list.length
  if (!len) return []

  const prevIdx = (movieIndex.value - 1 + len) % len
  const currIdx = movieIndex.value % len
  const nextIdx = (movieIndex.value + 1) % len

  return [
    { ...list[prevIdx], position: 'left' },
    { ...list[currIdx], position: 'center' },
    { ...list[nextIdx], position: 'right' }
  ]
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
const selectedCinema = ref('CineAI Thủ Đức')
const cinemas = ['CineAI Thủ Đức', 'CineAI Quận 1', 'CineAI Landmark 81']
const showtimes = ['10:15', '13:30', '16:45', '19:20', '21:50', '23:15']

// Tạo danh sách 3 ngày chiếu gần nhất tự động
const dates = computed(() => {
  const result = []
  const today = new Date()

  for (let i = 0; i < 3; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    const dayName = i === 0 ? 'Hôm Nay' : i === 1 ? 'Ngày Mai' : `Thứ ${d.getDay() + 1}`
    const dateStr = `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1).toString().padStart(2, '0')}`
    result.push(`${dayName} (${dateStr})`)
  }
  return result
})

const selectedDate = ref(dates.value[0])
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
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">

          <div class="lg:col-span-7 space-y-6 text-left reveal">
            <div
              class="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#1e2020]/90 border border-[#5e3f3b]/60 shadow-[0_0_20px_rgba(229,9,20,0.3)] backdrop-blur-md">
              <span class="w-2.5 h-2.5 rounded-full bg-[#e50914] animate-ping"></span>
              <span class="text-[12px] font-bold tracking-widest uppercase text-[#ffb4aa] font-sans">
                ĐANG CHIẾU TẠI RẠP
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

            <div class="flex items-center gap-4 text-xs font-semibold text-[#ffb4aa]">
              <span class="px-2.5 py-1 rounded bg-[#e50914] text-white font-bold">IMAX 3D</span>
              <span class="flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">schedule</span> 120 Phút
              </span>
              <span class="flex items-center gap-1">
                <span class="material-symbols-outlined text-sm text-yellow-500">star</span> 9.8 / 10
              </span>
            </div>

            <div class="flex flex-wrap items-center gap-4 pt-2">
              <a href="#quick-booking"
                class="bg-[#e50914] hover:bg-[#c0000c] text-white font-bold text-sm px-8 py-3.5 rounded-xl flex items-center gap-2 transition-all duration-300 hover:scale-105 active:scale-95 shadow-[0_0_25px_rgba(229,9,20,0.5)] border border-[#ffb4aa]/30">
                <span class="material-symbols-outlined text-xl">confirmation_number</span>
                <span class="uppercase tracking-wider">Đặt Vé Ngay</span>
              </a>

              <a href="#now-showing"
                class="bg-[#1e2020]/80 backdrop-blur-md text-[#ffb4aa] border border-[#5e3f3b] font-semibold text-sm px-6 py-3.5 rounded-xl flex items-center gap-2 hover:bg-[#343535] hover:text-white transition-all duration-300">
                <span class="material-symbols-outlined text-xl">play_circle</span>
                <span>Xem Trailer</span>
              </a>
            </div>
          </div>

          <div class="lg:col-span-5 flex flex-col items-center justify-center reveal">
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
                  Phim Nổi Bật Tuần
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

        <div class="relative flex items-center justify-center max-w-5xl mx-auto min-h-[440px]">
          <button @click="prevMovie" aria-label="Phim trước"
            class="absolute left-0 sm:-left-4 z-40 w-12 h-12 rounded-full bg-[#1e2020]/90 border border-[#e50914]/60 text-[#ffb4aa] flex items-center justify-center hover:bg-[#e50914] hover:text-white hover:scale-110 active:scale-95 transition-all duration-300 shadow-[0_0_15px_rgba(229,9,20,0.4)] backdrop-blur-md">
            <span class="material-symbols-outlined text-2xl">chevron_left</span>
          </button>

          <button @click="nextMovie" aria-label="Phim tiếp"
            class="absolute right-0 sm:-right-4 z-40 w-12 h-12 rounded-full bg-[#1e2020]/90 border border-[#e50914]/60 text-[#ffb4aa] flex items-center justify-center hover:bg-[#e50914] hover:text-white hover:scale-110 active:scale-95 transition-all duration-300 shadow-[0_0_15px_rgba(229,9,20,0.4)] backdrop-blur-md">
            <span class="material-symbols-outlined text-2xl">chevron_right</span>
          </button>

          <div class="flex items-center justify-center gap-4 sm:gap-8 w-full">
            <div v-for="item in visibleMovies" :key="'mov-' + item.id"
              @click="item.position === 'left' ? prevMovie() : item.position === 'right' ? nextMovie() : null"
              class="smooth-card cursor-pointer rounded-2xl overflow-hidden relative" :class="[
                item.position === 'center'
                  ? 'w-[280px] sm:w-[320px] scale-105 z-30 opacity-100 ring-2 ring-[#e50914] shadow-[0_0_30px_rgba(229,9,20,0.5)]'
                  : 'w-[220px] sm:w-[260px] scale-90 z-10 opacity-40 blur-[0.5px] hover:opacity-75 hidden sm:block'
              ]">
              <ProductCard v-bind="item" />
            </div>
          </div>
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

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
          <ProductCard v-for="product in products.slice(1, 5)" :key="'coming-' + product.id" v-bind="product" />
        </div>
      </div>
    </section>

    <!-- COMBO BẮP NƯỚC -->
    <section class="py-16 sm:py-24 relative z-10 border-b border-[#1a1c1c] bg-[#1a1c1c]/40">
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
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-bold uppercase text-[#ffb4aa] mr-2 flex items-center gap-1">
                <span class="material-symbols-outlined text-base">location_on</span> Rạp:
              </span>
              <button v-for="cName in cinemas" :key="cName" @click="selectedCinema = cName"
                class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all"
                :class="selectedCinema === cName ? 'bg-[#e50914] text-white shadow-md' : 'bg-[#1e2020] text-[#c8c6c5] border border-[#343535] hover:border-[#ffb4aa]/50'">
                {{ cName }}
              </button>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-bold uppercase text-[#ffb4aa] mr-2 flex items-center gap-1">
                <span class="material-symbols-outlined text-base">calendar_today</span> Ngày:
              </span>
              <button v-for="d in dates" :key="d" @click="selectedDate = d"
                class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all"
                :class="selectedDate === d ? 'bg-[#ffb4aa] text-[#121414] font-bold' : 'bg-[#1e2020] text-[#c8c6c5] border border-[#343535] hover:border-[#ffb4aa]/50'">
                {{ d }}
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="movie in nowShowingMovies.slice(0, 4)" :key="'book-' + movie.id"
              class="p-5 rounded-xl bg-[#121414] border border-[#343535] flex gap-4 hover:border-[#5e3f3b] transition-all">
              <img :src="getMovieImage(movie)" :alt="getMovieTitle(movie)"
                class="w-20 h-28 object-cover rounded-lg shadow-md" />
              <div class="flex-1 flex flex-col justify-between">
                <div>
                  <h4 class="font-montserrat font-bold text-[#e3e2e2] text-base mb-1 line-clamp-1">
                    {{ getMovieTitle(movie) }}
                  </h4>
                  <p class="font-sans text-xs text-[#c8c6c5] mb-3">2D Phụ Đề • 120 phút • T13</p>
                </div>

                <div class="flex flex-wrap gap-2">
                  <NuxtLink v-for="time in showtimes.slice(0, 4)" :key="time" to="/products"
                    class="px-3 py-1.5 rounded-lg bg-[#1e2020] hover:bg-[#e50914] border border-[#5e3f3b]/40 hover:border-[#ffb4aa] text-[#ffb4aa] hover:text-white text-xs font-semibold transition-all">
                    {{ time }}
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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

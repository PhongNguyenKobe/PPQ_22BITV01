<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductsStore } from '~/store/products'
import { useTicketsStore } from '~/store/tickets'
import { useUserStore } from '~/store/user'
import { getProductSlugUrl } from '~/utils/slug'
import {
  branchesService,
  comboService,
  movieService,
  promotionsService,
  youtubeEmbedUrl,
  youtubeTrailerLink,
  type BackendBranch,
  type CinemaCombo,
  type Promotion,
  type Showtime,
} from '~/services/api'

definePageMeta({ layout: 'default' })

const productsStore = useProductsStore()
const ticketsStore = useTicketsStore()
const userStore = useUserStore()
const router = useRouter()
const { products, loading: moviesLoading, error: moviesError } = storeToRefs(productsStore)

const branches = ref<BackendBranch[]>([])
const promotions = ref<Promotion[]>([])
const combos = ref<CinemaCombo[]>([])
const movieShowtimes = ref<Record<string, Showtime[]>>({})
const pageLoading = ref(true)
const pageError = ref('')
const combosLoading = ref(false)
const selectedBranchId = ref('')
const selectedDate = ref('')
const search = ref('')
const activeHeroIndex = ref(0)
const trailerMovie = ref<any>(null)
const copiedCode = ref('')
const followedMovieIds = ref<string[]>([])
let heroTimer: ReturnType<typeof setInterval> | undefined

const now = () => Date.now()
const branchByName = computed(() => new Map(branches.value.map(branch => [branch.name, branch])))
const selectedBranch = computed(() => branches.value.find(branch => branch.id === selectedBranchId.value) || null)

function isOpen(showtime: Showtime) {
  const starts = new Date(`${showtime.date}T${showtime.time}:00`).getTime()
  const closes = showtime.bookingClosesAt ? new Date(showtime.bookingClosesAt).getTime() : starts
  return starts > now() && closes > now()
}

function schedules(movieId: string | number) {
  return (movieShowtimes.value[String(movieId)] || [])
    .filter(isOpen)
    .filter(item => !selectedBranch.value || item.branchName === selectedBranch.value.name)
    .sort((a, b) => `${a.date}${a.time}`.localeCompare(`${b.date}${b.time}`))
}

const dates = computed(() => [...new Set(
  Object.values(movieShowtimes.value).flat()
    .filter(isOpen)
    .filter(item => !selectedBranch.value || item.branchName === selectedBranch.value.name)
    .map(item => item.date),
)].sort().slice(0, 7))

const normalizedSearch = computed(() => search.value.trim().toLocaleLowerCase('vi'))
const openMovies = computed(() => products.value
  .filter(movie => movie.status === 'NOW_SHOWING' && schedules(movie.id).length > 0)
  .filter(movie => !normalizedSearch.value || `${movie.name} ${movie.category} ${(movie.genres || []).join(' ')}`.toLocaleLowerCase('vi').includes(normalizedSearch.value)))

const heroMovies = computed(() => openMovies.value.slice(0, 5))
const currentHero = computed(() => heroMovies.value[activeHeroIndex.value] || heroMovies.value[0] || null)
const currentHeroSchedules = computed(() => currentHero.value ? schedules(currentHero.value.id).slice(0, 4) : [])
const upcomingMovies = computed(() => products.value
  .filter(movie => movie.status === 'UPCOMING')
  .filter(movie => !normalizedSearch.value || `${movie.name} ${movie.category}`.toLocaleLowerCase('vi').includes(normalizedSearch.value))
  .slice(0, 8))
const currentPromotions = computed(() => promotions.value.filter(item =>
  item.is_active && new Date(item.starts_at).getTime() <= now() && new Date(item.ends_at).getTime() >= now()
  && (item.usage_limit === null || item.used_count < item.usage_limit)
  && (!item.branch_ids.length || !selectedBranchId.value || item.branch_ids.includes(selectedBranchId.value)),
).slice(0, 3))
const quickMovies = computed(() => openMovies.value.map(movie => ({
  movie,
  items: schedules(movie.id).filter(item => !selectedDate.value || item.date === selectedDate.value).slice(0, 6),
})).filter(entry => entry.items.length).slice(0, 6))
const canContinue = computed(() => Boolean(ticketsStore.selectedMovie && (ticketsStore.selectedShowtime || ticketsStore.selectedCinema)))

function moviePayload(movie: any, price?: number) {
  return {
    id: movie.id, name: movie.name, backendMovieId: movie.backendMovieId || null,
    imageUrl: movie.imageUrl, category: movie.category, price: price ? price / 1000 : movie.price,
    rating: movie.rating || null, description: movie.description, trailerUrl: movie.trailerUrl || null,
  }
}

function chooseShowtime(movie: any, showtime: Showtime) {
  ticketsStore.selectMovie(moviePayload(movie, showtime.price))
  ticketsStore.selectCinema(showtime.branchName)
  ticketsStore.selectShowtime(showtime)
  const destination = '/checkout/seat'
  if (!userStore.isAuthenticated) return router.push({ path: '/login', query: { redirect: destination } })
  router.push(destination)
}

function startMovie(movie: any) {
  const nearest = schedules(movie.id)[0]
  if (nearest) return chooseShowtime(movie, nearest)
  ticketsStore.selectMovie(moviePayload(movie))
  router.push('/checkout/cinema')
}

function continueBooking() {
  if (!userStore.isAuthenticated) return router.push({ path: '/login', query: { redirect: '/checkout/seat' } })
  router.push(ticketsStore.selectedShowtime ? '/checkout/seat' : ticketsStore.selectedCinema ? '/checkout/showtime' : '/checkout/cinema')
}

function dateLabel(value: string) {
  const date = new Date(`${value}T00:00:00`)
  const today = new Date(); const tomorrow = new Date(today); tomorrow.setDate(today.getDate() + 1)
  const prefix = date.toDateString() === today.toDateString() ? 'Hôm nay' : date.toDateString() === tomorrow.toDateString() ? 'Ngày mai' : date.toLocaleDateString('vi-VN', { weekday: 'short' })
  return `${prefix} · ${date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })}`
}

function money(value: number) { return `${Number(value || 0).toLocaleString('vi-VN')}đ` }
function discount(item: Promotion) { return item.discount_type === 'PERCENT' ? `Giảm ${item.discount_value}%` : `Giảm ${money(item.discount_value)}` }
function openTrailer(movie: any) { trailerMovie.value = movie }
function focusHero(index: number) {
  activeHeroIndex.value = index
  if (process.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}
function isFollowed(movieId: string | number) { return followedMovieIds.value.includes(String(movieId)) }
function toggleFollow(movieId: string | number) {
  const id = String(movieId)
  followedMovieIds.value = isFollowed(id) ? followedMovieIds.value.filter(item => item !== id) : [...followedMovieIds.value, id]
  if (process.client) localStorage.setItem('cineai_followed_movies', JSON.stringify(followedMovieIds.value))
}
async function copyPromotion(code: string) {
  await navigator.clipboard.writeText(code)
  copiedCode.value = code
  window.setTimeout(() => { if (copiedCode.value === code) copiedCode.value = '' }, 1500)
}

async function loadShowtimes() {
  const target = products.value.filter(movie => movie.status === 'NOW_SHOWING' && movie.backendMovieId)
  const entries = await Promise.all(target.map(async movie => [String(movie.id), await movieService.getShowtimes(String(movie.backendMovieId)).catch(() => [])] as const))
  movieShowtimes.value = Object.fromEntries(entries)
}

async function loadHome(force = false) {
  pageLoading.value = true; pageError.value = ''
  try {
    await productsStore.fetchProducts(force)
    const [branchData, promotionData] = await Promise.all([branchesService.getAll(), promotionsService.getPublicPromotions()])
    branches.value = branchData
    promotions.value = promotionData
    await loadShowtimes()
    const saved = process.client ? localStorage.getItem('cineai_preferred_branch') : ''
    if (!selectedBranchId.value) selectedBranchId.value = branches.value.some(item => item.id === saved) ? saved! : branches.value[0]?.id || ''
  } catch (error: any) {
    pageError.value = error?.message || 'Không thể tải dữ liệu trang chủ.'
  } finally { pageLoading.value = false }
}

watch(selectedBranchId, async value => {
  if (process.client && value) localStorage.setItem('cineai_preferred_branch', value)
  selectedDate.value = dates.value[0] || ''
  combos.value = []
  if (!value) return
  combosLoading.value = true
  try { combos.value = await comboService.getPublic(value) } catch { combos.value = [] } finally { combosLoading.value = false }
})
watch(dates, values => { if (!values.includes(selectedDate.value)) selectedDate.value = values[0] || '' })
watch(heroMovies, values => { if (activeHeroIndex.value >= values.length) activeHeroIndex.value = 0 })

onMounted(() => {
  try { followedMovieIds.value = JSON.parse(localStorage.getItem('cineai_followed_movies') || '[]') } catch { followedMovieIds.value = [] }
  void loadHome()
  heroTimer = setInterval(() => { if (heroMovies.value.length > 1) activeHeroIndex.value = (activeHeroIndex.value + 1) % heroMovies.value.length }, 6000)
})
onUnmounted(() => { if (heroTimer) clearInterval(heroTimer) })
</script>

<template>
  <main class="min-h-screen bg-[#0d0f10] text-white">
    <section v-if="pageLoading" class="flex min-h-[72vh] items-center justify-center">
      <div class="text-center"><span class="material-symbols-outlined animate-spin text-5xl text-red-500">progress_activity</span><p class="mt-3 text-sm text-white/55">Đang đồng bộ phim và lịch chiếu...</p></div>
    </section>
    <section v-else-if="pageError || moviesError" class="mx-auto flex min-h-[70vh] max-w-xl items-center px-5 text-center">
      <div class="w-full rounded-3xl border border-red-500/25 bg-red-500/10 p-10"><span class="material-symbols-outlined text-5xl text-red-400">cloud_off</span><h1 class="mt-3 text-2xl font-black">Không tải được trang chủ</h1><p class="mt-2 text-sm text-white/60">{{ pageError || moviesError }}</p><button class="mt-6 rounded-xl bg-red-600 px-6 py-3 font-black" @click="loadHome(true)">Thử tải lại</button></div>
    </section>

    <template v-else>
      <section class="relative flex min-h-[640px] h-[82vh] max-h-[840px] select-none items-center overflow-hidden border-b border-white/5 bg-[#121414]">
        <template v-if="currentHero">
          <img :src="currentHero.imageUrl" :alt="currentHero.name" class="absolute inset-0 h-full w-full object-cover brightness-[.28] contrast-125 saturate-90 transition duration-700">
          <div class="absolute inset-0 bg-gradient-to-r from-[#0d0f10] via-[#1a1012]/85 to-[#0d0f10]/45"></div>
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(179,20,30,.22),transparent_60%)]"></div>
          <div class="pointer-events-none absolute -top-24 left-1/4 h-[520px] w-[640px] rounded-full bg-red-700/20 blur-[160px]"></div>
          <div class="pointer-events-none absolute -bottom-44 right-8 h-[400px] w-[400px] rounded-full bg-[#2b0508]/85 blur-[140px]"></div>

          <div class="relative mx-auto flex min-h-[640px] w-full max-w-[1280px] items-center px-6 py-16 lg:px-12">
            <div class="max-w-[680px]">
              <span class="inline-flex items-center rounded-full border border-red-300/20 bg-[#2a1f22] px-6 py-2 text-xs font-black uppercase tracking-[.18em] text-[#ffc2bf]">Đang chiếu tại rạp</span>
              <h1 class="mt-7 font-montserrat text-5xl font-black leading-[.95] tracking-tight text-white drop-shadow-[0_15px_40px_rgba(0,0,0,.6)] md:text-7xl">{{ currentHero.name }}</h1>
              <p class="mt-6 max-w-xl text-lg leading-8 text-white/72">{{ currentHero.description }}</p>

              <div class="mt-6 flex flex-wrap items-center gap-4 text-sm font-bold text-white/70">
                <span class="rounded-md bg-[#e50914] px-3 py-1.5 text-white">IMAX 3D</span>
                <span class="inline-flex items-center gap-1.5"><span class="material-symbols-outlined text-base">schedule</span>{{ currentHero.duration }} phút</span>
                <span v-if="currentHero.rating" class="inline-flex items-center gap-1.5 text-[#ffc15a]"><span class="material-symbols-outlined text-base">star</span>{{ currentHero.rating }} / 10</span>
              </div>

              <div class="mt-8 flex flex-wrap gap-4">
                <button class="flex items-center gap-2 rounded-2xl border border-[#ffb4aa]/35 bg-[#e50914] px-8 py-4 text-lg font-black shadow-[0_0_28px_rgba(229,9,20,.35)] transition hover:bg-[#c10610]" @click="startMovie(currentHero)">
                  <span class="material-symbols-outlined">confirmation_number</span>
                  Đặt vé ngay
                </button>
                <button class="flex items-center gap-2 rounded-2xl border border-white/20 bg-black/25 px-8 py-4 text-lg font-bold text-white/90 backdrop-blur-sm transition hover:bg-white/10" @click="openTrailer(currentHero)">
                  <span class="material-symbols-outlined">play_circle</span>
                  Xem Trailer
                </button>
              </div>
            </div>

            <div class="absolute right-12 top-1/2 hidden w-[320px] -translate-y-1/2 md:block xl:right-16">
              <div class="rounded-[1.4rem] border-2 border-[#f01623] bg-[#13090c] p-1 shadow-[0_0_32px_rgba(229,9,20,.35)]">
                <div class="relative w-full overflow-hidden rounded-[1.2rem]">
                  <img :src="currentHero.imageUrl" :alt="currentHero.name" class="aspect-[2/3] w-full object-cover">
                  <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent px-4 pb-5 pt-10">
                    <span class="inline-flex rounded-full border border-white/20 bg-black/45 px-3 py-1 text-[11px] font-black uppercase tracking-wide text-red-200">Phim đang chiếu</span>
                  </div>
                </div>
              </div>

              <div class="mt-5 flex items-center justify-center gap-2.5">
                <button v-for="(movie, index) in heroMovies" :key="movie.id" class="relative overflow-hidden rounded-xl border transition" :class="index === activeHeroIndex ? 'border-red-500 shadow-[0_0_16px_rgba(229,9,20,.45)]' : 'border-white/10 opacity-65 hover:border-white/40 hover:opacity-100'" :aria-label="`Hiển thị ${movie.name}`" @click="focusHero(index)">
                  <img :src="movie.imageUrl" :alt="movie.name" class="h-14 w-10 object-cover">
                </button>
              </div>
            </div>
          </div>
        </template>

        <div v-else class="flex min-h-[650px] items-center justify-center text-center">
          <div>
            <span class="material-symbols-outlined text-6xl text-white/20">event_busy</span>
            <h1 class="mt-3 text-2xl font-black">Chưa có suất chiếu đang mở bán</h1>
            <p class="mt-2 text-white/50">Hãy quay lại sau khi chi nhánh công bố lịch mới.</p>
          </div>
        </div>
      </section>

      <section class="relative z-20 px-5 py-5">
        <div class="mx-auto flex max-w-[1184px] flex-col gap-3 rounded-2xl border border-white/10 bg-[#181a1a]/95 p-3 shadow-[0_24px_65px_rgba(0,0,0,.5)] backdrop-blur-xl lg:flex-row">
          <label class="relative flex-1"><span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-white/35">search</span><input v-model="search" class="h-13 w-full rounded-xl border border-transparent bg-white/[.045] py-3.5 pl-12 pr-4 outline-none focus:border-red-500" placeholder="Tìm phim hoặc thể loại..."></label>
          <select v-model="selectedBranchId" class="min-w-[260px] rounded-xl border border-transparent bg-[#202326] px-4 py-3.5 font-bold outline-none focus:border-red-500"><option v-for="branch in branches" :key="branch.id" :value="branch.id">{{ branch.name }} · {{ branch.city }}</option></select>
          <button v-if="canContinue" class="rounded-xl bg-white/10 px-5 py-3.5 font-bold hover:bg-white/15" @click="continueBooking">Tiếp tục đặt vé →</button>
        </div>
      </section>

      <section class="mx-auto max-w-[1280px] px-6 py-20 md:px-12">
        <div class="flex items-end justify-between"><div><p class="eyebrow">Mở bán tại {{ selectedBranch?.name || 'hệ thống' }}</p><h2 class="section-title">Phim có suất để đặt ngay</h2></div><NuxtLink to="/products" class="more-link">Xem tất cả →</NuxtLink></div>
        <div v-if="openMovies.length" class="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4"><article v-for="movie in openMovies.slice(0, 8)" :key="movie.id" class="movie-card"><NuxtLink :to="getProductSlugUrl(movie)" class="relative block aspect-[2/3] overflow-hidden"><img :src="movie.imageUrl" :alt="movie.name" class="h-full w-full object-cover transition duration-500 hover:scale-105"><span class="absolute left-3 top-3 rounded-lg bg-red-600 px-2.5 py-1 text-[10px] font-black">ĐANG BÁN VÉ</span></NuxtLink><div class="p-4"><h3 class="line-clamp-1 text-lg font-black">{{ movie.name }}</h3><p class="mt-1 text-xs text-white/45">{{ movie.category }} · {{ movie.duration }} phút</p><div class="mt-4 flex flex-wrap gap-2"><button v-for="item in schedules(movie.id).slice(0, 4)" :key="item.id" class="rounded-lg border border-white/10 bg-white/5 px-2.5 py-2 text-xs hover:border-red-500 hover:bg-red-600" @click="chooseShowtime(movie, item)">{{ item.time }} · {{ item.date.slice(5).replace('-', '/') }}</button></div></div></article></div>
        <div v-else class="empty">Không tìm thấy phim đang mở bán phù hợp với rạp hoặc từ khóa.</div>
      </section>

      <section class="mx-auto max-w-7xl px-5 py-16 md:px-10"><div class="flex items-end justify-between"><div><p class="eyebrow">Sắp ra mắt</p><h2 class="section-title">Phim sắp chiếu</h2><p v-if="followedMovieIds.length" class="mt-2 text-xs text-pink-300">Đang theo dõi {{ followedMovieIds.length }} phim trên thiết bị này.</p></div><NuxtLink :to="{ path: '/products', query: { status: 'UPCOMING' } }" class="more-link">Xem toàn bộ →</NuxtLink></div><div v-if="upcomingMovies.length" class="mt-8 grid grid-cols-2 gap-5 md:grid-cols-4"><div v-for="movie in upcomingMovies" :key="movie.id" class="relative"><ProductCard v-bind="movie" /><button class="absolute right-3 top-3 z-20 flex h-10 w-10 items-center justify-center rounded-full border border-white/20 bg-black/70 backdrop-blur" :class="isFollowed(movie.id) ? 'text-pink-400' : 'text-white'" :title="isFollowed(movie.id) ? 'Bỏ theo dõi phim' : 'Theo dõi phim'" @click="toggleFollow(movie.id)"><span class="material-symbols-outlined" :style="isFollowed(movie.id) ? `font-variation-settings:'FILL' 1` : ''">favorite</span></button></div></div><div v-else class="empty">Không có phim sắp chiếu phù hợp.</div></section>

      <section v-if="currentPromotions.length" class="border-y border-white/5 bg-gradient-to-r from-red-950/20 to-amber-950/10 py-16"><div class="mx-auto max-w-7xl px-5 md:px-10"><div class="flex items-end justify-between"><div><p class="eyebrow">Ưu đãi đang dùng được</p><h2 class="section-title">Khuyến mãi CineAI</h2></div><NuxtLink to="/promotions" class="more-link">Xem điều kiện →</NuxtLink></div><div class="mt-8 grid gap-5 md:grid-cols-3"><article v-for="item in currentPromotions" :key="item.id" class="rounded-2xl border border-red-500/20 bg-[#191b1d] p-6"><span class="text-xs font-black uppercase tracking-wider text-red-300">CineAI Voucher</span><h3 class="mt-2 text-xl font-black">{{ item.name }}</h3><p class="mt-3 text-2xl font-black text-emerald-400">{{ discount(item) }}</p><p class="mt-2 text-xs text-white/45">Đơn tối thiểu {{ money(item.min_order_amount) }}</p><button class="mt-6 flex w-full items-center justify-between rounded-xl border border-dashed border-red-400/40 bg-red-500/5 px-4 py-3 font-mono font-black" @click="copyPromotion(item.code)"><span>{{ item.code }}</span><small class="font-sans text-red-300">{{ copiedCode === item.code ? 'Đã chép' : 'Sao chép' }}</small></button></article></div></div></section>

      <section class="mx-auto max-w-7xl px-5 py-16 md:px-10"><div class="flex items-end justify-between"><div><p class="eyebrow">Theo rạp đã chọn</p><h2 class="section-title">Combo bắp nước tại {{ selectedBranch?.name }}</h2></div><span class="text-xs text-white/40">Tồn kho và giá từ backend</span></div><div v-if="combosLoading" class="empty">Đang tải combo...</div><div v-else-if="combos.length" class="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4"><article v-for="combo in combos.slice(0, 4)" :key="combo.id" class="overflow-hidden rounded-2xl border border-white/10 bg-[#191b1d]"><img :src="combo.image_url || '/images/movie-placeholder.svg'" :alt="combo.name" class="h-44 w-full bg-white/5 object-cover" @error="($event.target as HTMLImageElement).src='/images/movie-placeholder.svg'"><div class="p-5"><h3 class="font-black">{{ combo.name }}</h3><p class="mt-2 line-clamp-2 min-h-10 text-xs text-white/45">{{ combo.description || 'Thông tin thành phần đang cập nhật.' }}</p><div class="mt-4 flex items-end justify-between"><b class="text-xl text-amber-300">{{ money(combo.price) }}</b><small :class="combo.stock_quantity === 0 ? 'text-red-400' : 'text-emerald-400'">{{ combo.stock_quantity == null ? 'Còn hàng' : combo.stock_quantity === 0 ? 'Hết hàng' : `Còn ${combo.stock_quantity}` }}</small></div></div></article></div><div v-else class="empty">Rạp này chưa mở bán combo. Bạn vẫn có thể tiếp tục đặt vé không kèm bắp nước.</div><p class="mt-5 text-center text-xs text-white/40">Combo được chọn sau khi chọn ghế để hệ thống kiểm tra tồn kho chính xác.</p></section>
    </template>

    <Teleport to="body"><div v-if="trailerMovie" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/85 p-4" @click.self="trailerMovie = null"><div class="w-full max-w-4xl overflow-hidden rounded-2xl border border-white/15 bg-[#111]"><div class="flex items-center justify-between p-4"><h3 class="font-black">Trailer · {{ trailerMovie.name }}</h3><button class="material-symbols-outlined" @click="trailerMovie = null">close</button></div><div v-if="youtubeEmbedUrl(trailerMovie.trailerUrl)" class="aspect-video"><iframe class="h-full w-full" :src="youtubeEmbedUrl(trailerMovie.trailerUrl)" :title="`Trailer ${trailerMovie.name}`" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div><div v-else class="p-14 text-center"><span class="material-symbols-outlined text-5xl text-white/25">video_library</span><p class="mt-3 text-white/55">Phim chưa có trailer chính thức trong dữ liệu.</p><a :href="youtubeTrailerLink(null, trailerMovie.name)" target="_blank" rel="noopener" class="mt-5 inline-flex rounded-xl bg-red-600 px-5 py-3 font-bold">Tìm trailer trên YouTube</a></div></div></div></Teleport>
  </main>
</template>

<style scoped>
.eyebrow{font-size:.72rem;font-weight:900;text-transform:uppercase;letter-spacing:.18em;color:#fca5a5}.section-title{margin-top:.35rem;font-size:clamp(1.7rem,4vw,2.45rem);font-weight:950}.more-link{font-size:.82rem;font-weight:900;color:#f87171}.movie-card{overflow:hidden;border:1px solid rgba(255,255,255,.09);border-radius:1.15rem;background:#191b1d;transition:.25s}.movie-card:hover{transform:translateY(-4px);border-color:rgba(239,68,68,.4)}.empty{margin-top:2rem;border:1px dashed rgba(255,255,255,.12);border-radius:1rem;padding:3rem 1.5rem;text-align:center;font-size:.9rem;color:rgba(255,255,255,.45)}
.rank-outline{-webkit-text-stroke:1.5px rgba(255,255,255,.38)}
</style>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useMoviesStore } from '~/store/movies'
import { useTicketsStore } from '~/store/tickets'

definePageMeta({ layout: 'default' })

const moviesStore = useMoviesStore()
const ticketsStore = useTicketsStore()

const { movies, loading, activeShowtimes } = storeToRefs(moviesStore)
const { activeMovie } = storeToRefs(moviesStore)

type Step = 'intent' | 'recommend' | 'ready'
const step = ref<Step>('intent')

// User intent (AI assistant input)
const intentText = ref('')
const isListening = ref(false)
const isSearched = ref(false)

const recommendedMovie = computed(() => pickBestMovie(movies.value))

const chosenShowtime = computed(() => {
  // We rely on checkout store for selectedShowtime, but since its ref isn't exposed here,
  // we compute from activeShowtimes after selecting.
  return ticketsStore.selectedShowtime || (activeShowtimes.value?.[0] ?? null)
})

onMounted(async () => {
  await moviesStore.fetchMovies()
})

function extractScore(m: { isFeatured?: boolean; rating?: number } | null) {
  if (!m) return 0
  const featuredScore = m.isFeatured ? 2 : 0
  const ratingScore = (m.rating ?? 0) / 5
  return featuredScore + ratingScore
}

function pickBestMovie(list: typeof movies.value) {
  if (!list?.length) return null
  const sorted = [...list].sort((a, b) => extractScore(b) - extractScore(a))
  return sorted[0] || null
}

function pickBestShowtime(showtimes: typeof activeShowtimes.value) {
  if (!showtimes?.length) return null

  const toMinutes = (t: string) => {
    const [hh, mm] = t.split(':').map(Number)
    return hh * 60 + (mm || 0)
  }

  // ưu tiên khung 18:00 - 21:00
  const preferredFrom = 18 * 60
  const preferredTo = 21 * 60

  const scored = showtimes.map(s => {
    const mins = toMinutes(s.time)
    let score = 0
    const inWindow = mins >= preferredFrom && mins <= preferredTo
    score += inWindow ? 5 : 0
    score -= Math.abs(mins - 19 * 60) / 60
    return { s, score }
  })

  scored.sort((a, b) => b.score - a.score)
  return scored[0]?.s || null
}

async function runAiBookingFlow() {
  const text = intentText.value.trim()
  if (!text) return

  isSearched.value = true
  step.value = 'recommend'

  // 1) AI semantic search -> candidate movies
  await moviesStore.searchMovies(text)

  // 2) pick best movie
  const best = pickBestMovie(movies.value)
  if (!best) {
    step.value = 'intent'
    return
  }

  // 3) load showtimes for that movie
  await moviesStore.fetchMovieDetails(best.id)

  const bestShow = pickBestShowtime(activeShowtimes.value)
  if (!bestShow) {
    step.value = 'intent'
    return
  }

  // 4) initialize checkout state
  ticketsStore.selectShowtime(bestShow)
  step.value = 'ready'

  if (process.client) {
    window.scrollTo({ top: 520, behavior: 'smooth' })
  }
}

function clearIntent() {
  intentText.value = ''
  isSearched.value = false
  step.value = 'intent'
}

function runAiBookingCTA() {
  intentText.value = 'Cho tôi đặt vé phim viễn tưởng kịch tính có robot tối nay, ưu tiên suất đẹp và giá hợp lý'
  runAiBookingFlow()
}

function proceedToSeatCheckout() {
  navigateTo('/checkout/seat')
}

// Web Speech Voice Search (AI intent)
let recognition: any = null
function startVoiceSearch() {
  if (!process.client) return

  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SpeechRecognition) {
    alert('Trình duyệt của bạn không hỗ trợ chức năng tìm kiếm bằng giọng nói.')
    return
  }

  if (isListening.value) {
    if (recognition) recognition.stop()
    isListening.value = false
    return
  }

  recognition = new SpeechRecognition()
  recognition.lang = 'vi-VN'
  recognition.continuous = false
  recognition.interimResults = false

  recognition.onstart = () => {
    isListening.value = true
    intentText.value = 'Đang lắng nghe giọng nói...'
  }

  recognition.onerror = (e: any) => {
    console.error('Speech error', e)
    isListening.value = false
    intentText.value = ''
  }

  recognition.onend = () => {
    isListening.value = false
  }

  recognition.onresult = async (event: any) => {
    const textResult = event.results[0][0].transcript
    intentText.value = textResult
    isListening.value = false
    await runAiBookingFlow()
  }

  recognition.start()
}
</script>

<template>
  <div class="min-h-screen bg-background text-on-surface pb-24">
    <!-- Hero Section: AI Ticket Booking -->
    <section class="relative h-[55vh] min-h-[420px] flex flex-col items-center justify-center text-center px-6 md:px-0">
      <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full pointer-events-none z-0 animate-pulse" style="background:rgba(229,9,20,0.06);filter:blur(120px)"></div>
      <div class="absolute top-1/2 -right-48 w-96 h-96 rounded-full pointer-events-none z-0" style="background:rgba(138,43,226,0.06);filter:blur(120px)"></div>

      <h1 class="font-headline-xl text-headline-xl md:text-[56px] md:leading-[64px] font-bold max-w-4xl mb-8 relative z-10">
        AI đề xuất lộ trình <span class="text-primary-container">đặt vé</span> nhanh
      </h1>

      <div class="w-full max-w-3xl glass-panel p-2 rounded-full flex items-center gap-3 border-white/20 shadow-xl focus-within:ring-2 focus-within:ring-primary-container transition-all relative z-10">
        <span class="material-symbols-outlined ml-6 text-on-surface-variant">auto_awesome</span>

        <input
          v-model="intentText"
          @keydown.enter="runAiBookingFlow"
          class="bg-transparent border-none focus:ring-0 flex-grow font-body-md text-on-surface placeholder:text-on-surface-variant/50 outline-none"
          :placeholder="isListening ? 'Hãy nói ý muốn đặt vé của bạn...' : 'Thử nói: Đặt vé tối nay, ưu tiên suất đẹp cho 2 người...'"
          type="text"
        />

        <button
          v-if="intentText"
          @click="clearIntent"
          type="button"
          class="p-2 text-on-surface-variant hover:text-on-surface mr-1"
          title="Xóa"
        >
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>

        <button
          @click="startVoiceSearch"
          :class="isListening ? 'bg-primary-container text-white animate-bounce' : 'bg-primary-container/10 text-primary-container hover:bg-primary-container/20'"
          class="p-4 rounded-full transition-colors flex items-center justify-center group"
          title="Đặt vé bằng giọng nói"
        >
          <span class="material-symbols-outlined text-[24px]">mic</span>
        </button>

        <button
          @click="runAiBookingFlow"
          class="bg-primary-container text-on-primary-container px-8 py-4 rounded-full font-label-md text-label-md font-bold red-glow-hover transition-all shrink-0"
        >
          AI Đặt Vé Nhanh
        </button>
      </div>

      <p class="mt-6 text-on-surface-variant font-label-md text-label-md relative z-10">
        Ví dụ: <span class="text-on-surface">"Ngồi VIP hàng F", "Suất tối muộn hôm nay"</span>
      </p>
    </section>

    <!-- AI Booking Flow Cards -->
    <section class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-10">
      <div class="flex items-center justify-between gap-6 mb-8">
        <div>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-secondary" style="font-variation-settings: 'FILL' 1">smart_toy</span>
            <h2 class="font-headline-lg text-headline-lg">Trợ lý AI đang tối ưu đặt vé</h2>
          </div>
          <p class="text-on-surface-variant mt-2">Rút ngắn thời gian: AI tự chọn phim + suất tối ưu để bạn chỉ việc chọn ghế.</p>
        </div>

        <button
          @click="runAiBookingCTA"
          class="bg-primary-container text-white px-6 py-3 rounded-2xl font-bold flex items-center gap-2 red-glow-hover transition-all shrink-0"
          title="Điền câu mẫu"
        >
          <span class="material-symbols-outlined">auto_awesome</span>
          Tự động gợi ý
        </button>
      </div>

      <div v-if="loading" class="glass-panel rounded-2xl p-8 text-center border border-white/10">
        <div class="flex items-center justify-center gap-3">
          <span class="material-symbols-outlined text-2xl animate-spin" style="animation-duration: 1200ms">progress_activity</span>
          <p class="font-bold">AI đang đề xuất phim và suất chiếu tối ưu...</p>
        </div>
        <p class="text-on-surface-variant text-sm mt-3">Đang phân tích yêu cầu của bạn (không phải tìm kím phim).</p>
      </div>

      <div v-else-if="isSearched" class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <!-- Recommended Movie -->
        <div class="lg:col-span-6 glass-panel rounded-2xl border border-glass-stroke p-6 overflow-hidden relative">
          <div class="absolute inset-0 bg-cover bg-center opacity-20" :style="recommendedMovie ? { backgroundImage: `url(${recommendedMovie.poster})` } : {}"></div>
          <div class="relative">
            <div class="flex items-center justify-between">
              <span class="bg-primary-container/10 border border-primary-container/20 text-primary-container text-xs font-bold px-3 py-1 rounded-full">Phim AI chọn</span>
              <span class="text-[11px] text-on-surface-variant font-bold">Bước 1/2</span>
            </div>

            <h3 class="font-headline-md text-2xl font-black text-on-surface mt-3" v-if="recommendedMovie">{{ recommendedMovie.title }}</h3>
            <p class="text-on-surface-variant text-sm mt-2" v-if="recommendedMovie">{{ recommendedMovie.description }}</p>

            <div class="mt-4 flex flex-wrap gap-2" v-if="recommendedMovie">
              <span v-for="g in recommendedMovie.genre" :key="g" class="px-3 py-1 rounded-full bg-surface-container-high border border-white/5 text-xs font-bold">{{ g }}</span>
            </div>

            <div class="mt-6">
              <NuxtLink v-if="recommendedMovie" :to="`/movies/${recommendedMovie.id}`" class="text-primary-container hover:underline text-sm font-bold">
                Xem chi tiết phim
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Recommended Showtime -->
        <div class="lg:col-span-6 glass-panel rounded-2xl border border-glass-stroke p-6">
          <div class="flex items-center justify-between">
            <span class="bg-secondary-container/10 border border-secondary-container/20 text-secondary text-xs font-bold px-3 py-1 rounded-full">Suất chiếu tối ưu</span>
            <span class="text-[11px] text-on-surface-variant font-bold">Bước 2/2</span>
          </div>

          <div v-if="ticketsStore.selectedShowtime" class="mt-4">
            <h3 class="font-headline-md text-2xl font-black text-on-surface">{{ ticketsStore.selectedShowtime.time }} • {{ ticketsStore.selectedShowtime.date }}</h3>
            <div class="mt-3 space-y-2 text-sm text-on-surface-variant">
              <div class="flex justify-between gap-4"><span>Rạp</span><span class="text-on-surface font-bold">{{ ticketsStore.selectedShowtime.branchName }}</span></div>
              <div class="flex justify-between gap-4"><span>Phòng</span><span class="text-on-surface font-bold">{{ ticketsStore.selectedShowtime.screenName }}</span></div>
              <div class="flex justify-between gap-4"><span>Giá từ</span><span class="text-on-surface font-bold text-primary">{{ ticketsStore.selectedShowtime.price.toLocaleString() }} VNĐ</span></div>
            </div>

            <div class="mt-6 flex flex-col sm:flex-row gap-3">
              <button
                @click="proceedToSeatCheckout"
                class="bg-primary-container text-on-primary-container px-6 py-3 rounded-xl font-bold flex items-center justify-center gap-2 red-glow-hover transition-all"
              >
                <span class="material-symbols-outlined">confirmation_number</span>
                Chọn ghế & đặt vé ngay
              </button>

              <button
                @click="step = 'intent'; isSearched = false; ticketsStore.clearSelection()"
                class="border border-white/10 bg-surface-container-high px-6 py-3 rounded-xl font-bold hover:bg-white/5 transition-all"
              >
                Sửa yêu cầu
              </button>
            </div>
          </div>

          <div v-else class="mt-4 text-center text-on-surface-variant">
            AI không tìm được suất chiếu phù hợp. Hãy thử mô tả khác (ví dụ: "sớm hơn", "tối nay").
          </div>
        </div>
      </div>

      <div v-else class="mt-10 glass-panel border border-white/10 rounded-2xl p-8">
        <div class="flex items-start gap-4">
         
          <div>
            <h3 class="font-headline-md text-xl font-black text-on-surface">Bắt đầu từ mong muốn đặt vé</h3>
            <p class="text-on-surface-variant text-sm mt-2">Bạn chỉ cần nói/nhập: thời gian, phong cách, rạp/loại ghế (nếu có). AI sẽ tự đề xuất phim + suất tối ưu để bạn chọn ghế.</p>

            <div class="mt-4 flex flex-wrap gap-2">
              <button @click="runAiBookingCTA" class="px-4 py-2 rounded-full bg-primary-container/10 border border-primary-container/20 text-primary-container text-xs font-bold hover:bg-primary-container/15 transition-all">
                Tôi muốn đặt vé tối nay (ưu tiên suất đẹp)
              </button>
              <button
                @click="intentText = 'Đặt vé hôm nay, 2 người, chỗ ngồi VIP'; runAiBookingFlow()"
                class="px-4 py-2 rounded-full bg-primary-container/10 border border-primary-container/20 text-primary-container text-xs font-bold hover:bg-primary-container/15 transition-all"
              >
                Đặt vé 2 người VIP
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Bottom CTA -->
    <section class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-12">
      <div class="glass-panel p-12 rounded-[32px] flex flex-col md:flex-row items-center justify-between gap-12 overflow-hidden relative border border-white/10">
        <div class="absolute top-0 right-0 w-96 h-96 pointer-events-none" style="background:rgba(229,9,20,0.05);filter:blur(80px)"></div>

        <div class="max-w-xl text-center md:text-left relative z-10">
          <h3 class="font-headline-lg text-headline-lg mb-4">Bạn muốn đặt vé nhanh trong 30 giây?</h3>
          <p class="text-on-surface-variant font-body-md text-body-md">AI sẽ tối ưu lộ trình: chọn phim + suất phù hợp, sau đó đưa bạn thẳng tới bước chọn ghế.</p>
        </div>

        <button
          @click="runAiBookingCTA"
          class="bg-primary-container text-white px-10 py-5 rounded-2xl font-headline-md text-[18px] font-bold flex items-center gap-4 red-glow-hover transition-all shrink-0 relative z-10"
        >
          <span class="material-symbols-outlined text-2xl animate-pulse">auto_awesome</span>
          Khởi động AI Booking
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.glass-panel {
  background: rgba(31, 31, 31, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.red-glow-hover:hover {
  box-shadow: 0 0 25px -5px rgba(229, 9, 20, 0.5);
}
</style>


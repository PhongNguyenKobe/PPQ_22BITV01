<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketsStore } from '~/store/tickets'
import { aiDiscoveryService } from '~/services/api'
import { isShowtimeExpired } from '~/utils/showtime'

definePageMeta({ layout: 'default' })

const router = useRouter()
const ticketsStore = useTicketsStore()

interface ChatMessage {
  id: string
  role: 'user' | 'model'
  text: string
  movies?: any[]
  branches?: any[]
  showtimes?: any[]
}

const messages = ref<ChatMessage[]>([
  {
    id: 'welcome',
    role: 'model',
    text: 'Xin chào! Tôi là **CineAI Assistant** 🤖, trợ lý đặt vé thông minh của bạn tại CineAI.\n\nTôi có thể giúp bạn tìm kiếm phim, rạp chiếu, suất chiếu phù hợp dựa trên ngôn ngữ nói tự nhiên. Hãy gõ yêu cầu của bạn bên dưới, ví dụ:\n\n* *"Tôi muốn xem phim Trí Tuệ Nhân Tạo ở quận 1 khoảng 1-4h chiều"* \n* *"Tối nay lúc 8h có phim nào hay ở Hùng Vương không?"* \n* *"Tìm suất chiếu của phim Thành Phố Vô Hình"*'
  }
])

const inputMessage = ref('')
const isLoading = ref(false)
const chatContainerRef = ref<HTMLElement | null>(null)

// Quick prompt suggestions
const quickPrompts = [
  'Xem phim Trí Tuệ Nhân Tạo ở Quận 1 từ 1h đến 4h chiều',
  'Tối nay có phim gì ở rạp Sala Quận 2?',
  'Suất chiếu phim Thành Phố Vô Hình sau 18h tối',
  'Phim viễn tưởng đang chiếu ở rạp Hùng Vương'
]

const selectQuickPrompt = (prompt: string) => {
  inputMessage.value = prompt
  sendMessage()
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainerRef.value) {
    chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
  }
}

const sendMessage = async () => {
  const text = inputMessage.value.trim()
  if (!text || isLoading.value) return

  // 1. Push user message
  messages.value.push({
    id: `user-${Date.now()}`,
    role: 'user',
    text
  })
  inputMessage.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    // 2. Build history payload
    const history = messages.value
      .slice(0, messages.value.length - 1) // Exclude current user prompt
      .filter(msg => msg.id !== 'welcome')
      .map(msg => ({
        role: msg.role,
        parts: [{ text: msg.text }]
      }))

    // 3. Query backend AI Discovery service
    const response = await aiDiscoveryService.query(text, history)

    // 4. Push AI response
    messages.value.push({
      id: `ai-${Date.now()}`,
      role: 'model',
      text: response.reply,
      movies: response.movies,
      branches: response.branches,
      showtimes: response.showtimes
    })
  } catch (e: any) {
    console.error('AI assistant error:', e)
    messages.value.push({
      id: `error-${Date.now()}`,
      role: 'model',
      text: 'Thành thật xin lỗi bạn, hệ thống AI đang gặp sự cố kết nối. Vui lòng gửi lại yêu cầu hoặc thử lại sau.'
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

// Helpers for displaying details in the view
const getMovieForShowtime = (showtime: any, msg: ChatMessage) => {
  if (!msg.movies) return null
  return msg.movies.find(m => m.id === showtime.movieId)
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('vi-VN').format(price) + 'đ'
}

const formatDate = (dateStr: string) => {
  const [year, month, day] = dateStr.split('-')
  return `${day}/${month}/${year}`
}

const handleQuickBook = (showtime: any, movie: any) => {
  if (isShowtimeExpired(showtime)) return

  // Format movie object shape as expected by the tickets store / checkout pages
  const moviePayload = {
    id: showtime.movieId,
    name: movie?.title || 'Phim đã chọn',
    backendMovieId: showtime.movieId,
    imageUrl: movie?.poster || '/images/movie-placeholder.svg',
    category: movie?.genre?.join(', ') || '2D',
    price: showtime.price / 1000,
    rating: 4.8,
    description: movie?.description || '',
    trailerUrl: movie?.trailer || null
  }

  // Set checkout state in Pinia tickets store
  ticketsStore.selectMovie(moviePayload)
  ticketsStore.selectCinema(showtime.branchName)
  ticketsStore.selectShowtime(showtime)

  // Notify custom toast
  if (import.meta.client) {
    window.dispatchEvent(new CustomEvent('cineai:toast', {
      detail: {
        message: 'Đã chọn suất chiếu! Đang chuyển hướng đến trang chọn ghế...',
        type: 'success'
      }
    }))
  }

  // Redirect user to the seat selection page
  router.push('/checkout/seat')
}

// Support basic markdown rendering for *bold*, _italic_, and line breaks
const renderMarkdown = (text: string) => {
  if (!text) return ''
  let html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br />')
  return html
}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <section class="ai-discovery-container py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto flex flex-col h-[82vh] rounded-3xl border border-white/10 bg-[#121414]/90 p-5 shadow-3xl backdrop-blur-2xl relative overflow-hidden">
      <!-- Glow background highlights -->
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-primary-container/10 rounded-full blur-[100px] pointer-events-none"></div>

      <!-- Header -->
      <header class="flex items-center gap-4 pb-4 mb-4 border-b border-white/5 relative z-10">
        <div class="relative">
          <span class="material-symbols-outlined rounded-2xl bg-gradient-to-tr from-primary-container to-purple-600 p-3 text-white shadow-lg animate-pulse">smart_toy</span>
          <span class="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 border-2 border-[#121414] rounded-full"></span>
        </div>
        <div>
          <h1 class="text-xl font-black text-white tracking-wide">CineAI Assistant</h1>
          <p class="text-xs text-on-surface-variant flex items-center gap-1.5 mt-0.5">
            <span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-ping"></span>
            Trực tuyến • Sẵn sàng hỗ trợ đặt vé
          </p>
        </div>
      </header>

      <!-- Chat Area -->
      <main ref="chatContainerRef" class="flex-1 overflow-y-auto px-2 space-y-6 scrollbar-custom relative z-10 pb-4">
        <div v-for="msg in messages" :key="msg.id" class="flex flex-col" :class="msg.role === 'user' ? 'items-end' : 'items-start'">
          <div class="flex items-start gap-3 max-w-[85%]" :class="msg.role === 'user' ? 'flex-row-reverse' : ''">
            <!-- Icon -->
            <div class="flex-shrink-0">
              <span class="material-symbols-outlined text-sm p-2 rounded-xl text-white shadow"
                    :class="msg.role === 'user' ? 'bg-primary-container/80' : 'bg-purple-600/80'">
                {{ msg.role === 'user' ? 'person' : 'smart_toy' }}
              </span>
            </div>
            <!-- Message Bubble -->
            <div>
              <div class="rounded-2xl p-4 text-sm sm:text-base leading-relaxed text-white shadow-md border"
                   :class="msg.role === 'user'
                     ? 'bg-gradient-to-br from-primary-container/20 to-primary-container/5 border-primary-container/20 rounded-tr-none'
                     : 'bg-white/5 border-white/10 rounded-tl-none'">
                <p v-html="renderMarkdown(msg.text)"></p>
              </div>

              <!-- Recommendations (Showtimes, Movies) attached to model messages -->
              <div v-if="msg.role === 'model' && (msg.showtimes?.length || msg.movies?.length)" class="mt-4 space-y-4">
                
                <!-- Match showtimes -->
                <div v-if="msg.showtimes?.length" class="space-y-3">
                  <h3 class="text-xs font-bold text-amber-300 uppercase tracking-widest flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base">confirmation_number</span>
                    Suất chiếu phù hợp cho bạn:
                  </h3>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div v-for="st in msg.showtimes" :key="st.id"
                         class="flex flex-col rounded-2xl border border-white/10 bg-white/5 p-4 shadow-sm transition hover:border-primary-container hover:bg-white/10 relative overflow-hidden group">
                      
                      <!-- Expired badge -->
                      <div v-if="isShowtimeExpired(st)" class="absolute inset-0 bg-[#121414]/80 backdrop-blur-[1px] flex items-center justify-center z-20">
                        <span class="px-3 py-1.5 rounded-full border border-red-500/20 bg-red-500/10 text-red-400 font-bold text-xs">
                          Đã hết giờ bán vé
                        </span>
                      </div>

                      <div class="flex gap-3">
                        <!-- Movie Poster -->
                        <div class="w-16 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-white/5">
                          <img :src="getMovieForShowtime(st, msg)?.poster || '/images/movie-placeholder.svg'"
                               :alt="getMovieForShowtime(st, msg)?.title"
                               class="w-full h-full object-cover transition duration-300 group-hover:scale-105" />
                        </div>
                        <!-- Details -->
                        <div class="flex-1 flex flex-col justify-between min-w-0">
                          <div>
                            <h4 class="font-bold text-white text-sm sm:text-base truncate">{{ getMovieForShowtime(st, msg)?.title || 'Phim đã chọn' }}</h4>
                            <p class="text-xs text-on-surface-variant flex items-center gap-1 mt-1 font-medium truncate">
                              <span class="material-symbols-outlined text-xs text-primary-container">theater_comedy</span>
                              {{ st.branchName }}
                            </p>
                            <p class="text-xs text-on-surface-variant flex items-center gap-1 mt-1 font-medium">
                              <span class="material-symbols-outlined text-xs text-purple-400">meeting_room</span>
                              {{ st.screenName }}
                            </p>
                          </div>
                          <!-- Time and price -->
                          <div class="flex items-baseline justify-between mt-2 border-t border-white/5 pt-1.5">
                            <span class="text-xs text-primary-container font-black">{{ st.time }} • {{ formatDate(st.date) }}</span>
                            <span class="text-sm font-bold text-amber-300">{{ formatPrice(st.price) }}</span>
                          </div>
                        </div>
                      </div>

                      <!-- Booking CTA -->
                      <button @click="handleQuickBook(st, getMovieForShowtime(st, msg))"
                              :disabled="isShowtimeExpired(st)"
                              class="mt-3 w-full bg-gradient-to-r from-primary-container to-purple-600 hover:from-primary-container hover:to-purple-500 text-white py-2 rounded-xl text-sm font-bold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-1.5">
                        <span class="material-symbols-outlined text-sm">confirmation_number</span>
                        Đặt vé ngay
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Match movies (if no direct showtimes available) -->
                <div v-else-if="msg.movies?.length" class="space-y-3">
                  <h3 class="text-xs font-bold text-purple-400 uppercase tracking-widest flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base">movie</span>
                    Phim được đề xuất:
                  </h3>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div v-for="m in msg.movies" :key="m.id"
                         class="flex gap-3 rounded-2xl border border-white/10 bg-white/5 p-3.5 shadow-sm transition hover:border-purple-500 hover:bg-white/10">
                      <!-- Movie Poster -->
                      <div class="w-14 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-white/5">
                        <img :src="m.poster || '/images/movie-placeholder.svg'" :alt="m.title" class="w-full h-full object-cover" />
                      </div>
                      <!-- Details -->
                      <div class="flex-1 flex flex-col justify-between min-w-0">
                        <div>
                          <h4 class="font-bold text-white text-sm truncate">{{ m.title }}</h4>
                          <p class="text-xs text-on-surface-variant truncate mt-1">{{ m.genre?.join(', ') }}</p>
                          <p class="text-xs text-purple-300 mt-1 font-medium">{{ m.duration }} phút • {{ m.status === 'NOW_SHOWING' ? 'Đang chiếu' : 'Sắp chiếu' }}</p>
                        </div>
                        <button @click="selectQuickPrompt(`Tìm lịch chiếu phim ${m.title}`)"
                                class="mt-2 text-xs font-bold text-primary-container hover:underline flex items-center gap-0.5 justify-end">
                          Xem suất chiếu
                          <span class="material-symbols-outlined text-xs">arrow_forward</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        <!-- Chat processing/typing indicator -->
        <div v-if="isLoading" class="flex items-start gap-3">
          <div class="flex-shrink-0">
            <span class="material-symbols-outlined text-sm p-2 rounded-xl text-white bg-purple-600/80 shadow">smart_toy</span>
          </div>
          <div class="rounded-2xl p-4 bg-white/5 border border-white/10 rounded-tl-none shadow-md flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full bg-purple-400 animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-purple-400 animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-purple-400 animate-bounce" style="animation-delay: 300ms"></span>
          </div>
        </div>
      </main>

      <!-- Bottom controls (quick prompts + input) -->
      <footer class="mt-4 pt-4 border-t border-white/5 relative z-10">
        <!-- Quick Prompts list -->
        <div v-if="!isLoading" class="flex items-center gap-2 overflow-x-auto pb-3.5 scrollbar-none-horizontal">
          <button v-for="prompt in quickPrompts" :key="prompt"
                  @click="selectQuickPrompt(prompt)"
                  class="flex-shrink-0 bg-white/5 border border-white/10 hover:border-purple-500 hover:bg-white/10 rounded-full px-4.5 py-1.5 text-xs font-bold text-purple-300 hover:text-white transition">
            {{ prompt }}
          </button>
        </div>

        <!-- Input field -->
        <div class="flex items-center gap-2 relative mt-1">
          <input v-model="inputMessage"
                 @keydown.enter="sendMessage"
                 :disabled="isLoading"
                 type="text"
                 placeholder="Hỏi về lịch chiếu, rạp chiếu hoặc phim (ví dụ: Xem phim..."
                 class="flex-1 rounded-2xl border border-white/10 bg-white/5 px-5 py-3.5 text-sm sm:text-base text-white placeholder-on-surface-variant focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed" />
          
          <button @click="sendMessage"
                  :disabled="isLoading || !inputMessage.trim()"
                  class="flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-r from-primary-container to-purple-600 hover:from-primary-container hover:to-purple-500 text-white font-bold transition disabled:opacity-40 disabled:cursor-not-allowed shadow-md hover:scale-105 active:scale-95">
            <span class="material-symbols-outlined">send</span>
          </button>
        </div>
      </footer>
    </div>
  </section>
</template>

<style scoped>
.ai-discovery-container {
  min-height: calc(100vh - 72px);
  background-color: #0b0c0c;
  display: flex;
  align-items: center;
}

/* Custom scrollbars */
.scrollbar-custom::-webkit-scrollbar {
  width: 6px;
}
.scrollbar-custom::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-custom::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
}
.scrollbar-custom::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.scrollbar-none-horizontal::-webkit-scrollbar {
  display: none;
}
.scrollbar-none-horizontal {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
</style>

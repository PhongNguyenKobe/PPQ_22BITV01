<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketsStore } from '~/store/tickets'
import { aiDiscoveryService } from '~/services/api'
import { isShowtimeExpired } from '~/utils/showtime'
import { getMovieSlugUrl } from '~/utils/slug'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const router = useRouter()
const ticketsStore = useTicketsStore()

// ==========================================
// LOGIC CHẾ ĐỘ 1: CINEAI ASSISTANT (CHATBOT)
// ==========================================
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

  messages.value.push({
    id: `user-${Date.now()}`,
    role: 'user',
    text
  })
  inputMessage.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    const history = messages.value
      .slice(0, messages.value.length - 1)
      .filter(msg => msg.id !== 'welcome')
      .map(msg => ({
        role: msg.role,
        parts: [{ text: msg.text }]
      }))

    const response = await aiDiscoveryService.query(text, history)

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

  ticketsStore.selectMovie(moviePayload)
  ticketsStore.selectCinema(showtime.branchName)
  ticketsStore.selectShowtime(showtime)

  if (import.meta.client) {
    window.dispatchEvent(new CustomEvent('cineai:toast', {
      detail: {
        message: 'Đã chọn suất chiếu! Đang chuyển hướng đến trang chọn ghế...',
        type: 'success'
      }
    }))
  }

  router.push('/checkout/seat')
}

const renderMarkdown = (text: string) => {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br />')
}

// ==========================================
// PERSISTENCE LOGIC (30 MIN SLIDING EXPIRY)
// ==========================================
const CHAT_EXPIRY_MS = 30 * 60 * 1000 // 30 minutes

const saveHistory = () => {
  const data = {
    messages: messages.value,
    expiresAt: Date.now() + CHAT_EXPIRY_MS
  }
  localStorage.setItem('cineai_chat_history', JSON.stringify(data))
}

const loadHistory = () => {
  try {
    const raw = localStorage.getItem('cineai_chat_history')
    if (!raw) return
    const data = JSON.parse(raw)
    if (Date.now() > data.expiresAt) {
      localStorage.removeItem('cineai_chat_history')
      return
    }
    if (data.messages && Array.isArray(data.messages)) {
      messages.value = data.messages
    }
  } catch (e) {
    console.error('Failed to load chat history:', e)
  }
}

const clearChat = () => {
  if (confirm('Bạn có chắc chắn muốn xóa toàn bộ lịch sử chat không?')) {
    messages.value = [
      {
        id: 'welcome',
        role: 'model',
        text: 'Xin chào! Tôi là **CineAI Assistant** 🤖, trợ lý đặt vé thông minh của bạn tại CineAI.\n\nTôi có thể giúp bạn tìm kiếm phim, rạp chiếu, suất chiếu phù hợp dựa trên ngôn ngữ nói tự nhiên. Hãy gõ yêu cầu của bạn bên dưới, ví dụ:\n\n* *"Tôi muốn xem phim Trí Tuệ Nhân Tạo ở quận 1 khoảng 1-4h chiều"* \n* *"Tối nay lúc 8h có phim nào hay ở Hùng Vương không?"* \n* *"Tìm suất chiếu của phim Thành Phố Vô Hình"*'
      }
    ]
    if (process.client) {
      localStorage.removeItem('cineai_chat_history')
    }
  }
}

// Auto-save history whenever messages change
watch(messages, () => {
  if (process.client) {
    saveHistory()
  }
}, { deep: true })

// ==========================================
// HOOKS
// ==========================================
onMounted(() => {
  if (process.client) {
    loadHistory()
  }
  void scrollToBottom()
})
</script>

<template>
  <section class="ai-discovery-container py-8 px-4 sm:px-6 lg:px-8">
    <!-- Glow backgrounds -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-primary-container/10 rounded-full blur-[100px] pointer-events-none"></div>

    <!-- CHATBOT ASSISTANT MODE -->
    <div class="max-w-4xl mx-auto flex flex-col h-[82vh] rounded-3xl border border-white/10 bg-[#121414]/90 p-5 shadow-3xl backdrop-blur-2xl relative overflow-hidden animate-fade-in">
      
      <!-- Header -->
      <header class="flex items-center justify-between pb-4 mb-4 border-b border-white/5 relative z-10">
        <div class="flex items-center gap-4">
          <div class="relative">
            <span class="material-symbols-outlined rounded-2xl bg-gradient-to-tr from-primary-container to-purple-600 p-3 text-white shadow-lg">smart_toy</span>
            <span class="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 border-2 border-[#121414] rounded-full"></span>
          </div>
          <div>
            <h1 class="text-lg sm:text-xl font-black text-white tracking-wide">CineAI Assistant</h1>
            <p class="text-xs text-on-surface-variant flex items-center gap-1.5 mt-0.5">
              <span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-ping"></span>
              Đang hoạt động • Trợ lý đặt vé
            </p>
          </div>
        </div>
        <button @click="clearChat" class="px-3.5 py-2 text-xs font-bold text-gray-400 hover:text-red-400 bg-white/5 border border-white/10 hover:border-red-500/20 hover:bg-red-500/10 rounded-xl transition flex items-center gap-1.5">
          <span class="material-symbols-outlined text-sm">delete</span>
          Xóa lịch sử
        </button>
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
                      <div v-if="isShowtimeExpired(st)" class="absolute inset-0 bg-[#121414]/80 backdrop-blur-[1px] flex items-center justify-center z-20">
                        <span class="px-3 py-1.5 rounded-full border border-red-500/20 bg-red-500/10 text-red-400 font-bold text-xs">
                          Đã hết giờ bán vé
                        </span>
                      </div>
                      <div class="flex gap-3">
                        <div class="w-16 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-white/5">
                          <img :src="getMovieForShowtime(st, msg)?.poster || '/images/movie-placeholder.svg'"
                               :alt="getMovieForShowtime(st, msg)?.title"
                               class="w-full h-full object-cover transition duration-300 group-hover:scale-105" />
                        </div>
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
                          <div class="flex justify-between items-end mt-2">
                            <div>
                              <p class="text-sm font-black text-white">{{ formatDate(st.date) }}</p>
                              <p class="text-base font-black text-red-400 mt-0.5">{{ st.time }}</p>
                            </div>
                            <button @click="handleQuickBook(st, getMovieForShowtime(st, msg))"
                                    :disabled="isShowtimeExpired(st)"
                                    class="px-4 py-2 bg-gradient-to-r from-primary-container to-red-600 hover:from-primary-container hover:to-red-700 text-white font-bold text-xs rounded-xl shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed">
                              Đặt vé
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Match movies list (no showtimes) -->
                <div v-if="!msg.showtimes?.length && msg.movies?.length" class="space-y-3">
                  <h3 class="text-xs font-bold text-purple-300 uppercase tracking-widest flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-base">local_movies</span>
                    Phim được gợi ý:
                  </h3>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div v-for="m in msg.movies" :key="m.id"
                         class="flex gap-4 rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-purple-500/40 hover:bg-white/10 group">
                      <div class="w-20 h-28 rounded-lg overflow-hidden flex-shrink-0 bg-white/5">
                        <img :src="m.poster || '/images/movie-placeholder.svg'" :alt="m.title" class="w-full h-full object-cover transition duration-300 group-hover:scale-105" />
                      </div>
                      <div class="flex-1 flex flex-col justify-between min-w-0">
                        <div>
                          <h4 class="font-bold text-white text-base truncate">{{ m.title }}</h4>
                          <p class="text-xs text-gray-400 mt-1 line-clamp-3 leading-relaxed">{{ m.description || 'Chưa có mô tả chi tiết cho phim này.' }}</p>
                        </div>
                        <NuxtLink :to="getMovieSlugUrl(m)" class="text-xs font-bold text-purple-400 hover:underline flex items-center gap-0.5 mt-2">
                          Xem chi tiết lịch chiếu <span class="material-symbols-outlined text-xs">arrow_forward</span>
                        </NuxtLink>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Input Area -->
      <footer class="border-t border-white/5 pt-4 mt-2 relative z-10">
        <!-- Quick Prompts list (visible when input is empty) -->
        <div v-if="!inputMessage.trim() && messages.length <= 1" class="flex gap-2 overflow-x-auto pb-4 scrollbar-none flex-nowrap whitespace-nowrap">
          <button v-for="promptText in quickPrompts" :key="promptText"
                  @click="selectQuickPrompt(promptText)"
                  class="flex-shrink-0 px-4 py-2 border border-white/5 bg-white/5 hover:bg-white/10 rounded-full text-xs text-gray-300 hover:text-white transition">
            {{ promptText }}
          </button>
        </div>

        <form @submit.prevent="sendMessage" class="flex gap-2">
          <input v-model="inputMessage"
                 placeholder="Hỏi trợ lý đặt vé... (ví dụ: tối nay 8h có phim gì ở rạp Sala?)"
                 class="flex-1 px-5 py-4 bg-white/5 border border-white/10 rounded-2xl text-sm sm:text-base text-white placeholder-gray-500 focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container/30 transition-all" />
          <button type="submit" :disabled="!inputMessage.trim() || isLoading"
                  class="p-4 rounded-2xl bg-gradient-to-tr from-primary-container to-red-600 hover:from-primary-container hover:to-red-700 text-white font-bold transition shadow-lg shadow-red-600/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
            <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span v-else class="material-symbols-outlined text-lg">send</span>
          </button>
        </form>
      </footer>
    </div>
  </section>
</template>

<style scoped>
.panel-glass {
  background: rgba(26, 28, 36, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.scrollbar-custom::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-custom::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-custom::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
}

.scrollbar-custom::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.16);
}

.scrollbar-none::-webkit-scrollbar {
  display: none;
}

.animate-fade-in {
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

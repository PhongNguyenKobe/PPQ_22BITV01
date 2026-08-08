<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketsStore } from '~/store/tickets'
import { aiDiscoveryService, type AiMoodMatchItem } from '~/services/api'
import { isShowtimeExpired } from '~/utils/showtime'
import { getMovieSlugUrl } from '~/utils/slug'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const router = useRouter()
const ticketsStore = useTicketsStore()

// State điều hướng Hub AI: 'select' (chọn chế độ), 'chat' (CineAI Assistant), 'mood' (AI Mood Matcher)
const activeMode = ref<'select' | 'chat' | 'mood'>('chat')

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
// LOGIC CHẾ ĐỘ 2: AI MOOD MATCHER
// ==========================================
const moodPrompt = ref('')
const isMoodLoading = ref(false)
const moodRecommendations = ref<AiMoodMatchItem[]>([])
const moodError = ref('')

const quickMoods = [
  { text: 'Giải tỏa căng thẳng sau giờ làm việc 🎭', prompt: 'Tôi muốn tìm một bộ phim hài hước nhẹ nhàng hoặc hoạt hình vui vẻ để giải tỏa áp lực và stress sau một ngày làm việc mệt mỏi.' },
  { text: 'Hẹn hò lãng mạn cùng người yêu 💖', prompt: 'Tôi muốn xem một bộ phim tình cảm lãng mạn, ấm áp hoặc phim hài nhẹ nhàng để đi xem cùng người yêu vào tối nay.' },
  { text: 'Hack não kịch tính, ly kỳ bất ngờ 🧠', prompt: 'Tôi muốn xem một bộ phim giật gân, ly kỳ, hành động hoặc trinh thám hack não với nhiều cú twist bất ngờ.' },
  { text: 'Phim giải trí lý tưởng cho gia đình 🍿', prompt: 'Tôi muốn tìm một bộ phim phiêu lưu giả tưởng, hoạt hình hoặc phim gia đình thân thiện, dễ xem cho cả người lớn và trẻ em.' }
]

const selectQuickMood = (text: string) => {
  moodPrompt.value = text
  submitMood()
}

const submitMood = async () => {
  const text = moodPrompt.value.trim()
  if (!text || isMoodLoading.value) return

  isMoodLoading.value = true
  moodError.value = ''
  moodRecommendations.value = []

  try {
    const result = await aiDiscoveryService.matchMood(text)
    moodRecommendations.value = result.recommendations
    if (moodRecommendations.value.length === 0) {
      moodError.value = 'Không tìm thấy bộ phim nào phù hợp. Vui lòng thử lại với mô tả khác.'
    }
  } catch (e: any) {
    console.error(e)
    moodError.value = e?.message || 'Đã xảy ra lỗi khi kết nối với CineAI Assistant. Vui lòng thử lại sau.'
  } finally {
    isMoodLoading.value = false
  }
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
  if (activeMode.value === 'chat') {
    void scrollToBottom()
  }
})
</script>

<template>
  <section class="ai-discovery-container py-8 px-4 sm:px-6 lg:px-8">
    <!-- 1. MODE SELECTION VIEW -->
    <div v-if="activeMode === 'select'" class="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8 text-center space-y-12 animate-fade-in relative z-10">
      <!-- Glow backgrounds -->
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-red-600/10 rounded-full blur-[100px] pointer-events-none"></div>

      <div class="space-y-4">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-bold uppercase tracking-wider animate-pulse">
          <span class="material-symbols-outlined text-sm">auto_awesome</span>
          CineAI Intelligence Center
        </div>
        <h1 class="text-3xl sm:text-5xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-gray-400">
          Khám Phá Trí Tuệ Nhân Tạo CineAI
        </h1>
        <p class="text-sm sm:text-base text-gray-400 max-w-2xl mx-auto">
          Chọn một trong hai trợ lý thông minh dưới đây để bắt đầu khám phá thế giới điện ảnh được cá nhân hóa hoàn hảo cho riêng bạn.
        </p>
      </div>

      <!-- Feature Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto pt-6">
        <!-- Card 1: Chatbot Assistant -->
        <div @click="activeMode = 'chat'; scrollToBottom()"
             class="panel-glass p-8 rounded-3xl border border-white/5 bg-[#12141c]/50 hover:bg-[#12141c]/80 hover:border-primary-container/40 transition-all duration-300 cursor-pointer text-left group flex flex-col justify-between h-72 shadow-xl hover:shadow-[0_10px_30px_rgba(229,9,20,0.15)] relative overflow-hidden">
          <div class="absolute -right-16 -top-16 w-32 h-32 bg-primary-container/10 rounded-full blur-2xl group-hover:bg-primary-container/20 transition-all"></div>
          <div class="space-y-4 relative z-10">
            <span class="material-symbols-outlined text-3xl p-3.5 rounded-2xl bg-gradient-to-tr from-primary-container to-red-600 text-white shadow-lg">smart_toy</span>
            <div>
              <h3 class="text-xl font-black text-white group-hover:text-primary-container transition-colors">CineAI Assistant</h3>
              <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mt-1">Tư vấn lịch chiếu & đặt vé trực tuyến</p>
            </div>
            <p class="text-sm text-gray-400 leading-relaxed line-clamp-3">
              Trò chuyện bằng ngôn ngữ tự nhiên để tìm kiếm phim, rạp chiếu, và suất chiếu trực tiếp theo thời gian thực. Hỗ trợ đặt vé siêu tốc.
            </p>
          </div>
          <div class="flex items-center gap-1 text-sm font-bold text-primary-container group-hover:translate-x-1 transition-transform pt-4 relative z-10">
            Bắt đầu trò chuyện <span class="material-symbols-outlined text-sm">arrow_forward</span>
          </div>
        </div>

        <!-- Card 2: AI Mood Matcher -->
        <div @click="activeMode = 'mood'"
             class="panel-glass p-8 rounded-3xl border border-white/5 bg-[#12141c]/50 hover:bg-[#12141c]/80 hover:border-purple-500/40 transition-all duration-300 cursor-pointer text-left group flex flex-col justify-between h-72 shadow-xl hover:shadow-[0_10px_30px_rgba(168,85,247,0.15)] relative overflow-hidden">
          <div class="absolute -right-16 -top-16 w-32 h-32 bg-purple-600/10 rounded-full blur-2xl group-hover:bg-purple-600/20 transition-all"></div>
          <div class="space-y-4 relative z-10">
            <span class="material-symbols-outlined text-3xl p-3.5 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white shadow-lg">psychology</span>
            <div>
              <h3 class="text-xl font-black text-white group-hover:text-purple-400 transition-colors">AI Mood Matcher</h3>
              <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mt-1">Chọn phim theo tâm trạng, cảm xúc</p>
            </div>
            <p class="text-sm text-gray-400 leading-relaxed line-clamp-3">
              Nhập tâm trạng, hoàn cảnh hoặc cảm xúc hiện tại của bạn. AI sẽ lập tức gợi ý Top phim phù hợp nhất đang chiếu kèm lời khuyên chi tiết.
            </p>
          </div>
          <div class="flex items-center gap-1 text-sm font-bold text-purple-400 group-hover:translate-x-1 transition-transform pt-4 relative z-10">
            Tìm phim theo tâm trạng <span class="material-symbols-outlined text-sm">arrow_forward</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. CHATBOT ASSISTANT MODE -->
    <div v-else-if="activeMode === 'chat'" class="max-w-4xl mx-auto flex flex-col h-[82vh] rounded-3xl border border-white/10 bg-[#121414]/90 p-5 shadow-3xl backdrop-blur-2xl relative overflow-hidden animate-fade-in">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-primary-container/10 rounded-full blur-[100px] pointer-events-none"></div>

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

    <!-- 3. AI MOOD MATCHER MODE -->
    <div v-else-if="activeMode === 'mood'" class="max-w-4xl mx-auto relative z-10 space-y-8 animate-fade-in">
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-white/5 pb-4 mb-2">
        <div class="flex items-center gap-4">
          <button @click="activeMode = 'select'" class="p-2 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl text-gray-300 hover:text-white transition flex items-center justify-center" title="Quay lại">
            <span class="material-symbols-outlined text-base">arrow_back</span>
          </button>
          <div>
            <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] font-bold uppercase tracking-wider animate-pulse">
              <span class="material-symbols-outlined text-xs">psychology</span>
              AI Mood Matcher
            </div>
            <h1 class="text-xl font-black text-white tracking-wide mt-1">Chọn Phim Theo Tâm Trạng</h1>
          </div>
        </div>
      </div>

      <!-- Input Card -->
      <div class="panel-glass p-6 rounded-3xl border border-white/10 bg-[#12141c]/80 shadow-2xl backdrop-blur-md space-y-6">
        <div class="space-y-2">
          <label class="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
            <span class="material-symbols-outlined text-sm text-purple-400">chat_bubble</span>
            Bạn đang cảm thấy thế nào hôm nay?
          </label>
          <textarea
            v-model="moodPrompt"
            rows="3"
            placeholder="Ví dụ: Tôi muốn xem một phim hành động gay cấn nhưng không quá bạo lực để đi xem với bạn gái vào tối nay..."
            class="w-full px-5 py-4 bg-white/5 border border-white/10 rounded-2xl text-sm sm:text-base text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/50 transition-all resize-none"
            @keydown.enter.prevent="submitMood"
          ></textarea>
        </div>

        <!-- Quick Suggestions -->
        <div class="space-y-3">
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wider">Gợi ý nhanh:</p>
          <div class="flex flex-wrap gap-2.5">
            <button
              v-for="mood in quickMoods"
              :key="mood.text"
              @click="selectQuickMood(mood.prompt)"
              class="px-3.5 py-2 rounded-xl border border-white/5 bg-white/5 hover:bg-purple-500/10 hover:border-purple-500/30 text-xs text-gray-300 hover:text-white transition-all text-left"
            >
              {{ mood.text }}
            </button>
          </div>
        </div>

        <!-- Action Button -->
        <div class="pt-2 flex justify-end">
          <button
            @click="submitMood"
            :disabled="!moodPrompt.trim() || isMoodLoading"
            class="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-purple-600 to-red-600 hover:from-purple-700 hover:to-red-700 text-white font-bold text-sm sm:text-base rounded-2xl transition-all shadow-lg shadow-red-600/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isMoodLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span v-else class="material-symbols-outlined text-lg">magic_button</span>
            {{ isMoodLoading ? 'AI Đang Phân Tích...' : 'AI Khớp Tâm Trạng' }}
          </button>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="moodError" class="panel-glass p-5 rounded-2xl border border-red-500/20 bg-red-500/5 text-red-400 text-center flex items-center justify-center gap-2">
        <span class="material-symbols-outlined text-lg">error</span>
        <span class="font-medium text-sm">{{ moodError }}</span>
      </div>

      <!-- Recommendations Output -->
      <div v-if="moodRecommendations.length" class="space-y-6 animate-fade-in pb-10">
        <div class="border-b border-white/5 pb-3">
          <h3 class="text-base sm:text-lg font-black text-white flex items-center gap-2">
            <span class="material-symbols-outlined text-yellow-400">workspace_premium</span>
            Top Phim Phù Hợp Nhất Với Bạn
          </h3>
        </div>

        <div class="grid grid-cols-1 gap-6">
          <div
            v-for="(item, index) in moodRecommendations"
            :key="item.movie.id"
            class="panel-glass p-5 sm:p-6 rounded-3xl border border-white/5 bg-[#12141c]/50 hover:bg-[#12141c]/80 transition-all flex flex-col md:flex-row gap-6 relative overflow-hidden group shadow-md"
          >
            <!-- Rank Badge -->
            <div class="absolute top-4 left-4 w-7 h-7 rounded-full flex items-center justify-center font-black text-xs z-10 shadow bg-gradient-to-tr from-purple-600 to-red-600 text-white">
              #{{ index + 1 }}
            </div>

            <!-- Movie Poster -->
            <div class="w-full md:w-[140px] aspect-[2/3] rounded-2xl overflow-hidden bg-slate-800 flex-shrink-0 relative mx-auto md:mx-0">
              <img v-if="item.movie.poster" :src="item.movie.poster" :alt="item.movie.title" class="w-full h-full object-cover group-hover:scale-105 transition duration-500" />
              <div v-else class="w-full h-full flex flex-col items-center justify-center p-4 text-center">
                <span class="material-symbols-outlined text-4xl text-gray-600">local_movies</span>
              </div>
            </div>

            <!-- Movie Details & Reason -->
            <div class="flex-1 flex flex-col justify-between space-y-4">
              <div class="space-y-2">
                <div class="flex flex-wrap items-center gap-2">
                  <h4 class="text-lg sm:text-xl font-black text-white group-hover:text-purple-400 transition-colors leading-tight">
                    {{ item.movie.title }}
                  </h4>
                  <span v-if="item.movie.genre && item.movie.genre.length" class="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[9px] text-gray-400 font-bold uppercase tracking-wider">
                    {{ item.movie.genre[0] }}
                  </span>
                </div>
                <p class="text-[11px] text-gray-500 font-medium">
                  Thời lượng: {{ item.movie.duration }} phút | Thể loại: {{ item.movie.genre ? item.movie.genre.join(', ') : 'Đang cập nhật' }}
                </p>
                <p class="text-xs sm:text-sm text-gray-400 line-clamp-3 leading-relaxed">
                  {{ item.movie.description || 'Chưa có mô tả chi tiết cho phim này.' }}
                </p>
              </div>

              <!-- AI Personalized Explanation -->
              <div class="p-4 rounded-2xl bg-purple-500/5 border border-purple-500/20 text-xs sm:text-sm text-purple-300 leading-relaxed relative overflow-hidden">
                <div class="absolute top-0 right-0 p-2 opacity-15">
                  <span class="material-symbols-outlined text-4xl">smart_toy</span>
                </div>
                <div class="flex items-start gap-2 relative z-10">
                  <span class="material-symbols-outlined text-sm text-purple-400 mt-0.5">smart_toy</span>
                  <div>
                    <strong class="text-purple-200">Lời khuyên từ AI Assistant:</strong>
                    <p class="mt-1 text-purple-300/90 font-medium">{{ item.reason }}</p>
                  </div>
                </div>
              </div>

              <!-- Buttons -->
              <div class="flex flex-wrap items-center gap-3 pt-1">
                <NuxtLink
                  :to="getMovieSlugUrl(item.movie)"
                  class="px-4 py-2 bg-white/5 hover:bg-white/10 text-white font-bold text-xs rounded-xl border border-white/10 hover:border-white/20 transition-all flex items-center gap-1.5"
                >
                  <span class="material-symbols-outlined text-sm">info</span>
                  Chi tiết phim
                </NuxtLink>
                <NuxtLink
                  :to="getMovieSlugUrl(item.movie)"
                  class="px-4 py-2 bg-gradient-to-r from-purple-600 to-red-600 hover:from-purple-700 hover:to-red-700 text-white font-bold text-xs rounded-xl transition-all shadow-md flex items-center gap-1.5"
                >
                  <span class="material-symbols-outlined text-sm">confirmation_number</span>
                  Đặt vé ngay
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
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

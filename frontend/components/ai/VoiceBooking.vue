<script setup lang="ts">
import { ref } from 'vue'
import { aiService } from '~/services/api'
import { useTicketsStore } from '~/store/tickets'
import { useMoviesStore } from '~/store/movies'

const isListening = ref(false)
const transcript = ref('')
const responseText = ref('')
const loading = ref(false)
const showDialog = ref(false)

// We can support real SpeechRecognition if supported by the browser
let recognition: any = null

function initSpeechRecognition() {
  if (process.client) {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (SpeechRecognition) {
      recognition = new SpeechRecognition()
      recognition.lang = 'vi-VN'
      recognition.continuous = false
      recognition.interimResults = false

      recognition.onstart = () => {
        isListening.value = true
        transcript.value = 'Đang lắng nghe... Hãy nói "Đặt vé phim Dune"'
        responseText.value = ''
      }

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error', event)
        isListening.value = false
        transcript.value = 'Không thể nghe rõ. Vui lòng bấm để thử lại hoặc chọn lệnh mẫu dưới đây.'
      }

      recognition.onend = () => {
        isListening.value = false
      }

      recognition.onresult = async (event: any) => {
        const textResult = event.results[0][0].transcript
        transcript.value = `Bạn nói: "${textResult}"`
        await handleVoiceTranscript(textResult)
      }
    }
  }
}

function startListening() {
  showDialog.value = true
  if (!recognition) {
    initSpeechRecognition()
  }

  if (recognition) {
    try {
      recognition.start()
    } catch (e) {
      // In case recognition is already running
      recognition.stop()
    }
  } else {
    // If Web Speech is not supported, we show the mock actions dialog directly
    transcript.value = 'Trình duyệt không hỗ trợ micro. Bạn có thể sử dụng các lệnh mẫu bên dưới:'
  }
}

async function handleVoiceTranscript(text: string) {
  loading.value = true
  try {
    const result = await aiService.parseVoiceCommand(text)
    transcript.value = `Nhận diện: "${result.text}"`
    
    if (result.parsedAction === 'BOOK_MOVIE' && result.data) {
      responseText.value = 'Đang dẫn bạn đến trang đặt vé phim Dune: Part Two...'
      setTimeout(() => {
        showDialog.value = false
        navigateTo(`/movies/${result.data.movieId}`)
      }, 2000)
    } else if (result.parsedAction === 'SEARCH_GENRE' && result.data) {
      responseText.value = `Đang tìm kiếm phim thuộc thể loại: ${result.data.genre}...`
      const moviesStore = useMoviesStore()
      await moviesStore.searchMovies(result.data.genre)
      setTimeout(() => {
        showDialog.value = false
        navigateTo('/movies')
      }, 2000)
    } else if (result.parsedAction === 'VIEW_SHOWTIMES' && result.data) {
      responseText.value = 'Đang hiển thị thông tin phim John Wick...'
      setTimeout(() => {
        showDialog.value = false
        navigateTo(`/movies/${result.data.movieId}`)
      }, 2000)
    } else {
      responseText.value = 'CineAI chưa hiểu rõ lệnh này. Bạn hãy thử nói lại: "Đặt vé phim Dune" hoặc "Tìm phim hành động".'
    }
  } catch (e) {
    responseText.value = 'Không thể phân tích khẩu lệnh. Vui lòng thử lại!'
  } finally {
    loading.value = false
  }
}

function selectMockCommand(commandText: string) {
  transcript.value = `Lệnh mẫu: "${commandText}"`
  handleVoiceTranscript(commandText)
}
</script>

<template>
  <div>
    <!-- Floating Mic Button -->
    <button
      @click="startListening"
      class="fixed bottom-6 left-6 z-40 w-14 h-14 rounded-full flex items-center justify-center text-white bg-primary-container shadow-2xl red-glow hover:scale-105 active:scale-95 transition-all duration-300 group"
      aria-label="Đặt vé bằng giọng nói"
    >
      <span class="material-symbols-outlined text-[28px] group-hover:scale-110 transition-transform">mic</span>
      <span class="absolute -inset-1 rounded-full border border-primary-container/30 animate-ping"></span>
    </button>

    <!-- Voice Booking Dialog Overlay -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showDialog" class="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-6 relative flex flex-col items-center">
          <button @click="showDialog = false" class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface">
            <span class="material-symbols-outlined">close</span>
          </button>

          <h3 class="font-headline-md text-xl font-bold text-center mb-6 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary-container animate-pulse">mic</span>
            Đặt Vé Bằng Giọng Nói AI
          </h3>

          <!-- Mic Animation Orb -->
          <div
            class="w-24 h-24 rounded-full flex items-center justify-center mb-6 relative"
            :class="isListening ? 'bg-primary-container animate-pulse' : 'bg-surface-container-high border border-glass-stroke'"
          >
            <span class="material-symbols-outlined text-[48px]" :class="isListening ? 'text-white' : 'text-on-surface-variant'">mic</span>
            
            <template v-if="isListening">
              <span class="absolute -inset-4 rounded-full border-2 border-primary-container/40 animate-ping"></span>
              <span class="absolute -inset-8 rounded-full border border-primary-container/20 animate-ping" style="animation-delay: 200ms"></span>
            </template>
          </div>

          <div class="w-full text-center mb-6">
            <p class="text-sm font-semibold text-on-surface mb-2 h-12 flex items-center justify-center px-4">
              {{ transcript }}
            </p>
            <p v-if="loading" class="text-xs text-secondary animate-pulse">AI đang suy nghĩ...</p>
            <p v-else class="text-xs text-primary-fixed-dim font-medium min-h-[20px]">{{ responseText }}</p>
          </div>

          <!-- Mock Actions Fallback -->
          <div class="w-full border-t border-glass-stroke pt-4">
            <span class="text-xs text-on-surface-variant block mb-3 uppercase tracking-wider text-center font-bold">Hoặc Click Lệnh Mẫu</span>
            <div class="grid grid-cols-1 gap-2">
              <button
                @click="selectMockCommand('Cho tôi đặt vé phim Dune tối nay ở Sala')"
                class="text-left text-xs bg-surface-container-high hover:bg-white/10 px-3 py-2.5 rounded-xl border border-glass-stroke flex items-center gap-2 text-on-surface hover:text-primary transition-all"
              >
                <span class="material-symbols-outlined text-sm">play_arrow</span>
                "Cho tôi đặt vé phim Dune tối nay ở Sala"
              </button>
              <button
                @click="selectMockCommand('Tìm kiếm phim hành động hay nhất')"
                class="text-left text-xs bg-surface-container-high hover:bg-white/10 px-3 py-2.5 rounded-xl border border-glass-stroke flex items-center gap-2 text-on-surface hover:text-primary transition-all"
              >
                <span class="material-symbols-outlined text-sm">search</span>
                "Tìm kiếm phim hành động hay nhất"
              </button>
              <button
                @click="selectMockCommand('Tôi muốn xem lịch chiếu John Wick')"
                class="text-left text-xs bg-surface-container-high hover:bg-white/10 px-3 py-2.5 rounded-xl border border-glass-stroke flex items-center gap-2 text-on-surface hover:text-primary transition-all"
              >
                <span class="material-symbols-outlined text-sm">schedule</span>
                "Tôi muốn xem lịch chiếu John Wick"
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

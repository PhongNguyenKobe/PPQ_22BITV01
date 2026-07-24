<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { aiService } from '~/services/api'

interface Message {
  sender: 'user' | 'bot'
  text: string
  time: string
}

const isOpen = ref(false)
const queryInput = ref('')
const loading = ref(false)
const messages = ref<Message[]>([
  {
    sender: 'bot',
    text: 'Xin chào! Tôi là CineAI Assistant 🤖. Tôi có thể gợi ý phim và hướng dẫn đặt vé nhanh cho bạn. Bạn muốn xem phim gì hôm nay?',
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
])

const chatContainer = ref<HTMLElement | null>(null)

const quickReplies = [
  'Gợi ý phim hay',
  'Giá vé thế nào?',
  'Lịch chiếu phim hôm nay',
  'Hướng dẫn đặt vé'
]

async function sendMessage(text: string) {
  if (!text.trim() || loading.value) return
  
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  
  // Append User message
  messages.value.push({
    sender: 'user',
    text,
    time
  })
  
  queryInput.value = ''
  loading.value = true
  
  await scrollToBottom()
  
  try {
    const res = await aiService.askChatbot(text)
    
    // Append Bot message
    messages.value.push({
      sender: 'bot',
      text: res.response,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })

    // Perform specific navigation actions if requested by the AI
    if (res.action === 'NAVIGATE_TO_MOVIES') {
      navigateTo('/products')
    }
  } catch (e) {
    messages.value.push({
      sender: 'bot',
      text: 'Xin lỗi, hệ thống AI đang bận xử lý. Bạn vui lòng thử lại sau giây lát!',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
    <!-- Chat Window -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform scale-95 opacity-0 translate-y-10"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 translate-y-10"
    >
      <div v-if="isOpen" class="glass-panel w-[360px] h-[500px] rounded-2xl flex flex-col shadow-2xl border border-glass-stroke overflow-hidden mb-4">
        <!-- Chat Header -->
        <div class="bg-surface-container-high px-4 py-3 flex items-center justify-between border-b border-glass-stroke">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center text-white animate-ai">
              <span class="material-symbols-outlined">smart_toy</span>
            </div>
            <div>
              <h4 class="font-bold text-sm text-on-surface">Trợ Lý CineAI</h4>
              <span class="text-xs text-green-400 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-green-400 inline-block animate-ping"></span>
                Trực tuyến
              </span>
            </div>
          </div>
          <button @click="isOpen = false" class="text-on-surface-variant hover:text-on-surface">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <!-- Chat Messages -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="flex"
            :class="msg.sender === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[75%] rounded-2xl px-4 py-2.5 text-sm"
              :class="msg.sender === 'user'
                ? 'bg-primary-container text-on-primary-container rounded-tr-none'
                : 'bg-surface-container-high border border-glass-stroke text-on-surface rounded-tl-none'"
            >
              <p class="whitespace-pre-line leading-relaxed">{{ msg.text }}</p>
              <span class="text-[10px] text-on-surface-variant block text-right mt-1">{{ msg.time }}</span>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="loading" class="flex justify-start">
            <div class="bg-surface-container-high border border-glass-stroke rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-1.5">
              <div class="w-1.5 h-1.5 bg-primary-container rounded-full animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-1.5 h-1.5 bg-primary-container rounded-full animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-1.5 h-1.5 bg-primary-container rounded-full animate-bounce" style="animation-delay: 300ms"></div>
            </div>
          </div>
        </div>

        <!-- Quick Replies -->
        <div class="px-4 py-2 bg-surface-container-low border-t border-glass-stroke overflow-x-auto hide-scrollbar flex gap-2 flex-shrink-0">
          <button
            v-for="reply in quickReplies"
            :key="reply"
            @click="sendMessage(reply)"
            class="text-xs bg-surface border border-glass-stroke hover:border-primary-container px-3 py-1.5 rounded-full whitespace-nowrap text-on-surface-variant hover:text-on-surface transition-all"
          >
            {{ reply }}
          </button>
        </div>

        <!-- Chat Input -->
        <form @submit.prevent="sendMessage(queryInput)" class="p-3 bg-surface border-t border-glass-stroke flex items-center gap-2">
          <input
            v-model="queryInput"
            type="text"
            placeholder="Nhập câu hỏi của bạn..."
            class="bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container flex-1 text-on-surface"
          />
          <button type="submit" class="bg-primary-container hover:bg-opacity-90 text-white w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 red-glow">
            <span class="material-symbols-outlined">send</span>
          </button>
        </form>
      </div>
    </transition>

    <!-- Floating Toggle Button -->
    <button
      @click="isOpen = !isOpen"
      class="w-14 h-14 rounded-full flex items-center justify-center text-white ai-gradient-border shadow-2xl relative group red-glow hover:scale-105 active:scale-95 transition-all duration-300"
    >
      <span class="material-symbols-outlined text-[28px] relative z-10 group-hover:rotate-12 transition-transform">smart_toy</span>
      <span class="absolute -top-1 -right-1 w-3 h-3 bg-primary-container rounded-full animate-ping z-20"></span>
      <span class="absolute -top-1 -right-1 w-3 h-3 bg-primary-container rounded-full z-20"></span>
    </button>
  </div>
</template>


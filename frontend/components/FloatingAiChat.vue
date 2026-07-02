<script setup lang="ts">
import { ref } from 'vue'

const isOpen = ref(false)
const inputMessage = ref('')
const messages = ref([
  { role: 'ai', text: 'Chào bạn! Tôi là trợ lý ảo CineAI. Tôi có thể giúp bạn tìm lịch chiếu, gợi ý phim theo sở thích, hoặc chọn combo bắp nước phù hợp.' }
])
const suggestions = [
  'Tìm phim hành động cuối tuần',
  'Rạp nào gần đây có IMAX?',
  'Phim ma mới nhất có hay không?'
]

function toggleChat() {
  isOpen.value = !isOpen.value
}

function sendMessage(text?: string) {
  const msg = text || inputMessage.value.trim()
  if (!msg) return
  
  messages.value.push({ role: 'user', text: msg })
  inputMessage.value = ''
  
  // Fake AI response
  setTimeout(() => {
    messages.value.push({ 
      role: 'ai', 
      text: `Đây là phản hồi tự động từ CineAI: Bạn vừa hỏi "${msg}". Tính năng kết nối LLM thực tế sẽ được tích hợp sau.` 
    })
  }, 1000)
}
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
    <!-- Chat Window -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-8 opacity-0 scale-95"
      enter-to-class="transform translate-y-0 opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100 scale-100"
      leave-to-class="transform translate-y-8 opacity-0 scale-95"
    >
      <div v-if="isOpen" class="mb-4 w-80 md:w-96 h-[500px] flex flex-col rounded-2xl overflow-hidden shadow-[0_10px_40px_rgba(0,0,0,0.5)] border border-white/10" style="background:rgba(18,20,20,0.95);backdrop-filter:blur(16px)">
        <!-- Header -->
        <div class="p-4 flex items-center justify-between border-b border-white/10" style="background:linear-gradient(to right,rgba(229,9,20,0.1),rgba(138,43,226,0.1))">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full flex items-center justify-center bg-primary-container text-white">
              <span class="material-symbols-outlined text-[20px]">smart_toy</span>
            </div>
            <div>
              <h4 class="font-label-md text-label-md font-bold text-on-surface">CineAI Assistant</h4>
              <span class="font-label-sm text-[10px] text-primary flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-primary inline-block animate-pulse"></span> Trực tuyến
              </span>
            </div>
          </div>
          <button @click="toggleChat" class="text-on-surface-variant hover:text-white transition-colors">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <!-- Chat History -->
        <div class="flex-grow p-4 overflow-y-auto flex flex-col gap-4">
          <div v-for="(msg, i) in messages" :key="i" class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start items-end gap-2'">
            <div v-if="msg.role === 'ai'" class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center bg-surface-container-high text-primary mb-1 border border-white/5">
              <span class="material-symbols-outlined text-[16px]">smart_toy</span>
            </div>
            <div 
              class="p-3 rounded-2xl font-body-sm text-sm"
              :class="msg.role === 'user' 
                ? 'bg-[#1F1F1F] text-on-surface rounded-tr-sm max-w-[80%] border border-white/5' 
                : 'bg-primary-container/10 text-on-surface rounded-tl-sm max-w-[85%] border border-primary-container/20'"
            >
              {{ msg.text }}
            </div>
          </div>
        </div>

        <!-- Suggestions -->
        <div v-if="messages.length < 3" class="px-4 pb-2 flex flex-wrap gap-2">
          <button v-for="sug in suggestions" :key="sug" @click="sendMessage(sug)" class="text-[11px] font-label-sm bg-surface-container hover:bg-white/10 text-on-surface-variant px-3 py-1.5 rounded-full border border-white/5 transition-colors">
            {{ sug }}
          </button>
        </div>

        <!-- Input Area -->
        <div class="p-3 border-t border-white/10 bg-surface">
          <form @submit.prevent="sendMessage()" class="flex items-center gap-2 bg-[#121212] border border-white/10 rounded-full px-4 py-2">
            <input 
              v-model="inputMessage" 
              type="text" 
              placeholder="Hỏi AI bất kỳ điều gì..." 
              class="flex-grow bg-transparent border-none focus:ring-0 text-sm text-on-surface placeholder:text-on-surface-variant outline-none py-1"
            >
            <button type="submit" class="text-primary-container hover:scale-110 transition-transform">
              <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">send</span>
            </button>
          </form>
        </div>
      </div>
    </transition>

    <!-- Floating Button -->
    <button 
      @click="toggleChat"
      class="w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 relative group"
      :class="isOpen ? 'bg-surface-container border border-white/10 text-on-surface hover:bg-white/5' : 'bg-gradient-to-r from-primary-container to-[#8a2be2] text-white hover:scale-110 shadow-[0_0_20px_-5px_rgba(229,9,20,0.5)]'"
    >
      <div v-if="!isOpen" class="absolute -inset-2 bg-primary-container/20 rounded-full animate-ping pointer-events-none group-hover:hidden"></div>
      <span class="material-symbols-outlined text-[28px]" :class="isOpen ? 'rotate-90 scale-0 opacity-0 absolute' : 'rotate-0 scale-100 opacity-100 absolute transition-all duration-300'">smart_toy</span>
      <span class="material-symbols-outlined text-[28px]" :class="isOpen ? 'rotate-0 scale-100 opacity-100 absolute transition-all duration-300' : '-rotate-90 scale-0 opacity-0 absolute'">close</span>
    </button>
  </div>
</template>

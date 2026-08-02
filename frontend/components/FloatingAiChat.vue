<script setup lang="ts">
import { ref } from 'vue'

const isOpen = ref(false)
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
    <transition
      enter-active-class="transition duration-200"
      enter-from-class="translate-y-4 opacity-0"
      leave-active-class="transition duration-150"
      leave-to-class="translate-y-4 opacity-0"
    >
      <div v-if="isOpen" class="mb-4 w-80 rounded-2xl border border-white/10 bg-[#121414]/95 p-6 shadow-2xl backdrop-blur-xl">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined rounded-full bg-primary-container p-2 text-white animate-pulse">smart_toy</span>
            <div>
              <h4 class="font-bold text-white">CineAI Assistant</h4>
              <p class="text-xs text-green-400 font-bold">Online</p>
            </div>
          </div>
          <button class="text-on-surface-variant hover:text-white" @click="isOpen = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <p class="mt-5 text-sm leading-6 text-on-surface-variant">
          Chào bạn! Tôi có thể giúp bạn tìm lịch chiếu, gợi ý phim và hỗ trợ đặt vé bằng ngôn ngữ tự nhiên một cách nhanh chóng.
        </p>
        <NuxtLink to="/ai-discovery" class="mt-5 inline-flex items-center gap-2 text-sm font-bold text-primary-container" @click="isOpen = false">
          Trò chuyện với AI ngay
          <span class="material-symbols-outlined text-base">arrow_forward</span>
        </NuxtLink>
      </div>
    </transition>

    <button
      class="flex h-14 w-14 items-center justify-center rounded-full bg-primary-container text-white shadow-[0_0_25px_rgba(229,9,20,.35)] transition hover:scale-105"
      title="CineAI Assistant — đang phát triển"
      @click="isOpen = !isOpen"
    >
      <span class="material-symbols-outlined text-2xl">smart_toy</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const config = useRuntimeConfig()
const pageId = config.public.facebookPageId
const appId = config.public.facebookAppId

const isOfficialLoaded = ref(false)
const showTooltip = ref(false)
let checkInterval: any = null

const checkOfficialSdk = () => {
  // Check if Facebook customer chat iframe or dialog element is rendered
  // Facebook SDK renders an iframe with names like "fXXXXX" and source containing facebook.com, or specific class lists
  const fbIframe = document.querySelector('iframe[src*="facebook.com/plugins/customer_chat"], iframe[name^="f"], .fb_dialog')
  if (fbIframe) {
    isOfficialLoaded.value = true
    if (checkInterval) {
      clearInterval(checkInterval)
      checkInterval = null
    }
  }
}

onMounted(() => {
  if (!pageId) return

  // 1. Set attributes on fb-customer-chat element
  const chatbox = document.getElementById('fb-customer-chat')
  if (chatbox) {
    chatbox.setAttribute('page_id', pageId)
    chatbox.setAttribute('attribution', 'biz_inbox')
  }

  // 2. Initialize Facebook SDK
  window.fbAsyncInit = function() {
    window.FB.init({
      appId: appId || undefined,
      xfbml: true,
      version: 'v18.0'
    })
  }

  // 3. Inject Facebook SDK Script
  if (!document.getElementById('facebook-jssdk')) {
    const js = document.createElement('script')
    js.id = 'facebook-jssdk'
    js.src = 'https://connect.facebook.net/vi_VN/sdk/xfbml.customerchat.js'
    const fjs = document.getElementsByTagName('script')[0]
    if (fjs && fjs.parentNode) {
      fjs.parentNode.insertBefore(js, fjs)
    } else {
      document.head.appendChild(js)
    }
  }

  // 4. Start interval to detect if official Facebook SDK has successfully rendered
  // (check every 1 second, up to 12 seconds to prevent infinite looping)
  let count = 0
  checkInterval = setInterval(() => {
    checkOfficialSdk()
    count++
    if (count > 12 && checkInterval) {
      clearInterval(checkInterval)
      checkInterval = null
    }
  }, 1000)
})

onBeforeUnmount(() => {
  if (checkInterval) {
    clearInterval(checkInterval)
  }
})

// Types for window
declare global {
  interface Window {
    fbAsyncInit: () => void;
    FB: any;
  }
}
</script>

<template>
  <div v-if="pageId">
    <!-- Official Messenger Chat Markup -->
    <div id="fb-root"></div>
    <div id="fb-customer-chat" class="fb-customerchat"></div>

    <!-- Fallback Custom Floating Messenger Button -->
    <div 
      v-if="!isOfficialLoaded"
      class="fixed bottom-24 right-6 z-50 flex flex-col items-end group"
      @mouseenter="showTooltip = true"
      @mouseleave="showTooltip = false"
    >
      <!-- Tooltip -->
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 translate-x-2"
        leave-active-class="transition duration-150 ease-in"
        leave-to-class="opacity-0 translate-x-2"
      >
        <div 
          v-show="showTooltip" 
          class="absolute right-16 top-1/2 -translate-y-1/2 whitespace-nowrap rounded-lg border border-white/10 bg-black/80 px-3 py-1.5 text-xs font-semibold text-white shadow-lg backdrop-blur-md"
        >
          Chat qua Messenger
        </div>
      </transition>

      <!-- Pulse ripple effect -->
      <span class="absolute inline-flex h-14 w-14 animate-ping rounded-full bg-gradient-to-tr from-[#0695FF] via-[#A334FA] to-[#FF6968] opacity-25"></span>

      <!-- Floating Button -->
      <a
        :href="`https://m.me/${pageId}`"
        target="_blank"
        rel="noopener noreferrer"
        class="relative flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-tr from-[#0695FF] via-[#A334FA] to-[#FF6968] text-white shadow-[0_0_20px_rgba(163,52,250,0.4)] transition duration-300 hover:scale-110 hover:shadow-[0_0_30px_rgba(163,52,250,0.6)]"
      >
        <!-- Messenger SVG Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" class="h-6 w-6 fill-white">
          <path d="M224 32C103.6 32 5.7 124 5.7 236.8c0 61.1 29 116.1 76.5 155.1V480c0 8.6 6.8 15.6 15.2 15.6 5.1 0 9.7-2.5 12.5-6.8l53.8-82c19.3 5.4 39.8 8.4 60.3 8.4 120.4 0 218.3-92 218.3-204.8S344.4 32 224 32zm42.6 230.1l-50.6-54c-7.4-7.9-19.8-7.9-27.2 0l-50.6 54c-12 12.8-31.5 5.5-33.3-12.1l-10-97.1c-1.4-13.4 13.9-22.3 24.9-14.1l50.6 37.9c7.4 5.5 17.7 5.5 25.1 0l50.6-37.9c11-8.2 26.3.7 24.9 14.1l-10 97.1c-1.8 17.6-21.3 24.9-33.3 12.1z"/>
        </svg>
      </a>
    </div>
  </div>
</template>

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: false },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'
    }
  },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],
  app: {
    head: {
      title: 'CineAI - Đặt vé xem phim thông minh với AI',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'Hệ thống đặt vé xem phim dạng Multi-vendor tích hợp AI gợi ý, tìm kiếm ngữ nghĩa, và đặt vé bằng giọng nói.' }
      ],
      link: [
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap' }
      ],
      bodyAttrs: {
        class: 'bg-background text-on-surface font-body-md antialiased min-h-screen selection:bg-primary-container selection:text-white'
      }
    }
  },
  css: [
    '~/assets/css/tailwind.css'
  ],
  pinia: {
    storesDirs: ['./store/**']
  }
})

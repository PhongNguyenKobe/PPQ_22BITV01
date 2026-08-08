// https://nuxt.com/docs/api/configuration/nuxt-config

export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',

  devtools: {
    enabled: false
  },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],

  runtimeConfig: {
    tmdbToken: process.env.TMDB_API_TOKEN,
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
      facebookPageId: process.env.NUXT_PUBLIC_FACEBOOK_PAGE_ID || '883225894869557',
      facebookAppId: process.env.NUXT_PUBLIC_FACEBOOK_APP_ID || '844524511361538'
    }
  },

  app: {
    head: {
      title: 'CineAI - Đặt vé xem phim thông minh với AI',
      htmlAttrs: {
        lang: 'vi'
      },
      meta: [
        { charset: 'utf-8' },
        {
          name: 'viewport',
          content: 'width=device-width, initial-scale=1'
        },
        {
          name: 'description',
          content: 'CineAI - Hệ thống đặt vé xem phim thông minh ứng dụng Trí Tuệ Nhân Tạo (AI). Khám phá phim hay đang chiếu, tìm kiếm lịch chiếu suất chiếu ngữ nghĩa chuẩn xác, đặt vé và combo bắp nước nhanh chóng, an toàn cùng nhiều chương trình khuyến mãi ưu đãi cực kỳ hấp dẫn mỗi ngày.'
        },
        // Open Graph / Facebook
        { property: 'fb:app_id', content: process.env.NUXT_PUBLIC_FACEBOOK_APP_ID || '844524511361538' },
        { property: 'og:type', content: 'website' },
        { property: 'og:title', content: 'CineAI - Đặt vé xem phim thông minh với AI' },
        { property: 'og:description', content: 'CineAI - Hệ thống đặt vé xem phim thông minh ứng dụng Trí Tuệ Nhân Tạo (AI). Khám phá phim hay đang chiếu, tìm kiếm lịch chiếu suất chiếu ngữ nghĩa chuẩn xác, đặt vé và combo bắp nước nhanh chóng, an toàn cùng nhiều chương trình khuyến mãi ưu đãi cực kỳ hấp dẫn mỗi ngày.' },
        { property: 'og:image', content: 'http://localhost:3000/images/icons8-cinema-ticket-16.png' },
        { property: 'og:url', content: 'http://localhost:3000' },
        // Twitter
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: 'CineAI - Đặt vé xem phim thông minh với AI' },
        { name: 'twitter:description', content: 'CineAI - Hệ thống đặt vé xem phim thông minh ứng dụng Trí Tuệ Nhân Tạo (AI). Khám phá phim hay đang chiếu, tìm kiếm lịch chiếu suất chiếu ngữ nghĩa chuẩn xác, đặt vé và combo bắp nước nhanh chóng, an toàn cùng nhiều chương trình khuyến mãi ưu đãi cực kỳ hấp dẫn mỗi ngày.' },
        { name: 'twitter:image', content: 'http://localhost:3000/images/icons8-cinema-ticket-16.png' }
      ],
      link: [
        {
          rel: 'icon',
          type: 'image/png',
          href: '/images/icons8-cinema-ticket-16.png'
        },
        {
          rel: 'canonical',
          href: 'http://localhost:3000'
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap'
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap'
        }
      ],
      script: [
        // Schema.org Structured Data
        {
          type: 'application/ld+json',
          innerHTML: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "CineAI",
            "url": "http://localhost:3000",
            "description": "Hệ thống đặt vé xem phim dạng Multi-vendor tích hợp AI gợi ý và tìm kiếm ngữ nghĩa.",
            "potentialAction": {
              "@type": "SearchAction",
              "target": "http://localhost:3000/ai-discovery?q={search_term_string}",
              "query-input": "required name=search_term_string"
            }
          })
        },
        // Google Analytics (GA4)
        {
          src: 'https://www.googletagmanager.com/gtag/js?id=G-CINEAI1234',
          async: true
        },
        {
          innerHTML: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-CINEAI1234');
          `
        }
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


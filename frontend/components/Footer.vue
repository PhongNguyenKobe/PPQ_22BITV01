<script setup lang="ts">
const currentYear = new Date().getFullYear()

const navigationLinks = [
  { name: 'Phim', to: '/movies' },
  { name: 'Lịch chiếu', to: '/showtimes' },
  { name: 'Rạp chiếu', to: '/cinemas' },
  { name: 'AI Discovery', to: '/ai' }
]

const supportLinks = [
  { name: 'Trung tâm hỗ trợ', to: '/support' },
  { name: 'Điều khoản dịch vụ', to: '/terms' },
  { name: 'Chính sách bảo mật', to: '/privacy' },
  { name: 'Liên hệ', to: '/contact' }
]

const socialLinks = [
  {
    name: 'Facebook',
    icon: 'facebook',
    href: 'https://facebook.com'
  },
  {
    name: 'Instagram',
    icon: 'photo_camera',
    href: 'https://instagram.com'
  },
  {
    name: 'YouTube',
    icon: 'play_circle',
    href: 'https://youtube.com'
  },
  {
    name: 'TikTok',
    icon: 'music_note',
    href: 'https://tiktok.com'
  }
]
</script>

<template>
  <footer
    class="mt-24 border-t border-glass-stroke bg-surface-container-lowest/90 backdrop-blur-xl"
  >
    <div
      class="mx-auto grid max-w-container-max gap-12 px-6 py-16 md:grid-cols-2 lg:grid-cols-4"
    >
      <!-- Brand -->
      <section>
        <NuxtLink
          to="/"
          class="text-3xl font-bold text-primary-container hover:opacity-90"
        >
          CineAI
        </NuxtLink>

        <p class="mt-5 text-sm leading-7 text-on-surface-variant">
          CineAI là nền tảng đặt vé xem phim thông minh ứng dụng Trí Tuệ Nhân Tạo,
          giúp người dùng khám phá phim phù hợp, đặt vé nhanh chóng và trải nghiệm
          điện ảnh hiện đại.
        </p>
      </section>

      <!-- Navigation -->
      <nav>
        <h3
          class="mb-5 text-sm font-bold uppercase tracking-wider text-on-surface"
        >
          Khám phá
        </h3>

        <ul class="space-y-3">
          <li
            v-for="item in navigationLinks"
            :key="item.to"
          >
            <NuxtLink
              :to="item.to"
              class="text-sm text-on-surface-variant transition hover:text-primary-container"
            >
              {{ item.name }}
            </NuxtLink>
          </li>
        </ul>
      </nav>

      <!-- Support -->
      <nav>
        <h3
          class="mb-5 text-sm font-bold uppercase tracking-wider text-on-surface"
        >
          Hỗ trợ
        </h3>

        <ul class="space-y-3">
          <li
            v-for="item in supportLinks"
            :key="item.to"
          >
            <NuxtLink
              :to="item.to"
              class="text-sm text-on-surface-variant transition hover:text-primary-container"
            >
              {{ item.name }}
            </NuxtLink>
          </li>
        </ul>
      </nav>

      <!-- Contact -->
      <section>
        <h3
          class="mb-5 text-sm font-bold uppercase tracking-wider text-on-surface"
        >
          Liên hệ
        </h3>

        <ul class="space-y-4 text-sm text-on-surface-variant">
          <li class="flex items-center gap-3">
            <span class="material-symbols-outlined text-lg">
              call
            </span>

            1900 1234
          </li>

          <li class="flex items-center gap-3">
            <span class="material-symbols-outlined text-lg">
              mail
            </span>

            support@cineai.vn
          </li>

          <li class="flex items-start gap-3">
            <span class="material-symbols-outlined text-lg">
              location_on
            </span>

            TP. Hồ Chí Minh, Việt Nam
          </li>
        </ul>

        <!-- Social -->

        <div class="mt-8 flex gap-4">
          <a
            v-for="social in socialLinks"
            :key="social.name"
            :href="social.href"
            target="_blank"
            rel="noopener noreferrer"
            class="flex h-11 w-11 items-center justify-center rounded-full border border-glass-stroke bg-surface-container hover:bg-primary-container hover:text-on-primary-container transition-all duration-300 hover:scale-110"
          >
            <span class="material-symbols-outlined">
              {{ social.icon }}
            </span>
          </a>
        </div>
      </section>
    </div>

    <!-- Bottom -->

    <div
      class="border-t border-glass-stroke py-6 text-center text-sm text-on-surface-variant"
    >
      © {{ currentYear }}

      <span class="font-semibold text-primary-container">
        CineAI
      </span>

      • All Rights Reserved.

      <div class="mt-2 text-xs opacity-70">
        Designed & Developed with Nuxt 3 · Vue 3 · TailwindCSS
      </div>
    </div>
  </footer>
</template>
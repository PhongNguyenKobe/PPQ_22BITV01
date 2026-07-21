<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useMoviesStore } from '~/store/movies'
import ProductList from '~/components/ProductList.vue'

definePageMeta({
  layout: 'default'
})

const moviesStore = useMoviesStore()
const { movies } = storeToRefs(moviesStore)

await moviesStore.fetchMovies()

const highlights = [
  {
    icon: 'chair',
    title: 'Đặt vé trực quan',
    description:
      'Chọn ghế ngồi thông minh theo thời gian thực tại các chi nhánh với độ chính xác cao.'
  },
  {
    icon: 'smart_toy',
    title: 'Trợ lý ảo AI',
    description:
      'Tìm kiếm bằng ngôn ngữ tự nhiên, gợi ý phim cá nhân hóa theo gu điện ảnh.'
  },
  {
    icon: 'payments',
    title: 'Thanh toán đa kênh',
    description:
      'Hỗ trợ Momo, VNPAY, thẻ ngân hàng quét mã QR an toàn.'
  },
  {
    icon: 'qr_code',
    title: 'Vé điện tử',
    description:
      'Lưu trữ vé số hóa và check-in bằng QR Code.'
  }
]
</script>

<template>
  <div>
    <!-- Hero Section -->
    <header class="relative w-full min-h-[85vh] flex items-center pt-8 overflow-hidden">
      <!-- Background Backdrop with Unsplash image -->
      <div class="absolute inset-0 z-0">
        <div class="w-full h-full bg-[url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat"></div>
        <div class="absolute inset-0 bg-background/85 backdrop-blur-[2px]"></div>
        <div class="absolute inset-0 gradient-fade-bottom"></div>
      </div>

      <div class="relative z-10 w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-16">
        <div class="max-w-4xl relative">
          <!-- Ambient glowing background shapes -->
          <div class="absolute -top-24 -left-24 w-96 h-96 bg-primary-container/10 rounded-full blur-[120px] animate-pulse pointer-events-none z-0"></div>
          <div class="absolute top-1/2 -right-48 w-64 h-64 bg-secondary-container/15 rounded-full blur-[100px] pointer-events-none z-0"></div>

          <div class="relative z-10">
            <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-container/10 border border-primary-container/20 mb-8 backdrop-blur-xl">
              <span class="material-symbols-outlined text-primary-container text-[20px] animate-pulse">psychology</span>
              <span class="text-[11px] font-bold tracking-wider uppercase text-primary-container">Trí tuệ điện ảnh thế hệ mới</span>
            </div>

            <h1 class="font-headline-xl text-[40px] leading-[48px] md:text-[68px] md:leading-[76px] font-bold mb-6 text-on-surface tracking-tight">
              Đặt vé xem phim <br />thông minh với
              <span class="relative inline-block ml-2">
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-[#ffb4aa] drop-shadow-[0_0_15px_rgba(229,9,20,0.6)]">AI</span>
                <span class="absolute -inset-1 bg-primary-container/20 blur-xl rounded-full"></span>
              </span>
            </h1>

            <p class="font-body-lg text-body-lg text-on-surface-variant mb-10 max-w-2xl leading-relaxed">
              Trải nghiệm tương lai của điện ảnh cùng CineAI. Tìm kiếm lịch chiếu, đặt ghế thông minh và nhận đề xuất các tác phẩm phim phù hợp với gu cá nhân chỉ trong nháy mắt.
            </p>

            <div class="flex flex-col sm:flex-row gap-4">
              <NuxtLink to="/movies" class="group relative bg-primary-container text-on-primary-container font-label-md text-label-md px-10 py-4.5 rounded-xl flex items-center justify-center gap-3 red-glow-hover transition-all duration-300 overflow-hidden">
                <span class="relative z-10">Đặt Vé Ngay</span>
                <span class="material-symbols-outlined text-[20px] relative z-10 group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </NuxtLink>
              <NuxtLink to="/movies" class="group bg-surface-container/40 backdrop-blur-md text-on-surface border border-white/10 font-label-md text-label-md px-10 py-4.5 rounded-xl flex items-center justify-center gap-3 hover:bg-white/10 hover:border-primary-container/50 transition-all duration-300">
                <span class="material-symbols-outlined text-[20px] text-secondary group-hover:rotate-12 transition-transform">smart_toy</span>
                Khám Phá Phim AI
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Highlights Benefits Section -->
    <section class="py-16 bg-surface-container-lowest/40 relative">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
        <div class="text-center mb-16 max-w-2xl mx-auto">
          <span class="text-xs font-bold text-secondary uppercase tracking-widest block mb-2">Đặc Quyền CineAI</span>
          <h2 class="font-headline-lg text-3xl font-bold text-on-surface">Công Nghệ Cho Trải Nghiệm Đỉnh Cao</h2>
          <p class="text-sm text-on-surface-variant mt-3">Chúng tôi mang lại giải pháp toàn diện giúp đơn giản hóa mọi điểm chạm đặt vé của khách hàng.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="(hl, index) in highlights"
            :key="index"
            class="glass-panel rounded-2xl border border-glass-stroke p-6 hover:border-primary-container/30 transition-all duration-300 flex flex-col"
          >
            <div class="w-12 h-12 rounded-xl bg-surface-container-high border border-glass-stroke flex items-center justify-center text-primary-container mb-6">
              <span class="material-symbols-outlined text-[28px]">{{ hl.icon }}</span>
            </div>
            <h3 class="font-bold text-lg text-on-surface mb-2">{{ hl.title }}</h3>
            <p class="text-xs text-on-surface-variant leading-relaxed">{{ hl.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Movie Catalog Spotlight -->
    <section class="py-16">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
        <div class="flex items-center justify-between mb-12">
          <div>
            <h2 class="font-headline-lg text-2xl md:text-3xl text-on-surface font-bold">Phim Đang Chiếu Nổi Bật</h2>
            <p class="text-sm text-on-surface-variant mt-1">Danh sách các bộ phim bom tấn không thể bỏ qua tại các cụm rạp CineAI.</p>
          </div>
          <NuxtLink to="/movies" class="text-sm font-bold text-primary hover:underline flex items-center gap-1">
            Xem tất cả
            <span class="material-symbols-outlined text-xs">arrow_forward</span>
          </NuxtLink>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          <MovieCard
            v-for="movie in movies.slice(0, 4)"
            :key="movie.id"
            :movie="movie"
          />
        </div>
      </div>
    </section>

    <!-- Products Section -->
    <section class="py-20 bg-surface-container-lowest/40">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">

        <div class="flex items-center justify-between mb-12">

          <div>
            <h2
              class="font-headline-lg text-2xl md:text-3xl font-bold text-on-surface"
            >
              Vé & Combo Nổi Bật
            </h2>

            <p class="text-sm text-on-surface-variant mt-2">
              Vé xem phim, combo bắp nước và các gói thành viên hấp dẫn tại CineAI.
            </p>
          </div>

          <NuxtLink
            to="/products"
            class="text-primary font-semibold hover:underline flex items-center gap-1"
          >
            Xem tất cả

            <span class="material-symbols-outlined">
              arrow_forward
            </span>

          </NuxtLink>

        </div>

        <ProductList />

      </div>
    </section>
  </div>
</template>
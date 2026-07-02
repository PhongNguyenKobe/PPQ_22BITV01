<script setup lang="ts">
import { ref } from 'vue'

definePageMeta({ layout: 'default' })

const selectedTheater = ref('Tất cả rạp')
const selectedMovie = ref('Tất cả phim')
const selectedDay = ref(0)

const theaters = ['Tất cả rạp', 'CineAI Landmark 81', 'CineAI Bitexco Financial', 'CineAI West Lake Hanoi', 'CineAI Đà Nẵng Dragon']
const movieList = ['Tất cả phim', 'Dune: Phần Hai', 'Oppenheimer', 'Mai', 'Kung Fu Panda 4']

const days = [
  { label: 'TH 3', date: 12 },
  { label: 'TH 4', date: 13 },
  { label: 'TH 5', date: 14 },
  { label: 'TH 6', date: 15 },
  { label: 'TH 7', date: 16 },
  { label: 'CN', date: 17 },
  { label: 'TH 2', date: 18 },
]

const aiCards = [
  { badge: 'Trải nghiệm tốt nhất', badgeColor: 'bg-primary-container/10 text-primary-container', match: '98%', movie: 'Dune: Phần Hai', desc: 'Bạn thường xem phim sci-fi vào tối Thứ 3 tại các rạp IMAX.', time: 'Hôm nay, 20:15', theater: 'CineAI Landmark 81' },
  { badge: 'Suất chiếu vắng khách', badgeColor: 'bg-[#8a2be2]/10 text-[#8a2be2]', match: '85%', movie: 'Oppenheimer', desc: 'Dành cho bạn muốn không gian yên tĩnh để cảm thụ tác phẩm dài.', time: 'Hôm nay, 14:30', theater: 'CineAI Bitexco' },
  { badge: 'Ưu đãi thành viên', badgeColor: 'bg-green-500/10 text-green-500', match: '92%', movie: 'Mai', desc: 'Thành viên Diamond được giảm 30% giá vé cho suất chiếu này.', time: 'Hôm nay, 19:45', theater: 'CineAI West Lake' },
]
</script>

<template>
  <div class="min-h-screen pt-20">
    <!-- Hero Filter -->
    <section class="relative pt-12 pb-8 px-6 md:px-margin-desktop bg-gradient-to-b from-surface-container-lowest to-surface">
      <div class="max-w-container-max mx-auto">
        <h1 class="font-headline-xl text-headline-xl mb-10 text-on-surface">Lịch Chiếu</h1>

        <!-- Filters Panel -->
        <div class="flex flex-col md:flex-row items-start md:items-center gap-6 p-6 rounded-2xl mb-8" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
          <!-- Theater Filter -->
          <div class="w-full md:w-1/4">
            <label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1">Chọn Rạp</label>
            <div class="relative">
              <select v-model="selectedTheater" class="w-full bg-surface-container-high border-white/10 text-on-surface rounded-lg py-3 px-4 appearance-none focus:ring-primary-container focus:border-primary-container font-label-md text-label-md cursor-pointer outline-none border border-white/10">
                <option v-for="t in theaters" :key="t">{{ t }}</option>
              </select>
              <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
            </div>
          </div>

          <!-- Movie Filter -->
          <div class="w-full md:w-1/4">
            <label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1">Chọn Phim</label>
            <div class="relative">
              <select v-model="selectedMovie" class="w-full bg-surface-container-high border-white/10 text-on-surface rounded-lg py-3 px-4 appearance-none focus:ring-primary-container focus:border-primary-container font-label-md text-label-md cursor-pointer outline-none border border-white/10">
                <option v-for="m in movieList" :key="m">{{ m }}</option>
              </select>
              <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
            </div>
          </div>

          <!-- Date Timeline -->
          <div class="w-full md:w-2/4">
            <label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1">Chọn Ngày</label>
            <div class="flex gap-3 overflow-x-auto pb-2" style="scrollbar-width:none">
              <button
                v-for="(d, i) in days" :key="i"
                @click="selectedDay = i"
                class="flex-shrink-0 flex flex-col items-center justify-center min-w-[70px] h-[70px] rounded-xl transition-all"
                :class="selectedDay === i ? 'bg-primary-container text-white shadow-[0_0_20px_-5px_rgba(229,9,20,0.3)]' : 'bg-surface-container-high border border-white/5 hover:border-primary-container text-on-surface'"
              >
                <span class="text-label-sm font-label-sm opacity-80">{{ d.label }}</span>
                <span class="text-headline-md font-bold">{{ d.date }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI Recommendations -->
    <section class="px-6 md:px-margin-desktop py-12">
      <div class="max-w-container-max mx-auto">
        <div class="flex items-center gap-3 mb-8">
          <span class="material-symbols-outlined text-primary-container text-[32px]" style="font-variation-settings:'FILL' 1">psychology</span>
          <h2 class="font-headline-lg text-headline-lg text-on-surface">Gợi ý suất chiếu AI</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="c in aiCards" :key="c.movie" class="overflow-hidden rounded-xl" style="position:relative;background:rgba(31,31,31,0.8);border-radius:12px;padding:1px">
            <div class="absolute inset-0 rounded-xl" style="padding:1.5px;background:linear-gradient(45deg,#e50914,#8a2be2,#e50914);background-size:200% 200%;animation:gradient-move 4s linear infinite;-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);-webkit-mask-composite:xor;mask-composite:exclude"></div>
            <div class="p-6 rounded-[11px] flex flex-col justify-between h-full" style="background:#1e2020">
              <div>
                <div class="flex justify-between items-start mb-4">
                  <div :class="c.badgeColor" class="px-3 py-1 rounded-full text-label-sm font-bold uppercase tracking-wider">{{ c.badge }}</div>
                  <span class="text-on-surface-variant text-label-sm">Độ khớp: {{ c.match }}</span>
                </div>
                <h3 class="font-headline-md text-headline-md text-on-surface mb-2">{{ c.movie }}</h3>
                <p class="text-on-surface-variant font-body-md mb-6">{{ c.desc }}</p>
              </div>
              <div class="flex items-center justify-between">
                <div class="flex flex-col">
                  <span class="text-label-sm text-on-surface-variant">{{ c.time }}</span>
                  <span class="text-label-md font-bold text-on-surface">{{ c.theater }}</span>
                </div>
                <NuxtLink to="/checkout/seat" class="bg-primary-container text-on-primary-container p-3 rounded-full hover:scale-110 transition-transform">
                  <span class="material-symbols-outlined">confirmation_number</span>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Theater Showtimes List -->
    <section class="px-6 md:px-margin-desktop py-12 pb-24">
      <div class="max-w-container-max mx-auto">
        <div class="flex justify-between items-end mb-10 border-b border-white/10 pb-4">
          <h2 class="font-headline-lg text-headline-lg text-on-surface">Danh Sách Rạp & Suất Chiếu</h2>
          <button class="flex items-center gap-2 text-label-md font-label-md text-primary-container hover:underline">
            <span class="material-symbols-outlined text-[18px]">near_me</span>
            Rạp gần nhất
          </button>
        </div>

        <div class="space-y-12">
          <!-- Theater Block -->
          <div class="flex flex-col lg:flex-row gap-8">
            <div class="lg:w-1/3">
              <div class="sticky top-24">
                <h3 class="font-headline-md text-headline-md text-on-surface mb-2">CineAI Landmark 81</h3>
                <p class="text-on-surface-variant text-body-md mb-4">Tầng B1, Vincom Landmark 81, 720A Điện Biên Phủ, P.22, Q. Bình Thạnh, TP.HCM</p>
                <div class="flex gap-3">
                  <span class="px-3 py-1 bg-surface-container-high rounded-full text-label-sm font-label-sm border border-white/5">IMAX Laser</span>
                  <span class="px-3 py-1 bg-surface-container-high rounded-full text-label-sm font-label-sm border border-white/5">Dolby Atmos</span>
                </div>
              </div>
            </div>
            <div class="lg:w-2/3 space-y-8">
              <div class="p-6 rounded-2xl flex flex-col sm:flex-row gap-6" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
                <div class="w-full sm:w-24 h-36 flex-shrink-0 overflow-hidden rounded-lg bg-surface-container-high">
                  <img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA2DxRn9LX5nB6WnIAOYW9DKmmhcE6uElKuus5BETh5P_NWANMiCRx-rqmtYAxDlmZvgAlW0rr9mR3clYlocTp4sgJWWIFgiY8Egy-m9kjSdQzQefnKidmumxbH1SC9yMkJ1A1PxXkTbfQcwOPI6m6ANsupHZwga1EHmOkHe7PIiC0nuS1GtSiJXzpIxoy3xwRd24xogsNOCN8BrGsfp3cR-pSosZ4x8r2iKZc9n-CLepGxXjH2dYfNoob6raeE_deBtuqFCMduTY5Z" alt="Dune" />
                </div>
                <div class="flex-grow">
                  <h4 class="font-headline-md text-headline-md text-on-surface mb-4">Dune: Phần Hai (T13)</h4>
                  <div class="space-y-4">
                    <div>
                      <p class="text-label-sm font-label-sm text-primary-container mb-3 uppercase tracking-tighter font-bold">IMAX 2D - Phụ Đề</p>
                      <div class="flex flex-wrap gap-3">
                        <NuxtLink to="/checkout/seat" class="px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 hover:border-primary-container hover:bg-primary-container/10 transition-all font-label-md text-label-md text-on-surface">19:30</NuxtLink>
                        <NuxtLink to="/checkout/seat" class="px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 hover:border-primary-container hover:bg-primary-container/10 transition-all font-label-md text-label-md text-on-surface">22:15</NuxtLink>
                      </div>
                    </div>
                    <div>
                      <p class="text-label-sm font-label-sm text-on-surface-variant mb-3 uppercase tracking-tighter">2D - Phụ Đề</p>
                      <div class="flex flex-wrap gap-3">
                        <NuxtLink to="/checkout/seat" class="px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 hover:border-primary-container hover:bg-primary-container/10 transition-all font-label-md text-label-md text-on-surface">18:00</NuxtLink>
                        <span class="px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 font-label-md text-label-md text-on-surface-variant opacity-50 cursor-not-allowed">21:00 (Hết vé)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
@keyframes gradient-move {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
</style>
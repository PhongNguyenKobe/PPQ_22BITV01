<script setup lang="ts">
import { ref } from 'vue'

definePageMeta({ layout: 'default' })

const selectedChain = ref('Tất cả chuỗi rạp')
const activeCinema = ref(0)

const chains = ['Tất cả chuỗi rạp', 'CGV Cinemas', 'Galaxy Cinema', 'Lotte Cinema', 'BHD Star Cineplex', 'Beta Cinemas']

const cinemaList = [
  { name: 'CGV Vincom Đồng Khởi', address: 'Tầng 3, Vincom Center B, 72 Lê Thánh Tôn, Q.1', distance: '0.8 km', rating: '4.8', reviews: '2.1k', status: 'Mở cửa' },
  { name: 'CGV Aeon Bình Tân', address: 'Số 1 Đường Số 17A, Khu phố 11, Bình Tân', distance: '5.2 km', rating: '4.5', reviews: '1.5k', status: 'Mở cửa' },
  { name: 'CGV Landmark 81', address: 'B1 Vincom Center Landmark 81, Bình Thạnh', distance: '3.1 km', rating: '4.9', reviews: '3.2k', status: 'Mở cửa' },
  { name: 'CGV Crescent Mall', address: 'Lầu 5, Crescent Mall, Q.7', distance: '6.7 km', rating: '4.7', reviews: '1.8k', status: 'Mở cửa' },
  { name: 'CGV Vivo City', address: 'Lầu 5, SC VivoCity, 1058 Nguyễn Văn Linh, Q.7', distance: '7.2 km', rating: '4.6', reviews: '1.2k', status: 'Mở cửa' },
]

const movieGrid = [
  { name: 'Neural Breach', genre: 'Hành động, Viễn tưởng - 124 ph', rating: 'T16', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB5MLLqulnK8Oj5wJ2HAQV6DbvVtSweCD5FKG110-UWQkANqW-99hDHi_vktcnEFrh5ZfSEDFZrM1QYiVS1Uks3MkNGyFJQNylExj0dE2WOKciVgMIA7_x99ckjcFRg4VX639s5lO1ylETkGDzA2VlwbZOW9Pou1ilbSFJWGL9Ifn5SMmIjjqo0PkM270uAav0vFdlZ8i2K9dm1QcurSy-cK2X7A8E4zet_xAZNmeYfCUuNoWmEeBW3vFkJosF71Mtqm698I8LLUKFv' },
  { name: 'Echoes of Eden', genre: 'Phiêu lưu, Kỳ ảo - 142 ph', rating: 'P', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB5uxjgTkJfkk1Ny9uwjY1w8giBjHS5RRYy2dFvd_kzLnYY0TANQCGD6QJv3BApG4OJt2dcZzqZ2MH8_LGD2kan7q3BO8SfqedxGwtSiQTE35Mdo9fDklFpDdlasbR4_WBywjgh7tRhrY__K6d55TJATtzy0lJCkNxvGHXfsnRPSFtKTAVygIL-t08xQugu11-3ACIPZa1cxzLxx_M8yFLlEDFTiVnd0g_-lghtdbOUQVhTWGriV3993SUeXBXpwqhRPXol9TZwAbK6' },
  { name: 'The Void Project', genre: 'Kinh dị, Bí ẩn - 98 ph', rating: 'T18', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD-QStG-CpQUnc-FJ7TE-nJe_3BKqDEeiJYJ8Zb7a22kZ7Dufx2F7Bf1qFlmnjXxj4a_zyPpK8n6JN06GzZ4WAmDO83A23Og1P0G_VSQVcc7OSlQArJcRCcr_s5xrZ6E0mfsD1FPLISVHrCX8yF4_CrE84FfHEPdzS_DJWLmTUAH_8Ta-Ga8JRbnsYJxdjJ66lXQ7kFY6secJVtr8d0OaC1VN0-R7lzNFrO4ESrH53UhHvX16g6R4FtV1hwulp6TRTgm6zEdaJdZbhU' },
  { name: 'Midnight Strings', genre: 'Lãng mạn, Âm nhạc - 115 ph', rating: 'T13', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAgoEnJkBVQIW0xHvbvChQiMfsHWVBU1AIH8IgBRj0GpOPVIEgpFcdAElDz5CP67U04y2XXr-bKitzrt2WQRAeJ6GnORKOfOArR9bh-PLKTIb1cKCr4ev0zayyffz8uJEVmthrqFxA_VDdMoPzLcZ2fdYZQ4c9xyTXzYwicZfLYveJYLSBshlYFYdQ' },
]
</script>

<template>
  <div class="min-h-screen pt-20">
    <!-- Hero -->
    <section class="w-full px-6 md:px-margin-desktop py-12 bg-gradient-to-b from-surface-container-low to-background">
      <div class="max-w-container-max mx-auto">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
          <div>
            <h1 class="font-headline-xl text-headline-xl mb-2 text-on-surface">Hệ Thống Rạp</h1>
            <p class="text-on-surface-variant font-body-lg text-body-lg">Tìm kiếm rạp chiếu phim CineAI gần bạn nhất với công nghệ trải nghiệm tương lai.</p>
          </div>
          <div class="flex flex-col gap-3">
            <label class="font-label-md text-label-md text-primary-container ml-1">Chọn chuỗi rạp</label>
            <div class="relative min-w-[280px]">
              <select v-model="selectedChain" class="w-full bg-surface-container border border-white/10 rounded-xl px-4 py-3 text-on-surface appearance-none focus:border-primary-container focus:ring-0 cursor-pointer outline-none">
                <option v-for="c in chains" :key="c">{{ c }}</option>
              </select>
              <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <section class="px-6 md:px-margin-desktop pb-24">
      <div class="max-w-container-max mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Sidebar -->
        <aside class="lg:col-span-4 flex flex-col gap-4">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-headline-md text-headline-md text-on-surface">Chi nhánh ({{ cinemaList.length }})</h3>
            <button class="text-primary-container flex items-center gap-1 font-label-sm text-label-sm hover:underline">
              <span class="material-symbols-outlined text-[18px]">location_on</span> Gần tôi nhất
            </button>
          </div>
          <div class="rounded-2xl overflow-hidden" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1);max-height:600px;overflow-y:auto">
            <div
              v-for="(cinema, i) in cinemaList" :key="i"
              @click="activeCinema = i"
              class="p-5 border-b border-white/5 cursor-pointer hover:bg-white/5 transition-all"
              :class="activeCinema === i ? 'border-l-4 border-l-primary-container bg-primary-container/5' : ''"
            >
              <div class="flex justify-between items-start mb-1">
                <h4 class="font-headline-md text-[16px] text-on-surface">{{ cinema.name }}</h4>
                <span class="bg-primary-container/20 text-primary-container text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">{{ cinema.status }}</span>
              </div>
              <p class="text-on-surface-variant text-label-md mb-3 truncate">{{ cinema.address }}</p>
              <div class="flex items-center gap-4 text-on-surface-variant text-label-sm">
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">distance</span> {{ cinema.distance }}</span>
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">stars</span> {{ cinema.rating }} ({{ cinema.reviews }} đánh giá)</span>
              </div>
            </div>
          </div>
        </aside>

        <!-- Detail -->
        <div class="lg:col-span-8 flex flex-col gap-6">
          <!-- Cinema Header -->
          <div class="rounded-3xl overflow-hidden" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
            <div class="h-64 w-full relative">
              <img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBsxpm-_EKZxL5GSj0I6E4HsmRq4e0n81zJ5l6suZ5a4BnxdZcMRpEbSEATKmxS4YXVSTb_tGvr6eaFydsNWZDtOCPa1ADc0JM8dnjYpvYyoBwgLpjPHeRCDnowXFA5IOSshiHdnutAbIONd2FjMZdn7mV8Bzc_qX3w_VGtpVi9ERUSugQjUwyOjlWqBE7X1vcJA-exhK1gl8Gc27j9n9KPqo0YVlhWcES-RJZU6xlzxT4yAxwaWSJrhHXjAhIF8gjCuo1okyEyu-Mw" alt="Cinema" />
              <div class="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent"></div>
              <div class="absolute bottom-6 left-8 right-8 flex justify-between items-end">
                <div>
                  <h2 class="font-headline-xl text-headline-xl text-white drop-shadow-lg">{{ cinemaList[activeCinema].name }}</h2>
                  <div class="flex items-center gap-3 mt-2">
                    <span class="bg-primary-container px-3 py-1 rounded text-white font-bold text-label-sm">IMAX</span>
                    <span class="px-3 py-1 rounded text-white font-bold text-label-sm border" style="background:rgba(138,43,226,0.3);border-color:rgba(138,43,226,0.5)">4DX + AI ENHANCED</span>
                  </div>
                </div>
                <div class="flex gap-2">
                  <button class="p-3 rounded-full transition-colors border" style="background:rgba(255,255,255,0.1);backdrop-filter:blur(8px);border-color:rgba(255,255,255,0.1)">
                    <span class="material-symbols-outlined">share</span>
                  </button>
                  <button class="p-3 rounded-full transition-colors border" style="background:rgba(255,255,255,0.1);backdrop-filter:blur(8px);border-color:rgba(255,255,255,0.1)">
                    <span class="material-symbols-outlined">favorite</span>
                  </button>
                </div>
              </div>
            </div>
            <div class="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="space-y-4">
                <div>
                  <h5 class="text-on-surface-variant font-label-md text-label-md uppercase tracking-widest mb-1">Địa chỉ</h5>
                  <p class="font-body-lg text-body-lg text-on-surface">{{ cinemaList[activeCinema].address }}</p>
                </div>
                <div class="flex gap-4">
                  <button class="flex-1 bg-white/5 hover:bg-white/10 border border-white/10 py-3 rounded-xl flex items-center justify-center gap-2 transition-all text-on-surface">
                    <span class="material-symbols-outlined">call</span> Gọi rạp
                  </button>
                  <button class="flex-1 bg-white/5 hover:bg-white/10 border border-white/10 py-3 rounded-xl flex items-center justify-center gap-2 transition-all text-on-surface">
                    <span class="material-symbols-outlined">directions</span> Chỉ đường
                  </button>
                </div>
              </div>
              <div class="rounded-2xl overflow-hidden h-40 border border-white/10 opacity-80 hover:opacity-100 transition-all duration-500" style="filter:grayscale(0.5) contrast(1.2)">
                <div class="w-full h-full bg-surface-container-high flex items-center justify-center relative">
                  <div class="w-8 h-8 bg-primary-container rounded-full animate-ping absolute"></div>
                  <span class="material-symbols-outlined text-primary-container text-4xl relative z-10" style="font-variation-settings:'FILL' 1">location_on</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Movies at this cinema -->
          <div>
            <div class="flex items-center justify-between mb-6">
              <h3 class="font-headline-md text-headline-md text-on-surface">Phim đang chiếu</h3>
              <div class="flex items-center gap-4">
                <button class="text-on-surface-variant font-label-md text-label-md pb-1 border-b-2 border-primary-container text-primary-container">Hôm nay</button>
                <button class="text-on-surface-variant font-label-md text-label-md pb-1 hover:text-on-surface transition-colors">Ngày mai</button>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div
                v-for="m in movieGrid" :key="m.name"
                class="rounded-2xl p-4 flex gap-4 hover:border-primary-container/50 transition-all group"
                style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)"
              >
                <div class="w-24 h-36 rounded-lg overflow-hidden shrink-0">
                  <img class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" :src="m.img" :alt="m.name" />
                </div>
                <div class="flex flex-col justify-between py-1 flex-1">
                  <div>
                    <h4 class="font-headline-md text-[16px] leading-tight mb-1 group-hover:text-primary-container transition-colors text-on-surface">{{ m.name }}</h4>
                    <p class="text-on-surface-variant text-label-sm">{{ m.genre }}</p>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-primary-container font-bold text-label-md">{{ m.rating }}</span>
                    <NuxtLink to="/showtimes" class="bg-primary-container/10 hover:bg-primary-container text-primary-container hover:text-white px-4 py-2 rounded-lg font-label-md text-label-md transition-all">Xem lịch chiếu</NuxtLink>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI CTA -->
          <div class="rounded-3xl p-8 flex flex-col md:flex-row items-center gap-8 relative overflow-hidden" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
            <div class="relative z-10 flex-1">
              <h3 class="font-headline-lg text-headline-lg mb-4 text-on-surface">Trợ lý CineAI giúp bạn chọn phim?</h3>
              <p class="text-on-surface-variant font-body-md text-body-md mb-6">Bạn đang ở rạp nhưng chưa biết xem phim gì? Hãy để trí tuệ nhân tạo của chúng tôi gợi ý phim phù hợp.</p>
              <NuxtLink to="/ai-discovery" class="bg-[#8a2be2] text-white px-8 py-3 rounded-full font-bold hover:scale-105 transition-all flex items-center gap-2 group w-fit">
                <span class="material-symbols-outlined">auto_awesome</span> Khám phá ngay
                <span class="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </NuxtLink>
            </div>
            <div class="w-48 h-48 relative z-10 hidden md:block">
              <div class="w-full h-full rounded-full opacity-30 animate-pulse" style="background:linear-gradient(to top right,#e50914,#8a2be2);filter:blur(48px)"></div>
              <span class="material-symbols-outlined text-[120px] text-[#8a2be2] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" style="font-variation-settings:'FILL' 1">neurology</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
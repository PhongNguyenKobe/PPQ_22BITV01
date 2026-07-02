<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMoviesStore } from '~/store/movies'
import { storeToRefs } from 'pinia'

definePageMeta({ layout: 'default' })

const moviesStore = useMoviesStore()
const { movies } = storeToRefs(moviesStore)

const searchInput = ref('')
const selectedGenre = ref('Tất cả phim')
const activeSort = ref('Độ phù hợp AI')

const genres = ['Tất cả phim', 'Hành Động', 'Viễn Tưởng', 'Tâm Lý', 'Kịch Tính', 'Cyberpunk', 'Neon-Noir', 'Phim Tài Liệu']
const sorts = ['Độ phù hợp AI', 'Ngày Phát Hành', 'Phổ Biến']

const suggestions = [
  'Phim viễn tưởng vũ trụ hoành tráng',
  'Hành động kịch tính nghẹt thở',
  'Cyberpunk neon đen tối mới nhất',
  'Phim của đạo diễn Christopher Nolan'
]

const aiMovies = [
  { title: 'Techno-Dystopia: Tín Hiệu Cuối', genre: 'Viễn Tưởng', score: '98%', badge: 'AI Lựa Chọn Hàng Đầu', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuApX8V3ac0arkT6yk4kzv8Yw7ILjPdcDl879XQvy3C9I2bt0qO4ksMSkGKyM4yQnmcCtTvEX1oDLfr1O2aZnTYg3wQ9VBnBBnl4KLMfkg0R_LqPzSH-YxlvxiLSyXrVFUTbbKBCS2gWfT2o7SGmREu5rzFkfKAPJc6ZqlgQ1-ZjWchKP5pRsXzqGX90XfLy7FPQicSCMja312CH216FNHMpZ61TdiwsL7akjZZ-CGT-4de7l6oc9iVO8UoAQCJHsjIOzD_ki3m0VQHU' },
  { title: 'Tiếng Vang Của Thuật Toán', genre: 'Tâm Lý', score: '95%', badge: 'Tuyệt Tác', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDBKGmSMrGByy2OJMqN0m9EMoxzjyatedzRHy4_2jzbNm103d-rNfYmTRIsK9aCUl6vDhdxoxHJ8r4ebmTn9qw5frwtVPSDwa0ZzGwJtryO-Ai17TtL9_vmfCsXTtJaRkG5b1A_94BaAd2MZwoXRgfKSH0qKUMJrDO8-DcSjqd7vcOE44R6GmmUzhQRfcZJ_ldfXW4Xz2oZCT-J5MrMjI9WZO2HrXUZmgEW-k6a5Qu_KJGqP4FgU4AGiG7x8CGJWtcWx0FFmUMOKUn7' },
]

const movieGrid = [
  { title: 'Giấc Mơ Robot', genre: 'Viễn Tưởng', rating: '8.9', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAIzDZyiO4JqUEg_LDomlwA8haE6bBgMLvOdO2ZRHCvG-oBi841ymz-C4vv7lEiHWaVmWXDbOpdb-IgAVOtUH7vlK70p2ZQqzrXOKn6rjL3n8gobVlVpLNvG1rbUqGd_iGTA1fSJfbeTeWNAQ3LXP2uFuC6oXp78nqR4fu9g_jnAOvHpz8Cv1gUZQ5-HGv3SntcXdHwwFNcu_pqjLzzpe3hoXP9K7liTJ7p_zW6rnF9aZJ8y0wMljdK0cGR2Ph-tQPBWoEFyvYcIq9G' },
  { title: 'Thành Phố Neo', genre: 'Cyberpunk', rating: '9.1', img: 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=800&auto=format&fit=crop' },
  { title: 'Đường Hậu Toàn', genre: 'Hành Động', rating: '8.5', img: 'https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=800&auto=format&fit=crop' },
  { title: 'Người Đỏ Bất Bại', genre: 'Viễn Tưởng', rating: '7.8', img: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=800&auto=format&fit=crop' },
  { title: 'Biến Cố 2099', genre: 'Viễn Tưởng', rating: '8.2', img: 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=800&auto=format&fit=crop' },
]

async function triggerSearch() {
  if (searchInput.value.trim()) {
    moviesStore.searchMovies(searchInput.value)
  }
}
</script>

<template>
  <div class="min-h-screen pt-20">
    <!-- Hero Search -->
    <section class="relative h-[400px] flex items-center overflow-hidden">
      <div class="absolute inset-0 z-0">
        <div class="w-full h-full bg-[url('https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center"></div>
        <div class="absolute inset-0" style="background:rgba(18,20,20,0.8)"></div>
        <div class="absolute inset-0" style="background:linear-gradient(to top,rgba(18,20,20,1) 0%,rgba(18,20,20,0) 100%)"></div>
      </div>
      <div class="relative z-10 max-w-container-max mx-auto px-6 md:px-margin-desktop w-full text-center">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6" style="background:rgba(229,9,20,0.1);border:1px solid rgba(229,9,20,0.2)">
          <span class="material-symbols-outlined text-primary-container text-[20px] animate-pulse">psychology</span>
          <span class="text-label-sm font-bold tracking-wider uppercase text-primary-container">Khám Phá AI</span>
        </div>
        <h1 class="font-headline-xl text-headline-xl mb-6 text-on-surface">Trải Nghiệm Trí Tuệ <span class="text-primary-container">Điện Ảnh</span></h1>
        <div class="max-w-2xl mx-auto relative group">
          <div class="absolute -inset-1 rounded-full blur opacity-25 group-hover:opacity-50 transition duration-1000" style="background:linear-gradient(to right,#e50914,#8a2be2)"></div>
          <div class="relative flex items-center rounded-full p-2" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
            <span class="material-symbols-outlined ml-4 text-primary-container" style="font-variation-settings:'FILL' 1">psychology</span>
            <input
              v-model="searchInput"
              @keydown.enter="triggerSearch"
              class="bg-transparent border-none focus:ring-0 w-full text-on-surface px-4 py-3 placeholder:text-on-surface-variant outline-none"
              placeholder="Thử 'Tìm phim trinh thám về AI'..."
              type="text"
            />
            <button @click="triggerSearch" class="bg-primary-container text-on-primary-container px-8 py-3 rounded-full font-bold hover:scale-105 transition-all flex items-center gap-2 shadow-[0_0_20px_-5px_rgba(229,9,20,0.5)]">
              Khám Phá
            </button>
          </div>
        </div>
        <div class="mt-8 flex flex-wrap justify-center gap-3">
          <span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Xu hướng:</span>
          <button v-for="sug in suggestions" :key="sug" @click="searchInput = sug; triggerSearch()" class="px-4 py-1 rounded-full text-on-surface text-label-md hover:bg-white/10 transition-colors" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
            {{ sug }}
          </button>
        </div>
      </div>
    </section>

    <!-- Filter Bar -->
    <section class="py-6 sticky top-20 z-40" style="background:rgba(18,20,20,0.8);backdrop-filter:blur(16px)">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
        <div class="flex items-center gap-4 overflow-x-auto pb-2" style="scrollbar-width:none">
          <button
            v-for="g in genres" :key="g"
            @click="selectedGenre = g"
            class="flex-shrink-0 px-6 py-2 rounded-lg font-label-md text-label-md transition-all"
            :class="selectedGenre === g ? 'bg-primary-container text-on-primary-container' : 'text-on-surface hover:bg-white/10 transition-colors' "
            :style="selectedGenre === g ? '' : 'background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)'"
          >
            {{ g }}
          </button>
          <div class="ml-auto flex items-center gap-2 pl-4 shrink-0">
            <span class="font-label-md text-label-md text-on-surface-variant whitespace-nowrap">Sắp xếp:</span>
            <select v-model="activeSort" class="bg-transparent border border-white/10 rounded-lg text-on-surface font-label-md py-1 px-3 outline-none">
              <option v-for="s in sorts" :key="s">{{ s }}</option>
            </select>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured AI Recommendations -->
    <section class="py-16 bg-surface-container-lowest">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
        <div class="flex items-center justify-between mb-12">
          <div>
            <h2 class="font-headline-lg text-headline-lg text-on-surface flex items-center gap-3">
              <span class="material-symbols-outlined text-primary-container" style="font-variation-settings:'FILL' 1">auto_awesome</span>
              Gợi Ý Cho Bạn
            </h2>
            <p class="text-on-surface-variant mt-2">Tuyển tập được AI lựa chọn dựa trên hồ sơ xem phim của bạn.</p>
          </div>
          <NuxtLink to="/movies" class="text-primary-container font-label-md hover:underline">Xem Tất Cả</NuxtLink>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div v-for="m in aiMovies" :key="m.title" class="group relative rounded-2xl overflow-hidden" style="aspect-ratio:16/9">
            <img :src="m.img" :alt="m.title" class="w-full h-full object-cover" />
            <div class="absolute inset-0 flex flex-col justify-end p-8" style="background:linear-gradient(to top,rgba(18,20,20,0.95) 0%,transparent 100%)">
              <div class="flex items-center gap-2 mb-4">
                <span class="bg-secondary-container text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest">{{ m.badge }}</span>
                <span class="text-white/80 text-sm">{{ m.score }} Tương Thích</span>
              </div>
              <h3 class="font-headline-lg text-headline-lg text-white mb-2">{{ m.title }}</h3>
              <div class="flex items-center gap-4">
                <button class="bg-primary-container text-on-primary-container px-6 py-2 rounded-lg font-bold hover:scale-105 transition-all">Xem Trailer</button>
                <NuxtLink :to="`/movies/1`" class="px-6 py-2 rounded-lg font-bold hover:bg-white/10 transition-colors text-white border border-white/20">Chi Tiết</NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Movie Grid -->
    <section class="py-16">
      <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
        <h2 class="font-headline-lg text-headline-lg text-on-surface mb-12">Khám Phá Phim</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
          <div v-for="m in movieGrid" :key="m.title" class="relative rounded-xl overflow-hidden group hover:scale-105 transition-transform duration-300 cursor-pointer" style="aspect-ratio:2/3">
            <img :src="m.img" :alt="m.title" class="w-full h-full object-cover" />
            <div class="absolute inset-0 flex flex-col justify-end p-4" style="background:linear-gradient(to top,rgba(0,0,0,0.9) 0%,rgba(0,0,0,0.3) 50%,transparent 100%)">
              <div class="flex justify-between items-center mb-2">
                <span class="text-[#8a2be2] text-xs font-bold uppercase">{{ m.genre }}</span>
                <div class="flex items-center gap-1 px-2 py-1 rounded" style="background:rgba(52,53,53,0.9)">
                  <span class="material-symbols-outlined text-[14px] text-primary" style="font-variation-settings:'FILL' 1">star</span>
                  <span class="text-white text-[12px] font-bold">{{ m.rating }}</span>
                </div>
              </div>
              <h4 class="font-headline-md text-[14px] text-white mb-3">{{ m.title }}</h4>
              <NuxtLink to="/checkout/seat" class="w-full bg-primary-container text-on-primary-container py-2 rounded-lg text-label-md font-bold text-center block opacity-0 group-hover:opacity-100 transition-opacity">
                Đặt chỗ
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
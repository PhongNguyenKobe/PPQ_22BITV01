<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useMoviesStore } from '~/store/movies'

definePageMeta({ layout: 'default' })

const moviesStore = useMoviesStore()
const { movies } = storeToRefs(moviesStore)

onMounted(async () => {
  await moviesStore.fetchMovies()
})

const features = [
  { icon: 'chair', title: 'Đặt vé trực tuyến', desc: 'Chọn chỗ ngồi theo thời gian thực tại mọi cụm rạp trên toàn quốc với độ chính xác tuyệt đối.' },
  { icon: 'smart_toy', title: 'Trợ lý AI Chatbot', desc: 'Tìm phim bằng ngôn ngữ tự nhiên, nhận đề xuất cá nhân hóa dựa trên sở thích của bạn.' },
  { icon: 'payments', title: 'Thanh toán đa kênh', desc: 'Hỗ trợ thanh toán nhanh chóng qua Momo, VNPAY, thẻ tín dụng hoặc quét mã QR an toàn.' },
  { icon: 'qr_code', title: 'Quản lý vé điện tử', desc: 'Lưu trữ vé thông minh, quét mã QR tại rạp không cần in giấy, thân thiện với môi trường.' },
]

const promos = [
  { icon: 'loyalty', label: 'Tặng ngay', title: 'Mã giảm giá 20% lần đầu' },
  { icon: 'local_dining', label: 'Đồng giá', title: 'Combo bắp nước 99k' },
]

const chatMessages = [
  { role: 'user', text: 'Tìm phim hành động tối nay ở Quận 7 giá dưới 150k' },
  { role: 'ai', text: 'Chào bạn! Tôi tìm thấy 3 suất chiếu phim John Wick 4 tại CGV SC VivoCity:' },
]
const showtimeButtons = ['19:30', '20:15', '21:00']
</script>

<template>
  <div>
    <!-- Hero Section -->
    <header class="relative w-full min-h-[90vh] flex items-center pt-20">
      <div class="absolute inset-0 z-0">
        <div class="w-full h-full bg-[url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat"></div>
        <div class="absolute inset-0" style="background:rgba(18,20,20,0.8)"></div>
        <div class="absolute inset-0" style="background:linear-gradient(to top,rgba(18,20,20,1) 0%,rgba(18,20,20,0) 100%)"></div>
      </div>

      <div class="relative z-10 w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-24">
        <div class="max-w-4xl relative">
          <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full pointer-events-none z-0 animate-pulse" style="background:rgba(229,9,20,0.1);filter:blur(120px)"></div>
          <div class="absolute top-1/2 -right-48 w-64 h-64 rounded-full pointer-events-none z-0" style="background:rgba(138,43,226,0.1);filter:blur(100px)"></div>

          <div class="relative z-10">
            <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-8" style="background:rgba(229,9,20,0.1);border:1px solid rgba(229,9,20,0.2);backdrop-filter:blur(16px)">
              <span class="material-symbols-outlined text-primary-container text-[20px] animate-pulse">psychology</span>
              <span class="text-label-md font-bold tracking-wider uppercase text-primary-container">Trí tuệ điện ảnh thế hệ mới</span>
            </div>

            <h1 class="font-headline-xl md:text-[72px] md:leading-[80px] font-bold mb-8 text-on-surface tracking-tight">
              Đặt vé xem phim <br />thông minh với
              <span class="relative inline-block ml-2">
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-[#ffb4aa]" style="filter:drop-shadow(0 0 15px rgba(229,9,20,0.6))">AI</span>
                <span class="absolute -inset-1 rounded-full" style="background:rgba(229,9,20,0.2);filter:blur(16px)"></span>
              </span>
            </h1>

            <p class="font-body-lg text-body-lg text-on-surface-variant mb-12 max-w-2xl leading-relaxed">
              Trải nghiệm tương lai của điện ảnh. Tìm kiếm, khám phá và đặt vé chỉ trong vài giây với trợ lý AI thông minh của CineAI.
            </p>

            <div class="flex flex-col sm:flex-row gap-6">
              <NuxtLink to="/movies" class="group relative bg-primary-container text-on-primary-container font-label-md text-label-md px-10 py-5 rounded-xl flex items-center justify-center gap-3 transition-all duration-300 overflow-hidden" style="box-shadow:0 0 25px -2px rgba(229,9,20,0.3)">
                <div class="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                <span class="relative z-10">Đặt vé ngay</span>
                <span class="material-symbols-outlined text-[22px] relative z-10 group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </NuxtLink>
              <NuxtLink to="/ai-discovery" class="group bg-surface-container/40 backdrop-blur-md text-on-surface border border-white/10 font-label-md text-label-md px-10 py-5 rounded-xl flex items-center justify-center gap-3 hover:bg-white/10 hover:border-primary-container/50 transition-all duration-300">
                <span class="material-symbols-outlined text-[22px] text-primary-container group-hover:rotate-12 transition-transform">smart_toy</span>
                Trải nghiệm trợ lý AI
              </NuxtLink>
            </div>

            <div class="mt-16 flex items-center gap-8 opacity-60">
              <div class="flex flex-col">
                <span class="text-headline-md font-bold text-on-surface">500k+</span>
                <span class="text-label-sm text-on-surface-variant uppercase">Người dùng</span>
              </div>
              <div class="w-px h-10 bg-white/10"></div>
              <div class="flex flex-col">
                <span class="text-headline-md font-bold text-on-surface">99.9%</span>
                <span class="text-label-sm text-on-surface-variant uppercase">Chính xác</span>
              </div>
              <div class="w-px h-10 bg-white/10"></div>
              <div class="flex flex-col">
                <span class="text-headline-md font-bold text-on-surface">24/7</span>
                <span class="text-label-sm text-on-surface-variant uppercase">Hỗ trợ AI</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="flex-grow">
      <!-- Phim dang chieu -->
      <section class="w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-24">
        <div class="flex justify-between items-end mb-12">
          <h2 class="font-headline-lg text-headline-lg font-bold text-on-surface">Phim đang chiếu</h2>
          <NuxtLink to="/movies" class="hidden md:flex items-center gap-1 text-primary-container font-label-md text-label-md hover:text-primary transition-colors">
            Xem tất cả <span class="material-symbols-outlined text-[20px]">chevron_right</span>
          </NuxtLink>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <article v-for="movie in movies.slice(0,4)" :key="movie.id" class="group relative rounded-xl overflow-hidden bg-surface-container hover:scale-[1.02] transition-transform duration-300">
            <div class="aspect-[2/3] w-full bg-surface-variant relative overflow-hidden">
              <img v-if="movie.poster" :src="movie.poster" :alt="movie.title" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full bg-[url('https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1925&auto=format&fit=crop')] bg-cover bg-center"></div>
              <div class="absolute inset-0" style="background:linear-gradient(to top,rgba(18,20,20,1) 0%,rgba(18,20,20,0) 100%)"></div>
              <div class="absolute top-4 left-4">
                <span class="bg-[#1F1F1F] text-on-surface px-3 py-1 rounded-full font-label-sm text-label-sm border border-white/10">{{ movie.format || 'IMAX' }}</span>
              </div>
            </div>
            <div class="absolute bottom-0 w-full p-6 translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
              <div class="flex items-center gap-1 text-primary mb-2">
                <span class="material-symbols-outlined text-[16px]" style="font-variation-settings:'FILL' 1">star</span>
                <span class="font-label-sm text-label-sm text-on-surface font-semibold">{{ movie.rating || '4.8' }}</span>
              </div>
              <h3 class="font-headline-md text-headline-md font-bold text-on-surface mb-4 truncate">{{ movie.title }}</h3>
              <div class="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100">
                <NuxtLink :to="`/movies/${movie.id}`" class="w-full bg-primary-container text-on-primary-container font-label-md text-label-md py-2.5 rounded-lg text-center transition-all" style="box-shadow:0 0 25px -2px rgba(229,9,20,0.3)">Đặt chỗ</NuxtLink>
                <button class="w-full bg-transparent border border-white/20 text-on-surface font-label-md text-label-md py-2.5 rounded-lg hover:bg-white/10 transition-colors">Xem trailer</button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Features -->
      <section class="w-full bg-surface-container-low py-24 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-[500px] h-[500px] pointer-events-none" style="background:rgba(229,9,20,0.05);filter:blur(100px)"></div>
        <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop relative z-10">
          <div class="text-center mb-16">
            <h2 class="font-headline-lg text-headline-lg font-bold text-on-surface mb-4">Công nghệ dẫn đầu trải nghiệm</h2>
            <p class="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mx-auto">Hệ sinh thái thông minh giúp hành trình xem phim của bạn liền mạch từ lúc chọn ghế đến khi vào rạp.</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div v-for="f in features" :key="f.icon" class="p-8 rounded-xl hover:-translate-y-2 transition-transform duration-300" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
              <div class="w-14 h-14 bg-surface-variant rounded-lg flex items-center justify-center mb-6 border border-white/5">
                <span class="material-symbols-outlined text-[28px] text-primary">{{ f.icon }}</span>
              </div>
              <h3 class="font-headline-md text-[20px] leading-tight font-bold text-on-surface mb-3">{{ f.title }}</h3>
              <p class="font-body-md text-body-md text-on-surface-variant">{{ f.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- AI Chatbot Demo -->
      <section class="w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-24">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 class="font-headline-xl text-headline-xl font-bold text-on-surface mb-6">Giao tiếp tự nhiên, <br/>nhận vé tức thì</h2>
            <p class="font-body-lg text-body-lg text-on-surface-variant mb-8">Không cần duyệt qua hàng tá lịch chiếu phức tạp. Chỉ cần nói cho AI của chúng tôi biết bạn muốn xem gì, ở đâu và mức giá mong muốn.</p>
            <ul class="space-y-4 mb-10">
              <li class="flex items-center gap-3 text-on-surface">
                <span class="material-symbols-outlined text-primary">check_circle</span>
                <span class="font-body-md text-body-md">Xử lý ngôn ngữ tự nhiên tiếng Việt chính xác</span>
              </li>
              <li class="flex items-center gap-3 text-on-surface">
                <span class="material-symbols-outlined text-primary">check_circle</span>
                <span class="font-body-md text-body-md">So sánh giá và suất chiếu đa rạp theo thời gian thực</span>
              </li>
              <li class="flex items-center gap-3 text-on-surface">
                <span class="material-symbols-outlined text-primary">check_circle</span>
                <span class="font-body-md text-body-md">Tự động đề xuất combo bắp nước tối ưu</span>
              </li>
            </ul>
            <NuxtLink to="/ai-discovery" class="bg-transparent text-on-surface border-[1.5px] border-white/20 font-label-md text-label-md px-8 py-3 rounded-lg hover:bg-white/10 transition-colors duration-300 inline-block">
              Khám phá tính năng AI
            </NuxtLink>
          </div>
          <div class="relative">
            <div class="absolute -inset-1 rounded-2xl blur opacity-20" style="background:linear-gradient(to right,#e50914,#8a2be2)"></div>
            <div class="relative rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[480px]" style="background:#121212;border:1px solid #1F1F1F">
              <div class="p-4 flex items-center gap-3 border-b border-white/5" style="background:#1F1F1F">
                <div class="w-10 h-10 rounded-full flex items-center justify-center" style="background:rgba(229,9,20,0.2)">
                  <span class="material-symbols-outlined text-primary text-[20px]">smart_toy</span>
                </div>
                <div>
                  <h4 class="font-label-md text-label-md text-on-surface font-bold">Trợ lý CineAI</h4>
                  <span class="font-label-sm text-label-sm text-primary flex items-center gap-1">
                    <span class="w-2 h-2 rounded-full bg-primary inline-block animate-pulse"></span> Trực tuyến
                  </span>
                </div>
              </div>
              <div class="flex-grow p-6 flex flex-col gap-6 overflow-y-auto">
                <div class="flex justify-end">
                  <div class="bg-[#1F1F1F] text-on-surface font-body-md text-body-md p-4 rounded-2xl rounded-tr-sm max-w-[80%] border border-white/5">
                    Tìm phim hành động tối nay ở Quận 7 giá dưới 150k
                  </div>
                </div>
                <div class="flex justify-start items-end gap-2">
                  <div class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mb-1" style="background:rgba(229,9,20,0.2)">
                    <span class="material-symbols-outlined text-primary text-[16px]">smart_toy</span>
                  </div>
                  <div class="text-on-surface font-body-md text-body-md p-4 rounded-2xl rounded-tl-sm max-w-[85%]" style="background:rgba(229,9,20,0.1);border:1px solid rgba(229,9,20,0.2)">
                    Chào bạn! Tôi tìm thấy 3 suất chiếu phim <span class="text-primary font-semibold">'John Wick 4'</span> tại <span class="font-semibold text-on-surface">CGV SC VivoCity</span>:<br/><br/>
                    <div class="flex gap-2 my-2">
                      <span v-for="t in showtimeButtons" :key="t" :class="t==='19:30' ? 'bg-primary-container text-on-primary-container' : 'border border-white/20 text-on-surface'" class="px-3 py-1 rounded font-label-sm text-label-sm font-bold">{{ t }}</span>
                    </div>
                    <br/>Giá vé đang ưu đãi chỉ từ <span class="text-primary font-bold">120k</span>. Bạn có muốn đặt vé ngay không?
                  </div>
                </div>
              </div>
              <div class="p-4 border-t border-white/5 flex gap-3 items-center" style="background:#1F1F1F">
                <div class="flex-grow rounded-full px-4 py-3 flex items-center gap-2 transition-all" style="background:#121212;border:1px solid #2A2A2A">
                  <span class="material-symbols-outlined text-on-surface-variant text-[20px]">mic</span>
                  <span class="text-on-surface-variant font-body-md text-body-md">Đặt vé suất 19:30</span>
                </div>
                <NuxtLink to="/checkout/seat" class="w-12 h-12 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center transition-all flex-shrink-0 hover:scale-105" style="box-shadow:0 0 20px -5px rgba(229,9,20,0.3)">
                  <span class="material-symbols-outlined">send</span>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Promo Banner -->
      <section class="w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-12">
        <div class="border-l-4 border-l-primary-container rounded-r-xl p-8 flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden" style="background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)">
          <div class="absolute top-0 right-0 w-64 h-64 pointer-events-none" style="background:rgba(229,9,20,0.1);filter:blur(48px)"></div>
          <div class="relative z-10 flex-shrink-0">
            <h2 class="font-headline-lg text-headline-md md:text-headline-lg font-bold text-on-surface mb-2">Ưu đãi độc quyền cho thành viên CineAI</h2>
            <p class="font-body-md text-body-md text-on-surface-variant">Đăng ký ngay để nhận những đặc quyền dành riêng cho bạn.</p>
          </div>
          <div class="relative z-10 flex flex-wrap gap-4 w-full md:w-auto justify-start md:justify-end">
            <div v-for="p in promos" :key="p.icon" class="rounded-lg px-6 py-4 flex items-center gap-4" style="background:#121212;border:1px solid rgba(255,255,255,0.1)">
              <div class="w-12 h-12 rounded-full flex items-center justify-center text-primary-container" style="background:rgba(229,9,20,0.2)">
                <span class="material-symbols-outlined">{{ p.icon }}</span>
              </div>
              <div>
                <p class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">{{ p.label }}</p>
                <p class="font-headline-md text-[18px] font-bold text-on-surface">{{ p.title }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Final CTA -->
      <section class="w-full bg-surface-container-low py-24 mt-12 relative overflow-hidden">
        <div class="absolute inset-0 z-0 opacity-20">
          <div class="w-full h-full bg-[url('https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center"></div>
        </div>
        <div class="absolute inset-0 bg-gradient-to-t from-background to-transparent z-0"></div>
        <div class="max-w-4xl mx-auto px-6 text-center relative z-10">
          <h2 class="font-headline-xl text-headline-xl md:text-[56px] md:leading-[64px] font-bold text-on-surface mb-8">Khám phá trải nghiệm đặt vé thông minh ngay hôm nay!</h2>
          <NuxtLink to="/register" class="bg-primary-container text-on-primary-container font-label-md text-label-md px-10 py-5 rounded-lg text-lg inline-flex items-center gap-2 transition-all duration-300 hover:scale-105" style="box-shadow:0 0 25px -2px rgba(229,9,20,0.3)">
            Đăng ký ngay
            <span class="material-symbols-outlined">arrow_forward</span>
          </NuxtLink>
        </div>
      </section>
    </main>
  </div>
</template>
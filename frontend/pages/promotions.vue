<script setup lang="ts">
import { ref, computed } from 'vue'

definePageMeta({
  layout: 'default'
})

interface Promotion {
  id: string
  title: string
  description: string
  category: 'ticket' | 'fnb' | 'partner' | 'member'
  code: string
  discount: string
  validUntil: string
  badge: 'HOT' | 'Sắp hết hạn' | 'Độc quyền App' | 'Đặc quyền VIP'
  imageUrl: string
  terms: string[]
  branches: string[]
}

const activeCategory = ref<'all' | 'ticket' | 'fnb' | 'partner' | 'member'>('all')
const selectedPromo = ref<Promotion | null>(null)

// Toast notification state
const showToast = ref(false)
const toastMessage = ref('')

const categories = [
  { key: 'all', label: 'Tất cả' },
  { key: 'ticket', label: 'Ưu đãi Vé' },
  { key: 'fnb', label: 'Combo Bắp Nước' },
  { key: 'partner', label: 'Đối tác / Ngân hàng' },
  { key: 'member', label: 'Thành viên AI Club' }
]

// Mock Promotions Data
const promotions = ref<Promotion[]>([
  {
    id: 'promo-1',
    title: 'Happy Wednesday - Vé Đồng Giá 45K',
    description: 'Thứ 4 vui vẻ cùng CineAI, đồng giá vé ghế đơn tiêu chuẩn cho tất cả các suất chiếu 2D.',
    category: 'ticket',
    code: 'HAPPYWED45',
    discount: 'Đồng giá 45K',
    validUntil: '31/12/2026',
    badge: 'HOT',
    imageUrl: 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=600&auto=format&fit=crop',
    terms: [
      'Áp dụng vào ngày thứ Tư hàng tuần.',
      'Chỉ áp dụng cho định dạng phòng chiếu 2D thường.',
      'Không giới hạn số lượng đặt vé.',
      'Không áp dụng đồng thời với các chương trình khuyến mãi khác.'
    ],
    branches: ['CineAI Cầu Giấy (HN)', 'CineAI Hà Đông (HN)', 'CineAI Quận 1 (HCM)']
  },
  {
    id: 'promo-2',
    title: 'Thành Viên AI Pass - Trải Nghiệm 0đ',
    description: 'Tặng ngay 1 vé xem phim IMAX miễn phí hàng tháng dành riêng cho hội viên sở hữu thẻ AI Pass.',
    category: 'member',
    code: 'AIPASSFREE',
    discount: '1 Vé IMAX 0đ',
    validUntil: '30/11/2026',
    badge: 'Độc quyền App',
    imageUrl: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=600&auto=format&fit=crop',
    terms: [
      'Áp dụng cho hội viên sở hữu thẻ AI Pass đang kích hoạt.',
      'Mỗi hội viên nhận tối đa 1 vé miễn phí / tháng.',
      'Áp dụng cho cả phòng chiếu IMAX, 3D và 2D.',
      'Cần xác thực tài khoản VIP trên ứng dụng di động CineAI.'
    ],
    branches: ['Tất cả các chi nhánh CineAI trên toàn quốc']
  },
  {
    id: 'promo-3',
    title: 'Combo AI Dual Tiết Kiệm 30%',
    description: 'Ưu đãi bắp nước đôi hoành tráng bao gồm 2 bắp rang phô mai lớn và 4 pepsi cực lạnh.',
    category: 'fnb',
    code: 'AIDUAL30',
    discount: 'Giảm 30% Combo',
    validUntil: '15/10/2026',
    badge: 'Sắp hết hạn',
    imageUrl: 'https://images.unsplash.com/photo-1578849278619-e73505e9610f?q=80&w=600&auto=format&fit=crop',
    terms: [
      'Áp dụng mua trực tiếp tại quầy hoặc đặt trước qua website/app CineAI.',
      'Vui lòng xuất trình mã vạch đơn hàng khi nhận bắp nước.',
      'Hạn đổi quà trùng khớp với thời gian ghi trên vé đã mua.'
    ],
    branches: ['CineAI Cầu Giấy (HN)', 'CineAI Hà Đông (HN)', 'CineAI Quận 1 (HCM)']
  },
  {
    id: 'promo-4',
    title: 'Giảm 50K Khi Thanh Toán Qua VNPAY',
    description: 'Nhập mã giảm giá khi thanh toán mua vé xem phim qua cổng VNPAY-QR trên website/app CineAI.',
    category: 'partner',
    code: 'CINEAIVNPAY',
    discount: 'Giảm ngay 50K',
    validUntil: '31/12/2026',
    badge: 'HOT',
    imageUrl: 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?q=80&w=600&auto=format&fit=crop',
    terms: [
      'Áp dụng cho giao dịch mua vé có giá trị từ 150K trở lên.',
      'Mỗi tài khoản ví/ngân hàng được áp dụng 1 lần / tuần.',
      'Chỉ áp dụng khi thanh toán bằng phương thức quét mã QR VNPAY.'
    ],
    branches: ['Tất cả các chi nhánh CineAI trên toàn quốc']
  },
  {
    id: 'promo-5',
    title: 'Ưu Đãi Học Sinh Sinh Viên - Vé 50K',
    description: 'Đồng giá vé 50K suất chiếu 2D cả tuần dành cho học sinh, sinh viên khi xuất trình thẻ HSSV.',
    category: 'ticket',
    code: 'STUDENT50',
    discount: 'Vé 2D 50K',
    validUntil: '31/12/2026',
    badge: 'Đặc quyền VIP',
    imageUrl: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=600&auto=format&fit=crop',
    terms: [
      'Cần xuất trình thẻ Học sinh - Sinh viên còn hạn hoặc CCCD chứng minh dưới 22 tuổi tại quầy soát vé.',
      'Áp dụng từ Thứ Hai đến Chủ Nhật.',
      'Chỉ áp dụng cho ghế tiêu chuẩn hoặc VIP 2D.'
    ],
    branches: ['CineAI Cầu Giấy (HN)', 'CineAI Hà Đông (HN)', 'CineAI Quận 1 (HCM)']
  },
  {
    id: 'promo-6',
    title: 'Combo Single Bắp Pepsi Chỉ 85K',
    description: 'Thưởng thức phim trọn vẹn với Combo đơn bao gồm 1 bắp rang lớn tự chọn vị và 1 cốc pepsi mát lạnh.',
    category: 'fnb',
    code: 'SINGLE85',
    discount: 'Combo 85K',
    validUntil: '30/09/2026',
    badge: 'Sắp hết hạn',
    imageUrl: 'https://images.unsplash.com/photo-1513151233558-d860c5398176?q=80&w=600&auto=format&fit=crop',
    terms: [
      'Áp dụng mua kèm với vé xem phim bất kỳ.',
      'Hỗ trợ đổi sang vị bắp Caramel hoặc Phô mai không phụ phí.'
    ],
    branches: ['CineAI Cầu Giấy (HN)', 'CineAI Hà Đông (HN)', 'CineAI Quận 1 (HCM)']
  }
])

// Computed
const filteredPromotions = computed(() => {
  if (activeCategory.value === 'all') {
    return promotions.value
  }
  return promotions.value.filter(p => p.category === activeCategory.value)
})

// Category label helper
function getCategoryLabel(category: Promotion['category']) {
  switch (category) {
    case 'ticket':
      return 'Vé Xem Phim'
    case 'fnb':
      return 'Bắp Nước'
    case 'partner':
      return 'Đối Tác Liên Kết'
    case 'member':
      return 'Thành Viên VIP'
    default:
      return 'Ưu Đãi'
  }
}

function copyCode(code: string) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(code)
    toastMessage.value = `Đã sao chép mã ưu đãi "${code}" thành công!`
    showToast.value = true
    setTimeout(() => {
      showToast.value = false
    }, 3000)
  }
}
</script>

<template>
  <div
    class="promotions-page min-h-screen bg-[#0b0c10] text-gray-100 pt-20 pb-24 selection:bg-red-600 selection:text-white relative overflow-hidden">

    <!-- Toast Alert Notification -->
    <transition enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="showToast"
        class="fixed bottom-6 right-6 z-50 bg-[#1e2020] border border-green-500/30 text-green-400 px-5 py-3 rounded-2xl shadow-2xl flex items-center gap-2 backdrop-blur-md">
        <span class="material-symbols-outlined text-sm">check_circle</span>
        <span class="text-xs font-bold">{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- SECTION 1: HERO DEALS BANNER -->
    <section
      class="relative w-full py-16 px-4 sm:px-6 lg:px-8 border-b border-white/5 bg-gradient-to-b from-black/60 to-transparent">
      <div class="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-red-600/10 blur-[130px] pointer-events-none">
      </div>
      <div
        class="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-purple-600/10 blur-[130px] pointer-events-none">
      </div>

      <div class="max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-12 relative z-10">
        <div class="max-w-2xl space-y-4 text-center lg:text-left">
          <span
            class="text-xs font-bold text-red-500 tracking-widest uppercase bg-red-600/10 border border-red-500/20 px-3 py-1 rounded-full">
            CINEAI OFFERS
          </span>
          <h1 class="text-4xl md:text-5xl font-black text-white tracking-tight uppercase leading-none">
            CineAI Deals & Rewards
          </h1>
          <p class="text-xs md:text-sm text-gray-400 font-medium leading-relaxed max-w-xl">
            Săn hàng loạt ưu đãi vé xem phim cực HOT, Combo bắp nước siêu tiết kiệm và các chương trình liên kết ngân
            hàng đặc quyền mỗi ngày.
          </p>
        </div>

        <!-- Highlight Hero Card -->
        <div @click="selectedPromo = promotions[0]"
          class="glass-panel border border-white/10 rounded-3xl p-6 w-full max-w-md cursor-pointer hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(229,9,20,0.2)] transition-all duration-300 group flex gap-4">
          <img :src="promotions[0].imageUrl"
            class="w-24 h-24 object-cover rounded-2xl border border-white/10 group-hover:scale-105 transition-transform" />
          <div class="flex-1 flex flex-col justify-between">
            <div>
              <span class="text-[9px] font-black bg-red-600 text-white px-2 py-0.5 rounded uppercase tracking-wider">
                Mùa lễ hội
              </span>
              <h3
                class="font-bold text-sm text-white mt-1.5 group-hover:text-red-400 transition-colors line-clamp-1 uppercase">
                {{ promotions[0].title }}
              </h3>
              <p class="text-[11px] text-gray-400 mt-1 line-clamp-2 leading-relaxed font-light">
                {{ promotions[0].description }}
              </p>
            </div>
            <div class="text-[10px] text-red-400 font-bold flex items-center gap-1.5 mt-2">
              Xem chi tiết <span class="material-symbols-outlined text-xs">arrow_forward</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 2: FILTER & PROMOTIONS GRID -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-10">

      <!-- Pill Filter Category -->
      <div class="flex items-center gap-2.5 overflow-x-auto pb-4 scrollbar-none border-b border-white/5">
        <button v-for="cat in categories" :key="cat.key" @click="activeCategory = cat.key as any"
          class="flex-shrink-0 px-4 py-2.5 rounded-full text-xs font-bold border transition-all duration-300" :class="activeCategory === cat.key
            ? 'bg-red-600 border-red-500 text-white shadow-[0_0_15px_rgba(229,9,20,0.4)]'
            : 'bg-white/5 border-white/10 text-gray-400 hover:text-white hover:bg-white/10'">
          {{ cat.label }}
        </button>
      </div>

      <!-- Promotions Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="promo in filteredPromotions" :key="promo.id"
          class="glass-panel border border-white/10 rounded-3xl overflow-hidden hover:-translate-y-1 hover:shadow-2xl transition-all duration-300 group flex flex-col justify-between">
          <!-- Thumbnail banner -->
          <div @click="selectedPromo = promo" class="relative aspect-[16/9] w-full overflow-hidden cursor-pointer">
            <img :src="promo.imageUrl" :alt="promo.title"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-transparent to-black/35"></div>

            <span
              class="absolute top-4 left-4 px-2.5 py-0.5 bg-red-600 text-white text-[9px] font-black rounded uppercase tracking-wider">
              {{ promo.badge }}
            </span>

            <span class="absolute bottom-4 left-4 text-[10px] text-gray-300 font-bold flex items-center gap-1">
              <span class="material-symbols-outlined text-xs">schedule</span> Hạn: {{ promo.validUntil }}
            </span>
          </div>

          <!-- Description and Coupon details -->
          <div class="p-6 space-y-4 flex-1 flex flex-col justify-between">
            <div class="space-y-2 cursor-pointer" @click="selectedPromo = promo">
              <span class="text-[10px] font-bold text-red-500 uppercase tracking-widest">
                {{ getCategoryLabel(promo.category) }}
              </span>
              <h3
                class="text-base font-black text-white group-hover:text-red-400 transition-colors uppercase leading-snug line-clamp-1">
                {{ promo.title }}
              </h3>
              <p class="text-xs text-gray-400 font-light leading-relaxed line-clamp-2">{{ promo.description }}</p>
            </div>

            <!-- Coupon discount + Actions -->
            <div class="pt-4 border-t border-white/5 flex items-center justify-between gap-4">
              <div class="min-w-0">
                <span class="text-[9px] font-bold uppercase tracking-wider text-gray-500 block">Ưu đãi</span>
                <span class="text-sm font-black text-white font-mono truncate block">{{ promo.discount }}</span>
              </div>

              <div class="flex items-center gap-2">
                <button @click="copyCode(promo.code)"
                  class="px-3.5 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-xs font-bold text-white transition-all flex items-center gap-1">
                  <span class="material-symbols-outlined text-sm">content_copy</span> Copy
                </button>
                <NuxtLink to="/showtimes"
                  class="px-3.5 py-2 bg-red-600 hover:bg-red-700 rounded-xl text-xs font-bold text-white transition-all shadow-md">
                  Dùng
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 3: PROMOTION DETAIL MODAL POP-UP -->
    <transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0"
      enter-to-class="opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="opacity-100"
      leave-to-class="opacity-0">
      <div v-if="selectedPromo"
        class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div
          class="glass-panel w-full max-w-xl rounded-3xl border border-white/10 p-6 relative overflow-hidden shadow-2xl animate-modal">

          <button @click="selectedPromo = null"
            class="absolute top-4 right-4 w-9 h-9 rounded-xl hover:bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-colors">
            <span class="material-symbols-outlined text-lg">close</span>
          </button>

          <div class="space-y-6">
            <!-- Modal Header -->
            <div class="flex gap-4 items-start pt-2">
              <img :src="selectedPromo.imageUrl"
                class="w-16 h-16 object-cover rounded-xl border border-white/10 flex-shrink-0" />
              <div>
                <span class="text-[9px] font-black bg-red-600 text-white px-2 py-0.5 rounded uppercase tracking-wider">
                  {{ selectedPromo.badge }}
                </span>
                <h3 class="text-lg font-black text-white mt-1.5 uppercase leading-tight">{{ selectedPromo.title }}</h3>
                <span class="text-[10px] text-gray-400 font-bold block mt-1">
                  Khuyến mãi hạn đến: {{ selectedPromo.validUntil }}
                </span>
              </div>
            </div>

            <!-- Modal Content details -->
            <div class="space-y-4 border-t border-white/5 pt-4">
              <div>
                <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Chi tiết chương trình</span>
                <p class="text-xs text-gray-300 leading-relaxed font-light mt-1">{{ selectedPromo.description }}</p>
              </div>

              <!-- Terms and conditions -->
              <div>
                <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                  Điều kiện & Điều khoản sử dụng (T&C)
                </span>
                <ul class="list-disc list-inside text-xs text-gray-400 leading-relaxed font-light mt-2 space-y-1">
                  <li v-for="t in selectedPromo.terms" :key="t">{{ t }}</li>
                </ul>
              </div>

              <!-- Cinemas applicable -->
              <div>
                <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Chi nhánh rạp áp dụng</span>
                <div class="flex flex-wrap gap-1.5 mt-2">
                  <span v-for="b in selectedPromo.branches" :key="b"
                    class="px-2 py-1 bg-white/5 border border-white/10 text-[9px] text-gray-300 rounded font-semibold">
                    {{ b }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Modal Footer Actions -->
            <div class="pt-4 border-t border-white/5 flex items-center justify-between gap-4">
              <div
                class="bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 flex items-center justify-between gap-6 flex-1">
                <span class="text-[10px] text-gray-500 uppercase font-black">Mã Coupon</span>
                <span class="text-sm font-black text-white font-mono tracking-wider">{{ selectedPromo.code }}</span>
              </div>
              <button @click="copyCode(selectedPromo.code)"
                class="px-5 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-xs font-bold text-white transition-all flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">content_copy</span> Sao chép mã
              </button>
              <NuxtLink to="/showtimes" @click="selectedPromo = null"
                class="px-6 py-3 bg-[#E50914] text-white font-black text-xs uppercase rounded-xl transition-all shadow-lg shadow-red-600/30">
                Đặt vé ngay
              </NuxtLink>
            </div>
          </div>

        </div>
      </div>
    </transition>

  </div>
</template>

<style scoped>
.scrollbar-none::-webkit-scrollbar {
  display: none;
}

.scrollbar-none {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

@keyframes modalScale {
  from {
    transform: scale(0.95);
    opacity: 0;
  }

  to {
    transform: scale(1);
    opacity: 1;
  }
}

.animate-modal {
  animation: modalScale 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
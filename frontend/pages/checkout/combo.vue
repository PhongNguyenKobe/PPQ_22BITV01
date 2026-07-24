<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { useMoviesStore } from '~/store/movies'

definePageMeta({
  layout: 'default'
})

const ticketsStore = useTicketsStore()
const moviesStore = useMoviesStore()
const { selectedShowtime, selectedSeats, totalAmount } = storeToRefs(ticketsStore)
const { activeMovie } = storeToRefs(moviesStore)

const combos = ref([
  { id: 'c1', name: 'CGV Combo Solo', price: 85000, desc: '1 Bắp lớn + 1 Nước ngọt lớn', img: 'https://images.unsplash.com/photo-1585647347384-259e51c8651a?q=80&w=300&auto=format&fit=crop', qty: 0 },
  { id: 'c2', name: 'CGV Combo Couple', price: 120000, desc: '1 Bắp siêu lớn + 2 Nước ngọt lớn', img: 'https://images.unsplash.com/photo-1599059813005-11265ba4b4ce?q=80&w=300&auto=format&fit=crop', qty: 0 },
  { id: 'c3', name: 'Snack Khoai Tây', price: 45000, desc: 'Khoai tây chiên giòn tan vị phô mai', img: 'https://images.unsplash.com/photo-1576107025879-ff00ab9c3dd2?q=80&w=300&auto=format&fit=crop', qty: 0 }
])

onMounted(() => {
  // Redirect back if no seats selected
  if (selectedSeats.value.length === 0 || !selectedShowtime.value) {
    navigateTo('/products')
  }
})

const totalComboPrice = computed(() => {
  return combos.value.reduce((acc, curr) => acc + (curr.price * curr.qty), 0)
})

function increaseQty(index: number) {
  combos.value[index].qty++
}

function decreaseQty(index: number) {
  if (combos.value[index].qty > 0) {
    combos.value[index].qty--
  }
}

function handleProceedToPayment() {
  // In a real app, we'd save selected combos to the store here
  // ticketsStore.setCombos(...)
  
  // Navigate to payment
  navigateTo('/checkout/payment')
}
</script>

<template>
  <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-12 pt-24">
    <!-- Selection Breadcrumb / Header -->
    <div class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <NuxtLink to="/checkout/seat" class="text-xs text-on-surface-variant hover:text-primary-container flex items-center gap-1 mb-2">
          <span class="material-symbols-outlined text-sm">arrow_back</span>
          Quay lại Chọn Ghế
        </NuxtLink>
        <h1 class="font-headline-lg text-2xl md:text-3xl font-black text-on-surface">
          Chọn Bắp Nước (Tùy chọn)
        </h1>
      </div>
      
      <!-- Stepper Indicator -->
      <div class="flex items-center gap-3 text-[10px] md:text-xs font-bold bg-surface-container-low border border-white/10 px-4 py-2.5 rounded-full overflow-x-auto whitespace-nowrap hide-scrollbar max-w-full">
        <span class="text-on-surface-variant flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">check_circle</span> Ghế</span>
        <span class="text-on-surface-variant">/</span>
        <span class="text-primary-container">2. Bắp Nước</span>
        <span class="text-on-surface-variant">/</span>
        <span class="text-on-surface-variant">3. Thanh Toán</span>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- Combo List (8 cols) -->
      <div class="lg:col-span-8 space-y-6">
        <div class="bg-surface-container-low border border-white/10 rounded-2xl p-6">
          <div class="flex items-center gap-3 mb-6">
            <span class="material-symbols-outlined text-primary-container text-3xl">local_dining</span>
            <h2 class="text-on-surface font-headline-md text-xl">Combo độc quyền từ {{ selectedShowtime?.branchName || 'Rạp' }}</h2>
          </div>
          
          <div class="space-y-4">
            <div v-for="(combo, index) in combos" :key="combo.id" class="flex items-center gap-4 p-4 rounded-xl border border-white/5 bg-surface hover:border-primary-container/30 transition-colors">
              <div class="w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-surface-container">
                <img :src="combo.img" :alt="combo.name" class="w-full h-full object-cover">
              </div>
              <div class="flex-grow">
                <h3 class="text-on-surface font-bold text-sm mb-1">{{ combo.name }}</h3>
                <p class="text-on-surface-variant text-xs mb-2">{{ combo.desc }}</p>
                <span class="text-primary-container font-bold text-sm">{{ combo.price.toLocaleString() }}đ</span>
              </div>
              <div class="flex items-center gap-3 bg-surface-container-high rounded-full p-1 border border-white/10">
                <button @click="decreaseQty(index)" class="w-8 h-8 rounded-full bg-surface hover:bg-white/10 flex items-center justify-center transition-colors text-on-surface" :class="combo.qty === 0 ? 'opacity-50 cursor-not-allowed' : ''">
                  <span class="material-symbols-outlined text-[16px]">remove</span>
                </button>
                <span class="w-4 text-center font-bold text-on-surface text-sm">{{ combo.qty }}</span>
                <button @click="increaseQty(index)" class="w-8 h-8 rounded-full bg-primary-container text-on-primary-container hover:scale-105 flex items-center justify-center transition-transform">
                  <span class="material-symbols-outlined text-[16px]">add</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary (4 cols) -->
      <div class="lg:col-span-4">
        <div class="bg-surface-container-low border border-white/10 rounded-2xl p-6 md:p-8 space-y-6 sticky top-24 shadow-xl">
          <div class="border-b border-white/10 pb-4">
            <h3 class="font-bold text-lg text-on-surface mb-2">Tóm Tắt Đơn Hàng</h3>
            <span class="text-sm font-semibold text-primary-container block">{{ activeMovie?.title || 'Phim' }}</span>
          </div>

          <!-- Tickets Subtotal -->
          <div class="space-y-3 text-sm text-on-surface-variant border-b border-white/10 pb-4">
            <div class="flex justify-between items-start">
              <span>Ghế x{{ selectedSeats.length }}:</span>
              <div class="text-right flex flex-col">
                <span class="font-bold text-on-surface">{{ selectedSeats.map(s => s.row + s.number).join(', ') }}</span>
                <span class="text-xs">{{ totalAmount.toLocaleString() }}đ</span>
              </div>
            </div>
          </div>

          <!-- Combos Subtotal -->
          <div v-if="totalComboPrice > 0" class="space-y-3 text-sm text-on-surface-variant border-b border-white/10 pb-4">
            <span class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Bắp nước</span>
            <div v-for="combo in combos.filter(c => c.qty > 0)" :key="combo.id" class="flex justify-between items-center text-xs">
              <span>{{ combo.qty }}x {{ combo.name }}</span>
              <span class="font-bold text-on-surface">{{ (combo.price * combo.qty).toLocaleString() }}đ</span>
            </div>
          </div>

          <!-- Total Amount -->
          <div class="pt-2">
            <div class="flex justify-between items-end mb-6">
              <span class="text-on-surface-variant font-medium">Tổng thanh toán:</span>
              <span class="text-3xl font-black text-primary-container">{{ (totalAmount + totalComboPrice).toLocaleString() }}đ</span>
            </div>

            <button
              @click="handleProceedToPayment"
              class="w-full bg-primary-container text-on-primary-container hover:bg-primary py-4 rounded-xl font-bold transition-all shadow-[0_0_20px_-5px_rgba(229,9,20,0.4)] flex justify-center items-center gap-2"
            >
              Tiếp tục Thanh toán
              <span class="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

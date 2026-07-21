<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'

definePageMeta({
  layout: 'default'
})

const ticketsStore = useTicketsStore()
const { selectedMovie, selectedShowtime, selectedSeats, totalAmount } = storeToRefs(ticketsStore)

onMounted(() => {
  // Redirect back to cinema selection if no showtime has been selected
  if (!selectedShowtime.value) {
    navigateTo('/checkout/cinema')
  }
})

function handleProceedToPayment() {
  if (selectedSeats.value.length === 0) return
  navigateTo('/checkout/payment')
}
</script>

<template>
  <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-12">
    <!-- Selection Breadcrumb / Header -->
    <div class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <button @click="$router.back()" class="text-xs text-on-surface-variant hover:text-primary-container flex items-center gap-1 mb-2">
          <span class="material-symbols-outlined text-sm">arrow_back</span>
          Quay lại Chọn Suất
        </button>
        <h1 class="font-headline-lg text-2xl md:text-3xl font-black text-on-surface">
          Chọn Ghế Ngồi Thông Minh
        </h1>
      </div>
      
      <!-- Stepper Indicator -->
      <div class="flex items-center justify-center gap-3 text-xs font-bold">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">1</div>
          <span>Chọn Rạp</span>
        </div>
        <div class="w-8 h-0.5 bg-surface-container-highest"></div>
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">2</div>
          <span>Chọn Suất</span>
        </div>
        <div class="w-8 h-0.5 bg-surface-container-highest"></div>
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center">3</div>
          <span>Chọn Ghế</span>
        </div>
        <div class="w-8 h-0.5 bg-surface-container-highest"></div>
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">4</div>
          <span>Thanh Toán</span>
        </div>
      </div>
    </div>

    <!-- Booking Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- Seat Map Grid (8 cols) -->
      <div class="lg:col-span-8">
        <SeatSelection />
      </div>

      <!-- Ticket Selection Summary (4 cols) -->
      <div class="lg:col-span-4" v-if="selectedShowtime">
        <div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8 space-y-6">
          <div class="border-b border-glass-stroke/40 pb-4">
            <h3 class="font-bold text-lg text-on-surface mb-2">Thông Tin Suất Chiếu</h3>
            <span class="text-sm font-semibold text-primary-fixed-dim block">{{ selectedMovie?.name }}</span>
          </div>

          <div class="space-y-3 text-xs text-on-surface-variant border-b border-glass-stroke/40 pb-4">
            <div class="flex justify-between">
              <span>Rạp:</span>
              <span class="font-bold text-on-surface">{{ selectedShowtime.branchName }}</span>
            </div>
            <div class="flex justify-between">
              <span>Phòng chiếu:</span>
              <span class="font-bold text-on-surface uppercase">{{ selectedShowtime.screenName }}</span>
            </div>
            <div class="flex justify-between">
              <span>Ngày chiếu:</span>
              <span class="font-bold text-on-surface">{{ selectedShowtime.date }}</span>
            </div>
            <div class="flex justify-between">
              <span>Giờ chiếu:</span>
              <span class="font-bold text-on-surface text-sm text-primary">{{ selectedShowtime.time }}</span>
            </div>
          </div>

          <!-- Selected seats selection report -->
          <div class="border-b border-glass-stroke/40 pb-4">
            <span class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Ghế Đã Chọn</span>
            
            <div v-if="selectedSeats.length === 0" class="text-xs text-on-surface-variant italic">
              Vui lòng chọn ghế ngồi trên sơ đồ.
            </div>

            <div v-else class="flex flex-wrap gap-2">
              <span
                v-for="seat in selectedSeats"
                :key="seat.id"
                class="bg-primary-container/10 border border-primary-container/20 text-primary-container text-xs font-bold px-3 py-1 rounded-lg"
              >
                {{ seat.row }}{{ seat.number }}
              </span>
            </div>
          </div>

          <!-- Total price summary -->
          <div class="flex items-center justify-between border-t border-glass-stroke/10 pt-4">
            <div class="flex flex-col">
              <span class="text-xs text-on-surface-variant">Tổng cộng:</span>
              <span class="text-xl font-black text-primary-fixed-dim">{{ totalAmount.toLocaleString() }} VNĐ</span>
            </div>
            
            <button
              @click="handleProceedToPayment"
              :disabled="selectedSeats.length === 0"
              class="bg-primary-container text-on-primary-container px-6 py-3 rounded-xl text-xs font-bold hover:scale-105 active:scale-95 transition-all flex items-center gap-1.5 red-glow disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100 disabled:shadow-none"
            >
              Tiếp tục
              <span class="material-symbols-outlined text-xs">arrow_forward</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

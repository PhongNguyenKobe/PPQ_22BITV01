<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { useMoviesStore } from '~/store/movies'

definePageMeta({
  layout: 'default'
})

const ticketsStore = useTicketsStore()
const moviesStore = useMoviesStore()
const { selectedShowtime, selectedSeats, totalAmount, loading } = storeToRefs(ticketsStore)
const { activeMovie } = storeToRefs(moviesStore)

const selectedPayment = ref('Ví Momo')
const processing = ref(false)
const showQR = ref(false)

const paymentMethods = [
  { name: 'Ví Momo', icon: 'payments', desc: 'Thanh toán qua ứng dụng Momo' },
  { name: 'Ví VNPAY', icon: 'account_balance_wallet', desc: 'Thanh toán qua cổng VNPAY' },
  { name: 'Thẻ ATM/Tín Dụng', icon: 'credit_card', desc: 'Visa, Mastercard, JCB hoặc thẻ nội địa' },
  { name: 'Quét Mã QR', icon: 'qr_code_scanner', desc: 'Quét mã QR để chuyển khoản nhanh' }
]

onMounted(() => {
  // If no seats selected, send them back to seat choice
  if (selectedSeats.value.length === 0 || !selectedShowtime.value) {
    navigateTo('/movies')
  }
})

async function handleConfirmPayment() {
  if (selectedPayment.value === 'Quét Mã QR' && !showQR.value) {
    showQR.value = true
    return
  }

  processing.value = true
  
  // Simulate network payment validation delay
  await new Promise(resolve => setTimeout(resolve, 2000))

  try {
    const ticket = await ticketsStore.purchaseTickets(selectedPayment.value)
    if (ticket) {
      navigateTo('/profile/tickets')
    }
  } catch (e) {
    console.error('Payment confirmation error', e)
  } finally {
    processing.value = false
  }
}
</script>

<template>
  <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-12">
    <div class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <NuxtLink to="/checkout/seat" class="text-xs text-on-surface-variant hover:text-primary-container flex items-center gap-1 mb-2">
          <span class="material-symbols-outlined text-sm">arrow_back</span>
          Quay lại Chọn Ghế
        </NuxtLink>
        <h1 class="font-headline-lg text-2xl md:text-3xl font-black text-on-surface">
          Thanh Toán Đơn Vé
        </h1>
      </div>
      
      <!-- Stepper Indicator -->
      <div class="flex items-center gap-3 text-xs font-bold bg-surface-container-low border border-glass-stroke px-4 py-2.5 rounded-full">
        <span class="text-on-surface-variant">1. Chọn Ghế</span>
        <span class="text-on-surface-variant">/</span>
        <span class="text-primary-container">2. Thanh Toán</span>
        <span class="text-on-surface-variant">/</span>
        <span class="text-on-surface-variant">3. Nhận Vé</span>
      </div>
    </div>

    <!-- Payment contents layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      
      <!-- Payment Methods (8 cols) -->
      <div class="lg:col-span-8 space-y-6">
        <div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8">
          <h3 class="font-bold text-lg text-on-surface mb-6 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary-container">payment</span>
            Chọn Phương Thức Thanh Toán
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              v-for="method in paymentMethods"
              :key="method.name"
              @click="selectedPayment = method.name; showQR = false"
              class="border rounded-2xl p-4 text-left flex items-start gap-4 transition-all"
              :class="selectedPayment === method.name
                ? 'bg-primary-container/5 border-primary-container shadow-md'
                : 'bg-surface border-glass-stroke hover:bg-white/5'"
            >
              <div class="w-10 h-10 rounded-xl flex items-center justify-center bg-surface-container border border-glass-stroke text-primary-container">
                <span class="material-symbols-outlined">{{ method.icon }}</span>
              </div>
              <div>
                <span class="block text-sm font-semibold text-on-surface">{{ method.name }}</span>
                <span class="text-xs text-on-surface-variant block mt-1">{{ method.desc }}</span>
              </div>
            </button>
          </div>
        </div>

        <!-- Simulated Scan QR Modal Box -->
        <div v-if="selectedPayment === 'Quét Mã QR' && showQR" class="glass-panel border border-purple-500/20 rounded-2xl p-6 md:p-8 flex flex-col items-center text-center">
          <span class="bg-secondary-container/20 border border-secondary-container/30 text-secondary text-[11px] font-bold px-3 py-1 rounded-full inline-flex items-center gap-1.5 backdrop-blur-md mb-4">
            <span class="material-symbols-outlined text-xs">qr_code</span>
            Cổng thanh toán tự động
          </span>
          <h4 class="font-bold text-base text-on-surface mb-2">Quét Mã QR Để Thanh Toán</h4>
          <p class="text-xs text-on-surface-variant max-w-sm mb-6">Mã QR bên dưới chứa thông tin tài khoản và tổng số tiền thanh toán của bạn.</p>
          
          <!-- Mock QR image -->
          <div class="w-48 h-48 bg-white p-3 rounded-2xl border border-glass-stroke mb-4 shadow-xl">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=CineAI_Checkout_Booking" alt="Mock QR Code Checkout" class="w-full h-full" />
          </div>
          
          <span class="text-xs text-on-surface-variant">Vui lòng quét mã và xác nhận chuyển khoản để hoàn tất.</span>
        </div>
      </div>

      <!-- Summary & Confirm (4 cols) -->
      <div class="lg:col-span-4" v-if="selectedShowtime">
        <div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8 space-y-6">
          <div>
            <h3 class="font-bold text-lg text-on-surface mb-2">Đơn Vé Của Bạn</h3>
            <span class="text-sm font-semibold text-primary-fixed-dim block">{{ activeMovie?.title }}</span>
          </div>

          <div class="space-y-3 text-xs text-on-surface-variant border-t border-glass-stroke/40 pt-4">
            <div class="flex justify-between">
              <span>Rạp:</span>
              <span class="font-bold text-on-surface">{{ selectedShowtime.branchName }}</span>
            </div>
            <div class="flex justify-between">
              <span>Suất chiếu:</span>
              <span class="font-bold text-on-surface text-primary">{{ selectedShowtime.time }} | {{ selectedShowtime.date }}</span>
            </div>
            <div class="flex justify-between">
              <span>Phòng chiếu:</span>
              <span class="font-bold text-on-surface uppercase">{{ selectedShowtime.screenName }}</span>
            </div>
            <div class="flex justify-between">
              <span>Ghế ngồi:</span>
              <div class="flex flex-wrap gap-1 justify-end max-w-[60%]">
                <span v-for="seat in selectedSeats" :key="seat.id" class="font-bold text-on-surface">
                  {{ seat.row }}{{ seat.number }},
                </span>
              </div>
            </div>
          </div>

          <div class="border-t border-glass-stroke/40 pt-4 space-y-4">
            <div class="flex justify-between items-center text-xs">
              <span class="text-on-surface-variant">Phương thức:</span>
              <span class="font-bold text-on-surface">{{ selectedPayment }}</span>
            </div>
            
            <div class="flex justify-between items-center">
              <span class="text-xs text-on-surface-variant">Tổng số tiền:</span>
              <span class="text-lg font-black text-primary">{{ totalAmount.toLocaleString() }} VNĐ</span>
            </div>
          </div>

          <!-- Proceed to validation button -->
          <button
            @click="handleConfirmPayment"
            :disabled="processing"
            class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-105 active:scale-95 transition-all text-xs flex items-center justify-center gap-2 red-glow disabled:opacity-50"
          >
            <template v-if="processing">
              <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              Đang xác thực...
            </template>
            <template v-else>
              Xác Nhận Thanh Toán
            </template>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

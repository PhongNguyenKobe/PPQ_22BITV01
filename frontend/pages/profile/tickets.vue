<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'default'
})

const ticketsStore = useTicketsStore()
const userStore = useUserStore()

const { ticketHistory } = storeToRefs(ticketsStore)
const { currentUser, isAuthenticated } = storeToRefs(userStore)

onMounted(() => {
  if (!isAuthenticated.value) {
    navigateTo('/login')
  }
})
</script>

<template>
  <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-12">
    <div v-if="!isAuthenticated" class="py-24 text-center text-on-surface-variant">
      ⚠️ Vui lòng đăng nhập để xem thông tin vé điện tử của bạn.
      <div class="mt-4">
        <NuxtLink to="/login" class="bg-primary-container text-white px-6 py-2.5 rounded-xl font-bold">Đăng nhập</NuxtLink>
      </div>
    </div>

    <div v-else class="space-y-12">
      <!-- Welcome Header -->
      <div class="border-b border-glass-stroke pb-6">
        <h1 class="font-headline-lg text-2xl md:text-3xl font-black text-on-surface">Vé Điện Tử Của Tôi</h1>
        <p class="text-xs text-on-surface-variant mt-1">
          Lưu trữ thông tin vé và quét mã QR tại quầy soát vé để vào phòng chiếu.
        </p>
      </div>

      <!-- Tickets container -->
      <div v-if="ticketHistory.length === 0" class="py-16 text-center text-on-surface-variant">
        <span class="material-symbols-outlined text-[48px] mb-2 text-on-surface-variant">confirmation_number</span>
        <p class="text-sm font-medium">Bạn chưa thực hiện bất kỳ giao dịch đặt vé nào.</p>
        <NuxtLink to="/movies" class="text-primary-container font-bold hover:underline mt-2 inline-block">Đặt vé ngay</NuxtLink>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Loop tickets -->
        <div
          v-for="ticket in ticketHistory"
          :key="ticket.id"
          class="glass-panel border border-glass-stroke rounded-3xl overflow-hidden flex flex-col md:flex-row shadow-xl relative"
        >
          <!-- Absolute decorative ticket notches -->
          <div class="hidden md:block absolute left-[65%] top-0 -translate-y-1/2 w-8 h-8 rounded-full bg-background z-20"></div>
          <div class="hidden md:block absolute left-[65%] bottom-0 translate-y-1/2 w-8 h-8 rounded-full bg-background z-20"></div>

          <!-- Movie Poster & Details (Left 65%) -->
          <div class="p-6 md:w-[65%] flex flex-col justify-between space-y-4">
            <div class="flex gap-4">
              <!-- Small poster -->
              <img :src="ticket.poster" :alt="ticket.movieTitle" class="w-20 h-28 object-cover rounded-xl border border-glass-stroke flex-shrink-0" />
              <div>
                <span class="text-[10px] bg-primary-container/10 border border-primary-container/20 text-primary-container px-2 py-0.5 rounded font-bold uppercase">
                  Vé Đã Xác Nhận
                </span>
                <h3 class="font-black text-base text-on-surface line-clamp-2 mt-1 leading-snug">{{ ticket.movieTitle }}</h3>
                <p class="text-[11px] text-on-surface-variant mt-1">Mã đặt vé: <span class="text-on-surface font-bold font-mono">{{ ticket.id }}</span></p>
              </div>
            </div>

            <!-- Showtime meta -->
            <div class="grid grid-cols-2 gap-3 text-xs text-on-surface-variant border-t border-glass-stroke/40 pt-4">
              <div>
                <span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">Rạp Chiếu</span>
                <span class="font-bold text-on-surface truncate block">{{ ticket.branchName }}</span>
              </div>
              <div>
                <span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">Phòng Chiếu</span>
                <span class="font-bold text-on-surface uppercase">{{ ticket.screenName }}</span>
              </div>
              <div>
                <span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">Thời Gian</span>
                <span class="font-bold text-primary block">{{ ticket.time }} | {{ ticket.date }}</span>
              </div>
              <div>
                <span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">Ghế Ngồi</span>
                <span class="font-bold text-on-surface truncate block">{{ ticket.seats.join(', ') }}</span>
              </div>
            </div>

            <div class="border-t border-glass-stroke/20 pt-3 flex justify-between items-center text-xs text-on-surface-variant">
              <span>Ngày đặt: {{ ticket.bookingDate }}</span>
              <span class="font-bold text-on-surface">{{ ticket.totalAmount.toLocaleString() }}đ</span>
            </div>
          </div>

          <!-- Dotted Divider Line -->
          <div class="border-t md:border-t-0 md:border-l border-dashed border-glass-stroke/60 relative"></div>

          <!-- QR code panel (Right 35%) -->
          <div class="p-6 md:w-[35%] bg-surface-container/20 flex flex-col items-center justify-center text-center space-y-4">
            <div class="w-32 h-32 bg-white p-2 rounded-2xl border border-glass-stroke shadow-md">
              <img :src="`https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${ticket.qrCode}`" alt="E-Ticket QR code" class="w-full h-full" />
            </div>
            <div>
              <span class="text-[10px] text-on-surface-variant uppercase tracking-wider block">Quét tại quầy vé</span>
              <span class="text-xs font-bold text-on-surface mt-0.5 block font-mono">{{ ticket.id }}</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

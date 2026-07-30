<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { useUserStore } from '~/store/user'
import type { UserTicket } from '~/services/api'
import { formatDate, formatDateTime } from '~/utils/date'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const ticketsStore = useTicketsStore()
const userStore = useUserStore()

const { ticketHistory, historyLoading, historyError } = storeToRefs(ticketsStore)
const { currentUser, isAuthenticated } = storeToRefs(userStore)

const selectedTicket = ref<UserTicket | null>(null)
const cancellationLoading = ref(false)
const cancellationError = ref('')

// Phân trang
const currentPage = ref(1)
const pageSize = 6

const totalPages = computed(() => Math.ceil(ticketHistory.value.length / pageSize))

const paginatedTickets = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return ticketHistory.value.slice(start, start + pageSize)
})

const visiblePages = computed(() => {
  const range = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) {
    range.push(i)
  }
  return range
})

function scrollToTop() {
  if (process.client) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

watch(ticketHistory, () => {
  currentPage.value = 1
})

const canRequestCancellation = computed(() => {
  if (!selectedTicket.value || selectedTicket.value.status !== 'CONFIRMED') return false
  return new Date(`${selectedTicket.value.date}T${selectedTicket.value.time}`).getTime() > Date.now()
})

function closeTicketDetails() {
  selectedTicket.value = null
  cancellationError.value = ''
}

async function requestCancellation() {
  if (!selectedTicket.value || !canRequestCancellation.value) return
  const reason = window.prompt('Vui lòng nhập lý do yêu cầu hủy vé (ít nhất 5 ký tự):')?.trim()
  if (!reason) return
  if (reason.length < 5) {
    cancellationError.value = 'Lý do phải có ít nhất 5 ký tự.'
    return
  }
  cancellationLoading.value = true
  cancellationError.value = ''
  try {
    const bookingId = selectedTicket.value.id
    await ticketsStore.requestCancellation(bookingId, reason)
    selectedTicket.value = ticketHistory.value.find(ticket => ticket.id === bookingId) || null
  } catch (error: any) {
    cancellationError.value = error?.message || 'Không thể gửi yêu cầu hủy vé.'
  } finally {
    cancellationLoading.value = false
  }
}

onMounted(async () => {
  if (!isAuthenticated.value) {
    await navigateTo('/login')
    return
  }
  await ticketsStore.loadTicketHistory()
})
</script>

<template>
  <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-12">
    <div v-if="!isAuthenticated" class="py-24 text-center text-on-surface-variant">
      Vui lòng đăng nhập để xem thông tin vé điện tử của bạn.
      <div class="mt-4">
        <NuxtLink to="/login" class="bg-primary-container text-white px-6 py-2.5 rounded-xl font-bold">Đăng nhập
        </NuxtLink>
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
      <div v-if="historyError && ticketHistory.length > 0"
        class="mb-6 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
        {{ historyError }} Dữ liệu bên dưới là bản lưu tạm trên trình duyệt.
      </div>

      <div v-if="historyLoading" class="py-16 text-center text-on-surface-variant">
        <span class="material-symbols-outlined text-[40px] mb-2 animate-spin">progress_activity</span>
        <p class="text-sm font-medium">Đang tải vé của bạn...</p>
      </div>

      <div v-else-if="historyError && ticketHistory.length === 0" class="py-16 text-center text-on-surface-variant">
        <span class="material-symbols-outlined text-[40px] mb-2 text-red-400">error</span>
        <p class="text-sm font-medium">{{ historyError }}</p>
        <button class="text-primary-container font-bold hover:underline mt-2" @click="ticketsStore.loadTicketHistory()">
          Thử lại
        </button>
      </div>

      <div v-else-if="ticketHistory.length === 0" class="py-16 text-center text-on-surface-variant">
        <span class="material-symbols-outlined text-[48px] mb-2 text-on-surface-variant">confirmation_number</span>
        <p class="text-sm font-medium">Bạn chưa thực hiện bất kỳ giao dịch đặt vé nào.</p>
        <NuxtLink to="/products" class="text-primary-container font-bold hover:underline mt-2 inline-block">Đặt vé ngay
        </NuxtLink>
      </div>

      <div v-else class="space-y-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Loop tickets -->
          <div v-for="ticket in paginatedTickets" :key="ticket.id" @click="selectedTicket = ticket"
            class="glass-panel border border-glass-stroke rounded-3xl overflow-hidden flex flex-col md:flex-row shadow-xl relative cursor-pointer hover:border-primary-container/50 hover:shadow-primary-container/20 transition-all duration-300 transform hover:-translate-y-1">
            <!-- Absolute decorative ticket notches -->
            <div
              class="hidden md:block absolute left-[65%] top-0 -translate-y-1/2 w-8 h-8 rounded-full bg-background z-20">
            </div>
            <div
              class="hidden md:block absolute left-[65%] bottom-0 translate-y-1/2 w-8 h-8 rounded-full bg-background z-20">
            </div>

            <!-- Movie Poster & Details (Left 65%) -->
            <div class="p-6 md:w-[65%] flex flex-col justify-between space-y-4">
              <div class="flex gap-4">
                <!-- Small poster -->
                <img :src="ticket.poster" :alt="ticket.movieTitle"
                  class="w-20 h-28 object-cover rounded-xl border border-glass-stroke flex-shrink-0" />
                <div>
                  <span
                    class="text-[10px] bg-primary-container/10 border border-primary-container/20 text-primary-container px-2 py-0.5 rounded font-bold uppercase">
                    Vé Đã Xác Nhận
                  </span>
                  <h3 class="font-black text-base text-on-surface line-clamp-2 mt-1 leading-snug">{{ ticket.movieTitle }}
                  </h3>
                  <p class="text-[11px] text-on-surface-variant mt-1">Mã đặt vé: <span
                      class="text-on-surface font-bold font-mono">{{ ticket.id }}</span></p>
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
                  <span class="font-bold text-primary block">{{ ticket.time }} | {{ formatDate(ticket.date) }}</span>
                </div>
                <div>
                  <span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">Ghế Ngồi</span>
                  <span class="font-bold text-on-surface truncate block">{{ ticket.seats.join(', ') }}</span>
                </div>
              </div>

              <div
                class="border-t border-glass-stroke/20 pt-3 flex justify-between items-center text-xs text-on-surface-variant">
                <span>Ngày đặt: {{ formatDateTime(ticket.bookingDate) }}</span>
                <span class="font-bold text-on-surface">{{ ticket.totalAmount.toLocaleString() }}đ</span>
              </div>
            </div>

            <!-- Dotted Divider Line -->
            <div class="border-t md:border-t-0 md:border-l border-dashed border-glass-stroke/60 relative"></div>

            <!-- QR code panel (Right 35%) -->
            <div
              class="p-6 md:w-[35%] bg-surface-container/20 flex flex-col items-center justify-center text-center space-y-4">
              <div class="w-32 h-32 bg-white p-2 rounded-2xl border border-glass-stroke shadow-md">
                <QrCodeImage :value="ticket.qrCode" :size="120" />
              </div>
              <div>
                <span class="text-[10px] text-on-surface-variant uppercase tracking-wider block">Quét tại quầy vé</span>
                <span class="text-xs font-bold text-on-surface mt-0.5 block font-mono">{{ ticket.id }}</span>
              </div>
            </div>

          </div>
        </div>

        <!-- Pagination Controls -->
        <div v-if="totalPages > 1" class="flex flex-col sm:flex-row justify-between items-center gap-4 pt-6 border-t border-glass-stroke/20">
          <span class="text-xs text-on-surface-variant">Hiển thị trang {{ currentPage }} / {{ totalPages }} (Tổng {{ ticketHistory.length }} vé)</span>
          <div class="flex items-center gap-1.5">
            <button 
              :disabled="currentPage === 1" 
              @click="currentPage--; scrollToTop()"
              class="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-primary-container disabled:bg-transparent border border-glass-stroke/40 hover:border-primary-container disabled:opacity-30 transition-all text-xs font-bold text-on-surface disabled:hover:text-on-surface disabled:cursor-not-allowed flex items-center gap-1"
            >
              <span class="material-symbols-outlined text-xs">chevron_left</span>
              Trước
            </button>
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="currentPage = page; scrollToTop()"
              class="w-8 h-8 rounded-xl text-xs font-bold transition-all border flex items-center justify-center"
              :class="currentPage === page ? 'bg-primary-container border-primary-container text-white' : 'bg-white/5 border-glass-stroke/40 hover:bg-white/10 text-on-surface'"
            >
              {{ page }}
            </button>
            <button 
              :disabled="currentPage === totalPages" 
              @click="currentPage++; scrollToTop()"
              class="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-primary-container disabled:bg-transparent border border-glass-stroke/40 hover:border-primary-container disabled:opacity-30 transition-all text-xs font-bold text-on-surface disabled:hover:text-on-surface disabled:cursor-not-allowed flex items-center gap-1"
            >
              Sau
              <span class="material-symbols-outlined text-xs">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Ticket Details Modal (Teleported to body for better z-index management if needed, but here inline is fine) -->
    <div v-if="selectedTicket"
      class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      @click.self="closeTicketDetails">
      <div
        class="bg-surface-container rounded-3xl w-full max-w-md md:max-w-lg overflow-hidden border border-glass-stroke shadow-[0_0_40px_rgba(255,122,26,0.15)] animate-fade-in relative flex flex-col max-h-[90vh]">
        <!-- Close button -->
        <button @click="closeTicketDetails"
          class="absolute top-4 right-4 text-white hover:text-primary-container bg-black/40 backdrop-blur-md rounded-full p-2 transition-all z-20 flex items-center justify-center border border-white/10 hover:border-primary-container/50">
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>

        <!-- Movie Banner & Title -->
        <div class="relative w-full h-48 md:h-56 flex-shrink-0">
          <div class="absolute inset-0 bg-cover bg-center"
            :style="{ backgroundImage: `url(${selectedTicket.poster})`, filter: 'blur(8px) brightness(0.4)' }"></div>
          <div class="absolute inset-0 bg-gradient-to-t from-surface-container via-surface-container/80 to-transparent">
          </div>
          <div class="absolute bottom-4 left-6 right-6 flex items-end gap-4">
            <img :src="selectedTicket.poster"
              class="w-24 h-36 md:w-28 md:h-40 rounded-xl border border-glass-stroke shadow-2xl object-cover z-10" />
            <div class="pb-1 z-10 flex-1">
              <span
                class="bg-primary-container text-white text-[10px] uppercase font-bold px-2 py-1 rounded-md tracking-wider">Vé
                Đã Thanh Toán</span>
              <h2 class="text-xl md:text-2xl font-black text-white mt-2 leading-tight line-clamp-2">{{
                selectedTicket.movieTitle }}</h2>
            </div>
          </div>
        </div>

        <!-- Ticket Body (Scrollable if needed) -->
        <div class="p-6 overflow-y-auto custom-scrollbar flex-1">
          <!-- Big QR Code -->
          <div class="flex flex-col items-center justify-center mb-6">
            <div class="bg-white p-3 rounded-2xl border border-glass-stroke shadow-lg mb-3">
              <QrCodeImage :value="selectedTicket.qrCode" :size="250"
                class="w-40 h-40 md:w-48 md:h-48" />
            </div>
            <p class="text-center text-xs text-on-surface-variant uppercase tracking-widest">Mã đặt vé</p>
            <p class="text-center text-lg font-bold text-white font-mono mt-0.5">{{ selectedTicket.id }}</p>
          </div>

          <!-- Detailed Info Grid -->
          <div class="bg-surface/50 rounded-2xl border border-glass-stroke p-5 space-y-4">
            <div class="grid grid-cols-2 gap-y-4 gap-x-6 text-sm">
              <div>
                <p class="text-on-surface-variant text-[11px] uppercase tracking-wider mb-1">Rạp Chiếu</p>
                <p class="font-bold text-white">{{ selectedTicket.branchName }}</p>
              </div>
              <div>
                <p class="text-on-surface-variant text-[11px] uppercase tracking-wider mb-1">Phòng Chiếu</p>
                <p class="font-bold text-white uppercase">{{ selectedTicket.screenName }}</p>
              </div>
              <div>
                <p class="text-on-surface-variant text-[11px] uppercase tracking-wider mb-1">Thời Gian</p>
                <p class="font-bold text-primary-container">{{ selectedTicket.time }}</p>
                <p class="font-semibold text-white/90 text-xs">{{ formatDate(selectedTicket.date) }}</p>
              </div>
              <div>
                <p class="text-on-surface-variant text-[11px] uppercase tracking-wider mb-1">Ghế Ngồi</p>
                <p class="font-bold text-white">{{ selectedTicket.seats.join(', ') }}</p>
              </div>
            </div>

            <div class="border-t border-glass-stroke/50 pt-4 flex justify-between items-center">
              <div>
                <p class="text-on-surface-variant text-[11px] uppercase tracking-wider mb-1">Thanh toán</p>
                <p class="font-bold text-white">{{ selectedTicket.paymentMethod || 'Không xác định' }}</p>
              </div>
              <div class="text-right">
                <p class="text-on-surface-variant text-[11px] uppercase tracking-wider mb-1">Tổng tiền</p>
                <p class="font-black text-xl text-primary">{{ selectedTicket.totalAmount.toLocaleString() }}đ</p>
              </div>
            </div>
          </div>

          <div class="text-center mt-6">
            <p class="text-[11px] text-on-surface-variant/70">Ngày đặt vé: {{ formatDateTime(selectedTicket.bookingDate) }}</p>
            <p v-if="selectedTicket.status === 'CANCEL_REQUESTED'" class="mt-3 text-sm font-bold text-amber-400">
              Đang chờ chi nhánh duyệt yêu cầu hủy
            </p>
            <p v-else-if="selectedTicket.status === 'CANCELLED'" class="mt-3 text-sm font-bold text-red-400">
              Vé đã hủy
            </p>
            <p v-if="selectedTicket.cancellationReason" class="mt-1 text-xs text-on-surface-variant">
              Lý do: {{ selectedTicket.cancellationReason }}
            </p>
            <p v-if="cancellationError" class="mt-3 text-xs text-red-400">{{ cancellationError }}</p>
            <button
              v-if="canRequestCancellation"
              class="mt-4 rounded-xl border border-red-500/40 px-4 py-2 text-sm font-bold text-red-300 hover:bg-red-500/10 disabled:opacity-50"
              :disabled="cancellationLoading"
              @click="requestCancellation"
            >
              {{ cancellationLoading ? 'Đang gửi...' : 'Yêu cầu hủy vé' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.2s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }

  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>

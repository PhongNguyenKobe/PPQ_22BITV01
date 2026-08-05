<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { checkoutService } from '~/services/api'
import { isShowtimeExpired } from '../../utils/showtime'
import { formatDate } from '~/utils/date'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const ticketsStore = useTicketsStore()
const { selectedMovie, selectedShowtime, selectedSeats, selectedCombos, totalAmount, purchaseError } = storeToRefs(ticketsStore)
const showtimeExpired = computed(() => isShowtimeExpired(selectedShowtime.value))

const selectedPayment = ref('Ví VNPAY')
const processing = ref(false)
const showQR = ref(false)
const preparedVnpayPayment = ref<{ transactionRef: string; paymentUrl: string } | null>(null)
const cancellingPayment = ref(false)

// --- BỔ SUNG STATE VOUCHER ---
const voucherCode = ref('')
const isVoucherApplied = ref(false)
const voucherDiscount = ref(0) // Số tiền giảm giá (VNĐ)
const voucherError = ref('')
const voucherSuccessMsg = ref('')

const paymentMethods = [
  { name: 'Paypal', icon: 'payments', desc: 'Thanh toán qua Paypal', enabled: true },
  { name: 'Ví VNPAY', icon: 'account_balance_wallet', desc: 'Thanh toán qua cổng VNPAY', enabled: true },
  { name: 'Thẻ ATM/Tín Dụng', icon: 'credit_card', desc: 'Tạm thời chưa phát triển', enabled: false },
  { name: 'Quét Mã QR', icon: 'qr_code_scanner', desc: 'Tạm thời chưa phát triển', enabled: false }
]

// Tính toán tổng tiền sau khi trừ voucher
const finalTotal = computed(() => {
  return Math.max(0, totalAmount.value - voucherDiscount.value)
})

const backgroundStyle = computed(() => {
  if (!selectedMovie.value?.imageUrl) return {}
  return {
    backgroundImage: `linear-gradient(90deg, rgba(18,20,20,0.95) 0%, rgba(18,20,20,0.82) 24%, rgba(18,20,20,0.68) 56%, rgba(18,20,20,0.92) 100%), url('${selectedMovie.value.imageUrl}')`,
  }
})

const formattedMoviePrice = computed(() => {
  if (!selectedMovie.value?.price) return 'Đang cập nhật'
  return new Intl.NumberFormat('vi-VN').format(Number(selectedMovie.value.price) * 1000) + 'đ'
})

onMounted(() => {
  if (selectedSeats.value.length === 0 || !selectedShowtime.value) {
    navigateTo('/checkout/seat')
  }
})

// --- HÀM XỬ LÝ ÁP DỤNG VOUCHER ---
async function applyVoucher() {
  voucherError.value = ''
  voucherSuccessMsg.value = ''
  const code = voucherCode.value.trim().toUpperCase()

  if (!code) {
    voucherError.value = 'Vui lòng nhập mã giảm giá'
    return
  }

  try {
    const quote = await checkoutService.validatePromotion(code, totalAmount.value)
    voucherCode.value = quote.code
    voucherDiscount.value = Number(quote.discount_amount)
    isVoucherApplied.value = true
    voucherSuccessMsg.value = `Đã áp dụng ${quote.code} (-${voucherDiscount.value.toLocaleString('vi-VN')}đ)`
  } catch (error: any) {
    voucherDiscount.value = 0
    isVoucherApplied.value = false
    voucherError.value = error?.message || 'Mã giảm giá không hợp lệ hoặc đã hết hạn'
  }
}

function removeVoucher() {
  voucherCode.value = ''
  voucherDiscount.value = 0
  isVoucherApplied.value = false
  voucherError.value = ''
  voucherSuccessMsg.value = ''
}

async function handleConfirmPayment() {
  if (showtimeExpired.value) {
    purchaseError.value = 'Đã hết thời gian mua vé cho suất chiếu này. Vui lòng chọn suất khác.'
    return
  }
  processing.value = true
  try {
    if (selectedPayment.value === 'Ví VNPAY') {
      const payment = await ticketsStore.startVnpayPayment(
        isVoucherApplied.value ? voucherCode.value : undefined,
        finalTotal.value,
      )
      if (payment) {
        preparedVnpayPayment.value = payment
      }
      return
    }
    if (selectedPayment.value === 'Paypal') {
      const payment = await ticketsStore.startPaypalPayment(
        isVoucherApplied.value ? voucherCode.value : undefined,
        finalTotal.value,
      )
      if (payment && payment.paymentUrl) {
        if (process.client) {
          window.location.assign(payment.paymentUrl)
        }
      }
      return
    }
    purchaseError.value = 'Phương thức này tạm thời chưa phát triển. Vui lòng chọn VNPAY hoặc Paypal.'
  } catch (e) {
    console.error('Payment confirmation error', e)
  } finally {
    processing.value = false
  }
}

async function cancelPreparedVnpayPayment() {
  if (!preparedVnpayPayment.value || cancellingPayment.value) return
  cancellingPayment.value = true
  purchaseError.value = ''
  try {
    await checkoutService.cancelPendingPayment(preparedVnpayPayment.value.transactionRef)
    preparedVnpayPayment.value = null
    await ticketsStore.releaseCurrentSeatHolds()
    await navigateTo('/checkout/seat')
  } catch (error: any) {
    purchaseError.value = error?.message || 'Không thể hủy yêu cầu thanh toán. Vui lòng tải lại và thử lại.'
  } finally {
    cancellingPayment.value = false
  }
}
</script>

<template>
  <section class="checkout-shell py-6 px-3 sm:px-5 md:px-8">
    <div class="checkout-hero max-w-[1500px] mx-auto" :style="backgroundStyle">
      <div class="checkout-overlay"></div>

      <div class="checkout-grid">
        <aside class="movie-column" v-if="selectedMovie">
          <img :src="selectedMovie.imageUrl" :alt="selectedMovie.name" class="movie-poster" />

          <div class="movie-meta">
            <h2 class="movie-title">{{ selectedMovie.name }}</h2>
            <div class="movie-badges">
              <span v-if="selectedMovie.rating" class="movie-rating">
                <span class="material-symbols-outlined text-sm text-yellow-400">star</span>
                {{ Number(selectedMovie.rating).toFixed(1) }}
              </span>
              <span class="movie-dot">•</span>
              <span>{{ selectedMovie.category || '2D' }}</span>
            </div>
            <p class="movie-price">Giá từ {{ formattedMoviePrice }}</p>
          </div>
        </aside>

        <main class="selection-column">
          <div class="booking-stepper">
            <div class="step done"><span>1</span><small>Chọn rạp</small></div>
            <div class="step-line active"></div>
            <div class="step done"><span>2</span><small>Chọn suất</small></div>
            <div class="step-line active"></div>
            <div class="step done"><span>3</span><small>Chọn ghế</small></div>
            <div class="step-line active"></div>
            <div class="step done"><span>4</span><small>Bắp nước</small></div>
            <div class="step-line active"></div>
            <div class="step active"><span>5</span><small>Thanh toán</small></div>
          </div>

          <div class="selection-panel">
            <div v-if="showtimeExpired || purchaseError"
              class="mb-4 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-300">
              <strong>Không thể tiếp tục thanh toán</strong>
              <p class="mt-1 text-sm">{{ purchaseError || 'Đã hết thời gian mua vé cho suất chiếu này.' }}</p>
              <NuxtLink to="/checkout/showtime" class="mt-3 inline-block font-bold underline">Chọn suất chiếu khác
              </NuxtLink>
            </div>
            <div class="selection-header">
              <h1>Thanh Toán Đơn Vé</h1>
              <p>Chọn phương thức thanh toán và xác nhận giao dịch.</p>
            </div>

            <div class="methods-grid">
              <button v-for="method in paymentMethods" :key="method.name"
                :disabled="!method.enabled"
                @click="selectedPayment = method.name; showQR = false; preparedVnpayPayment = null"
                :class="['method-card', selectedPayment === method.name ? 'method-active' : '', !method.enabled ? 'cursor-not-allowed opacity-45' : '']">
                <div class="method-icon">
                  <span class="material-symbols-outlined">{{ method.icon }}</span>
                </div>
                <h3>{{ method.name }}</h3>
                <p>{{ method.desc }}</p>
                <span v-if="selectedPayment === method.name"
                  class="method-check material-symbols-outlined">check_circle</span>
              </button>
            </div>

            <div class="method-note">
              Với VNPAY, hệ thống sẽ lưu yêu cầu PENDING trước. Sau đó bạn chủ động mở cổng thanh toán trong tab mới.
            </div>

            <div v-if="preparedVnpayPayment" class="mt-4 rounded-xl border border-amber-400/30 bg-amber-400/10 p-4">
              <h4 class="font-bold text-amber-300">Đã lưu yêu cầu VNPAY trong hệ thống</h4>
              <p class="mt-2 text-sm text-on-surface-variant">
                Giao dịch đang PENDING trong CineAI. Bấm nút bên dưới để thanh toán tại VNPAY; CineAI vẫn được giữ ở tab này.
              </p>
              <div class="mt-3 text-sm">
                <span class="text-on-surface-variant">Mã tham chiếu:</span>
                <strong class="ml-2 break-all font-mono">{{ preparedVnpayPayment.transactionRef }}</strong>
              </div>
              <a
                :href="preparedVnpayPayment.paymentUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="mt-4 inline-flex items-center gap-2 rounded-xl bg-primary-container px-5 py-3 font-bold text-on-primary-container"
              >
                <span class="material-symbols-outlined">open_in_new</span>
                Mở VNPAY để thanh toán
              </a>
              <button
                type="button"
                :disabled="cancellingPayment"
                class="ml-3 mt-4 inline-flex items-center gap-2 rounded-xl border border-red-400/40 px-5 py-3 font-bold text-red-300 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                @click="cancelPreparedVnpayPayment"
              >
                <span class="material-symbols-outlined">cancel</span>
                {{ cancellingPayment ? 'Đang hủy...' : 'Hủy yêu cầu và chọn lại ghế' }}
              </button>
              <p class="mt-3 text-xs text-on-surface-variant">
                Sau khi thanh toán xong, quay lại tab CineAI hoặc chọn “Xem vé của tôi” tại trang kết quả.
              </p>
            </div>

            <div v-if="selectedPayment === 'Quét Mã QR' && showQR" class="qr-panel">
              <h4>Quét Mã QR Để Thanh Toán</h4>
              <p>Mã QR chứa thông tin chuyển khoản cho giao dịch hiện tại.</p>
              <div class="qr-image-box">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=CineAI_Checkout_Booking"
                  alt="Mock QR Code Checkout" class="w-full h-full" />
              </div>
            </div>
          </div>
        </main>

        <aside class="summary-column" v-if="selectedShowtime">
          <div class="summary-card">
            <h3>Đơn Hàng</h3>

            <div class="summary-block">
              <div class="summary-row">
                <span>Rạp</span>
                <strong>{{ selectedShowtime.branchName }}</strong>
              </div>
              <div class="summary-row">
                <span>Suất chiếu</span>
                <strong>{{ selectedShowtime.time }} • {{ formatDate(selectedShowtime.date) }}</strong>
              </div>
              <div class="summary-row">
                <span>Phòng</span>
                <strong>{{ selectedShowtime.screenName }}</strong>
              </div>
            </div>

            <div class="summary-seats">
              <p>Ghế đã chọn</p>
              <div class="seat-tags">
                <span v-for="seat in selectedSeats" :key="seat.id">{{ seat.row }}{{ seat.number }}</span>
              </div>
            </div>

            <!-- --- KHU VỰC NHẬP MÃ GIẢM GIÁ (MỚI BỔ SUNG) --- -->
            <div class="voucher-box">
              <p class="voucher-label">Mã khuyến mãi / Voucher</p>
              <div class="voucher-input-group">
                <input type="text" v-model="voucherCode" :disabled="isVoucherApplied" placeholder="Nhập mã giảm giá..."
                  class="voucher-input" />
                <button v-if="!isVoucherApplied" @click="applyVoucher" class="voucher-btn">
                  Áp dụng
                </button>
                <button v-else @click="removeVoucher" class="voucher-btn remove-btn">
                  Bỏ chọn
                </button>
              </div>
              <p v-if="voucherError" class="voucher-msg error">{{ voucherError }}</p>
              <p v-if="voucherSuccessMsg" class="voucher-msg success">{{ voucherSuccessMsg }}</p>
            </div>

            <div class="summary-pricing">
              <div>
                <span>{{ selectedSeats.length }} vé x {{ selectedShowtime.price.toLocaleString('vi-VN') }}đ</span>
                <strong>{{ totalAmount.toLocaleString('vi-VN') }}đ</strong>
              </div>
              <div v-for="item in selectedCombos" :key="item.combo.id">
                <span>{{ item.combo.name }} x {{ item.quantity }}</span>
                <strong>{{ (Number(item.combo.price) * item.quantity).toLocaleString('vi-VN') }}đ</strong>
              </div>
              <div>
                <span>Phí dịch vụ</span>
                <strong>0đ</strong>
              </div>
              <div v-if="voucherDiscount > 0">
                <span>Giảm giá</span>
                <strong class="text-green-400">-{{ voucherDiscount.toLocaleString('vi-VN') }}đ</strong>
              </div>
              <div>
                <span>Phương thức</span>
                <strong>{{ selectedPayment }}</strong>
              </div>
            </div>

            <div class="summary-total">
              <span>Tổng thanh toán</span>
              <strong>{{ finalTotal.toLocaleString('vi-VN') }} VNĐ</strong>
            </div>

            <button @click="handleConfirmPayment"
              :disabled="processing || showtimeExpired || (selectedPayment === 'Ví VNPAY' && !!preparedVnpayPayment)"
              class="summary-next">
              <template v-if="processing">
                <span class="loading-state">
                  <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  Đang xác thực...
                </span>
              </template>
              <template v-else>
                {{ selectedPayment === 'Ví VNPAY' && preparedVnpayPayment ? 'Đã Lưu Yêu Cầu PENDING' : 'Xác Nhận Thanh Toán' }}
              </template>
            </button>
          </div>
        </aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
.checkout-shell {
  min-height: calc(100vh - 72px);
}

.checkout-hero {
  position: relative;
  overflow: hidden;
  border-radius: 1.35rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background-color: #1a1c1c;
  background-position: center;
  background-size: cover;
}

.checkout-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(18, 20, 20, 0.1) 0%, rgba(18, 20, 20, 0.28) 100%);
}

.checkout-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 250px minmax(0, 1fr) 300px;
  gap: 1.5rem;
  padding: 1.5rem;
  align-items: start;
}

.movie-column,
.summary-card,
.selection-panel {
  background: rgba(31, 31, 31, 0.74);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.2rem;
}

.movie-column {
  padding: 1rem;
}

.movie-poster {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
  border-radius: 1rem;
}

.movie-meta {
  margin-top: 1rem;
}

.movie-title {
  font-size: 1.45rem;
  line-height: 1.08;
  font-weight: 900;
  color: #fff;
}

.movie-badges {
  margin-top: 0.7rem;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: #d6d6d6;
  font-size: 0.88rem;
}

.movie-dot {
  color: rgba(255, 255, 255, 0.45);
}

.movie-rating {
  display: inline-flex;
  align-items: center;
  gap: 0.18rem;
}

.movie-price {
  margin-top: 0.75rem;
  color: #fbbf24;
  font-weight: 800;
}

.booking-stepper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin: 0.25rem 0 1rem;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  color: #9ca3af;
  font-size: 0.68rem;
  font-weight: 700;
}

.step span {
  width: 1.9rem;
  height: 1.9rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.12);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.step.active,
.step.done {
  color: #ffb4aa;
}

.step.active span,
.step.done span {
  background: #ff7a1a;
  color: #fff;
}

.step-line {
  width: 72px;
  height: 2px;
  background: rgba(255, 255, 255, 0.14);
}

.step-line.active {
  background: linear-gradient(90deg, #ff7a1a, #f59e0b);
}

.selection-panel {
  padding: 1.35rem;
}

.selection-header h1 {
  font-size: 2rem;
  line-height: 1.05;
  font-weight: 900;
  color: #fff;
}

.selection-header p {
  margin-top: 0.45rem;
  color: #c8c8c8;
  font-size: 0.95rem;
}

.methods-grid {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.method-card {
  position: relative;
  text-align: left;
  border-radius: 0.95rem;
  border: 1px solid rgba(255, 122, 26, 0.24);
  background: rgba(255, 255, 255, 0.03);
  padding: 0.95rem;
  min-height: 124px;
  transition: all 0.2s ease;
}

.method-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 122, 26, 0.5);
}

.method-icon {
  margin-bottom: 0.35rem;
  color: #ffd1a8;
}

.method-card h3 {
  color: #fff;
  font-weight: 800;
  font-size: 0.9rem;
}

.method-card p {
  color: #c7cad0;
  font-size: 0.8rem;
  margin-top: 0.28rem;
  line-height: 1.5;
}

.method-check {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  color: #ff7a1a;
  font-size: 1.1rem;
}

.method-active {
  border-color: rgba(255, 122, 26, 0.65);
  background: rgba(255, 122, 26, 0.12);
}

.method-note {
  margin-top: 1rem;
  border-radius: 0.8rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.75rem 0.9rem;
  color: #c7cad0;
  font-size: 0.9rem;
}

.qr-panel {
  margin-top: 1rem;
  border-radius: 0.95rem;
  border: 1px solid rgba(255, 122, 26, 0.28);
  background: rgba(255, 255, 255, 0.04);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.5rem;
}

.qr-panel h4 {
  color: #fff;
  font-weight: 800;
}

.qr-panel p {
  color: #c7cad0;
  font-size: 0.85rem;
}

.qr-image-box {
  margin-top: 0.45rem;
  width: 190px;
  height: 190px;
  border-radius: 0.85rem;
  background: #fff;
  padding: 0.5rem;
}

.summary-card {
  padding: 1.2rem;
}

.summary-card h3 {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 900;
  text-transform: uppercase;
}

.summary-block {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.14);
  display: grid;
  gap: 0.85rem;
}

.summary-row {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.summary-row span {
  color: #aeb3bb;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-row strong {
  color: #fff;
  font-size: 0.92rem;
}

.summary-seats {
  margin-top: 1rem;
}

.summary-seats p {
  color: #aeb3bb;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.seat-tags {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.seat-tags span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  border-radius: 0.6rem;
  padding: 0 0.6rem;
  background: rgba(255, 122, 26, 0.14);
  color: #ffd1a8;
  font-size: 0.76rem;
  font-weight: 700;
}

/* STYLES MỚI CHO VOUCHER */
.voucher-box {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.14);
}

.voucher-label {
  color: #aeb3bb;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.4rem;
}

.voucher-input-group {
  display: flex;
  gap: 0.5rem;
}

.voucher-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 0.6rem;
  padding: 0.45rem 0.65rem;
  color: #fff;
  font-size: 0.82rem;
  text-transform: uppercase;
  outline: none;
}

.voucher-input:focus {
  border-color: #ff7a1a;
}

.voucher-input:disabled {
  opacity: 0.6;
}

.voucher-btn {
  background: #ff7a1a;
  color: #fff;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0 0.75rem;
  border-radius: 0.6rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.voucher-btn:hover {
  background: #e0650d;
}

.voucher-btn.remove-btn {
  background: rgba(255, 255, 255, 0.15);
  color: #f87171;
}

.voucher-btn.remove-btn:hover {
  background: rgba(239, 68, 68, 0.2);
}

.voucher-msg {
  font-size: 0.75rem;
  margin-top: 0.35rem;
}

.voucher-msg.error {
  color: #f87171;
}

.voucher-msg.success {
  color: #4ade80;
}

.summary-pricing {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.14);
  display: grid;
  gap: 0.8rem;
}

.summary-pricing>div {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}

.summary-pricing span {
  color: #aeb3bb;
  font-size: 0.82rem;
}

.summary-pricing strong {
  color: #fff;
  font-size: 0.9rem;
  font-weight: 700;
}

.summary-total {
  margin-top: 1rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.14);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.summary-total span {
  color: #aeb3bb;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-total strong {
  color: #fff;
  font-size: 1.2rem;
  font-weight: 900;
}

.summary-next {
  margin-top: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 44px;
  border-radius: 0.8rem;
  background: #ff7a1a;
  color: #fff;
  font-weight: 800;
  transition: all 0.2s ease;
}

.summary-next:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.loading-state {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

@media (max-width: 1200px) {
  .checkout-grid {
    grid-template-columns: 240px minmax(0, 1fr);
  }

  .summary-column {
    grid-column: 1 / -1;
  }
}

@media (max-width: 992px) {
  .checkout-grid {
    grid-template-columns: 1fr;
  }

  .methods-grid {
    grid-template-columns: 1fr;
  }

  .booking-stepper {
    overflow-x: auto;
    justify-content: flex-start;
    padding-bottom: 0.3rem;
  }

  .step-line {
    min-width: 44px;
  }
}
</style>

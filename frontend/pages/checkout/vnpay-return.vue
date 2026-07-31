<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { checkoutService } from '~/services/api'
import { useTicketsStore } from '~/store/tickets'

definePageMeta({ layout: 'default' })

const route = useRoute()
const ticketsStore = useTicketsStore()
const loading = ref(true)
const success = ref(false)
const message = ref('Đang xác thực giao dịch VNPay...')
const paymentId = ref('')
const transactionRef = ref('')
const paymentStatus = ref('')

onMounted(async () => {
  try {
    const result = await checkoutService.verifyVnpayCallback(route.query as Record<string, string | string[]>)
    success.value = result.success
    paymentId.value = result.payment_id || ''
    transactionRef.value = result.transaction_ref || String(route.query.vnp_TxnRef || '')
    paymentStatus.value = result.payment_status || ''
    message.value = result.success
      ? 'VNPAY đã xác nhận giao dịch. Vé của bạn đã được phát hành.'
      : result.message
    if (result.success) ticketsStore.clearSelection()
  } catch (error: any) {
    message.value = error?.message || 'Không thể xác thực giao dịch VNPay.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="mx-auto flex min-h-[60vh] max-w-xl items-center px-4 py-10">
    <section class="w-full rounded-2xl border border-white/10 bg-surface-container p-8 text-center shadow-xl">
      <span class="material-symbols-outlined text-5xl" :class="loading ? 'text-primary-container' : success ? 'text-green-400' : 'text-red-400'">
        {{ loading ? 'hourglass_top' : success ? 'check_circle' : 'cancel' }}
      </span>
      <h1 class="mt-4 text-2xl font-bold">{{ loading ? 'Đang xử lý thanh toán' : success ? 'Thanh toán thành công' : 'Thanh toán chưa thành công' }}</h1>
      <p class="mt-3 text-on-surface-variant">{{ message }}</p>
      <dl v-if="!loading && (transactionRef || paymentId || paymentStatus)" class="mt-5 space-y-2 rounded-xl bg-black/20 p-4 text-left text-sm">
        <div v-if="transactionRef" class="flex justify-between gap-4">
          <dt class="text-on-surface-variant">Mã tham chiếu</dt>
          <dd class="break-all font-mono">{{ transactionRef }}</dd>
        </div>
        <div v-if="paymentId" class="flex justify-between gap-4">
          <dt class="text-on-surface-variant">Mã thanh toán</dt>
          <dd class="break-all font-mono">{{ paymentId }}</dd>
        </div>
        <div v-if="paymentStatus" class="flex justify-between gap-4">
          <dt class="text-on-surface-variant">Trạng thái</dt>
          <dd class="font-bold">{{ paymentStatus }}</dd>
        </div>
      </dl>
      <div v-if="!loading" class="mt-7 flex flex-wrap justify-center gap-3">
        <NuxtLink :to="success ? '/profile/tickets' : '/checkout/payment'" class="inline-block rounded-xl bg-primary-container px-5 py-3 font-bold text-on-primary-container">
          {{ success ? 'Xem vé của tôi' : 'Quay lại thanh toán' }}
        </NuxtLink>
        <NuxtLink to="/" class="inline-block rounded-xl border border-white/15 px-5 py-3 font-bold">
          Về trang chủ
        </NuxtLink>
      </div>
    </section>
  </main>
</template>

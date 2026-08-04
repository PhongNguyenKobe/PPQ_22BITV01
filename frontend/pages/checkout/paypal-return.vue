<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useTicketsStore } from '~/store/tickets'

definePageMeta({ layout: 'default' })

const route = useRoute()
const ticketsStore = useTicketsStore()
const loading = ref(true)
const success = ref(false)
const message = ref('Đang xử lý kết quả thanh toán PayPal...')
const paymentId = ref('')
const resultStatus = ref('')

onMounted(() => {
  try {
    const result = route.query.result as string
    const id = route.query.payment_id as string
    const errMsg = route.query.message as string

    paymentId.value = id || ''
    resultStatus.value = result || ''

    if (result === 'success') {
      success.value = true
      message.value = 'PayPal đã xác nhận giao dịch thành công. Vé của bạn đã được phát hành.'
      ticketsStore.clearSelection()
    } else if (result === 'cancelled') {
      success.value = false
      message.value = 'Bạn đã hủy yêu cầu thanh toán qua PayPal.'
    } else {
      success.value = false
      message.value = errMsg || 'Giao dịch qua PayPal không thành công hoặc đã bị từ chối.'
    }
  } catch (error: any) {
    message.value = error?.message || 'Không thể xử lý kết quả thanh toán từ PayPal.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="mx-auto flex min-h-[60vh] max-w-xl items-center px-4 py-10">
    <section class="w-full rounded-2xl border border-white/10 bg-surface-container p-8 text-center shadow-xl">
      <span class="material-symbols-outlined text-5xl" :class="loading ? 'text-primary-container' : success ? 'text-green-400' : 'text-red-400'">
        {{ loading ? 'hourglass_top' : success ? 'check_circle' : (resultStatus === 'cancelled' ? 'cancel' : 'error') }}
      </span>
      <h1 class="mt-4 text-2xl font-bold">
        {{ loading ? 'Đang xử lý thanh toán' : success ? 'Thanh toán thành công' : (resultStatus === 'cancelled' ? 'Đã hủy thanh toán' : 'Thanh toán thất bại') }}
      </h1>
      <p class="mt-3 text-on-surface-variant">{{ message }}</p>
      <dl v-if="!loading && paymentId" class="mt-5 space-y-2 rounded-xl bg-black/20 p-4 text-left text-sm">
        <div class="flex justify-between gap-4">
          <dt class="text-on-surface-variant">Mã thanh toán</dt>
          <dd class="break-all font-mono">{{ paymentId }}</dd>
        </div>
        <div class="flex justify-between gap-4">
          <dt class="text-on-surface-variant">Phương thức</dt>
          <dd class="font-bold text-blue-400">Paypal</dd>
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

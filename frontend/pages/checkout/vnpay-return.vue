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

onMounted(async () => {
  try {
    const result = await checkoutService.verifyVnpayCallback(route.query as Record<string, string | string[]>)
    success.value = result.success
    message.value = result.message
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
      <NuxtLink v-if="!loading" :to="success ? '/profile/tickets' : '/checkout/payment'" class="mt-7 inline-block rounded-xl bg-primary-container px-5 py-3 font-bold text-on-primary-container">
        {{ success ? 'Xem vé của tôi' : 'Quay lại thanh toán' }}
      </NuxtLink>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'

definePageMeta({ layout: 'default', middleware: ['auth'] })

const ticketsStore = useTicketsStore()
const { selectedShowtime, selectedSeats } = storeToRefs(ticketsStore)

onMounted(() => {
  if (!selectedShowtime.value || selectedSeats.value.length === 0) navigateTo('/products')
})
</script>

<template>
  <section class="mx-auto flex min-h-[65vh] max-w-3xl items-center px-6 py-20 text-center">
    <div class="w-full rounded-3xl border border-amber-400/25 bg-amber-400/5 p-8 md:p-12">
      <span class="material-symbols-outlined text-5xl text-amber-300">local_dining</span>
      <h1 class="mt-5 text-3xl font-black text-on-surface">Combo bắp nước sẽ phát triển sau</h1>
      <p class="mx-auto mt-4 max-w-xl leading-7 text-on-surface-variant">
        Dữ liệu combo, tồn kho và thanh toán combo chưa được kết nối. Bạn có thể bỏ qua bước này
        và tiếp tục thanh toán vé; tổng tiền sẽ chỉ gồm các ghế đã chọn.
      </p>
      <div class="mt-7 flex flex-wrap justify-center gap-3">
        <NuxtLink to="/checkout/seat" class="rounded-xl border border-white/15 px-6 py-3 font-bold text-on-surface">
          Quay lại chọn ghế
        </NuxtLink>
        <NuxtLink to="/checkout/payment" class="rounded-xl bg-primary-container px-6 py-3 font-bold text-white">
          Tiếp tục thanh toán vé
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

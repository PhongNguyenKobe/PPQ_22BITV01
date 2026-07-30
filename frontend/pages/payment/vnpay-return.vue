<script setup lang="ts">
definePageMeta({ layout: 'default' })
const route = useRoute()
const success = computed(() => route.query.result === 'success')
</script>

<template>
  <main class="mx-auto flex min-h-[65vh] max-w-xl items-center px-5 py-16">
    <section class="w-full rounded-3xl border border-white/10 bg-[#1a1c1c] p-8 text-center shadow-2xl">
      <span class="material-symbols-outlined text-6xl" :class="success ? 'text-emerald-400' : 'text-rose-400'">
        {{ success ? 'check_circle' : 'cancel' }}
      </span>
      <h1 class="mt-4 text-2xl font-black">{{ success ? 'Thanh toán thành công' : 'Thanh toán chưa thành công' }}</h1>
      <p class="mt-2 text-on-surface-variant">
        {{ success ? 'VNPAY đã xác nhận giao dịch. Vé của bạn đã được phát hành.' : 'Giao dịch bị hủy, thất bại hoặc chưa được VNPAY xác nhận.' }}
      </p>
      <div class="mt-7 flex justify-center gap-3">
        <NuxtLink to="/profile/tickets" class="action-primary">Xem vé của tôi</NuxtLink>
        <NuxtLink to="/showtimes" class="action-ghost">Chọn suất khác</NuxtLink>
      </div>
    </section>
  </main>
</template>

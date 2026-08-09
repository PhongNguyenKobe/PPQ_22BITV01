<script setup lang="ts">
definePageMeta({ layout: 'default' })
</script>

<template>
  <section class="mx-auto flex min-h-[65vh] max-w-3xl items-center px-6 py-20 text-center">
    <div class="w-full rounded-3xl border border-amber-400/25 bg-amber-400/5 p-8 md:p-12">
      <span class="material-symbols-outlined text-5xl text-amber-300">construction</span>
      <h1 class="mt-5 text-3xl font-black text-on-surface">Giỏ hàng đang được phát triển</h1>
      <p class="mx-auto mt-4 max-w-xl leading-7 text-on-surface-variant">
        Chức năng mua sản phẩm và thanh toán đơn hàng chưa kết nối với hệ thống đơn hàng thật.
        Hiện tại CineAI chỉ hỗ trợ đặt và thanh toán vé xem phim.
      </p>
      <NuxtLink to="/phim" class="mt-7 inline-flex rounded-xl bg-primary-container px-6 py-3 font-bold text-white">
        Xem phim và đặt vé
      </NuxtLink>
    </div>
  </section>
</template>

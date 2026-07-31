<script setup lang="ts">
definePageMeta({ layout: 'default' })
</script>

<template>
  <section class="mx-auto flex min-h-[65vh] max-w-3xl items-center px-6 py-20 text-center">
    <div class="w-full rounded-3xl border border-amber-400/25 bg-amber-400/5 p-10">
      <span class="material-symbols-outlined text-5xl text-amber-300">construction</span>
      <h1 class="mt-4 text-3xl font-black text-on-surface">Trang mua sản phẩm chưa phát triển</h1>
      <p class="mt-3 text-on-surface-variant">Route cũ này chưa kết nối đơn hàng và thanh toán thật.</p>
      <NuxtLink to="/products" class="mt-7 inline-flex rounded-xl bg-primary-container px-6 py-3 font-bold text-white">
        Quay lại danh sách phim
      </NuxtLink>
    </div>
  </section>
</template>

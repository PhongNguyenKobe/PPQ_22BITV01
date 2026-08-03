<script setup lang="ts">
import { onBeforeMount } from 'vue'

definePageMeta({
  layout: 'default'
})

onBeforeMount(() => {
  navigateTo('/login')
})
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="text-center">
      <p class="text-on-surface-variant text-sm mb-4">Đang chuyển hướng tới trang Đăng nhập & Đăng ký...</p>
      <NuxtLink to="/login" class="text-primary-container font-bold hover:underline">Nhấp vào đây nếu không tự động chuyển hướng</NuxtLink>
    </div>
  </div>
</template>

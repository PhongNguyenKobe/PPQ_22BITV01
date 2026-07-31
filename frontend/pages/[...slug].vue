<script setup lang="ts">
const route = useRoute()
const futurePages: Record<string, string> = {
  support: 'Trung tâm hỗ trợ',
  terms: 'Điều khoản dịch vụ',
  privacy: 'Chính sách bảo mật',
  contact: 'Liên hệ',
}
const slug = Array.isArray(route.params.slug) ? route.params.slug.join('/') : String(route.params.slug || '')
const futureTitle = futurePages[slug]
</script>

<template>
  <section class="py-24 text-center max-w-container-max mx-auto px-6">
    <h1 class="font-headline-lg text-4xl font-bold text-on-surface mb-4">{{ futureTitle || '404' }}</h1>
    <p class="text-on-surface-variant mb-8">
      {{ futureTitle ? 'Nội dung này tạm thời chưa phát triển xong.' : 'Trang bạn tìm không tồn tại.' }}
    </p>
    <NuxtLink to="/" class="bg-primary-container text-on-primary-container px-6 py-3 rounded-xl font-bold red-glow-hover">
      Về trang chủ
    </NuxtLink>
  </section>
</template>

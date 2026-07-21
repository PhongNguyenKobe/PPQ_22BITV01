<script setup lang="ts">
import products from '@/assets/data/products.json'

const route = useRoute()
const product = computed(() =>
  products.find((p) => p.id === Number(route.params.id))
)
</script>

<template>
  <div v-if="!product" class="py-16 text-center text-on-surface-variant">
    Không tìm thấy sản phẩm.
  </div>

  <section v-else class="py-16 max-w-container-max mx-auto px-6 md:px-margin-desktop grid md:grid-cols-2 gap-10">
    <img
      :src="product.imageUrl"
      :alt="product.name"
      class="w-full rounded-2xl object-cover aspect-[2/3]"
    />

    <div>
      <span class="text-xs font-bold uppercase tracking-wide text-primary-container">
        {{ product.category }}
      </span>
      <h1 class="font-headline-lg text-3xl font-bold text-on-surface mt-2 mb-4">
        {{ product.name }}
      </h1>
      <p class="text-on-surface-variant leading-relaxed mb-6">
        {{ product.description }}
      </p>
      <p class="text-2xl font-bold text-on-surface mb-8">
        {{ new Intl.NumberFormat('vi-VN').format(product.price * 1000) }}₫
      </p>

      <button class="bg-primary-container text-on-primary-container px-8 py-3 rounded-xl font-bold red-glow-hover">
        Thêm vào giỏ
      </button>
    </div>
  </section>
</template>
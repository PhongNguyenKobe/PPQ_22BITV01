<script setup lang="ts">
import { useProductsStore } from '~/store/products'
import { useCartStore } from '~/store/cart'

definePageMeta({ layout: 'default' })

const route = useRoute()
const productsStore = useProductsStore()
const cartStore = useCartStore()

// Nếu user vào thẳng URL /products/:id (chưa từng ghé /products), store vẫn tự fetch
await productsStore.fetchProducts()

const product = computed(() =>
  productsStore.products.find((p) => p.id === Number(route.params.id))
)

function addToCart() {
  if (product.value) cartStore.addItem(product.value)
}
</script>

<template>
  <div v-if="!product" class="py-16 text-center text-on-surface-variant">
    Không tìm thấy sản phẩm.
    <NuxtLink to="/products" class="text-primary-container underline block mt-2">← Quay lại danh sách</NuxtLink>
  </div>

  <section v-else class="py-16 max-w-container-max mx-auto px-6 md:px-margin-desktop">
    <NuxtLink to="/products" class="inline-block mb-6 text-sm text-on-surface-variant hover:text-primary-container">
      ← Quay lại danh sách
    </NuxtLink>

    <div class="grid md:grid-cols-2 gap-10">
      <img :src="product.imageUrl" :alt="product.name" class="w-full rounded-2xl object-cover aspect-[2/3]" />

      <div>
        <span class="text-xs font-bold uppercase tracking-wide text-primary-container">{{ product.category }}</span>
        <h1 class="font-headline-lg text-3xl font-bold text-on-surface mt-2 mb-4">{{ product.name }}</h1>
        <p class="text-on-surface-variant leading-relaxed mb-6">{{ product.description }}</p>
        <p class="text-2xl font-bold text-on-surface mb-8">
          {{ new Intl.NumberFormat('vi-VN').format(product.price * 1000) }}₫
        </p>
        <button
          @click="addToCart"
          class="bg-primary-container text-on-primary-container px-8 py-3 rounded-xl font-bold red-glow-hover"
        >
          Thêm vào giỏ
        </button>
      </div>
    </div>
  </section>
</template>
<script setup lang="ts">
import ProductCard from './ProductCard.vue'
import { useProductsStore } from '~/store/products'

const productsStore = useProductsStore()

await productsStore.fetchProducts()
</script>

<template>
  <div class="product-carousel">
    <ProductCard
      v-for="product in productsStore.products.slice(0, 8)"
      :key="product.id"
      v-bind="product"
      class="snap-start shrink-0"
    />
  </div>
</template>

<style scoped>
.product-carousel {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding-bottom: 8px;
}

.product-carousel::-webkit-scrollbar {
  height: 6px;
}

.product-carousel::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  border-radius: 3px;
}
</style>
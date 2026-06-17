<script setup lang="ts">
import ProductCard from './ProductCard.vue'
import products from '../data/products.json'
</script>

<template>
  <section class="section container" id="products">
    <div class="section__heading">
      <h2>Vé & Combo nổi bật</h2>
      <a class="section__more" href="#products">
        Xem tất cả <span class="material-symbols-outlined">chevron_right</span>
      </a>
    </div>

    <div class="product-scroll">
      <ProductCard
        v-for="product in products"
        :key="product.id"
        v-bind="product"
      />
    </div>
  </section>
</template>

<style scoped>
.product-scroll {
  display: flex;
  flex-direction: row;
  gap: 16px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 12px;
  cursor: grab;
}

.product-scroll:active {
  cursor: grabbing;
}

/* Ẩn scrollbar nhưng vẫn scroll được */
.product-scroll::-webkit-scrollbar {
  height: 4px;
}
.product-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.product-scroll::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.2);
  border-radius: 999px;
}
</style>
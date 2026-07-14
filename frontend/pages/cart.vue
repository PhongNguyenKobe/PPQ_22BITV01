<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useCartStore } from '~/store/cart'

definePageMeta({ layout: 'default' })

const cartStore = useCartStore()
const { items, total } = storeToRefs(cartStore)

function checkout() {
  alert('Chức năng thanh toán sẽ làm ở session sau.')
}
</script>

<template>
  <section class="py-16 max-w-container-max mx-auto px-6 md:px-margin-desktop">
    <h2 class="font-headline-lg text-3xl font-bold text-on-surface mb-8">Giỏ hàng</h2>

    <div v-if="items.length === 0" class="text-center py-10 text-on-surface-variant">
      Giỏ hàng đang trống.
      <NuxtLink to="/products" class="text-primary-container underline block mt-2">Tiếp tục mua sắm</NuxtLink>
    </div>

    <template v-else>
      <div class="space-y-4 mb-8">
        <div v-for="item in items" :key="item.id" class="flex items-center gap-4 bg-surface-container-low border border-glass-stroke rounded-xl p-4">
          <img :src="item.imageUrl" :alt="item.name" class="w-16 h-24 object-cover rounded-lg" />
          <div class="flex-1">
            <h3 class="font-bold text-on-surface">{{ item.name }}</h3>
            <p class="text-sm text-on-surface-variant">Số lượng: {{ item.qty }}</p>
          </div>
          <p class="font-bold text-on-surface">{{ new Intl.NumberFormat('vi-VN').format(item.price * item.qty * 1000) }}₫</p>
          <button @click="cartStore.removeItem(item.id)" class="text-red-500 text-sm hover:underline">Xóa</button>
        </div>
      </div>

      <div class="flex items-center justify-between border-t border-glass-stroke pt-6">
        <p class="text-xl font-bold text-on-surface">Tổng: {{ new Intl.NumberFormat('vi-VN').format(total * 1000) }}₫</p>
        <div class="flex gap-3">
          <NuxtLink to="/products" class="px-6 py-3 rounded-xl border border-glass-stroke hover:bg-white/10 transition">Tiếp tục mua sắm</NuxtLink>
          <button @click="checkout" class="bg-primary-container text-on-primary-container px-6 py-3 rounded-xl font-bold red-glow-hover">Thanh toán</button>
        </div>
      </div>
    </template>
  </section>
</template>
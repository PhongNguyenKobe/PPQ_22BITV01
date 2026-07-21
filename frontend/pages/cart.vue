<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useCartStore } from '~/store/cart'
import { useUserStore } from '~/store/user'

definePageMeta({ layout: 'default' })

const cartStore = useCartStore()
const userStore = useUserStore()
const { items, total } = storeToRefs(cartStore)
const { isAuthenticated, currentUser } = storeToRefs(userStore)

const isCheckingOut = ref(false)
const orderId = ref<string | null>(null)

async function checkout() {
  if (items.value.length === 0) return

  if (!isAuthenticated.value || !currentUser.value) {
    navigateTo('/login')
    return
  }

  isCheckingOut.value = true
  await new Promise((resolve) => setTimeout(resolve, 1200))

  orderId.value = `DH-${Date.now().toString().slice(-6)}`
  cartStore.clearCart()
  isCheckingOut.value = false
}
</script>

<template>
  <section class="py-16 max-w-container-max mx-auto px-6 md:px-margin-desktop">
    <h2 class="font-headline-lg text-3xl font-bold text-on-surface mb-8">Giỏ hàng</h2>

    <div v-if="items.length === 0" class="text-center py-10 text-on-surface-variant">
      <div v-if="orderId" class="rounded-2xl border border-primary-container/20 bg-primary-container/10 p-6 max-w-xl mx-auto">
        <p class="text-lg font-semibold text-on-surface">Đặt hàng thành công!</p>
        <p class="mt-2">Mã đơn hàng của bạn là <span class="font-bold text-primary-container">{{ orderId }}</span>.</p>
        <NuxtLink to="/products" class="text-primary-container underline block mt-4">Tiếp tục mua sắm</NuxtLink>
      </div>
      <template v-else>
        Giỏ hàng đang trống.
        <NuxtLink to="/products" class="text-primary-container underline block mt-2">Tiếp tục mua sắm</NuxtLink>
      </template>
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

      <div class="flex flex-col gap-4 border-t border-glass-stroke pt-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-xl font-bold text-on-surface">Tổng: {{ new Intl.NumberFormat('vi-VN').format(total * 1000) }}₫</p>
          <p class="text-sm text-on-surface-variant mt-1">Đơn hàng sẽ được xác nhận sau khi bạn nhấn thanh toán.</p>
        </div>
        <div class="flex gap-3">
          <NuxtLink to="/products" class="px-6 py-3 rounded-xl border border-glass-stroke hover:bg-white/10 transition">Tiếp tục mua sắm</NuxtLink>
          <button @click="checkout" :disabled="isCheckingOut" class="bg-primary-container text-on-primary-container px-6 py-3 rounded-xl font-bold red-glow-hover disabled:opacity-60 disabled:cursor-not-allowed">
            <span v-if="isCheckingOut">Đang xử lý...</span>
            <span v-else>Thanh toán</span>
          </button>
        </div>
      </div>
    </template>
  </section>
</template>
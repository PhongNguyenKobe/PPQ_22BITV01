<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useCartStore } from '~/store/cart'

definePageMeta({ layout: 'default' })

const cartStore = useCartStore()
const { items, totalPrice, totalQuantity } = storeToRefs(cartStore)

function updateQuantity(itemId: string, event: Event) {
    const target = event.target as HTMLInputElement
    const quantity = Number(target.value)
    cartStore.updateQuantity(itemId, quantity)
}

function handleClearCart() {
    cartStore.clearCart()
}
</script>

<template>
    <div class="min-h-screen pt-24 pb-16">
        <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">
            <div class="flex flex-col md:flex-row items-start justify-between gap-6 mb-8">
                <div>
                    <h1 class="font-headline-xl text-headline-xl text-on-surface">Giỏ hàng của bạn</h1>
                    <p class="text-on-surface-variant mt-2">Quản lý lựa chọn vé và kiểm tra tổng chi phí trước khi đặt
                        hàng.</p>
                </div>
                <div class="rounded-3xl bg-surface-container-high border border-white/10 px-5 py-4">
                    <p class="text-sm text-on-surface-variant">Tổng sản phẩm</p>
                    <p class="mt-1 text-2xl font-bold text-on-surface">{{ totalQuantity }}</p>
                </div>
            </div>

            <div v-if="items.length === 0"
                class="rounded-3xl border border-white/10 bg-surface-container p-12 text-center">
                <span class="material-symbols-outlined text-6xl text-on-surface-variant mb-4">shopping_cart</span>
                <p class="text-on-surface font-semibold text-lg">Giỏ hàng trống</p>
                <NuxtLink to="/movies"
                    class="mt-4 inline-flex items-center gap-2 text-primary-container font-semibold hover:underline">
                    <span class="material-symbols-outlined">arrow_back</span>
                    Quay lại danh sách phim
                </NuxtLink>
            </div>

            <div v-else class="grid grid-cols-1 lg:grid-cols-[1.6fr_1fr] gap-8">
                <div class="space-y-4">
                    <div v-for="item in items" :key="item.id"
                        class="rounded-3xl border border-white/10 bg-surface-container p-6 flex flex-col gap-4 md:flex-row md:items-center">
                        <img :src="item.poster" :alt="item.title"
                            class="w-full md:w-32 h-40 rounded-3xl object-cover" />
                        <div class="flex-1 space-y-3">
                            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                                <div>
                                    <h2 class="font-bold text-on-surface">{{ item.title }}</h2>
                                    <p class="text-sm text-on-surface-variant">{{ item.showtime || 'Vé xem phim' }}</p>
                                </div>
                                <button @click="cartStore.removeFromCart(item.id)"
                                    class="text-red-400 hover:text-red-300 font-semibold text-sm">Xóa</button>
                            </div>
                            <div class="flex flex-wrap items-center gap-4 justify-between">
                                <div class="flex items-center gap-2">
                                    <label class="text-sm text-on-surface-variant">Số lượng:</label>
                                    <input type="number" min="1" :value="item.quantity"
                                        @input="event => updateQuantity(item.id, event)"
                                        class="w-20 rounded-xl border border-white/10 bg-surface px-3 py-2 text-on-surface outline-none" />
                                </div>
                                <p class="text-sm font-semibold text-on-surface">{{ item.price.toLocaleString() }} VNĐ /
                                    vé</p>
                                <p class="text-base font-bold text-on-surface">Thành tiền: {{ (item.price *
                                    item.quantity).toLocaleString() }} VNĐ</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="rounded-3xl border border-white/10 bg-surface-container p-6 space-y-6">
                    <div>
                        <p class="text-sm text-on-surface-variant">Tổng chi phí</p>
                        <p class="mt-2 text-3xl font-bold text-on-surface">{{ totalPrice.toLocaleString() }} VNĐ</p>
                    </div>
                    <button @click="handleClearCart"
                        class="w-full rounded-3xl bg-red-500/90 text-white py-4 font-bold hover:bg-red-500 transition-all">Xóa
                        toàn bộ giỏ</button>
                    <NuxtLink to="/checkout/seat"
                        class="w-full inline-flex items-center justify-center rounded-3xl bg-primary-container text-on-primary-container py-4 font-bold hover:brightness-110 transition-all">
                        Tiếp tục đặt vé
                    </NuxtLink>
                </div>
            </div>
        </div>
    </div>
</template>

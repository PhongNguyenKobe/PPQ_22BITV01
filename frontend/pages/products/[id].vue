<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useProductsStore } from '~/store/products'
import { useTicketsStore } from '~/store/tickets'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'default'
})

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()
const ticketsStore = useTicketsStore()
const userStore = useUserStore()

const { products } = storeToRefs(productsStore)
const loading = ref(true)

// Fetch products if not already loaded
onMounted(async () => {
  try {
    if (products.value.length === 0) {
      await productsStore.fetchProducts()
    }
    loading.value = false
  } catch (error) {
    console.error('Lỗi tải sản phẩm:', error)
    loading.value = false
  }
})

// Get current product
const currentProduct = computed(() => {
  const id = parseInt(route.params.id as string)
  return products.value.find((p) => p.id === id)
})

// Start booking process
function startBooking() {
  if (!currentProduct.value) return
  
  if (!userStore.isAuthenticated) {
    return router.push('/login')
  }
  
  // Set movie in tickets store
  ticketsStore.selectMovie({
    id: currentProduct.value.id,
    name: currentProduct.value.name
  })
  
  // Navigate to cinema selection
  router.push('/checkout/cinema')
}
</script>

<template>
  <!-- Loading -->
  <div v-if="loading" class="py-20 text-center text-on-surface">
    Đang tải chi tiết phim...
  </div>

  <!-- Not found -->
  <div v-else-if="!currentProduct" class="py-20 text-center">
    <p class="text-on-surface mb-4">Không tìm thấy phim</p>
    <NuxtLink to="/products" class="text-primary font-bold">
      ← Quay lại danh sách
    </NuxtLink>
  </div>

  <!-- Product detail -->
  <section v-else class="py-16 max-w-container-max mx-auto px-6 md:px-margin-desktop">
    <!-- Breadcrumb -->
    <div class="mb-6 flex items-center gap-2 text-sm text-on-surface-variant">
      <NuxtLink to="/products" class="hover:text-primary">Sản phẩm</NuxtLink>
      <span class="material-symbols-outlined text-base">chevron_right</span>
      <span class="text-on-surface">{{ currentProduct.name }}</span>
    </div>

    <!-- Product detail layout -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
      <!-- Image section -->
      <div class="flex items-center justify-center">
        <img
          :src="currentProduct.imageUrl"
          :alt="currentProduct.name"
          class="w-full max-w-sm rounded-xl object-cover shadow-lg"
        />
      </div>

      <!-- Info section -->
      <div class="flex flex-col justify-start">
        <!-- Title -->
        <h1 class="text-3xl md:text-4xl font-bold text-on-surface mb-2">
          {{ currentProduct.name }}
        </h1>

        <!-- Rating & Category -->
        <div class="flex items-center gap-4 mb-6 pb-6 border-b border-outline-variant">
          <div v-if="currentProduct.rating" class="flex items-center gap-1">
            <span class="material-symbols-outlined text-yellow-500">star</span>
            <span class="text-on-surface font-semibold">{{ currentProduct.rating.toFixed(1) }}</span>
          </div>
          <span class="px-3 py-1 bg-primary-container text-primary rounded-full text-sm font-bold">
            {{ currentProduct.category }}
          </span>
        </div>

        <!-- Description -->
        <div class="mb-8">
          <h3 class="text-lg font-bold text-on-surface mb-3">Mô tả Phim</h3>
          <p class="text-on-surface-variant leading-relaxed">
            {{ currentProduct.description || 'Không có mô tả chi tiết' }}
          </p>
        </div>

        <!-- Call to action buttons -->
        <div class="flex gap-4 flex-col md:flex-row mt-auto">
          <!-- Xem trailer button -->
          <button
            class="flex-1 px-6 py-3 rounded-lg font-bold border-2 border-outline-variant bg-surface-container-high text-on-surface hover:border-primary hover:text-primary transition flex items-center justify-center gap-2"
          >
            <span class="material-symbols-outlined">play_circle</span>
            Xem Trailer
          </button>

          <!-- Đặt vé button -->
          <button
            @click="startBooking"
            class="flex-1 px-6 py-3 rounded-lg font-bold bg-primary text-on-primary hover:brightness-110 transition flex items-center justify-center gap-2"
          >
            <span class="material-symbols-outlined">confirmation_number</span>
            Đặt Vé
          </button>
        </div>

        <!-- Additional info -->
        <div class="mt-8 pt-6 border-t border-outline-variant space-y-3 text-sm text-on-surface-variant">
          <div class="flex items-start gap-3">
            <span class="material-symbols-outlined text-on-surface mt-0.5">info</span>
            <span>Chọn rạp, suất chiếu và ghế yêu thích của bạn</span>
          </div>
          <div class="flex items-start gap-3">
            <span class="material-symbols-outlined text-on-surface mt-0.5">lock</span>
            <span>Thanh toán an toàn qua nhiều phương thức</span>
          </div>
          <div class="flex items-start gap-3">
            <span class="material-symbols-outlined text-on-surface mt-0.5">confirmation_number</span>
            <span>Nhận vé ngay sau khi thanh toán thành công</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
button {
  transition: all 0.2s ease;
}
</style>

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
  const id = String(route.params.id as string)
  return products.value.find((p) => String(p.id) === id)
})

const trailerHref = computed(() => {
  if (!currentProduct.value) return '#'
  return currentProduct.value.trailerUrl || `https://www.youtube.com/results?search_query=${encodeURIComponent(`${currentProduct.value.name} trailer`)}`
})

const backgroundStyle = computed(() => {
  if (!currentProduct.value) return {}
  return {
    backgroundImage: `linear-gradient(90deg, rgba(18,20,20,0.96) 0%, rgba(18,20,20,0.82) 40%, rgba(18,20,20,0.55) 68%, rgba(18,20,20,0.76) 100%), url('${currentProduct.value.imageUrl}')`,
  }
})

const formattedPrice = computed(() => {
  if (!currentProduct.value) return ''
  return new Intl.NumberFormat('vi-VN').format(currentProduct.value.price * 1000) + 'đ'
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
    name: currentProduct.value.name,
    backendMovieId: currentProduct.value.backendMovieId || null,
    imageUrl: currentProduct.value.imageUrl,
    category: currentProduct.value.category,
    price: currentProduct.value.price,
    rating: currentProduct.value.rating || null,
    description: currentProduct.value.description,
    trailerUrl: currentProduct.value.trailerUrl || null,
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

  <section v-else class="detail-shell py-6 px-3 sm:px-5 md:px-8">
    <div class="detail-hero max-w-[1500px] mx-auto" :style="backgroundStyle">
      <div class="detail-overlay"></div>

      <div class="detail-topbar">
        <NuxtLink to="/products" class="detail-backlink">
          <span class="material-symbols-outlined text-base">arrow_back</span>
          Quay lại danh sách phim
        </NuxtLink>
      </div>

      <div class="detail-grid">
        <div class="detail-copy">
          <span class="detail-chip">{{ currentProduct.category }}</span>

          <h1 class="detail-title">{{ currentProduct.name }}</h1>

          <div class="detail-meta">
            <div class="detail-meta-item">
              <span class="material-symbols-outlined text-sm">calendar_today</span>
              Đang mở bán
            </div>
            <div class="detail-meta-item">
              <span class="material-symbols-outlined text-sm">sell</span>
              {{ formattedPrice }}
            </div>
            <div v-if="currentProduct.rating" class="detail-meta-item">
              <span class="material-symbols-outlined text-sm text-yellow-400">star</span>
              {{ currentProduct.rating.toFixed(1) }} điểm
            </div>
          </div>

          <p class="detail-description">
            {{ currentProduct.description || 'Không có mô tả chi tiết cho phim này.' }}
          </p>

          <div class="detail-actions">
            <a
              :href="trailerHref"
              target="_blank"
              rel="noopener noreferrer"
              class="detail-btn detail-btn-primary"
            >
              <span class="material-symbols-outlined text-base">play_arrow</span>
              Xem Trailer
            </a>

            <button
              @click="startBooking"
              class="detail-btn detail-btn-secondary"
            >
              Đặt Vé
            </button>
          </div>

          <div class="detail-facts">
            <div class="detail-fact">
              <span class="detail-fact-label">Định dạng:</span>
              <span class="detail-fact-value">{{ currentProduct.category }}</span>
            </div>
            <div class="detail-fact">
              <span class="detail-fact-label">Giá mở bán:</span>
              <span class="detail-fact-value">{{ formattedPrice }}</span>
            </div>
            <div class="detail-fact">
              <span class="detail-fact-label">Trải nghiệm:</span>
              <span class="detail-fact-value">Chọn rạp, suất chiếu và ghế ngay trong vài bước</span>
            </div>
          </div>
        </div>

        <div class="detail-poster-col">
          <img
            :src="currentProduct.imageUrl"
            :alt="currentProduct.name"
            class="detail-poster"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.detail-shell {
  min-height: calc(100vh - 72px);
}

.detail-hero {
  position: relative;
  overflow: hidden;
  border-radius: 1.35rem;
  min-height: 760px;
  background-position: center;
  background-size: cover;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.detail-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(18, 20, 20, 0.08) 0%, rgba(18, 20, 20, 0.35) 100%);
}

.detail-topbar {
  position: relative;
  z-index: 1;
  padding: 1.3rem 1.5rem 0;
}

.detail-backlink {
  display: inline-flex;
  align-items: center;
  gap: 0.42rem;
  color: #e2e2e2;
  font-size: 0.84rem;
  font-weight: 700;
}

.detail-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) 340px;
  gap: 3rem;
  align-items: center;
  min-height: 680px;
  padding: 2.1rem 3rem 3rem;
}

.detail-copy {
  max-width: 720px;
}

.detail-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.45rem;
  background: #ff7a1a;
  color: #fff;
  min-height: 28px;
  padding: 0 0.65rem;
  font-size: 0.72rem;
  font-weight: 900;
}

.detail-title {
  margin-top: 1rem;
  font-size: clamp(2.5rem, 4.2vw, 4.6rem);
  line-height: 0.98;
  font-weight: 900;
  text-transform: uppercase;
  color: #ffffff;
}

.detail-meta {
  margin-top: 1.25rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.detail-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: #e5e7eb;
  font-size: 0.92rem;
}

.detail-description {
  margin-top: 1.4rem;
  color: #f3f4f6;
  font-size: 1rem;
  line-height: 1.9;
  text-wrap: pretty;
}

.detail-actions {
  margin-top: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem;
}

.detail-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 48px;
  min-width: 132px;
  padding: 0 1.1rem;
  border-radius: 0.8rem;
  font-weight: 800;
  transition: all 0.2s ease;
}

.detail-btn-primary {
  background: #ff7a1a;
  color: #fff;
}

.detail-btn-primary:hover {
  filter: brightness(1.05);
}

.detail-btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.28);
  color: #ffffff;
}

.detail-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.detail-facts {
  margin-top: 2rem;
  display: grid;
  gap: 0.75rem;
}

.detail-fact {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  font-size: 0.92rem;
}

.detail-fact-label {
  color: #c7cad0;
  font-weight: 700;
}

.detail-fact-value {
  color: #ffffff;
}

.detail-poster-col {
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-poster {
  width: min(100%, 320px);
  aspect-ratio: 2 / 3;
  object-fit: cover;
  border-radius: 1rem;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.14);
}

@media (max-width: 1100px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
    min-height: auto;
    padding: 2rem 1.4rem 2.2rem;
  }

  .detail-copy {
    max-width: none;
  }

  .detail-poster-col {
    justify-content: flex-start;
  }

  .detail-hero {
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .detail-title {
    font-size: 2.2rem;
  }

  .detail-description {
    font-size: 0.94rem;
    line-height: 1.75;
  }

  .detail-poster {
    width: 260px;
  }
}
</style>

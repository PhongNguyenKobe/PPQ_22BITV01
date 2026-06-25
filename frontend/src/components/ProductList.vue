<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import ProductCard from './ProductCard.vue'

// ---------- Types ----------
interface Product {
  id: number
  name: string
  price: number
  category: string
  imageUrl: string
  description: string
}

// ---------- State ----------
const products         = ref<Product[]>([])
const loading          = ref(true)
const error            = ref('')
const searchTerm       = ref('')
const selectedCategory = ref('All')
const sortOption       = ref<'none' | 'price-asc' | 'price-desc'>('none')

// ---------- Fetch (tách hàm riêng để có thể gọi lại khi Thử lại) ----------
async function fetchProducts() {
  loading.value = true
  error.value   = ''
  try {
    const res = await axios.get('https://fakestoreapi.com/products')
    // Nếu GV yêu cầu products.json, đổi URL thành: '/data/products.json'
    products.value = res.data.map((item: any) => ({
      id:          item.id,
      name:        item.title,
      price:       Math.round(item.price * 1000),
      category:    item.category,
      imageUrl:    item.image,
      description: item.description,
    }))
  } catch (err) {
    error.value = 'Không thể tải sản phẩm. Vui lòng thử lại sau.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchProducts)

// ---------- Derived ----------
const categories = computed(() => [
  'All',
  ...Array.from(new Set(products.value.map((p) => p.category))),
])

const filteredProducts = computed(() => {
  let list = [...products.value]

  // 1) Search
  const q = searchTerm.value.trim().toLowerCase()
  if (q) {
    list = list.filter((p) => p.name.toLowerCase().includes(q))
  }

  // 2) Category filter
  if (selectedCategory.value !== 'All') {
    list = list.filter((p) => p.category === selectedCategory.value)
  }

  // 3) Sort
  if (sortOption.value === 'price-asc') {
    list = [...list].sort((a, b) => a.price - b.price)
  } else if (sortOption.value === 'price-desc') {
    list = [...list].sort((a, b) => b.price - a.price)
  }

  return list
})

// ---------- Actions ----------
function clearFilters() {
  searchTerm.value       = ''
  selectedCategory.value = 'All'
  sortOption.value       = 'none'
}
</script>

<template>
  <section class="section container" id="products">

    <!-- Heading -->
    <div class="section__heading">
      <h2>Vé &amp; Combo nổi bật</h2>
      <a class="section__more" href="#products">
        Xem tất cả
        <span class="material-symbols-outlined">chevron_right</span>
      </a>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="state-box">
      <span class="material-symbols-outlined state-box__icon spin">progress_activity</span>
      <p>Đang tải sản phẩm...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="state-box state-box--error">
      <span class="material-symbols-outlined state-box__icon">error_outline</span>
      <p>{{ error }}</p>
      <button class="filter-bar__clear-btn" @click="fetchProducts">
        <span class="material-symbols-outlined">refresh</span>
        Thử lại
      </button>
    </div>

    <!-- Main content -->
    <template v-else>
      <!-- Filter bar -->
      <div class="filter-bar">
        <!-- Search -->
        <div class="filter-bar__input-wrap">
          <span class="material-symbols-outlined filter-bar__icon">search</span>
          <input
            v-model="searchTerm"
            type="text"
            class="filter-bar__input"
            placeholder="Tìm sản phẩm..."
          />
          <button
            v-if="searchTerm"
            class="filter-bar__clear-icon"
            aria-label="Xóa tìm kiếm"
            @click="searchTerm = ''"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <!-- Category -->
        <select v-model="selectedCategory" class="filter-bar__select">
          <option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat === 'All' ? 'Tất cả danh mục' : cat }}
          </option>
        </select>

        <!-- Sort -->
        <select v-model="sortOption" class="filter-bar__select">
          <option value="none">Sắp xếp theo giá</option>
          <option value="price-asc">Giá: Thấp → Cao</option>
          <option value="price-desc">Giá: Cao → Thấp</option>
        </select>

        <!-- Clear -->
        <button class="filter-bar__clear-btn" @click="clearFilters">
          <span class="material-symbols-outlined">filter_list_off</span>
          Xóa bộ lọc
        </button>
      </div>

      <!-- Result count -->
      <p class="result-count">
        Hiển thị
        <strong>{{ filteredProducts.length }}</strong>
        /
        <strong>{{ products.length }}</strong>
        sản phẩm
      </p>

      <!-- Product list -->
      <div v-if="filteredProducts.length > 0" class="product-scroll">
        <ProductCard
          v-for="product in filteredProducts"
          :key="product.id"
          v-bind="product"
        />
      </div>

      <!-- Empty state -->
      <div v-else class="state-box">
        <span class="material-symbols-outlined state-box__icon">search_off</span>
        <p>Không tìm thấy sản phẩm phù hợp.</p>
        <button class="filter-bar__clear-btn" @click="clearFilters">Xóa bộ lọc</button>
      </div>
    </template>

  </section>
</template>

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 16px 0 12px;
}

.filter-bar__input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1 1 200px;
  min-width: 180px;
}

.filter-bar__icon {
  position: absolute;
  left: 10px;
  font-size: 18px;
  color: var(--muted);
  pointer-events: none;
}

.filter-bar__input {
  width: 100%;
  padding: 8px 36px 8px 36px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: #121212;
  color: var(--text);
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}

.filter-bar__input::placeholder { color: var(--muted); }

.filter-bar__input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.18);
}

.filter-bar__clear-icon {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--muted);
  display: flex;
  align-items: center;
  padding: 0;
  font-size: 18px;
}

.filter-bar__clear-icon:hover { color: var(--text); }

.filter-bar__select {
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: #121212;
  color: var(--text);
  font-size: 0.88rem;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.filter-bar__select:focus { border-color: var(--primary); }

.filter-bar__clear-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: transparent;
  color: var(--text-soft);
  font-size: 0.88rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.filter-bar__clear-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
}

.filter-bar__clear-btn .material-symbols-outlined { font-size: 18px; }

.result-count {
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0 0 12px;
}

.result-count strong { color: var(--text); }

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

.product-scroll:active { cursor: grabbing; }

.product-scroll::-webkit-scrollbar { height: 4px; }
.product-scroll::-webkit-scrollbar-track { background: transparent; }
.product-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 999px;
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 0;
  color: var(--muted);
  text-align: center;
}

.state-box--error { color: #ff6b6b; }

.state-box__icon { font-size: 48px; opacity: 0.5; }

.state-box p { margin: 0; font-size: 0.95rem; }

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spin { animation: spin 1s linear infinite; display: inline-block; }

@media (max-width: 720px) {
  .filter-bar { flex-direction: column; }
  .filter-bar__input-wrap,
  .filter-bar__select,
  .filter-bar__clear-btn { width: 100%; }
}
</style>
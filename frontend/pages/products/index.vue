<script setup lang="ts">
import { storeToRefs } from 'pinia'
import ProductCard from "~/components/ProductCard.vue";
import { useProductsStore } from '~/store/products'

definePageMeta({
  layout: "default",
});


// State
const productsStore = useProductsStore()
const { products, loading } = storeToRefs(productsStore)
const error = ref("");

const searchTerm = ref("");
const selectedCategory = ref("All");
const sortOption = ref<"none" | "price-asc" | "price-desc">("none");

// Fetch dữ liệu phim từ backend catalog
onMounted(async () => {
  try {
    await productsStore.fetchProducts()
  } catch (err) {
    console.error(err);
    error.value = "Không thể tải danh sách phim.";
  }
});
// Danh mục
const categories = computed(() => [
  "All",
  ...new Set(products.value.map((p) => p.category)),
]);

// Search + Filter + Sort
const filteredProducts = computed(() => {
  let updated = [...products.value];

  if (searchTerm.value.trim() !== "") {
    const lower = searchTerm.value.toLowerCase();

    updated = updated.filter((p) =>
      p.name.toLowerCase().includes(lower)
    );
  }

  if (selectedCategory.value !== "All") {
    updated = updated.filter(
      (p) => p.category === selectedCategory.value
    );
  }

  if (sortOption.value === "price-asc") {
    updated.sort((a, b) => a.price - b.price);
  } else if (sortOption.value === "price-desc") {
    updated.sort((a, b) => b.price - a.price);
  }

  return updated;
});

// Reset
function clearFilters() {
  searchTerm.value = "";
  selectedCategory.value = "All";
  sortOption.value = "none";
}
</script>

<template>
  <!-- Loading -->
  <div
    v-if="loading"
    class="py-20 text-center text-on-surface"
  >
    Đang tải sản phẩm...
  </div>

  <!-- Error -->
  <div
    v-else-if="error"
    class="py-20 text-center text-red-500"
  >
    {{ error }}
  </div>

  <!-- Content -->
  <section v-else class="products-shell py-10 max-w-container-max mx-auto px-4 sm:px-6 md:px-margin-desktop">
    <div class="mb-7">
      <p class="text-xs uppercase tracking-[0.18em] text-on-surface-variant">Danh mục chiếu phim</p>
      <h2 class="font-headline-lg text-3xl font-bold text-on-surface mt-2">PHIM</h2>
      <p class="text-sm text-on-surface-variant mt-2">Khám phá phim đang nổi bật và đặt vé theo suất chiếu mong muốn.</p>
    </div>

    <div class="filters-wrap mb-5">
      <input
        v-model="searchTerm"
        type="text"
        placeholder="Tìm theo tên phim..."
        class="control-input"
      />

      <select v-model="selectedCategory" class="control-input">
        <option v-for="cat in categories" :key="cat" :value="cat">
          {{ cat }}
        </option>
      </select>

      <select v-model="sortOption" class="control-input">
        <option value="none">Sắp xếp: mặc định</option>
        <option value="price-asc">Giá: Thấp → Cao</option>
        <option value="price-desc">Giá: Cao → Thấp</option>
      </select>

      <button @click="clearFilters" class="control-clear">Xóa bộ lọc</button>
    </div>

    <p class="text-xs text-on-surface-variant mb-5">
      Hiển thị {{ filteredProducts.length }} / {{ products.length }} phim
    </p>

    <div v-if="filteredProducts.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
      <ProductCard
        v-for="product in filteredProducts"
        :key="product.id"
        v-bind="product"
      />
    </div>

    <div v-else class="text-center py-10 text-on-surface-variant">
      Không tìm thấy phim phù hợp.
    </div>
  </section>
</template>

<style scoped>
.products-shell {
  position: relative;
}

.filters-wrap {
  display: grid;
  grid-template-columns: 1.2fr 0.9fr 0.9fr auto;
  gap: 0.7rem;
}

.control-input {
  width: 100%;
  background: rgba(51, 53, 53, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.65rem;
  padding: 0.56rem 0.72rem;
  font-size: 0.9rem;
  color: #e7eaef;
}

.control-input:focus {
  outline: none;
  border-color: rgba(229, 9, 20, 0.5);
}

.control-clear {
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.06);
  border-radius: 0.65rem;
  padding: 0.56rem 0.9rem;
  font-size: 0.84rem;
  color: #e2e8f0;
  font-weight: 700;
}

@media (max-width: 992px) {
  .filters-wrap {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .filters-wrap {
    grid-template-columns: 1fr;
  }
}
</style>
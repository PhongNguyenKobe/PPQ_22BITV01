<script setup lang="ts">
import { storeToRefs } from 'pinia'
import ProductCard from "~/components/ProductCard.vue";
import { useProductsStore } from '~/store/products'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: "default",
});


// State
const productsStore = useProductsStore()
const userStore = useUserStore()
const route = useRoute()
const { products, loading } = storeToRefs(productsStore)
const error = ref("");
const isAdminPreview = computed(() =>
  route.query.preview === 'admin'
  && ['admin', 'branch-admin'].includes(userStore.currentUser?.role || '')
)
const adminReturnPath = computed(() =>
  userStore.currentUser?.role === 'branch-admin'
    ? '/branch-admin/dashboard'
    : '/admin/dashboard'
)

const searchTerm = ref("");
const selectedCategory = ref("ALL");
const selectedStatus = ref<"ALL" | "NOW_SHOWING" | "UPCOMING">("ALL");
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
  ...new Set(
    products.value
      .flatMap((product) => product.genres)
      .map((genre) => genre.trim())
      .filter(Boolean)
  ),
].sort((a, b) => a.localeCompare(b, "vi")));

// Search + Filter + Sort
const filteredProducts = computed(() => {
  let updated = [...products.value];

  if (searchTerm.value.trim() !== "") {
    const lower = searchTerm.value.toLowerCase();

    updated = updated.filter((p) =>
      p.name.toLowerCase().includes(lower)
    );
  }

  if (selectedCategory.value !== "ALL") {
    const selected = selectedCategory.value.toLocaleLowerCase("vi");
    updated = updated.filter((product) =>
      product.genres.some((genre) => genre.toLocaleLowerCase("vi") === selected)
    );
  }
  if (selectedStatus.value !== "ALL") updated = updated.filter((p) => p.status === selectedStatus.value)

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
  selectedCategory.value = "ALL";
  selectedStatus.value = "ALL";
  sortOption.value = "none";
}
</script>

<template>
  <div v-if="isAdminPreview" class="sticky top-0 z-40 border-b border-amber-400/30 bg-amber-500/10 px-4 py-3 backdrop-blur-xl">
    <div class="mx-auto flex max-w-container-max flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-sm font-bold text-amber-200">Chế độ xem trước dành cho quản trị viên</p>
        <p class="text-xs text-amber-100/70">Bạn đang kiểm tra nội dung khách hàng sẽ nhìn thấy. Mua vé đã được khóa trong chế độ này.</p>
      </div>
      <NuxtLink :to="adminReturnPath" class="rounded-lg bg-amber-300 px-4 py-2 text-xs font-bold text-black">
        Quay lại quản trị
      </NuxtLink>
    </div>
  </div>
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

      <select v-model="selectedCategory" class="control-input" aria-label="Lọc theo thể loại">
        <option value="ALL">Tất cả thể loại</option>
        <option v-for="cat in categories" :key="cat" :value="cat">
          {{ cat }}
        </option>
      </select>

      <select v-model="selectedStatus" class="control-input">
        <option value="ALL">Tất cả trạng thái</option>
        <option value="NOW_SHOWING">Đang chiếu</option>
        <option value="UPCOMING">Sắp chiếu</option>
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
        :admin-preview="isAdminPreview"
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
  grid-template-columns: 1.2fr 0.9fr 0.9fr 0.9fr auto;
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

<script setup lang="ts">
import ProductCard from "~/components/ProductCard.vue";

definePageMeta({
  layout: "default",
});


// State
const products = ref<any[]>([]);
const loading = ref(true);
const error = ref("");

const searchTerm = ref("");
const selectedCategory = ref("All");
const sortOption = ref<"none" | "price-asc" | "price-desc">("none");

// Các loại vé
const ticketTypes = ["2D", "IMAX", "4DX", "VIP"];

// Fetch dữ liệu từ TMDB
onMounted(async () => {
  try {
    const data: any = await $fetch("/api/movies");

    products.value = data.results.map((movie: any) => ({
      id: movie.id,

      // Tên phim
      name: movie.title,

      // Giá vé giả lập
      price: (Math.floor(Math.random() * 16) + 7) * 10,

      // Loại vé giả lập
      category:
        ticketTypes[Math.floor(Math.random() * ticketTypes.length)],

      // Poster
      imageUrl: movie.poster_path
        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
        : "https://placehold.co/500x750?text=No+Image",

      // Mô tả
      description: movie.overview,
    }));
  } catch (err) {
    console.error(err);
    error.value = "Không thể tải danh sách phim.";
  } finally {
    loading.value = false;
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
  <section
    v-else
    class="py-16 max-w-container-max mx-auto px-6 md:px-margin-desktop"
  >
    <h2
      class="font-headline-lg text-3xl font-bold text-on-surface mb-2"
    >
      Vé & Combo
    </h2>

    <p
      class="text-sm text-on-surface-variant mb-8"
    >
      Tìm kiếm, lọc và sắp xếp sản phẩm.
    </p>

    <!-- Filter -->
    <div class="flex flex-wrap gap-3 mb-6">

      <input
        v-model="searchTerm"
        type="text"
        placeholder="Tìm theo tên sản phẩm..."
        class="px-3 py-2 rounded-lg bg-surface-container-high border border-glass-stroke text-sm min-w-[220px]"
      />

      <select
        v-model="selectedCategory"
        class="px-3 py-2 rounded-lg bg-surface-container-high border border-glass-stroke text-sm"
      >
        <option
          v-for="cat in categories"
          :key="cat"
          :value="cat"
        >
          {{ cat }}
        </option>
      </select>

      <select
        v-model="sortOption"
        class="px-3 py-2 rounded-lg bg-surface-container-high border border-glass-stroke text-sm"
      >
        <option value="none">
          Sắp xếp: mặc định
        </option>

        <option value="price-asc">
          Giá: Thấp → Cao
        </option>

        <option value="price-desc">
          Giá: Cao → Thấp
        </option>
      </select>

      <button
        @click="clearFilters"
        class="px-4 py-2 rounded-lg bg-surface-container border border-glass-stroke hover:bg-white/10 transition"
      >
        Xóa bộ lọc
      </button>

    </div>

    <!-- Count -->
    <p
      class="text-xs text-on-surface-variant mb-4"
    >
      Hiển thị
      {{ filteredProducts.length }}
      /
      {{ products.length }}
      sản phẩm
    </p>

    <!-- Product Grid -->
    <div
      v-if="filteredProducts.length"
      class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-6"
    >
      <ProductCard
        v-for="product in filteredProducts"
        :key="product.id"
        v-bind="product"
      />
    </div>

    <!-- Empty -->
    <div
      v-else
      class="text-center py-10 text-on-surface-variant"
    >
      Không tìm thấy sản phẩm phù hợp.
    </div>

  </section>
</template>
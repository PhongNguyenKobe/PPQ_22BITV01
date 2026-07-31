<script setup lang="ts">
import { storeToRefs } from 'pinia'
import ProductCard from "~/components/ProductCard.vue";
import { useProductsStore } from '~/store/products'
import { useUserStore } from '~/store/user'
import { branchesService, type BackendBranch, type BranchDetail } from '~/services/api'

definePageMeta({
  layout: "default",
});


// State
const productsStore = useProductsStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { products, loading } = storeToRefs(productsStore)
const error = ref("");
const catalogLoading = ref(false)
const branches = ref<BackendBranch[]>([])
const branchCatalogs = ref<BranchDetail[]>([])
const customerSelectedBranch = useState<string>('customer-selected-branch', () => 'ALL')
const isAdminPreview = computed(() =>
  route.query.preview === 'admin'
  && ['admin', 'branch-admin'].includes(userStore.currentUser?.role || '')
)
const adminReturnPath = computed(() =>
  userStore.currentUser?.role === 'branch-admin'
    ? '/branch-admin/dashboard'
    : '/admin/dashboard'
)
const selectedBranch = computed({
  get: () => String(route.query.branch_id || customerSelectedBranch.value || 'ALL'),
  set: (value: string) => {
    customerSelectedBranch.value = value
    const query = { ...route.query }
    if (value === 'ALL') delete query.branch_id
    else query.branch_id = value
    void router.replace({ query })
  },
})
const selectedBranchInfo = computed(() =>
  branches.value.find(branch => branch.id === selectedBranch.value),
)
const selectedScopeLabel = computed(() =>
  selectedBranchInfo.value
    ? `${selectedBranchInfo.value.name} (${selectedBranchInfo.value.city})`
    : 'Phim tại toàn hệ thống',
)

type MovieAvailability = { branchNames: string[]; minPrice: number }
const movieAvailability = computed(() => {
  const result = new Map<string, MovieAvailability>()
  const catalogs = selectedBranch.value === 'ALL'
    ? branchCatalogs.value
    : branchCatalogs.value.filter(branch => branch.id === selectedBranch.value)
  for (const catalog of catalogs) {
    for (const showtime of catalog.showtimes) {
      const movieId = String(showtime.movie_id)
      const current = result.get(movieId) || { branchNames: [], minPrice: Number.POSITIVE_INFINITY }
      if (!current.branchNames.includes(catalog.name)) current.branchNames.push(catalog.name)
      current.minPrice = Math.min(current.minPrice, Number(showtime.base_price))
      result.set(movieId, current)
    }
  }
  return result
})

const searchTerm = ref("");
const selectedCategory = ref("ALL");
const selectedStatus = ref<"ALL" | "NOW_SHOWING" | "UPCOMING">("ALL");
const sortOption = ref<"none" | "price-asc" | "price-desc">("none");
const hasActiveFilters = computed(() =>
  searchTerm.value.trim() !== ''
  || selectedCategory.value !== 'ALL'
  || selectedStatus.value !== 'ALL'
  || sortOption.value !== 'none'
)

// Fetch dữ liệu phim từ backend catalog
onMounted(async () => {
  try {
    catalogLoading.value = true
    await productsStore.fetchProducts()
    branches.value = await branchesService.getAll()

    if (isAdminPreview.value && userStore.currentUser?.role === 'branch-admin' && userStore.currentUser.branchId) {
      selectedBranch.value = userStore.currentUser.branchId
    }

    if (
      selectedBranch.value !== 'ALL'
      && !branches.value.some(branch => branch.id === selectedBranch.value)
    ) {
      selectedBranch.value = 'ALL'
    }

    const catalogResults = await Promise.allSettled(
      branches.value.map(branch => branchesService.getById(branch.id, true)),
    )
    branchCatalogs.value = catalogResults.flatMap(result =>
      result.status === 'fulfilled' ? [result.value] : [],
    )

    const availableBranchIds = new Set(branchCatalogs.value.map(branch => branch.id))
    if (selectedBranch.value !== 'ALL' && !availableBranchIds.has(selectedBranch.value)) {
      selectedBranch.value = 'ALL'
    }

    const failedCount = catalogResults.length - branchCatalogs.value.length
    if (failedCount) {
      console.warn(`Không tải được dữ liệu của ${failedCount} chi nhánh; trang vẫn hiển thị các chi nhánh còn hoạt động.`)
    }
  } catch (err) {
    console.error(err);
    error.value = "Không thể tải danh sách phim.";
  } finally {
    catalogLoading.value = false
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

function normalizeSearchText(value: string | null | undefined) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[đĐ]/g, character => character === 'Đ' ? 'D' : 'd')
    .toLocaleLowerCase('vi')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
}

// Search + Filter + Sort
const filteredProducts = computed(() => {
  let updated = products.value.filter(product => movieAvailability.value.has(String(product.backendMovieId || product.id)));

  if (searchTerm.value.trim() !== "") {
    const query = normalizeSearchText(searchTerm.value);

    updated = updated.filter((product) => {
      const searchableTitle = normalizeSearchText(
        `${product.name} ${product.originalTitle || ''}`,
      )
      return searchableTitle.includes(query)
    });
  }

  if (selectedCategory.value !== "ALL") {
    const selected = selectedCategory.value.toLocaleLowerCase("vi");
    updated = updated.filter((product) =>
      product.genres.some((genre) => genre.toLocaleLowerCase("vi") === selected)
    );
  }
  if (selectedStatus.value !== "ALL") updated = updated.filter((p) => p.status === selectedStatus.value)

  if (sortOption.value === "price-asc") {
    updated.sort((a, b) => effectivePrice(a) - effectivePrice(b));
  } else if (sortOption.value === "price-desc") {
    updated.sort((a, b) => effectivePrice(b) - effectivePrice(a));
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

function availabilityFor(product: { id: string | number; backendMovieId?: string }) {
  return movieAvailability.value.get(String(product.backendMovieId || product.id))
}

function effectivePrice(product: { id: string | number; backendMovieId?: string; price: number }) {
  return availabilityFor(product)?.minPrice || Number(product.price) * 1000
}
</script>

<template>
  <div v-if="isAdminPreview" class="sticky top-0 z-40 border-b border-amber-400/30 bg-amber-500/10 px-4 py-3 backdrop-blur-xl">
    <div class="mx-auto flex max-w-container-max flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-sm font-bold text-amber-200">Chế độ xem trước: {{ selectedScopeLabel }}</p>
        <p class="text-xs text-amber-100/70">Nội dung bên dưới là phim đang mở bán tại phạm vi đã chọn. Mua vé đã được khóa.</p>
      </div>
      <NuxtLink :to="adminReturnPath" class="rounded-lg bg-amber-300 px-4 py-2 text-xs font-bold text-black">
        Quay lại quản trị
      </NuxtLink>
    </div>
  </div>
  <!-- Loading -->
  <div
    v-if="loading || catalogLoading"
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

    <div class="mb-5 flex flex-col gap-3 rounded-2xl border border-sky-500/20 bg-sky-500/5 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p class="text-xs font-bold uppercase tracking-wider text-sky-300">Chi nhánh đang xem</p>
        <p class="mt-1 text-sm text-on-surface">{{ selectedScopeLabel }}</p>
      </div>
      <select v-model="selectedBranch" class="control-input max-w-sm" aria-label="Chọn chi nhánh">
        <option value="ALL">Phim tại toàn hệ thống</option>
        <option v-for="branch in branches" :key="branch.id" :value="branch.id">
          {{ branch.name }} ({{ branch.city }})
        </option>
      </select>
    </div>

    <div class="movie-toolbar mb-6">
      <!-- Top Row: Search input + Toggles / Dropdowns -->
      <div class="grid grid-cols-1 gap-3 md:grid-cols-12">
        <!-- Search Input -->
        <div class="relative md:col-span-6">
          <span class="material-symbols-outlined pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-xl text-red-400">search</span>
          <input
            v-model="searchTerm"
            autocomplete="off"
            type="text"
            placeholder="Tìm nhanh tên phim bạn muốn xem..."
            class="control-input search-control !pl-12 !pr-11"
            aria-label="Tìm phim theo tên"
          />
          <button
            v-if="searchTerm"
            type="button"
            class="absolute right-3 top-1/2 flex -translate-y-1/2 items-center rounded-full p-1 text-gray-400 transition hover:bg-white/10 hover:text-white"
            aria-label="Xóa nội dung tìm kiếm"
            @click="searchTerm = ''"
          >
            <span class="material-symbols-outlined text-lg">close</span>
          </button>
        </div>
        
        <!-- Category Dropdown -->
        <div class="md:col-span-3 relative">
          <select v-model="selectedCategory" class="control-input !pr-10 appearance-none cursor-pointer" aria-label="Lọc theo thể loại">
            <option value="ALL">Tất cả thể loại</option>
            <option v-for="cat in categories" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
          <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none text-sm">expand_more</span>
        </div>

        <!-- Sort Option Dropdown -->
        <div class="md:col-span-3 relative">
          <select v-model="sortOption" class="control-input !pr-10 appearance-none cursor-pointer">
            <option value="none">Sắp xếp: mặc định</option>
            <option value="price-asc">Giá: Thấp → Cao</option>
            <option value="price-desc">Giá: Cao → Thấp</option>
          </select>
          <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none text-sm">expand_more</span>
        </div>
      </div>

      <!-- Bottom Row: Status Tabs (Pills) + Clear Button -->
      <div class="mt-3 flex flex-wrap items-center gap-3">
        <!-- Status Tabs / Pills -->
        <div class="flex bg-black/40 p-1 rounded-xl border border-white/5">
          <button
            class="rounded-lg px-4 py-2 text-xs font-bold transition-all"
            :class="selectedStatus === 'ALL' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30' : 'text-gray-400 hover:text-white'"
            @click="selectedStatus = 'ALL'"
          >
            Tất cả
          </button>
          <button
            class="rounded-lg px-4 py-2 text-xs font-bold transition-all"
            :class="selectedStatus === 'NOW_SHOWING' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30' : 'text-gray-400 hover:text-white'"
            @click="selectedStatus = 'NOW_SHOWING'"
          >
            Đang chiếu
          </button>
          <button
            class="rounded-lg px-4 py-2 text-xs font-bold transition-all"
            :class="selectedStatus === 'UPCOMING' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30' : 'text-gray-400 hover:text-white'"
            @click="selectedStatus = 'UPCOMING'"
          >
            Sắp chiếu
          </button>
        </div>

        <!-- Clear Button -->
        <span class="ml-auto text-xs text-on-surface-variant">
          {{ filteredProducts.length }} kết quả
        </span>

        <button
          v-if="hasActiveFilters"
          type="button"
          @click="clearFilters"
          class="flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold text-red-300 transition hover:bg-red-500/10 hover:text-red-200"
        >
          <span class="material-symbols-outlined text-sm">filter_alt_off</span>
          Đặt lại
        </button>
      </div>
    </div>

    <p class="text-xs text-on-surface-variant mb-5">
      Hiển thị {{ filteredProducts.length }} phim đang mở bán tại {{ selectedScopeLabel }}
    </p>

    <div v-if="filteredProducts.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
      <ProductCard
        v-for="product in filteredProducts"
        :key="product.id"
        v-bind="product"
        :price="(availabilityFor(product)?.minPrice || product.price * 1000) / 1000"
        :branch-names="availabilityFor(product)?.branchNames || []"
        :selected-branch-name="selectedBranchInfo?.name"
        :selected-branch-id="selectedBranch === 'ALL' ? undefined : selectedBranch"
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

.movie-toolbar {
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1.15rem;
  background: rgba(25, 27, 27, 0.82);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
}

.search-control {
  min-height: 3.2rem;
  background: rgba(8, 9, 9, 0.72);
  border-color: rgba(229, 9, 20, 0.28);
  font-size: 0.95rem;
}

.search-control:focus {
  border-color: rgba(239, 68, 68, 0.78);
  box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.1);
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

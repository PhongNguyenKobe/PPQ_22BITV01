<script setup lang="ts">
import { storeToRefs } from 'pinia'
import ProductCard from '~/components/ProductCard.vue'
import { useProductsStore } from '~/store/products'
import { useUserStore } from '~/store/user'
import { branchesService, type BackendBranch, type BranchDetail, youtubeTrailerLink } from '~/services/api'

definePageMeta({ layout: 'default' })

const productsStore = useProductsStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { products, loading } = storeToRefs(productsStore)
const error = ref('')
const catalogLoading = ref(false)
const branches = ref<BackendBranch[]>([])
const branchCatalogs = ref<BranchDetail[]>([])
const customerSelectedBranch = useState<string>('customer-selected-branch', () => 'ALL')

const isAdminPreview = computed(() => route.query.preview === 'admin' && ['admin', 'branch-admin'].includes(userStore.currentUser?.role || ''))
const adminReturnLocation = computed(() => ({
  path: userStore.currentUser?.role === 'branch-admin' ? '/branch-admin/dashboard' : '/admin/dashboard',
  query: { tab: String(route.query.return_tab || 'overview') },
}))
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
const selectedBranchInfo = computed(() => branches.value.find(branch => branch.id === selectedBranch.value))
const selectedScopeLabel = computed(() => selectedBranchInfo.value ? `${selectedBranchInfo.value.name} · ${selectedBranchInfo.value.city}` : 'Tất cả cụm rạp CineAI')

type MovieAvailability = { branchNames: string[]; minPrice: number }
const movieAvailability = computed(() => {
  const result = new Map<string, MovieAvailability>()
  const catalogs = selectedBranch.value === 'ALL' ? branchCatalogs.value : branchCatalogs.value.filter(branch => branch.id === selectedBranch.value)
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

const searchTerm = ref('')
const selectedCategory = ref('ALL')
const initialStatus = ['NOW_SHOWING', 'UPCOMING'].includes(String(route.query.status)) ? String(route.query.status) : 'ALL'
const selectedStatus = ref<'ALL' | 'NOW_SHOWING' | 'UPCOMING'>(initialStatus as 'ALL' | 'NOW_SHOWING' | 'UPCOMING')
const sortOption = ref<'none' | 'price-asc' | 'price-desc'>('none')
const categories = computed(() => [...new Set(products.value.flatMap(product => product.genres).map(genre => genre.trim()).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'vi')))

function availabilityFor(product: { id: string | number; backendMovieId?: string }) {
  return movieAvailability.value.get(String(product.backendMovieId || product.id))
}
function effectivePrice(product: { id: string | number; backendMovieId?: string; price: number }) {
  return availabilityFor(product)?.minPrice || Number(product.price) * 1000
}
function normalizeSearchText(value: string | null | undefined) {
  return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[đĐ]/g, c => c === 'Đ' ? 'D' : 'd').toLocaleLowerCase('vi').replace(/[^a-z0-9]+/g, ' ').trim()
}

// Phim đang chiếu chỉ được bán khi có suất chiếu. Phim sắp chiếu là nội dung
// giới thiệu toàn hệ thống nên vẫn phải xuất hiện dù chưa được chi nhánh xếp lịch.
const customerVisibleProducts = computed(() => products.value.filter(product =>
  product.status === 'UPCOMING'
  || (product.status === 'NOW_SHOWING' && movieAvailability.value.has(String(product.backendMovieId || product.id))),
))
const featuredProduct = computed(() => [...customerVisibleProducts.value].sort((a, b) => Number(b.status === 'NOW_SHOWING') - Number(a.status === 'NOW_SHOWING') || Number(b.rating || 0) - Number(a.rating || 0))[0])
const filteredProducts = computed(() => {
  let result = [...customerVisibleProducts.value]
  const query = normalizeSearchText(searchTerm.value)
  if (query) result = result.filter(product => normalizeSearchText(`${product.name} ${product.originalTitle || ''}`).includes(query))
  if (selectedCategory.value !== 'ALL') result = result.filter(product => product.genres.some(genre => genre.toLocaleLowerCase('vi') === selectedCategory.value.toLocaleLowerCase('vi')))
  if (selectedStatus.value !== 'ALL') result = result.filter(product => product.status === selectedStatus.value)
  if (sortOption.value === 'price-asc') result.sort((a, b) => effectivePrice(a) - effectivePrice(b))
  if (sortOption.value === 'price-desc') result.sort((a, b) => effectivePrice(b) - effectivePrice(a))
  return result
})
const hasActiveFilters = computed(() => searchTerm.value.trim() || selectedCategory.value !== 'ALL' || selectedStatus.value !== 'ALL' || sortOption.value !== 'none')
const featuredQuery = computed(() => ({ ...(isAdminPreview.value ? { preview: 'admin' } : {}), ...(selectedBranch.value !== 'ALL' ? { branch_id: selectedBranch.value } : {}) }))

function clearFilters() {
  searchTerm.value = ''
  selectedCategory.value = 'ALL'
  selectedStatus.value = 'ALL'
  sortOption.value = 'none'
}

onMounted(async () => {
  try {
    catalogLoading.value = true
    await productsStore.fetchProducts()
    branches.value = await branchesService.getAll()
    if (isAdminPreview.value && userStore.currentUser?.role === 'branch-admin' && userStore.currentUser.branchId) selectedBranch.value = userStore.currentUser.branchId
    if (selectedBranch.value !== 'ALL' && !branches.value.some(branch => branch.id === selectedBranch.value)) selectedBranch.value = 'ALL'
    const results = await Promise.allSettled(branches.value.map(branch => branchesService.getById(branch.id, true)))
    branchCatalogs.value = results.flatMap(result => result.status === 'fulfilled' ? [result.value] : [])
  } catch (cause) {
    console.error(cause)
    error.value = 'Không thể tải danh sách phim. Vui lòng thử lại.'
  } finally {
    catalogLoading.value = false
  }
})

watch(() => route.query.status, (value) => {
  selectedStatus.value = ['NOW_SHOWING', 'UPCOMING'].includes(String(value))
    ? String(value) as 'NOW_SHOWING' | 'UPCOMING'
    : 'ALL'
})
</script>

<template>
  <div v-if="isAdminPreview" class="preview-strip">
    <div class="mx-auto flex max-w-container-max items-center justify-between gap-4 px-4 py-3 sm:px-6 md:px-margin-desktop">
      <div class="flex min-w-0 items-center gap-3">
        <span class="material-symbols-outlined rounded-xl bg-amber-400/15 p-2 text-amber-300">visibility</span>
        <div class="min-w-0">
          <p class="truncate text-sm font-bold text-white">Bản xem trước trang bán vé · {{ selectedScopeLabel }}</p>
          <p class="text-xs text-white/55">Bạn đang xem giao diện khách hàng; chức năng thanh toán đã được khóa.</p>
        </div>
      </div>
      <NuxtLink :to="adminReturnLocation" class="shrink-0 rounded-xl border border-white/15 px-4 py-2 text-xs font-bold text-white transition hover:bg-white/10">Quay lại quản trị</NuxtLink>
    </div>
  </div>

  <div v-if="loading || catalogLoading" class="flex min-h-[55vh] flex-col items-center justify-center gap-4 text-white/60">
    <span class="loader-ring" />
    <p>Đang chuẩn bị lịch phim...</p>
  </div>
  <div v-else-if="error" class="mx-auto max-w-xl py-24 text-center">
    <span class="material-symbols-outlined text-5xl text-red-400">error</span>
    <p class="mt-4 text-lg font-bold text-white">{{ error }}</p>
    <button class="mt-5 rounded-xl bg-red-600 px-5 py-3 font-bold text-white" @click="router.go(0)">Thử lại</button>
  </div>

  <main v-else class="mx-auto max-w-container-max px-4 pb-16 pt-7 sm:px-6 md:px-margin-desktop">
    <section v-if="featuredProduct" class="featured-hero" :style="{ '--hero-image': `url(${featuredProduct.imageUrl})` }">
      <div class="featured-copy">
        <p class="mb-3 text-xs font-bold uppercase tracking-[0.24em] text-red-400">Phim nổi bật tại CineAI</p>
        <h1 class="max-w-3xl text-4xl font-black leading-tight text-white md:text-6xl">{{ featuredProduct.name }}</h1>
        <div class="mt-4 flex flex-wrap items-center gap-3 text-sm text-white/75">
          <span v-if="featuredProduct.rating" class="flex items-center gap-1 font-bold text-amber-300"><span class="material-symbols-outlined text-lg" style="font-variation-settings:'FILL' 1">star</span>{{ featuredProduct.rating.toFixed(1) }}</span>
          <span v-if="featuredProduct.duration">{{ featuredProduct.duration }} phút</span>
          <span>{{ featuredProduct.genres.slice(0, 3).join(' · ') }}</span>
          <span class="rounded-md border border-white/20 px-2 py-0.5 text-xs">T13</span>
        </div>
        <p class="mt-5 max-w-2xl line-clamp-3 text-sm leading-7 text-white/65 md:text-base">{{ featuredProduct.description }}</p>
        <div class="mt-7 flex flex-wrap gap-3">
          <NuxtLink :to="{ path: `/products/${featuredProduct.id}`, query: featuredQuery }" class="hero-primary"><span class="material-symbols-outlined">confirmation_number</span>{{ isAdminPreview ? 'Xem luồng bán vé' : 'Xem suất chiếu' }}</NuxtLink>
          <a :href="youtubeTrailerLink(featuredProduct.trailerUrl, featuredProduct.name)" target="_blank" rel="noopener noreferrer" class="hero-secondary"><span class="material-symbols-outlined">play_circle</span>Xem trailer</a>
        </div>
      </div>
      <img :src="featuredProduct.imageUrl" :alt="featuredProduct.name" class="featured-poster" @error="($event.target as HTMLImageElement).src = '/images/movie-placeholder.svg'">
    </section>

    <section class="mt-10">
      <div class="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div><p class="text-xs font-bold uppercase tracking-[0.2em] text-red-400">Đang mở bán</p><h2 class="mt-1 text-3xl font-black text-white">Chọn phim bạn muốn xem</h2></div>
        <p class="text-sm text-white/45">{{ filteredProducts.length }} phim phù hợp</p>
      </div>

      <div class="filter-panel">
        <div class="status-tabs">
          <button v-for="item in [{ value: 'ALL', label: 'Tất cả' }, { value: 'NOW_SHOWING', label: 'Đang chiếu' }, { value: 'UPCOMING', label: 'Sắp chiếu' }]" :key="item.value" :class="{ active: selectedStatus === item.value }" @click="selectedStatus = item.value as typeof selectedStatus">{{ item.label }}</button>
        </div>
        <label class="filter-control filter-search"><span class="material-symbols-outlined">search</span><input v-model="searchTerm" type="search" placeholder="Tìm tên phim..." aria-label="Tìm phim"></label>
        <select v-model="selectedBranch" class="filter-select" aria-label="Chọn cụm rạp"><option value="ALL">Tất cả cụm rạp</option><option v-for="branch in branches" :key="branch.id" :value="branch.id">{{ branch.name }} · {{ branch.city }}</option></select>
        <select v-model="selectedCategory" class="filter-select" aria-label="Chọn thể loại"><option value="ALL">Tất cả thể loại</option><option v-for="category in categories" :key="category" :value="category">{{ category }}</option></select>
        <select v-model="sortOption" class="filter-select" aria-label="Sắp xếp"><option value="none">Sắp xếp mặc định</option><option value="price-asc">Giá thấp đến cao</option><option value="price-desc">Giá cao đến thấp</option></select>
      </div>
      <div class="mt-3 flex items-center justify-between text-xs text-white/45"><span><span class="material-symbols-outlined mr-1 align-middle text-sm">location_on</span>{{ selectedScopeLabel }}</span><button v-if="hasActiveFilters" class="font-bold text-red-400 hover:text-red-300" @click="clearFilters">Xóa bộ lọc</button></div>

      <div v-if="filteredProducts.length" class="mt-7 grid grid-cols-2 gap-4 sm:gap-6 md:grid-cols-3 xl:grid-cols-4">
        <ProductCard v-for="product in filteredProducts" :key="product.id" v-bind="product" :price="effectivePrice(product) / 1000" :branch-names="availabilityFor(product)?.branchNames || []" :selected-branch-name="selectedBranchInfo?.name" :selected-branch-id="selectedBranch === 'ALL' ? undefined : selectedBranch" :admin-preview="isAdminPreview" />
      </div>
      <div v-else class="empty-state"><span class="material-symbols-outlined">movie_off</span><h3>Chưa tìm thấy phim phù hợp</h3><p>Thử chọn cụm rạp khác hoặc xóa bớt bộ lọc.</p><button @click="clearFilters">Xóa bộ lọc</button></div>
    </section>
  </main>
</template>

<style scoped>
.preview-strip{position:relative;z-index:30;border-bottom:1px solid rgba(255,255,255,.08);background:rgba(18,19,22,.96);backdrop-filter:blur(18px)}
.featured-hero{--hero-image:none;position:relative;min-height:520px;overflow:hidden;border:1px solid rgba(255,255,255,.09);border-radius:30px;background:#141517;box-shadow:0 34px 80px -50px #000;display:flex;align-items:center}
.featured-hero::before{content:"";position:absolute;inset:0;background-image:linear-gradient(90deg,#111214 0%,rgba(17,18,20,.94) 42%,rgba(17,18,20,.28) 76%,rgba(17,18,20,.65) 100%),var(--hero-image);background-size:cover;background-position:center 30%;filter:saturate(.8)}
.featured-hero::after{content:"";position:absolute;inset:0;background:linear-gradient(0deg,#111214 0%,transparent 32%)}
.featured-copy{position:relative;z-index:2;width:min(68%,800px);padding:clamp(28px,5vw,72px)}
.featured-poster{position:absolute;z-index:2;right:6%;width:min(25%,290px);aspect-ratio:2/3;object-fit:cover;border-radius:20px;box-shadow:0 30px 70px #000;transform:rotate(2deg)}
.hero-primary,.hero-secondary{display:inline-flex;min-height:48px;align-items:center;gap:9px;border-radius:13px;padding:0 20px;font-size:14px;font-weight:800;transition:.2s}.hero-primary{background:#e50914;color:white;box-shadow:0 14px 30px -15px #e50914}.hero-secondary{border:1px solid rgba(255,255,255,.17);background:rgba(255,255,255,.08);color:white;backdrop-filter:blur(10px)}.hero-primary:hover,.hero-secondary:hover{transform:translateY(-2px);filter:brightness(1.08)}
.filter-panel{display:grid;grid-template-columns:auto minmax(220px,1fr) repeat(3,minmax(155px,auto));gap:10px;padding:12px;border:1px solid rgba(255,255,255,.09);border-radius:20px;background:#17191b}
.status-tabs{display:flex;padding:4px;border-radius:13px;background:#0d0e10}.status-tabs button{white-space:nowrap;border-radius:10px;padding:10px 13px;font-size:12px;font-weight:800;color:rgba(255,255,255,.48)}.status-tabs button.active{background:#e50914;color:white;box-shadow:0 7px 18px -9px #e50914}
.filter-control{display:flex;align-items:center;gap:9px;min-height:46px;border:1px solid rgba(255,255,255,.1);border-radius:13px;background:#202225;padding:0 13px;color:rgba(255,255,255,.45)}.filter-control input{min-width:0;width:100%;outline:none;background:transparent;color:white}.filter-select{min-height:46px;border:1px solid rgba(255,255,255,.1);border-radius:13px;background:#202225;padding:0 13px;color:white;outline:none}
.empty-state{margin-top:28px;display:flex;min-height:330px;flex-direction:column;align-items:center;justify-content:center;border:1px dashed rgba(255,255,255,.14);border-radius:24px;background:rgba(255,255,255,.02);color:rgba(255,255,255,.45)}.empty-state>span{font-size:58px}.empty-state h3{margin-top:14px;font-size:20px;font-weight:800;color:white}.empty-state p{margin-top:6px}.empty-state button{margin-top:18px;border-radius:11px;background:#e50914;padding:10px 18px;font-weight:800;color:white}
.loader-ring{height:42px;width:42px;border:3px solid rgba(255,255,255,.15);border-top-color:#e50914;border-radius:999px;animation:spin .8s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:1180px){.filter-panel{grid-template-columns:1fr 1fr 1fr}.status-tabs{grid-column:span 3}.filter-search{grid-column:span 2}}
@media(max-width:720px){.featured-hero{min-height:470px}.featured-copy{width:100%;padding:28px}.featured-poster{display:none}.filter-panel{grid-template-columns:1fr}.status-tabs,.filter-search{grid-column:auto}.status-tabs{overflow-x:auto}.preview-strip p.text-xs{display:none}}
</style>

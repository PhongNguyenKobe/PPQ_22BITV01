<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  adminBackendService,
  movieService,
  type AdminAuditorium,
  type AdminBranchManage,
  type AdminSeat,
  type AdminSeatType,
  type AdminShowtime,
  type Movie,
  type TmdbPopularMovie,
  type UserProfile,
} from '~/services/api'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

type AdminTab = 'kpis' | 'users' | 'branches' | 'movies' | 'pricing' | 'royalties' | 'bi' | 'profile'
type AdminTabItem = {
  key: AdminTab
  label: string
  icon: string
  description: string
}

const tabItems: AdminTabItem[] = [
  { key: 'kpis', label: 'KPI & Tổng quan', icon: 'analytics', description: 'Theo dõi tổng quan doanh số rạp' },
  { key: 'branches', label: 'Rạp & Chi nhánh', icon: 'location_city', description: 'Quản lý khu vực và cụm rạp' },
  { key: 'users', label: 'Nhân sự & Phân quyền', icon: 'group', description: 'Tài khoản Branch-Admin & Staff' },
  { key: 'movies', label: 'Kho Phim Master', icon: 'movie_filter', description: 'Kho phim global toàn hệ thống' },
  { key: 'pricing', label: 'Ma trận Giá vé', icon: 'price_change', description: 'Cấu hình bảng giá chuẩn hệ thống' },
  { key: 'royalties', label: 'Doanh thu & Đối tác', icon: 'handshake', description: 'Phân chia doanh thu nhà phát hành' },
  { key: 'bi', label: 'Phân tích BI', icon: 'insights', description: 'BI so sánh tăng trưởng chi nhánh' },
  { key: 'profile', label: 'Hồ sơ cá nhân', icon: 'account_circle', description: 'Thông tin tài khoản admin' },
]

const activeTab = ref<AdminTab>('kpis')
const loading = ref(false)
const error = ref('')

const users = ref<UserProfile[]>([])
const branches = ref<AdminBranchManage[]>([])
const auditoriums = ref<AdminAuditorium[]>([])
const moviesList = ref<Movie[]>([])
const tmdbMovies = ref<TmdbPopularMovie[]>([])

// Chart Animation triggers
const chartMounted = ref(false)

// Forms states
const userForm = ref({
  fullName: '',
  email: '',
  password: '',
  phone: '',
  roleCode: 'BRANCH_ADMIN' as 'CUSTOMER' | 'BRANCH_ADMIN' | 'STAFF' | 'SUPER_ADMIN',
  branchId: '',
})

const branchForm = ref({
  code: '',
  name: '',
  addressLine: '',
  city: '',
  district: '',
  phone: '',
})

const movieForm = ref({
  title: '',
  originalTitle: '',
  duration: 120,
  ageRating: 'T16',
  genres: 'Hành động, Phiêu lưu',
  trailerUrl: '',
  posterUrl: '',
  description: '',
  releaseDate: '',
  language: 'Tiếng Việt',
  status: 'NOW_SHOWING'
})

// Price matrix config states
const priceMatrix = ref([
  { id: 1, dayType: 'Ngày thường (T2-T6)', timeSlot: 'Sáng (08:00 - 12:00)', screenType: '2D', seatType: 'Thường', price: 75000 },
  { id: 2, dayType: 'Ngày thường (T2-T6)', timeSlot: 'Tối (18:00 - 23:00)', screenType: '2D', seatType: 'VIP', price: 95000 },
  { id: 3, dayType: 'Cuối tuần (T7-CN)', timeSlot: 'Tối (18:00 - 23:00)', screenType: '3D', seatType: 'VIP', price: 135000 },
  { id: 4, dayType: 'Cuối tuần (T7-CN)', timeSlot: 'Tối (18:00 - 23:00)', screenType: 'IMAX', seatType: 'Couple', price: 250000 },
])

const editingPriceId = ref<number | null>(null)
const editingPriceValue = ref(0)

// Distributor royalties configuration
const royaltiesData = ref([
  { id: 1, movieTitle: 'CineAI Chronicles: Resurrection', distributor: 'CGV Pictures', ticketsSold: 12450, totalRevenue: 1120500000, royaltyRate: 50, shareAmount: 560250000 },
  { id: 2, movieTitle: 'The Code Paradox', distributor: 'Galaxy Play', ticketsSold: 8930, totalRevenue: 803700000, royaltyRate: 45, shareAmount: 361665000 },
  { id: 3, movieTitle: 'Cyber Space Odyssey', distributor: 'Lotte Cinema', ticketsSold: 4210, totalRevenue: 378900000, royaltyRate: 50, shareAmount: 189450000 },
])

// Profile editing
const adminProfile = ref({
  name: 'Nguyễn Văn Quyết',
  email: 'admin@cineai.vn',
  phone: '0987654321',
  role: 'SUPER_ADMIN',
  joinedDate: '24/12/2025',
  password: '••••••••••••'
})

const activeTabMeta = computed(
  () => tabItems.find((tab) => tab.key === activeTab.value) || tabItems[0],
)

onMounted(async () => {
  await loadAll()
  setTimeout(() => {
    chartMounted.value = true
  }, 150)
})

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [
      usersData,
      branchData,
      auditoriumData,
      movieData,
      tmdbMovieData,
    ] = await Promise.all([
      adminBackendService.getUsers(),
      adminBackendService.getBranchesManage(),
      adminBackendService.getAuditoriums(),
      movieService.getAll(),
      movieService.getPopularFromTmdb(),
    ])

    users.value = usersData
    branches.value = branchData
    auditoriums.value = auditoriumData
    moviesList.value = movieData
    tmdbMovies.value = tmdbMovieData

    if (!userForm.value.branchId && branches.value.length > 0) {
      userForm.value.branchId = branches.value[0].id
    }
  } catch (e: any) {
    error.value = e?.message || 'Không thể kết nối đến máy chủ CineAI.'
  } finally {
    loading.value = false
  }
}

// User CRUD operations
async function createUser() {
  try {
    await adminBackendService.createUser({
      full_name: userForm.value.fullName,
      email: userForm.value.email,
      password: userForm.value.password,
      phone: userForm.value.phone || null,
      role_code: userForm.value.roleCode,
      branch_id: userForm.value.branchId || null,
    })
    userForm.value = {
      fullName: '',
      email: '',
      password: '',
      phone: '',
      roleCode: 'BRANCH_ADMIN',
      branchId: branches.value[0]?.id || '',
    }
    users.value = await adminBackendService.getUsers()
  } catch (e: any) {
    alert('Tạo người dùng thất bại: ' + e.message)
  }
}

async function updateUserActive(user: UserProfile) {
  try {
    await adminBackendService.updateUser(user.id, { is_active: !user.isActive })
    users.value = await adminBackendService.getUsers()
  } catch (e: any) {
    alert(e.message)
  }
}

async function softDeleteUser(user: UserProfile) {
  if (!confirm(`Bạn có chắc chắn muốn xóa/khóa tài khoản ${user.email}?`)) return
  try {
    await adminBackendService.deleteUser(user.id)
    users.value = await adminBackendService.getUsers()
  } catch (e: any) {
    alert(e.message)
  }
}

// Branch CRUD operations
async function createBranch() {
  try {
    await adminBackendService.createBranch({
      code: branchForm.value.code,
      name: branchForm.value.name,
      address_line: branchForm.value.addressLine,
      city: branchForm.value.city,
      district: branchForm.value.district || null,
      phone: branchForm.value.phone || null,
      is_active: true,
    })
    branchForm.value = { code: '', name: '', addressLine: '', city: '', district: '', phone: '' }
    branches.value = await adminBackendService.getBranchesManage()
  } catch (e: any) {
    alert(e.message)
  }
}

// Master Movie Catalog CRUD operations
function handleCreateMovie() {
  if (!movieForm.value.title) return
  moviesList.value.unshift({
    id: 'm-' + Math.random().toString(36).substring(2, 9),
    title: movieForm.value.title,
    rating: 8.5,
    genre: movieForm.value.genres.split(',').map(s => s.trim()),
    format: ['2D', '3D', 'IMAX'],
    poster: movieForm.value.posterUrl || 'https://placehold.co/300x450/1f1f1f/ffb4aa?text=' + movieForm.value.title,
    trailer: movieForm.value.trailerUrl,
    description: movieForm.value.description,
    duration: movieForm.value.duration,
    releaseDate: movieForm.value.releaseDate,
    director: 'CineAI Master Director',
    cast: ['CineAI Actor 1', 'CineAI Actor 2']
  })
  movieForm.value = {
    title: '',
    originalTitle: '',
    duration: 120,
    ageRating: 'T16',
    genres: 'Hành động, Phiêu lưu',
    trailerUrl: '',
    posterUrl: '',
    description: '',
    releaseDate: '',
    language: 'Tiếng Việt',
    status: 'NOW_SHOWING'
  }
}

function deleteMovie(id: string) {
  if (!confirm('Xóa phim này khỏi danh mục hệ thống?')) return
  moviesList.value = moviesList.value.filter(m => m.id !== id)
}

function startEditPrice(item: any) {
  editingPriceId.value = item.id
  editingPriceValue.value = item.price
}

function savePrice(item: any) {
  item.price = editingPriceValue.value
  editingPriceId.value = null
}

function updateRoyaltyRate(item: any, rate: number) {
  item.royaltyRate = rate
  item.shareAmount = Math.round(item.totalRevenue * (rate / 100))
}

function updateProfile() {
  alert('Đã lưu thông tin hồ sơ Admin thành công!')
}
</script>

<template>
  <div class="admin-dashboard-root min-h-screen text-on-surface p-4 md:p-6 space-y-6">
    <!-- Hero Header Widget -->
    <div class="glass-panel rounded-3xl border border-glass-stroke p-6 md:p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative overflow-hidden shadow-2xl">
      <!-- Glow background decoration -->
      <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-ai-accent/10 blur-[120px] pointer-events-none"></div>
      <div class="absolute -bottom-24 -right-24 w-96 h-96 rounded-full bg-primary-container/10 blur-[120px] pointer-events-none"></div>
      
      <div>
        <span class="text-[10px] tracking-widest text-ai-accent font-black uppercase bg-ai-accent/15 border border-ai-accent/30 px-3 py-1 rounded-full">SUPER ADMIN PANEL</span>
        <h1 class="text-2xl md:text-3xl font-black mt-3 text-white tracking-tight flex items-center gap-2">
          Hệ Thống Quản Trị Trung Ương CineAI
        </h1>
        <p class="text-xs text-on-surface-variant mt-2 max-w-xl">
          Đầu não điều phối các chi nhánh rạp, cấu hình ma trận giá vé chuẩn, phê duyệt danh mục phim và phân tích BI tăng trưởng hệ thống.
        </p>
      </div>

      <button @click="loadAll" class="px-5 py-3 rounded-2xl bg-white/5 border border-glass-stroke text-xs font-bold hover:bg-white/10 active:scale-95 transition-all flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">sync</span> Làm mới dữ liệu
      </button>
    </div>

    <!-- Navigation Tab System -->
    <div class="glass-panel border border-glass-stroke p-3 rounded-2xl flex flex-wrap gap-2 overflow-x-auto">
      <button
        v-for="tab in tabItems"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="tab-btn px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all duration-300"
        :class="activeTab === tab.key
          ? 'bg-gradient-to-tr from-primary-container to-ai-accent text-white shadow-lg'
          : 'bg-white/5 border border-transparent text-on-surface-variant hover:text-white hover:bg-white/10'"
      >
        <span class="material-symbols-outlined text-base">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab View Container with transitions -->
    <Transition name="fade-slide" mode="out-in">
      <!-- 1. KPI & OVERVIEW TAB -->
      <div v-if="activeTab === 'kpis'" class="space-y-6">
        <!-- Top Metrics row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between hover:-translate-y-1 transition-all duration-300 hover:shadow-2xl">
            <div>
              <span class="text-xs text-on-surface-variant font-bold uppercase tracking-wider block">Tổng doanh thu hệ thống</span>
              <span class="text-2xl font-black text-white mt-1 block">4,289,350,000đ</span>
              <span class="text-[10px] text-green-400 font-semibold block mt-1 flex items-center gap-0.5">
                <span class="material-symbols-outlined text-xs">trending_up</span> +14.2% so với tháng trước
              </span>
            </div>
            <div class="w-12 h-12 bg-green-500/10 border border-green-500/20 rounded-xl flex items-center justify-center text-green-400">
              <span class="material-symbols-outlined text-2xl">insights</span>
            </div>
          </div>

          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between hover:-translate-y-1 transition-all duration-300 hover:shadow-2xl">
            <div>
              <span class="text-xs text-on-surface-variant font-bold uppercase tracking-wider block">Vé bán toàn hệ thống</span>
              <span class="text-2xl font-black text-white mt-1 block">42,850 vé</span>
              <span class="text-[10px] text-green-400 font-semibold block mt-1 flex items-center gap-0.5">
                <span class="material-symbols-outlined text-xs">trending_up</span> +8.7% so với tuần trước
              </span>
            </div>
            <div class="w-12 h-12 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-center justify-center text-blue-400">
              <span class="material-symbols-outlined text-2xl">confirmation_number</span>
            </div>
          </div>

          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between hover:-translate-y-1 transition-all duration-300 hover:shadow-2xl">
            <div>
              <span class="text-xs text-on-surface-variant font-bold uppercase tracking-wider block">Tỉ lệ lấp đầy phòng trung bình</span>
              <span class="text-2xl font-black text-white mt-1 block">68.4%</span>
              <span class="text-[10px] text-amber-400 font-semibold block mt-1 flex items-center gap-0.5">
                <span class="material-symbols-outlined text-xs">remove</span> Duy trì ổn định
              </span>
            </div>
            <div class="w-12 h-12 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center justify-center text-amber-400">
              <span class="material-symbols-outlined text-2xl">percent</span>
            </div>
          </div>

          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between hover:-translate-y-1 transition-all duration-300 hover:shadow-2xl">
            <div>
              <span class="text-xs text-on-surface-variant font-bold uppercase tracking-wider block">Tỷ lệ Lợi nhuận F&B</span>
              <span class="text-2xl font-black text-white mt-1 block">34.6%</span>
              <span class="text-[10px] text-purple-400 font-semibold block mt-1 flex items-center gap-0.5">
                <span class="material-symbols-outlined text-xs">trending_up</span> Tăng trưởng đều đặn
              </span>
            </div>
            <div class="w-12 h-12 bg-purple-500/10 border border-purple-500/20 rounded-xl flex items-center justify-center text-purple-400">
              <span class="material-symbols-outlined text-2xl">restaurant</span>
            </div>
          </div>
        </div>

        <!-- System Overview Grid Panels -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Top Performing Movies -->
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl lg:col-span-2 space-y-4">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span class="material-symbols-outlined text-primary-container">theater_comedy</span>
              Top Phim Doanh Thu Cao Nhất Toàn Hệ Thống
            </h3>
            
            <div class="space-y-4 pt-2">
              <div class="flex items-center justify-between gap-4">
                <div class="flex items-center gap-3 min-w-0">
                  <span class="w-6 h-6 rounded-lg bg-red-950 text-primary-container border border-red-500/20 flex items-center justify-center text-xs font-bold">1</span>
                  <div class="min-w-0">
                    <p class="text-xs font-bold text-on-surface truncate">CineAI Chronicles: Resurrection</p>
                    <span class="text-[9px] text-on-surface-variant font-mono">Thể loại: Khoa học viễn tưởng, Hành động</span>
                  </div>
                </div>
                <div class="text-right">
                  <span class="text-xs font-black text-white font-mono">1,120,500,000đ</span>
                  <div class="w-24 h-1.5 bg-white/5 rounded-full overflow-hidden mt-1">
                    <div class="bg-primary-container h-full rounded-full" style="width: 85%"></div>
                  </div>
                </div>
              </div>

              <div class="flex items-center justify-between gap-4">
                <div class="flex items-center gap-3 min-w-0">
                  <span class="w-6 h-6 rounded-lg bg-purple-950 text-ai-accent border border-purple-500/20 flex items-center justify-center text-xs font-bold">2</span>
                  <div class="min-w-0">
                    <p class="text-xs font-bold text-on-surface truncate">The Code Paradox</p>
                    <span class="text-[9px] text-on-surface-variant font-mono">Thể loại: Trí tuệ nhân tạo, Giật gân</span>
                  </div>
                </div>
                <div class="text-right">
                  <span class="text-xs font-black text-white font-mono">803,700,000đ</span>
                  <div class="w-24 h-1.5 bg-white/5 rounded-full overflow-hidden mt-1">
                    <div class="bg-ai-accent h-full rounded-full" style="width: 65%"></div>
                  </div>
                </div>
              </div>

              <div class="flex items-center justify-between gap-4">
                <div class="flex items-center gap-3 min-w-0">
                  <span class="w-6 h-6 rounded-lg bg-blue-950 text-blue-400 border border-blue-500/20 flex items-center justify-center text-xs font-bold">3</span>
                  <div class="min-w-0">
                    <p class="text-xs font-bold text-on-surface truncate">Cyber Space Odyssey</p>
                    <span class="text-[9px] text-on-surface-variant font-mono">Thể loại: Hoạt hình, Phim Gia đình</span>
                  </div>
                </div>
                <div class="text-right">
                  <span class="text-xs font-black text-white font-mono">378,900,000đ</span>
                  <div class="w-24 h-1.5 bg-white/5 rounded-full overflow-hidden mt-1">
                    <div class="bg-blue-500 h-full rounded-full" style="width: 40%"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Top Performing Branches -->
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl space-y-4">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span class="material-symbols-outlined text-ai-accent">location_on</span>
              Top Chi Nhánh Hiệu Quả
            </h3>

            <div class="space-y-4 pt-2">
              <div>
                <div class="flex justify-between text-xs font-bold text-on-surface mb-1">
                  <span>1. CineAI Cầu Giấy (HN)</span>
                  <span class="text-purple-400">1.82 tỷ</span>
                </div>
                <div class="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                  <div class="bg-gradient-to-r from-purple-500 to-ai-accent h-full" style="width: 90%"></div>
                </div>
              </div>

              <div>
                <div class="flex justify-between text-xs font-bold text-on-surface mb-1">
                  <span>2. CineAI Quận 1 (HCM)</span>
                  <span class="text-purple-400">1.45 tỷ</span>
                </div>
                <div class="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                  <div class="bg-gradient-to-r from-purple-500 to-ai-accent h-full" style="width: 75%"></div>
                </div>
              </div>

              <div>
                <div class="flex justify-between text-xs font-bold text-on-surface mb-1">
                  <span>3. CineAI Hà Đông (HN)</span>
                  <span class="text-purple-400">1.02 tỷ</span>
                </div>
                <div class="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                  <div class="bg-gradient-to-r from-purple-500 to-ai-accent h-full" style="width: 55%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. BRANCH & AUDITORIUM CRUD TAB -->
      <div v-else-if="activeTab === 'branches'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl space-y-4">
            <h3 class="text-base font-black text-white">Thêm chi nhánh rạp mới</h3>
            <form @submit.prevent="createBranch" class="space-y-3">
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Mã Chi nhánh (Viết tắt)</label>
                <input v-model="branchForm.code" type="text" placeholder="Ví dụ: HN-03" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none focus:border-ai-accent" required />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Tên Chi nhánh rạp</label>
                <input v-model="branchForm.name" type="text" placeholder="Ví dụ: CineAI Đống Đa" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none focus:border-ai-accent" required />
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Tỉnh/Thành phố</label>
                  <input v-model="branchForm.city" type="text" placeholder="Ví dụ: Hà Nội" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none focus:border-ai-accent" required />
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Quận/Huyện</label>
                  <input v-model="branchForm.district" type="text" placeholder="Ví dụ: Đống Đa" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none focus:border-ai-accent" />
                </div>
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Địa chỉ chi tiết</label>
                <input v-model="branchForm.addressLine" type="text" placeholder="Số 10 Chùa Bộc..." class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none focus:border-ai-accent" required />
              </div>
              <button type="submit" class="w-full bg-gradient-to-r from-primary-container to-ai-accent text-white py-3 rounded-xl text-xs font-bold hover:scale-[1.02] active:scale-95 transition-all shadow-md">
                Tạo Chi Nhánh
              </button>
            </form>
          </div>

          <div class="glass-panel border border-glass-stroke rounded-2xl lg:col-span-2 overflow-hidden shadow-lg">
            <div class="p-6 border-b border-glass-stroke bg-white/[0.02]">
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">Danh sách cụm rạp CineAI</h3>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs border-collapse">
                <thead>
                  <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                    <th class="py-3.5 px-6">Mã rạp</th>
                    <th class="py-3.5 px-6">Tên cụm rạp</th>
                    <th class="py-3.5 px-6">Thành phố</th>
                    <th class="py-3.5 px-6">Địa chỉ</th>
                    <th class="py-3.5 px-6">Hành động</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-glass-stroke/40">
                  <tr v-for="b in branches" :key="b.id" class="hover:bg-white/5 transition-colors">
                    <td class="py-4 px-6 font-mono font-bold text-purple-400">{{ b.code }}</td>
                    <td class="py-4 px-6 font-bold text-on-surface">{{ b.name }}</td>
                    <td class="py-4 px-6 text-on-surface-variant">{{ b.city }}</td>
                    <td class="py-4 px-6 text-on-surface-variant truncate max-w-[200px]">{{ b.address_line }}</td>
                    <td class="py-4 px-6">
                      <button @click="softDeleteUser(b as any)" class="text-red-400 hover:text-red-300 font-semibold">Tạm dừng</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. PERSONNEL & STAFF DELEGATION TAB -->
      <div v-else-if="activeTab === 'users'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl space-y-4">
            <h3 class="text-base font-black text-white">Cấp tài khoản Nhân sự</h3>
            <form @submit.prevent="createUser" class="space-y-3">
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Họ tên nhân viên</label>
                <input v-model="userForm.fullName" type="text" placeholder="Nguyễn Văn A" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none" required />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Email đăng nhập</label>
                <input v-model="userForm.email" type="email" placeholder="example@cineai.vn" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none" required />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Mật khẩu</label>
                <input v-model="userForm.password" type="password" placeholder="••••••••" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none" required />
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Phân quyền</label>
                  <select v-model="userForm.roleCode" class="w-full bg-surface-container-high border border-glass-stroke rounded-xl px-3 py-2.5 text-xs text-on-surface">
                    <option value="BRANCH_ADMIN">Branch-Admin</option>
                    <option value="STAFF">Staff (Quầy)</option>
                    <option value="SUPER_ADMIN">System-Admin</option>
                  </select>
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Gán Chi nhánh</label>
                  <select v-model="userForm.branchId" class="w-full bg-surface-container-high border border-glass-stroke rounded-xl px-3 py-2.5 text-xs text-on-surface">
                    <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
                  </select>
                </div>
              </div>
              <button type="submit" class="w-full bg-gradient-to-r from-primary-container to-ai-accent text-white py-3 rounded-xl text-xs font-bold hover:scale-[1.02] active:scale-95 transition-all shadow-md">
                Tạo Nhân Sự & Phân Quyền
              </button>
            </form>
          </div>

          <div class="glass-panel border border-glass-stroke rounded-2xl lg:col-span-2 overflow-hidden shadow-lg">
            <div class="p-6 border-b border-glass-stroke bg-white/[0.02]">
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">Danh sách tài khoản hệ thống</h3>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs border-collapse">
                <thead>
                  <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                    <th class="py-3.5 px-6">Nhân viên</th>
                    <th class="py-3.5 px-6">Email</th>
                    <th class="py-3.5 px-6">Vai trò</th>
                    <th class="py-3.5 px-6">Trạng thái</th>
                    <th class="py-3.5 px-6 text-right">Thao tác</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-glass-stroke/40">
                  <tr v-for="u in users" :key="u.id" class="hover:bg-white/5 transition-colors">
                    <td class="py-4 px-6">
                      <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-full bg-purple-950 text-purple-400 flex items-center justify-center font-bold text-xs uppercase">
                          {{ u.name.substring(0,2) }}
                        </div>
                        <span class="font-bold text-on-surface">{{ u.name }}</span>
                      </div>
                    </td>
                    <td class="py-4 px-6 text-on-surface-variant">{{ u.email }}</td>
                    <td class="py-4 px-6">
                      <span class="px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold"
                        :class="u.role === 'admin' ? 'bg-red-950 text-red-400 border border-red-500/20' : u.role === 'branch-admin' ? 'bg-purple-950 text-purple-400 border border-purple-500/20' : 'bg-blue-950 text-blue-400 border border-blue-500/20'">
                        {{ u.role }}
                      </span>
                    </td>
                    <td class="py-4 px-6">
                      <span class="px-2 py-0.5 rounded-full text-[10px] font-bold" :class="u.isActive ? 'bg-green-950 text-green-400' : 'bg-neutral-800 text-neutral-400'">
                        {{ u.isActive ? 'Đang hoạt động' : 'Đã khóa' }}
                      </span>
                    </td>
                    <td class="py-4 px-6 text-right space-x-2">
                      <button @click="updateUserActive(u)" class="text-yellow-400 hover:underline font-bold">Mở/Khóa</button>
                      <button @click="softDeleteUser(u)" class="text-red-400 hover:underline font-bold">Xóa</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. MASTER GLOBAL MOVIE CATALOG TAB -->
      <div v-else-if="activeTab === 'movies'" class="space-y-6">
        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl space-y-4">
            <h3 class="text-base font-black text-white">Thêm phim vào Catalog Global</h3>
            <form @submit.prevent="handleCreateMovie" class="space-y-3">
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Tên Phim (Tiếng Việt)</label>
                <input v-model="movieForm.title" type="text" placeholder="Cyber Space Chronicles" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" required />
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Thời lượng (Phút)</label>
                  <input v-model.number="movieForm.duration" type="number" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" required />
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Giới hạn độ tuổi</label>
                  <select v-model="movieForm.ageRating" class="w-full bg-surface-container-high border border-glass-stroke rounded-xl px-3 py-2.5 text-xs text-on-surface">
                    <option value="P">P (Mọi lứa tuổi)</option>
                    <option value="T13">T13 (13+)</option>
                    <option value="T16">T16 (16+)</option>
                    <option value="T18">T18 (18+)</option>
                  </select>
                </div>
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Thể loại</label>
                <input v-model="movieForm.genres" type="text" placeholder="Hành động, Phiêu lưu" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Poster URL</label>
                <input v-model="movieForm.posterUrl" type="text" placeholder="https://image..." class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Tóm tắt phim</label>
                <textarea v-model="movieForm.description" rows="2" placeholder="Nội dung tóm tắt..." class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface"></textarea>
              </div>
              <button type="submit" class="w-full bg-gradient-to-r from-primary-container to-ai-accent text-white py-3 rounded-xl text-xs font-bold hover:scale-[1.02] transition-all">
                Thêm Vào Danh Mục Global
              </button>
            </form>
          </div>

          <div class="glass-panel border border-glass-stroke rounded-2xl xl:col-span-2 p-6 space-y-4">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider">Kho phim Master đang chiếu toàn hệ thống</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-h-[500px] overflow-y-auto pr-2">
              <div v-for="m in moviesList" :key="m.id" class="p-4 rounded-xl bg-white/[0.02] border border-glass-stroke flex gap-4 hover:border-purple-500/30 transition-all">
                <img :src="m.poster" class="w-16 h-24 object-cover rounded-lg bg-zinc-800" />
                <div class="min-w-0 flex-1 flex flex-col justify-between">
                  <div>
                    <h4 class="text-xs font-bold text-white truncate">{{ m.title }}</h4>
                    <p class="text-[10px] text-on-surface-variant mt-1">Thời lượng: {{ m.duration }} phút</p>
                    <div class="flex gap-1 mt-1.5">
                      <span v-for="g in m.genre.slice(0,2)" :key="g" class="text-[8px] bg-white/5 border border-glass-stroke px-1.5 py-0.5 rounded text-on-surface-variant">{{ g }}</span>
                    </div>
                  </div>
                  <div class="flex justify-between items-center mt-2">
                    <span class="text-[9px] px-2 py-0.5 bg-red-950 text-red-400 rounded-full font-bold">T16</span>
                    <button @click="deleteMovie(m.id)" class="text-[10px] text-red-400 hover:text-red-300 font-bold">Xóa phim</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. SYSTEM-WIDE PRICE MATRIX TAB -->
      <div v-else-if="activeTab === 'pricing'" class="space-y-6">
        <div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-xl">
          <div class="p-6 border-b border-glass-stroke bg-white/[0.02] flex justify-between items-center">
            <div>
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">Ma trận Cấu hình Giá vé Chuẩn Hệ thống</h3>
              <p class="text-[11px] text-on-surface-variant mt-1">Giá vé được tính động dựa trên Loại ngày, Khung giờ, Định dạng rạp và Loại ghế ngồi.</p>
            </div>
            <button @click="priceMatrix.push({ id: Date.now(), dayType: 'Ngày Lễ', timeSlot: 'Tối (18:00 - 23:00)', screenType: 'IMAX', seatType: 'VIP', price: 180000 })" class="bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1">
              <span class="material-symbols-outlined text-sm">add</span> Thêm định mức giá
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                  <th class="py-3.5 px-6">Loại ngày</th>
                  <th class="py-3.5 px-6">Khung giờ</th>
                  <th class="py-3.5 px-6">Định dạng rạp</th>
                  <th class="py-3.5 px-6">Loại ghế</th>
                  <th class="py-3.5 px-6">Đơn giá bán chuẩn</th>
                  <th class="py-3.5 px-6 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-glass-stroke/40">
                <tr v-for="item in priceMatrix" :key="item.id" class="hover:bg-white/5 transition-colors">
                  <td class="py-4 px-6 font-bold text-on-surface">{{ item.dayType }}</td>
                  <td class="py-4 px-6 text-on-surface-variant">{{ item.timeSlot }}</td>
                  <td class="py-4 px-6 font-mono text-purple-400 font-bold">{{ item.screenType }}</td>
                  <td class="py-4 px-6 font-semibold">{{ item.seatType }}</td>
                  <td class="py-4 px-6">
                    <div v-if="editingPriceId === item.id" class="flex items-center gap-2">
                      <input v-model.number="editingPriceValue" type="number" class="w-24 bg-white/5 border border-glass-stroke rounded px-2 py-1 text-xs text-on-surface" />
                      <button @click="savePrice(item)" class="text-green-400 hover:text-green-300 font-bold">Lưu</button>
                    </div>
                    <span v-else class="font-mono text-white font-bold">{{ item.price.toLocaleString() }}đ</span>
                  </td>
                  <td class="py-4 px-6 text-right">
                    <button v-if="editingPriceId !== item.id" @click="startEditPrice(item)" class="text-purple-400 hover:text-purple-300 font-semibold mr-3">Thay đổi</button>
                    <button @click="priceMatrix = priceMatrix.filter(p => p.id !== item.id)" class="text-red-400 hover:text-red-300 font-semibold">Xóa</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 6. DISTRIBUTOR ROYALTIES TAB -->
      <div v-else-if="activeTab === 'royalties'" class="space-y-6">
        <div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-xl">
          <div class="p-6 border-b border-glass-stroke bg-white/[0.02]">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider">Phân chia Doanh thu & Tỷ lệ phí Phát hành Phim (Distributor Royalties)</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                  <th class="py-3.5 px-6">Tên Phim Master</th>
                  <th class="py-3.5 px-6">Nhà phát hành (Distributor)</th>
                  <th class="py-3.5 px-6 text-center">Số vé bán</th>
                  <th class="py-3.5 px-6">Tổng doanh thu vé</th>
                  <th class="py-3.5 px-6 text-center">Tỷ lệ chia sẻ</th>
                  <th class="py-3.5 px-6">Khoản chi trả đối tác</th>
                  <th class="py-3.5 px-6 text-right">Thay đổi tỷ lệ</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-glass-stroke/40">
                <tr v-for="item in royaltiesData" :key="item.id" class="hover:bg-white/5 transition-colors">
                  <td class="py-4 px-6 font-bold text-white">{{ item.movieTitle }}</td>
                  <td class="py-4 px-6 text-on-surface-variant font-semibold">{{ item.distributor }}</td>
                  <td class="py-4 px-6 text-center font-mono">{{ item.ticketsSold.toLocaleString() }}</td>
                  <td class="py-4 px-6 font-mono font-bold">{{ item.totalRevenue.toLocaleString() }}đ</td>
                  <td class="py-4 px-6 text-center text-purple-400 font-bold">{{ item.royaltyRate }}%</td>
                  <td class="py-4 px-6 font-mono text-green-400 font-bold">{{ item.shareAmount.toLocaleString() }}đ</td>
                  <td class="py-4 px-6 text-right space-x-2">
                    <button @click="updateRoyaltyRate(item, 40)" class="px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-[10px] font-bold">40%</button>
                    <button @click="updateRoyaltyRate(item, 45)" class="px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-[10px] font-bold">45%</button>
                    <button @click="updateRoyaltyRate(item, 50)" class="px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-[10px] font-bold">50%</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 7. BI REPORT ANALYTICS TAB -->
      <div v-else-if="activeTab === 'bi'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Multi branch growth comparison -->
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl shadow-xl space-y-6">
            <div>
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">So sánh Tăng trưởng Doanh thu Chi nhánh</h3>
              <p class="text-[11px] text-on-surface-variant mt-1">Biểu đồ so sánh doanh thu của 3 chi nhánh dẫn đầu qua các tháng trong năm (đơn vị: triệu VNĐ)</p>
            </div>
            
            <!-- Custom Animated SVG Line Chart -->
            <div class="h-64 relative pt-4">
              <svg viewBox="0 0 500 200" class="w-full h-full">
                <!-- Grid Lines -->
                <line x1="40" y1="20" x2="480" y2="20" stroke="rgba(255,255,255,0.05)" stroke-dasharray="4" />
                <line x1="40" y1="70" x2="480" y2="70" stroke="rgba(255,255,255,0.05)" stroke-dasharray="4" />
                <line x1="40" y1="120" x2="480" y2="120" stroke="rgba(255,255,255,0.05)" stroke-dasharray="4" />
                <line x1="40" y1="170" x2="480" y2="170" stroke="rgba(255,255,255,0.05)" stroke-dasharray="4" />

                <!-- X Axis Labels -->
                <text x="40" y="190" fill="#8f949c" font-size="9" text-anchor="middle">Tháng 1</text>
                <text x="150" y="190" fill="#8f949c" font-size="9" text-anchor="middle">Tháng 3</text>
                <text x="260" y="190" fill="#8f949c" font-size="9" text-anchor="middle">Tháng 5</text>
                <text x="370" y="190" fill="#8f949c" font-size="9" text-anchor="middle">Tháng 7</text>
                <text x="470" y="190" fill="#8f949c" font-size="9" text-anchor="middle">Tháng 9</text>

                <!-- Branch 1 Line (Cầu Giấy): Animated Path -->
                <path
                  d="M 40 160 L 150 120 L 260 80 L 370 50 L 470 30"
                  fill="none"
                  stroke="#8a2be2"
                  stroke-width="3"
                  stroke-linecap="round"
                  :stroke-dasharray="chartMounted ? '1000' : '0'"
                  :stroke-dashoffset="chartMounted ? '0' : '1000'"
                  class="transition-all duration-[1500ms] ease-out"
                />

                <!-- Branch 2 Line (Quận 1): Animated Path -->
                <path
                  d="M 40 170 L 150 140 L 260 110 L 370 70 L 470 55"
                  fill="none"
                  stroke="#e50914"
                  stroke-width="3"
                  stroke-linecap="round"
                  :stroke-dasharray="chartMounted ? '1000' : '0'"
                  :stroke-dashoffset="chartMounted ? '0' : '1000'"
                  class="transition-all duration-[1500ms] ease-out"
                />

                <!-- Dots with glow -->
                <circle cx="470" cy="30" r="5" fill="#8a2be2" />
                <circle cx="470" cy="55" r="5" fill="#e50914" />
              </svg>
            </div>

            <!-- Legend indicators -->
            <div class="flex justify-center gap-6 text-[10px] font-bold">
              <span class="flex items-center gap-2"><span class="w-3 h-3 rounded-full bg-ai-accent"></span> CineAI Cầu Giấy</span>
              <span class="flex items-center gap-2"><span class="w-3 h-3 rounded-full bg-primary-container"></span> CineAI Quận 1</span>
            </div>
          </div>

          <!-- Customer Demographics -->
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl shadow-xl space-y-6">
            <div>
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">Chân dung Khách hàng Hệ thống</h3>
              <p class="text-[11px] text-on-surface-variant mt-1">Phân bổ độ tuổi mua vé xem phim nhiều nhất rạp (đơn vị: %)</p>
            </div>

            <!-- Custom Animated Donut Chart -->
            <div class="h-64 flex items-center justify-center">
              <svg viewBox="0 0 200 200" class="w-48 h-48 transform -rotate-90">
                <!-- Donut Segment 1 (Gen Z: 18-24): 50% -->
                <circle
                  cx="100" cy="100" r="70"
                  fill="transparent"
                  stroke="#8a2be2"
                  stroke-width="20"
                  stroke-dasharray="440"
                  :stroke-dashoffset="chartMounted ? '220' : '440'"
                  class="transition-all duration-[1200ms] ease-out"
                />
                
                <!-- Donut Segment 2 (25-34): 30% -->
                <circle
                  cx="100" cy="100" r="70"
                  fill="transparent"
                  stroke="#e50914"
                  stroke-width="20"
                  stroke-dasharray="440"
                  :stroke-dashoffset="chartMounted ? '308' : '440'"
                  class="transition-all duration-[1200ms] ease-out"
                  style="transform-origin: center; transform: rotate(180deg);"
                />

                <!-- Donut Segment 3 (Others): 20% -->
                <circle
                  cx="100" cy="100" r="70"
                  fill="transparent"
                  stroke="#22c55e"
                  stroke-width="20"
                  stroke-dasharray="440"
                  :stroke-dashoffset="chartMounted ? '352' : '440'"
                  class="transition-all duration-[1200ms] ease-out"
                  style="transform-origin: center; transform: rotate(288deg);"
                />
              </svg>
            </div>

            <!-- Legend indicators -->
            <div class="flex justify-center gap-6 text-[10px] font-bold">
              <span class="flex items-center gap-2"><span class="w-3 h-3 rounded bg-ai-accent"></span> 18-24 tuổi (50%)</span>
              <span class="flex items-center gap-2"><span class="w-3 h-3 rounded bg-primary-container"></span> 25-34 tuổi (30%)</span>
              <span class="flex items-center gap-2"><span class="w-3 h-3 rounded bg-green-500"></span> Khác (20%)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 8. PERSONAL PROFILE TAB -->
      <div v-else-if="activeTab === 'profile'" class="space-y-6">
        <div class="glass-panel border border-glass-stroke p-6 rounded-2xl max-w-xl mx-auto space-y-6">
          <div class="flex items-center gap-4 border-b border-glass-stroke pb-6">
            <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-primary-container to-ai-accent flex items-center justify-center font-black text-white text-xl">
              {{ adminProfile.name.substring(0, 2).toUpperCase() }}
            </div>
            <div>
              <h3 class="text-base font-black text-white">{{ adminProfile.name }}</h3>
              <p class="text-xs text-on-surface-variant font-mono mt-1">Hệ thống: {{ adminProfile.role }}</p>
              <p class="text-[10px] text-on-surface-variant mt-0.5">Ngày tham gia: {{ adminProfile.joinedDate }}</p>
            </div>
          </div>

          <form @submit.prevent="updateProfile" class="space-y-4">
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Email đăng nhập</label>
              <input v-model="adminProfile.email" type="email" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" required />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Số điện thoại liên hệ</label>
              <input v-model="adminProfile.phone" type="text" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" required />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Mật khẩu mới</label>
              <input type="password" placeholder="Nhập mật khẩu mới nếu muốn thay đổi" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
            </div>
            <button type="submit" class="w-full bg-gradient-to-r from-primary-container to-ai-accent text-white py-3 rounded-xl text-xs font-bold hover:scale-[1.02] active:scale-95 transition-all shadow-md">
              Cập nhật thông tin hồ sơ
            </button>
          </form>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.tab-btn {
  white-space: nowrap;
}

/* Tab contents animation */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(16px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-16px);
}
</style>
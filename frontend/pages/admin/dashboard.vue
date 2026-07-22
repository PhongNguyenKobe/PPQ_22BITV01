 <script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { adminBackendService, adminService, type BackendBranch, type Movie, type MovieRequest, type UserProfile } from '~/services/api'

definePageMeta({
  layout: 'admin'
})

const activeTab = ref<'movies' | 'branches' | 'users' | 'approvals'>('movies')

// Stats
const totalBranches = ref(0)
const totalMovies = ref(0)
const totalUsers = ref(0)
const totalRevenue = ref(0)
const revenueChartData = ref<{ label: string; value: number }[]>([])

// Lists
const moviesList = ref<Movie[]>([])
const usersList = ref<UserProfile[]>([])
const branchOptions = ref<BackendBranch[]>([])
const movieRequests = ref<MovieRequest[]>([])
const branchesList = ref([
  { id: 'b1', name: 'CineAI Hùng Vương', city: 'TP. Hồ Chí Minh', screens: 6, status: 'Hoạt động' },
  { id: 'b2', name: 'CineAI Sala Q2', city: 'TP. Hồ Chí Minh', screens: 8, status: 'Hoạt động' },
  { id: 'b3', name: 'CineAI Nguyễn Du', city: 'TP. Hồ Chí Minh', screens: 4, status: 'Hoạt động' },
  { id: 'b4', name: 'CineAI Vincom Bà Triệu', city: 'Hà Nội', screens: 5, status: 'Hoạt động' },
  { id: 'b5', name: 'CineAI Đà Nẵng Plaza', city: 'Đà Nẵng', screens: 4, status: 'Bảo trì' }
])

// Add/Edit Movie Modal Dialog Form State
const showAddMovieModal = ref(false)
const editingMovieId = ref<string | null>(null)
const newMovieTitle = ref('')
const newMovieGenre = ref('')
const newMovieDirector = ref('')
const newMovieDuration = ref(120)
const newMovieRating = ref(4.5)

const showRoleModal = ref(false)
const selectedUser = ref<UserProfile | null>(null)
const selectedRoleCode = ref<'CUSTOMER' | 'BRANCH_ADMIN' | 'STAFF' | 'SUPER_ADMIN'>('CUSTOMER')
const selectedBranchId = ref('')

onMounted(async () => {
  try {
    const stats = await adminService.getSuperAdminStats()
    totalBranches.value = stats.totalBranches
    totalMovies.value = stats.totalMovies
    totalUsers.value = stats.totalUsers
    totalRevenue.value = stats.totalRevenue
    revenueChartData.value = stats.revenueChartData
    moviesList.value = stats.moviesList
    usersList.value = await adminBackendService.getUsers()
    branchOptions.value = await adminBackendService.getBranches()
    movieRequests.value = await adminBackendService.getMovieRequests()
  } catch (e) {
    console.error('Failed to load admin stats:', e)
  }
})

function openAddMovieModal() {
  editingMovieId.value = null
  newMovieTitle.value = ''
  newMovieGenre.value = ''
  newMovieDirector.value = ''
  newMovieDuration.value = 120
  newMovieRating.value = 4.5
  showAddMovieModal.value = true
}

function openEditMovieModal(movie: Movie) {
  editingMovieId.value = movie.id
  newMovieTitle.value = movie.title
  newMovieGenre.value = movie.genre.join(', ')
  newMovieDirector.value = movie.director
  newMovieDuration.value = movie.duration
  newMovieRating.value = movie.rating
  showAddMovieModal.value = true
}

function handleDeleteMovie(id: string) {
  moviesList.value = moviesList.value.filter(m => m.id !== id)
  totalMovies.value = moviesList.value.length
}

async function loadMovieRequests() {
  movieRequests.value = await adminBackendService.getMovieRequests()
}

async function handleApproveRequest(requestId: string) {
  await adminBackendService.approveMovieRequest(requestId)
  await loadMovieRequests()
}

async function handleRejectRequest(requestId: string) {
  await adminBackendService.rejectMovieRequest(requestId, 'Từ chối bởi admin website')
  await loadMovieRequests()
}

function openRoleModal(user: UserProfile) {
  selectedUser.value = user
  selectedRoleCode.value = user.role === 'branch-admin' ? 'BRANCH_ADMIN' : user.role === 'admin' ? 'SUPER_ADMIN' : 'CUSTOMER'
  selectedBranchId.value = user.branchId || ''
  showRoleModal.value = true
}

async function handleSaveUserRole() {
  if (!selectedUser.value) return
  const updated = await adminBackendService.updateUserRole(
    selectedUser.value.id,
    selectedRoleCode.value,
    selectedBranchId.value || undefined,
  )
  usersList.value = usersList.value.map(user => (user.id === updated.id ? updated : user))
  showRoleModal.value = false
  selectedUser.value = null
}

function handleAddMovieSubmit() {
  if (!newMovieTitle.value) return
  
  if (editingMovieId.value) {
    // Edit existing
    const idx = moviesList.value.findIndex(m => m.id === editingMovieId.value)
    if (idx !== -1) {
      moviesList.value[idx].title = newMovieTitle.value
      moviesList.value[idx].genre = newMovieGenre.value.split(',').map(s => s.trim())
      moviesList.value[idx].director = newMovieDirector.value
      moviesList.value[idx].duration = newMovieDuration.value
      moviesList.value[idx].rating = newMovieRating.value
    }
  } else {
    // Add new
    const created: Movie = {
      id: `m-${Date.now()}`,
      title: newMovieTitle.value,
      genre: newMovieGenre.value.split(',').map(s => s.trim()),
      director: newMovieDirector.value || 'N/A',
      duration: newMovieDuration.value || 120,
      rating: newMovieRating.value || 4.5,
      poster: 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=300',
      trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
      description: 'Bộ phim mới được nhập vào hệ thống CineAI.',
      releaseDate: new Date().toISOString().substring(0, 10),
      format: ['2D', '3D'],
      cast: ['Diễn viên A', 'Diễn viên B']
    }
    moviesList.value.unshift(created)
    totalMovies.value = moviesList.value.length
  }
  
  showAddMovieModal.value = false
  newMovieTitle.value = ''
  newMovieGenre.value = ''
  newMovieDirector.value = ''
}

// Find max revenue for chart proportions
const maxRevenueValue = computed(() => {
  if (revenueChartData.value.length === 0) return 1
  return Math.max(...revenueChartData.value.map(c => c.value))
})
</script>

<template>
  <div class="space-y-8">
    
    <!-- Stats Cards Overview Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      
      <!-- Revenue stats -->
      <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md">
        <div>
          <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Tổng doanh thu</span>
          <span class="text-2xl font-black text-primary">{{ totalRevenue.toLocaleString() }}đ</span>
        </div>
        <div class="w-12 h-12 bg-primary-container/10 border border-primary-container/20 rounded-xl flex items-center justify-center text-primary-container">
          <span class="material-symbols-outlined text-[28px]">monitoring</span>
        </div>
      </div>

      <!-- Branches count -->
      <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md">
        <div>
          <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Tổng chi nhánh</span>
          <span class="text-2xl font-black text-on-surface">{{ totalBranches }}</span>
        </div>
        <div class="w-12 h-12 bg-surface-container-high border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant">
          <span class="material-symbols-outlined text-[28px]">storefront</span>
        </div>
      </div>

      <!-- Movies count -->
      <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md">
        <div>
          <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Phim quản lý</span>
          <span class="text-2xl font-black text-on-surface">{{ totalMovies }}</span>
        </div>
        <div class="w-12 h-12 bg-surface-container-high border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant">
          <span class="material-symbols-outlined text-[28px]">movie</span>
        </div>
      </div>

      <!-- Users count -->
      <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md">
        <div>
          <span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Khách hàng</span>
          <span class="text-2xl font-black text-secondary">{{ totalUsers }}</span>
        </div>
        <div class="w-12 h-12 bg-secondary-container/10 border border-secondary-container/20 rounded-xl flex items-center justify-center text-secondary">
          <span class="material-symbols-outlined text-[28px]">groups</span>
        </div>
      </div>

    </div>

    <!-- Chart row -->
    <div class="glass-panel border border-glass-stroke p-6 md:p-8 rounded-2xl shadow-lg">
      <h3 class="font-bold text-base text-on-surface mb-6 flex items-center gap-2">
        <span class="material-symbols-outlined text-primary-container">bar_chart</span>
        Biểu Đồ Doanh Thu Hệ Thống
      </h3>
      
      <!-- Visual Bar Chart -->
      <div class="h-64 flex items-end gap-4 md:gap-8 justify-center pt-8 border-b border-glass-stroke">
        <div
          v-for="bar in revenueChartData"
          :key="bar.label"
          class="flex flex-col items-center flex-1 max-w-[60px] group relative"
        >
          <!-- Value popup tooltip -->
          <span class="absolute -top-8 bg-black/85 border border-glass-stroke text-[10px] font-bold text-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10 shadow-lg">
            {{ (bar.value / 1000000).toFixed(1) }}Mđ
          </span>
          <!-- Bar column -->
          <div
            class="w-full rounded-t-lg bg-gradient-to-t from-primary-container/60 to-primary-container transition-all hover:brightness-110"
            :style="{ height: `${(bar.value / maxRevenueValue) * 160}px` }"
          ></div>
          <span class="text-xs text-on-surface-variant font-bold mt-2 pb-2 truncate w-full text-center">{{ bar.label }}</span>
        </div>
      </div>
    </div>

    <!-- Data Tables Area -->
    <div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-lg">
      <!-- Tabs header -->
      <div class="bg-surface-container-high/80 border-b border-glass-stroke flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-4">
          <button
            @click="activeTab = 'movies'"
            class="text-sm font-bold pb-2 transition-all border-b-2"
            :class="activeTab === 'movies' ? 'border-primary-container text-on-surface' : 'border-transparent text-on-surface-variant hover:text-on-surface'"
          >
            Quản Lý Phim
          </button>
          <button
            @click="activeTab = 'branches'"
            class="text-sm font-bold pb-2 transition-all border-b-2"
            :class="activeTab === 'branches' ? 'border-primary-container text-on-surface' : 'border-transparent text-on-surface-variant hover:text-on-surface'"
          >
            Quản Lý Chi Nhánh
          </button>
          <button
            @click="activeTab = 'users'"
            class="text-sm font-bold pb-2 transition-all border-b-2"
            :class="activeTab === 'users' ? 'border-primary-container text-on-surface' : 'border-transparent text-on-surface-variant hover:text-on-surface'"
          >
            Quản Lý Thành Viên
          </button>
          <button
            @click="activeTab = 'approvals'"
            class="text-sm font-bold pb-2 transition-all border-b-2"
            :class="activeTab === 'approvals' ? 'border-primary-container text-on-surface' : 'border-transparent text-on-surface-variant hover:text-on-surface'"
          >
            Phê Duyệt Phim
          </button>
        </div>
        
        <button
          v-if="activeTab === 'movies'"
          @click="openAddMovieModal"
          class="bg-primary-container hover:bg-opacity-90 text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1.5 red-glow transition-all"
        >
          <span class="material-symbols-outlined text-sm">add</span>
          Thêm Phim Mới
        </button>
      </div>

      <!-- Tab Contents -->
      <div class="p-6">
        
        <!-- Movies Table -->
        <div v-if="activeTab === 'movies'" class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                <th class="py-3.5 px-4">Tên Phim</th>
                <th class="py-3.5 px-4">Đạo Diễn</th>
                <th class="py-3.5 px-4">Thể Loại</th>
                <th class="py-3.5 px-4 text-center">Thời Lượng</th>
                <th class="py-3.5 px-4 text-center">Đánh Giá</th>
                <th class="py-3.5 px-4 text-right">Thao Tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-glass-stroke/40">
              <tr v-for="movie in moviesList" :key="movie.id" class="hover:bg-white/5 transition-colors">
                <td class="py-4 px-4 font-bold text-on-surface">{{ movie.title }}</td>
                <td class="py-4 px-4 text-on-surface-variant">{{ movie.director }}</td>
                <td class="py-4 px-4 text-on-surface-variant">{{ movie.genre.join(', ') }}</td>
                <td class="py-4 px-4 text-center text-on-surface-variant font-mono">{{ movie.duration }} phút</td>
                <td class="py-4 px-4 text-center text-yellow-500 font-bold">★ {{ movie.rating.toFixed(1) }}</td>
                <td class="py-4 px-4 text-right space-x-2">
                  <button @click="openEditMovieModal(movie)" class="text-blue-400 hover:text-blue-300 font-semibold">Sửa</button>
                  <button @click="handleDeleteMovie(movie.id)" class="text-red-400 hover:text-red-300 font-semibold">Xóa</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Branches Table -->
        <div v-if="activeTab === 'branches'" class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                <th class="py-3.5 px-4">Tên Chi Nhánh</th>
                <th class="py-3.5 px-4">Khu Vực</th>
                <th class="py-3.5 px-4 text-center">Số Phòng Chiếu</th>
                <th class="py-3.5 px-4 text-center">Trạng Thái</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-glass-stroke/40">
              <tr v-for="branch in branchesList" :key="branch.id" class="hover:bg-white/5 transition-colors">
                <td class="py-4 px-4 font-bold text-on-surface">{{ branch.name }}</td>
                <td class="py-4 px-4 text-on-surface-variant">{{ branch.city }}</td>
                <td class="py-4 px-4 text-center text-on-surface-variant font-mono">{{ branch.screens }}</td>
                <td class="py-4 px-4 text-center">
                  <span class="px-2.5 py-0.5 rounded-full font-bold text-[10px]" :class="branch.status === 'Hoạt động' ? 'bg-green-950 text-green-400 border border-green-500/20' : 'bg-yellow-950 text-yellow-400 border border-yellow-500/20'">
                    {{ branch.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Users Table -->
        <div v-if="activeTab === 'users'" class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                <th class="py-3.5 px-4">Họ Tên</th>
                <th class="py-3.5 px-4">Email</th>
                <th class="py-3.5 px-4">Phân Quyền</th>
                <th class="py-3.5 px-4">Thao Tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-glass-stroke/40">
              <tr v-for="user in usersList" :key="user.id" class="hover:bg-white/5 transition-colors">
                <td class="py-4 px-4 font-bold text-on-surface">{{ user.name }}</td>
                <td class="py-4 px-4 text-on-surface-variant font-mono">{{ user.email }}</td>
                <td class="py-4 px-4 capitalize">
                  <span class="px-2.5 py-0.5 rounded-full font-bold text-[10px]" :class="user.role === 'admin' ? 'bg-red-950 text-red-400 border border-red-500/20' : user.role === 'branch-admin' ? 'bg-purple-950 text-purple-400 border border-purple-500/20' : 'bg-blue-950 text-blue-400 border border-blue-500/20'">
                    {{ user.role }}
                  </span>
                </td>
                <td class="py-4 px-4">
                  <button @click="openRoleModal(user)" class="text-primary-container font-semibold hover:underline">Chỉnh sửa</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Approvals Table -->
        <div v-if="activeTab === 'approvals'" class="overflow-x-auto">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-sm text-on-surface">Yêu cầu phim chờ duyệt</h3>
            <button @click="loadMovieRequests" class="text-xs font-bold text-primary-container hover:underline">Tải lại</button>
          </div>
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                <th class="py-3.5 px-4">Phim</th>
                <th class="py-3.5 px-4">Loại</th>
                <th class="py-3.5 px-4">Người gửi</th>
                <th class="py-3.5 px-4 text-center">Trạng thái</th>
                <th class="py-3.5 px-4 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-glass-stroke/40">
              <tr v-for="request in movieRequests" :key="request.id" class="hover:bg-white/5 transition-colors">
                <td class="py-4 px-4 font-bold text-on-surface">{{ request.payload.title }}</td>
                <td class="py-4 px-4 text-on-surface-variant uppercase font-mono">{{ request.request_type }}</td>
                <td class="py-4 px-4 text-on-surface-variant">{{ request.requested_by?.name || request.requested_by_id }}</td>
                <td class="py-4 px-4 text-center">
                  <span class="px-2.5 py-0.5 rounded-full font-bold text-[10px]" :class="request.status === 'PENDING' ? 'bg-yellow-950 text-yellow-400 border border-yellow-500/20' : request.status === 'APPROVED' ? 'bg-green-950 text-green-400 border border-green-500/20' : 'bg-red-950 text-red-400 border border-red-500/20'">
                    {{ request.status }}
                  </span>
                </td>
                <td class="py-4 px-4 text-right space-x-2">
                  <button @click="handleApproveRequest(request.id)" class="text-green-400 hover:text-green-300 font-semibold">Duyệt</button>
                  <button @click="handleRejectRequest(request.id)" class="text-red-400 hover:text-red-300 font-semibold">Từ chối</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- Add/Edit Movie Modal overlay -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showAddMovieModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-6 relative">
          <button @click="showAddMovieModal = false" class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface">
            <span class="material-symbols-outlined">close</span>
          </button>
          
          <h3 class="font-headline-md text-lg font-bold text-on-surface mb-6">{{ editingMovieId ? 'Chỉnh Sửa Phim' : 'Thêm Phim Mới' }}</h3>
          
          <form @submit.prevent="handleAddMovieSubmit" class="space-y-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Tên phim</label>
              <input v-model="newMovieTitle" type="text" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="Nhập tên phim" />
            </div>
            
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Thể loại (ngăn cách bằng dấu phẩy)</label>
              <input v-model="newMovieGenre" type="text" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="Hành Động, Viễn Tưởng" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Đạo diễn</label>
                <input v-model="newMovieDirector" type="text" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="Denis Villeneuve" />
              </div>
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Thời lượng (phút)</label>
                <input v-model.number="newMovieDuration" type="number" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Đánh giá</label>
              <input v-model.number="newMovieRating" type="number" min="0" max="10" step="0.1" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
            </div>

            <button type="submit" class="w-full bg-primary-container text-white py-3 rounded-xl text-xs font-bold hover:scale-105 active:scale-95 transition-all shadow-md red-glow">
              {{ editingMovieId ? 'Cập nhật' : 'Tạo phim mới' }}
            </button>
          </form>
        </div>
      </div>
    </transition>

    <!-- Role Edit Modal -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showRoleModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-6 relative">
          <button @click="showRoleModal = false" class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface">
            <span class="material-symbols-outlined">close</span>
          </button>

          <h3 class="font-headline-md text-lg font-bold text-on-surface mb-6">Cập nhật phân quyền</h3>

          <div v-if="selectedUser" class="mb-4 text-xs text-on-surface-variant">
            {{ selectedUser.name }} - {{ selectedUser.email }}
          </div>

          <form @submit.prevent="handleSaveUserRole" class="space-y-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Vai trò</label>
              <select v-model="selectedRoleCode" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface">
                <option value="CUSTOMER">Customer</option>
                <option value="BRANCH_ADMIN">Branch Admin</option>
                <option value="STAFF">Branch Staff</option>
                <option value="SUPER_ADMIN">Website Admin</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Chi nhánh</label>
              <select v-model="selectedBranchId" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface">
                <option value="">-- Không gán --</option>
                <option v-for="branch in branchOptions" :key="branch.id" :value="branch.id">
                  {{ branch.name }} - {{ branch.city }}
                </option>
              </select>
            </div>

            <button type="submit" class="w-full bg-primary-container text-white py-3 rounded-xl text-xs font-bold hover:scale-105 active:scale-95 transition-all shadow-md red-glow">
              Lưu thay đổi
            </button>
          </form>
        </div>
      </div>
    </transition>

  </div>
</template>


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

type AdminTab = 'users' | 'branches' | 'auditoriums' | 'seats' | 'showtimes'
type AdminTabItem = {
  key: AdminTab
  label: string
  icon: string
  description: string
}

const tabItems: AdminTabItem[] = [
  { key: 'users', label: 'Người dùng', icon: 'group', description: 'Tài khoản và phân quyền' },
  { key: 'branches', label: 'Chi nhánh', icon: 'location_city', description: 'Khu vực và cụm rạp' },
  { key: 'auditoriums', label: 'Phòng chiếu', icon: 'theaters', description: 'Màn hình và sức chứa' },
  { key: 'seats', label: 'Ghế ngồi', icon: 'event_seat', description: 'Sơ đồ ghế theo phòng' },
  { key: 'showtimes', label: 'Suất chiếu', icon: 'schedule', description: 'Lịch chiếu đang mở bán' },
]

const activeTab = ref<AdminTab>('users')
const loading = ref(false)
const error = ref('')

const users = ref<UserProfile[]>([])
const branches = ref<AdminBranchManage[]>([])
const auditoriums = ref<AdminAuditorium[]>([])
const seats = ref<AdminSeat[]>([])
const seatTypes = ref<AdminSeatType[]>([])
const showtimes = ref<AdminShowtime[]>([])
const movies = ref<Movie[]>([])
const tmdbMovies = ref<TmdbPopularMovie[]>([])

const userForm = ref({
  fullName: '',
  email: '',
  password: '',
  phone: '',
  roleCode: 'CUSTOMER' as 'CUSTOMER' | 'BRANCH_ADMIN' | 'STAFF' | 'SUPER_ADMIN',
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

const auditoriumForm = ref({
  branchId: '',
  code: '',
  name: '',
  totalSeats: 100,
  screenType: '2D',
})

const seatForm = ref({
  auditoriumId: '',
  row: 'A',
  number: 1,
  seatTypeId: 1,
})

const showtimeForm = ref({
  movieId: '',
  auditoriumId: '',
  startsAt: '',
  endsAt: '',
  basePrice: 90000,
  status: 'OPEN' as 'OPEN' | 'CLOSED' | 'CANCELLED',
})

const showtimeMovieOptions = computed(() => {
  const tmdbOptions = tmdbMovies.value.map((movie) => ({
    value: `tmdb:${movie.tmdb_id}`,
    label: `${movie.title} (TMDB)`,
  }))
  const backendOptions = movies.value.map((movie) => ({
    value: movie.id,
    label: `${movie.title} (DB)`,
  }))
  return [...tmdbOptions, ...backendOptions]
})

const stats = computed(() => ({
  users: users.value.length,
  branches: branches.value.length,
  auditoriums: auditoriums.value.length,
  seats: seats.value.length,
  showtimes: showtimes.value.length,
}))

const activeTabMeta = computed(
  () => tabItems.find((tab) => tab.key === activeTab.value) || tabItems[0],
)

const branchNameMap = computed(() => {
  const map = new Map<string, string>()
  for (const branch of branches.value) {
    map.set(branch.id, branch.name)
  }
  return map
})

onMounted(async () => {
  await loadAll()
})

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [
      usersData,
      branchData,
      auditoriumData,
      seatTypeData,
      showtimeData,
      movieData,
      tmdbMovieData,
    ] = await Promise.all([
      adminBackendService.getUsers(),
      adminBackendService.getBranchesManage(),
      adminBackendService.getAuditoriums(),
      adminBackendService.getSeatTypes(),
      adminBackendService.getShowtimes(),
      movieService.getAll(),
      movieService.getPopularFromTmdb(),
    ])

    users.value = usersData
    branches.value = branchData
    auditoriums.value = auditoriumData
    seatTypes.value = seatTypeData
    showtimes.value = showtimeData
    movies.value = movieData
    tmdbMovies.value = tmdbMovieData

    if (!showtimeForm.value.movieId && showtimeMovieOptions.value.length > 0) {
      showtimeForm.value.movieId = showtimeMovieOptions.value[0].value
    }
    if (!auditoriumForm.value.branchId && branches.value.length > 0) {
      auditoriumForm.value.branchId = branches.value[0].id
    }
    if (!seatForm.value.auditoriumId && auditoriums.value.length > 0) {
      seatForm.value.auditoriumId = auditoriums.value[0].id
    }
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải dữ liệu admin.'
  } finally {
    loading.value = false
  }
}

function roleToCode(role: UserProfile['role']) {
  if (role === 'admin') return 'SUPER_ADMIN'
  if (role === 'branch-admin') return 'BRANCH_ADMIN'
  if (role === 'staff') return 'STAFF'
  return 'CUSTOMER'
}

function toIso(value: string) {
  const date = new Date(value)
  return date.toISOString()
}

async function createUser() {
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
    roleCode: 'CUSTOMER',
    branchId: '',
  }
  users.value = await adminBackendService.getUsers()
}

async function updateUserRole(user: UserProfile) {
  const next = window.prompt('Nhập role code: CUSTOMER | BRANCH_ADMIN | STAFF | SUPER_ADMIN', roleToCode(user.role))
  if (!next) return
  const branch = window.prompt('Nhập branch id (để trống nếu không gán):', user.branchId || '')
  const updated = await adminBackendService.updateUserRole(user.id, next as any, branch || null)
  users.value = users.value.map((u) => (u.id === updated.id ? updated : u))
}

async function updateUserActive(user: UserProfile) {
  const target = !user.isActive
  await adminBackendService.updateUser(user.id, { is_active: target })
  users.value = await adminBackendService.getUsers()
}

async function softDeleteUser(user: UserProfile) {
  if (!window.confirm(`Khoá tài khoản ${user.email}?`)) return
  await adminBackendService.deleteUser(user.id)
  users.value = await adminBackendService.getUsers()
}

async function createBranch() {
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
}

async function editBranch(branch: AdminBranchManage) {
  const name = window.prompt('Tên chi nhánh', branch.name)
  if (!name) return
  const city = window.prompt('Thành phố', branch.city)
  if (!city) return
  const addressLine = window.prompt('Địa chỉ', branch.address_line)
  if (!addressLine) return
  await adminBackendService.updateBranch(branch.id, { name, city, address_line: addressLine })
  branches.value = await adminBackendService.getBranchesManage()
}

async function deleteBranch(branch: AdminBranchManage) {
  if (!window.confirm(`Xoá chi nhánh ${branch.name}?`)) return
  await adminBackendService.deleteBranch(branch.id)
  branches.value = await adminBackendService.getBranchesManage()
}

async function createAuditorium() {
  await adminBackendService.createAuditorium({
    branch_id: auditoriumForm.value.branchId,
    code: auditoriumForm.value.code,
    name: auditoriumForm.value.name,
    total_seats: auditoriumForm.value.totalSeats,
    screen_type: auditoriumForm.value.screenType,
    is_active: true,
  })
  auditoriumForm.value.code = ''
  auditoriumForm.value.name = ''
  auditoriumForm.value.totalSeats = 100
  auditoriums.value = await adminBackendService.getAuditoriums()
}

async function editAuditorium(item: AdminAuditorium) {
  const name = window.prompt('Tên phòng', item.name)
  if (!name) return
  const capacityRaw = window.prompt('Số ghế', String(item.total_seats))
  if (!capacityRaw) return
  await adminBackendService.updateAuditorium(item.id, {
    name,
    total_seats: Number(capacityRaw),
  })
  auditoriums.value = await adminBackendService.getAuditoriums()
}

async function deleteAuditorium(item: AdminAuditorium) {
  if (!window.confirm(`Xoá phòng ${item.name}?`)) return
  await adminBackendService.deleteAuditorium(item.id)
  auditoriums.value = await adminBackendService.getAuditoriums()
}

async function createSeat() {
  await adminBackendService.createSeat({
    auditorium_id: seatForm.value.auditoriumId,
    seat_row: seatForm.value.row,
    seat_number: seatForm.value.number,
    seat_type_id: seatForm.value.seatTypeId,
    is_active: true,
  })
  seats.value = await adminBackendService.getSeats(seatForm.value.auditoriumId)
}

async function loadSeatsByAuditorium() {
  if (!seatForm.value.auditoriumId) return
  seats.value = await adminBackendService.getSeats(seatForm.value.auditoriumId)
}

async function editSeat(item: AdminSeat) {
  const row = window.prompt('Hàng ghế', item.seat_row)
  if (!row) return
  const numberRaw = window.prompt('Số ghế', String(item.seat_number))
  if (!numberRaw) return
  await adminBackendService.updateSeat(item.id, { seat_row: row, seat_number: Number(numberRaw) })
  await loadSeatsByAuditorium()
}

async function deleteSeat(item: AdminSeat) {
  if (!window.confirm(`Xoá ghế ${item.seat_row}${item.seat_number}?`)) return
  await adminBackendService.deleteSeat(item.id)
  await loadSeatsByAuditorium()
}

async function createShowtime() {
  let movieId = showtimeForm.value.movieId

  if (movieId.startsWith('tmdb:')) {
    const tmdbId = Number(movieId.replace('tmdb:', ''))
    const tmdbMovie = tmdbMovies.value.find((item) => item.tmdb_id === tmdbId)
    if (!tmdbMovie) {
      throw new Error('Không tìm thấy phim TMDB để import')
    }

    const imported = await adminBackendService.importTmdbMovie({
      tmdb_id: tmdbMovie.tmdb_id,
      title: tmdbMovie.title,
      overview: tmdbMovie.overview || null,
      poster_path: tmdbMovie.poster_path || null,
      release_date: tmdbMovie.release_date || null,
      original_title: tmdbMovie.original_title || null,
      language: 'vi-VN',
      duration_min: 120,
    })
    movieId = imported.id
  }

  await adminBackendService.createShowtime({
    movie_id: movieId,
    auditorium_id: showtimeForm.value.auditoriumId,
    starts_at: toIso(showtimeForm.value.startsAt),
    ends_at: toIso(showtimeForm.value.endsAt),
    base_price: showtimeForm.value.basePrice,
    status: showtimeForm.value.status,
  })
  movies.value = await movieService.getAll()
  showtimes.value = await adminBackendService.getShowtimes()
}

async function editShowtime(item: AdminShowtime) {
  const priceRaw = window.prompt('Giá vé', String(item.base_price))
  if (!priceRaw) return
  const statusRaw = window.prompt('Trạng thái OPEN | CLOSED | CANCELLED', item.status)
  if (!statusRaw) return
  await adminBackendService.updateShowtime(item.id, {
    base_price: Number(priceRaw),
    status: statusRaw as 'OPEN' | 'CLOSED' | 'CANCELLED',
  })
  showtimes.value = await adminBackendService.getShowtimes()
}

async function deleteShowtime(item: AdminShowtime) {
  if (!window.confirm(`Xoá suất chiếu ${item.id}?`)) return
  await adminBackendService.deleteShowtime(item.id)
  showtimes.value = await adminBackendService.getShowtimes()
}

function fmtDateTime(value: string) {
  return new Date(value).toLocaleString('vi-VN')
}

function fmtCurrency(value: number) {
  return Number(value).toLocaleString('vi-VN') + 'đ'
}

function resolveUserBranchName(branchId: string | null | undefined) {
  if (!branchId) return '-'
  return branchNameMap.value.get(branchId) || branchId
}

function roleBadgeClass(role: UserProfile['role']) {
  if (role === 'admin') return 'badge role-admin'
  if (role === 'branch-admin') return 'badge role-branch-admin'
  if (role === 'staff') return 'badge role-staff'
  return 'badge role-customer'
}

function showtimeStatusClass(status: AdminShowtime['status']) {
  if (status === 'OPEN') return 'badge status-open'
  if (status === 'CLOSED') return 'badge status-closed'
  return 'badge status-cancelled'
}
</script>

<template>
  <div class="admin-page space-y-5">
    <section class="hero-panel">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p class="hero-kicker">CineAI Admin</p>
          <h1 class="hero-title">Trang chủ quản trị vận hành</h1>
          <p class="hero-subtitle">
            Tổng quan hiệu suất hệ thống rạp, phân quyền người dùng và điều phối lịch chiếu theo thời gian thực.
          </p>
        </div>
        <button
          @click="loadAll"
          class="action-ghost"
        >
          <span class="material-symbols-outlined text-base">refresh</span>
          Làm mới dữ liệu
        </button>
      </div>
    </section>

    <section class="grid grid-cols-2 gap-3 lg:grid-cols-5">
      <div class="metric-card">
        <div class="metric-icon metric-green">
          <span class="material-symbols-outlined">group</span>
        </div>
        <div>
          <p class="metric-label">Tổng người dùng</p>
          <p class="metric-value">{{ stats.users }}</p>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon metric-blue">
          <span class="material-symbols-outlined">storefront</span>
        </div>
        <div>
          <p class="metric-label">Chi nhánh</p>
          <p class="metric-value">{{ stats.branches }}</p>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon metric-violet">
          <span class="material-symbols-outlined">theaters</span>
        </div>
        <div>
          <p class="metric-label">Phòng chiếu</p>
          <p class="metric-value">{{ stats.auditoriums }}</p>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon metric-amber">
          <span class="material-symbols-outlined">event_seat</span>
        </div>
        <div>
          <p class="metric-label">Ghế</p>
          <p class="metric-value">{{ stats.seats }}</p>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon metric-pink">
          <span class="material-symbols-outlined">schedule</span>
        </div>
        <div>
          <p class="metric-label">Suất chiếu</p>
          <p class="metric-value">{{ stats.showtimes }}</p>
        </div>
      </div>
    </section>

    <section class="panel p-3 md:p-4">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="tab in tabItems"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="tab-btn"
          :class="activeTab === tab.key
            ? 'tab-btn-active'
            : 'tab-btn-idle'"
        >
          <span class="material-symbols-outlined text-base">{{ tab.icon }}</span>
          {{ tab.label }}
        </button>
      </div>

      <div class="tab-desc">
        <p class="text-sm font-semibold text-on-surface">{{ activeTabMeta.label }}</p>
        <p class="text-xs text-on-surface-variant mt-0.5">{{ activeTabMeta.description }}</p>
      </div>
    </section>

    <p v-if="error" class="panel border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</p>
    <p v-if="loading" class="panel border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">Đang tải dữ liệu mới nhất...</p>

    <section v-if="activeTab === 'users'" class="space-y-4">
      <div class="panel p-5 space-y-4">
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-lg font-bold text-on-surface">Tạo người dùng mới</h3>
          <span class="pill-muted">Users: {{ users.length }}</span>
        </div>
        <form class="grid md:grid-cols-3 gap-3" @submit.prevent="createUser">
          <input v-model="userForm.fullName" placeholder="Họ tên" class="field-input" required />
          <input v-model="userForm.email" type="email" placeholder="Email" class="field-input" required />
          <input v-model="userForm.password" type="password" placeholder="Mật khẩu" class="field-input" required />
          <input v-model="userForm.phone" placeholder="SĐT" class="field-input" />
          <select v-model="userForm.roleCode" class="field-input">
            <option value="CUSTOMER">CUSTOMER</option>
            <option value="BRANCH_ADMIN">BRANCH_ADMIN</option>
            <option value="STAFF">STAFF</option>
            <option value="SUPER_ADMIN">SUPER_ADMIN</option>
          </select>
          <select v-model="userForm.branchId" class="field-input">
            <option value="">Không gán chi nhánh</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
          <button class="md:col-span-3 action-primary">Tạo user</button>
        </form>
      </div>

      <div class="panel overflow-hidden">
        <div class="overflow-auto">
          <table class="w-full text-sm min-w-[860px]">
            <thead class="table-head">
              <tr class="text-left text-on-surface-variant">
                <th class="px-4 py-3">Tên</th>
                <th class="px-4 py-3">Email</th>
                <th class="px-4 py-3">Role</th>
                <th class="px-4 py-3">Trạng thái</th>
                <th class="px-4 py-3">Chi nhánh</th>
                <th class="px-4 py-3">Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id" class="table-row">
                <td class="px-4 py-3 font-semibold text-on-surface">{{ u.name }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ u.email }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold" :class="roleBadgeClass(u.role)">{{ u.role }}</span>
                </td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                    :class="u.isActive ? 'badge status-open' : 'badge status-cancelled'"
                  >
                    {{ u.isActive ? 'Đang hoạt động' : 'Đã khoá' }}
                  </span>
                </td>
                <td class="px-4 py-3 text-on-surface-variant">{{ resolveUserBranchName(u.branchId) }}</td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button @click="updateUserRole(u)" class="action-link action-link-blue">Đổi role</button>
                    <button @click="updateUserActive(u)" class="action-link action-link-amber">Khoá/Mở</button>
                    <button @click="softDeleteUser(u)" class="action-link action-link-rose">Xoá mềm</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'branches'" class="space-y-4">
      <div class="panel p-5 space-y-4">
        <h3 class="text-lg font-bold text-on-surface">Tạo chi nhánh / khu vực</h3>
        <form class="grid md:grid-cols-3 gap-3" @submit.prevent="createBranch">
          <input v-model="branchForm.code" placeholder="Mã" class="field-input" required />
          <input v-model="branchForm.name" placeholder="Tên chi nhánh" class="field-input" required />
          <input v-model="branchForm.city" placeholder="Thành phố" class="field-input" required />
          <input v-model="branchForm.addressLine" placeholder="Địa chỉ" class="field-input md:col-span-2" required />
          <input v-model="branchForm.district" placeholder="Quận/Huyện" class="field-input" />
          <input v-model="branchForm.phone" placeholder="SĐT" class="field-input" />
          <button class="md:col-span-3 action-primary">Tạo chi nhánh</button>
        </form>
      </div>

      <div class="panel overflow-hidden">
        <div class="overflow-auto">
          <table class="w-full text-sm min-w-[760px]">
            <thead class="table-head">
              <tr class="text-left text-on-surface-variant">
                <th class="px-4 py-3">Code</th>
                <th class="px-4 py-3">Tên</th>
                <th class="px-4 py-3">City</th>
                <th class="px-4 py-3">Số phòng</th>
                <th class="px-4 py-3">Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in branches" :key="b.id" class="table-row">
                <td class="px-4 py-3 font-semibold text-on-surface">{{ b.code }}</td>
                <td class="px-4 py-3 text-on-surface">{{ b.name }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ b.city }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ b.auditoriums_count }}</td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button @click="editBranch(b)" class="action-link action-link-blue">Sửa</button>
                    <button @click="deleteBranch(b)" class="action-link action-link-rose">Xoá</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'auditoriums'" class="space-y-4">
      <div class="panel p-5 space-y-4">
        <h3 class="text-lg font-bold text-on-surface">Tạo phòng chiếu</h3>
        <form class="grid md:grid-cols-3 gap-3" @submit.prevent="createAuditorium">
          <select v-model="auditoriumForm.branchId" class="field-input" required>
            <option value="" disabled>Chọn chi nhánh</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
          <input v-model="auditoriumForm.code" placeholder="Mã phòng" class="field-input" required />
          <input v-model="auditoriumForm.name" placeholder="Tên phòng" class="field-input" required />
          <input v-model.number="auditoriumForm.totalSeats" type="number" placeholder="Số ghế" class="field-input" required />
          <input v-model="auditoriumForm.screenType" placeholder="Loại màn hình" class="field-input" />
          <button class="md:col-span-3 action-primary">Tạo phòng</button>
        </form>
      </div>

      <div class="panel overflow-hidden">
        <div class="overflow-auto">
          <table class="w-full text-sm min-w-[760px]">
            <thead class="table-head">
              <tr class="text-left text-on-surface-variant">
                <th class="px-4 py-3">Phòng</th>
                <th class="px-4 py-3">Chi nhánh</th>
                <th class="px-4 py-3">Số ghế</th>
                <th class="px-4 py-3">Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in auditoriums" :key="a.id" class="table-row">
                <td class="px-4 py-3 text-on-surface">{{ a.name }} ({{ a.code }})</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ a.branch_name }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ a.total_seats }}</td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button @click="editAuditorium(a)" class="action-link action-link-blue">Sửa</button>
                    <button @click="deleteAuditorium(a)" class="action-link action-link-rose">Xoá</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'seats'" class="space-y-4">
      <div class="panel p-5 space-y-4">
        <h3 class="text-lg font-bold text-on-surface">Tạo ghế trong phòng</h3>
        <div class="grid md:grid-cols-5 gap-3">
          <select v-model="seatForm.auditoriumId" @change="loadSeatsByAuditorium" class="field-input">
            <option value="" disabled>Chọn phòng</option>
            <option v-for="a in auditoriums" :key="a.id" :value="a.id">{{ a.branch_name }} - {{ a.name }}</option>
          </select>
          <input v-model="seatForm.row" placeholder="Hàng" class="field-input" />
          <input v-model.number="seatForm.number" type="number" placeholder="Số" class="field-input" />
          <select v-model.number="seatForm.seatTypeId" class="field-input">
            <option v-for="st in seatTypes" :key="st.id" :value="st.id">{{ st.code }}</option>
          </select>
          <button @click="createSeat" class="action-primary">Tạo ghế</button>
        </div>
      </div>

      <div class="panel overflow-hidden">
        <div class="overflow-auto">
          <table class="w-full text-sm min-w-[760px]">
            <thead class="table-head">
              <tr class="text-left text-on-surface-variant">
                <th class="px-4 py-3">Ghế</th>
                <th class="px-4 py-3">Loại</th>
                <th class="px-4 py-3">Phòng</th>
                <th class="px-4 py-3">Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in seats" :key="s.id" class="table-row">
                <td class="px-4 py-3 font-semibold text-on-surface">{{ s.seat_row }}{{ s.seat_number }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ s.seat_type_code }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ s.branch_name }} - {{ s.auditorium_name }}</td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button @click="editSeat(s)" class="action-link action-link-blue">Sửa</button>
                    <button @click="deleteSeat(s)" class="action-link action-link-rose">Xoá</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'showtimes'" class="space-y-4">
      <div class="panel p-5 space-y-4">
        <h3 class="text-lg font-bold text-on-surface">Tạo suất chiếu</h3>
        <p class="text-xs text-on-surface-variant">Phim chọn từ TMDB sẽ được import tự động vào catalog nội bộ trước khi tạo suất.</p>
        <form class="grid md:grid-cols-3 gap-3" @submit.prevent="createShowtime">
          <select v-model="showtimeForm.movieId" class="field-input" required>
            <option value="" disabled>Chọn phim</option>
            <option v-for="m in showtimeMovieOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
          <select v-model="showtimeForm.auditoriumId" class="field-input" required>
            <option value="" disabled>Chọn phòng</option>
            <option v-for="a in auditoriums" :key="a.id" :value="a.id">{{ a.branch_name }} - {{ a.name }}</option>
          </select>
          <input v-model.number="showtimeForm.basePrice" type="number" placeholder="Giá vé" class="field-input" required />
          <input v-model="showtimeForm.startsAt" type="datetime-local" class="field-input" required />
          <input v-model="showtimeForm.endsAt" type="datetime-local" class="field-input" required />
          <select v-model="showtimeForm.status" class="field-input">
            <option value="OPEN">OPEN</option>
            <option value="CLOSED">CLOSED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
          <button class="md:col-span-3 action-primary">Tạo suất chiếu</button>
        </form>
      </div>

      <div class="panel overflow-hidden">
        <div class="overflow-auto">
          <table class="w-full text-sm min-w-[960px]">
            <thead class="table-head">
              <tr class="text-left text-on-surface-variant">
                <th class="px-4 py-3">Phim</th>
                <th class="px-4 py-3">Rạp/Phòng</th>
                <th class="px-4 py-3">Bắt đầu</th>
                <th class="px-4 py-3">Giá</th>
                <th class="px-4 py-3">Trạng thái</th>
                <th class="px-4 py-3">Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="st in showtimes" :key="st.id" class="table-row">
                <td class="px-4 py-3 font-semibold text-on-surface">{{ st.movie_title }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ st.branch_name }} - {{ st.auditorium_name }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ fmtDateTime(st.starts_at) }}</td>
                <td class="px-4 py-3 text-on-surface">{{ fmtCurrency(st.base_price) }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold" :class="showtimeStatusClass(st.status)">{{ st.status }}</span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button @click="editShowtime(st)" class="action-link action-link-blue">Sửa</button>
                    <button @click="deleteShowtime(st)" class="action-link action-link-rose">Xoá</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.admin-page {
  --surface: #121414;
  --card: #1a1c1c;
  --line: rgba(255, 255, 255, 0.08);
  --text-main: #e2e2e2;
  --text-soft: #b3b3b3;
  background:
    radial-gradient(90% 130% at 0% 0%, rgba(229, 9, 20, 0.08) 0%, #121414 45%, #121414 100%);
  color: var(--text-main);
  min-height: 100%;
}

.panel {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 1rem;
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.24);
}

.hero-panel {
  background: linear-gradient(120deg, rgba(26, 28, 28, 0.98) 0%, rgba(36, 18, 21, 0.95) 100%);
  border: 1px solid var(--line);
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.24);
}

.hero-kicker {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 800;
  color: #ffb4aa;
}

.hero-title {
  margin-top: 0.42rem;
  font-size: 1.7rem;
  font-weight: 900;
  color: #ffffff;
}

.hero-subtitle {
  margin-top: 0.42rem;
  max-width: 50rem;
  font-size: 0.9rem;
  color: var(--text-soft);
}

.metric-card {
  background: rgba(30, 32, 32, 0.92);
  border: 1px solid var(--line);
  border-radius: 1rem;
  padding: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
}

.metric-icon {
  width: 2.15rem;
  height: 2.15rem;
  border-radius: 0.7rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.metric-green { background: linear-gradient(135deg, #22c55e, #16a34a); }
.metric-blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.metric-violet { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.metric-amber { background: linear-gradient(135deg, #f59e0b, #d97706); }
.metric-pink { background: linear-gradient(135deg, #ec4899, #db2777); }

.metric-label {
  font-size: 0.73rem;
  color: var(--text-soft);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-value {
  margin-top: 0.2rem;
  font-size: 1.4rem;
  color: var(--text-main);
  font-weight: 900;
}

.action-ghost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  border-radius: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #e2e2e2;
  padding: 0.62rem 1rem;
  font-size: 0.82rem;
  font-weight: 700;
  transition: all 0.2s ease;
}

.action-ghost:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.18);
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 0.8rem;
  border: 1px solid;
  padding: 0.55rem 0.78rem;
  font-size: 0.82rem;
  font-weight: 700;
  transition: all 0.2s ease;
}

.tab-btn-active {
  border-color: transparent;
  color: #fff;
  background: linear-gradient(135deg, #e50914, #9f1239);
  box-shadow: 0 12px 24px -16px rgba(229, 9, 20, 0.9);
}

.tab-btn-idle {
  border-color: rgba(255, 255, 255, 0.12);
  color: #b3b3b3;
  background: rgba(255, 255, 255, 0.03);
}

.tab-btn-idle:hover {
  border-color: rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.08);
}

.tab-desc {
  margin-top: 0.72rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.8rem;
  background: rgba(255, 255, 255, 0.03);
  padding: 0.7rem 0.9rem;
}

.pill-muted {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748b;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  padding: 0.24rem 0.6rem;
}

.field-input {
  background: rgba(30, 32, 32, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.75rem;
  padding: 0.6rem 0.75rem;
  font-size: 0.875rem;
  color: #f5f5f5;
  transition: all 0.2s ease;
}

.field-input:focus {
  outline: none;
  border-color: rgba(229, 9, 20, 0.65);
  box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.15);
}

.action-primary {
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #e50914 0%, #be0812 100%);
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: #fff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.action-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px -16px rgba(229, 9, 20, 0.95);
}

.action-link {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.6rem;
  padding: 0.32rem 0.5rem;
  font-size: 0.72rem;
  font-weight: 700;
  line-height: 1;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.2s ease;
}

.action-link:hover {
  border-color: rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.08);
}

.action-link-blue { color: #7dd3fc; }
.action-link-amber { color: #fcd34d; }
.action-link-rose { color: #fda4af; }

.table-head {
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.table-row {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.badge {
  border-radius: 9999px;
  border: 1px solid transparent;
}

.role-admin { background: rgba(229, 9, 20, 0.16); border-color: rgba(229, 9, 20, 0.28); color: #fecaca; }
.role-branch-admin { background: rgba(139, 92, 246, 0.18); border-color: rgba(139, 92, 246, 0.28); color: #ddd6fe; }
.role-staff { background: rgba(59, 130, 246, 0.18); border-color: rgba(59, 130, 246, 0.28); color: #bfdbfe; }
.role-customer { background: rgba(34, 197, 94, 0.16); border-color: rgba(34, 197, 94, 0.26); color: #bbf7d0; }

.status-open { background: rgba(34, 197, 94, 0.16); border-color: rgba(34, 197, 94, 0.26); color: #bbf7d0; }
.status-closed { background: rgba(245, 158, 11, 0.16); border-color: rgba(245, 158, 11, 0.28); color: #fde68a; }
.status-cancelled { background: rgba(148, 163, 184, 0.16); border-color: rgba(148, 163, 184, 0.26); color: #cbd5e1; }

@media (max-width: 768px) {
  .hero-title {
    font-size: 1.35rem;
  }
}
</style>
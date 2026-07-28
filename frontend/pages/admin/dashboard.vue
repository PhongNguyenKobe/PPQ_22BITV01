<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import {
  adminBackendService,
  adminService,
  movieService,
  tmdbService,
  type AdminAuditorium,
  type AdminBranchManage,
  type AdminSeat,
  type AdminSeatType,
  type AdminShowtime,
  type Movie,
  type TmdbPopularMovie,
  type UserProfile,
  type SuperAdminStats,
  type Promotion,
} from '~/services/api'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

type AdminTab = 'overview' | 'users' | 'movies' | 'promotions' | 'branches' | 'auditoriums' | 'seats' | 'showtimes'
type AdminTabItem = {
  key: AdminTab
  label: string
  icon: string
  description: string
}

const allTabItems: AdminTabItem[] = [
  { key: 'overview', label: 'Tổng quan', icon: 'dashboard', description: 'Doanh thu và hiệu suất toàn hệ thống' },
  { key: 'movies', label: 'Phim', icon: 'movie', description: 'Danh mục phim và nội dung hiển thị' },
  { key: 'users', label: 'Người dùng', icon: 'group', description: 'Tài khoản và phân quyền' },
  { key: 'branches', label: 'Chi nhánh', icon: 'location_city', description: 'Khu vực và cụm rạp' },
  { key: 'promotions', label: 'Khuyến mãi', icon: 'sell', description: 'Mã giảm giá và giới hạn sử dụng' },
  { key: 'auditoriums', label: 'Phòng chiếu', icon: 'theaters', description: 'Màn hình và sức chứa' },
  { key: 'seats', label: 'Ghế ngồi', icon: 'event_seat', description: 'Sơ đồ ghế theo phòng' },
  { key: 'showtimes', label: 'Suất chiếu', icon: 'schedule', description: 'Lịch chiếu đang mở bán' },
]

const userStore = useUserStore()
const route = useRoute()
const { currentUser } = storeToRefs(userStore)
const isBranchAdmin = computed(() => currentUser.value?.role === 'branch-admin')
const tabItems = computed(() =>
  allTabItems.filter((tab) =>
    isBranchAdmin.value
      ? ['auditoriums', 'seats', 'showtimes'].includes(tab.key)
      : ['overview', 'movies', 'users', 'branches', 'promotions'].includes(tab.key),
  ),
)
const requestedTab = String(route.query.tab || '')
const activeTab = ref<AdminTab>(
  currentUser.value?.role === 'branch-admin'
    ? (['auditoriums', 'seats', 'showtimes'].includes(requestedTab) ? requestedTab as AdminTab : 'auditoriums')
    : (['overview', 'movies', 'users', 'branches', 'promotions'].includes(requestedTab) ? requestedTab as AdminTab : 'overview'),
)
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
const superStats = ref<SuperAdminStats | null>(null)
const promotions = ref<Promotion[]>([])
const promotionForm = ref({
  code: '',
  name: '',
  discount_type: 'PERCENT' as 'PERCENT' | 'FIXED',
  discount_value: 10,
  max_discount: null as number | null,
  min_order_amount: 0,
  starts_at: toDateTimeLocal(new Date()),
  ends_at: toDateTimeLocal(new Date(Date.now() + 30 * 86_400_000)),
  usage_limit: null as number | null,
  is_active: true,
})

watch(
  () => route.query.tab,
  (tab) => {
    const next = String(tab || '')
    if (tabItems.value.some((item) => item.key === next)) activeTab.value = next as AdminTab
  },
)

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
  rows: 8,
  seatsPerRow: 12,
  screenType: '2D',
})

const seatForm = ref({
  auditoriumId: '',
})
type SeatTool = 'INACTIVE' | 'STANDARD' | 'VIP' | 'COUPLE'
type SeatLayoutCell = {
  row: string
  number: number
  typeId: number
  typeCode: string
  active: boolean
}
const seatLayoutRows = ref(8)
const seatLayoutColumns = ref(12)
const seatTool = ref<SeatTool>('STANDARD')
const seatTools: { code: SeatTool; label: string; cls: string }[] = [
  { code: 'STANDARD', label: 'Ghế thường', cls: 'bg-slate-600' },
  { code: 'VIP', label: 'Ghế VIP', cls: 'bg-red-600' },
  { code: 'COUPLE', label: 'Ghế đôi', cls: 'bg-pink-600' },
  { code: 'INACTIVE', label: 'Lối đi / Ẩn', cls: 'bg-zinc-800' },
]
const seatLayout = ref<SeatLayoutCell[]>([])
const seatLayoutSaving = ref(false)

const showtimeForm = ref({
  movieId: '',
  auditoriumId: '',
  startsAt: '',
  endsAt: '',
  basePrice: 90000,
  status: 'DRAFT' as 'DRAFT' | 'OPEN' | 'CANCELLED',
})
const selectedMovieDuration = ref(120)
const selectedMovieReleaseDate = ref('')
type ShowtimeMode = 'single' | 'bulk'
type BulkShowtimeDraft = {
  movie_id: string
  movie_title: string
  auditorium_id: string
  auditorium_name: string
  starts_at: string
  ends_at: string
  base_price: number
  status: 'DRAFT'
}
const showtimeMode = ref<ShowtimeMode>('bulk')
const bulkPublishing = ref(false)
const bulkPreview = ref<BulkShowtimeDraft[]>([])
const bulkForm = ref({
  startDate: toDateTimeLocal(new Date()).slice(0, 10),
  endDate: toDateTimeLocal(new Date()).slice(0, 10),
  openingTime: '09:00',
  closingTime: '23:30',
  gapMinutes: 15,
  movieIds: [] as string[],
  auditoriumIds: [] as string[],
})
const scheduleDate = ref(toDateTimeLocal(new Date()).slice(0, 10))
const scheduleBranch = ref('')
const scheduleStatus = ref<'ALL' | 'ACTIVE' | 'OPEN' | 'DRAFT' | 'FINISHED' | 'CANCELLED'>('ALL')

const movieForm = ref({
  title: '',
  description: '',
  duration: 120,
  releaseDate: '',
  poster: '',
  trailer: '',
  status: 'UPCOMING' as 'UPCOMING' | 'NOW_SHOWING' | 'ENDED',
  genres: '',
})

const showtimeMovieOptions = computed(() => {
  const tmdbOptions = tmdbMovies.value.map((movie) => ({
    value: `tmdb:${movie.tmdb_id}`,
    label: `${movie.title} (TMDB)`,
    suggestedPrice: movie.suggested_ticket_price,
  }))
  const backendOptions = movies.value.map((movie) => ({
    value: movie.id,
    label: `${movie.title} (DB)`,
    suggestedPrice: showtimes.value.find((item) => item.movie_id === movie.id)?.base_price || 90000,
  }))
  return [...tmdbOptions, ...backendOptions]
})

const selectedShowtimeMovie = computed(() =>
  showtimeMovieOptions.value.find((movie) => movie.value === showtimeForm.value.movieId),
)

watch(
  () => showtimeForm.value.movieId,
  async (movieId) => {
    if (selectedShowtimeMovie.value) {
      showtimeForm.value.basePrice = Number(selectedShowtimeMovie.value.suggestedPrice)
    }

    const tmdbMovie = movieId.startsWith('tmdb:')
      ? tmdbMovies.value.find((movie) => `tmdb:${movie.tmdb_id}` === movieId)
      : undefined
    const backendMovie = tmdbMovie
      ? undefined
      : movies.value.find((movie) => movie.id === movieId)

    selectedMovieReleaseDate.value = tmdbMovie?.release_date || backendMovie?.releaseDate || ''
    selectedMovieDuration.value = backendMovie?.duration || 120

    if (tmdbMovie) {
      try {
        const detail = await tmdbService.getMovieDetail(tmdbMovie.tmdb_id)
        if (showtimeForm.value.movieId === movieId) {
          selectedMovieDuration.value = detail.duration || 120
        }
      } catch {
        // Keep the safe 120-minute fallback when TMDB detail is unavailable.
      }
    }

    if (showtimeForm.value.movieId === movieId) {
      applySuggestedShowtime()
    }
  },
)

watch(
  () => showtimeForm.value.startsAt,
  (startsAt) => {
    if (!startsAt) return
    const end = new Date(startsAt)
    end.setMinutes(end.getMinutes() + selectedMovieDuration.value)
    showtimeForm.value.endsAt = toDateTimeLocal(end)
  },
)

const stats = computed(() => ({
  users: users.value.length,
  branches: branches.value.length,
  auditoriums: auditoriums.value.length,
  seats: seats.value.length,
  showtimes: showtimes.value.length,
}))

const filteredScheduleShowtimes = computed(() =>
  showtimes.value.filter((item) => {
    const sameDate = toDateTimeLocal(new Date(item.starts_at)).slice(0, 10) === scheduleDate.value
    const sameBranch = !scheduleBranch.value || item.branch_name === scheduleBranch.value
    const sameStatus =
      scheduleStatus.value === 'ALL'
      || (scheduleStatus.value === 'ACTIVE' && ['OPEN', 'DRAFT'].includes(item.status))
      || item.status === scheduleStatus.value
    return sameDate && sameBranch && sameStatus
  }),
)

const scheduleRooms = computed(() => {
  const items = filteredScheduleShowtimes.value
  const grouped = new Map<string, { name: string; branch: string; items: AdminShowtime[] }>()
  for (const item of items) {
    if (!grouped.has(item.auditorium_id)) {
      grouped.set(item.auditorium_id, {
        name: item.auditorium_name,
        branch: item.branch_name,
        items: [],
      })
    }
    grouped.get(item.auditorium_id)!.items.push(item)
  }
  return [...grouped.values()]
    .map((room) => ({
      ...room,
      items: room.items.sort((a, b) => a.starts_at.localeCompare(b.starts_at)),
    }))
    .sort((a, b) => `${a.branch}${a.name}`.localeCompare(`${b.branch}${b.name}`))
})

const availableScheduleDates = computed(() => {
  const counts = new Map<string, number>()
  for (const item of showtimes.value) {
    if (scheduleBranch.value && item.branch_name !== scheduleBranch.value) continue
    const date = toDateTimeLocal(new Date(item.starts_at)).slice(0, 10)
    counts.set(date, (counts.get(date) || 0) + 1)
  }
  return [...counts.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([date, count]) => ({ date, count }))
})

const scheduleSummary = computed(() => ({
  total: filteredScheduleShowtimes.value.length,
  open: filteredScheduleShowtimes.value.filter((item) => item.status === 'OPEN').length,
  draft: filteredScheduleShowtimes.value.filter((item) => item.status === 'DRAFT').length,
  sold: filteredScheduleShowtimes.value.reduce((sum, item) => sum + Number(item.sold_seats || 0), 0),
  revenue: filteredScheduleShowtimes.value.reduce((sum, item) => sum + Number(item.revenue || 0), 0),
}))

function moveScheduleDate(days: number) {
  const date = new Date(`${scheduleDate.value}T12:00:00`)
  date.setDate(date.getDate() + days)
  scheduleDate.value = toDateTimeLocal(date).slice(0, 10)
}

function selectToday() {
  scheduleDate.value = toDateTimeLocal(new Date()).slice(0, 10)
}

function selectNearestUsefulScheduleDate() {
  const today = toDateTimeLocal(new Date()).slice(0, 10)
  const useful = showtimes.value
    .filter((item) => ['OPEN', 'DRAFT'].includes(item.status))
    .map((item) => toDateTimeLocal(new Date(item.starts_at)).slice(0, 10))
    .filter((date) => date >= today)
    .sort()[0]
  if (useful) scheduleDate.value = useful
}

const scheduleBranchOptions = computed(() =>
  [...new Set(auditoriums.value.map((item) => item.branch_name))].sort(),
)
const draftShowtimes = computed(() => showtimes.value.filter((item) => item.stored_status === 'DRAFT'))
const bulkConflictIndexes = computed(() => {
  const conflicts = new Set<number>()
  bulkPreview.value.forEach((draft, index) => {
    if (showtimes.value.some((current) =>
      current.status !== 'CANCELLED'
      && current.auditorium_id === draft.auditorium_id
      && new Date(current.starts_at) < new Date(draft.ends_at)
      && new Date(current.ends_at) > new Date(draft.starts_at)
    )) {
      conflicts.add(index)
    }
    bulkPreview.value.forEach((other, otherIndex) => {
      if (
        index !== otherIndex
        && other.auditorium_id === draft.auditorium_id
        && new Date(other.starts_at) < new Date(draft.ends_at)
        && new Date(other.ends_at) > new Date(draft.starts_at)
      ) {
        conflicts.add(index)
      }
    })
  })
  return conflicts
})
const bulkConflictCount = computed(() => bulkConflictIndexes.value.size)

const activeTabMeta = computed(
  () => tabItems.value.find((tab) => tab.key === activeTab.value) || tabItems.value[0],
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
    if (isBranchAdmin.value) {
      const [statsData, auditoriumData, seatTypeData, showtimeData, movieData, tmdbMovieData] = await Promise.all([
        adminService.getBranchAdminStats(),
        adminBackendService.getAuditoriums(),
        adminBackendService.getSeatTypes(),
        adminBackendService.getShowtimes(),
        movieService.getAll(),
        movieService.getPopularFromTmdb(),
      ])
      branches.value = [{
        id: statsData.branchId,
        vendor_id: '',
        code: '',
        name: statsData.branchName,
        address_line: '',
        city: '',
        district: null,
        phone: null,
        is_active: true,
        auditoriums_count: auditoriumData.length,
      }]
      auditoriums.value = auditoriumData
      seatTypes.value = seatTypeData
      showtimes.value = showtimeData
      selectNearestUsefulScheduleDate()
      movies.value = movieData
      users.value = []
      tmdbMovies.value = tmdbMovieData
    } else {
      const [statsData, usersData, branchData, movieData, tmdbMovieData, promotionData] = await Promise.all([
        adminService.getSuperAdminStats(),
        adminBackendService.getUsers(),
        adminBackendService.getBranchesManage(),
        movieService.getAll(),
        movieService.getPopularFromTmdb(),
        adminBackendService.getPromotions(),
      ])
      superStats.value = statsData
      users.value = usersData
      branches.value = branchData
      movies.value = movieData
      tmdbMovies.value = tmdbMovieData
      promotions.value = promotionData
      auditoriums.value = []
      seatTypes.value = []
      showtimes.value = []
    }

    if (!showtimeForm.value.movieId && showtimeMovieOptions.value.length > 0) {
      showtimeForm.value.movieId = showtimeMovieOptions.value[0].value
    }
    if (!auditoriumForm.value.branchId && branches.value.length > 0) {
      auditoriumForm.value.branchId = branches.value[0].id
    }
    if (!seatForm.value.auditoriumId && auditoriums.value.length > 0) {
      seatForm.value.auditoriumId = auditoriums.value[0].id
      await loadSeatsByAuditorium()
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

function toDateTimeLocal(value: Date) {
  const offset = value.getTimezoneOffset()
  return new Date(value.getTime() - offset * 60_000).toISOString().slice(0, 16)
}

function suggestedStartDate() {
  const now = new Date()
  const release = selectedMovieReleaseDate.value
    ? new Date(`${selectedMovieReleaseDate.value}T18:00:00`)
    : now
  const start = release > now ? release : now
  start.setSeconds(0, 0)
  if (start <= now) {
    start.setMinutes(Math.ceil(start.getMinutes() / 15) * 15)
  }
  return start
}

function applySuggestedShowtime() {
  showtimeForm.value.startsAt = toDateTimeLocal(suggestedStartDate())
}

const minimumShowtimeDate = computed(() => {
  const today = toDateTimeLocal(new Date())
  if (!selectedMovieReleaseDate.value) return today
  const release = `${selectedMovieReleaseDate.value}T00:00`
  return release > today ? release : today
})

async function createPromotion() {
  error.value = ''
  try {
    const created = await adminBackendService.createPromotion({
      ...promotionForm.value,
      code: promotionForm.value.code.trim().toUpperCase(),
      starts_at: toIso(promotionForm.value.starts_at),
      ends_at: toIso(promotionForm.value.ends_at),
    })
    promotions.value.unshift(created)
    promotionForm.value.code = ''
    promotionForm.value.name = ''
  } catch (e: any) {
    error.value = e?.message || 'Không thể tạo khuyến mãi.'
  }
}

async function togglePromotion(item: Promotion) {
  try {
    const updated = await adminBackendService.updatePromotion(item.id, { is_active: !item.is_active })
    promotions.value = promotions.value.map((current) => current.id === updated.id ? updated : current)
  } catch (e: any) {
    error.value = e?.message || 'Không thể cập nhật khuyến mãi.'
  }
}

async function createMovie() {
  await adminBackendService.createMovie({
    title: movieForm.value.title,
    description: movieForm.value.description || undefined,
    duration_min: Number(movieForm.value.duration),
    release_date: movieForm.value.releaseDate || null,
    poster_url: movieForm.value.poster || undefined,
    trailer_url: movieForm.value.trailer || undefined,
    status: movieForm.value.status,
    genres: movieForm.value.genres.split(',').map((item) => item.trim()).filter(Boolean),
  })
  movies.value = await movieService.getAll()
  movieForm.value = { title: '', description: '', duration: 120, releaseDate: '', poster: '', trailer: '', status: 'UPCOMING', genres: '' }
}

async function editMovie(movie: Movie) {
  const title = window.prompt('Tên phim', movie.title)
  if (!title) return
  const description = window.prompt('Mô tả', movie.description) ?? movie.description
  const updated = await adminBackendService.updateMovie(movie.id, {
    title,
    description,
    duration_min: movie.duration,
    release_date: movie.releaseDate || null,
    poster_url: movie.poster || null,
    trailer_url: movie.trailer || null,
    status: 'NOW_SHOWING',
    genres: movie.genre,
  })
  movies.value = movies.value.map((item) => item.id === updated.id ? updated : item)
}

async function deleteMovie(movie: Movie) {
  if (!window.confirm(`Xoá phim "${movie.title}"?`)) return
  await adminBackendService.deleteMovie(movie.id)
  movies.value = movies.value.filter((item) => item.id !== movie.id)
}

async function createUser() {
  error.value = ''
  try {
    await adminBackendService.createUser({
      full_name: userForm.value.fullName.trim(),
      email: userForm.value.email.trim(),
      password: userForm.value.password,
      phone: userForm.value.phone.trim() || null,
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
  } catch (e: any) {
    const message = e?.response?.data?.detail || e?.message || ''
    error.value = message === 'EMAIL_EXISTS'
      ? 'Email này đã được sử dụng.'
      : message === 'PHONE_EXISTS'
        ? 'Số điện thoại này đã được sử dụng.'
        : message || 'Không thể tạo tài khoản.'
  }
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

async function toggleBranchActive(branch: AdminBranchManage) {
  await adminBackendService.updateBranch(branch.id, { is_active: !branch.is_active })
  branches.value = await adminBackendService.getBranchesManage()
}

async function deleteBranch(branch: AdminBranchManage) {
  if (!window.confirm(`Xoá chi nhánh ${branch.name}?`)) return
  await adminBackendService.deleteBranch(branch.id)
  branches.value = await adminBackendService.getBranchesManage()
}

async function createAuditorium() {
  const created = await adminBackendService.createAuditorium({
    branch_id: auditoriumForm.value.branchId,
    code: auditoriumForm.value.code,
    name: auditoriumForm.value.name,
    total_seats: auditoriumForm.value.rows * auditoriumForm.value.seatsPerRow,
    screen_type: auditoriumForm.value.screenType,
    is_active: true,
  })
  const standard = seatTypeByCode('STANDARD')
  if (standard) {
    const initialSeats = []
    for (let rowIndex = 0; rowIndex < auditoriumForm.value.rows; rowIndex += 1) {
      for (let number = 1; number <= auditoriumForm.value.seatsPerRow; number += 1) {
        initialSeats.push({
          seat_row: String.fromCharCode(65 + rowIndex),
          seat_number: number,
          seat_type_id: standard.id,
          is_active: true,
        })
      }
    }
    await adminBackendService.saveSeatLayout(created.id, initialSeats)
  }
  auditoriumForm.value.code = ''
  auditoriumForm.value.name = ''
  auditoriumForm.value.rows = 8
  auditoriumForm.value.seatsPerRow = 12
  auditoriums.value = await adminBackendService.getAuditoriums()
}

async function editAuditorium(item: AdminAuditorium) {
  const name = window.prompt('Tên phòng', item.name)
  if (!name) return
  const screenType = window.prompt('Loại màn hình: 2D | 3D | IMAX | 4DX', item.screen_type || '2D')
  if (!screenType) return
  await adminBackendService.updateAuditorium(item.id, {
    name,
    screen_type: screenType.toUpperCase(),
  })
  auditoriums.value = await adminBackendService.getAuditoriums()
}

async function deleteAuditorium(item: AdminAuditorium) {
  if (!window.confirm(`Xoá phòng ${item.name}?`)) return
  await adminBackendService.deleteAuditorium(item.id)
  auditoriums.value = await adminBackendService.getAuditoriums()
}

function seatTypeByCode(code: string) {
  return seatTypes.value.find((item) => item.code === code) || seatTypes.value[0]
}

function rebuildSeatLayout(existing: AdminSeat[] = []) {
  const existingMap = new Map(existing.map((seat) => [`${seat.seat_row}-${seat.seat_number}`, seat]))
  const fallback = seatTypeByCode('STANDARD')
  seatLayout.value = []
  for (let rowIndex = 0; rowIndex < seatLayoutRows.value; rowIndex += 1) {
    const row = String.fromCharCode(65 + rowIndex)
    for (let number = 1; number <= seatLayoutColumns.value; number += 1) {
      const saved = existingMap.get(`${row}-${number}`)
      seatLayout.value.push({
        row,
        number,
        typeId: saved?.seat_type_id || fallback?.id || 1,
        typeCode: saved?.seat_type_code || fallback?.code || 'STANDARD',
        active: saved?.is_active ?? true,
      })
    }
  }
}

async function loadSeatsByAuditorium() {
  if (!seatForm.value.auditoriumId) return
  seats.value = await adminBackendService.getSeats(seatForm.value.auditoriumId)
  if (seats.value.length) {
    const rows = [...new Set(seats.value.map((seat) => seat.seat_row))]
    seatLayoutRows.value = Math.max(1, rows.length)
    seatLayoutColumns.value = Math.max(...seats.value.map((seat) => seat.seat_number), 1)
  } else {
    seatLayoutRows.value = 8
    seatLayoutColumns.value = 12
  }
  rebuildSeatLayout(seats.value)
}

function resizeSeatLayout() {
  const current = seatLayout.value.map((cell) => ({
    id: '',
    auditorium_id: seatForm.value.auditoriumId,
    auditorium_name: '',
    branch_name: '',
    seat_row: cell.row,
    seat_number: cell.number,
    seat_type_id: cell.typeId,
    seat_type_code: cell.typeCode,
    is_active: cell.active,
  }))
  rebuildSeatLayout(current)
}

function applySeatTool(cell: SeatLayoutCell) {
  if (seatTool.value === 'INACTIVE') {
    cell.active = false
    return
  }
  const type = seatTypeByCode(seatTool.value)
  if (!type) return
  cell.active = true
  cell.typeId = type.id
  cell.typeCode = type.code
}

function selectSeatTool(tool: SeatTool) {
  seatTool.value = tool
}

function applyToolToRow(row: string) {
  seatLayout.value.filter((cell) => cell.row === row).forEach(applySeatTool)
}

async function saveSeatLayout() {
  if (!seatForm.value.auditoriumId || !seatLayout.value.length) return
  seatLayoutSaving.value = true
  error.value = ''
  try {
    const result = await adminBackendService.saveSeatLayout(
      seatForm.value.auditoriumId,
      seatLayout.value.map((cell) => ({
        seat_row: cell.row,
        seat_number: cell.number,
        seat_type_id: cell.typeId,
        is_active: cell.active,
      })),
    )
    seats.value = result.seats
    auditoriums.value = await adminBackendService.getAuditoriums()
  } catch (e: any) {
    const message = e?.message || ''
    const seatMatch = message.match(/Seat ([A-Z0-9]+) has a ticket for an upcoming showtime/)
    error.value = seatMatch
      ? `Ghế ${seatMatch[1]} đã có người mua vé cho một suất sắp chiếu nên chưa thể thay đổi.`
      : message || 'Không thể lưu sơ đồ ghế.'
  } finally {
    seatLayoutSaving.value = false
  }
}

const activeSeatCount = computed(() => seatLayout.value.filter((cell) => cell.active).length)
const seatLayoutRowNames = computed(() => [...new Set(seatLayout.value.map((cell) => cell.row))])

async function createShowtime() {
  error.value = ''
  try {
    let movieId = showtimeForm.value.movieId

    if (new Date(showtimeForm.value.startsAt) < new Date(minimumShowtimeDate.value)) {
      throw new Error('Suất chiếu không thể bắt đầu trước ngày khởi chiếu của phim.')
    }
    if (
      showtimeForm.value.status === 'OPEN'
      && new Date(showtimeForm.value.startsAt).getTime() <= Date.now() + 15 * 60 * 1000
    ) {
      throw new Error('Suất chiếu OPEN phải bắt đầu sau hiện tại ít nhất 15 phút để còn thời gian bán vé.')
    }

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
        duration_min: selectedMovieDuration.value || 120,
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
  } catch (e: any) {
    error.value = e?.message === 'The auditorium already has a showtime in this time range'
      ? 'Phòng đã có phim trong khung giờ này. Hãy chọn giờ hoặc phòng khác.'
      : e?.message || 'Không thể tạo suất chiếu.'
  }
}

function eachDate(start: string, end: string) {
  const dates: string[] = []
  const cursor = new Date(`${start}T00:00:00`)
  const last = new Date(`${end}T00:00:00`)
  while (cursor <= last && dates.length < 31) {
    dates.push(toDateTimeLocal(cursor).slice(0, 10))
    cursor.setDate(cursor.getDate() + 1)
  }
  return dates
}

function generateBulkPreview() {
  error.value = ''
  bulkPreview.value = []
  if (!bulkForm.value.movieIds.length || !bulkForm.value.auditoriumIds.length) {
    error.value = 'Hãy chọn ít nhất một phim và một phòng chiếu.'
    return
  }
  if (bulkForm.value.endDate < bulkForm.value.startDate) {
    error.value = 'Ngày kết thúc phải từ ngày bắt đầu trở đi.'
    return
  }
  if (bulkForm.value.closingTime <= bulkForm.value.openingTime) {
    error.value = 'Giờ đóng cửa phải sau giờ mở cửa.'
    return
  }

  const selectedMovies = bulkForm.value.movieIds
    .map((id) => movies.value.find((movie) => movie.id === id))
    .filter((movie): movie is Movie => Boolean(movie))
  const selectedRooms = bulkForm.value.auditoriumIds
    .map((id) => auditoriums.value.find((room) => room.id === id))
    .filter((room): room is AdminAuditorium => Boolean(room))
  const drafts: BulkShowtimeDraft[] = []

  eachDate(bulkForm.value.startDate, bulkForm.value.endDate).forEach((date, dayIndex) => {
    const dayMovies = selectedMovies.filter((movie) => !movie.releaseDate || date >= movie.releaseDate)
    if (!dayMovies.length) return
    selectedRooms.forEach((room, roomIndex) => {
      let cursor = new Date(`${date}T${bulkForm.value.openingTime}:00`)
      const closing = new Date(`${date}T${bulkForm.value.closingTime}:00`)
      let movieIndex = (dayIndex + roomIndex) % dayMovies.length
      while (cursor < closing && drafts.length < 500) {
        const movie = dayMovies[movieIndex % dayMovies.length]
        const end = new Date(cursor)
        end.setMinutes(end.getMinutes() + (movie.duration || 120))
        if (end > closing) break
        const previousPrice = showtimes.value.find((item) => item.movie_id === movie.id)?.base_price
        drafts.push({
          movie_id: movie.id,
          movie_title: movie.title,
          auditorium_id: room.id,
          auditorium_name: `${room.branch_name} · ${room.name}`,
          starts_at: toDateTimeLocal(cursor),
          ends_at: toDateTimeLocal(end),
          base_price: Number(previousPrice || 90000),
          status: 'DRAFT',
        })
        cursor = new Date(end)
        cursor.setMinutes(cursor.getMinutes() + Number(bulkForm.value.gapMinutes))
        movieIndex += 1
      }
    })
  })
  bulkPreview.value = drafts
}

function updateBulkDraftMovie(index: number) {
  const draft = bulkPreview.value[index]
  const movie = movies.value.find((item) => item.id === draft.movie_id)
  if (!movie) return
  draft.movie_title = movie.title
  const end = new Date(draft.starts_at)
  end.setMinutes(end.getMinutes() + (movie.duration || 120))
  draft.ends_at = toDateTimeLocal(end)
  draft.base_price = Number(
    showtimes.value.find((item) => item.movie_id === movie.id)?.base_price || 90000,
  )
}

function updateBulkDraftRoom(index: number) {
  const draft = bulkPreview.value[index]
  const room = auditoriums.value.find((item) => item.id === draft.auditorium_id)
  if (room) draft.auditorium_name = `${room.branch_name} · ${room.name}`
}

function updateBulkDraftStart(index: number) {
  const draft = bulkPreview.value[index]
  const movie = movies.value.find((item) => item.id === draft.movie_id)
  if (!movie || !draft.starts_at) return
  const end = new Date(draft.starts_at)
  end.setMinutes(end.getMinutes() + (movie.duration || 120))
  draft.ends_at = toDateTimeLocal(end)
}

function removeBulkDraft(index: number) {
  bulkPreview.value.splice(index, 1)
}

async function saveBulkDraftSchedule() {
  if (!bulkPreview.value.length) return
  bulkPublishing.value = true
  error.value = ''
  try {
    await adminBackendService.createShowtimesBulk(
      bulkPreview.value.map(({ movie_title, auditorium_name, ...item }) => ({
        ...item,
        starts_at: toIso(item.starts_at),
        ends_at: toIso(item.ends_at),
      })),
    )
    showtimes.value = await adminBackendService.getShowtimes()
    scheduleDate.value = bulkForm.value.startDate
    bulkPreview.value = []
    showtimeMode.value = 'bulk'
  } catch (e: any) {
    error.value = e?.message || 'Không thể xuất bản lịch chiếu.'
  } finally {
    bulkPublishing.value = false
  }
}

async function publishDraftShowtimes() {
  if (!draftShowtimes.value.length) return
  bulkPublishing.value = true
  error.value = ''
  try {
    await adminBackendService.publishShowtimes(draftShowtimes.value.map((item) => item.id))
    showtimes.value = await adminBackendService.getShowtimes()
  } catch (e: any) {
    error.value = e?.message || 'Không thể xuất bản lịch nháp.'
  } finally {
    bulkPublishing.value = false
  }
}

async function editShowtime(item: AdminShowtime) {
  const hasSales = item.booking_count > 0
  const priceRaw = window.prompt(
    hasSales
      ? `Suất đã có ${item.sold_seats} ghế bán. Chỉ nên đổi giá cho các giao dịch mới. Giá vé:`
      : 'Giá vé',
    String(item.base_price),
  )
  if (!priceRaw) return
  const statusRaw = window.prompt(
    'Trạng thái DRAFT | OPEN | CANCELLED\n(Các trạng thái hết hạn/đang chiếu/kết thúc do hệ thống tự tính)',
    item.stored_status,
  )?.trim().toUpperCase()
  if (!statusRaw) return
  if (!['DRAFT', 'OPEN', 'CANCELLED'].includes(statusRaw)) {
    error.value = 'Trạng thái không hợp lệ.'
    return
  }
  let cancellationReason: string | undefined
  if (statusRaw === 'CANCELLED') {
    cancellationReason = window.prompt(
      hasSales
        ? 'Suất đã bán vé. Nhập lý do hủy để chuyển giao dịch sang chờ hoàn tiền:'
        : 'Nhập lý do hủy suất:',
      item.cancellation_reason || '',
    )?.trim()
    if (!cancellationReason) return
  }
  try {
    await adminBackendService.updateShowtime(item.id, {
      base_price: Number(priceRaw),
      status: statusRaw as 'DRAFT' | 'OPEN' | 'CANCELLED',
      cancellation_reason: cancellationReason,
    })
    showtimes.value = await adminBackendService.getShowtimes()
  } catch (e: any) {
    error.value = e?.message || 'Không thể cập nhật suất chiếu.'
  }
}

async function deleteShowtime(item: AdminShowtime) {
  if (item.booking_count > 0) {
    error.value = `Không thể xóa suất đã có ${item.booking_count} đơn. Hãy hủy suất và xử lý hoàn tiền.`
    return
  }
  if (!window.confirm(`Xoá suất chiếu ${item.id}?`)) return
  try {
    await adminBackendService.deleteShowtime(item.id)
    showtimes.value = await adminBackendService.getShowtimes()
  } catch (e: any) {
    error.value = e?.message || 'Không thể xóa suất chiếu.'
  }
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

function showtimeStatusClass(status: string) {
  if (status === 'OPEN') return 'badge status-open'
  if (status === 'DRAFT') return 'badge status-draft'
  if (status === 'CANCELLED') return 'badge status-cancelled'
  return 'badge status-closed'
}
</script>

<template>
  <div class="admin-page space-y-5">
    <section class="hero-panel">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p class="hero-kicker">{{ isBranchAdmin ? 'CineAI Branch Admin' : 'CineAI Super Admin' }}</p>
          <h1 class="hero-title">{{ isBranchAdmin ? 'Quản trị vận hành chi nhánh' : 'Quản trị hệ thống CineAI' }}</h1>
          <p class="hero-subtitle">
            {{ isBranchAdmin
              ? 'Quản lý phòng chiếu, sơ đồ ghế và lịch chiếu thuộc chi nhánh được phân công.'
              : 'Theo dõi tổng quan, quản lý phim, tài khoản người dùng và hệ thống chi nhánh.' }}
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

    <section v-if="false" class="grid grid-cols-1 gap-3 md:grid-cols-3">
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
          <span class="material-symbols-outlined">movie</span>
        </div>
        <div>
          <p class="metric-label">Phim trong catalog</p>
          <p class="metric-value">{{ movies.length }}</p>
        </div>
      </div>
    </section>

    <section v-if="isBranchAdmin" class="grid grid-cols-1 gap-3 md:grid-cols-3">
      <div class="metric-card">
        <div class="metric-icon metric-violet"><span class="material-symbols-outlined">theaters</span></div>
        <div><p class="metric-label">Phòng chiếu</p><p class="metric-value">{{ auditoriums.length }}</p></div>
      </div>
      <div class="metric-card">
        <div class="metric-icon metric-amber"><span class="material-symbols-outlined">event_seat</span></div>
        <div><p class="metric-label">Tổng sức chứa</p><p class="metric-value">{{ auditoriums.reduce((sum, room) => sum + room.total_seats, 0) }}</p></div>
      </div>
      <div class="metric-card">
        <div class="metric-icon metric-pink"><span class="material-symbols-outlined">schedule</span></div>
        <div><p class="metric-label">Suất chiếu</p><p class="metric-value">{{ showtimes.length }}</p></div>
      </div>
    </section>

    <section v-if="false" class="panel p-3 md:p-4">
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

    <section v-if="!isBranchAdmin && activeTab === 'overview' && superStats" class="space-y-4">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        <div class="metric-card"><div class="metric-icon metric-green"><span class="material-symbols-outlined">payments</span></div><div><p class="metric-label">Tổng doanh thu</p><p class="metric-value">{{ fmtCurrency(superStats.totalRevenue) }}</p></div></div>
        <div class="metric-card"><div class="metric-icon metric-blue"><span class="material-symbols-outlined">today</span></div><div><p class="metric-label">Doanh thu hôm nay</p><p class="metric-value">{{ fmtCurrency(superStats.todayRevenue) }}</p></div></div>
        <div class="metric-card"><div class="metric-icon metric-violet"><span class="material-symbols-outlined">calendar_month</span></div><div><p class="metric-label">Doanh thu tháng này</p><p class="metric-value">{{ fmtCurrency(superStats.monthRevenue) }}</p></div></div>
        <div class="metric-card"><div class="metric-icon metric-amber"><span class="material-symbols-outlined">confirmation_number</span></div><div><p class="metric-label">Ghế đã bán</p><p class="metric-value">{{ superStats.ticketsSold }}</p></div></div>
        <div class="metric-card"><div class="metric-icon metric-pink"><span class="material-symbols-outlined">receipt_long</span></div><div><p class="metric-label">Đơn thành công</p><p class="metric-value">{{ superStats.successfulBookings }}</p></div></div>
        <div class="metric-card"><div class="metric-icon metric-violet"><span class="material-symbols-outlined">storefront</span></div><div><p class="metric-label">Quy mô hệ thống</p><p class="metric-value">{{ superStats.totalBranches }} chi nhánh</p></div></div>
      </div>

      <div class="grid gap-4 xl:grid-cols-2">
        <div class="panel p-5">
          <h3 class="text-lg font-bold text-on-surface">Doanh thu 7 ngày gần nhất</h3>
          <div class="mt-5 flex h-52 items-end gap-3">
            <div v-for="point in superStats.revenueChartData" :key="point.label" class="flex min-w-0 flex-1 flex-col items-center gap-2">
              <span class="text-[10px] text-on-surface-variant">{{ fmtCurrency(point.value) }}</span>
              <div class="w-full rounded-t-lg bg-gradient-to-t from-red-600 to-fuchsia-500" :style="{ height: `${Math.max(6, (point.value / Math.max(...superStats.revenueChartData.map(item => item.value), 1)) * 150)}px` }"></div>
              <span class="text-xs text-on-surface-variant">{{ point.label }}</span>
            </div>
          </div>
        </div>
        <div class="panel overflow-hidden">
          <div class="border-b border-white/10 p-5"><h3 class="text-lg font-bold text-on-surface">Hiệu suất theo chi nhánh</h3></div>
          <table class="w-full text-sm">
            <thead><tr><th class="px-5 py-3 text-left">Chi nhánh</th><th class="px-5 py-3 text-right">Vé</th><th class="px-5 py-3 text-right">Doanh thu</th></tr></thead>
            <tbody><tr v-for="item in superStats.branchPerformance" :key="item.label" class="border-t border-white/10"><td class="px-5 py-3 font-semibold">{{ item.label }}</td><td class="px-5 py-3 text-right">{{ item.tickets }}</td><td class="px-5 py-3 text-right">{{ fmtCurrency(item.revenue) }}</td></tr></tbody>
          </table>
        </div>
        <div class="panel overflow-hidden xl:col-span-2">
          <div class="flex items-center justify-between border-b border-white/10 p-5"><h3 class="text-lg font-bold text-on-surface">Phim kinh doanh tốt nhất</h3><span class="pill-muted">Chờ: {{ superStats.pendingBookings }} · Hủy: {{ superStats.cancelledBookings }}</span></div>
          <table class="w-full text-sm">
            <thead><tr><th class="px-5 py-3 text-left">Phim</th><th class="px-5 py-3 text-right">Ghế đã bán</th><th class="px-5 py-3 text-right">Doanh thu</th></tr></thead>
            <tbody><tr v-for="item in superStats.topMovies" :key="item.label" class="border-t border-white/10"><td class="px-5 py-3 font-semibold">{{ item.label }}</td><td class="px-5 py-3 text-right">{{ item.tickets }}</td><td class="px-5 py-3 text-right">{{ fmtCurrency(item.revenue) }}</td></tr></tbody>
          </table>
        </div>
      </div>
    </section>

    <p v-if="error" class="panel border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</p>
    <p v-if="loading" class="panel border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">Đang tải dữ liệu mới nhất...</p>

    <section v-if="activeTab === 'promotions'" class="space-y-4">
      <div class="grid gap-4 xl:grid-cols-[420px_1fr]">
        <form class="panel-card space-y-3 p-5" @submit.prevent="createPromotion">
          <h3 class="text-lg font-black">Tạo mã khuyến mãi</h3>
          <div class="grid grid-cols-2 gap-3">
            <input v-model="promotionForm.code" required placeholder="Mã voucher" class="field-control uppercase" />
            <input v-model="promotionForm.name" required placeholder="Tên chương trình" class="field-control" />
            <select v-model="promotionForm.discount_type" class="field-control">
              <option value="PERCENT">Theo phần trăm</option>
              <option value="FIXED">Số tiền cố định</option>
            </select>
            <input v-model.number="promotionForm.discount_value" required min="1" type="number" placeholder="Mức giảm" class="field-control" />
            <input v-model.number="promotionForm.min_order_amount" min="0" type="number" placeholder="Đơn tối thiểu" class="field-control" />
            <input v-model.number="promotionForm.max_discount" min="1" type="number" placeholder="Giảm tối đa" class="field-control" />
            <input v-model="promotionForm.starts_at" required type="datetime-local" class="field-control" />
            <input v-model="promotionForm.ends_at" required type="datetime-local" class="field-control" />
            <input v-model.number="promotionForm.usage_limit" min="0" type="number" placeholder="Giới hạn lượt dùng" class="field-control col-span-2" />
          </div>
          <button class="primary-action w-full" type="submit">Tạo khuyến mãi</button>
        </form>

        <div class="panel-card overflow-hidden">
          <div class="border-b border-white/10 p-5">
            <h3 class="text-lg font-black">Danh sách mã</h3>
          </div>
          <div class="divide-y divide-white/10">
            <div v-for="item in promotions" :key="item.id" class="flex flex-wrap items-center justify-between gap-3 p-4">
              <div>
                <p class="font-black">{{ item.code }} · {{ item.name }}</p>
                <p class="text-xs text-on-surface-variant">
                  {{ item.discount_type === 'PERCENT' ? `${item.discount_value}%` : `${Number(item.discount_value).toLocaleString('vi-VN')}đ` }}
                  · Đã dùng {{ item.used_count }}/{{ item.usage_limit ?? '∞' }}
                </p>
              </div>
              <button class="secondary-action" type="button" @click="togglePromotion(item)">
                {{ item.is_active ? 'Tạm dừng' : 'Kích hoạt' }}
              </button>
            </div>
            <p v-if="promotions.length === 0" class="p-6 text-center text-on-surface-variant">Chưa có mã khuyến mãi.</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'movies'" class="space-y-4">
      <div class="panel p-5 space-y-4">
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-lg font-bold text-on-surface">Tạo phim mới</h3>
          <span class="pill-muted">Phim: {{ movies.length }}</span>
        </div>
        <form class="grid md:grid-cols-3 gap-3" @submit.prevent="createMovie">
          <input v-model="movieForm.title" placeholder="Tên phim" class="field-input" required />
          <input v-model.number="movieForm.duration" type="number" min="1" placeholder="Thời lượng (phút)" class="field-input" required />
          <input v-model="movieForm.releaseDate" type="date" class="field-input" />
          <input v-model="movieForm.poster" placeholder="URL poster" class="field-input" />
          <input v-model="movieForm.trailer" placeholder="URL trailer" class="field-input" />
          <select v-model="movieForm.status" class="field-input">
            <option value="UPCOMING">Sắp chiếu</option>
            <option value="NOW_SHOWING">Đang chiếu</option>
            <option value="ENDED">Đã kết thúc</option>
          </select>
          <input v-model="movieForm.genres" placeholder="Thể loại, cách nhau bởi dấu phẩy" class="field-input md:col-span-2" />
          <textarea v-model="movieForm.description" placeholder="Mô tả" class="field-input md:col-span-3" rows="3"></textarea>
          <button class="md:col-span-3 action-primary">Tạo phim</button>
        </form>
      </div>
      <div class="panel overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead><tr><th class="px-4 py-3 text-left">Phim</th><th class="px-4 py-3 text-left">Thể loại</th><th class="px-4 py-3 text-left">Thời lượng</th><th class="px-4 py-3 text-left">Thao tác</th></tr></thead>
            <tbody>
              <tr v-for="movie in movies" :key="movie.id" class="border-t border-white/10">
                <td class="px-4 py-3"><div class="font-semibold">{{ movie.title }}</div><div class="text-xs text-on-surface-variant line-clamp-1">{{ movie.description }}</div></td>
                <td class="px-4 py-3">{{ movie.genre.join(', ') || '—' }}</td>
                <td class="px-4 py-3">{{ movie.duration }} phút</td>
                <td class="px-4 py-3"><div class="flex gap-2"><button @click="editMovie(movie)" class="action-link action-link-blue">Sửa</button><button @click="deleteMovie(movie)" class="action-link action-link-rose">Xoá</button></div></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

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
                <th class="px-4 py-3">Địa chỉ</th>
                <th class="px-4 py-3">Số phòng</th>
                <th class="px-4 py-3">Trạng thái</th>
                <th class="px-4 py-3">Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in branches" :key="b.id" class="table-row">
                <td class="px-4 py-3 font-semibold text-on-surface">{{ b.code }}</td>
                <td class="px-4 py-3 text-on-surface">{{ b.name }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ b.city }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ b.address_line }}<span v-if="b.district">, {{ b.district }}</span></td>
                <td class="px-4 py-3 text-on-surface-variant">{{ b.auditoriums_count }}</td>
                <td class="px-4 py-3">
                  <span :class="b.is_active ? 'badge status-open' : 'badge status-closed'">
                    {{ b.is_active ? 'Đang hoạt động' : 'Tạm đóng' }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button @click="editBranch(b)" class="action-link action-link-blue">Sửa</button>
                    <button @click="toggleBranchActive(b)" class="action-link">
                      {{ b.is_active ? 'Tạm đóng' : 'Mở lại' }}
                    </button>
                    <button
                      @click="deleteBranch(b)"
                      class="action-link action-link-rose disabled:opacity-40"
                      :disabled="b.auditoriums_count > 0"
                      :title="b.auditoriums_count > 0 ? 'Chi nhánh đã có phòng, hãy tạm đóng thay vì xóa' : 'Xóa chi nhánh'"
                    >Xoá</button>
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
          <input v-model.number="auditoriumForm.rows" min="1" max="26" type="number" placeholder="Số hàng ghế" class="field-input" required />
          <input v-model.number="auditoriumForm.seatsPerRow" min="1" max="30" type="number" placeholder="Ghế mỗi hàng" class="field-input" required />
          <select v-model="auditoriumForm.screenType" class="field-input">
            <option value="2D">2D</option>
            <option value="3D">3D</option>
            <option value="IMAX">IMAX</option>
            <option value="4DX">4DX</option>
          </select>
          <p class="md:col-span-3 text-xs text-on-surface-variant">
            Sơ đồ ban đầu: {{ auditoriumForm.rows }} hàng × {{ auditoriumForm.seatsPerRow }} ghế.
            Sức chứa thực tế sẽ được tính lại khi lưu sơ đồ ghế.
          </p>
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
                <th class="px-4 py-3">Màn hình</th>
                <th class="px-4 py-3">Trạng thái</th>
                <th class="px-4 py-3">Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in auditoriums" :key="a.id" class="table-row">
                <td class="px-4 py-3 text-on-surface">{{ a.name }} ({{ a.code }})</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ a.branch_name }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ a.total_seats }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ a.screen_type || '2D' }}</td>
                <td class="px-4 py-3">
                  <span :class="a.is_active ? 'badge status-open' : 'badge status-closed'">
                    {{ a.is_active ? 'Hoạt động' : 'Bảo trì' }}
                  </span>
                </td>
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
        <div>
          <h3 class="text-lg font-bold text-on-surface">Thiết kế sơ đồ ghế</h3>
          <p class="text-xs text-on-surface-variant">Chọn công cụ rồi bấm vào ghế, hoặc áp dụng nhanh cho cả hàng.</p>
        </div>
        <div class="grid gap-3 md:grid-cols-3">
          <select v-model="seatForm.auditoriumId" @change="loadSeatsByAuditorium" class="field-input">
            <option value="" disabled>Chọn phòng</option>
            <option v-for="a in auditoriums" :key="a.id" :value="a.id">{{ a.branch_name }} - {{ a.name }}</option>
          </select>
          <label class="text-xs text-on-surface-variant">Số hàng
            <input v-model.number="seatLayoutRows" type="number" min="1" max="26" class="field-input mt-1 w-full" @change="resizeSeatLayout" />
          </label>
          <label class="text-xs text-on-surface-variant">Ghế mỗi hàng
            <input v-model.number="seatLayoutColumns" type="number" min="1" max="30" class="field-input mt-1 w-full" @change="resizeSeatLayout" />
          </label>
        </div>

        <div v-if="seatForm.auditoriumId" class="flex flex-wrap gap-2">
          <button
            v-for="tool in seatTools"
            :key="tool.code"
            type="button"
            class="rounded-xl border px-4 py-2 text-sm font-semibold text-white"
            :class="[tool.cls, seatTool === tool.code ? 'ring-2 ring-white' : 'border-white/10 opacity-70']"
            @click="selectSeatTool(tool.code)"
          >{{ tool.label }}</button>
        </div>

        <div v-if="seatForm.auditoriumId" class="overflow-auto rounded-2xl border border-white/10 bg-black/20 p-5">
          <div class="mx-auto mb-10 max-w-3xl">
            <div class="h-2 rounded-[100%] bg-gradient-to-r from-transparent via-primary to-transparent shadow-[0_8px_24px_rgba(229,9,20,.45)]"></div>
            <p class="mt-3 text-center text-xs font-bold tracking-[0.35em] text-on-surface-variant">MÀN HÌNH</p>
          </div>
          <div class="mx-auto w-max space-y-2">
            <div v-for="row in seatLayoutRowNames" :key="row" class="flex items-center gap-2">
              <button
                type="button"
                class="w-8 text-sm font-bold text-on-surface-variant hover:text-primary"
                title="Áp dụng công cụ cho cả hàng"
                @click="applyToolToRow(row)"
              >{{ row }}</button>
              <button
                v-for="cell in seatLayout.filter((item) => item.row === row)"
                :key="`${cell.row}-${cell.number}`"
                type="button"
                class="h-9 w-10 rounded-lg border text-[11px] font-bold transition hover:-translate-y-0.5"
                :class="
                  !cell.active ? 'border-dashed border-white/10 bg-transparent text-white/20'
                  : cell.typeCode === 'VIP' ? 'border-red-400/50 bg-red-600 text-white'
                  : cell.typeCode === 'COUPLE' ? 'border-pink-400/50 bg-pink-600 text-white'
                  : 'border-violet-400/40 bg-violet-700 text-white'
                "
                @click="applySeatTool(cell)"
              >{{ cell.active ? `${cell.row}${cell.number}` : '×' }}</button>
              <button
                type="button"
                class="w-8 text-sm font-bold text-on-surface-variant hover:text-primary"
                title="Áp dụng công cụ cho cả hàng"
                @click="applyToolToRow(row)"
              >{{ row }}</button>
            </div>
          </div>
          <div class="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4">
            <p class="text-sm text-on-surface-variant">
              Sức chứa thực tế: <strong class="text-on-surface">{{ activeSeatCount }} ghế</strong>
            </p>
            <button class="action-primary !w-auto px-8" :disabled="seatLayoutSaving" @click="saveSeatLayout">
              {{ seatLayoutSaving ? 'Đang lưu...' : 'Lưu toàn bộ sơ đồ' }}
            </button>
          </div>
        </div>

        <div v-else class="rounded-xl border border-dashed border-white/10 p-10 text-center text-sm text-on-surface-variant">
          Chọn một phòng chiếu để bắt đầu thiết kế sơ đồ.
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'showtimes'" class="space-y-4">
      <div class="panel p-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-xl font-bold text-on-surface">Điều phối lịch chiếu</h2>
          <p class="text-xs text-on-surface-variant">Xếp lịch theo phòng, kiểm tra trước rồi mới mở bán.</p>
        </div>
        <div class="flex rounded-xl bg-black/20 p-1">
          <button
            class="rounded-lg px-4 py-2 text-sm font-semibold"
            :class="showtimeMode === 'bulk' ? 'bg-primary text-white' : 'text-on-surface-variant'"
            @click="showtimeMode = 'bulk'"
          >Xếp lịch hàng loạt</button>
          <button
            class="rounded-lg px-4 py-2 text-sm font-semibold"
            :class="showtimeMode === 'single' ? 'bg-primary text-white' : 'text-on-surface-variant'"
            @click="showtimeMode = 'single'"
          >Tạo một suất</button>
        </div>
      </div>

      <div v-if="showtimeMode === 'single'" class="panel p-5 space-y-4">
        <h3 class="text-lg font-bold text-on-surface">Tạo suất chiếu</h3>
        <p class="text-xs text-on-surface-variant">Phim chọn từ TMDB sẽ được import tự động vào catalog nội bộ trước khi tạo suất.</p>
        <p v-if="error" class="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm font-semibold text-red-300">
          {{ error }}
        </p>
        <form class="grid md:grid-cols-3 gap-3" @submit.prevent="createShowtime">
          <select v-model="showtimeForm.movieId" class="field-input" required>
            <option value="" disabled>Chọn phim</option>
            <option v-for="m in showtimeMovieOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
          <select v-model="showtimeForm.auditoriumId" class="field-input" required>
            <option value="" disabled>Chọn phòng</option>
            <option v-for="a in auditoriums" :key="a.id" :value="a.id">{{ a.branch_name }} - {{ a.name }}</option>
          </select>
          <div>
            <input v-model.number="showtimeForm.basePrice" type="number" min="1000" step="1000" placeholder="Giá vé" class="field-input w-full" required />
            <p v-if="selectedShowtimeMovie" class="mt-1 px-1 text-[10px] text-primary">
              Giá gợi ý theo dữ liệu TMDB, có thể chỉnh sửa
            </p>
          </div>
          <div>
            <input v-model="showtimeForm.startsAt" :min="minimumShowtimeDate" type="datetime-local" class="field-input w-full" required />
            <p v-if="selectedMovieReleaseDate" class="mt-1 px-1 text-[10px] text-on-surface-variant">
              Khởi chiếu: {{ new Date(`${selectedMovieReleaseDate}T00:00:00`).toLocaleDateString('vi-VN') }}
            </p>
          </div>
          <div>
            <input v-model="showtimeForm.endsAt" :min="showtimeForm.startsAt" type="datetime-local" class="field-input w-full" required />
            <p class="mt-1 px-1 text-[10px] text-on-surface-variant">
              Tự tính theo thời lượng {{ selectedMovieDuration }} phút
            </p>
          </div>
          <select v-model="showtimeForm.status" class="field-input">
            <option value="DRAFT">DRAFT - Chưa mở bán</option>
            <option value="OPEN">OPEN</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
          <button class="md:col-span-3 action-primary">Tạo suất chiếu</button>
        </form>
      </div>

      <div v-else class="panel p-5 space-y-5">
        <div>
          <h3 class="text-lg font-bold text-on-surface">Tạo lịch chiếu tự động</h3>
          <p class="mt-1 text-xs text-on-surface-variant">
            Hệ thống luân phiên phim trong từng phòng, tự tính giờ kết thúc và thời gian vệ sinh giữa hai suất.
          </p>
        </div>

        <div class="grid gap-3 md:grid-cols-5">
          <label class="text-xs text-on-surface-variant">Từ ngày
            <input v-model="bulkForm.startDate" type="date" class="field-input mt-1 w-full" />
          </label>
          <label class="text-xs text-on-surface-variant">Đến ngày
            <input v-model="bulkForm.endDate" :min="bulkForm.startDate" type="date" class="field-input mt-1 w-full" />
          </label>
          <label class="text-xs text-on-surface-variant">Mở cửa
            <input v-model="bulkForm.openingTime" type="time" class="field-input mt-1 w-full" />
          </label>
          <label class="text-xs text-on-surface-variant">Đóng cửa
            <input v-model="bulkForm.closingTime" type="time" class="field-input mt-1 w-full" />
          </label>
          <label class="text-xs text-on-surface-variant">Nghỉ giữa suất (phút)
            <input v-model.number="bulkForm.gapMinutes" type="number" min="0" max="90" class="field-input mt-1 w-full" />
          </label>
        </div>

        <div class="grid gap-5 lg:grid-cols-2">
          <div>
            <div class="mb-2 flex items-center justify-between">
              <h4 class="font-semibold text-on-surface">1. Chọn phim trong catalog</h4>
              <span class="text-xs text-primary">{{ bulkForm.movieIds.length }} phim</span>
            </div>
            <div class="max-h-52 space-y-1 overflow-auto rounded-xl border border-white/10 bg-black/10 p-2">
              <label v-for="movie in movies" :key="movie.id" class="flex cursor-pointer items-center gap-3 rounded-lg p-2 hover:bg-white/5">
                <input v-model="bulkForm.movieIds" type="checkbox" :value="movie.id" class="rounded border-white/20 bg-transparent text-primary" />
                <span class="min-w-0 flex-1 truncate text-sm text-on-surface">{{ movie.title }}</span>
                <span class="text-xs text-on-surface-variant">{{ movie.duration }} phút</span>
              </label>
            </div>
          </div>
          <div>
            <div class="mb-2 flex items-center justify-between">
              <h4 class="font-semibold text-on-surface">2. Chọn phòng áp dụng</h4>
              <span class="text-xs text-primary">{{ bulkForm.auditoriumIds.length }} phòng</span>
            </div>
            <div class="max-h-52 space-y-1 overflow-auto rounded-xl border border-white/10 bg-black/10 p-2">
              <label v-for="room in auditoriums" :key="room.id" class="flex cursor-pointer items-center gap-3 rounded-lg p-2 hover:bg-white/5">
                <input v-model="bulkForm.auditoriumIds" type="checkbox" :value="room.id" class="rounded border-white/20 bg-transparent text-primary" />
                <span class="min-w-0 flex-1 truncate text-sm text-on-surface">{{ room.branch_name }} · {{ room.name }}</span>
                <span class="text-xs text-on-surface-variant">{{ room.screen_type || '2D' }}</span>
              </label>
            </div>
          </div>
        </div>

        <button class="action-primary w-full" @click="generateBulkPreview">Tạo bản xem trước</button>

        <div v-if="bulkPreview.length" class="space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h4 class="font-bold text-on-surface">Bản xem trước</h4>
              <p class="text-xs text-on-surface-variant">{{ bulkPreview.length }} suất · Có thể đổi phim, phòng, giờ và giá trước khi lưu nháp</p>
              <p v-if="bulkConflictCount" class="mt-1 text-xs font-semibold text-red-400">
                Có {{ bulkConflictCount }} suất trùng với lịch hiện tại. Hãy đổi ngày/phòng trước khi lưu.
              </p>
            </div>
            <button class="action-primary !w-auto px-6" :disabled="bulkPublishing || bulkConflictCount > 0" @click="saveBulkDraftSchedule">
              {{ bulkPublishing ? 'Đang lưu...' : `Lưu ${bulkPreview.length} suất thành bản nháp` }}
            </button>
          </div>
          <div class="max-h-[520px] overflow-auto rounded-xl border border-white/10">
            <table class="w-full min-w-[1250px] text-sm">
              <thead class="table-head">
                <tr>
                  <th class="px-3 py-3 text-left">Ngày & giờ bắt đầu</th>
                  <th class="px-3 py-3 text-left">Giờ kết thúc</th>
                  <th class="px-3 py-3 text-left">Phòng</th>
                  <th class="px-3 py-3 text-left">Phim</th>
                  <th class="px-3 py-3 text-left">Giá</th>
                  <th class="px-3 py-3 text-center">Thao tác</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in bulkPreview"
                  :key="index"
                  class="table-row"
                  :class="bulkConflictIndexes.has(index) ? '!bg-red-500/10' : ''"
                >
                  <td class="px-3 py-2">
                    <input
                      v-model="item.starts_at"
                      type="datetime-local"
                      class="field-input w-full !px-3 !py-2"
                      @change="updateBulkDraftStart(index)"
                    />
                    <span v-if="bulkConflictIndexes.has(index)" class="mt-1 block text-[10px] font-bold text-red-400">
                      Trùng lịch phòng
                    </span>
                  </td>
                  <td class="px-3 py-2">
                    <div class="rounded-lg bg-black/20 px-3 py-2 font-semibold text-on-surface">
                      {{ new Date(item.ends_at).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) }}
                    </div>
                  </td>
                  <td class="px-3 py-2">
                    <select
                      v-model="item.auditorium_id"
                      class="field-input w-full !px-3 !py-2"
                      @change="updateBulkDraftRoom(index)"
                    >
                      <option v-for="room in auditoriums" :key="room.id" :value="room.id">
                        {{ room.branch_name }} · {{ room.name }}
                      </option>
                    </select>
                  </td>
                  <td class="px-3 py-2">
                    <select
                      v-model="item.movie_id"
                      class="field-input w-full !px-3 !py-2"
                      @change="updateBulkDraftMovie(index)"
                    >
                      <option v-for="movie in movies" :key="movie.id" :value="movie.id">
                        {{ movie.title }} ({{ movie.duration }} phút)
                      </option>
                    </select>
                  </td>
                  <td class="px-3 py-2">
                    <input v-model.number="item.base_price" type="number" min="1000" step="1000" class="field-input w-32 !px-3 !py-2" />
                  </td>
                  <td class="px-3 py-2 text-center">
                    <button class="rounded-lg border border-red-500/30 px-3 py-2 font-semibold text-red-400 hover:bg-red-500/10" @click="removeBulkDraft(index)">
                      Xóa suất
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="panel p-5 space-y-4">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h3 class="text-lg font-bold text-on-surface">Lịch vận hành theo phòng</h3>
            <p class="text-xs text-on-surface-variant">Mỗi cột là một phòng; các thẻ được sắp theo giờ bắt đầu.</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              v-if="draftShowtimes.length"
              class="action-primary !w-auto"
              :disabled="bulkPublishing"
              @click="publishDraftShowtimes"
            >
              {{ bulkPublishing ? 'Đang mở bán...' : `Xuất bản ${draftShowtimes.length} suất nháp` }}
            </button>
            <button type="button" class="secondary-action !px-3" title="Ngày trước" @click="moveScheduleDate(-1)">←</button>
            <button type="button" class="secondary-action" @click="selectToday">Hôm nay</button>
            <input v-model="scheduleDate" type="date" class="field-input !w-auto" />
            <button type="button" class="secondary-action !px-3" title="Ngày sau" @click="moveScheduleDate(1)">→</button>
            <select v-model="scheduleBranch" class="field-input !w-auto">
              <option value="">Tất cả chi nhánh</option>
              <option v-for="branch in scheduleBranchOptions" :key="branch" :value="branch">{{ branch }}</option>
            </select>
            <select v-model="scheduleStatus" class="field-input !w-auto">
              <option value="ALL">Tất cả trạng thái</option>
              <option value="ACTIVE">Đang mở / Bản nháp</option>
              <option value="OPEN">Đang mở bán</option>
              <option value="DRAFT">Bản nháp</option>
              <option value="FINISHED">Đã kết thúc</option>
              <option value="CANCELLED">Đã hủy</option>
            </select>
          </div>
        </div>
        <div v-if="availableScheduleDates.length" class="flex gap-2 overflow-x-auto pb-1">
          <button
            v-for="dateItem in availableScheduleDates"
            :key="dateItem.date"
            type="button"
            class="shrink-0 rounded-xl border px-3 py-2 text-left transition"
            :class="scheduleDate === dateItem.date ? 'border-primary bg-primary/15 text-white' : 'border-white/10 bg-black/10 text-on-surface-variant hover:border-white/25'"
            @click="scheduleDate = dateItem.date"
          >
            <span class="block text-xs font-bold">{{ new Date(`${dateItem.date}T12:00:00`).toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' }) }}</span>
            <span class="text-[10px]">{{ dateItem.count }} suất</span>
          </button>
        </div>
        <div class="grid grid-cols-2 gap-2 md:grid-cols-5">
          <div class="rounded-xl border border-white/10 bg-black/10 p-3"><p class="text-[10px] uppercase text-on-surface-variant">Tổng suất</p><strong>{{ scheduleSummary.total }}</strong></div>
          <div class="rounded-xl border border-white/10 bg-black/10 p-3"><p class="text-[10px] uppercase text-on-surface-variant">Mở bán</p><strong class="text-emerald-400">{{ scheduleSummary.open }}</strong></div>
          <div class="rounded-xl border border-white/10 bg-black/10 p-3"><p class="text-[10px] uppercase text-on-surface-variant">Bản nháp</p><strong class="text-amber-400">{{ scheduleSummary.draft }}</strong></div>
          <div class="rounded-xl border border-white/10 bg-black/10 p-3"><p class="text-[10px] uppercase text-on-surface-variant">Ghế đã bán</p><strong>{{ scheduleSummary.sold }}</strong></div>
          <div class="rounded-xl border border-white/10 bg-black/10 p-3"><p class="text-[10px] uppercase text-on-surface-variant">Doanh thu</p><strong>{{ fmtCurrency(scheduleSummary.revenue) }}</strong></div>
        </div>
        <div v-if="scheduleRooms.length" class="grid gap-3 overflow-x-auto" :style="{ gridTemplateColumns: `repeat(${scheduleRooms.length}, minmax(260px, 1fr))` }">
          <div v-for="room in scheduleRooms" :key="`${room.branch}-${room.name}`" class="rounded-xl border border-white/10 bg-black/10 p-3">
            <div class="mb-3 border-b border-white/10 pb-2">
              <h4 class="font-bold text-on-surface">{{ room.name }}</h4>
              <p class="text-xs text-on-surface-variant">{{ room.branch }}</p>
            </div>
            <div class="space-y-2">
              <article v-for="item in room.items" :key="item.id" class="rounded-lg border-l-4 p-3" :class="item.status === 'OPEN' ? 'border-l-emerald-500 bg-emerald-500/10' : item.status === 'CANCELLED' ? 'border-l-red-500 bg-red-500/10' : 'border-l-amber-500 bg-amber-500/10'">
                <div class="flex items-center justify-between gap-2">
                  <strong class="text-sm text-on-surface">{{ new Date(item.starts_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }}–{{ new Date(item.ends_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }}</strong>
                  <span class="text-[10px] font-bold">{{ item.status }}</span>
                </div>
                <p class="mt-1 line-clamp-2 text-sm font-semibold text-on-surface">{{ item.movie_title }}</p>
                <p class="mt-1 text-[11px] text-on-surface-variant">
                  {{ item.sold_seats }} ghế đã bán · {{ fmtCurrency(item.revenue) }}
                </p>
                <div class="mt-2 flex gap-3 text-xs">
                  <button class="text-sky-400" @click="editShowtime(item)">Sửa</button>
                  <button
                    class="text-rose-400 disabled:cursor-not-allowed disabled:opacity-40"
                    :disabled="item.booking_count > 0"
                    :title="item.booking_count > 0 ? 'Suất đã phát sinh đơn, chỉ có thể hủy' : 'Xóa suất'"
                    @click="deleteShowtime(item)"
                  >Xóa</button>
                </div>
              </article>
            </div>
          </div>
        </div>
        <div v-else class="rounded-xl border border-dashed border-white/10 p-8 text-center text-sm text-on-surface-variant">
          Không có suất chiếu phù hợp ngày và bộ lọc đã chọn.
        </div>
      </div>

      <div class="panel overflow-hidden">
        <div class="border-b border-white/10 px-5 py-4">
          <h3 class="font-bold text-on-surface">Danh sách chi tiết · {{ filteredScheduleShowtimes.length }} suất</h3>
        </div>
        <div class="overflow-auto">
          <table class="w-full text-sm min-w-[960px]">
            <thead class="table-head">
              <tr class="text-left text-on-surface-variant">
                <th class="px-4 py-3">Phim</th>
                <th class="px-4 py-3">Rạp/Phòng</th>
                <th class="px-4 py-3">Bắt đầu</th>
                <th class="px-4 py-3">Kết thúc</th>
                <th class="px-4 py-3">Giá</th>
                <th class="px-4 py-3">Đã bán</th>
                <th class="px-4 py-3">Doanh thu</th>
                <th class="px-4 py-3">Trạng thái</th>
                <th class="px-4 py-3">Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="st in filteredScheduleShowtimes" :key="st.id" class="table-row">
                <td class="px-4 py-3 font-semibold text-on-surface">{{ st.movie_title }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ st.branch_name }} - {{ st.auditorium_name }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ fmtDateTime(st.starts_at) }}</td>
                <td class="px-4 py-3 text-on-surface-variant">{{ fmtDateTime(st.ends_at) }}</td>
                <td class="px-4 py-3 text-on-surface">{{ fmtCurrency(st.base_price) }}</td>
                <td class="px-4 py-3 text-on-surface">{{ st.sold_seats }} ghế / {{ st.booking_count }} đơn</td>
                <td class="px-4 py-3 text-on-surface">{{ fmtCurrency(st.revenue) }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold" :class="showtimeStatusClass(st.status)">{{ st.status }}</span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button @click="editShowtime(st)" class="action-link action-link-blue">Sửa</button>
                    <button
                      @click="deleteShowtime(st)"
                      class="action-link action-link-rose disabled:cursor-not-allowed disabled:opacity-40"
                      :disabled="st.booking_count > 0"
                      :title="st.booking_count > 0 ? 'Suất đã phát sinh đơn, chỉ có thể hủy' : 'Xóa suất'"
                    >Xoá</button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredScheduleShowtimes.length === 0">
                <td colspan="9" class="px-4 py-10 text-center text-on-surface-variant">Không có dữ liệu cho ngày và bộ lọc hiện tại.</td>
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
.status-draft { background: rgba(59, 130, 246, 0.16); border-color: rgba(59, 130, 246, 0.28); color: #bfdbfe; }
.status-cancelled { background: rgba(148, 163, 184, 0.16); border-color: rgba(148, 163, 184, 0.26); color: #cbd5e1; }

@media (max-width: 768px) {
  .hero-title {
    font-size: 1.35rem;
  }
}
</style>

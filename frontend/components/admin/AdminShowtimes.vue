<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { adminBackendService, movieService, type AdminAuditorium, type AdminShowtime, type Movie, type BulkShowtimeDraft } from '~/services/api'
import { useUserStore } from '~/store/user'

const userStore = useUserStore()
const isBranchAdmin = computed(() => userStore.currentUser?.role === 'branch-admin')

const auditoriums = ref<AdminAuditorium[]>([])
const showtimes = ref<AdminShowtime[]>([])
const movies = ref<Movie[]>([])
const loading = ref(false)
const error = ref('')

const showtimeMode = ref<'single' | 'bulk'>('bulk')

const showtimeForm = ref({
  movieId: '',
  auditoriumId: '',
  startsAt: '',
  endsAt: '',
  basePrice: 90000,
  status: 'DRAFT' as 'DRAFT' | 'OPEN' | 'CANCELLED',
})

const bulkForm = ref({
  startDate: toDateTimeLocal(new Date()).slice(0, 10),
  endDate: toDateTimeLocal(new Date()).slice(0, 10),
  openingTime: '09:00',
  closingTime: '23:30',
  gapMinutes: 15,
  movieIds: [] as string[],
  auditoriumIds: [] as string[],
})

const bulkPreview = ref<BulkShowtimeDraft[]>([])
const bulkPublishing = ref(false)

const scheduleDate = ref(toDateTimeLocal(new Date()).slice(0, 10))
const scheduleBranch = ref('')
const scheduleStatus = ref<'ALL' | 'ACTIVE' | 'OPEN' | 'DRAFT' | 'FINISHED' | 'CANCELLED'>('ALL')

const showtimeMovieOptions = computed(() => {
  return movies.value.map((movie) => ({
    value: movie.id,
    label: movie.title,
    suggestedPrice: showtimes.value.find((item) => item.movie_id === movie.id)?.base_price || 90000,
  }))
})

const selectedShowtimeMovie = computed(() =>
  showtimeMovieOptions.value.find((movie) => movie.value === showtimeForm.value.movieId),
)

const selectedMovieReleaseDate = ref('')
const selectedMovieDuration = ref(120)

watch(
  () => showtimeForm.value.movieId,
  (movieId) => {
    if (selectedShowtimeMovie.value) {
      showtimeForm.value.basePrice = Number(selectedShowtimeMovie.value.suggestedPrice)
    }

    const backendMovie = movies.value.find((movie) => movie.id === movieId)
    selectedMovieReleaseDate.value = backendMovie?.releaseDate || ''
    selectedMovieDuration.value = backendMovie?.duration || 120

    applySuggestedShowtime()
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

const scheduleBranchOptions = computed(() =>
  [...new Set(auditoriums.value.map((item) => item.branch_name))].sort(),
)

const draftShowtimes = computed(() => showtimes.value.filter((item) => item.stored_status === 'DRAFT'))
const bulkConflictIndexes = computed(() => {
  const conflicts = new Set<number>()

  bulkPreview.value.forEach((draft: BulkShowtimeDraft, index: number) => {
    // 1. Kiểm tra trùng lịch với danh sách suất chiếu hiện có trên hệ thống
    if (
      showtimes.value.some(
        (current: AdminShowtime) =>
          current.status !== 'CANCELLED' &&
          current.auditorium_id === draft.auditorium_id &&
          new Date(current.starts_at) < new Date(draft.ends_at) &&
          new Date(current.ends_at) > new Date(draft.starts_at),
      )
    ) {
      conflicts.add(index)
    }

    // 2. Kiểm tra trùng lịch giữa các suất chiếu trong chính danh sách tạo hàng loạt (drafts)
    bulkPreview.value.forEach((other: BulkShowtimeDraft, otherIndex: number) => {
      if (
        index !== otherIndex &&
        other.auditorium_id === draft.auditorium_id &&
        new Date(other.starts_at) < new Date(draft.ends_at) &&
        new Date(other.ends_at) > new Date(draft.starts_at)
      ) {
        conflicts.add(index)
      }
    })
  })

  return conflicts
})
const bulkConflictCount = computed(() => bulkConflictIndexes.value.size)

const minimumShowtimeDate = computed(() => {
  const today = toDateTimeLocal(new Date())
  if (!selectedMovieReleaseDate.value) return today
  const release = `${selectedMovieReleaseDate.value}T00:00`
  return release > today ? release : today
})

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

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [auditoriumData, showtimeData, movieData] = await Promise.all([
      adminBackendService.getAuditoriums(),
      adminBackendService.getShowtimes(),
      movieService.getAll(),
    ])
    auditoriums.value = auditoriumData
    showtimes.value = showtimeData
    movies.value = movieData
    
    selectNearestUsefulScheduleDate()
    
    if (!showtimeForm.value.movieId && showtimeMovieOptions.value.length > 0) {
      showtimeForm.value.movieId = showtimeMovieOptions.value[0].value
    }
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải dữ liệu lịch chiếu.'
  } finally {
    loading.value = false
  }
}

async function createShowtime() {
  error.value = ''
  try {
    const movieId = showtimeForm.value.movieId
    if (new Date(showtimeForm.value.startsAt) < new Date(minimumShowtimeDate.value)) {
      throw new Error('Suất chiếu không thể bắt đầu trước ngày khởi chiếu của phim.')
    }
    if (
      showtimeForm.value.status === 'OPEN'
      && new Date(showtimeForm.value.startsAt).getTime() <= Date.now() + 15 * 60 * 1000
    ) {
      throw new Error('Suất chiếu OPEN phải bắt đầu sau hiện tại ít nhất 15 phút để còn thời gian bán vé.')
    }

    await adminBackendService.createShowtime({
      movie_id: movieId,
      auditorium_id: showtimeForm.value.auditoriumId,
      starts_at: toIso(showtimeForm.value.startsAt),
      ends_at: toIso(showtimeForm.value.endsAt),
      base_price: showtimeForm.value.basePrice,
      status: showtimeForm.value.status,
    })
    showtimes.value = await adminBackendService.getShowtimes()
    alert('Tạo suất chiếu thành công!')
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
    alert(`Đã lưu ${bulkPreview.value.length} suất chiếu nháp.`)
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
    alert('Đã mở bán thành công!')
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

function showtimeStatusClass(status: string) {
  if (status === 'OPEN') return 'badge bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
  if (status === 'DRAFT') return 'badge bg-amber-500/10 text-amber-400 border border-amber-500/20'
  if (status === 'CANCELLED') return 'badge bg-rose-500/10 text-rose-400 border border-rose-500/20'
  return 'badge bg-white/5 text-white/50 border border-white/10'
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="space-y-6">
    <div class="panel p-5 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-on-surface flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">calendar_month</span>
          Điều phối Lịch chiếu
        </h2>
        <p class="text-xs text-on-surface-variant mt-1">Sắp xếp lịch chiếu tự động hoặc thủ công. Lịch mới sẽ được lưu nháp trước khi mở bán chính thức.</p>
      </div>
      
      <div class="flex bg-black/40 p-1 rounded-xl border border-white/5">
        <button
          class="rounded-lg px-5 py-2 text-sm font-bold transition-all"
          :class="showtimeMode === 'bulk' ? 'bg-primary text-white shadow-lg' : 'text-on-surface-variant hover:text-white'"
          @click="showtimeMode = 'bulk'"
        >Xếp lịch hàng loạt</button>
        <button
          class="rounded-lg px-5 py-2 text-sm font-bold transition-all"
          :class="showtimeMode === 'single' ? 'bg-primary text-white shadow-lg' : 'text-on-surface-variant hover:text-white'"
          @click="showtimeMode = 'single'"
        >Tạo một suất</button>
      </div>
    </div>
    
    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-400 animate-fade-in">
      {{ error }}
    </p>

    <!-- Create Single -->
    <div v-if="showtimeMode === 'single'" class="panel p-6 space-y-5 animate-fade-in">
      <h3 class="text-lg font-bold text-on-surface border-b border-white/10 pb-3 flex items-center gap-2">
        <span class="material-symbols-outlined text-[20px]">add</span>
        Tạo thủ công một suất chiếu
      </h3>
      
      <form class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5" @submit.prevent="createShowtime">
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Bộ phim</label>
          <select v-model="showtimeForm.movieId" class="field-input" required>
            <option value="" disabled>-- Chọn phim --</option>
            <option v-for="m in showtimeMovieOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Phòng chiếu</label>
          <select v-model="showtimeForm.auditoriumId" class="field-input" required>
            <option value="" disabled>-- Chọn phòng --</option>
            <option v-for="a in auditoriums" :key="a.id" :value="a.id">{{ a.branch_name }} - {{ a.name }}</option>
          </select>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Giá cơ bản (VNĐ)</label>
          <input v-model.number="showtimeForm.basePrice" type="number" min="1000" step="1000" placeholder="VD: 90000" class="field-input" required />
          <p v-if="selectedShowtimeMovie" class="text-[10px] text-primary mt-1">Gợi ý từ lịch sử: {{ fmtCurrency(selectedShowtimeMovie.suggestedPrice) }}</p>
        </div>
        
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Giờ bắt đầu chiếu</label>
          <input v-model="showtimeForm.startsAt" :min="minimumShowtimeDate" type="datetime-local" class="field-input" required />
          <p v-if="selectedMovieReleaseDate" class="text-[10px] text-on-surface-variant mt-1">
            Ngày ra mắt phim: {{ new Date(`${selectedMovieReleaseDate}T00:00:00`).toLocaleDateString('vi-VN') }}
          </p>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Giờ kết thúc (Dự kiến)</label>
          <input v-model="showtimeForm.endsAt" :min="showtimeForm.startsAt" type="datetime-local" class="field-input" required />
          <p class="text-[10px] text-on-surface-variant mt-1">
            Tự động tính bằng Thời lượng phim ({{ selectedMovieDuration }} phút)
          </p>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Trạng thái khởi tạo</label>
          <select v-model="showtimeForm.status" class="field-input">
            <option value="DRAFT">Lưu nháp (DRAFT) - Chưa bán</option>
            <option value="OPEN">Mở bán ngay (OPEN)</option>
          </select>
        </div>
        
        <div class="xl:col-span-3 pt-3 border-t border-white/10 flex justify-end">
          <button type="submit" class="action-primary px-8 flex items-center gap-2 text-base">
            <span class="material-symbols-outlined">movie</span> Xác nhận tạo
          </button>
        </div>
      </form>
    </div>

    <!-- Create Bulk -->
    <div v-else class="panel p-6 space-y-6 animate-fade-in">
      <div>
        <h3 class="text-lg font-bold text-on-surface flex items-center gap-2">
          <span class="material-symbols-outlined text-[20px]">auto_mode</span>
          Lên lịch tự động thông minh
        </h3>
        <p class="text-xs text-on-surface-variant mt-1">
          Hệ thống sẽ luân phiên phát các phim đã chọn trong các phòng chiếu theo thời gian làm việc.
        </p>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Từ ngày</label>
          <input v-model="bulkForm.startDate" type="date" class="field-input" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Đến ngày</label>
          <input v-model="bulkForm.endDate" :min="bulkForm.startDate" type="date" class="field-input" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Mở rạp lúc</label>
          <input v-model="bulkForm.openingTime" type="time" class="field-input" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Đóng rạp lúc</label>
          <input v-model="bulkForm.closingTime" type="time" class="field-input" />
        </div>
        <div class="space-y-1 col-span-2 md:col-span-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Vệ sinh rạp (phút)</label>
          <input v-model.number="bulkForm.gapMinutes" type="number" min="0" max="90" class="field-input" />
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Movies Selection -->
        <div class="flex flex-col h-full bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
          <div class="p-3 border-b border-white/10 bg-black/40 flex justify-between items-center">
            <h4 class="font-bold text-sm text-on-surface">1. Chọn phim để chiếu</h4>
            <span class="badge bg-primary/20 text-primary border border-primary/30">{{ bulkForm.movieIds.length }} phim</span>
          </div>
          <div class="p-2 overflow-y-auto max-h-64 space-y-1">
            <label v-for="movie in movies" :key="movie.id" class="flex cursor-pointer items-center gap-3 rounded-xl p-3 hover:bg-white/5 transition border border-transparent hover:border-white/10" :class="{ 'bg-primary/5 border-primary/20': bulkForm.movieIds.includes(movie.id) }">
              <input v-model="bulkForm.movieIds" type="checkbox" :value="movie.id" class="rounded border-white/20 text-primary focus:ring-primary w-4 h-4" />
              <div class="flex-1 min-w-0">
                <p class="truncate text-sm font-bold text-on-surface">{{ movie.title }}</p>
                <p class="text-xs text-on-surface-variant">{{ movie.duration }} phút</p>
              </div>
            </label>
          </div>
        </div>
        
        <!-- Rooms Selection -->
        <div class="flex flex-col h-full bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
          <div class="p-3 border-b border-white/10 bg-black/40 flex justify-between items-center">
            <h4 class="font-bold text-sm text-on-surface">2. Chọn phòng áp dụng</h4>
            <span class="badge bg-primary/20 text-primary border border-primary/30">{{ bulkForm.auditoriumIds.length }} phòng</span>
          </div>
          <div class="p-2 overflow-y-auto max-h-64 space-y-1">
            <label v-for="room in auditoriums" :key="room.id" class="flex cursor-pointer items-center gap-3 rounded-xl p-3 hover:bg-white/5 transition border border-transparent hover:border-white/10" :class="{ 'bg-primary/5 border-primary/20': bulkForm.auditoriumIds.includes(room.id) }">
              <input v-model="bulkForm.auditoriumIds" type="checkbox" :value="room.id" class="rounded border-white/20 text-primary focus:ring-primary w-4 h-4" />
              <div class="flex-1 min-w-0">
                <p class="truncate text-sm font-bold text-on-surface">{{ room.name }}</p>
                <p class="text-xs text-on-surface-variant">{{ room.branch_name }}</p>
              </div>
              <span class="text-[10px] uppercase font-bold bg-white/10 px-2 py-1 rounded text-white/70">{{ room.screen_type || '2D' }}</span>
            </label>
          </div>
        </div>
      </div>

      <button class="w-full action-primary py-3 text-base flex justify-center items-center gap-2" @click="generateBulkPreview">
        <span class="material-symbols-outlined">preview</span> Tạo Bản xem trước lịch chiếu
      </button>

      <!-- Preview Editor -->
      <div v-if="bulkPreview.length" class="animate-fade-in space-y-4 pt-4 border-t border-white/10 mt-6">
        <div class="flex flex-wrap items-center justify-between gap-4 bg-black/40 p-4 rounded-xl border border-white/5">
          <div>
            <h4 class="text-lg font-black text-on-surface flex items-center gap-2">
              Bản xem trước <span class="badge bg-white/10 text-white/70">{{ bulkPreview.length }} suất</span>
            </h4>
            <p class="text-xs text-on-surface-variant mt-1">Dễ dàng điều chỉnh thông số từng suất trước khi lưu vào hệ thống.</p>
            <p v-if="bulkConflictCount" class="mt-2 text-xs font-bold text-rose-400 flex items-center gap-1">
              <span class="material-symbols-outlined text-[16px]">warning</span> Phát hiện {{ bulkConflictCount }} suất bị trùng giờ. Vui lòng sửa lại!
            </p>
          </div>
          <button class="action-primary !w-auto px-8 py-3 shadow-[0_0_20px_rgba(229,9,20,0.3)] hover:shadow-[0_0_30px_rgba(229,9,20,0.5)] transition-shadow" :disabled="bulkPublishing || bulkConflictCount > 0" @click="saveBulkDraftSchedule">
            <span class="flex items-center gap-2">
              <span class="material-symbols-outlined" v-if="!bulkPublishing">cloud_upload</span>
              {{ bulkPublishing ? 'Đang lưu...' : `Xác nhận & Lưu ${bulkPreview.length} suất nháp` }}
            </span>
          </button>
        </div>
        
        <div class="max-h-[500px] overflow-auto rounded-2xl border border-white/10 shadow-inner">
          <table class="w-full min-w-[1200px] text-sm text-left">
            <thead class="sticky top-0 bg-[#242626] border-b border-white/10 shadow-md z-10">
              <tr>
                <th class="px-4 py-4 font-bold text-on-surface-variant w-[240px]">Bắt đầu</th>
                <th class="px-4 py-4 font-bold text-on-surface-variant">Kết thúc</th>
                <th class="px-4 py-4 font-bold text-on-surface-variant w-[240px]">Phòng</th>
                <th class="px-4 py-4 font-bold text-on-surface-variant w-[240px]">Phim</th>
                <th class="px-4 py-4 font-bold text-on-surface-variant w-[160px]">Giá vé (VNĐ)</th>
                <th class="px-4 py-4 font-bold text-on-surface-variant text-center">Thao tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5 bg-black/20">
              <tr
                v-for="(item, index) in bulkPreview"
                :key="index"
                class="hover:bg-white/5 transition-colors"
                :class="bulkConflictIndexes.has(index) ? '!bg-rose-500/10' : ''"
              >
                <td class="px-4 py-3">
                  <input v-model="item.starts_at" type="datetime-local" class="field-input !py-1.5" @change="updateBulkDraftStart(index)" />
                  <span v-if="bulkConflictIndexes.has(index)" class="mt-1 block text-[10px] font-black text-rose-400">Trùng lịch phòng</span>
                </td>
                <td class="px-4 py-3">
                  <div class="rounded-lg bg-white/5 border border-white/5 px-3 py-2 text-xs font-bold text-on-surface-variant flex items-center justify-center">
                    {{ new Date(item.ends_at).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) }}
                  </div>
                </td>
                <td class="px-4 py-3">
                  <select v-model="item.auditorium_id" class="field-input !py-1.5" @change="updateBulkDraftRoom(index)">
                    <option v-for="room in auditoriums" :key="room.id" :value="room.id">{{ room.branch_name }} · {{ room.name }}</option>
                  </select>
                </td>
                <td class="px-4 py-3">
                  <select v-model="item.movie_id" class="field-input !py-1.5 truncate pr-8" @change="updateBulkDraftMovie(index)">
                    <option v-for="movie in movies" :key="movie.id" :value="movie.id">{{ movie.title }} ({{ movie.duration }}p)</option>
                  </select>
                </td>
                <td class="px-4 py-3">
                  <input v-model.number="item.base_price" type="number" min="1000" step="1000" class="field-input !py-1.5 font-bold text-primary" />
                </td>
                <td class="px-4 py-3 text-center">
                  <button class="w-8 h-8 rounded-full bg-rose-500/10 text-rose-400 hover:bg-rose-500 hover:text-white flex items-center justify-center transition-colors mx-auto" @click="removeBulkDraft(index)" title="Xoá suất này">
                    <span class="material-symbols-outlined text-[18px]">close</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Schedule Management -->
    <div class="panel p-0 overflow-hidden shadow-2xl border-white/10">
      <!-- Toolbar Header -->
      <div class="bg-black/40 p-5 border-b border-white/10 flex flex-col xl:flex-row gap-5 items-center justify-between">
        <div>
          <h3 class="text-xl font-bold text-on-surface flex items-center gap-2">
            Lịch vận hành
            <span class="badge bg-primary/20 text-primary text-xs ml-2">{{ scheduleSummary.total }} suất chiếu</span>
          </h3>
          <p class="text-xs text-on-surface-variant mt-1">Cái nhìn tổng quan về lịch chiếu hiện tại của rạp. Bạn có thể xuất bản suất nháp từ đây.</p>
        </div>
        
        <div class="flex flex-wrap gap-3 items-center w-full xl:w-auto">
          <!-- Filter tools -->
          <div class="flex items-center bg-black/50 p-1 rounded-xl border border-white/10">
            <button type="button" class="w-8 h-8 flex items-center justify-center rounded-lg text-on-surface-variant hover:text-white hover:bg-white/10 transition" title="Ngày trước" @click="moveScheduleDate(-1)"><span class="material-symbols-outlined text-[18px]">chevron_left</span></button>
            <input v-model="scheduleDate" type="date" class="bg-transparent border-none text-sm font-bold text-on-surface focus:outline-none w-[120px] text-center" />
            <button type="button" class="w-8 h-8 flex items-center justify-center rounded-lg text-on-surface-variant hover:text-white hover:bg-white/10 transition" title="Ngày sau" @click="moveScheduleDate(1)"><span class="material-symbols-outlined text-[18px]">chevron_right</span></button>
            <div class="w-px h-5 bg-white/20 mx-1"></div>
            <button type="button" class="text-xs font-bold text-sky-400 px-3 hover:text-sky-300" @click="selectToday">Hôm nay</button>
          </div>
          
          <select v-model="scheduleBranch" class="field-input !w-auto bg-black/50 text-sm">
            <option value="">Tất cả chi nhánh</option>
            <option v-for="branch in scheduleBranchOptions" :key="branch" :value="branch">{{ branch }}</option>
          </select>
          
          <select v-model="scheduleStatus" class="field-input !w-auto bg-black/50 text-sm">
            <option value="ALL">Tất cả trạng thái</option>
            <option value="ACTIVE">Đang mở & Bản nháp</option>
            <option value="OPEN">Đang mở bán (OPEN)</option>
            <option value="DRAFT">Bản nháp (DRAFT)</option>
            <option value="FINISHED">Đã kết thúc</option>
            <option value="CANCELLED">Đã hủy</option>
          </select>
          
          <button
            v-if="draftShowtimes.length"
            class="action-primary !w-auto text-sm px-6 shadow-lg ml-auto"
            :disabled="bulkPublishing"
            @click="publishDraftShowtimes"
          >
            {{ bulkPublishing ? 'Đang mở bán...' : `Mở bán ${draftShowtimes.length} suất nháp` }}
          </button>
        </div>
      </div>
      
      <!-- Date Scroller -->
      <div v-if="availableScheduleDates.length" class="flex gap-2 overflow-x-auto p-4 border-b border-white/5 bg-[#1e2020]">
        <button
          v-for="dateItem in availableScheduleDates"
          :key="dateItem.date"
          type="button"
          class="shrink-0 rounded-2xl border px-5 py-3 text-center transition-all flex flex-col items-center justify-center min-w-[80px]"
          :class="scheduleDate === dateItem.date ? 'border-primary bg-primary/20 text-white shadow-[0_0_15px_rgba(229,9,20,0.2)]' : 'border-white/5 bg-black/20 text-on-surface-variant hover:border-white/20 hover:bg-white/5'"
          @click="scheduleDate = dateItem.date"
        >
          <span class="text-xs font-bold uppercase mb-1 opacity-70">{{ new Date(`${dateItem.date}T12:00:00`).toLocaleDateString('vi-VN', { weekday: 'short' }) }}</span>
          <span class="text-xl font-black">{{ new Date(`${dateItem.date}T12:00:00`).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }) }}</span>
          <span class="mt-2 text-[10px] px-2 py-0.5 rounded-full bg-white/10 font-bold">{{ dateItem.count }} suất</span>
        </button>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-2 md:grid-cols-5 divide-x divide-white/5 border-b border-white/5 bg-black/20">
        <div class="p-4 flex flex-col items-center justify-center">
          <p class="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant mb-1">Tổng số suất chiếu</p>
          <strong class="text-2xl text-on-surface">{{ scheduleSummary.total }}</strong>
        </div>
        <div class="p-4 flex flex-col items-center justify-center">
          <p class="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant mb-1">Mở bán chính thức</p>
          <strong class="text-2xl text-emerald-400">{{ scheduleSummary.open }}</strong>
        </div>
        <div class="p-4 flex flex-col items-center justify-center">
          <p class="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant mb-1">Suất chưa mở (Nháp)</p>
          <strong class="text-2xl text-amber-400">{{ scheduleSummary.draft }}</strong>
        </div>
        <div class="p-4 flex flex-col items-center justify-center">
          <p class="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant mb-1">Tổng vé đã bán</p>
          <strong class="text-2xl text-sky-400">{{ scheduleSummary.sold }}</strong>
        </div>
        <div class="p-4 flex flex-col items-center justify-center">
          <p class="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant mb-1">Ước tính Doanh thu</p>
          <strong class="text-xl font-black text-primary">{{ fmtCurrency(scheduleSummary.revenue) }}</strong>
        </div>
      </div>

      <!-- Timeline View -->
      <div class="p-5 overflow-x-auto">
        <div v-if="scheduleRooms.length" class="flex gap-4" :style="{ minWidth: 'min-content' }">
          <div v-for="room in scheduleRooms" :key="`${room.branch}-${room.name}`" class="rounded-2xl border border-white/10 bg-[#161818] w-[280px] shrink-0 flex flex-col max-h-[600px] overflow-hidden shadow-lg relative">
            <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-white/5 via-white/20 to-white/5"></div>
            
            <div class="p-4 border-b border-white/5 bg-black/30 sticky top-0 z-10 backdrop-blur-md">
              <h4 class="font-black text-lg text-on-surface">{{ room.name }}</h4>
              <p class="text-xs text-on-surface-variant flex items-center gap-1 mt-0.5"><span class="material-symbols-outlined text-[14px]">location_on</span> {{ room.branch }}</p>
            </div>
            
            <div class="p-3 overflow-y-auto flex-1 space-y-3 custom-scrollbar">
              <article v-for="item in room.items" :key="item.id" class="rounded-xl border border-white/5 p-3.5 relative overflow-hidden group transition-colors hover:border-white/20" :class="
                item.status === 'OPEN' ? 'bg-emerald-900/10' : 
                item.status === 'CANCELLED' ? 'bg-rose-900/10' : 
                'bg-amber-900/10'
              ">
                <!-- Left Accent Border -->
                <div class="absolute left-0 top-0 bottom-0 w-1" :class="
                  item.status === 'OPEN' ? 'bg-emerald-500' : 
                  item.status === 'CANCELLED' ? 'bg-rose-500' : 
                  'bg-amber-500'
                "></div>
                
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center gap-1.5 font-bold font-mono text-sm" :class="
                    item.status === 'OPEN' ? 'text-emerald-400' : 
                    item.status === 'CANCELLED' ? 'text-rose-400' : 
                    'text-amber-400'
                  ">
                    <span>{{ new Date(item.starts_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }}</span>
                    <span class="text-white/30 text-[10px]">→</span>
                    <span class="text-white/70">{{ new Date(item.ends_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }}</span>
                  </div>
                  <span class="text-[9px] uppercase font-black px-1.5 py-0.5 rounded-sm" :class="
                    item.status === 'OPEN' ? 'bg-emerald-500/20 text-emerald-300' : 
                    item.status === 'CANCELLED' ? 'bg-rose-500/20 text-rose-300' : 
                    'bg-amber-500/20 text-amber-300'
                  ">{{ item.status }}</span>
                </div>
                
                <p class="text-sm font-bold text-on-surface line-clamp-2 leading-tight mb-2">{{ item.movie_title }}</p>
                
                <div class="flex items-center justify-between text-xs text-on-surface-variant font-medium bg-black/20 p-2 rounded-lg">
                  <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">confirmation_number</span> {{ item.sold_seats }} vé</span>
                  <span class="text-primary font-bold">{{ fmtCurrency(item.revenue) }}</span>
                </div>
                
                <!-- Action overlay on hover -->
                <div class="absolute inset-0 bg-black/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3 z-10">
                  <button class="w-10 h-10 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center hover:bg-sky-500 hover:text-white transition-colors border border-sky-500/30" title="Chỉnh sửa" @click="editShowtime(item)">
                    <span class="material-symbols-outlined">edit</span>
                  </button>
                  <button 
                    class="w-10 h-10 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center hover:bg-rose-500 hover:text-white transition-colors border border-rose-500/30 disabled:opacity-30 disabled:cursor-not-allowed" 
                    title="Huỷ/Xoá" 
                    :disabled="item.booking_count > 0"
                    @click="deleteShowtime(item)"
                  >
                    <span class="material-symbols-outlined">delete</span>
                  </button>
                </div>
              </article>
            </div>
          </div>
        </div>
        
        <div v-else class="py-16 text-center border-2 border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center">
          <span class="material-symbols-outlined text-[48px] text-white/20 mb-4">calendar_month</span>
          <p class="text-lg text-on-surface-variant font-medium">Không tìm thấy suất chiếu phù hợp.</p>
          <p class="text-sm text-white/40 mt-1">Hãy thay đổi bộ lọc ngày, chi nhánh hoặc tạo suất mới.</p>
        </div>
      </div>

      <!-- Detailed List -->
      <div class="border-t border-white/10">
        <details class="group">
          <summary class="p-4 font-bold text-on-surface bg-black/20 cursor-pointer flex items-center justify-between hover:bg-white/5 transition select-none">
            <span class="flex items-center gap-2">
              <span class="material-symbols-outlined group-open:rotate-180 transition-transform">expand_more</span>
              Hiển thị dạng bảng chi tiết ({{ filteredScheduleShowtimes.length }} suất)
            </span>
          </summary>
          <div class="overflow-x-auto bg-[#1a1c1c]">
            <table class="w-full text-sm min-w-[1000px]">
              <thead class="bg-black/40 border-b border-white/10 text-on-surface-variant">
                <tr>
                  <th class="px-5 py-4 text-left font-semibold">Bộ phim</th>
                  <th class="px-5 py-4 text-left font-semibold">Phòng chiếu</th>
                  <th class="px-5 py-4 text-left font-semibold">Khung giờ</th>
                  <th class="px-5 py-4 text-right font-semibold">Giá vé (VNĐ)</th>
                  <th class="px-5 py-4 text-center font-semibold">Đã bán</th>
                  <th class="px-5 py-4 text-right font-semibold">Doanh thu</th>
                  <th class="px-5 py-4 text-center font-semibold">Trạng thái</th>
                  <th class="px-5 py-4 text-center font-semibold w-[120px]">Tuỳ chọn</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/5">
                <tr v-for="st in filteredScheduleShowtimes" :key="st.id" class="hover:bg-white/5 transition-colors">
                  <td class="px-5 py-3 font-bold text-on-surface">{{ st.movie_title }}</td>
                  <td class="px-5 py-3">
                    <div class="text-on-surface font-semibold">{{ st.auditorium_name }}</div>
                    <div class="text-xs text-on-surface-variant">{{ st.branch_name }}</div>
                  </td>
                  <td class="px-5 py-3 text-on-surface-variant text-xs space-y-0.5">
                    <div class="flex gap-2">T: <strong class="text-on-surface">{{ fmtDateTime(st.starts_at) }}</strong></div>
                    <div class="flex gap-2 text-white/50">Đ: <span>{{ fmtDateTime(st.ends_at) }}</span></div>
                  </td>
                  <td class="px-5 py-3 text-right font-bold text-primary">{{ fmtCurrency(st.base_price) }}</td>
                  <td class="px-5 py-3 text-center">
                    <div class="bg-white/5 rounded px-2 py-1 inline-block">
                      <span class="font-bold text-sky-400">{{ st.sold_seats }}</span> <span class="text-xs text-on-surface-variant">ghế</span>
                      <span class="mx-1 text-white/20">|</span>
                      <span class="font-bold text-emerald-400">{{ st.booking_count }}</span> <span class="text-xs text-on-surface-variant">đơn</span>
                    </div>
                  </td>
                  <td class="px-5 py-3 text-right font-bold text-on-surface">{{ fmtCurrency(st.revenue) }}</td>
                  <td class="px-5 py-3 text-center">
                    <span class="inline-block px-2.5 py-1 text-[10px] font-black uppercase rounded" :class="showtimeStatusClass(st.status)">{{ st.status }}</span>
                  </td>
                  <td class="px-5 py-3 text-center">
                    <div class="flex items-center justify-center gap-2">
                      <button @click="editShowtime(st)" class="p-1.5 rounded bg-sky-500/10 text-sky-400 hover:bg-sky-500 hover:text-white transition" title="Sửa"><span class="material-symbols-outlined text-[16px]">edit</span></button>
                      <button
                        @click="deleteShowtime(st)"
                        class="p-1.5 rounded bg-rose-500/10 text-rose-400 hover:bg-rose-500 hover:text-white transition disabled:opacity-30 disabled:cursor-not-allowed"
                        :disabled="st.booking_count > 0"
                        title="Xoá"
                      ><span class="material-symbols-outlined text-[16px]">delete</span></button>
                    </div>
                  </td>
                </tr>
                <tr v-if="filteredScheduleShowtimes.length === 0">
                  <td colspan="8" class="px-5 py-12 text-center text-on-surface-variant font-medium">Không có dữ liệu cho bộ lọc hiện tại.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel {
  background: var(--card, #1a1c1c);
  border: 1px solid var(--line, rgba(255, 255, 255, 0.08));
  border-radius: 1rem;
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.24);
}

.field-input {
  background: rgba(30, 32, 32, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.75rem;
  padding: 0.6rem 0.75rem;
  font-size: 0.875rem;
  color: #f5f5f5;
  transition: all 0.2s ease;
  width: 100%;
}

.field-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.action-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px -16px rgba(229, 9, 20, 0.95);
}

.animate-fade-in {
  animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.2);
}
</style>

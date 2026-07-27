<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  adminBackendService,
  adminService,
  movieService,
  type AdminAuditorium,
  type AdminShowtime,
  type Movie,
  type MovieRequest
} from '~/services/api'

definePageMeta({
  layout: 'admin',
  middleware: ['auth']
})

type BranchTab = 'kpis' | 'showtimes' | 'seats' | 'fnb' | 'pos' | 'vouchers' | 'transactions' | 'profile'
type BranchTabItem = {
  key: BranchTab
  label: string
  icon: string
  description: string
}

const tabItems: BranchTabItem[] = [
  { key: 'kpis', label: 'Chi nhánh & Sales', icon: 'storefront', description: 'Doanh thu và lượng vé hôm nay' },
  { key: 'showtimes', label: 'Suất chiếu & Phim', icon: 'schedule', description: 'Lập lịch chiếu theo phòng/giờ' },
  { key: 'seats', label: 'Sơ đồ ghế ngồi', icon: 'event_seat', description: 'Editor thiết lập trạng thái ghế' },
  { key: 'fnb', label: 'Bắp nước & Kho', icon: 'restaurant_menu', description: 'CRUD Combo và kiểm kê tồn kho' },
  { key: 'pos', label: 'POS & Soát vé', icon: 'point_of_sale', description: 'Bán vé nhanh & Quét QR soát vé' },
  { key: 'vouchers', label: 'Mã ưu đãi rạp', icon: 'local_offer', description: 'Tạo mã ưu đãi riêng chi nhánh' },
  { key: 'transactions', label: 'Lịch sử giao dịch', icon: 'receipt_long', description: 'Bảng theo dõi giao dịch real-time' },
  { key: 'profile', label: 'Tài khoản cá nhân', icon: 'person', description: 'Chỉnh sửa hồ sơ và đổi mật khẩu' },
]

const activeTab = ref<BranchTab>('kpis')
const branchId = ref('')
const branchName = ref('CineAI Cầu Giấy')
const ticketsSold = ref(150)
const activeShowtimes = ref(12)
const activePromos = ref(4)
const branchRevenue = ref(13500000)

// Data arrays
const showtimesList = ref<AdminShowtime[]>([])
const promotionsList = ref<{ code: string; discount: number; desc: string; active: boolean }[]>([])
const myMovieRequests = ref<MovieRequest[]>([])
const movies = ref<Movie[]>([])
const auditoriums = ref<AdminAuditorium[]>([])

// Chart trigger
const chartMounted = ref(false)

// Modals / forms states
const showAddShowtimeModal = ref(false)
const selectMovieId = ref('')
const selectAuditoriumId = ref('')
const inputDate = ref('2026-07-28')
const inputTime = ref('20:00')
const inputPrice = ref(90000)

// Room/Seat Editor state
const selectedAuditoriumId = ref('')
const rows = ['A', 'B', 'C', 'D', 'E', 'F']
const cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
const seatMap = ref<Record<string, { type: 'standard' | 'vip' | 'couple'; status: 'available' | 'maintenance' }>>({})

// F&B combos inventory
const fnbCombos = ref([
  { id: 1, name: 'Combo Single (1 Bắp + 1 Nước)', price: 85000, stock: 120, unit: 'Bộ' },
  { id: 2, name: 'Combo Double (1 Bắp + 2 Nước)', price: 115000, stock: 85, unit: 'Bộ' },
  { id: 3, name: 'Combo Party Family (2 Bắp + 4 Nước)', price: 210000, stock: 40, unit: 'Bộ' },
  { id: 4, name: 'Bắp rang vị Phô mai', price: 55000, stock: 350, unit: 'Hộp' },
])
const editingComboId = ref<number | null>(null)
const editingComboStock = ref(0)

// POS / Selling tickets states
const posMovieId = ref('')
const posShowtimeId = ref('')
const selectedSeats = ref<string[]>([])
const posDiscountCode = ref('')
const posSuccess = ref(false)

// QR Scanner Simulator
const qrCodeInput = ref('')
const scanResult = ref<{ success: boolean; msg: string } | null>(null)

// Promo code form
const newPromoCode = ref('')
const newPromoDiscount = ref(15)
const newPromoDesc = ref('Ưu đãi CineAI Cầu Giấy')

// Transactions
const transactionHistory = ref([
  { id: 'TX-8921', time: '18:42:15', movieTitle: 'CineAI Chronicles: Resurrection', seats: ['E5', 'E6'], totalAmount: 190000, status: 'SUCCESS' },
  { id: 'TX-8920', time: '18:39:10', movieTitle: 'The Code Paradox', seats: ['C2'], totalAmount: 95000, status: 'SUCCESS' },
  { id: 'TX-8919', time: '18:25:02', movieTitle: 'Cyber Space Odyssey', seats: ['G10', 'G11'], totalAmount: 250000, status: 'SUCCESS' },
])

// Profile changing
const branchAdminProfile = ref({
  name: 'Nguyễn Văn Quyết',
  email: 'branchadmin@cineai.vn',
  branch: 'CineAI Cầu Giấy',
  phone: '0987654321',
  password: '',
  confirmPassword: ''
})

onMounted(async () => {
  try {
    const stats = await adminService.getBranchAdminStats()
    branchId.value = stats.branchId
    branchName.value = stats.branchName
    ticketsSold.value = stats.ticketsSold
    activeShowtimes.value = stats.activeShowtimes
    activePromos.value = stats.activePromos
    branchRevenue.value = stats.branchRevenue
    showtimesList.value = stats.showtimesList
    promotionsList.value = stats.promotionsList

    movies.value = await movieService.getAll()
    auditoriums.value = await adminBackendService.getAuditoriums(stats.branchId)
    myMovieRequests.value = await adminBackendService.getMyMovieRequests()

    if (auditoriums.value.length > 0) {
      selectedAuditoriumId.value = auditoriums.value[0].id
      initSeatMap()
    }
    if (movies.value.length > 0) {
      selectMovieId.value = movies.value[0].id
      posMovieId.value = movies.value[0].id
    }
    if (auditoriums.value.length > 0) {
      selectAuditoriumId.value = auditoriums.value[0].id
    }
  } catch (e) {
    console.error('Failed to load branch admin details:', e)
  }

  setTimeout(() => {
    chartMounted.value = true
  }, 150)
})

function initSeatMap() {
  seatMap.value = {}
  for (const r of rows) {
    for (const c of cols) {
      const id = `${r}${c}`
      let type: 'standard' | 'vip' | 'couple' = 'standard'
      if (r === 'D' || r === 'E') type = 'vip'
      if (r === 'F') type = 'couple'
      seatMap.value[id] = { type, status: 'available' }
    }
  }
}

function toggleSeatStatus(seatId: string) {
  const seat = seatMap.value[seatId]
  if (!seat) return
  if (seat.status === 'available') {
    seat.status = 'maintenance'
  } else {
    seat.status = 'available'
  }
}

function changeSeatType(seatId: string, type: 'standard' | 'vip' | 'couple') {
  if (seatMap.value[seatId]) {
    seatMap.value[seatId].type = type
  }
}

async function handleDeleteShowtime(id: string) {
  await adminBackendService.deleteShowtime(id)
  await refreshBranchData()
}

async function handleAddShowtimeSubmit() {
  const selectedMovie = movies.value.find(m => m.id === selectMovieId.value)
  const startsAt = new Date(`${inputDate.value}T${inputTime.value}:00`)
  const endsAt = new Date(startsAt)
  endsAt.setMinutes(endsAt.getMinutes() + (selectedMovie?.duration || 120) + 15)

  await adminBackendService.createShowtime({
    movie_id: selectMovieId.value,
    auditorium_id: selectAuditoriumId.value,
    starts_at: startsAt.toISOString(),
    ends_at: endsAt.toISOString(),
    base_price: inputPrice.value,
    status: 'OPEN',
  })

  showAddShowtimeModal.value = false
  await refreshBranchData()
}

function handleAddVoucher() {
  if (!newPromoCode.value) return
  promotionsList.value.push({
    code: newPromoCode.value.toUpperCase(),
    discount: newPromoDiscount.value,
    desc: newPromoDesc.value,
    active: true
  })
  newPromoCode.value = ''
  newPromoDiscount.value = 15
}

function startEditFnb(combo: any) {
  editingComboId.value = combo.id
  editingComboStock.value = combo.stock
}

function saveFnbStock(combo: any) {
  combo.stock = editingComboStock.value
  editingComboId.value = null
}

// POS flow simulator
function togglePosSeat(seatId: string) {
  if (selectedSeats.value.includes(seatId)) {
    selectedSeats.value = selectedSeats.value.filter(s => s !== seatId)
  } else {
    selectedSeats.value.push(seatId)
  }
}
const posSelectedMovieObj = computed(() => movies.value.find(m => m.id === posMovieId.value))
const posTotalAmount = computed(() => {
  let base = posSelectedMovieObj.value ? 90000 : 75000
  let amt = selectedSeats.value.length * base
  if (posDiscountCode.value) {
    amt = Math.round(amt * 0.85) // 15% discount mock
  }
  return amt
})

function submitPOSOrder() {
  if (selectedSeats.value.length === 0) return
  posSuccess.value = true
  transactionHistory.value.unshift({
    id: 'TX-' + Math.floor(1000 + Math.random() * 9000),
    time: new Date().toTimeString().split(' ')[0],
    movieTitle: posSelectedMovieObj.value?.title || 'CineAI Movie',
    seats: [...selectedSeats.value],
    totalAmount: posTotalAmount.value,
    status: 'SUCCESS'
  })
  ticketsSold.value += selectedSeats.value.length
  branchRevenue.value += posTotalAmount.value
  setTimeout(() => {
    posSuccess.value = false
    selectedSeats.value = []
    posDiscountCode.value = ''
  }, 3000)
}

// QR Check-in scanner simulation
function simulateQRScan() {
  if (!qrCodeInput.value) return
  if (qrCodeInput.value.startsWith('TICK-') || qrCodeInput.value.length >= 6) {
    scanResult.value = {
      success: true,
      msg: `Vé Hợp Lệ! Phòng Chiếu: Phòng số 2 IMAX - Ghế ${['C10', 'D5', 'E12'][Math.floor(Math.random() * 3)]} - Giờ chiếu: 20:00. Chào mừng quý khách!`
    }
  } else {
    scanResult.value = {
      success: false,
      msg: 'Mã vé không hợp lệ hoặc đã qua sử dụng. Vui lòng quét kiểm tra lại.'
    }
  }
  qrCodeInput.value = ''
}

async function refreshBranchData() {
  const stats = await adminService.getBranchAdminStats()
  branchId.value = stats.branchId
  branchName.value = stats.branchName
  ticketsSold.value = stats.ticketsSold
  activeShowtimes.value = stats.activeShowtimes
  activePromos.value = stats.activePromos
  branchRevenue.value = stats.branchRevenue
  showtimesList.value = stats.showtimesList
  promotionsList.value = stats.promotionsList
  auditoriums.value = await adminBackendService.getAuditoriums(stats.branchId)
}

function updatePassword() {
  if (branchAdminProfile.value.password !== branchAdminProfile.value.confirmPassword) {
    alert('Mật khẩu nhập lại không khớp!')
    return
  }
  alert('Đổi mật khẩu thành công!')
}
</script>

<template>
  <div class="branch-dashboard-root min-h-screen text-on-surface p-4 md:p-6 space-y-6">
    
    <!-- Branch Hero Widget -->
    <div class="glass-panel rounded-3xl border border-glass-stroke p-6 md:p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative overflow-hidden shadow-2xl">
      <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-purple-500/10 blur-[120px] pointer-events-none"></div>
      <div>
        <span class="text-[10px] tracking-widest text-purple-400 font-black uppercase bg-purple-500/15 border border-purple-500/30 px-3 py-1 rounded-full">BRANCH CONSOLE</span>
        <h1 class="text-2xl md:text-3xl font-black mt-3 text-white tracking-tight flex items-center gap-2">
          {{ branchName }} Operations
        </h1>
        <p class="text-xs text-on-surface-variant mt-2 max-w-xl">
          Bảng điều phối chi nhánh: Quản lý phòng chiếu, editor sơ đồ ghế ngồi, combo bắp nước, giao dịch POS và quét soát vé QR rạp.
        </p>
      </div>
      <button @click="refreshBranchData" class="px-5 py-3 rounded-2xl bg-white/5 border border-glass-stroke text-xs font-bold hover:bg-white/10 active:scale-95 transition-all flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">sync</span> Đồng bộ dữ liệu rạp
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
          ? 'bg-gradient-to-tr from-purple-600 to-ai-accent text-white shadow-lg'
          : 'bg-white/5 border border-transparent text-on-surface-variant hover:text-white hover:bg-white/10'"
      >
        <span class="material-symbols-outlined text-base">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Contents with animation -->
    <Transition name="fade-slide" mode="out-in">
      <!-- Tab 1: KPIs & Sales -->
      <div v-if="activeTab === 'kpis'" class="space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between">
            <div>
              <span class="text-xs text-on-surface-variant font-bold uppercase tracking-wider block">Doanh thu chi nhánh</span>
              <span class="text-2xl font-black text-purple-400 mt-1 block">{{ branchRevenue.toLocaleString() }}đ</span>
            </div>
            <div class="w-12 h-12 bg-purple-500/10 border border-purple-500/20 rounded-xl flex items-center justify-center text-purple-400">
              <span class="material-symbols-outlined text-2xl">payments</span>
            </div>
          </div>

          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between">
            <div>
              <span class="text-xs text-on-surface-variant font-bold uppercase tracking-wider block">Số vé bán ra (Hôm nay)</span>
              <span class="text-2xl font-black text-white mt-1 block">{{ ticketsSold }} vé</span>
            </div>
            <div class="w-12 h-12 bg-white/5 border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant">
              <span class="material-symbols-outlined text-2xl">confirmation_number</span>
            </div>
          </div>

          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between">
            <div>
              <span class="text-xs text-on-surface-variant font-bold uppercase tracking-wider block">Suất chiếu đang mở</span>
              <span class="text-2xl font-black text-white mt-1 block">{{ activeShowtimes }} suất</span>
            </div>
            <div class="w-12 h-12 bg-white/5 border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant">
              <span class="material-symbols-outlined text-2xl">calendar_today</span>
            </div>
          </div>

          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between">
            <div>
              <span class="text-xs text-on-surface-variant font-bold uppercase tracking-wider block">Mã giảm giá hoạt động</span>
              <span class="text-2xl font-black text-primary-fixed-dim mt-1 block">{{ activePromos }} voucher</span>
            </div>
            <div class="w-12 h-12 bg-primary-container/10 border border-primary-container/20 rounded-xl flex items-center justify-center text-primary-fixed-dim">
              <span class="material-symbols-outlined text-2xl">local_activity</span>
            </div>
          </div>
        </div>

        <!-- Custom Animated Hourly Ticket Sales SVG Chart -->
        <div class="glass-panel border border-glass-stroke p-6 rounded-2xl shadow-xl space-y-6">
          <h3 class="font-bold text-sm text-white uppercase tracking-wider flex items-center gap-2">
            <span class="material-symbols-outlined text-purple-400">query_stats</span>
            Lượng Vé Bán Ra Theo Khung Giờ Hoạt Động (Hôm nay)
          </h3>
          <div class="h-64 flex items-end gap-3 md:gap-6 justify-center pt-8 border-b border-glass-stroke">
            <div
              v-for="(tickets, hourIdx) in [15, 30, 45, 60, 40, 75, 90, 110, 60, 30]"
              :key="hourIdx"
              class="flex flex-col items-center flex-1 max-w-[60px] group relative"
            >
              <span class="absolute -top-8 bg-black/90 border border-glass-stroke text-[9px] font-bold text-white px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                {{ tickets }} vé
              </span>
              <div
                class="w-full rounded-t-lg bg-gradient-to-t from-purple-800 to-purple-400 transition-all duration-1000 ease-out hover:brightness-110"
                :style="{ height: chartMounted ? `${(tickets / 120) * 160}px` : '0px' }"
              ></div>
              <span class="text-[9px] text-on-surface-variant font-bold mt-2 pb-1">{{ 8 + hourIdx * 2 }}h</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 2: Showtimes & Movies Management -->
      <div v-else-if="activeTab === 'showtimes'" class="space-y-6">
        <div class="flex justify-between items-center bg-white/[0.01] border-b border-glass-stroke pb-4">
          <h3 class="text-sm font-bold text-white uppercase tracking-wider">Danh Sách Lịch Suất Chiếu Chi Nhánh</h3>
          <button @click="showAddShowtimeModal = true" class="bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1 shadow-md">
            <span class="material-symbols-outlined text-sm">add</span> Thêm Suất Chiếu mới
          </button>
        </div>

        <div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-xl">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                  <th class="py-3.5 px-6">Tên Phim</th>
                  <th class="py-3.5 px-6">Phòng chiếu</th>
                  <th class="py-3.5 px-6 text-center">Bắt đầu lúc</th>
                  <th class="py-3.5 px-6 text-center">Kết thúc lúc</th>
                  <th class="py-3.5 px-6 text-center">Đơn giá</th>
                  <th class="py-3.5 px-6 text-right">Hành động</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-glass-stroke/40">
                <tr v-for="showtime in showtimesList" :key="showtime.id" class="hover:bg-white/5 transition-colors">
                  <td class="py-4 px-6 font-bold text-white">{{ showtime.movie_title }}</td>
                  <td class="py-4 px-6 font-mono text-purple-400 font-bold uppercase">{{ showtime.auditorium_name }}</td>
                  <td class="py-4 px-6 text-center text-on-surface-variant">{{ new Date(showtime.starts_at).toLocaleString('vi-VN') }}</td>
                  <td class="py-4 px-6 text-center text-on-surface-variant">{{ new Date(showtime.ends_at).toLocaleString('vi-VN') }}</td>
                  <td class="py-4 px-6 text-center font-mono text-white font-bold">{{ Number(showtime.base_price).toLocaleString() }}đ</td>
                  <td class="py-4 px-6 text-right">
                    <button @click="handleDeleteShowtime(showtime.id)" class="text-red-400 hover:text-red-300 font-bold">Gỡ lịch</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab 3: Auditorium Room & Seat Editor -->
      <div v-else-if="activeTab === 'seats'" class="space-y-6">
        <div class="glass-panel border border-glass-stroke p-6 rounded-2xl space-y-6">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">Editor Cấu Hình Trạng Thái Ghế Ngồi</h3>
              <p class="text-[11px] text-on-surface-variant mt-1">Chọn phòng chiếu, click vào từng ghế để đổi sang chế độ bảo trì hoặc chọn loại ghế chuẩn.</p>
            </div>
            <select v-model="selectedAuditoriumId" class="bg-surface-container border border-glass-stroke rounded-xl px-4 py-2 text-xs text-on-surface">
              <option v-for="a in auditoriums" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </div>

          <!-- Cinema screen representation -->
          <div class="space-y-12 py-8 flex flex-col items-center">
            <div class="w-2/3 flex flex-col items-center">
              <div class="w-full h-2.5 bg-gradient-to-b from-purple-500 to-transparent rounded-full shadow-2xl"></div>
              <span class="text-[10px] text-purple-400 font-bold tracking-widest uppercase mt-2">MÀN HÌNH CHẾ CHIẾU</span>
            </div>

            <!-- Seat grid map -->
            <div class="grid gap-2">
              <div v-for="r in rows" :key="r" class="flex items-center gap-2">
                <span class="w-6 text-xs text-on-surface-variant font-bold text-center mr-2">{{ r }}</span>
                <div v-for="c in cols" :key="c" class="relative group">
                  <!-- Seat trigger button -->
                  <button
                    @click="toggleSeatStatus(`${r}${c}`)"
                    class="w-8 h-8 rounded-lg border flex items-center justify-center transition-all duration-200"
                    :class="seatMap[`${r}${c}`]?.status === 'maintenance'
                      ? 'bg-red-950 border-red-500/50 text-red-400'
                      : seatMap[`${r}${c}`]?.type === 'vip'
                        ? 'bg-purple-950 border-purple-500/50 text-purple-300'
                        : seatMap[`${r}${c}`]?.type === 'couple'
                          ? 'bg-pink-950 border-pink-500/50 text-pink-300'
                          : 'bg-white/5 border-glass-stroke text-on-surface-variant hover:bg-white/10'"
                  >
                    <span class="material-symbols-outlined text-sm">
                      {{ seatMap[`${r}${c}`]?.status === 'maintenance' ? 'build' : 'chair' }}
                    </span>
                  </button>

                  <!-- Floating seat config tooltips on hover -->
                  <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-32 hidden group-hover:block bg-surface-container-high border border-glass-stroke rounded-xl p-1.5 z-30 shadow-2xl">
                    <p class="text-[9px] font-black text-center text-white mb-1">Ghế {{ r }}{{ c }}</p>
                    <div class="grid grid-cols-3 gap-1">
                      <button @click="changeSeatType(`${r}${c}`, 'standard')" class="text-[8px] bg-white/5 hover:bg-white/10 py-1 rounded text-white font-bold">Thường</button>
                      <button @click="changeSeatType(`${r}${c}`, 'vip')" class="text-[8px] bg-purple-900 hover:bg-purple-800 py-1 rounded text-white font-bold">VIP</button>
                      <button @click="changeSeatType(`${r}${c}`, 'couple')" class="text-[8px] bg-pink-900 hover:bg-pink-800 py-1 rounded text-white font-bold">Couple</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Seat status legends -->
            <div class="flex flex-wrap justify-center gap-6 text-[10px] font-bold">
              <span class="flex items-center gap-2"><span class="w-3.5 h-3.5 rounded bg-white/5 border border-glass-stroke"></span> Ghế thường</span>
              <span class="flex items-center gap-2"><span class="w-3.5 h-3.5 rounded bg-purple-950 border border-purple-500/50"></span> Ghế VIP</span>
              <span class="flex items-center gap-2"><span class="w-3.5 h-3.5 rounded bg-pink-950 border border-pink-500/50"></span> Ghế Couple</span>
              <span class="flex items-center gap-2"><span class="w-3.5 h-3.5 rounded bg-red-950 border border-red-500/50 flex items-center justify-center text-red-400"><span class="material-symbols-outlined text-[10px]">build</span></span> Bảo trì / Ghế hỏng</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 4: F&B Combos & Inventory Inventory Control -->
      <div v-else-if="activeTab === 'fnb'" class="space-y-6">
        <div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-xl">
          <div class="p-6 border-b border-glass-stroke bg-white/[0.02] flex justify-between items-center">
            <div>
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">Danh Sách Combo Bắp Nước & Tồn Kho Chi Nhánh</h3>
              <p class="text-[11px] text-on-surface-variant mt-1">Cập nhật đơn giá bán lẻ và kiểm kê định kỳ tồn kho bắp nước tại quầy rạp.</p>
            </div>
            <button @click="fnbCombos.push({ id: Date.now(), name: 'Combo Đơn (Bắp ngọt + 1 Pepsi)', price: 75000, stock: 100, unit: 'Bộ' })" class="bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1">
              <span class="material-symbols-outlined text-sm">add</span> Thêm mặt hàng
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                  <th class="py-3.5 px-6">Tên mặt hàng/Combo</th>
                  <th class="py-3.5 px-6">Giá bán niêm yết</th>
                  <th class="py-3.5 px-6 text-center">Đơn vị</th>
                  <th class="py-3.5 px-6 text-center">Số lượng tồn kho</th>
                  <th class="py-3.5 px-6 text-right">Hành động</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-glass-stroke/40">
                <tr v-for="item in fnbCombos" :key="item.id" class="hover:bg-white/5 transition-colors">
                  <td class="py-4 px-6 font-bold text-white">{{ item.name }}</td>
                  <td class="py-4 px-6 font-mono font-bold">{{ item.price.toLocaleString() }}đ</td>
                  <td class="py-4 px-6 text-center text-on-surface-variant">{{ item.unit }}</td>
                  <td class="py-4 px-6 text-center">
                    <div v-if="editingComboId === item.id" class="flex items-center justify-center gap-2">
                      <input v-model.number="editingComboStock" type="number" class="w-16 bg-white/5 border border-glass-stroke rounded text-center text-xs py-1" />
                      <button @click="saveFnbStock(item)" class="text-green-400 hover:underline">Lưu</button>
                    </div>
                    <span v-else class="px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-white/5 border border-glass-stroke">{{ item.stock }}</span>
                  </td>
                  <td class="py-4 px-6 text-right">
                    <button v-if="editingComboId !== item.id" @click="startEditFnb(item)" class="text-purple-400 hover:underline font-bold mr-3">Nhập kho</button>
                    <button @click="fnbCombos = fnbCombos.filter(c => c.id !== item.id)" class="text-red-400 hover:underline font-bold">Xóa</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab 5: POS Counter & QR Scanning Simulator -->
      <div v-else-if="activeTab === 'pos'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          <!-- POS selling window -->
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl shadow-xl space-y-4">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span class="material-symbols-outlined text-purple-400">shopping_cart</span>
              Màn Hình Bán Vé Nhanh Tại Quầy (POS Terminal)
            </h3>

            <div class="space-y-3 pt-2">
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Chọn phim mở bán</label>
                <select v-model="posMovieId" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface">
                  <option v-for="m in movies" :key="m.id" :value="m.id">{{ m.title }}</option>
                </select>
              </div>

              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Chọn ghế (Click các ghế bên dưới)</label>
                <div class="flex flex-wrap gap-1.5 py-3 border border-glass-stroke/40 rounded-xl px-3 bg-white/[0.01]">
                  <button
                    v-for="seatNum in ['A1','A2','A3','B4','B5','C10','E5','E6','F1','F2']"
                    :key="seatNum"
                    @click="togglePosSeat(seatNum)"
                    class="px-2.5 py-1.5 rounded-lg border text-xs font-bold transition-all duration-150"
                    :class="selectedSeats.includes(seatNum)
                      ? 'bg-purple-600 border-purple-500 text-white'
                      : 'bg-white/5 border-glass-stroke text-on-surface-variant hover:bg-white/10'"
                  >
                    {{ seatNum }}
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Mã giảm giá áp dụng</label>
                  <input v-model="posDiscountCode" type="text" placeholder="Ví dụ: CINEAI15" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none" />
                </div>
                <div class="flex flex-col justify-end">
                  <span class="text-[10px] text-on-surface-variant uppercase font-black block mb-1">Tổng cộng đơn giá</span>
                  <span class="text-lg font-black text-purple-400 font-mono">{{ posTotalAmount.toLocaleString() }}đ</span>
                </div>
              </div>

              <button @click="submitPOSOrder" class="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-xl text-xs font-bold hover:scale-[1.01] active:scale-95 transition-all shadow-md">
                In Vé & Thanh Toán Tại Quầy
              </button>

              <p v-if="posSuccess" class="text-xs text-green-400 text-center font-bold animate-pulse">✓ Đặt vé thành công! Đang tự động in vé cứng cho khách...</p>
            </div>
          </div>

          <!-- QR ticket checking -->
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl shadow-xl space-y-4">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span class="material-symbols-outlined text-green-400 animate-pulse">qr_code_scanner</span>
              Module Quét Mã QR Soát Vé Vào Phòng Chiếu
            </h3>

            <div class="space-y-4 pt-2">
              <p class="text-xs text-on-surface-variant leading-snug">Nhập hoặc quét mã vé để xác thực trạng thái vào phòng chiếu của khách hàng.</p>
              
              <div class="flex gap-2">
                <input v-model="qrCodeInput" type="text" placeholder="Nhập mã vé (Ví dụ: TICK-9812 hoặc quét giả lập)" class="flex-1 bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" @keyup.enter="simulateQRScan" />
                <button @click="simulateQRScan" class="px-4 py-2.5 rounded-xl bg-green-600 hover:bg-green-700 text-white text-xs font-bold transition-all">Soát vé</button>
              </div>

              <!-- Scanner result screen -->
              <div v-if="scanResult" class="p-4 rounded-xl border" :class="scanResult.success ? 'bg-green-950/30 border-green-500/20 text-green-400' : 'bg-red-950/30 border-red-500/20 text-red-400'">
                <div class="flex items-center gap-2 mb-2">
                  <span class="material-symbols-outlined text-lg">{{ scanResult.success ? 'check_circle' : 'cancel' }}</span>
                  <span class="text-xs font-black uppercase tracking-wider">{{ scanResult.success ? 'THÀNH CÔNG' : 'TỪ CHỐI' }}</span>
                </div>
                <p class="text-[11px] leading-relaxed">{{ scanResult.msg }}</p>
              </div>

              <div class="rounded-xl border border-glass-stroke bg-white/[0.01] p-3 space-y-2">
                <span class="text-[10px] font-black text-on-surface-variant block uppercase tracking-wider">Mã vé giả lập demo soát nhanh</span>
                <div class="flex flex-wrap gap-2">
                  <button @click="qrCodeInput = 'TICK-9801'; simulateQRScan()" class="text-[9px] bg-white/5 border border-glass-stroke px-2 py-1 rounded text-purple-300 font-mono font-semibold">TICK-9801 (Đúng rạp)</button>
                  <button @click="qrCodeInput = 'INVALID'; simulateQRScan()" class="text-[9px] bg-white/5 border border-glass-stroke px-2 py-1 rounded text-red-400 font-mono font-semibold">INVALID (Sai rạp/Hết hạn)</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 6: Branch Promo Vouchers -->
      <div v-else-if="activeTab === 'vouchers'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="glass-panel border border-glass-stroke p-6 rounded-2xl space-y-4">
            <h3 class="text-base font-black text-white">Tạo mã ưu đãi Chi nhánh</h3>
            <form @submit.prevent="handleAddVoucher" class="space-y-3">
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Mã Voucher (Viết liền)</label>
                <input v-model="newPromoCode" type="text" placeholder="Ví dụ: CẦUGIẤY15" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none" required />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Phần trăm giảm (%)</label>
                <input v-model.number="newPromoDiscount" type="number" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none" required />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Mô tả chương trình ưu đãi</label>
                <input v-model="newPromoDesc" type="text" placeholder="Khuyến mãi mùa hè chi nhánh..." class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none" required />
              </div>
              <button type="submit" class="w-full bg-gradient-to-r from-purple-600 to-ai-accent text-white py-3 rounded-xl text-xs font-bold hover:scale-[1.02] active:scale-95 transition-all shadow-md">
                Mở chiến dịch ưu đãi
              </button>
            </form>
          </div>

          <div class="glass-panel border border-glass-stroke rounded-2xl lg:col-span-2 overflow-hidden shadow-lg">
            <div class="p-6 border-b border-glass-stroke bg-white/[0.02]">
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">Ưu đãi đang chạy tại rạp</h3>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs border-collapse">
                <thead>
                  <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                    <th class="py-3.5 px-6">Mã ưu đãi</th>
                    <th class="py-3.5 px-6 text-center">Tỷ lệ giảm</th>
                    <th class="py-3.5 px-6">Mô tả chương trình</th>
                    <th class="py-3.5 px-6 text-center">Trạng thái</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-glass-stroke/40">
                  <tr v-for="promo in promotionsList" :key="promo.code" class="hover:bg-white/5 transition-colors">
                    <td class="py-4 px-6 font-mono font-bold text-purple-400">{{ promo.code }}</td>
                    <td class="py-4 px-6 text-center text-white font-bold font-mono">{{ promo.discount }}%</td>
                    <td class="py-4 px-6 text-on-surface-variant">{{ promo.desc }}</td>
                    <td class="py-4 px-6 text-center">
                      <span class="px-2 py-0.5 rounded-full text-[10px] font-bold" :class="promo.active ? 'bg-green-950 text-green-400 border border-green-500/20' : 'bg-neutral-800 text-neutral-400'">
                        {{ promo.active ? 'Đang chạy' : 'Hết hạn' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 7: Real-time Ticket Orders & Transactions -->
      <div v-else-if="activeTab === 'transactions'" class="space-y-6">
        <div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-xl">
          <div class="p-6 border-b border-glass-stroke bg-white/[0.02]">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider">Lịch Sử Giao Dịch Vé Rạp (Real-time)</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold">
                  <th class="py-3.5 px-6">Mã hoá đơn</th>
                  <th class="py-3.5 px-6">Thời gian</th>
                  <th class="py-3.5 px-6">Tên phim</th>
                  <th class="py-3.5 px-6 text-center">Ghế đặt</th>
                  <th class="py-3.5 px-6">Tổng tiền thanh toán</th>
                  <th class="py-3.5 px-6 text-right">Trạng thái</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-glass-stroke/40">
                <tr v-for="tx in transactionHistory" :key="tx.id" class="hover:bg-white/5 transition-colors">
                  <td class="py-4 px-6 font-mono font-bold text-purple-400">{{ tx.id }}</td>
                  <td class="py-4 px-6 text-on-surface-variant font-mono">{{ tx.time }}</td>
                  <td class="py-4 px-6 font-bold text-white">{{ tx.movieTitle }}</td>
                  <td class="py-4 px-6 text-center font-mono font-semibold">{{ tx.seats.join(', ') }}</td>
                  <td class="py-4 px-6 font-mono font-bold text-green-400">{{ tx.totalAmount.toLocaleString() }}đ</td>
                  <td class="py-4 px-6 text-right">
                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-950 text-green-400 border border-green-500/20">Thành công</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab 8: Personal Account Change Password -->
      <div v-else-if="activeTab === 'profile'" class="space-y-6">
        <div class="glass-panel border border-glass-stroke p-6 rounded-2xl max-w-xl mx-auto space-y-6">
          <div class="flex items-center gap-4 border-b border-glass-stroke pb-6">
            <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-purple-600 to-ai-accent flex items-center justify-center font-black text-white text-xl">
              {{ branchAdminProfile.name.substring(0, 2).toUpperCase() }}
            </div>
            <div>
              <h3 class="text-base font-black text-white">{{ branchAdminProfile.name }}</h3>
              <p class="text-xs text-on-surface-variant font-mono mt-1">Vai trò: Branch Admin</p>
              <p class="text-[10px] text-on-surface-variant mt-0.5">Chi nhánh: {{ branchAdminProfile.branch }}</p>
            </div>
          </div>

          <form @submit.prevent="updatePassword" class="space-y-4">
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Email đăng nhập</label>
              <input v-model="branchAdminProfile.email" type="email" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" disabled />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Số điện thoại liên hệ</label>
              <input v-model="branchAdminProfile.phone" type="text" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" required />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Đổi mật khẩu mới</label>
              <input v-model="branchAdminProfile.password" type="password" placeholder="••••••••" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" required />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Xác nhận mật khẩu</label>
              <input v-model="branchAdminProfile.confirmPassword" type="password" placeholder="••••••••" class="w-full bg-white/5 border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" required />
            </div>
            <button type="submit" class="w-full bg-gradient-to-r from-purple-600 to-ai-accent text-white py-3 rounded-xl text-xs font-bold hover:scale-[1.02] active:scale-95 transition-all shadow-md">
              Cập nhật hồ sơ & mật khẩu
            </button>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Add Showtime Modal -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showAddShowtimeModal" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-md rounded-3xl border border-glass-stroke p-6 relative">
          <button @click="showAddShowtimeModal = false" class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface">
            <span class="material-symbols-outlined">close</span>
          </button>
          
          <h3 class="text-base font-black text-white mb-6">Thêm Suất Chiếu Mới Chi Nhánh</h3>
          
          <form @submit.prevent="handleAddShowtimeSubmit" class="space-y-4">
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Chọn phim chiếu</label>
              <select v-model="selectMovieId" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-purple-500">
                <option v-for="movie in movies" :key="movie.id" :value="movie.id">{{ movie.title }}</option>
              </select>
            </div>
            
            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Chọn phòng chiếu</label>
              <select v-model="selectAuditoriumId" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-purple-500">
                <option v-for="auditorium in auditoriums" :key="auditorium.id" :value="auditorium.id">{{ auditorium.name }}</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Ngày chiếu</label>
                <input v-model="inputDate" type="date" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Giờ bắt đầu</label>
                <input v-model="inputTime" type="time" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
              </div>
            </div>

            <div>
              <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Giá vé cơ bản (VNĐ)</label>
              <input v-model.number="inputPrice" type="number" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" />
            </div>

            <button type="submit" class="w-full bg-purple-600 text-white py-3 rounded-xl text-xs font-bold hover:scale-[1.01] active:scale-95 transition-all shadow-md">
              Mở bán suất chiếu mới
            </button>
          </form>
        </div>
      </div>
    </transition>

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

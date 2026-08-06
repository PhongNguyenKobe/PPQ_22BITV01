<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/store/user'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

type AdminTab = 'overview' | 'users' | 'movies' | 'promotions' | 'combos' | 'branches' | 'schedule-monitor' | 'auditoriums' | 'seats' | 'showtimes' | 'bookings' | 'payments' | 'ticket-scanner' | 'reports'
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
  { key: 'schedule-monitor', label: 'Giám sát lịch chiếu', icon: 'calendar_view_week', description: 'Xem phim và suất chiếu theo từng chi nhánh' },
  { key: 'promotions', label: 'Khuyến mãi', icon: 'sell', description: 'Mã giảm giá và giới hạn sử dụng' },
  { key: 'combos', label: 'Combo bắp nước', icon: 'fastfood', description: 'Tạo và quản lý combo của chi nhánh' },
  { key: 'auditoriums', label: 'Phòng chiếu', icon: 'theaters', description: 'Màn hình và sức chứa' },
  { key: 'seats', label: 'Ghế ngồi', icon: 'event_seat', description: 'Sơ đồ ghế theo phòng' },
  { key: 'showtimes', label: 'Suất chiếu', icon: 'schedule', description: 'Lịch chiếu đang mở bán' },
  { key: 'bookings', label: 'Đơn đặt vé', icon: 'confirmation_number', description: 'Tra cứu và xử lý đơn vé' },
  { key: 'payments', label: 'Thanh toán', icon: 'payments', description: 'Giao dịch và hoàn tiền' },
  { key: 'ticket-scanner', label: 'Soát vé QR', icon: 'qr_code_scanner', description: 'Kiểm tra và xác nhận vé vào rạp' },
  { key: 'reports', label: 'Báo cáo', icon: 'analytics', description: 'Doanh thu và hiệu suất vận hành' },
]

const userStore = useUserStore()
const route = useRoute()
const { currentUser } = storeToRefs(userStore)
const isBranchAdmin = computed(() => currentUser.value?.role === 'branch-admin')

const tabItems = computed(() =>
  allTabItems.filter((tab) =>
    isBranchAdmin.value
      ? ['auditoriums', 'seats', 'showtimes', 'combos', 'bookings', 'payments', 'ticket-scanner'].includes(tab.key)
      : ['overview', 'movies', 'users', 'branches', 'schedule-monitor', 'promotions', 'bookings', 'payments', 'reports'].includes(tab.key),
  ),
)

const requestedTab = String(route.query.tab || '')
const activeTab = ref<AdminTab>(
  currentUser.value?.role === 'branch-admin'
    ? (['auditoriums', 'seats', 'showtimes', 'combos', 'bookings', 'payments', 'ticket-scanner'].includes(requestedTab) ? requestedTab as AdminTab : 'auditoriums')
    : (['overview', 'movies', 'users', 'branches', 'schedule-monitor', 'promotions', 'bookings', 'payments', 'reports'].includes(requestedTab) ? requestedTab as AdminTab : 'overview'),
)

const tabRenderKeys = ref<Record<AdminTab, number>>({
  overview: 0,
  users: 0,
  movies: 0,
  promotions: 0,
  combos: 0,
  branches: 0,
  'schedule-monitor': 0,
  auditoriums: 0,
  seats: 0,
  showtimes: 0,
  bookings: 0,
  payments: 0,
  'ticket-scanner': 0,
  reports: 0,
})

watch(
  () => route.query.tab,
  (tab) => {
    const next = String(tab || '')
    if (tabItems.value.some((item) => item.key === next)) {
      activeTab.value = next as AdminTab
    }
  },
  { immediate: true },
)

function refreshActiveTab() {
  tabRenderKeys.value[activeTab.value] += 1
}
</script>
<template>
  <div class="admin-page space-y-5 px-6 py-6 lg:px-8">
    <section class="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-white/5 pb-4 gap-3">
      <div>
        <h1 class="text-xl font-black text-white flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
          {{ isBranchAdmin ? 'Vận Hành Chi Nhánh' : 'CineAI Super Admin' }}
        </h1>
        <p class="text-xs text-gray-400 mt-0.5">
          {{ isBranchAdmin
            ? 'Quản lý phòng chiếu, sơ đồ ghế và lịch chiếu được phân công.'
            : 'Hệ thống quản trị tổng quan, phim, tài khoản và chi nhánh.' }}
        </p>
      </div>
      <button @click="refreshActiveTab" class="action-ghost px-4 py-2 border border-white/10 rounded-xl hover:bg-white/5 text-xs font-bold text-gray-300 hover:text-white flex items-center gap-1.5 transition-all">
        <span class="material-symbols-outlined text-sm">sync</span>
        Làm mới dữ liệu
      </button>
    </section>

    <section v-if="activeTab === 'overview'" class="space-y-4">
      <AdminOverview :key="tabRenderKeys.overview" />
    </section>

    <section v-if="activeTab === 'promotions'" class="space-y-4">
      <AdminPromotions :key="tabRenderKeys.promotions" />
    </section>

    <section v-if="activeTab === 'movies'" class="space-y-4">
      <AdminMovies :key="tabRenderKeys.movies" />
    </section>

    <section v-if="activeTab === 'users'" class="space-y-4">
      <AdminUsers :key="tabRenderKeys.users" />
    </section>

    <section v-if="activeTab === 'branches'" class="space-y-4">
      <AdminBranches :key="tabRenderKeys.branches" />
    </section>

    <section v-if="activeTab === 'schedule-monitor'" class="space-y-4">
      <AdminScheduleMonitor :key="tabRenderKeys['schedule-monitor']" />
    </section>

    <section v-if="activeTab === 'auditoriums'" class="space-y-4">
      <AdminAuditoriums :key="tabRenderKeys.auditoriums" />
    </section>

    <section v-if="activeTab === 'seats'" class="space-y-4">
      <AdminSeats :key="tabRenderKeys.seats" />
    </section>

    <section v-if="activeTab === 'showtimes'" class="space-y-4">
      <AdminShowtimes :key="tabRenderKeys.showtimes" />
    </section>

    <section v-if="activeTab === 'bookings'" class="space-y-4">
      <AdminBookings :key="tabRenderKeys.bookings" />
    </section>

    <section v-if="activeTab === 'payments'" class="space-y-4">
      <AdminPayments :key="tabRenderKeys.payments" />
    </section>
    <section v-if="activeTab === 'combos'" class="space-y-4"><AdminCombos :key="tabRenderKeys.combos" /></section>

    <section v-if="activeTab === 'ticket-scanner'" class="space-y-4">
      <AdminTicketScanner :key="tabRenderKeys['ticket-scanner']" />
    </section>

    <section v-if="activeTab === 'reports'" class="space-y-4">
      <AdminReports :key="tabRenderKeys.reports" />
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

.metric-green {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.metric-blue {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.metric-violet {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.metric-amber {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.metric-pink {
  background: linear-gradient(135deg, #ec4899, #db2777);
}

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

.action-link-blue {
  color: #7dd3fc;
}

.action-link-amber {
  color: #fcd34d;
}

.action-link-rose {
  color: #fda4af;
}

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

.role-admin {
  background: rgba(229, 9, 20, 0.16);
  border-color: rgba(229, 9, 20, 0.28);
  color: #fecaca;
}

.role-branch-admin {
  background: rgba(139, 92, 246, 0.18);
  border-color: rgba(139, 92, 246, 0.28);
  color: #ddd6fe;
}

.role-staff {
  background: rgba(59, 130, 246, 0.18);
  border-color: rgba(59, 130, 246, 0.28);
  color: #bfdbfe;
}

.role-customer {
  background: rgba(34, 197, 94, 0.16);
  border-color: rgba(34, 197, 94, 0.26);
  color: #bbf7d0;
}

.status-open {
  background: rgba(34, 197, 94, 0.16);
  border-color: rgba(34, 197, 94, 0.26);
  color: #bbf7d0;
}

.status-closed {
  background: rgba(245, 158, 11, 0.16);
  border-color: rgba(245, 158, 11, 0.28);
  color: #fde68a;
}

.status-draft {
  background: rgba(59, 130, 246, 0.16);
  border-color: rgba(59, 130, 246, 0.28);
  color: #bfdbfe;
}

.status-cancelled {
  background: rgba(148, 163, 184, 0.16);
  border-color: rgba(148, 163, 184, 0.26);
  color: #cbd5e1;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 1.35rem;
  }
}
</style>

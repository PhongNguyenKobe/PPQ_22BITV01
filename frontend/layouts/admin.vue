<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/store/user'
import { adminBackendService, branchesService, type BackendBranch } from '~/services/api'

const userStore = useUserStore()
const { currentUser } = storeToRefs(userStore)
const route = useRoute()
const showBranchSelector = computed(() => ['overview', 'schedule-monitor', 'bookings', 'payments', 'reports'].includes(String(route.query.tab || 'overview')))

const isCollapsed = ref(false)
const showNotifications = ref(false)
const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const branchOptions = ref<BackendBranch[]>([])
const previewQuery = computed(() => {
  const branchId = currentUser.value?.role === 'branch-admin'
    ? currentUser.value.branchId
    : selectedBranch.value !== 'ALL' ? selectedBranch.value : undefined
  return {
    preview: 'admin',
    return_tab: String(route.query.tab || 'overview'),
    ...(branchId ? { branch_id: branchId } : {}),
  }
})
const dashboardPath = computed(() => currentUser.value?.role === 'branch-admin' ? '/branch-admin/dashboard' : '/admin/dashboard')

onMounted(async () => {
  try {
    branchOptions.value = await branchesService.getAll()
    if (currentUser.value?.role === 'admin') {
      const managedBranches = await adminBackendService.getBranchesManage()
      notifications.value = managedBranches
        .filter(branch => !branch.is_active || branch.auditoriums_count === 0)
        .map((branch, index) => ({
          id: index + 1,
          text: !branch.is_active
            ? `${branch.name} đang ngừng hoạt động`
            : `${branch.name} chưa được cấu hình phòng chiếu`,
          time: 'Cần kiểm tra',
          unread: true,
        }))
      notificationCount.value = notifications.value.length
    }
  } catch {
    branchOptions.value = []
  }
})

const notificationCount = ref(0)
const notifications = ref<Array<{ id: number; text: string; time: string; unread: boolean }>>([])

const adminMenu = [
  { tab: 'overview', label: 'Tổng quan', icon: 'dashboard' },
  { tab: 'movies', label: 'Phim', icon: 'movie' },
  { tab: 'users', label: 'Người dùng', icon: 'group' },
  { tab: 'branches', label: 'Chi nhánh', icon: 'location_city' },
  { tab: 'schedule-monitor', label: 'Giám sát lịch chiếu', icon: 'calendar_view_week' },
  { tab: 'promotions', label: 'Khuyến mãi', icon: 'sell' },
  { tab: 'bookings', label: 'Đơn đặt vé', icon: 'confirmation_number' },
  { tab: 'payments', label: 'Thanh toán', icon: 'payments' },
  { tab: 'reports', label: 'Báo cáo', icon: 'analytics' },
]
const branchMenu = [
  { tab: 'overview', label: 'Tổng quan chi nhánh', icon: 'dashboard' },
  { tab: 'auditoriums', label: 'Phòng chiếu', icon: 'theaters' },
  { tab: 'seats', label: 'Ghế ngồi', icon: 'event_seat' },
  { tab: 'showtimes', label: 'Suất chiếu', icon: 'schedule' },
  { tab: 'combos', label: 'Combo bắp nước', icon: 'fastfood' },
  { tab: 'bookings', label: 'Đơn đặt vé', icon: 'confirmation_number' },
  { tab: 'payments', label: 'Giao dịch & hoàn tiền', icon: 'payments' },
  { tab: 'ticket-scanner', label: 'Soát vé QR', icon: 'qr_code_scanner' },
]

function isCurrentTab(tab: string) {
  const fallback = 'overview'
  return String(route.query.tab || fallback) === tab
}

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}

function handleLogout() {
  userStore.logout()
  navigateTo('/login')
}

</script>

<template>
  <div class="admin-shell font-body-md">
    <!-- Sidebar Navigation -->
    <aside 
      class="admin-sidebar transition-all duration-300 ease-in-out"
      :class="isCollapsed ? 'w-20' : 'w-64'"
    >
      <div class="flex h-full min-h-0 flex-col">
        <div class="min-h-0 flex-1 overflow-y-auto">
          <!-- Sidebar Brand -->
          <div class="admin-sidebar-brand flex items-center justify-between" :class="isCollapsed ? 'px-4' : 'px-6'">
            <NuxtLink :to="dashboardPath" class="brand-link flex items-center gap-3">
              <span class="material-symbols-outlined text-primary-container text-3xl">local_activity</span>
              <span v-if="!isCollapsed" class="font-headline-md font-black tracking-wider text-on-surface text-lg">
                Cine<span class="text-primary-container">AI</span>
                <small class="text-[9px] text-on-surface-variant tracking-widest block font-bold">SYSTEM ADMIN</small>
              </span>
            </NuxtLink>
          </div>

          <!-- Navigation Links -->
          <nav class="admin-nav p-4 space-y-2">
            <div 
              v-if="!isCollapsed" 
              class="admin-nav-title text-xs font-black text-on-surface-variant tracking-wider uppercase px-3 py-2"
            >
              {{ currentUser?.role === 'admin' ? 'Quản trị hệ thống' : 'Quản lý chi nhánh' }}
            </div>

            <NuxtLink
              v-if="false"
              to="/admin/dashboard"
              class="nav-link flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
              active-class="nav-link-active"
            >
              <span class="material-symbols-outlined text-xl">dashboard</span>
              <span v-if="!isCollapsed" class="text-sm font-semibold">Bảng điều khiển</span>
            </NuxtLink>

            <NuxtLink
              v-if="false"
              to="/branch-admin/dashboard"
              class="nav-link flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
              active-class="nav-link-active"
            >
              <span class="material-symbols-outlined text-xl">storefront</span>
              <span v-if="!isCollapsed" class="text-sm font-semibold">Bảng chi nhánh</span>
            </NuxtLink>

            <NuxtLink
              v-for="item in (currentUser?.role === 'admin' ? adminMenu : branchMenu)"
              :key="item.tab"
              :to="{
                path: currentUser?.role === 'admin' ? '/admin/dashboard' : '/branch-admin/dashboard',
                query: { tab: item.tab },
              }"
              class="nav-link flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
              :class="{ 'nav-link-active': isCurrentTab(item.tab) }"
            >
              <span class="material-symbols-outlined text-xl">{{ item.icon }}</span>
              <span v-if="!isCollapsed" class="text-sm font-semibold">{{ item.label }}</span>
            </NuxtLink>

          </nav>
        </div>

        <!-- Sidebar User Section -->
        <div class="sidebar-user shrink-0 p-4 border-t border-glass-stroke bg-white/[0.02]">
          <div class="flex items-center gap-3" :class="isCollapsed ? 'justify-center' : 'mb-4'">
            <div class="avatar-circle w-10 h-10 rounded-full flex items-center justify-center font-bold text-white text-sm bg-gradient-to-tr from-primary-container to-ai-accent">
              {{ currentUser?.name.substring(0, 2).toUpperCase() }}
            </div>
            <div v-if="!isCollapsed" class="flex-1 min-w-0">
              <h5 class="text-xs font-bold truncate text-on-surface">{{ currentUser?.name }}</h5>
              <span class="text-[10px] px-2 py-0.5 rounded bg-white/10 text-on-surface-variant font-mono uppercase mt-1 inline-block">
                {{ currentUser?.role }}
              </span>
            </div>
          </div>
          <button
            @click="handleLogout"
            class="logout-btn w-full mt-2 border border-red-500/20 bg-red-950/20 hover:bg-red-950/40 text-red-400 py-2.5 rounded-xl text-xs font-black flex items-center justify-center gap-2 transition-all duration-200"
            title="Đăng xuất"
          >
            <span class="material-symbols-outlined text-sm">logout</span>
            <span v-if="!isCollapsed">Đăng xuất</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Dashboard Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Portal Top Header -->
      <header class="admin-header h-20 px-6 border-b border-glass-stroke bg-surface-container/60 backdrop-blur-md flex items-center justify-between z-40">
        <div class="flex items-center gap-4">
          <!-- Toggle Sidebar -->
          <button 
            @click="toggleSidebar" 
            class="w-10 h-10 rounded-xl hover:bg-white/5 flex items-center justify-center text-on-surface border border-glass-stroke transition-colors"
          >
            <span class="material-symbols-outlined">{{ isCollapsed ? 'menu_open' : 'menu' }}</span>
          </button>
          
          <div>
            <h2 class="text-base font-black text-on-surface flex items-center gap-2">
              {{ currentUser?.role === 'admin' ? 'Hệ thống Quản trị Tổng' : 'Hệ thống Quản trị Chi nhánh' }}
            </h2>
            <p class="text-xs text-on-surface-variant hidden sm:block">Theo dõi dữ liệu vận hành rạp theo thời gian thực</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Switch quick branch (if super admin) -->
          <div v-if="currentUser?.role === 'admin' && showBranchSelector" class="hidden md:flex items-center gap-2 bg-white/5 border border-glass-stroke rounded-xl px-3 py-1.5">
            <span class="material-symbols-outlined text-sm text-ai-accent">location_on</span>
            <select v-model="selectedBranch" class="bg-transparent border-0 text-xs font-bold text-on-surface p-0 focus:ring-0 cursor-pointer">
              <option value="ALL">Tất cả chi nhánh</option>
              <option v-for="branch in branchOptions" :key="branch.id" :value="branch.id">
                {{ branch.name }} ({{ branch.city }})
              </option>
            </select>
          </div>

          <div class="relative">
            <div class="px-3 py-1.5 rounded-xl bg-gradient-to-r from-ai-accent/20 to-primary-container/20 border border-glass-stroke text-xs font-black text-primary-fixed-dim flex items-center gap-1">
              <span class="material-symbols-outlined text-sm">settings_accessibility</span>
              {{ currentUser?.role === 'admin' ? 'Super Admin' : 'Branch Admin' }}
            </div>
          </div>

          <!-- Notification Dropdown -->
          <div class="relative">
            <button 
              @click="showNotifications = !showNotifications"
              class="w-10 h-10 rounded-xl hover:bg-white/5 flex items-center justify-center text-on-surface border border-glass-stroke relative transition-colors"
            >
              <span class="material-symbols-outlined text-xl">notifications</span>
              <span v-if="notificationCount > 0" class="absolute top-2 right-2 w-2.5 h-2.5 rounded-full bg-primary-container animate-ping"></span>
              <span v-if="notificationCount > 0" class="absolute top-2 right-2 w-2.5 h-2.5 rounded-full bg-primary-container"></span>
            </button>
            <div 
              v-if="showNotifications" 
              class="absolute right-0 mt-2 w-80 bg-surface-container-high border border-glass-stroke rounded-2xl shadow-2xl overflow-hidden z-50 animate-fade"
            >
              <div class="p-4 border-b border-glass-stroke flex justify-between items-center bg-white/[0.02]">
                <h4 class="text-xs font-bold text-on-surface uppercase tracking-wider">Thông báo ({{ notificationCount }})</h4>
                <button @click="notificationCount = 0" class="text-[10px] text-primary-container font-semibold hover:underline">Đánh dấu đã đọc</button>
              </div>
              <div class="max-h-64 overflow-y-auto divide-y divide-glass-stroke/50">
                <div 
                  v-for="item in notifications" 
                  :key="item.id" 
                  class="p-3 text-xs hover:bg-white/5 cursor-pointer"
                >
                  <p class="text-on-surface leading-snug">{{ item.text }}</p>
                  <span class="text-[10px] text-on-surface-variant block mt-1.5">{{ item.time }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Return to main ticket view -->
          <NuxtLink :to="{ path: '/products', query: previewQuery }" target="_blank" class="back-btn hidden lg:flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-glass-stroke bg-white/5 hover:bg-white/10 text-xs font-bold text-on-surface transition-all">
            <span class="material-symbols-outlined text-sm">open_in_new</span>
            Mở trang khách hàng
          </NuxtLink>
        </div>
      </header>

      <!-- Dashboard Pages Scroll -->
      <main class="admin-main flex-1 overflow-y-auto bg-surface relative">
        <slot />
      </main>
    </div>
  </div>
</template>

<style>
/* Page transition settings */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade {
  animation: fade-in 0.2s ease-out forwards;
}
</style>

<style scoped>
.admin-shell {
  display: flex;
  height: 100vh;
  background: #121414;
  color: #e2e2e2;
  overflow: hidden;
}

.admin-sidebar {
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  background: #171919;
  z-index: 50;
  flex-shrink: 0;
}

.admin-sidebar-brand {
  height: 5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-link {
  font-weight: 900;
}

.nav-link {
  color: #b3b3b3;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

.nav-link-active {
  color: #ffffff !important;
  background: linear-gradient(135deg, #e50914, #7701d0);
  box-shadow: 0 8px 20px -8px rgba(119, 1, 208, 0.6);
}
</style>



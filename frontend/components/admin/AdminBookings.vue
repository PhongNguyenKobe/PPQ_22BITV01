<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { adminBackendService, type AdminBooking } from '~/services/api'
import { useUserStore } from '~/store/user'

const userStore = useUserStore()
const isBranchAdmin = computed(() => userStore.currentUser?.role === 'branch-admin')
const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const rows = ref<AdminBooking[]>([])
const total = ref(0)
const loading = ref(false)
const status = ref('')
const startDate = ref('')
const endDate = ref('')
const error = ref('')
const currentPage = ref(1)
const pageSize = 15

const totalPages = computed(() => Math.ceil(total.value / pageSize))

const visiblePages = computed(() => {
  const range = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) {
    range.push(i)
  }
  return range
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const result = await adminBackendService.getBookings({
      status: status.value || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      branch_id: !isBranchAdmin.value && selectedBranch.value !== 'ALL' ? selectedBranch.value : undefined,
      limit: pageSize,
      skip: (currentPage.value - 1) * pageSize,
    })
    rows.value = result.bookings
    total.value = result.total
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải đơn đặt vé.'
  } finally {
    loading.value = false
  }
}

async function cancel(item: AdminBooking) {
  const reason = window.prompt('Nhập lý do hủy đơn:')
  if (!reason?.trim()) return
  try {
    loading.value = true
    await adminBackendService.cancelBooking(item.id, reason.trim())
    await load()
  } catch (e: any) {
    error.value = e?.message || 'Không thể hủy đơn.'
  } finally {
    loading.value = false
  }
}

function handleFilter() {
  currentPage.value = 1
  void load()
}

onMounted(load)
watch(currentPage, () => {
  void load()
})
watch(selectedBranch, () => {
  currentPage.value = 1
  if (!isBranchAdmin.value) void load()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-red-500 text-2xl">confirmation_number</span>
          <h2 class="text-xl font-black text-white tracking-tight">{{ isBranchAdmin ? 'Quản lý đơn đặt vé' : 'Giám sát đơn đặt vé' }}</h2>
        </div>
        <p class="text-sm text-gray-400 mt-1">
          {{ isBranchAdmin ? `Tra cứu và xử lý ${total} đơn thuộc chi nhánh được phân công.` : `Theo dõi ${total} đơn trên toàn hệ thống ở chế độ chỉ đọc.` }}
        </p>
      </div>
    </div>

    <!-- Filter Control Panel -->
    <div class="panel-glass grid gap-4 p-5 md:grid-cols-4 items-end shadow-md">
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Từ ngày</label>
        <input v-model="startDate" type="date" class="field-input w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-red-500">
      </div>
      
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Đến ngày</label>
        <input v-model="endDate" type="date" class="field-input w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-red-500">
      </div>

      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Trạng thái</label>
        <div class="relative">
          <select v-model="status" class="field-input w-full pl-4 pr-10 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-red-500 cursor-pointer appearance-none">
            <option value="">Tất cả trạng thái</option>
            <option value="PENDING">PENDING</option>
            <option value="CONFIRMED">CONFIRMED</option>
            <option value="CANCEL_REQUESTED">CANCEL_REQUESTED</option>
            <option value="CANCELLED">CANCELLED</option>
            <option value="EXPIRED">EXPIRED</option>
          </select>
          <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none text-sm">expand_more</span>
        </div>
      </div>

      <button class="action-btn-primary w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold text-sm rounded-xl transition-all shadow-md flex items-center justify-center gap-2" @click="handleFilter" :disabled="loading">
        <span class="material-symbols-outlined text-sm">filter_alt</span>
        Lọc dữ liệu
      </button>
    </div>

    <!-- Error/Loading -->
    <div v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-400 flex items-center gap-2">
      <span class="material-symbols-outlined text-xl">error</span>
      <span class="font-medium">{{ error }}</span>
    </div>

    <!-- Data Table -->
    <div class="panel-glass overflow-hidden shadow-lg">
      <div class="overflow-x-auto">
        <table class="w-full text-sm border-collapse text-left">
          <thead>
            <tr class="border-b border-white/10 bg-white/5 text-gray-300 font-bold">
              <th class="p-4 text-xs uppercase tracking-wider">Mã đơn</th>
              <th class="p-4 text-xs uppercase tracking-wider">Phim & Suất Chiếu</th>
              <th class="p-4 text-xs uppercase tracking-wider">Ghế</th>
              <th class="p-4 text-xs uppercase tracking-wider">Tổng tiền</th>
              <th class="p-4 text-xs uppercase tracking-wider">Trạng thái</th>
              <th class="p-4 text-xs uppercase tracking-wider text-right">Hành động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in rows" :key="item.id" class="border-b border-white/5 hover:bg-white/5 transition-colors">
              <td class="p-4">
                <span class="font-mono text-xs text-red-400 font-bold bg-red-500/10 border border-red-500/20 px-2 py-1 rounded">
                  #{{ item.id.slice(0, 8) }}
                </span>
              </td>
              <td class="p-4">
                <div class="font-bold text-white">{{ item.movie_title }}</div>
                <div class="text-xs text-gray-400 mt-1 flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-xs">location_on</span>
                  {{ item.branch_name }} · {{ item.auditorium_name }}
                </div>
              </td>
              <td class="p-4 font-mono text-gray-300">
                {{ item.seats.map(s => `${s.row}${s.number}`).join(', ') }}
              </td>
              <td class="p-4 font-semibold text-white font-mono">
                {{ Number(item.total_price).toLocaleString('vi-VN') }}đ
              </td>
              <td class="p-4">
                <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase border"
                  :class="{
                    'bg-emerald-500/10 text-emerald-400 border-emerald-500/20': item.status === 'CONFIRMED',
                    'bg-amber-500/10 text-amber-400 border-amber-500/20': item.status === 'PENDING',
                    'bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse font-black shadow-[0_0_10px_rgba(244,63,94,0.2)]': item.status === 'CANCEL_REQUESTED',
                    'bg-zinc-500/10 text-zinc-400 border-zinc-500/20': item.status === 'CANCELLED' || item.status === 'EXPIRED'
                  }">
                  {{ item.status }}
                </span>
              </td>
              <td class="p-4 text-right">
                <button v-if="isBranchAdmin && ['PENDING','CONFIRMED','CANCEL_REQUESTED'].includes(item.status)" 
                  class="px-3 py-1.5 rounded-lg text-xs font-bold border transition-all"
                  :class="item.status === 'CANCEL_REQUESTED'
                    ? 'bg-rose-500 hover:bg-rose-600 text-white border-rose-500 shadow-md shadow-rose-500/20'
                    : 'bg-white/5 hover:bg-rose-500/20 text-rose-400 border-rose-500/20 hover:border-rose-500'" 
                  @click="cancel(item)">
                  {{ item.status === 'CANCEL_REQUESTED' ? 'Duyệt yêu cầu hủy' : 'Hủy đơn hàng' }}
                </button>
                <span v-else class="text-xs text-gray-500 font-medium">Không thể xử lý</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="!loading && !rows.length" class="p-16 text-center text-gray-400 flex flex-col items-center justify-center gap-2">
        <span class="material-symbols-outlined text-4xl text-gray-600">receipt_long</span>
        <p class="font-bold text-base">Không có đơn đặt vé nào phù hợp</p>
        <p class="text-xs text-gray-500">Thử thay đổi thời gian hoặc bộ lọc trạng thái để kiểm tra lại.</p>
      </div>

      <!-- Pagination Controls -->
      <div v-if="totalPages > 1" class="p-4 border-t border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4 bg-white/5">
        <span class="text-xs text-gray-400">Hiển thị trang {{ currentPage }} / {{ totalPages }} (Tổng {{ total }} đơn)</span>
        <div class="flex items-center gap-1.5">
          <button 
            :disabled="currentPage === 1" 
            @click="currentPage--"
            class="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-red-600 disabled:bg-transparent border border-white/10 hover:border-red-500 disabled:opacity-30 transition-all text-xs font-bold text-gray-300 disabled:hover:text-gray-500 hover:text-white"
          >
            Trước
          </button>
          <button 
            v-for="page in visiblePages" 
            :key="page"
            @click="currentPage = page"
            class="w-8 h-8 rounded-lg text-xs font-bold transition-all border flex items-center justify-center"
            :class="currentPage === page ? 'bg-red-600 border-red-500 text-white' : 'bg-white/5 border-white/10 hover:bg-white/10 text-gray-300'"
          >
            {{ page }}
          </button>
          <button 
            :disabled="currentPage === totalPages" 
            @click="currentPage++"
            class="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-red-600 disabled:bg-transparent border border-white/10 hover:border-red-500 disabled:opacity-30 transition-all text-xs font-bold text-gray-300 disabled:hover:text-gray-500 hover:text-white"
          >
            Sau
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-glass {
  background: rgba(26, 28, 28, 0.6);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
}
.field-input {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease-in-out;
}
.field-input:focus {
  border-color: #ef4444;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}
.action-btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
}
.action-btn-primary:active:not(:disabled) {
  transform: translateY(0);
}
</style>

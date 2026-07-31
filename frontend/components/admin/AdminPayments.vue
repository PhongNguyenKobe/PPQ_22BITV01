<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { adminBackendService, type AdminPayment } from '~/services/api'
import { useUserStore } from '~/store/user'
import { formatDateTime } from '~/utils/date'

const userStore = useUserStore()
const isBranchAdmin = computed(() => userStore.currentUser?.role === 'branch-admin')
const selectedBranch = useState<string>('admin-selected-branch', () => 'ALL')
const rows = ref<AdminPayment[]>([])
const total = ref(0)
const statusFilter = ref('')
const error = ref('')
const busyId = ref('')
const selected = ref<AdminPayment | null>(null)
const history = ref<any[]>([])

function isVnpay(item: AdminPayment) {
  return item.payment_method === 'VNPAY'
}

function isLegacy(item: AdminPayment) {
  return !item.provider_ref && !item.provider_transaction_no
}

function canRefundThroughGateway(item: AdminPayment) {
  return isBranchAdmin.value && isVnpay(item)
    && ['SUCCESS', 'REFUND_FAILED'].includes(item.status)
    && item.signature_valid === true
}

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
  error.value = ''
  try {
    const result = await adminBackendService.getPayments({
      status: statusFilter.value || undefined,
      branch_id: !isBranchAdmin.value && selectedBranch.value !== 'ALL' ? selectedBranch.value : undefined,
      limit: pageSize,
      skip: (currentPage.value - 1) * pageSize,
    })
    rows.value = result.payments
    total.value = result.total
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải giao dịch.'
  }
}

async function reconcile(item: AdminPayment) {
  busyId.value = item.id
  try {
    const result = await adminBackendService.reconcilePayment(item.id)
    window.alert(result.matched ? 'Dữ liệu CineAI khớp với VNPAY.' : 'Có sai lệch, vui lòng xem lịch sử đối soát.')
    await load()
  } catch (e: any) {
    error.value = e?.message || 'Không thể truy vấn VNPAY.'
  } finally {
    busyId.value = ''
  }
}

async function showHistory(item: AdminPayment) {
  selected.value = item
  history.value = await adminBackendService.getPaymentHistory(item.id)
}

async function refund(item: AdminPayment) {
  const reason = window.prompt('Nhập lý do hoàn tiền:')
  if (!reason?.trim() || !window.confirm(`Xác nhận hoàn ${Number(item.amount).toLocaleString('vi-VN')}đ?`)) return
  try {
    error.value = ''
    await adminBackendService.refundPayment(item.id, reason.trim())
    await load()
  } catch (e: any) {
    error.value = e?.message || 'Hoàn tiền thất bại.'
  }
}

onMounted(load)
watch(currentPage, () => {
  void load()
})
watch(statusFilter, () => {
  currentPage.value = 1
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
          <span class="material-symbols-outlined text-red-500 text-2xl">payments</span>
          <h2 class="text-xl font-black text-white tracking-tight">{{ isBranchAdmin ? 'Xử lý giao dịch & Hoàn tiền' :
            'Giám sát thanh toán' }}</h2>
        </div>
        <p class="text-sm text-gray-400 mt-1">
          {{ isBranchAdmin ? `Chỉ xử lý ${total} giao dịch phát sinh tại chi nhánh được phân công.` : `Theo dõi ${total}
          giao dịch toàn hệ thống ở chế độ chỉ đọc.` }}
        </p>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="panel-glass flex items-center justify-between p-5 gap-4 flex-wrap shadow-md">
      <div class="flex items-center gap-3">
        <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Trạng thái</label>
        <div class="relative min-w-[220px]">
          <select v-model="statusFilter"
            class="field-input w-full pl-4 pr-10 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-red-500 cursor-pointer appearance-none">
            <option value="">Tất cả trạng thái</option>
            <option value="SUCCESS">SUCCESS</option>
            <option value="PENDING">PENDING</option>
            <option value="FAILED">FAILED</option>
            <option value="REFUNDED">REFUNDED</option>
            <option value="REFUND_PENDING">REFUND_PENDING</option>
            <option value="REFUND_FAILED">REFUND_FAILED</option>
          </select>
          <span
            class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none text-sm">expand_more</span>
        </div>
      </div>

      <button
        class="action-btn-primary px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white font-bold text-sm rounded-xl transition-all shadow-md flex items-center gap-2"
        @click="() => { currentPage = 1; load(); }">
        <span class="material-symbols-outlined text-sm">sync</span>
        Làm mới giao dịch
      </button>
    </div>

    <!-- Error Indicator -->
    <div v-if="error"
      class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-400 flex items-center gap-2">
      <span class="material-symbols-outlined text-xl">error</span>
      <span class="font-medium">{{ error }}</span>
    </div>

    <!-- Payments Table -->
    <div class="panel-glass overflow-hidden shadow-lg">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1150px] text-left text-sm border-collapse">
          <thead>
            <tr class="border-b border-white/10 bg-white/5 text-gray-300 font-bold">
              <th class="p-4 text-xs uppercase tracking-wider">Mã giao dịch CineAI</th>
              <th class="p-4 text-xs uppercase tracking-wider">Mã Cổng VNPAY</th>
              <th class="p-4 text-xs uppercase tracking-wider">Mã Đơn</th>
              <th class="p-4 text-xs uppercase tracking-wider">Phương thức</th>
              <th class="p-4 text-xs uppercase tracking-wider">Số tiền</th>
              <th class="p-4 text-xs uppercase tracking-wider">Trạng thái</th>
              <th class="p-4 text-xs uppercase tracking-wider">Xác minh</th>
              <th class="p-4 text-xs uppercase tracking-wider text-right">Hành động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in rows" :key="item.id" class="border-b border-white/5 hover:bg-white/5 transition-colors">
              <td class="p-4">
                <div class="font-mono text-xs text-white font-semibold">{{ item.id.slice(0, 8) }}...{{ item.id.slice(-8)
                  }}</div>
                <span v-if="isLegacy(item)"
                  class="mt-1 inline-flex items-center gap-0.5 rounded bg-white/5 border border-white/5 px-2 py-0.5 text-[9px] text-gray-400 font-bold uppercase tracking-wider">
                  Legacy/Mock
                </span>
              </td>
              <td class="p-4">
                <template v-if="isVnpay(item)">
                  <div class="font-mono text-xs text-gray-400">Ref: {{ item.provider_ref || 'Đang tạo' }}</div>
                  <div class="mt-1 font-mono text-xs text-sky-400 flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-sky-400"></span>
                    No: {{ item.provider_transaction_no || 'Chưa phản hồi' }}
                  </div>
                </template>
                <span v-else class="text-xs text-gray-500 font-medium">Không áp dụng</span>
              </td>
              <td class="p-4">
                <span
                  class="font-mono text-xs text-red-400 font-bold bg-red-500/10 border border-red-500/20 px-2 py-0.5 rounded">
                  #{{ item.booking_id.slice(0, 8) }}
                </span>
              </td>
              <td class="p-4 text-gray-300 font-medium">{{ item.payment_method }}</td>
              <td class="p-4 font-mono font-bold text-white">{{ Number(item.amount).toLocaleString('vi-VN') }}đ</td>
              <td class="p-4">
                <span
                  class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase border"
                  :class="{
                    'bg-emerald-500/10 text-emerald-400 border-emerald-500/20': item.status === 'SUCCESS',
                    'bg-amber-500/10 text-amber-400 border-amber-500/20': item.status === 'PENDING',
                    'bg-rose-500/10 text-rose-400 border-rose-500/20': ['FAILED', 'REFUND_FAILED'].includes(item.status),
                    'bg-indigo-500/10 text-indigo-400 border-indigo-500/20': item.status === 'REFUNDED',
                    'bg-purple-500/10 text-purple-400 border-purple-500/20 animate-pulse': item.status === 'REFUND_PENDING'
                  }">
                  {{ item.status }}
                </span>
                <div v-if="isVnpay(item)" class="text-[10px] text-gray-500 mt-1">
                  Status: {{ item.provider_status || 'Chờ' }} · Code: {{ item.response_code || '—' }}
                </div>
                <div v-if="item.refund_error" class="mt-1 max-w-[220px] text-[10px] text-rose-400">
                  Hoàn tiền: {{ item.refund_error }}
                </div>
              </td>
              <td class="p-4">
                <template v-if="isVnpay(item)">
                  <div class="flex items-center gap-1.5 text-xs">
                    <template v-if="item.signature_valid === true">
                      <span class="material-symbols-outlined text-sm text-emerald-400">verified_user</span>
                      <span class="text-emerald-400 font-bold">Hợp lệ</span>
                    </template>
                    <template v-else-if="item.signature_valid === false">
                      <span class="material-symbols-outlined text-sm text-rose-400">gpp_bad</span>
                      <span class="text-rose-400 font-bold">Lỗi chữ ký</span>
                    </template>
                    <template v-else>
                      <span class="material-symbols-outlined text-sm text-amber-400">hourglass_empty</span>
                      <span class="text-amber-400 font-bold">Đang chờ</span>
                    </template>
                  </div>
                </template>
                <span v-else class="text-xs text-gray-500">N/A</span>
              </td>
              <td class="p-4 text-right whitespace-nowrap">
                <div class="flex items-center justify-end gap-2">
                  <button
                    class="px-2.5 py-1.5 rounded-lg text-xs font-bold bg-white/5 border border-white/10 hover:bg-white/10 text-gray-300 transition-colors"
                    @click="showHistory(item)">
                    Lịch sử
                  </button>
                  <button v-if="isBranchAdmin && isVnpay(item)"
                    class="px-2.5 py-1.5 rounded-lg text-xs font-bold bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/20 text-sky-400 transition-colors"
                    :disabled="busyId === item.id" @click="reconcile(item)">
                    {{ busyId === item.id ? 'Đang gọi...' : 'Đối soát' }}
                  </button>
                  <button v-if="canRefundThroughGateway(item)"
                    class="px-2.5 py-1.5 rounded-lg text-xs font-bold bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 text-amber-400 transition-colors animate-pulse"
                    @click="refund(item)">
                    {{ item.status === 'REFUND_FAILED' ? 'Thử hoàn lại' : 'Hoàn tiền' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!rows.length" class="p-16 text-center text-gray-400 flex flex-col items-center justify-center gap-2">
        <span class="material-symbols-outlined text-4xl text-gray-600">payment</span>
        <p class="font-bold text-base">Không tìm thấy giao dịch nào</p>
        <p class="text-xs text-gray-500">Không phát sinh giao dịch nào theo bộ lọc của bạn.</p>
      </div>

      <!-- Pagination Controls -->
      <div v-if="totalPages > 1" class="p-4 border-t border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4 bg-white/5">
        <span class="text-xs text-gray-400">Hiển thị trang {{ currentPage }} / {{ totalPages }} (Tổng {{ total }} giao dịch)</span>
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

    <!-- History Audit Details Panel (Sleek Drawer/Box) -->
    <Transition name="fade">
      <div v-if="selected" class="panel-glass p-6 shadow-xl relative border border-red-500/15 overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-red-500/5 rounded-full blur-xl pointer-events-none"></div>
        <div class="mb-5 flex justify-between items-start">
          <div>
            <h3 class="font-black text-white text-base">Nhật ký thay đổi trạng thái giao dịch</h3>
            <p class="font-mono text-xs text-gray-400 mt-1">Ref ID: {{ selected.provider_ref || selected.id }}</p>
          </div>
          <button
            class="w-8 h-8 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 hover:text-white flex items-center justify-center transition-colors"
            @click="selected = null">
            <span class="material-symbols-outlined text-sm">close</span>
          </button>
        </div>

        <div class="space-y-4 max-h-[300px] overflow-y-auto pr-2">
          <div v-for="(entry, index) in history" :key="entry.id"
            class="relative pl-6 pb-2 last:pb-0 border-l border-white/10 last:border-transparent">
            <!-- Timeline Dot -->
            <span
              class="absolute left-[-5px] top-1.5 w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"></span>

            <div class="flex flex-col gap-1">
              <div class="flex flex-wrap justify-between items-center gap-2">
                <span class="text-xs font-bold text-white bg-white/5 px-2 py-0.5 rounded border border-white/5">
                  {{ entry.source }} · <span class="text-gray-400">{{ entry.old_status || 'CREATE' }}</span> → <span
                    class="text-emerald-400">{{ entry.new_status }}</span>
                </span>
                <span class="text-xs text-gray-400 font-mono">{{ formatDateTime(entry.created_at) }}</span>
              </div>
              <p class="text-xs text-gray-400 leading-relaxed mt-1">
                <span class="font-semibold text-gray-300">VNPAY State:</span> code {{ entry.response_code || '—' }} ·
                status
                {{ entry.provider_status || '—' }}
                <span v-if="entry.note" class="block mt-0.5 text-gray-500 italic">Ghi chú: {{ entry.note }}</span>
              </p>
            </div>
          </div>

          <div v-if="!history.length" class="text-center py-6 text-gray-500 text-xs font-semibold">
            Không có nhật ký lịch sử cho giao dịch này.
          </div>
        </div>
      </div>
    </Transition>
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>

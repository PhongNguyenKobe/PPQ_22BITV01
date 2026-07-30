<script setup lang="ts">
import { adminBackendService, type AdminPayment } from '~/services/api'
import { useUserStore } from '~/store/user'

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
  return isBranchAdmin.value && isVnpay(item) && item.status === 'SUCCESS' && item.signature_valid === true
}

async function load() {
  error.value = ''
  try {
    const result = await adminBackendService.getPayments({
      status: statusFilter.value || undefined,
      branch_id: !isBranchAdmin.value && selectedBranch.value !== 'ALL' ? selectedBranch.value : undefined,
      limit: 100,
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
  await adminBackendService.refundPayment(item.id, reason.trim())
  await load()
}

onMounted(load)
watch(selectedBranch, () => {
  if (!isBranchAdmin.value) void load()
})
</script>

<template>
  <div class="space-y-5">
    <div>
      <h2 class="text-xl font-black">{{ isBranchAdmin ? 'Xử lý giao dịch và hoàn tiền' : 'Giám sát thanh toán' }}</h2>
      <p class="text-sm text-on-surface-variant">{{ isBranchAdmin ? `Chỉ xử lý ${total} giao dịch phát sinh tại chi nhánh được phân công.` : `Theo dõi ${total} giao dịch ở chế độ chỉ đọc; việc xử lý thuộc Branch Admin.` }}</p>
    </div>
    <div class="panel flex gap-3 p-4">
      <select v-model="statusFilter" class="field-input max-w-xs">
        <option value="">Tất cả trạng thái</option>
        <option>SUCCESS</option><option>PENDING</option><option>FAILED</option>
        <option>REFUNDED</option><option>REFUND_PENDING</option>
      </select>
      <button class="action-primary" @click="load">Lọc</button>
    </div>
    <p v-if="error" class="text-rose-400">{{ error }}</p>
    <div class="panel overflow-x-auto">
      <table class="w-full min-w-[1150px] text-left text-sm">
        <thead class="border-b border-white/10 text-on-surface-variant">
          <tr><th class="p-4">Mã thanh toán CineAI</th><th>Mã cổng thanh toán</th><th>Mã đơn</th><th>Phương thức</th><th>Số tiền</th><th>Trạng thái</th><th>Xác minh</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="item in rows" :key="item.id" class="border-b border-white/5">
            <td class="p-4">
              <div class="font-mono text-xs">{{ item.id }}</div>
              <span v-if="isLegacy(item)" class="mt-1 inline-block rounded bg-white/5 px-2 py-0.5 text-[10px] text-on-surface-variant">Dữ liệu cũ / mô phỏng</span>
            </td>
            <td>
              <template v-if="isVnpay(item)">
                <div class="font-mono text-xs">Ref: {{ item.provider_ref || 'Đang khởi tạo' }}</div>
                <div class="mt-1 font-mono text-xs text-sky-400">VNPAY: {{ item.provider_transaction_no || 'Chưa phản hồi' }}</div>
              </template>
              <span v-else class="text-on-surface-variant">Không áp dụng VNPAY</span>
            </td>
            <td class="font-mono">{{ item.booking_id.slice(0, 8) }}</td>
            <td>{{ item.payment_method }}</td>
            <td>{{ Number(item.amount).toLocaleString('vi-VN') }}đ</td>
            <td><b>{{ item.status }}</b><div v-if="isVnpay(item)" class="text-xs text-on-surface-variant">VNPAY: {{ item.provider_status || 'Chờ' }} · Response: {{ item.response_code || '—' }}</div></td>
            <td>
              <template v-if="isVnpay(item)">
                <span v-if="item.signature_valid === true" class="text-emerald-400">Chữ ký hợp lệ</span>
                <span v-else-if="item.signature_valid === false" class="text-rose-400">Sai chữ ký</span>
                <span v-else class="text-amber-400">Chờ VNPAY phản hồi</span>
              </template>
              <span v-else class="text-on-surface-variant">Không áp dụng</span>
            </td>
            <td class="space-x-3 whitespace-nowrap">
              <button class="text-sky-400" @click="showHistory(item)">Lịch sử</button>
              <button v-if="isBranchAdmin && isVnpay(item)" class="text-violet-400" :disabled="busyId === item.id" @click="reconcile(item)">Đối soát</button>
              <button v-if="canRefundThroughGateway(item)" class="text-amber-400" @click="refund(item)">Yêu cầu hoàn</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="selected" class="panel p-5">
      <div class="mb-4 flex justify-between">
        <div><h3 class="font-black">Lịch sử giao dịch</h3><p class="font-mono text-xs text-on-surface-variant">{{ selected.provider_ref || selected.id }}</p></div>
        <button class="text-on-surface-variant" @click="selected = null">Đóng</button>
      </div>
      <div v-for="entry in history" :key="entry.id" class="border-t border-white/5 py-3 text-sm">
        <div class="flex flex-wrap justify-between gap-2"><b>{{ entry.source }} · {{ entry.old_status || '—' }} → {{ entry.new_status }}</b><span>{{ formatDateTime(entry.created_at) }}</span></div>
        <p class="text-xs text-on-surface-variant">Response: {{ entry.response_code || '—' }} · Provider: {{ entry.provider_status || '—' }} · {{ entry.note || '' }}</p>
      </div>
    </div>
  </div>
</template>

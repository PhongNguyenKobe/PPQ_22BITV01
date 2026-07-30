<script setup lang="ts">
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

async function load() {
  loading.value = true
  error.value = ''
  try {
    const result = await adminBackendService.getBookings({
      status: status.value || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      branch_id: !isBranchAdmin.value && selectedBranch.value !== 'ALL' ? selectedBranch.value : undefined,
      limit: 100,
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
  await adminBackendService.cancelBooking(item.id, reason.trim())
  await load()
}

onMounted(load)
watch(selectedBranch, () => {
  if (!isBranchAdmin.value) void load()
})
</script>

<template>
  <div class="space-y-5">
    <div><h2 class="text-xl font-black">{{ isBranchAdmin ? 'Quản lý đơn đặt vé' : 'Giám sát đơn đặt vé' }}</h2><p class="text-sm text-on-surface-variant">{{ isBranchAdmin ? `Tra cứu và xử lý ${total} đơn thuộc chi nhánh.` : `Theo dõi ${total} đơn trên toàn hệ thống ở chế độ chỉ đọc.` }}</p></div>
    <div class="panel grid gap-3 p-4 md:grid-cols-4">
      <input v-model="startDate" type="date" class="field-input">
      <input v-model="endDate" type="date" class="field-input">
      <select v-model="status" class="field-input"><option value="">Tất cả trạng thái</option><option>PENDING</option><option>CONFIRMED</option><option>CANCEL_REQUESTED</option><option>CANCELLED</option><option>EXPIRED</option></select>
      <button class="action-primary" @click="load">Lọc dữ liệu</button>
    </div>
    <p v-if="error" class="text-rose-400">{{ error }}</p>
    <div class="panel overflow-x-auto">
      <table class="w-full text-sm"><thead class="border-b border-white/10 text-left text-on-surface-variant"><tr><th class="p-4">Mã đơn</th><th>Phim / rạp</th><th>Ghế</th><th>Tổng tiền</th><th>Trạng thái</th><th></th></tr></thead>
        <tbody><tr v-for="item in rows" :key="item.id" class="border-b border-white/5"><td class="p-4 font-mono">{{ item.id.slice(0, 8) }}</td><td><b>{{ item.movie_title }}</b><br><span class="text-xs text-on-surface-variant">{{ item.branch_name }} · {{ item.auditorium_name }}</span></td><td>{{ item.seats.map(s => `${s.row}${s.number}`).join(', ') }}</td><td>{{ Number(item.total_price).toLocaleString('vi-VN') }}đ</td><td>{{ item.status }}</td><td class="p-3"><button v-if="isBranchAdmin && ['PENDING','CONFIRMED','CANCEL_REQUESTED'].includes(item.status)" class="text-rose-400" @click="cancel(item)">{{ item.status === 'CANCEL_REQUESTED' ? 'Duyệt hủy' : 'Hủy đơn' }}</button></td></tr></tbody>
      </table>
      <p v-if="!loading && !rows.length" class="p-10 text-center text-on-surface-variant">Không có đơn phù hợp.</p>
    </div>
  </div>
</template>

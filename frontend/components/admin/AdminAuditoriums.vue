<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { adminBackendService, adminService, type AdminAuditorium, type AdminBranchManage } from '~/services/api'

const router = useRouter()
const auditoriums = ref<AdminAuditorium[]>([])
const branches = ref<AdminBranchManage[]>([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const statusFilter = ref('ALL')
const screenFilter = ref('ALL')
const showCreateForm = ref(false)
const creating = ref(false)
const saving = ref(false)
const actionConfirmItem = ref<AdminAuditorium | null>(null)
const editingAuditorium = ref<AdminAuditorium | null>(null)

const auditoriumForm = ref({ branchId: '', code: '', name: '', rows: 8, seatsPerRow: 12, screenType: '2D' })
const editForm = ref({ name: '', screenType: '2D' })
const formatDefaults: Record<string, { rows: number; columns: number; note: string }> = {
  '2D': { rows: 8, columns: 12, note: 'Mẫu phòng tiêu chuẩn' },
  '3D': { rows: 9, columns: 14, note: 'Mẫu phòng 3D mở rộng' },
  'IMAX': { rows: 10, columns: 16, note: 'Mẫu phòng màn hình lớn' },
  '4DX': { rows: 8, columns: 12, note: 'Mẫu phòng hiệu ứng chuyển động' },
}

function applyCreateFormatDefaults() {
  const preset = formatDefaults[auditoriumForm.value.screenType] || formatDefaults['2D']
  auditoriumForm.value.rows = preset.rows
  auditoriumForm.value.seatsPerRow = preset.columns
}

const totals = computed(() => ({
  rooms: auditoriums.value.length,
  ready: auditoriums.value.filter(item => item.is_ready).length,
  attention: auditoriums.value.filter(item => !item.is_ready).length,
  seats: auditoriums.value.reduce((sum, item) => sum + (item.active_seats_count ?? item.total_seats), 0),
}))

const filteredAuditoriums = computed(() => {
  const keyword = search.value.trim().toLocaleLowerCase('vi')
  return auditoriums.value.filter((item) => {
    const matchesSearch = !keyword || `${item.name} ${item.code}`.toLocaleLowerCase('vi').includes(keyword)
    const matchesScreen = screenFilter.value === 'ALL' || item.screen_type === screenFilter.value
    const status = !item.is_active ? 'INACTIVE' : item.is_ready ? 'READY' : 'NEEDS_SETUP'
    return matchesSearch && matchesScreen && (statusFilter.value === 'ALL' || statusFilter.value === status)
  })
})

function roomState(item: AdminAuditorium) {
  if (!item.is_active) return { label: 'Tạm ngưng', cls: 'border-slate-500/30 bg-slate-500/10 text-slate-300', icon: 'pause_circle' }
  if (!item.is_ready) return { label: 'Cần cấu hình ghế', cls: 'border-amber-500/30 bg-amber-500/10 text-amber-300', icon: 'warning' }
  if (item.future_showtimes_count > 0) return { label: 'Đang vận hành', cls: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300', icon: 'check_circle' }
  return { label: 'Sẵn sàng', cls: 'border-sky-500/30 bg-sky-500/10 text-sky-300', icon: 'task_alt' }
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [statsData, auditoriumData] = await Promise.all([
      adminService.getBranchAdminStats(),
      adminBackendService.getAuditoriums(),
    ])
    branches.value = [{ id: statsData.branchId, vendor_id: '', code: '', name: statsData.branchName, address_line: '', city: '', district: null, phone: null, is_active: true, auditoriums_count: auditoriumData.length, active_staff_count: 0, future_showtimes_count: 0, is_ready: true, can_delete: false }]
    auditoriums.value = auditoriumData
    auditoriumForm.value.branchId = statsData.branchId
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải dữ liệu phòng chiếu.'
  } finally {
    loading.value = false
  }
}

function validateCreate() {
  const code = auditoriumForm.value.code.trim().toUpperCase()
  if (auditoriums.value.some(item => item.code.toUpperCase() === code)) return 'Mã phòng đã tồn tại trong chi nhánh.'
  if (!/^[A-Z0-9_-]+$/.test(code)) return 'Mã phòng chỉ gồm chữ in hoa, số, dấu gạch ngang hoặc gạch dưới.'
  return ''
}

async function createAuditorium() {
  error.value = validateCreate()
  if (error.value) return
  creating.value = true
  try {
    await adminBackendService.createAuditorium({
      branch_id: auditoriumForm.value.branchId,
      code: auditoriumForm.value.code.trim().toUpperCase(),
      name: auditoriumForm.value.name.trim(),
      total_seats: auditoriumForm.value.rows * auditoriumForm.value.seatsPerRow,
      rows: auditoriumForm.value.rows,
      seats_per_row: auditoriumForm.value.seatsPerRow,
      screen_type: auditoriumForm.value.screenType,
      is_active: true,
    })
    auditoriumForm.value = { branchId: auditoriumForm.value.branchId, code: '', name: '', rows: 8, seatsPerRow: 12, screenType: '2D' }
    showCreateForm.value = false
    await loadData()
  } catch (e: any) {
    error.value = e?.message || 'Không thể tạo phòng chiếu mới.'
  } finally {
    creating.value = false
  }
}

function openEditModal(item: AdminAuditorium) {
  editingAuditorium.value = item
  editForm.value = { name: item.name, screenType: item.screen_type || '2D' }
}

async function saveAuditoriumEdit() {
  if (!editingAuditorium.value || !editForm.value.name.trim()) return
  saving.value = true
  error.value = ''
  try {
    await adminBackendService.updateAuditorium(editingAuditorium.value.id, { name: editForm.value.name.trim(), screen_type: editForm.value.screenType })
    editingAuditorium.value = null
    await loadData()
  } catch (e: any) {
    error.value = e?.message || 'Không thể cập nhật phòng chiếu.'
  } finally {
    saving.value = false
  }
}

async function toggleActive(item: AdminAuditorium) {
  error.value = ''
  try {
    await adminBackendService.updateAuditorium(item.id, { is_active: !item.is_active })
    await loadData()
  } catch (e: any) {
    error.value = e?.message || 'Không thể thay đổi trạng thái phòng.'
  }
}

async function executeDelete() {
  if (!actionConfirmItem.value) return
  try {
    await adminBackendService.deleteAuditorium(actionConfirmItem.value.id)
    actionConfirmItem.value = null
    await loadData()
  } catch (e: any) {
    error.value = e?.message || 'Không thể xóa phòng chiếu.'
    actionConfirmItem.value = null
  }
}

function openSeatMap(item: AdminAuditorium) {
  router.push({ query: { tab: 'seats', auditorium: item.id } })
}

onMounted(loadData)
</script>

<template>
  <div class="space-y-6">
    <header class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-xs font-black uppercase tracking-[0.2em] text-primary">Cấu hình cơ sở vật chất</p>
        <h2 class="mt-1 text-2xl font-black text-on-surface">Phòng chiếu</h2>
        <p class="mt-1 text-sm text-on-surface-variant">Tạo phòng, thiết lập sơ đồ ghế và kiểm soát trạng thái trước khi xếp lịch chiếu.</p>
      </div>
      <button class="action-primary flex items-center gap-2" @click="showCreateForm = !showCreateForm">
        <span class="material-symbols-outlined">{{ showCreateForm ? 'close' : 'meeting_room' }}</span>
        {{ showCreateForm ? 'Đóng biểu mẫu' : 'Tạo phòng mới' }}
      </button>
    </header>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-300">{{ error }}</p>

    <section class="grid grid-cols-2 gap-3 xl:grid-cols-4">
      <article class="metric"><span class="material-symbols-outlined text-primary">meeting_room</span><div><p>Tổng phòng</p><strong>{{ totals.rooms }}</strong></div></article>
      <article class="metric"><span class="material-symbols-outlined text-emerald-400">task_alt</span><div><p>Sẵn sàng</p><strong>{{ totals.ready }}</strong></div></article>
      <article class="metric"><span class="material-symbols-outlined text-amber-400">construction</span><div><p>Cần xử lý</p><strong>{{ totals.attention }}</strong></div></article>
      <article class="metric"><span class="material-symbols-outlined text-sky-400">event_seat</span><div><p>Ghế hoạt động</p><strong>{{ totals.seats }}</strong></div></article>
    </section>

    <form v-if="showCreateForm" class="panel space-y-5 p-6" @submit.prevent="createAuditorium">
      <div>
        <h3 class="text-lg font-black text-on-surface">Thiết lập phòng mới</h3>
        <p class="text-sm text-on-surface-variant">Hệ thống sẽ tạo phòng và toàn bộ ghế thường trong cùng một giao dịch.</p>
      </div>
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <label class="field"><span>Chi nhánh phụ trách</span><input :value="branches[0]?.name || 'Đang tải...'" class="field-input" disabled /></label>
        <label class="field"><span>Mã phòng nội bộ</span><input v-model="auditoriumForm.code" maxlength="30" required placeholder="Ví dụ: P01" class="field-input uppercase" /><small>Duy nhất, không đổi sau khi tạo.</small></label>
        <label class="field"><span>Tên hiển thị</span><input v-model="auditoriumForm.name" maxlength="100" required placeholder="Ví dụ: Cinema 1" class="field-input" /></label>
        <label class="field"><span>Định dạng phòng</span><select v-model="auditoriumForm.screenType" class="field-input" @change="applyCreateFormatDefaults"><option>2D</option><option>3D</option><option>IMAX</option><option>4DX</option></select><small>{{ formatDefaults[auditoriumForm.screenType]?.note }} · Có thể chỉnh lại số ghế.</small></label>
        <label class="field"><span>Số hàng ghế</span><input v-model.number="auditoriumForm.rows" type="number" min="1" max="26" required class="field-input" /></label>
        <label class="field"><span>Số ghế mỗi hàng</span><input v-model.number="auditoriumForm.seatsPerRow" type="number" min="1" max="50" required class="field-input" /></label>
        <div class="seat-total"><span>Sức chứa khởi tạo</span><strong>{{ auditoriumForm.rows * auditoriumForm.seatsPerRow }} ghế</strong></div>
      </div>
      <div class="flex justify-end gap-3 border-t border-white/10 pt-4">
        <button type="button" class="action-ghost" @click="showCreateForm = false">Hủy</button>
        <button class="action-primary" :disabled="creating">{{ creating ? 'Đang tạo...' : 'Tạo phòng và sơ đồ ghế' }}</button>
      </div>
    </form>

    <section class="panel grid gap-3 p-4 lg:grid-cols-[1fr_220px_220px]">
      <label class="search-box"><span class="material-symbols-outlined">search</span><input v-model="search" placeholder="Tìm theo tên hoặc mã phòng..." /></label>
      <select v-model="statusFilter" class="field-input"><option value="ALL">Tất cả trạng thái</option><option value="READY">Sẵn sàng</option><option value="NEEDS_SETUP">Cần cấu hình</option><option value="INACTIVE">Tạm ngưng</option></select>
      <select v-model="screenFilter" class="field-input"><option value="ALL">Tất cả màn hình</option><option>2D</option><option>3D</option><option>IMAX</option><option>4DX</option></select>
    </section>

    <div v-if="loading" class="panel py-16 text-center text-on-surface-variant">Đang tải danh sách phòng chiếu...</div>
    <div v-else class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      <article v-for="item in filteredAuditoriums" :key="item.id" class="room-card">
        <div class="flex items-start justify-between gap-3 p-5">
          <div class="flex min-w-0 items-center gap-3">
            <div class="room-icon"><span class="material-symbols-outlined">theaters</span></div>
            <div class="min-w-0"><p class="truncate text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">{{ item.branch_name }}</p><h3 class="truncate text-lg font-black text-on-surface">{{ item.name }}</h3><p class="text-xs text-on-surface-variant">Mã phòng: <b class="text-on-surface">{{ item.code }}</b></p></div>
          </div>
          <span class="status-chip" :class="roomState(item).cls"><span class="material-symbols-outlined">{{ roomState(item).icon }}</span>{{ roomState(item).label }}</span>
        </div>
        <div class="grid grid-cols-3 border-y border-white/5 bg-black/20">
          <div class="room-stat"><span>Màn hình</span><b>{{ item.screen_type || '2D' }}</b></div>
          <div class="room-stat"><span>Ghế hoạt động</span><b>{{ item.active_seats_count ?? item.total_seats }}</b></div>
          <div class="room-stat"><span>Suất sắp tới</span><b>{{ item.future_showtimes_count }}</b></div>
        </div>
        <div v-if="!item.is_ready && item.is_active" class="mx-5 mt-4 rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 text-xs text-amber-200">Phòng chưa có ghế hoạt động. Hãy hoàn thiện sơ đồ ghế trước khi tạo suất chiếu.</div>
        <div class="flex flex-wrap items-center gap-2 p-4">
          <button class="room-action primary" @click="openSeatMap(item)"><span class="material-symbols-outlined">event_seat</span>Sơ đồ ghế</button>
          <button class="room-action" @click="openEditModal(item)"><span class="material-symbols-outlined">edit</span>Sửa</button>
          <button class="room-action" :class="item.is_active ? 'warning' : 'success'" :disabled="item.is_active && item.future_showtimes_count > 0" :title="item.is_active && item.future_showtimes_count > 0 ? 'Hãy xử lý các suất chiếu tương lai trước' : ''" @click="toggleActive(item)"><span class="material-symbols-outlined">{{ item.is_active ? 'pause_circle' : 'play_circle' }}</span>{{ item.is_active && item.future_showtimes_count > 0 ? 'Đang có lịch' : item.is_active ? 'Tạm ngưng' : 'Mở lại' }}</button>
          <button v-if="item.can_delete" class="room-action danger ml-auto" @click="actionConfirmItem = item"><span class="material-symbols-outlined">delete</span>Xóa</button>
        </div>
      </article>
      <div v-if="filteredAuditoriums.length === 0" class="panel col-span-full py-14 text-center text-on-surface-variant"><span class="material-symbols-outlined mb-2 block text-5xl opacity-40">meeting_room</span>Không tìm thấy phòng chiếu phù hợp.</div>
    </div>

    <div v-if="editingAuditorium" class="modal-backdrop">
      <div class="modal-card">
        <div class="flex items-center justify-between border-b border-white/10 p-5"><div><h3 class="text-lg font-black">Chỉnh sửa {{ editingAuditorium.name }}</h3><p class="text-xs text-on-surface-variant">Mã {{ editingAuditorium.code }} không thể thay đổi.</p></div><button @click="editingAuditorium = null"><span class="material-symbols-outlined">close</span></button></div>
        <div class="space-y-4 p-6"><label class="field"><span>Tên hiển thị</span><input v-model="editForm.name" class="field-input" /></label><label class="field"><span>Loại màn hình</span><select v-model="editForm.screenType" class="field-input"><option>2D</option><option>3D</option><option>IMAX</option><option>4DX</option></select></label><p v-if="editingAuditorium.future_showtimes_count" class="rounded-xl bg-amber-500/10 p-3 text-xs text-amber-200">Phòng có {{ editingAuditorium.future_showtimes_count }} suất tương lai. Hãy chắc chắn loại màn hình mới đúng với lịch đã bán.</p></div>
        <div class="flex justify-end gap-3 border-t border-white/10 p-4"><button class="action-ghost" @click="editingAuditorium = null">Hủy</button><button class="action-primary" :disabled="saving" @click="saveAuditoriumEdit">{{ saving ? 'Đang lưu...' : 'Lưu thay đổi' }}</button></div>
      </div>
    </div>

    <div v-if="actionConfirmItem" class="modal-backdrop">
      <div class="modal-card max-w-sm p-6 text-center"><div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-rose-500/15 text-rose-400"><span class="material-symbols-outlined text-3xl">delete_forever</span></div><h3 class="text-xl font-black">Xóa phòng chưa sử dụng?</h3><p class="my-3 text-sm text-on-surface-variant">Phòng <b>{{ actionConfirmItem.name }}</b> chưa có lịch chiếu. Thao tác sẽ xóa cả sơ đồ ghế và không thể hoàn tác.</p><div class="mt-5 flex gap-3"><button class="action-ghost flex-1" @click="actionConfirmItem = null">Giữ lại</button><button class="flex-1 rounded-xl bg-rose-600 px-4 py-2 font-bold text-white" @click="executeDelete">Xóa vĩnh viễn</button></div></div>
    </div>
  </div>
</template>

<style scoped>
.panel,.room-card,.modal-card{border:1px solid rgba(255,255,255,.08);border-radius:1rem;background:#1a1c1c;box-shadow:0 14px 36px rgba(0,0,0,.2)}
.metric{display:flex;align-items:center;gap:.8rem;min-height:92px;padding:1rem;border:1px solid rgba(255,255,255,.08);border-radius:1rem;background:linear-gradient(145deg,#1d2020,#171919)}.metric>span{font-size:1.8rem}.metric p{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:#999}.metric strong{font-size:1.35rem;color:#f3f3f3}
.field{display:flex;flex-direction:column;gap:.35rem}.field>span{font-size:.7rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:#aaa}.field small{font-size:.65rem;color:#777}.field-input,.search-box{width:100%;border:1px solid rgba(255,255,255,.12);border-radius:.75rem;background:rgba(20,22,22,.9);padding:.7rem .8rem;color:#f5f5f5}.field-input:focus,.search-box:focus-within{outline:none;border-color:rgba(229,9,20,.7);box-shadow:0 0 0 3px rgba(229,9,20,.12)}.field-input:disabled{color:#999}.search-box{display:flex;align-items:center;gap:.6rem}.search-box input{width:100%;background:transparent;outline:none}.seat-total{display:flex;flex-direction:column;justify-content:center;border:1px solid rgba(229,9,20,.2);border-radius:.75rem;background:rgba(229,9,20,.06);padding:.7rem 1rem}.seat-total span{font-size:.7rem;color:#aaa}.seat-total strong{color:#ff6971}
.room-card{overflow:hidden;transition:.2s}.room-card:hover{transform:translateY(-2px);border-color:rgba(255,255,255,.16)}.room-icon{display:flex;width:48px;height:48px;flex:none;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.1);border-radius:14px;background:rgba(255,255,255,.05);color:#ff4f57}.status-chip{display:inline-flex;flex:none;align-items:center;gap:.25rem;border:1px solid;border-radius:999px;padding:.3rem .5rem;font-size:.62rem;font-weight:800}.status-chip span{font-size:.9rem}.room-stat{padding:1rem;border-right:1px solid rgba(255,255,255,.05)}.room-stat:last-child{border:0}.room-stat span{display:block;font-size:.62rem;text-transform:uppercase;color:#888}.room-stat b{font-size:.9rem;color:#eee}.room-action{display:inline-flex;align-items:center;gap:.3rem;border-radius:.65rem;padding:.48rem .65rem;font-size:.72rem;font-weight:800;color:#bbb;transition:.15s}.room-action span{font-size:1rem}.room-action:hover{background:rgba(255,255,255,.06);color:white}.room-action.primary{background:rgba(14,165,233,.1);color:#59c7fa}.room-action.warning{color:#fbbf24}.room-action.success{color:#34d399}.room-action.danger{color:#fb7185}
.room-action:disabled{cursor:not-allowed;opacity:.42}.room-action:disabled:hover{background:transparent;color:#fbbf24}.action-primary,.action-ghost{border-radius:.75rem;padding:.65rem 1rem;font-size:.82rem;font-weight:800}.action-primary{background:linear-gradient(135deg,#e50914,#bd0710);color:white}.action-primary:disabled{opacity:.55}.action-ghost{border:1px solid rgba(255,255,255,.1);color:#ccc}.modal-backdrop{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;padding:1rem;background:rgba(0,0,0,.72);backdrop-filter:blur(8px)}.modal-card{width:100%;max-width:460px;color:#eee}
</style>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { adminBackendService, adminService, type AdminAuditorium, type AdminBranchManage, type AdminSeatType } from '~/services/api'
import { useUserStore } from '~/store/user'

const userStore = useUserStore()
const isBranchAdmin = computed(() => userStore.currentUser?.role === 'branch-admin')

const auditoriums = ref<AdminAuditorium[]>([])
const branches = ref<AdminBranchManage[]>([])
const seatTypes = ref<AdminSeatType[]>([])
const loading = ref(false)
const error = ref('')

const showCreateForm = ref(false)
const creating = ref(false)

const auditoriumForm = ref({
  branchId: '',
  code: '',
  name: '',
  rows: 8,
  seatsPerRow: 12,
  screenType: '2D',
})

const editingAuditorium = ref<AdminAuditorium | null>(null)
const editForm = ref({
  name: '',
  screenType: '2D',
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    if (isBranchAdmin.value) {
      const [statsData, auditoriumData, seatTypeData] = await Promise.all([
        adminService.getBranchAdminStats(),
        adminBackendService.getAuditoriums(),
        adminBackendService.getSeatTypes(),
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
    } else {
      // Super Admin shouldn't ideally be creating auditoriums without branches, but we handle it just in case.
      // However, Super Admin DOES NOT see auditoriums tab in current UI logic.
      const [auditoriumData, branchData, seatTypeData] = await Promise.all([
        adminBackendService.getAuditoriums(),
        adminBackendService.getBranchesManage(),
        adminBackendService.getSeatTypes(),
      ])
      auditoriums.value = auditoriumData
      branches.value = branchData
      seatTypes.value = seatTypeData
    }
    
    if (branches.value.length > 0 && !auditoriumForm.value.branchId) {
      auditoriumForm.value.branchId = branches.value[0].id
    }
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải dữ liệu phòng chiếu.'
  } finally {
    loading.value = false
  }
}

function seatTypeByCode(code: string) {
  return seatTypes.value.find((item) => item.code === code) || seatTypes.value[0]
}

async function createAuditorium() {
  error.value = ''
  creating.value = true
  try {
    const created = await adminBackendService.createAuditorium({
      branch_id: auditoriumForm.value.branchId,
      code: auditoriumForm.value.code.trim().toUpperCase(),
      name: auditoriumForm.value.name.trim(),
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
    showCreateForm.value = false
    
    auditoriums.value = await adminBackendService.getAuditoriums()
  } catch (e: any) {
    error.value = e?.message || 'Không thể tạo phòng chiếu mới.'
  } finally {
    creating.value = false
  }
}

function openEditModal(item: AdminAuditorium) {
  editingAuditorium.value = item
  editForm.value = {
    name: item.name,
    screenType: item.screen_type || '2D',
  }
}

function closeEditModal() {
  editingAuditorium.value = null
}

async function saveAuditoriumEdit() {
  if (!editingAuditorium.value) return
  error.value = ''
  try {
    await adminBackendService.updateAuditorium(editingAuditorium.value.id, {
      name: editForm.value.name.trim(),
      screen_type: editForm.value.screenType.toUpperCase(),
    })
    auditoriums.value = await adminBackendService.getAuditoriums()
    closeEditModal()
  } catch (e: any) {
    error.value = e?.message || 'Không thể cập nhật thông tin phòng chiếu.'
  }
}

const actionConfirmItem = ref<AdminAuditorium | null>(null)

async function executeDelete() {
  if (!actionConfirmItem.value) return
  try {
    await adminBackendService.deleteAuditorium(actionConfirmItem.value.id)
    auditoriums.value = await adminBackendService.getAuditoriums()
    actionConfirmItem.value = null
  } catch (e: any) {
    error.value = e?.message || 'Không thể xoá phòng chiếu.'
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-on-surface">Phòng chiếu rạp</h2>
        <p class="text-sm text-on-surface-variant mt-1">Quản lý danh sách phòng chiếu và khởi tạo kích thước sơ đồ ghế.</p>
      </div>
      <button 
        @click="showCreateForm = !showCreateForm" 
        class="action-primary flex items-center gap-2"
        :class="{'!bg-surface-variant !text-on-surface hover:!bg-white/10': showCreateForm}"
      >
        <span class="material-symbols-outlined">{{ showCreateForm ? 'close' : 'meeting_room' }}</span>
        {{ showCreateForm ? 'Đóng' : 'Tạo phòng mới' }}
      </button>
    </div>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-400">
      {{ error }}
    </p>

    <!-- Create Form Toggle -->
    <div v-if="showCreateForm" class="panel p-6 shadow-xl border-primary/20 animate-fade-in relative overflow-hidden">
      <div class="absolute -right-20 -top-20 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
      
      <form class="space-y-5 relative z-10" @submit.prevent="createAuditorium">
        <h3 class="text-lg font-black text-on-surface flex items-center gap-2 border-b border-white/10 pb-3">
          <span class="material-symbols-outlined text-primary">add_box</span>
          Thiết lập phòng chiếu mới
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="space-y-1 md:col-span-2">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Chi nhánh</label>
            <select v-model="auditoriumForm.branchId" class="field-input font-medium" required>
              <option value="" disabled>Chọn chi nhánh</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>
          
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Mã phòng</label>
            <input v-model="auditoriumForm.code" required placeholder="VD: P01" class="field-input uppercase" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên hiển thị</label>
            <input v-model="auditoriumForm.name" required placeholder="VD: Cinema 1" class="field-input" />
          </div>
          
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Loại màn hình</label>
            <select v-model="auditoriumForm.screenType" class="field-input font-medium" required>
              <option value="2D">Tiêu chuẩn (2D)</option>
              <option value="3D">Màn hình 3D (3D)</option>
              <option value="IMAX">Màn hình siêu lớn (IMAX)</option>
              <option value="4DX">Phòng chiếu 4DX</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Số Hàng ghế</label>
            <input v-model.number="auditoriumForm.rows" type="number" min="1" max="26" class="field-input" required />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Số Cột ghế</label>
            <input v-model.number="auditoriumForm.seatsPerRow" type="number" min="1" max="50" class="field-input" required />
          </div>
          <div class="space-y-1 flex items-end">
            <div class="w-full bg-white/5 border border-white/10 rounded-xl p-3 flex flex-col items-center justify-center">
              <span class="text-xs text-on-surface-variant">Tổng số ghế</span>
              <span class="text-lg font-black text-primary">{{ auditoriumForm.rows * auditoriumForm.seatsPerRow }}</span>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-3 pt-4 border-t border-white/10 mt-2">
          <button type="button" @click="showCreateForm = false" class="px-5 py-2.5 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button type="submit" class="action-primary px-8" :disabled="creating">
            {{ creating ? 'Đang tạo...' : 'Lưu và sinh sơ đồ ghế' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Auditorium List -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <div v-for="item in auditoriums" :key="item.id" class="panel p-0 overflow-hidden flex flex-col group hover:border-white/20 transition-all hover:shadow-2xl">
        <div class="p-5 flex justify-between items-start border-b border-white/5 relative overflow-hidden">
          <div class="absolute -right-4 -top-4 w-20 h-20 bg-primary/10 rounded-full blur-2xl group-hover:bg-primary/20 transition-colors"></div>
          
          <div class="relative z-10 w-full flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10 shadow-inner">
                <span class="material-symbols-outlined text-white/50 text-[24px]">chair</span>
              </div>
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold">{{ item.branch_name }}</p>
                <h3 class="font-bold text-lg text-on-surface flex items-center gap-2">
                  {{ item.name }}
                  <span class="text-[10px] px-1.5 py-0.5 rounded border border-white/10 bg-black/40 text-on-surface-variant uppercase tracking-widest">{{ item.code }}</span>
                </h3>
              </div>
            </div>
          </div>
        </div>
        
        <div class="p-5 bg-black/20 grid grid-cols-2 gap-4 flex-1">
          <div>
            <span class="text-xs text-on-surface-variant block mb-1">Màn hình</span>
            <span class="inline-block px-2 py-0.5 rounded-full text-xs font-bold bg-white/10 text-on-surface border border-white/10">{{ item.screen_type || '2D' }}</span>
          </div>
          <div>
            <span class="text-xs text-on-surface-variant block mb-1">Sức chứa</span>
            <span class="text-on-surface font-bold text-sm">{{ item.total_seats }} ghế</span>
          </div>
        </div>
        
        <div class="p-4 bg-black/40 border-t border-white/5 flex justify-end gap-2 shrink-0">
          <button @click="openEditModal(item)" class="px-4 py-2 rounded-lg font-bold text-sky-400 hover:bg-sky-400/10 transition text-sm flex items-center gap-1.5">
            <span class="material-symbols-outlined text-[18px]">edit</span> Sửa
          </button>
          <button @click="actionConfirmItem = item" class="px-4 py-2 rounded-lg font-bold text-rose-400 hover:bg-rose-400/10 transition text-sm flex items-center gap-1.5">
            <span class="material-symbols-outlined text-[18px]">delete</span> Xoá
          </button>
        </div>
      </div>
      
      <div v-if="auditoriums.length === 0 && !loading" class="col-span-full py-12 flex flex-col items-center justify-center text-on-surface-variant border-2 border-dashed border-white/10 rounded-2xl bg-black/20">
        <span class="material-symbols-outlined text-[48px] mb-3 opacity-50">meeting_room</span>
        <p>Chi nhánh hiện chưa có phòng chiếu nào.</p>
        <button @click="showCreateForm = true" class="mt-4 px-5 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg font-bold transition">Tạo phòng chiếu đầu tiên</button>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingAuditorium" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border border-white/10 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden" @click.stop>
        <div class="p-5 border-b border-white/10 flex items-center justify-between">
          <h3 class="text-lg font-bold text-on-surface">Chỉnh sửa phòng chiếu</h3>
          <button @click="closeEditModal" class="text-on-surface-variant hover:text-white transition">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên hiển thị</label>
            <input v-model="editForm.name" required class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Loại màn hình</label>
            <select v-model="editForm.screenType" class="field-input" required>
              <option value="2D">Tiêu chuẩn (2D)</option>
              <option value="3D">Màn hình 3D (3D)</option>
              <option value="IMAX">Màn hình siêu lớn (IMAX)</option>
              <option value="4DX">Phòng chiếu 4DX</option>
            </select>
          </div>
        </div>
        <div class="p-4 border-t border-white/10 bg-black/20 flex justify-end gap-3">
          <button @click="closeEditModal" class="px-5 py-2 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button @click="saveAuditoriumEdit" class="action-primary px-6">Lưu thay đổi</button>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirm Modal -->
    <div v-if="actionConfirmItem" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border border-rose-500/30 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden text-center p-6">
        <div class="w-16 h-16 bg-rose-500/20 text-rose-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="material-symbols-outlined text-[32px]">warning</span>
        </div>
        <h3 class="text-xl font-bold text-on-surface mb-2">Xoá phòng chiếu?</h3>
        <p class="text-sm text-on-surface-variant mb-6">Bạn có chắc chắn muốn xoá phòng chiếu <strong>{{ actionConfirmItem.name }}</strong> không? Thao tác này sẽ xoá luôn sơ đồ ghế của phòng này.</p>
        
        <div class="flex gap-3">
          <button @click="actionConfirmItem = null" class="flex-1 py-2.5 rounded-xl font-bold border border-white/10 text-on-surface hover:bg-white/5 transition">Hủy bỏ</button>
          <button @click="executeDelete" class="flex-1 py-2.5 rounded-xl font-bold bg-rose-600 text-white hover:bg-rose-500 transition shadow-[0_0_20px_rgba(225,29,72,0.4)]">Xoá vĩnh viễn</button>
        </div>
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

.animate-fade-in {
  animation: fadeIn 0.2s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
</style>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { adminBackendService, type AdminBranchManage } from '~/services/api'

const branches = ref<AdminBranchManage[]>([])
const loading = ref(false)
const error = ref('')

const showCreateForm = ref(false)
const creating = ref(false)
const saving = ref(false)
const search = ref('')
const statusFilter = ref<'ALL' | 'ACTIVE' | 'INACTIVE' | 'NOT_READY'>('ALL')
const cityFilter = ref('ALL')
const sortBy = ref<'NAME' | 'ROOMS_DESC'>('NAME')
const currentPage = ref(1)
const pageSize = 6

const branchForm = ref({
  code: '',
  name: '',
  addressLine: '',
  city: '',
  district: '',
  phone: '',
})

// Edit State
const editingBranch = ref<AdminBranchManage | null>(null)
const editForm = ref({
  name: '',
  city: '',
  addressLine: '',
  district: '',
  phone: '',
})

const pendingStatus = ref<AdminBranchManage | null>(null)
const cities = computed(() => [...new Set(branches.value.map(item => item.city).filter(Boolean))].sort())
const filteredBranches = computed(() => {
  const keyword = search.value.trim().toLocaleLowerCase('vi')
  const result = branches.value.filter((branch) => {
    const matchesSearch = !keyword || [branch.code, branch.name, branch.address_line, branch.city, branch.district || '']
      .some(value => value.toLocaleLowerCase('vi').includes(keyword))
    const matchesCity = cityFilter.value === 'ALL' || branch.city === cityFilter.value
    const matchesStatus = statusFilter.value === 'ALL'
      || (statusFilter.value === 'ACTIVE' && branch.is_active)
      || (statusFilter.value === 'INACTIVE' && !branch.is_active)
      || (statusFilter.value === 'NOT_READY' && !branch.is_ready)
    return matchesSearch && matchesCity && matchesStatus
  })
  return [...result].sort((a, b) => sortBy.value === 'ROOMS_DESC'
    ? b.auditoriums_count - a.auditoriums_count
    : a.name.localeCompare(b.name, 'vi'))
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredBranches.value.length / pageSize)))
const paginatedBranches = computed(() => filteredBranches.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))
watch([search, statusFilter, cityFilter, sortBy], () => { currentPage.value = 1 })
watch(totalPages, value => { if (currentPage.value > value) currentPage.value = value })

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    branches.value = await adminBackendService.getBranchesManage()
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải danh sách chi nhánh.'
  } finally {
    loading.value = false
  }
}

async function createBranch() {
  error.value = ''
  creating.value = true
  try {
    await adminBackendService.createBranch({
      code: branchForm.value.code.trim().toUpperCase(),
      name: branchForm.value.name.trim(),
      address_line: branchForm.value.addressLine.trim(),
      city: branchForm.value.city.trim(),
      district: branchForm.value.district.trim() || null,
      phone: branchForm.value.phone.trim() || null,
      is_active: true,
    })
    branchForm.value = { code: '', name: '', addressLine: '', city: '', district: '', phone: '' }
    showCreateForm.value = false
    branches.value = await adminBackendService.getBranchesManage()
  } catch (e: any) {
    error.value = e?.message || 'Không thể tạo chi nhánh.'
  } finally {
    creating.value = false
  }
}

function openEditModal(branch: AdminBranchManage) {
  editingBranch.value = branch
  editForm.value = {
    name: branch.name,
    city: branch.city,
    addressLine: branch.address_line,
    district: branch.district || '',
    phone: branch.phone || '',
  }
}

function closeEditModal() {
  editingBranch.value = null
}

async function saveBranchEdit() {
  if (!editingBranch.value) return
  error.value = ''
  try {
    await adminBackendService.updateBranch(editingBranch.value.id, {
      name: editForm.value.name.trim(),
      city: editForm.value.city.trim(),
      address_line: editForm.value.addressLine.trim(),
      district: editForm.value.district.trim() || null,
      phone: editForm.value.phone.trim() || null,
    })
    branches.value = await adminBackendService.getBranchesManage()
    closeEditModal()
  } catch (e: any) {
    error.value = e?.message || 'Không thể cập nhật thông tin chi nhánh.'
  }
}

async function confirmStatusChange() {
  const branch = pendingStatus.value
  if (!branch) return
  try {
    await adminBackendService.updateBranch(branch.id, { is_active: !branch.is_active })
    branches.value = await adminBackendService.getBranchesManage()
    pendingStatus.value = null
  } catch (e: any) {
    error.value = e?.message || 'Không thể cập nhật trạng thái chi nhánh.'
  }
}

const showDeleteConfirm = ref<AdminBranchManage | null>(null)

async function deleteBranch() {
  if (!showDeleteConfirm.value) return
  try {
    await adminBackendService.deleteBranch(showDeleteConfirm.value.id)
    branches.value = await adminBackendService.getBranchesManage()
    showDeleteConfirm.value = null
  } catch (e: any) {
    error.value = e?.message || 'Không thể xoá chi nhánh.'
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
        <h2 class="text-2xl font-black text-on-surface">Quản lý Chi nhánh</h2>
        <p class="text-sm text-on-surface-variant mt-1">Quản lý danh sách các chi nhánh rạp phim trên toàn quốc.</p>
      </div>
      <button 
        @click="showCreateForm = !showCreateForm" 
        class="action-primary flex items-center gap-2"
        :class="{'!bg-surface-variant !text-on-surface hover:!bg-white/10': showCreateForm}"
      >
        <span class="material-symbols-outlined">{{ showCreateForm ? 'close' : 'add_business' }}</span>
        {{ showCreateForm ? 'Đóng' : 'Tạo chi nhánh mới' }}
      </button>
    </div>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-400">
      {{ error }}
    </p>

    <div class="panel p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
      <input v-model="search" class="field-input md:col-span-2" placeholder="Tìm theo tên, mã hoặc địa chỉ..." />
      <select v-model="statusFilter" class="field-input">
        <option value="ALL">Tất cả trạng thái</option>
        <option value="ACTIVE">Đang mở</option>
        <option value="INACTIVE">Tạm đóng</option>
        <option value="NOT_READY">Chưa sẵn sàng bán vé</option>
      </select>
      <select v-model="cityFilter" class="field-input">
        <option value="ALL">Tất cả thành phố</option>
        <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
      </select>
      <select v-model="sortBy" class="field-input md:col-start-4">
        <option value="NAME">Sắp xếp theo tên</option>
        <option value="ROOMS_DESC">Nhiều phòng nhất</option>
      </select>
    </div>

    <!-- Create Form (Toggle) -->
    <div v-if="showCreateForm" class="panel p-6 border-primary/30 shadow-[0_0_30px_rgba(229,9,20,0.1)] animate-fade-in">
      <form class="space-y-5" @submit.prevent="createBranch">
        <h3 class="text-lg font-black text-on-surface flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">storefront</span>
          Đăng ký cụm rạp mới
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Mã chi nhánh</label>
            <input v-model="branchForm.code" required placeholder="VD: SGN01" class="field-input uppercase" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên chi nhánh</label>
            <input v-model="branchForm.name" required placeholder="VD: CineAI Vincom" class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Thành phố</label>
            <input v-model="branchForm.city" required placeholder="Hồ Chí Minh" class="field-input" />
          </div>
          <div class="space-y-1 md:col-span-2">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Địa chỉ cụ thể</label>
            <input v-model="branchForm.addressLine" required placeholder="Số nhà, Tên đường..." class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Quận / Huyện</label>
            <input v-model="branchForm.district" placeholder="Tuỳ chọn" class="field-input" />
          </div>
          <div class="space-y-1 md:col-span-3">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Số điện thoại</label>
            <input v-model="branchForm.phone" placeholder="SĐT liên hệ rạp" class="field-input" />
          </div>
        </div>
        
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" @click="showCreateForm = false" class="px-5 py-2.5 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button type="submit" class="action-primary px-8" :disabled="creating">
            {{ creating ? 'Đang tạo...' : 'Lưu chi nhánh' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Branches List -->
    <div v-if="loading" class="py-12 flex justify-center">
      <div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>
    
    <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-5">
      <div v-for="b in paginatedBranches" :key="b.id" class="panel p-0 overflow-hidden flex flex-col transition hover:border-white/20">
        <div class="p-5 flex justify-between items-start border-b border-white/5">
          <div class="flex gap-4">
            <div class="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10 shrink-0 shadow-inner">
              <span class="material-symbols-outlined text-white/60 text-[28px]">movie_filter</span>
            </div>
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/20 text-primary-container border border-primary/30 uppercase tracking-widest">{{ b.code }}</span>
                <span class="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full" :class="b.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'">
                  <span class="w-1.5 h-1.5 rounded-full" :class="b.is_active ? 'bg-emerald-400' : 'bg-rose-400'"></span>
                  {{ b.is_active ? 'Đang mở' : 'Tạm đóng' }}
                </span>
              </div>
              <h3 class="font-bold text-lg text-on-surface leading-tight">{{ b.name }}</h3>
            </div>
          </div>
          
          <button 
            @click="pendingStatus = b"
            class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
            :class="b.is_active ? 'bg-emerald-500' : 'bg-surface-variant/50'"
            :title="b.is_active ? 'Nhấn để đóng cửa rạp' : 'Nhấn để mở cửa rạp'"
          >
            <span 
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
              :class="b.is_active ? 'translate-x-5' : 'translate-x-0'"
            ></span>
          </button>
        </div>
        
        <div class="p-5 bg-black/20 flex-1 grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-xs text-on-surface-variant block mb-1">Địa điểm</span>
            <span class="text-on-surface font-medium">{{ b.city }}</span>
          </div>
          <div>
            <span class="text-xs text-on-surface-variant block mb-1">Quy mô</span>
            <span class="text-on-surface font-medium">{{ b.auditoriums_count }} phòng chiếu</span>
          </div>
          <div class="col-span-2">
            <span class="text-xs text-on-surface-variant block mb-1">Địa chỉ</span>
            <span class="text-on-surface">{{ b.address_line }}<template v-if="b.district">, {{ b.district }}</template></span>
          </div>
          <div><span class="text-xs text-on-surface-variant block mb-1">Quản trị viên</span><span class="font-medium">{{ b.active_staff_count }} người</span></div>
          <div><span class="text-xs text-on-surface-variant block mb-1">Suất chiếu sắp tới</span><span class="font-medium">{{ b.future_showtimes_count }} suất</span></div>
          <div class="col-span-2 flex items-center justify-between gap-3">
            <span v-if="b.is_ready" class="rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-bold text-emerald-300">Sẵn sàng bán vé</span>
            <span v-else class="rounded-full bg-amber-500/15 px-3 py-1 text-xs font-bold text-amber-300">Chưa sẵn sàng bán vé</span>
            <span v-if="b.phone" class="text-xs text-on-surface-variant">{{ b.phone }}</span>
          </div>
        </div>
        
        <div class="p-4 bg-black/40 border-t border-white/5 flex gap-2 justify-end">
          <button @click="openEditModal(b)" class="px-4 py-2 rounded-lg font-bold text-sky-400 hover:bg-sky-400/10 transition text-sm flex items-center gap-1.5">
            <span class="material-symbols-outlined text-[18px]">edit</span> Chỉnh sửa
          </button>
          <button 
            @click="b.can_delete ? showDeleteConfirm = b : null"
            class="px-4 py-2 rounded-lg font-bold transition text-sm flex items-center gap-1.5"
            :class="!b.can_delete ? 'text-white/20 cursor-not-allowed' : 'text-rose-400 hover:bg-rose-400/10'"
            :title="b.auditoriums_count > 0 ? 'Phải xoá phòng chiếu trước' : 'Xoá rạp này'"
          >
            <span class="material-symbols-outlined text-[18px]">delete</span> Xoá rạp
          </button>
        </div>
      </div>
      <div v-if="!paginatedBranches.length" class="panel p-10 text-center text-on-surface-variant xl:col-span-2">
        Không tìm thấy chi nhánh phù hợp với bộ lọc.
      </div>
    </div>

    <div v-if="totalPages > 1" class="flex items-center justify-between panel px-4 py-3">
      <span class="text-sm text-on-surface-variant">Trang {{ currentPage }} / {{ totalPages }} · {{ filteredBranches.length }} chi nhánh</span>
      <div class="flex gap-2">
        <button class="px-4 py-2 rounded-lg border border-white/10 disabled:opacity-30" :disabled="currentPage === 1" @click="currentPage--">Trước</button>
        <button class="px-4 py-2 rounded-lg border border-white/10 disabled:opacity-30" :disabled="currentPage === totalPages" @click="currentPage++">Sau</button>
      </div>
    </div>

    <!-- Edit Branch Modal -->
    <div v-if="editingBranch" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border border-white/10 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden" @click.stop>
        <div class="p-5 border-b border-white/10 flex items-center justify-between">
          <h3 class="text-lg font-bold text-on-surface">Cập nhật chi nhánh</h3>
          <button @click="closeEditModal" class="text-on-surface-variant hover:text-white transition">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="bg-primary/10 border border-primary/20 p-3 rounded-lg flex items-center gap-3">
            <span class="material-symbols-outlined text-primary text-[24px]">store</span>
            <div>
              <p class="text-sm font-bold text-on-surface">{{ editingBranch.name }}</p>
              <p class="text-xs text-on-surface-variant uppercase tracking-widest mt-0.5">Mã: {{ editingBranch.code }}</p>
            </div>
          </div>
          
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên chi nhánh</label>
            <input v-model="editForm.name" required class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Thành phố</label>
            <input v-model="editForm.city" required class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Địa chỉ chi tiết</label>
            <input v-model="editForm.addressLine" required class="field-input" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Quận / Huyện</label>
              <input v-model="editForm.district" class="field-input" />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Số điện thoại</label>
              <input v-model="editForm.phone" inputmode="tel" class="field-input" placeholder="0xxxxxxxxx" />
            </div>
          </div>
        </div>
        <div class="p-4 border-t border-white/10 bg-black/20 flex justify-end gap-3">
          <button @click="closeEditModal" class="px-5 py-2 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button @click="saveBranchEdit" class="action-primary px-6">Lưu thay đổi</button>
        </div>
      </div>
    </div>
    
    <div v-if="pendingStatus" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border border-white/10 rounded-2xl shadow-2xl w-full max-w-md p-6">
        <h3 class="text-xl font-bold text-on-surface mb-2">{{ pendingStatus.is_active ? 'Tạm đóng chi nhánh?' : 'Mở lại chi nhánh?' }}</h3>
        <p class="text-sm text-on-surface-variant mb-3"><strong>{{ pendingStatus.name }}</strong></p>
        <p v-if="pendingStatus.is_active && pendingStatus.future_showtimes_count" class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">
          Chi nhánh còn {{ pendingStatus.future_showtimes_count }} suất chiếu tương lai. Hệ thống sẽ từ chối đóng cho đến khi các suất này được xử lý.
        </p>
        <p v-else class="text-sm text-on-surface-variant">Thao tác này sẽ thay đổi khả năng vận hành và bán vé của chi nhánh.</p>
        <div class="flex justify-end gap-3 mt-6">
          <button class="px-5 py-2.5 rounded-xl border border-white/10" @click="pendingStatus = null">Hủy</button>
          <button class="action-primary" :disabled="saving" @click="confirmStatusChange">Xác nhận</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border border-rose-500/30 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden text-center p-6">
        <div class="w-16 h-16 bg-rose-500/20 text-rose-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="material-symbols-outlined text-[32px]">warning</span>
        </div>
        <h3 class="text-xl font-bold text-on-surface mb-2">Xoá cụm rạp?</h3>
        <p class="text-sm text-on-surface-variant mb-6">Bạn có chắc chắn muốn xoá rạp <strong>{{ showDeleteConfirm.name }}</strong> không? Hành động này không thể hoàn tác.</p>
        
        <div class="flex gap-3">
          <button @click="showDeleteConfirm = null" class="flex-1 py-2.5 rounded-xl font-bold border border-white/10 text-on-surface hover:bg-white/5 transition">Hủy bỏ</button>
          <button @click="deleteBranch" class="flex-1 py-2.5 rounded-xl font-bold bg-rose-600 text-white hover:bg-rose-500 transition shadow-[0_0_20px_rgba(225,29,72,0.4)]">Xoá vĩnh viễn</button>
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

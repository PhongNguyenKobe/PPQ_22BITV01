<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { adminBackendService, type UserProfile, type AdminBranchManage } from '~/services/api'

const users = ref<UserProfile[]>([])
const branches = ref<AdminBranchManage[]>([])
const loading = ref(false)
const error = ref('')

const showCreateForm = ref(false)
const creating = ref(false)

const userForm = ref({
  fullName: '',
  email: '',
  password: '',
  phone: '',
  roleCode: 'CUSTOMER' as 'CUSTOMER' | 'BRANCH_ADMIN' | 'STAFF' | 'SUPER_ADMIN',
  branchId: '',
})

// Edit User State
const editingUser = ref<UserProfile | null>(null)
const editForm = ref({
  roleCode: 'CUSTOMER' as 'CUSTOMER' | 'BRANCH_ADMIN' | 'STAFF' | 'SUPER_ADMIN',
  branchId: '',
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [usersData, branchesData] = await Promise.all([
      adminBackendService.getUsers(),
      adminBackendService.getBranchesManage(),
    ])
    users.value = usersData
    branches.value = branchesData
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải danh sách người dùng.'
  } finally {
    loading.value = false
  }
}

async function createUser() {
  error.value = ''
  creating.value = true
  try {
    await adminBackendService.createUser({
      full_name: userForm.value.fullName.trim(),
      email: userForm.value.email.trim(),
      password: userForm.value.password,
      phone: userForm.value.phone.trim() || null,
      role_code: userForm.value.roleCode,
      branch_id: userForm.value.branchId || null,
    })
    
    // Reset
    userForm.value = { fullName: '', email: '', password: '', phone: '', roleCode: 'CUSTOMER', branchId: '' }
    showCreateForm.value = false
    
    // Reload users
    users.value = await adminBackendService.getUsers()
  } catch (e: any) {
    const message = e?.response?.data?.detail || e?.message || ''
    error.value = message === 'EMAIL_EXISTS'
      ? 'Email này đã được sử dụng.'
      : message === 'PHONE_EXISTS'
        ? 'Số điện thoại này đã được sử dụng.'
        : message || 'Không thể tạo tài khoản.'
  } finally {
    creating.value = false
  }
}

function openEditModal(user: UserProfile) {
  editingUser.value = user
  editForm.value = {
    roleCode: roleToCode(user.role),
    branchId: user.branchId || '',
  }
}

function closeEditModal() {
  editingUser.value = null
}

async function saveUserRole() {
  if (!editingUser.value) return
  error.value = ''
  try {
    const updated = await adminBackendService.updateUserRole(
      editingUser.value.id,
      editForm.value.roleCode,
      editForm.value.branchId || null
    )
    users.value = users.value.map((u) => (u.id === updated.id ? updated : u))
    closeEditModal()
  } catch (e: any) {
    error.value = e?.message || 'Không thể cập nhật quyền.'
  }
}

async function updateUserActive(user: UserProfile) {
  try {
    const target = !user.isActive
    await adminBackendService.updateUser(user.id, { is_active: target })
    users.value = await adminBackendService.getUsers()
  } catch (e: any) {
    error.value = e?.message || 'Không thể thay đổi trạng thái.'
  }
}

const showDeleteConfirm = ref<UserProfile | null>(null)

async function softDeleteUser() {
  if (!showDeleteConfirm.value) return
  try {
    await adminBackendService.deleteUser(showDeleteConfirm.value.id)
    users.value = await adminBackendService.getUsers()
    showDeleteConfirm.value = null
  } catch (e: any) {
    error.value = e?.message || 'Không thể xoá tài khoản.'
  }
}

function resolveUserBranchName(branchId: string | null | undefined) {
  if (!branchId) return '-'
  const branch = branches.value.find(b => b.id === branchId)
  return branch ? branch.name : branchId
}

function roleToCode(role: UserProfile['role']): 'CUSTOMER' | 'BRANCH_ADMIN' | 'STAFF' | 'SUPER_ADMIN' {
  if (role === 'admin') return 'SUPER_ADMIN'
  if (role === 'branch-admin') return 'BRANCH_ADMIN'
  if (role === 'staff') return 'STAFF'
  return 'CUSTOMER'
}

function roleBadgeClass(role: UserProfile['role']) {
  if (role === 'admin') return 'bg-red-500/20 text-red-300 border-red-500/30'
  if (role === 'branch-admin') return 'bg-violet-500/20 text-violet-300 border-violet-500/30'
  if (role === 'staff') return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
  return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-on-surface">Quản lý Tài khoản</h2>
        <p class="text-sm text-on-surface-variant mt-1">Tổng số: {{ users.length }} người dùng</p>
      </div>
      <button 
        @click="showCreateForm = !showCreateForm" 
        class="action-primary flex items-center gap-2"
        :class="{'!bg-surface-variant !text-on-surface hover:!bg-white/10': showCreateForm}"
      >
        <span class="material-symbols-outlined">{{ showCreateForm ? 'close' : 'person_add' }}</span>
        {{ showCreateForm ? 'Đóng' : 'Tạo tài khoản mới' }}
      </button>
    </div>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-400">
      {{ error }}
    </p>

    <!-- Create Form (Toggle) -->
    <div v-if="showCreateForm" class="panel p-6 border-primary/30 shadow-[0_0_30px_rgba(229,9,20,0.1)] animate-fade-in">
      <form class="space-y-5" @submit.prevent="createUser">
        <h3 class="text-lg font-black text-on-surface flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">badge</span>
          Thông tin tài khoản mới
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Họ và tên</label>
            <input v-model="userForm.fullName" required placeholder="Nguyễn Văn A" class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Email</label>
            <input v-model="userForm.email" type="email" required placeholder="example@email.com" class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Mật khẩu</label>
            <input v-model="userForm.password" type="password" required placeholder="••••••••" class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Số điện thoại</label>
            <input v-model="userForm.phone" placeholder="Để trống nếu không có" class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Phân quyền</label>
            <select v-model="userForm.roleCode" class="field-input font-medium">
              <option value="CUSTOMER">Khách hàng (Customer)</option>
              <option value="STAFF">Nhân viên (Staff)</option>
              <option value="BRANCH_ADMIN">Quản lý rạp (Branch Admin)</option>
              <option value="SUPER_ADMIN">Quản trị viên (Super Admin)</option>
            </select>
          </div>
          <div class="space-y-1" v-if="userForm.roleCode === 'BRANCH_ADMIN' || userForm.roleCode === 'STAFF'">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Cụm rạp trực thuộc</label>
            <select v-model="userForm.branchId" class="field-input font-medium">
              <option value="">-- Chọn cụm rạp --</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>
        </div>
        
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" @click="showCreateForm = false" class="px-5 py-2.5 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button type="submit" class="action-primary px-8" :disabled="creating">
            {{ creating ? 'Đang tạo...' : 'Lưu tài khoản' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Users Table -->
    <div class="panel overflow-hidden">
      <div v-if="loading" class="py-12 flex justify-center">
        <div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm min-w-[900px]">
          <thead class="bg-white/5 border-b border-white/10">
            <tr class="text-left text-on-surface-variant">
              <th class="px-5 py-4 font-semibold">Người dùng</th>
              <th class="px-5 py-4 font-semibold">Quyền hạn</th>
              <th class="px-5 py-4 font-semibold">Trạng thái</th>
              <th class="px-5 py-4 font-semibold">Chi nhánh</th>
              <th class="px-5 py-4 font-semibold">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr v-for="u in users" :key="u.id" class="group hover:bg-white/[0.02] transition-colors">
              <td class="px-5 py-3">
                <div class="font-bold text-on-surface">{{ u.name }}</div>
                <div class="text-xs text-on-surface-variant">{{ u.email }}</div>
              </td>
              <td class="px-5 py-3">
                <span class="inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold" :class="roleBadgeClass(u.role)">
                  {{ u.role.toUpperCase() }}
                </span>
              </td>
              <td class="px-5 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full" :class="u.isActive ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500'"></div>
                  <span class="text-sm font-medium" :class="u.isActive ? 'text-emerald-400' : 'text-rose-400'">
                    {{ u.isActive ? 'Đang hoạt động' : 'Đã khoá' }}
                  </span>
                </div>
              </td>
              <td class="px-5 py-3 text-on-surface-variant">{{ resolveUserBranchName(u.branchId) }}</td>
              <td class="px-5 py-3">
                <div class="flex items-center gap-2 opacity-60 group-hover:opacity-100 transition-opacity">
                  <button @click="openEditModal(u)" class="p-2 rounded-lg bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 transition tooltip" title="Đổi quyền">
                    <span class="material-symbols-outlined text-[18px]">manage_accounts</span>
                  </button>
                  <button @click="updateUserActive(u)" class="p-2 rounded-lg transition tooltip" :class="u.isActive ? 'bg-amber-500/10 text-amber-400 hover:bg-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20'" :title="u.isActive ? 'Khoá tài khoản' : 'Mở khoá'">
                    <span class="material-symbols-outlined text-[18px]">{{ u.isActive ? 'lock' : 'lock_open' }}</span>
                  </button>
                  <button @click="showDeleteConfirm = u" class="p-2 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition tooltip" title="Xoá mềm">
                    <span class="material-symbols-outlined text-[18px]">delete</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Role Modal -->
    <div v-if="editingUser" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border border-white/10 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden" @click.stop>
        <div class="p-5 border-b border-white/10 flex items-center justify-between">
          <h3 class="text-lg font-bold text-on-surface">Cập nhật quyền hạn</h3>
          <button @click="closeEditModal" class="text-on-surface-variant hover:text-white transition">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="bg-black/20 p-3 rounded-lg mb-2">
            <p class="text-sm font-semibold text-on-surface">{{ editingUser.name }}</p>
            <p class="text-xs text-on-surface-variant">{{ editingUser.email }}</p>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Vai trò mới</label>
            <select v-model="editForm.roleCode" class="field-input">
              <option value="CUSTOMER">Khách hàng (Customer)</option>
              <option value="STAFF">Nhân viên (Staff)</option>
              <option value="BRANCH_ADMIN">Quản lý rạp (Branch Admin)</option>
              <option value="SUPER_ADMIN">Quản trị viên (Super Admin)</option>
            </select>
          </div>
          <div class="space-y-1" v-if="editForm.roleCode === 'BRANCH_ADMIN' || editForm.roleCode === 'STAFF'">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Cụm rạp trực thuộc</label>
            <select v-model="editForm.branchId" class="field-input">
              <option value="">-- Chọn cụm rạp --</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>
        </div>
        <div class="p-4 border-t border-white/10 bg-black/20 flex justify-end gap-3">
          <button @click="closeEditModal" class="px-5 py-2 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button @click="saveUserRole" class="action-primary px-6">Lưu thay đổi</button>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirm Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border border-rose-500/30 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden text-center p-6">
        <div class="w-16 h-16 bg-rose-500/20 text-rose-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="material-symbols-outlined text-[32px]">warning</span>
        </div>
        <h3 class="text-xl font-bold text-on-surface mb-2">Xác nhận xoá?</h3>
        <p class="text-sm text-on-surface-variant mb-6">Bạn có chắc chắn muốn xoá mềm tài khoản <strong>{{ showDeleteConfirm.email }}</strong> không? Thao tác này sẽ khoá tài khoản vô thời hạn.</p>
        
        <div class="flex gap-3">
          <button @click="showDeleteConfirm = null" class="flex-1 py-2.5 rounded-xl font-bold border border-white/10 text-on-surface hover:bg-white/5 transition">Hủy bỏ</button>
          <button @click="softDeleteUser" class="flex-1 py-2.5 rounded-xl font-bold bg-rose-600 text-white hover:bg-rose-500 transition shadow-[0_0_20px_rgba(225,29,72,0.4)]">Xoá tài khoản</button>
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
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>

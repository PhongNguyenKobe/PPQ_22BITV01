<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { adminBackendService, type UserProfile, type AdminBranchManage } from '~/services/api'
import { useUserStore } from '~/store/user'
import { storeToRefs } from 'pinia'

const { currentUser } = storeToRefs(useUserStore())

const users = ref<UserProfile[]>([])
const branches = ref<AdminBranchManage[]>([])
const loading = ref(false)
const error = ref('')
const accountGroup = ref<'ADMIN' | 'CUSTOMER'>('ADMIN')
const userSearch = ref('')
const statusFilter = ref<'ALL' | 'ACTIVE' | 'LOCKED'>('ALL')
const roleFilter = ref<'ALL' | 'admin' | 'branch-admin' | 'customer'>('ALL')
const branchFilter = ref('ALL')
const verificationFilter = ref<'ALL' | 'VERIFIED' | 'UNVERIFIED'>('ALL')
const currentPage = ref(1)
const pageSize = 10
const adminUsers = computed(() => users.value.filter(user => user.role !== 'customer'))
const customerUsers = computed(() => users.value.filter(user => user.role === 'customer'))
const activeBranches = computed(() => branches.value.filter(branch => branch.is_active))
const filteredUsers = computed(() => {
  let result = accountGroup.value === 'ADMIN' ? adminUsers.value : customerUsers.value
  const query = userSearch.value.trim().toLocaleLowerCase('vi')
  if (query) {
    result = result.filter(user =>
      user.name.toLocaleLowerCase('vi').includes(query)
      || user.email.toLocaleLowerCase('vi').includes(query)
    )
  }
  if (statusFilter.value === 'ACTIVE') result = result.filter(user => user.isActive)
  if (statusFilter.value === 'LOCKED') result = result.filter(user => !user.isActive)
  if (roleFilter.value !== 'ALL') result = result.filter(user => user.role === roleFilter.value)
  if (accountGroup.value === 'ADMIN' && branchFilter.value !== 'ALL') {
    result = result.filter(user => user.branchId === branchFilter.value)
  }
  if (accountGroup.value === 'CUSTOMER' && verificationFilter.value !== 'ALL') {
    result = result.filter(user => verificationFilter.value === 'VERIFIED' ? user.isVerified : !user.isVerified)
  }
  return result
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize)))
const paginatedUsers = computed(() => filteredUsers.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))

watch(accountGroup, () => {
  roleFilter.value = 'ALL'
  branchFilter.value = 'ALL'
  verificationFilter.value = 'ALL'
  currentPage.value = 1
})
watch([userSearch, statusFilter, roleFilter, branchFilter, verificationFilter], () => { currentPage.value = 1 })

const showCreateForm = ref(false)
const creating = ref(false)

function validateAdminPassword(password: string): string | null {
  if (password.length < 8) return 'Mật khẩu phải có ít nhất 8 ký tự.'
  if (password.length > 16) return 'Mật khẩu tối đa 16 ký tự.'
  if (/\s/.test(password)) return 'Mật khẩu không được chứa khoảng trắng.'
  if (!/[a-z]/.test(password)) return 'Mật khẩu phải có ít nhất một chữ thường.'
  if (!/[A-Z]/.test(password)) return 'Mật khẩu phải có ít nhất một chữ in hoa.'
  if (!/\d/.test(password)) return 'Mật khẩu phải có ít nhất một chữ số.'
  if (!/[^A-Za-z0-9]/.test(password)) return 'Mật khẩu phải có ít nhất một ký tự đặc biệt.'
  return null
}

const userForm = ref({
  fullName: '',
  email: '',
  password: '',
  phone: '',
  roleCode: 'BRANCH_ADMIN' as 'BRANCH_ADMIN' | 'SUPER_ADMIN',
  branchId: '',
})

// Edit User State
const editingUser = ref<UserProfile | null>(null)
const editForm = ref({
  roleCode: 'CUSTOMER' as 'CUSTOMER' | 'BRANCH_ADMIN' | 'SUPER_ADMIN',
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
  if (!userForm.value.fullName.trim()) {
    error.value = 'Vui lòng nhập họ và tên.'
    return
  }
  if (!userForm.value.email.trim()) {
    error.value = 'Vui lòng nhập email.'
    return
  }
  const passwordError = validateAdminPassword(userForm.value.password)
  if (passwordError) {
    error.value = passwordError
    return
  }
  if (
    userForm.value.roleCode === 'BRANCH_ADMIN'
    && !userForm.value.branchId
  ) {
    error.value = 'Vui lòng chọn chi nhánh phụ trách.'
    return
  }
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
    userForm.value = { fullName: '', email: '', password: '', phone: '', roleCode: 'BRANCH_ADMIN', branchId: '' }
    showCreateForm.value = false
    
    // Reload users
    users.value = await adminBackendService.getUsers()
  } catch (e: any) {
    const message = e?.message || ''
    error.value = message === 'EMAIL_EXISTS'
      ? 'Email này đã được sử dụng.'
      : message === 'PHONE_EXISTS'
        ? 'Số điện thoại này đã được sử dụng.'
        : message === 'Branch is invalid or inactive'
          ? 'Chi nhánh đã chọn không hợp lệ hoặc đang tạm đóng.'
          : message === 'Role SUPER_ADMIN is not configured' || message === 'Role BRANCH_ADMIN is not configured'
            ? 'Hệ thống chưa cấu hình vai trò quản trị. Hãy chạy seed quyền quản trị.'
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
  if (
    editForm.value.roleCode === 'BRANCH_ADMIN'
    && !editForm.value.branchId
  ) {
    error.value = 'Vui lòng chọn chi nhánh phụ trách.'
    return
  }
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

function resolveUserBranchName(branchId: string | null | undefined) {
  if (!branchId) return '-'
  const branch = branches.value.find(b => b.id === branchId)
  return branch ? branch.name : branchId
}

function roleToCode(role: UserProfile['role']): 'CUSTOMER' | 'BRANCH_ADMIN' | 'SUPER_ADMIN' {
  if (role === 'admin') return 'SUPER_ADMIN'
  if (role === 'branch-admin') return 'BRANCH_ADMIN'
  return 'CUSTOMER'
}

function roleBadgeClass(role: UserProfile['role']) {
  if (role === 'admin') return 'bg-red-500/20 text-red-300 border-red-500/30'
  if (role === 'branch-admin') return 'bg-violet-500/20 text-violet-300 border-violet-500/30'
  if (role === 'staff') return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
  return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
}

function formatCreatedAt(value?: string) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short' }).format(new Date(value))
}

const pendingAction = ref<{ type: 'STATUS'; user: UserProfile } | { type: 'ROLE' } | null>(null)

async function executeConfirmedAction() {
  const action = pendingAction.value
  pendingAction.value = null
  if (!action) return
  if (action.type === 'STATUS') await updateUserActive(action.user)
  else await saveUserRole()
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="space-y-6">
    <div class="panel flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between">
      <div>
        <h2 class="text-xl font-bold text-on-surface">Quản lý tài khoản</h2>
        <p class="text-sm text-on-surface-variant mt-1">
          {{ adminUsers.length }} tài khoản quản trị · {{ customerUsers.length }} khách hàng
        </p>
      </div>
      <button 
        @click="showCreateForm = !showCreateForm" 
        class="action-primary flex items-center gap-2"
        :class="{'!bg-surface-variant !text-on-surface hover:!bg-white/10': showCreateForm}"
      >
        <span class="material-symbols-outlined">{{ showCreateForm ? 'close' : 'person_add' }}</span>
        {{ showCreateForm ? 'Đóng' : 'Tạo tài khoản quản trị' }}
      </button>
    </div>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-400">
      {{ error }}
    </p>

    <div class="inline-flex rounded-xl border border-white/10 bg-black/20 p-1">
      <button
        class="rounded-lg px-5 py-2.5 text-sm font-bold transition"
        :class="accountGroup === 'ADMIN' ? 'bg-violet-600 text-white' : 'text-on-surface-variant hover:text-white'"
        @click="accountGroup = 'ADMIN'"
      >
        Quản trị viên ({{ adminUsers.length }})
      </button>
      <button
        class="rounded-lg px-5 py-2.5 text-sm font-bold transition"
        :class="accountGroup === 'CUSTOMER' ? 'bg-emerald-600 text-white' : 'text-on-surface-variant hover:text-white'"
        @click="accountGroup = 'CUSTOMER'"
      >
        Khách hàng ({{ customerUsers.length }})
      </button>
    </div>

    <div class="panel grid gap-3 p-4 md:grid-cols-[minmax(260px,1fr)_220px_220px]">
      <div class="relative">
        <span class="material-symbols-outlined pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-on-surface-variant">search</span>
        <input
          v-model="userSearch"
          class="field-input search-input"
          placeholder="Tìm theo tên hoặc email..."
          aria-label="Tìm người dùng theo tên hoặc email"
        />
      </div>
      <select v-model="statusFilter" class="field-input" aria-label="Lọc trạng thái tài khoản">
        <option value="ALL">Tất cả trạng thái</option>
        <option value="ACTIVE">Đang hoạt động</option>
        <option value="LOCKED">Đã khóa</option>
      </select>
      <select v-if="accountGroup === 'ADMIN'" v-model="roleFilter" class="field-input" aria-label="Lọc vai trò">
        <option value="ALL">Tất cả vai trò</option>
        <option v-if="accountGroup === 'CUSTOMER'" value="customer">Khách hàng</option>
        <template v-else>
          <option value="admin">Super Admin</option>
          <option value="branch-admin">Branch Admin</option>
        </template>
      </select>
      <select v-else v-model="verificationFilter" class="field-input" aria-label="Lọc xác thực email">
        <option value="ALL">Tất cả xác thực</option>
        <option value="VERIFIED">Đã xác thực email</option>
        <option value="UNVERIFIED">Chưa xác thực email</option>
      </select>
      <select v-if="accountGroup === 'ADMIN'" v-model="branchFilter" class="field-input md:col-start-3" aria-label="Lọc chi nhánh">
        <option value="ALL">Tất cả chi nhánh</option>
        <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </div>

    <div class="rounded-xl border border-sky-500/20 bg-sky-500/5 px-4 py-3 text-xs text-sky-200">
      <strong>Khóa tài khoản</strong> sẽ chặn người dùng đăng nhập nhưng vẫn giữ nguyên hồ sơ, vé và lịch sử giao dịch.
      Muốn đổi khách hàng thành Branch Admin, hãy tìm email, chọn <strong>Đổi quyền</strong>, sau đó chọn chi nhánh phụ trách.
    </div>

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
              <option value="BRANCH_ADMIN">Quản lý rạp (Branch Admin)</option>
              <option value="SUPER_ADMIN">Quản trị viên (Super Admin)</option>
            </select>
          </div>
          <div class="space-y-1" v-if="userForm.roleCode === 'BRANCH_ADMIN'">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Cụm rạp trực thuộc</label>
            <select v-model="userForm.branchId" required class="field-input font-medium">
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
            <tr v-for="u in paginatedUsers" :key="u.id" class="group hover:bg-white/[0.02] transition-colors">
              <td class="px-5 py-3">
                <div class="font-bold text-on-surface">{{ u.name }}</div>
                <div class="text-xs text-on-surface-variant">{{ u.email }}</div>
                <div class="mt-1 text-[11px] text-on-surface-variant">Tạo ngày {{ formatCreatedAt(u.createdAt) }}<span v-if="u.phone"> · {{ u.phone }}</span></div>
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
                <div v-if="u.role === 'customer'" class="mt-1 text-[11px]" :class="u.isVerified ? 'text-sky-300' : 'text-amber-300'">
                  {{ u.isVerified ? 'Đã xác thực email' : 'Chưa xác thực email' }}
                </div>
              </td>
              <td class="px-5 py-3 text-on-surface-variant">
                <span v-if="u.role === 'branch-admin' && !u.branchId" class="font-bold text-rose-300">Chưa phân công</span>
                <span v-else>{{ resolveUserBranchName(u.branchId) }}</span>
              </td>
              <td class="px-5 py-3">
                <div class="flex flex-wrap items-center gap-2">
                  <span v-if="u.id === currentUser?.id" class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-bold text-on-surface-variant">Tài khoản của bạn</span>
                  <button v-if="u.id !== currentUser?.id" @click="openEditModal(u)" class="inline-flex items-center gap-1.5 rounded-lg bg-sky-500/10 px-3 py-2 text-xs font-bold text-sky-300 transition hover:bg-sky-500/20" title="Đổi vai trò và chi nhánh">
                    <span class="material-symbols-outlined text-[18px]">manage_accounts</span>
                    Đổi quyền
                  </button>
                  <button v-if="u.id !== currentUser?.id" @click="pendingAction = { type: 'STATUS', user: u }" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold transition" :class="u.isActive ? 'bg-amber-500/10 text-amber-300 hover:bg-amber-500/20' : 'bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20'" :title="u.isActive ? 'Chặn tài khoản đăng nhập' : 'Cho phép tài khoản đăng nhập lại'">
                    <span class="material-symbols-outlined text-[18px]">{{ u.isActive ? 'lock' : 'lock_open' }}</span>
                    {{ u.isActive ? 'Khóa' : 'Mở khóa' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!filteredUsers.length" class="p-10 text-center text-sm text-on-surface-variant">
          Không tìm thấy tài khoản phù hợp.
        </p>
      </div>
      <div v-if="totalPages > 1" class="flex items-center justify-between border-t border-white/10 px-5 py-3 text-sm">
        <span class="text-on-surface-variant">Trang {{ currentPage }}/{{ totalPages }} · {{ filteredUsers.length }} tài khoản</span>
        <div class="flex gap-2">
          <button class="rounded-lg border border-white/10 px-3 py-1.5 disabled:opacity-30" :disabled="currentPage === 1" @click="currentPage--">Trước</button>
          <button class="rounded-lg border border-white/10 px-3 py-1.5 disabled:opacity-30" :disabled="currentPage === totalPages" @click="currentPage++">Sau</button>
        </div>
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
              <option value="BRANCH_ADMIN">Quản lý rạp (Branch Admin)</option>
              <option value="SUPER_ADMIN">Quản trị viên (Super Admin)</option>
            </select>
          </div>
          <div class="space-y-1" v-if="editForm.roleCode === 'BRANCH_ADMIN'">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Cụm rạp trực thuộc</label>
            <select v-model="editForm.branchId" required class="field-input">
              <option value="">-- Chọn cụm rạp --</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>
        </div>
        <div class="p-4 border-t border-white/10 bg-black/20 flex justify-end gap-3">
          <button @click="closeEditModal" class="px-5 py-2 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button @click="pendingAction = { type: 'ROLE' }" class="action-primary px-6">Lưu thay đổi</button>
        </div>
      </div>
    </div>

    <div v-if="pendingAction" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div class="w-full max-w-md rounded-2xl border border-amber-500/30 bg-[#1a1c1c] p-6 shadow-2xl">
        <h3 class="text-lg font-black text-white">Xác nhận thay đổi tài khoản</h3>
        <p class="mt-3 text-sm leading-relaxed text-on-surface-variant">
          <template v-if="pendingAction.type === 'STATUS'">
            {{ pendingAction.user.isActive ? 'Khóa' : 'Mở khóa' }} tài khoản <strong class="text-white">{{ pendingAction.user.email }}</strong>?
            Hồ sơ, vé và lịch sử giao dịch vẫn được giữ nguyên.
          </template>
          <template v-else>
            Xác nhận đổi quyền của <strong class="text-white">{{ editingUser?.email }}</strong>.
            Quyền truy cập và phân công chi nhánh cũ sẽ được cập nhật ngay.
          </template>
        </p>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="pendingAction = null" class="rounded-xl px-5 py-2.5 font-bold text-on-surface-variant hover:bg-white/5">Hủy</button>
          <button @click="executeConfirmedAction" class="action-primary px-6">Xác nhận</button>
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

.field-input.search-input {
  padding-left: 2.55rem;
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

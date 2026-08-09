<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { adminBackendService, branchesService, movieService, type BackendBranch, type Movie, type Promotion } from '~/services/api'
import { formatDate } from '~/utils/date'

const promotions = ref<Promotion[]>([])
const branches = ref<BackendBranch[]>([])
const movies = ref<Movie[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const showForm = ref(false)
const showAdvanced = ref(false)
const editing = ref<Promotion | null>(null)
const pendingToggle = ref<Promotion | null>(null)
const search = ref('')
const statusFilter = ref('ALL')
const typeFilter = ref('ALL')
const currentPage = ref(1)
const pageSize = 9

function localDate(value: Date) {
  const offset = value.getTimezoneOffset()
  return new Date(value.getTime() - offset * 60_000).toISOString().slice(0, 16)
}
function emptyForm() {
  return {
    code: '', name: '', discount_type: 'PERCENT' as 'PERCENT' | 'FIXED', discount_value: 10,
    max_discount: null as number | null, min_order_amount: 0,
    starts_at: localDate(new Date()), ends_at: localDate(new Date(Date.now() + 30 * 86_400_000)),
    usage_limit: null as number | null, per_user_limit: 1 as number | null,
    budget_amount: null as number | null, branch_ids: [] as string[], movie_ids: [] as string[],
    payment_methods: [] as string[], excluded_dates_text: '', is_active: true,
  }
}
const form = ref(emptyForm())

function promoStatus(item: Promotion) {
  const now = Date.now()
  if (!item.is_active) return 'PAUSED'
  if (new Date(item.starts_at).getTime() > now) return 'UPCOMING'
  if (new Date(item.ends_at).getTime() < now) return 'EXPIRED'
  if (item.usage_limit !== null && item.used_count >= item.usage_limit) return 'EXHAUSTED'
  if (item.budget_amount !== null && Number(item.used_amount) >= Number(item.budget_amount)) return 'EXHAUSTED'
  return 'ACTIVE'
}
function statusLabel(status: string) {
  return ({ ACTIVE: 'Đang áp dụng', UPCOMING: 'Sắp diễn ra', PAUSED: 'Tạm dừng', EXPIRED: 'Đã hết hạn', EXHAUSTED: 'Đã hết lượt/ngân sách' } as Record<string, string>)[status]
}
function statusClass(status: string) {
  if (status === 'ACTIVE') return 'bg-emerald-500/15 text-emerald-300'
  if (status === 'UPCOMING') return 'bg-sky-500/15 text-sky-300'
  if (status === 'PAUSED') return 'bg-amber-500/15 text-amber-300'
  return 'bg-rose-500/15 text-rose-300'
}

const kpis = computed(() => ({
  total: promotions.value.length,
  active: promotions.value.filter(item => promoStatus(item) === 'ACTIVE').length,
  upcoming: promotions.value.filter(item => promoStatus(item) === 'UPCOMING').length,
  expired: promotions.value.filter(item => ['EXPIRED', 'EXHAUSTED'].includes(promoStatus(item))).length,
  used: promotions.value.reduce((sum, item) => sum + item.used_count, 0),
  amount: promotions.value.reduce((sum, item) => sum + Number(item.used_amount || 0), 0),
}))
const filtered = computed(() => promotions.value.filter((item) => {
  const keyword = search.value.trim().toLocaleLowerCase('vi')
  return (!keyword || [item.code, item.name].some(value => value.toLocaleLowerCase('vi').includes(keyword)))
    && (statusFilter.value === 'ALL' || promoStatus(item) === statusFilter.value)
    && (typeFilter.value === 'ALL' || item.discount_type === typeFilter.value)
}))
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))
const visible = computed(() => filtered.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))
watch([search, statusFilter, typeFilter], () => { currentPage.value = 1 })

function branchNames(ids: string[]) {
  if (!ids.length) return 'Toàn hệ thống'
  return ids.map(id => branches.value.find(item => item.id === id)?.name || id).join(', ')
}
function movieNames(ids: string[]) {
  if (!ids.length) return 'Tất cả phim'
  return ids.map(id => movies.value.find(item => item.id === id)?.title || id).join(', ')
}
function openCreate() { editing.value = null; form.value = emptyForm(); showAdvanced.value = false; showForm.value = true }
function openEdit(item: Promotion) {
  editing.value = item
  form.value = {
    code: item.code, name: item.name, discount_type: item.discount_type, discount_value: Number(item.discount_value),
    max_discount: item.max_discount === null ? null : Number(item.max_discount), min_order_amount: Number(item.min_order_amount),
    starts_at: localDate(new Date(item.starts_at)), ends_at: localDate(new Date(item.ends_at)),
    usage_limit: item.usage_limit, per_user_limit: item.per_user_limit, budget_amount: item.budget_amount,
    branch_ids: [...item.branch_ids], movie_ids: [...item.movie_ids], payment_methods: [...item.payment_methods],
    excluded_dates_text: item.excluded_dates.join(', '), is_active: item.is_active,
  }
  showAdvanced.value = true
  showForm.value = true
}
function payload() {
  return {
    ...form.value,
    code: form.value.code.trim().toUpperCase(), name: form.value.name.trim(),
    starts_at: new Date(form.value.starts_at).toISOString(), ends_at: new Date(form.value.ends_at).toISOString(),
    excluded_dates: form.value.excluded_dates_text.split(',').map(value => value.trim()).filter(Boolean),
    excluded_dates_text: undefined,
  }
}
async function save() {
  error.value = ''
  if (new Date(form.value.ends_at) <= new Date(form.value.starts_at)) { error.value = 'Thời gian kết thúc phải sau thời gian bắt đầu.'; return }
  saving.value = true
  try {
    if (editing.value) {
      const data = payload()
      delete (data as any).code
      await adminBackendService.updatePromotion(editing.value.id, data as any)
    } else await adminBackendService.createPromotion(payload())
    showForm.value = false
    await loadData()
  } catch (e: any) { error.value = e?.message || 'Không thể lưu khuyến mãi.' }
  finally { saving.value = false }
}
async function confirmToggle() {
  if (!pendingToggle.value) return
  saving.value = true
  try {
    await adminBackendService.updatePromotion(pendingToggle.value.id, { is_active: !pendingToggle.value.is_active })
    pendingToggle.value = null
    await loadData()
  } catch (e: any) { error.value = e?.message || 'Không thể cập nhật khuyến mãi.' }
  finally { saving.value = false }
}
async function loadData() {
  loading.value = true
  try { promotions.value = await adminBackendService.getPromotions() }
  catch (e: any) { error.value = e?.message || 'Không thể tải danh sách khuyến mãi.' }
  finally { loading.value = false }
}
onMounted(async () => {
  const [branchData, movieData] = await Promise.all([branchesService.getAll(), movieService.getAll()])
  branches.value = branchData
  movies.value = movieData
  await loadData()
})
</script>

<template>
  <div class="space-y-5">
    <header class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div><h2 class="text-2xl font-black">Quản lý Khuyến mãi</h2><p class="text-sm text-gray-400">Thiết lập voucher, phạm vi áp dụng và theo dõi ngân sách.</p></div>
      <button class="action-primary" @click="openCreate"><span class="material-symbols-outlined">add</span>Tạo khuyến mãi</button>
    </header>
    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300">{{ error }}</p>

    <section class="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
      <div class="metric"><span>Tổng chương trình</span><strong>{{ kpis.total }}</strong></div><div class="metric"><span>Đang áp dụng</span><strong class="text-emerald-300">{{ kpis.active }}</strong></div><div class="metric"><span>Sắp diễn ra</span><strong class="text-sky-300">{{ kpis.upcoming }}</strong></div><div class="metric"><span>Đã kết thúc</span><strong class="text-rose-300">{{ kpis.expired }}</strong></div><div class="metric"><span>Lượt sử dụng</span><strong>{{ kpis.used }}</strong></div><div class="metric"><span>Tổng tiền đã giảm</span><strong class="text-emerald-300 text-base">{{ kpis.amount.toLocaleString('vi-VN') }}đ</strong></div>
    </section>

    <section class="panel grid grid-cols-1 gap-3 p-4 md:grid-cols-4">
      <input v-model="search" class="field-input md:col-span-2" placeholder="Tìm mã hoặc tên chương trình..." />
      <select v-model="statusFilter" class="field-input"><option value="ALL">Tất cả trạng thái</option><option value="ACTIVE">Đang áp dụng</option><option value="UPCOMING">Sắp diễn ra</option><option value="PAUSED">Tạm dừng</option><option value="EXPIRED">Đã hết hạn</option><option value="EXHAUSTED">Hết lượt/ngân sách</option></select>
      <select v-model="typeFilter" class="field-input"><option value="ALL">Tất cả loại giảm</option><option value="PERCENT">Theo phần trăm</option><option value="FIXED">Số tiền cố định</option></select>
    </section>

    <div v-if="loading" class="panel p-16 text-center text-gray-400">Đang tải khuyến mãi...</div>
    <section v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
      <article v-for="item in visible" :key="item.id" class="panel p-5">
        <div class="flex items-start justify-between gap-3"><div><span class="rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-1 font-mono font-black text-red-300">{{ item.code }}</span><h3 class="mt-3 font-black">{{ item.name }}</h3></div><span class="rounded-full px-2.5 py-1 text-xs font-bold" :class="statusClass(promoStatus(item))">{{ statusLabel(promoStatus(item)) }}</span></div>
        <div class="mt-4 grid grid-cols-2 gap-2 text-sm"><div class="detail"><span>Mức giảm</span><strong>{{ item.discount_type === 'PERCENT' ? `${item.discount_value}%` : `${Number(item.discount_value).toLocaleString('vi-VN')}đ` }}</strong></div><div class="detail"><span>Giảm tối đa</span><strong>{{ item.max_discount ? `${Number(item.max_discount).toLocaleString('vi-VN')}đ` : 'Không giới hạn' }}</strong></div><div class="detail"><span>Đơn tối thiểu</span><strong>{{ Number(item.min_order_amount).toLocaleString('vi-VN') }}đ</strong></div><div class="detail"><span>Mỗi khách hàng</span><strong>{{ item.per_user_limit ?? 'Không giới hạn' }} lượt</strong></div></div>
        <div class="mt-3 rounded-xl bg-black/20 p-3 text-xs text-gray-400"><p><strong class="text-gray-200">Chi nhánh:</strong> {{ branchNames(item.branch_ids) }}</p><p class="mt-1 truncate" :title="movieNames(item.movie_ids)"><strong class="text-gray-200">Phim:</strong> {{ movieNames(item.movie_ids) }}</p><p class="mt-1"><strong class="text-gray-200">Thanh toán:</strong> {{ item.payment_methods.length ? item.payment_methods.join(', ') : 'Tất cả' }}</p></div>
        <div class="mt-3"><div class="flex justify-between text-xs text-gray-400"><span>Đã dùng {{ item.used_count }}{{ item.usage_limit ? `/${item.usage_limit}` : '' }} lượt</span><span>{{ item.usage_limit ? `${Math.min(100, Math.round(item.used_count / item.usage_limit * 100))}%` : 'Không giới hạn' }}</span></div><div v-if="item.usage_limit" class="mt-1 h-1.5 rounded bg-white/10"><div class="h-full rounded bg-red-400" :style="{width:`${Math.min(100,item.used_count/item.usage_limit*100)}%`}"></div></div></div>
        <div v-if="item.budget_amount" class="mt-3 text-xs text-gray-400">Ngân sách: {{ Number(item.used_amount).toLocaleString('vi-VN') }}/{{ Number(item.budget_amount).toLocaleString('vi-VN') }}đ</div>
        <div class="mt-4 flex justify-between border-t border-white/10 pt-3 text-xs text-gray-500"><span>{{ formatDate(item.starts_at) }}</span><span>{{ formatDate(item.ends_at) }}</span></div>
        <div class="mt-4 flex justify-end gap-2"><button class="secondary" @click="openEdit(item)">Chỉnh sửa</button><button class="secondary" :class="item.is_active ? '!text-amber-300' : '!text-emerald-300'" @click="pendingToggle=item">{{ item.is_active ? 'Tạm dừng' : 'Kích hoạt' }}</button></div>
      </article>
      <div v-if="!visible.length" class="panel p-16 text-center text-gray-400 lg:col-span-2 xl:col-span-3">Không có khuyến mãi phù hợp.</div>
    </section>

    <div v-if="totalPages>1" class="panel flex items-center justify-between p-3"><span class="text-sm text-gray-400">Trang {{ currentPage }}/{{ totalPages }}</span><div class="flex gap-2"><button class="secondary" :disabled="currentPage===1" @click="currentPage--">Trước</button><button class="secondary" :disabled="currentPage===totalPages" @click="currentPage++">Sau</button></div></div>

    <div v-if="showForm" class="modal"><form class="panel max-h-[90vh] w-full max-w-4xl overflow-y-auto p-6" @submit.prevent="save"><div class="flex justify-between"><div><h3 class="text-xl font-black">{{ editing ? 'Chỉnh sửa khuyến mãi' : 'Tạo khuyến mãi' }}</h3><p v-if="editing?.used_count" class="text-xs text-amber-300">Đã có lượt dùng: không thể đổi loại hoặc giá trị giảm.</p></div><button type="button" @click="showForm=false">✕</button></div>
      <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2"><label>Mã voucher<input v-model="form.code" class="field-input mt-1 uppercase" required :disabled="!!editing" /></label><label>Tên chương trình<input v-model="form.name" class="field-input mt-1" required /></label><label>Loại giảm<select v-model="form.discount_type" class="field-input mt-1" :disabled="!!editing?.used_count"><option value="PERCENT">Phần trăm</option><option value="FIXED">Số tiền</option></select></label><label>Mức giảm<input v-model.number="form.discount_value" type="number" min="1" :max="form.discount_type==='PERCENT'?100:undefined" class="field-input mt-1" required :disabled="!!editing?.used_count" /></label><label>Đơn tối thiểu<input v-model.number="form.min_order_amount" type="number" min="0" class="field-input mt-1" /></label><label>Giảm tối đa<input v-model.number="form.max_discount" type="number" min="1" class="field-input mt-1" placeholder="Để trống nếu không giới hạn" /></label><label>Bắt đầu<input v-model="form.starts_at" type="datetime-local" class="field-input mt-1" required /></label><label>Kết thúc<input v-model="form.ends_at" type="datetime-local" class="field-input mt-1" required /></label><label>Tổng lượt dùng<input v-model.number="form.usage_limit" type="number" min="1" class="field-input mt-1" placeholder="Để trống nếu không giới hạn" /></label><label>Mỗi khách hàng<input v-model.number="form.per_user_limit" type="number" min="1" class="field-input mt-1" placeholder="Để trống nếu không giới hạn" /></label></div>
      <button type="button" class="mt-5 font-bold text-sky-300" @click="showAdvanced=!showAdvanced">{{ showAdvanced?'Ẩn':'Hiện' }} điều kiện nâng cao</button>
      <div v-if="showAdvanced" class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2"><label>Ngân sách tối đa<input v-model.number="form.budget_amount" type="number" min="1" class="field-input mt-1" placeholder="VNĐ" /></label><label>Ngày không áp dụng<input v-model="form.excluded_dates_text" class="field-input mt-1" placeholder="2026-09-02, 2026-12-24" /></label><fieldset class="box"><legend>Chi nhánh (bỏ trống = toàn hệ thống)</legend><label v-for="branch in branches" :key="branch.id" class="check"><input v-model="form.branch_ids" type="checkbox" :value="branch.id" />{{ branch.name }}</label></fieldset><fieldset class="box max-h-44 overflow-y-auto"><legend>Phim (bỏ trống = tất cả)</legend><label v-for="movie in movies" :key="movie.id" class="check"><input v-model="form.movie_ids" type="checkbox" :value="movie.id" />{{ movie.title }}</label></fieldset><fieldset class="box md:col-span-2"><legend>Phương thức thanh toán</legend><label class="check"><input v-model="form.payment_methods" type="checkbox" value="VNPAY" />VNPAY</label><label class="check"><input v-model="form.payment_methods" type="checkbox" value="PAYPAL" />PayPal</label></fieldset></div>
      <div class="mt-6 flex justify-end gap-3"><button type="button" class="secondary" @click="showForm=false">Hủy</button><button class="action-primary" :disabled="saving">{{ saving?'Đang lưu...':'Lưu khuyến mãi' }}</button></div></form></div>

    <div v-if="pendingToggle" class="modal"><div class="panel w-full max-w-md p-6"><h3 class="text-xl font-black">{{ pendingToggle.is_active?'Tạm dừng':'Kích hoạt' }} voucher?</h3><p class="mt-2 text-gray-400">{{ pendingToggle.code }} · {{ pendingToggle.name }}</p><p class="mt-3 text-sm text-amber-200">Thay đổi có hiệu lực ngay với khách đang ở bước thanh toán.</p><div class="mt-6 flex justify-end gap-3"><button class="secondary" @click="pendingToggle=null">Hủy</button><button class="action-primary" :disabled="saving" @click="confirmToggle">Xác nhận</button></div></div></div>
  </div>
</template>

<style scoped>
.panel{background:#1a1c1c;border:1px solid rgba(255,255,255,.09);border-radius:1rem}.metric{min-height:92px;padding:1rem;background:#1a1c1c;border:1px solid rgba(255,255,255,.09);border-radius:1rem}.metric span,.detail span{display:block;color:#9ca3af;font-size:.7rem;text-transform:uppercase}.metric strong{display:block;margin-top:.5rem;font-size:1.35rem}.detail{padding:.7rem;background:rgba(0,0,0,.2);border-radius:.7rem}.detail strong{display:block;margin-top:.25rem}.field-input{width:100%;min-height:42px;border:1px solid rgba(255,255,255,.12);border-radius:.7rem;background:#202222;padding:.6rem .75rem;color:white}.action-primary{display:inline-flex;align-items:center;gap:.4rem;border-radius:.75rem;background:#e50914;padding:.65rem 1rem;font-weight:800}.secondary{border:1px solid rgba(255,255,255,.1);border-radius:.65rem;padding:.5rem .8rem;color:#7dd3fc;font-weight:700}.secondary:disabled{opacity:.3}.modal{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;padding:1rem;background:rgba(0,0,0,.72);backdrop-filter:blur(5px)}.box{border:1px solid rgba(255,255,255,.1);border-radius:.75rem;padding:.8rem}.box legend{padding:0 .3rem;color:#9ca3af;font-size:.75rem}.check{display:flex;align-items:center;gap:.5rem;padding:.25rem;font-size:.85rem}
</style>

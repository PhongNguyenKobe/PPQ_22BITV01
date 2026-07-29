<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminBackendService, type Promotion } from '~/services/api'

const promotions = ref<Promotion[]>([])
const loading = ref(false)
const error = ref('')

const showCreateForm = ref(false)
const creating = ref(false)

const promotionForm = ref({
  code: '',
  name: '',
  discount_type: 'PERCENT' as 'PERCENT' | 'FIXED',
  discount_value: 10,
  max_discount: null as number | null,
  min_order_amount: 0,
  starts_at: toDateTimeLocal(new Date()),
  ends_at: toDateTimeLocal(new Date(Date.now() + 30 * 86_400_000)),
  usage_limit: null as number | null,
  is_active: true,
})

function toDateTimeLocal(value: Date) {
  const offset = value.getTimezoneOffset()
  return new Date(value.getTime() - offset * 60_000).toISOString().slice(0, 16)
}

function toIso(value: string) {
  const date = new Date(value)
  return date.toISOString()
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    promotions.value = await adminBackendService.getPromotions()
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải danh sách khuyến mãi.'
  } finally {
    loading.value = false
  }
}

async function createPromotion() {
  error.value = ''
  creating.value = true
  try {
    const created = await adminBackendService.createPromotion({
      ...promotionForm.value,
      code: promotionForm.value.code.trim().toUpperCase(),
      starts_at: toIso(promotionForm.value.starts_at),
      ends_at: toIso(promotionForm.value.ends_at),
    })
    promotions.value.unshift(created)
    
    // Reset form and hide
    promotionForm.value.code = ''
    promotionForm.value.name = ''
    showCreateForm.value = false
  } catch (e: any) {
    error.value = e?.message || 'Không thể tạo khuyến mãi.'
  } finally {
    creating.value = false
  }
}

async function togglePromotion(item: Promotion) {
  try {
    const updated = await adminBackendService.updatePromotion(item.id, { is_active: !item.is_active })
    promotions.value = promotions.value.map((current) => current.id === updated.id ? updated : current)
  } catch (e: any) {
    error.value = e?.message || 'Không thể cập nhật khuyến mãi.'
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
        <h2 class="text-xl font-bold text-on-surface">Quản lý Khuyến mãi</h2>
        <p class="text-sm text-on-surface-variant mt-1">Tạo và quản lý các mã giảm giá cho khách hàng.</p>
      </div>
      <button 
        @click="showCreateForm = !showCreateForm" 
        class="action-primary flex items-center gap-2"
        :class="{'!bg-surface-variant !text-on-surface hover:!bg-white/10': showCreateForm}"
      >
        <span class="material-symbols-outlined">{{ showCreateForm ? 'close' : 'add' }}</span>
        {{ showCreateForm ? 'Đóng' : 'Tạo khuyến mãi mới' }}
      </button>
    </div>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-400">
      {{ error }}
    </p>

    <!-- Create Form (Toggle) -->
    <div v-if="showCreateForm" class="panel p-6 border-primary/30 shadow-[0_0_30px_rgba(229,9,20,0.1)] animate-fade-in">
      <form class="space-y-5" @submit.prevent="createPromotion">
        <h3 class="text-lg font-black text-on-surface flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">local_offer</span>
          Thiết lập mã khuyến mãi mới
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Mã voucher</label>
            <input v-model="promotionForm.code" required placeholder="VD: TET2024" class="field-input uppercase" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên chương trình</label>
            <input v-model="promotionForm.name" required placeholder="Khuyến mãi Tết" class="field-input" />
          </div>
          
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Loại giảm giá</label>
            <select v-model="promotionForm.discount_type" class="field-input">
              <option value="PERCENT">Giảm theo %</option>
              <option value="FIXED">Giảm số tiền cố định (VNĐ)</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Mức giảm</label>
            <input v-model.number="promotionForm.discount_value" required min="1" type="number" placeholder="Ví dụ: 10 hoặc 50000" class="field-input" />
          </div>

          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Đơn tối thiểu (VNĐ)</label>
            <input v-model.number="promotionForm.min_order_amount" min="0" type="number" placeholder="Ví dụ: 100000" class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Giảm tối đa (VNĐ)</label>
            <input v-model.number="promotionForm.max_discount" min="1" type="number" placeholder="Để trống nếu không giới hạn" class="field-input" />
          </div>

          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Thời gian bắt đầu</label>
            <input v-model="promotionForm.starts_at" required type="datetime-local" class="field-input" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Thời gian kết thúc</label>
            <input v-model="promotionForm.ends_at" required type="datetime-local" class="field-input" />
          </div>

          <div class="space-y-1 md:col-span-2">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Giới hạn lượt dùng</label>
            <input v-model.number="promotionForm.usage_limit" min="0" type="number" placeholder="Để trống nếu không giới hạn" class="field-input" />
          </div>
        </div>
        
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" @click="showCreateForm = false" class="px-5 py-2.5 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button type="submit" class="action-primary px-8" :disabled="creating">
            {{ creating ? 'Đang tạo...' : 'Lưu voucher' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-12 flex justify-center">
      <div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Promotions Grid -->
    <div v-else-if="promotions.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <div v-for="item in promotions" :key="item.id" class="panel p-5 relative overflow-hidden group transition hover:-translate-y-1 hover:border-primary/50">
        <!-- Decoration -->
        <div class="absolute -right-6 -top-6 w-24 h-24 bg-primary/10 rounded-full blur-2xl group-hover:bg-primary/20 transition duration-500"></div>
        
        <div class="relative z-10 flex flex-col h-full">
          <div class="flex justify-between items-start mb-4">
            <div>
              <div class="inline-flex items-center gap-1.5 bg-primary/20 text-primary-container px-3 py-1 rounded-lg border border-primary/30 font-mono font-black text-lg tracking-wider">
                <span class="material-symbols-outlined text-sm">confirmation_number</span>
                {{ item.code }}
              </div>
              <h3 class="font-bold text-on-surface mt-2 text-base line-clamp-1" :title="item.name">{{ item.name }}</h3>
            </div>
            
            <!-- Toggle Switch -->
            <button 
              @click="togglePromotion(item)"
              class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
              :class="item.is_active ? 'bg-primary' : 'bg-surface-variant/50'"
              :title="item.is_active ? 'Nhấn để tạm dừng' : 'Nhấn để kích hoạt'"
            >
              <span 
                class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                :class="item.is_active ? 'translate-x-5' : 'translate-x-0'"
              ></span>
            </button>
          </div>

          <div class="space-y-3 flex-1">
            <!-- Promo Details -->
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="bg-black/20 p-2.5 rounded-lg border border-white/5">
                <span class="text-on-surface-variant block mb-1">Mức giảm</span>
                <strong class="text-emerald-400 text-sm">
                  {{ item.discount_type === 'PERCENT' ? `${item.discount_value}%` : `${Number(item.discount_value).toLocaleString('vi-VN')}đ` }}
                </strong>
              </div>
              <div class="bg-black/20 p-2.5 rounded-lg border border-white/5">
                <span class="text-on-surface-variant block mb-1">Đơn tối thiểu</span>
                <strong class="text-white text-sm">{{ Number(item.min_order_amount).toLocaleString('vi-VN') }}đ</strong>
              </div>
            </div>

            <!-- Usage Progress -->
            <div class="bg-black/20 p-3 rounded-lg border border-white/5 mt-auto">
              <div class="flex justify-between items-center text-xs mb-1.5">
                <span class="text-on-surface-variant">Đã dùng: <strong class="text-white">{{ item.used_count }}</strong></span>
                <span class="text-on-surface-variant">Tổng: <strong class="text-white">{{ item.usage_limit ?? '∞' }}</strong></span>
              </div>
              <div class="w-full bg-surface-variant/30 rounded-full h-1.5 overflow-hidden">
                <div 
                  class="bg-gradient-to-r from-primary to-orange-400 h-1.5 rounded-full"
                  :style="{ width: item.usage_limit ? `${Math.min((item.used_count / item.usage_limit) * 100, 100)}%` : '100%' }"
                  :class="{'opacity-50': !item.usage_limit}"
                ></div>
              </div>
            </div>
            
            <div class="text-[11px] text-on-surface-variant flex items-center justify-between pt-2 border-t border-white/10">
              <span class="truncate">Từ: {{ new Date(item.starts_at).toLocaleDateString('vi-VN') }}</span>
              <span class="truncate text-right">Đến: {{ new Date(item.ends_at).toLocaleDateString('vi-VN') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="py-16 text-center text-on-surface-variant">
      <span class="material-symbols-outlined text-[48px] mb-2 opacity-50">local_offer</span>
      <p class="font-medium">Chưa có mã khuyến mãi nào.</p>
      <button @click="showCreateForm = true" class="text-primary mt-2 font-bold hover:underline">Tạo ngay</button>
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
  animation: fadeInDown 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

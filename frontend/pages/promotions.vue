<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { promotionsService, type Promotion } from '~/services/api'

definePageMeta({ layout: 'default' })

const promotions = ref<Promotion[]>([])
const loading = ref(true)
const error = ref('')
const copiedCode = ref('')
const now = ref(Date.now())

const currentPromotions = computed(() => promotions.value.filter(item =>
  new Date(item.starts_at).getTime() <= now.value
  && new Date(item.ends_at).getTime() >= now.value
  && (item.usage_limit === null || item.used_count < item.usage_limit)
))
const upcomingPromotions = computed(() => promotions.value.filter(item =>
  new Date(item.starts_at).getTime() > now.value
))

function money(value: number | null) {
  return Number(value || 0).toLocaleString('vi-VN') + 'đ'
}

function discountLabel(item: Promotion) {
  return item.discount_type === 'PERCENT'
    ? `Giảm ${Number(item.discount_value)}%`
    : `Giảm ${money(item.discount_value)}`
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  }).format(new Date(value))
}

function remaining(item: Promotion) {
  return item.usage_limit === null ? null : Math.max(0, item.usage_limit - item.used_count)
}

async function copyCode(code: string) {
  await navigator.clipboard.writeText(code)
  copiedCode.value = code
  window.setTimeout(() => {
    if (copiedCode.value === code) copiedCode.value = ''
  }, 1800)
}

async function loadPromotions() {
  loading.value = true
  error.value = ''
  try {
    promotions.value = await promotionsService.getPublicPromotions()
    now.value = Date.now()
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải chương trình khuyến mãi.'
  } finally {
    loading.value = false
  }
}

onMounted(loadPromotions)
</script>

<template>
  <main class="min-h-[75vh] bg-[#0f1111] px-5 py-10 md:px-10 md:py-14">
    <div class="mx-auto max-w-6xl">
      <section class="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-red-950/60 via-[#1a1c1c] to-[#151717] px-6 py-10 md:px-12 md:py-14">
        <div class="absolute -right-16 -top-24 h-72 w-72 rounded-full bg-red-600/20 blur-3xl"></div>
        <div class="relative max-w-2xl">
          <div class="mb-4 inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-xs font-black uppercase tracking-[0.18em] text-red-300">
            <span class="material-symbols-outlined text-base">local_offer</span>
            Ưu đãi đang áp dụng
          </div>
          <h1 class="text-3xl font-black leading-tight text-white md:text-5xl">Xem phim hay, giá vé tốt hơn</h1>
          <p class="mt-4 max-w-xl text-sm leading-6 text-gray-300 md:text-base">Các voucher bên dưới được cập nhật trực tiếp từ hệ thống CineAI. Sao chép mã và áp dụng tại bước thanh toán.</p>
          <div class="mt-7 flex flex-wrap gap-3">
            <div class="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
              <strong class="block text-2xl text-white">{{ currentPromotions.length }}</strong>
              <span class="text-xs text-gray-400">ưu đãi có thể dùng</span>
            </div>
            <div class="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
              <strong class="block text-2xl text-white">{{ upcomingPromotions.length }}</strong>
              <span class="text-xs text-gray-400">ưu đãi sắp diễn ra</span>
            </div>
          </div>
        </div>
      </section>

      <div v-if="loading" class="py-24 text-center text-gray-400">
        <span class="material-symbols-outlined animate-spin text-4xl text-red-500">progress_activity</span>
        <p class="mt-3">Đang tải ưu đãi từ hệ thống...</p>
      </div>

      <div v-else-if="error" class="my-8 rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-red-300">
        {{ error }}
        <button class="ml-2 font-bold underline" @click="loadPromotions">Thử lại</button>
      </div>

      <template v-else>
        <section class="mt-10">
          <div class="mb-5 flex items-end justify-between gap-4">
            <div>
              <p class="text-xs font-black uppercase tracking-[0.18em] text-red-400">Dùng ngay</p>
              <h2 class="mt-1 text-2xl font-black text-white">Khuyến mãi hiện có</h2>
            </div>
            <NuxtLink to="/products" class="hidden text-sm font-bold text-red-400 hover:text-red-300 sm:block">Chọn phim →</NuxtLink>
          </div>

          <div v-if="currentPromotions.length" class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            <article v-for="item in currentPromotions" :key="item.id" class="group flex min-h-[290px] flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#1a1c1c] shadow-xl transition hover:-translate-y-1 hover:border-red-500/40">
              <div class="h-1.5 bg-gradient-to-r from-red-600 via-orange-500 to-amber-400"></div>
              <div class="flex flex-1 flex-col p-6">
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-gray-400">CineAI Voucher</span>
                    <h3 class="mt-1 text-xl font-black text-white">{{ item.name }}</h3>
                  </div>
                  <span class="material-symbols-outlined rounded-xl bg-red-500/10 p-2 text-3xl text-red-500">confirmation_number</span>
                </div>

                <p class="mt-5 text-2xl font-black text-emerald-400">{{ discountLabel(item) }}</p>
                <div class="mt-3 space-y-1.5 text-sm text-gray-400">
                  <p>Đơn tối thiểu: <strong class="text-gray-200">{{ money(item.min_order_amount) }}</strong></p>
                  <p v-if="item.discount_type === 'PERCENT' && item.max_discount">Giảm tối đa: <strong class="text-gray-200">{{ money(item.max_discount) }}</strong></p>
                  <p>Hạn dùng: <strong class="text-gray-200">{{ formatDateTime(item.ends_at) }}</strong></p>
                  <p v-if="remaining(item) !== null">Còn <strong class="text-amber-300">{{ remaining(item) }}</strong> lượt sử dụng</p>
                </div>

                <div class="mt-auto pt-6">
                  <div class="flex items-center overflow-hidden rounded-xl border border-dashed border-red-500/40 bg-red-500/5">
                    <code class="min-w-0 flex-1 truncate px-4 py-3 text-lg font-black tracking-wider text-white">{{ item.code }}</code>
                    <button class="border-l border-red-500/30 px-4 py-3 text-sm font-bold text-red-300 hover:bg-red-500/10" @click="copyCode(item.code)">
                      {{ copiedCode === item.code ? 'Đã chép' : 'Sao chép' }}
                    </button>
                  </div>
                </div>
              </div>
            </article>
          </div>

          <div v-else class="rounded-2xl border border-white/10 bg-white/[0.03] px-6 py-14 text-center text-gray-400">
            <span class="material-symbols-outlined text-5xl text-gray-600">sell</span>
            <p class="mt-3 font-semibold">Hiện chưa có voucher nào có thể sử dụng.</p>
          </div>
        </section>

        <section v-if="upcomingPromotions.length" class="mt-12">
          <p class="text-xs font-black uppercase tracking-[0.18em] text-amber-400">Sắp diễn ra</p>
          <h2 class="mt-1 text-2xl font-black text-white">Ưu đãi sắp mở</h2>
          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <article v-for="item in upcomingPromotions" :key="item.id" class="flex items-center justify-between gap-5 rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <div>
                <span class="font-mono text-sm font-black text-amber-300">{{ item.code }}</span>
                <h3 class="mt-1 font-bold text-white">{{ item.name }}</h3>
                <p class="mt-1 text-sm text-gray-400">{{ discountLabel(item) }} · Mở từ {{ formatDateTime(item.starts_at) }}</p>
              </div>
              <span class="material-symbols-outlined text-3xl text-gray-500">schedule</span>
            </article>
          </div>
        </section>

        <section class="mt-12 flex flex-col items-center justify-between gap-5 rounded-2xl border border-white/10 bg-[#1a1c1c] p-7 text-center sm:flex-row sm:text-left">
          <div>
            <h2 class="text-xl font-black text-white">Đã chọn được voucher phù hợp?</h2>
            <p class="mt-1 text-sm text-gray-400">Chọn phim và nhập mã tại bước thanh toán để hệ thống kiểm tra giá trị ưu đãi thực tế.</p>
          </div>
          <NuxtLink to="/products" class="whitespace-nowrap rounded-xl bg-red-600 px-6 py-3 font-black text-white transition hover:bg-red-500">Đặt vé ngay</NuxtLink>
        </section>
      </template>
    </div>
  </main>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { branchesService, comboService, type CinemaCombo } from '~/services/api'

definePageMeta({ layout: 'default', middleware: ['auth'] })
const ticketsStore = useTicketsStore()
const { selectedShowtime, selectedSeats, selectedCombos, totalAmount } = storeToRefs(ticketsStore)
const combos = ref<CinemaCombo[]>([])
const loading = ref(true)
const error = ref('')
const ticketTotal = computed(() => selectedSeats.value.reduce((sum, seat) => sum + seat.price, 0))
const quantity = (id: string) => selectedCombos.value.find(item => item.combo.id === id)?.quantity || 0

onMounted(async () => {
  if (!selectedShowtime.value || !selectedSeats.value.length) return navigateTo('/products')
  try {
    const branches = await branchesService.getAll()
    const branch = branches.find(item => item.name === selectedShowtime.value?.branchName)
    if (!branch) throw new Error('Không xác định được chi nhánh của suất chiếu')
    combos.value = await comboService.getPublic(branch.id)
  } catch (e: any) { error.value = e?.message || 'Không thể tải combo' }
  finally { loading.value = false }
})

function change(combo: CinemaCombo, delta: number) {
  const next = Math.max(0, Math.min(10, quantity(combo.id) + delta))
  if (combo.stock_quantity != null && next > combo.stock_quantity) return
  ticketsStore.setComboQuantity(combo, next)
}
</script>

<template>
  <section class="min-h-screen bg-[#0b0c10] px-4 py-8 text-white">
    <div class="mx-auto max-w-6xl">
      <div class="mb-8 flex items-end justify-between gap-4">
        <div><p class="text-xs font-bold uppercase tracking-[.25em] text-red-400">Bước 4/5</p><h1 class="mt-2 text-3xl font-black">Chọn bắp nước</h1><p class="mt-2 text-sm text-gray-400">Có thể bỏ qua nếu bạn không có nhu cầu.</p></div>
        <NuxtLink to="/checkout/seat" class="text-sm text-gray-300 hover:text-white">← Chọn lại ghế</NuxtLink>
      </div>
      <div v-if="loading" class="py-20 text-center text-gray-400">Đang tải combo của chi nhánh...</div>
      <div v-else-if="error" class="rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-red-200">{{ error }}</div>
      <div v-else-if="!combos.length" class="rounded-3xl border border-dashed border-white/15 p-12 text-center text-gray-400">Chi nhánh chưa mở bán combo. Bạn vẫn có thể tiếp tục thanh toán.</div>
      <div v-else class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        <article v-for="combo in combos" :key="combo.id" class="overflow-hidden rounded-3xl border border-white/10 bg-[#17191f]">
          <div class="flex h-40 items-center justify-center bg-gradient-to-br from-red-950/60 to-orange-950/30">
            <img v-if="combo.image_url" :src="combo.image_url" :alt="combo.name" class="h-full w-full object-cover"><span v-else class="material-symbols-outlined text-6xl text-orange-300">fastfood</span>
          </div>
          <div class="p-5"><h2 class="font-black">{{ combo.name }}</h2><p class="mt-2 min-h-10 text-sm text-gray-400">{{ combo.description || 'Combo bắp nước tại rạp' }}</p>
            <div class="mt-5 flex items-center justify-between"><strong class="text-lg text-orange-300">{{ Number(combo.price).toLocaleString('vi-VN') }}đ</strong>
              <div class="flex items-center gap-3 rounded-full border border-white/10 p-1"><button class="h-8 w-8 rounded-full bg-white/10" @click="change(combo,-1)">−</button><span class="w-4 text-center font-bold">{{ quantity(combo.id) }}</span><button class="h-8 w-8 rounded-full bg-red-600" @click="change(combo,1)">+</button></div>
            </div>
          </div>
        </article>
      </div>
      <div class="sticky bottom-4 mt-8 flex flex-col gap-4 rounded-2xl border border-white/10 bg-[#17191f]/95 p-5 shadow-2xl backdrop-blur md:flex-row md:items-center md:justify-between">
        <div class="text-sm text-gray-400">Tiền vé: {{ ticketTotal.toLocaleString('vi-VN') }}đ · Combo: {{ (totalAmount-ticketTotal).toLocaleString('vi-VN') }}đ<br><strong class="text-xl text-white">Tổng: {{ totalAmount.toLocaleString('vi-VN') }}đ</strong></div>
        <NuxtLink to="/checkout/payment" class="rounded-xl bg-red-600 px-8 py-3 text-center font-bold">{{ selectedCombos.length ? 'Tiếp tục thanh toán' : 'Bỏ qua và thanh toán' }} →</NuxtLink>
      </div>
    </div>
  </section>
</template>

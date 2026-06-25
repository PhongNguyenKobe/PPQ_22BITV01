<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTicketsStore } from '~/store/tickets'
import { movieService, type Seat } from '~/services/api'

const ticketsStore = useTicketsStore()
const { selectedShowtime, selectedSeats } = storeToRefs(ticketsStore)

const seatsList = ref<Seat[]>([])
const loading = ref(false)

onMounted(async () => {
  if (selectedShowtime.value) {
    loading.value = true
    try {
      seatsList.value = await movieService.getSeats(selectedShowtime.value.id)
    } catch (e) {
      console.error('Failed to load seats map:', e)
    } finally {
      loading.value = false
    }
  }
})

// Organize seats by row
const seatsByRow = computed(() => {
  const map: Record<string, Seat[]> = {}
  seatsList.value.forEach(seat => {
    if (!map[seat.row]) {
      map[seat.row] = []
    }
    map[seat.row].push(seat)
  })
  // Sort keys alphabetically
  return Object.keys(map).sort().reduce((acc, key) => {
    acc[key] = map[key].sort((a, b) => a.number - b.number)
    return acc;
  }, {} as Record<string, Seat[]>);
})

function isSeatSelected(seatId: string): boolean {
  return selectedSeats.value.some(s => s.id === seatId)
}

function handleSeatClick(seat: Seat) {
  if (seat.status === 'occupied') return
  
  // Clone seat status update
  const seatObj = {
    ...seat,
    status: (isSeatSelected(seat.id) ? 'available' : 'selected') as any
  }
  ticketsStore.toggleSeat(seatObj)
}
</script>

<template>
  <div class="glass-panel rounded-2xl border border-glass-stroke p-6 md:p-8 flex flex-col items-center">
    <div v-if="loading" class="py-12 text-center text-on-surface-variant animate-pulse">
      Đang tải sơ đồ phòng chiếu thông minh...
    </div>
    
    <div v-else-if="!selectedShowtime" class="py-12 text-center text-on-surface-variant">
      ⚠️ Vui lòng quay lại trang chi tiết phim để lựa chọn suất chiếu.
    </div>

    <div v-else class="w-full flex flex-col items-center">
      <!-- Theater Screen projection -->
      <div class="w-full max-w-2xl mb-12 text-center screen-curve">
        <div class="w-full bg-white/20 h-1 rounded-full shadow-[0_2px_15px_rgba(255,255,255,0.3)]"></div>
        <div class="screen-glow"></div>
        <span class="text-xs text-on-surface-variant tracking-[0.2em] uppercase font-bold mt-2 inline-block">MÀN HÌNH CHẤT LƯỢNG CAO</span>
      </div>

      <!-- Seat Grid Layout -->
      <div class="overflow-x-auto w-full max-w-3xl flex justify-center pb-6 hide-scrollbar">
        <div class="flex flex-col gap-3 min-w-[500px]">
          <div
            v-for="(rowSeats, rowName) in seatsByRow"
            :key="rowName"
            class="flex items-center gap-3"
          >
            <!-- Row Letter -->
            <span class="w-6 font-bold text-sm text-on-surface-variant text-center mr-2">{{ rowName }}</span>
            
            <!-- Row Seats -->
            <div class="flex items-center gap-2">
              <button
                v-for="seat in rowSeats"
                :key="seat.id"
                @click="handleSeatClick(seat)"
                :disabled="seat.status === 'occupied'"
                :title="`${seat.row}${seat.number} - ${seat.type.toUpperCase()} (${seat.price.toLocaleString()}đ)`"
                class="w-8 h-8 rounded-lg text-[10px] font-bold transition-all relative flex items-center justify-center border"
                :class="[
                  seat.status === 'occupied'
                    ? 'bg-neutral-800 border-neutral-700 text-neutral-600 cursor-not-allowed'
                    : isSeatSelected(seat.id)
                      ? 'bg-primary-container border-primary-container text-white scale-110 shadow-[0_0_12px_rgba(229,9,20,0.5)]'
                      : seat.type === 'vip'
                        ? 'bg-purple-950/40 border-purple-600 text-purple-200 hover:bg-purple-700/30'
                        : seat.type === 'couple'
                          ? 'bg-pink-950/40 border-pink-600 text-pink-200 w-16 hover:bg-pink-700/30'
                          : 'bg-surface-container-high border-glass-stroke text-on-surface hover:bg-white/10'
                ]"
              >
                {{ seat.number }}
              </button>
            </div>
            
            <!-- Row Letter Right -->
            <span class="w-6 font-bold text-sm text-on-surface-variant text-center ml-2">{{ rowName }}</span>
          </div>
        </div>
      </div>

      <!-- Legends -->
      <div class="flex flex-wrap justify-center gap-6 border-t border-glass-stroke/40 pt-8 w-full max-w-2xl mt-4">
        <div class="flex items-center gap-2 text-xs">
          <div class="w-5 h-5 bg-surface-container-high border border-glass-stroke rounded"></div>
          <span class="text-on-surface-variant font-medium">Ghế Thường</span>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <div class="w-5 h-5 bg-purple-950/40 border border-purple-600 rounded"></div>
          <span class="text-on-surface-variant font-medium">Ghế VIP (+30%)</span>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <div class="w-10 h-5 bg-pink-950/40 border border-pink-600 rounded"></div>
          <span class="text-on-surface-variant font-medium">Ghế Đôi (+50%)</span>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <div class="w-5 h-5 bg-primary-container border border-primary-container rounded shadow-[0_0_8px_rgba(229,9,20,0.4)]"></div>
          <span class="text-on-surface-variant font-medium">Đang Chọn</span>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <div class="w-5 h-5 bg-neutral-800 border border-neutral-700 rounded"></div>
          <span class="text-on-surface-variant font-medium">Đã Bán</span>
        </div>
      </div>
    </div>
  </div>
</template>

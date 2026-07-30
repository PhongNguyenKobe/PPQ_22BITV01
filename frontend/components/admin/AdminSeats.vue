<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { adminBackendService, adminService, type AdminAuditorium, type AdminSeat, type AdminSeatType } from '~/services/api'
import { useUserStore } from '~/store/user'

const userStore = useUserStore()
const isBranchAdmin = computed(() => userStore.currentUser?.role === 'branch-admin')

const auditoriums = ref<AdminAuditorium[]>([])
const seatTypes = ref<AdminSeatType[]>([])
const loading = ref(false)
const error = ref('')

const seatForm = ref({
  auditoriumId: '',
})

type SeatTool = 'INACTIVE' | 'STANDARD' | 'VIP' | 'COUPLE'
type SeatLayoutCell = {
  row: string
  number: number
  typeId: number
  typeCode: string
  active: boolean
}

const seats = ref<AdminSeat[]>([])
const seatLayoutRows = ref(8)
const seatLayoutColumns = ref(12)
const seatTool = ref<SeatTool>('STANDARD')
const seatTools: { code: SeatTool; label: string; cls: string }[] = [
  { code: 'STANDARD', label: 'Ghế thường', cls: 'bg-slate-600 border-slate-500' },
  { code: 'VIP', label: 'Ghế VIP', cls: 'bg-red-600 border-red-500' },
  { code: 'COUPLE', label: 'Ghế đôi', cls: 'bg-pink-600 border-pink-500' },
  { code: 'INACTIVE', label: 'Lối đi / Ẩn', cls: 'bg-zinc-800 border-dashed border-white/20' },
]
const seatLayout = ref<SeatLayoutCell[]>([])
const seatLayoutSaving = ref(false)
const isPainting = ref(false)
const paintStart = ref<SeatLayoutCell | null>(null)
const paintCurrent = ref<SeatLayoutCell | null>(null)

const paintedSeatKeys = computed(() => {
  if (!paintStart.value || !paintCurrent.value) return new Set<string>()
  const firstRow = Math.min(paintStart.value.row.charCodeAt(0), paintCurrent.value.row.charCodeAt(0))
  const lastRow = Math.max(paintStart.value.row.charCodeAt(0), paintCurrent.value.row.charCodeAt(0))
  const firstNumber = Math.min(paintStart.value.number, paintCurrent.value.number)
  const lastNumber = Math.max(paintStart.value.number, paintCurrent.value.number)
  return new Set(
    seatLayout.value
      .filter(cell =>
        cell.row.charCodeAt(0) >= firstRow
        && cell.row.charCodeAt(0) <= lastRow
        && cell.number >= firstNumber
        && cell.number <= lastNumber,
      )
      .map(cell => `${cell.row}-${cell.number}`),
  )
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [auditoriumData, seatTypeData] = await Promise.all([
      adminBackendService.getAuditoriums(),
      adminBackendService.getSeatTypes(),
    ])
    auditoriums.value = auditoriumData
    seatTypes.value = seatTypeData
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải dữ liệu.'
  } finally {
    loading.value = false
  }
}

function seatTypeByCode(code: string) {
  return seatTypes.value.find((item) => item.code === code) || seatTypes.value[0]
}

function rebuildSeatLayout(existing: AdminSeat[] = []) {
  const existingMap = new Map(existing.map((seat) => [`${seat.seat_row}-${seat.seat_number}`, seat]))
  const fallback = seatTypeByCode('STANDARD')
  seatLayout.value = []
  for (let rowIndex = 0; rowIndex < seatLayoutRows.value; rowIndex += 1) {
    const row = String.fromCharCode(65 + rowIndex)
    for (let number = 1; number <= seatLayoutColumns.value; number += 1) {
      const saved = existingMap.get(`${row}-${number}`)
      seatLayout.value.push({
        row,
        number,
        typeId: saved?.seat_type_id || fallback?.id || 1,
        typeCode: saved?.seat_type_code || fallback?.code || 'STANDARD',
        active: saved?.is_active ?? true,
      })
    }
  }
}

async function loadSeatsByAuditorium() {
  if (!seatForm.value.auditoriumId) return
  error.value = ''
  seats.value = await adminBackendService.getSeats(seatForm.value.auditoriumId)
  if (seats.value.length) {
    const rows = [...new Set(seats.value.map((seat) => seat.seat_row))]
    seatLayoutRows.value = Math.max(1, rows.length)
    seatLayoutColumns.value = Math.max(...seats.value.map((seat) => seat.seat_number), 1)
  } else {
    seatLayoutRows.value = 8
    seatLayoutColumns.value = 12
  }
  rebuildSeatLayout(seats.value)
}

function resizeSeatLayout() {
  const current = seatLayout.value.map((cell) => ({
    id: '',
    auditorium_id: seatForm.value.auditoriumId,
    auditorium_name: '',
    branch_name: '',
    seat_row: cell.row,
    seat_number: cell.number,
    seat_type_id: cell.typeId,
    seat_type_code: cell.typeCode,
    is_active: cell.active,
  }))
  rebuildSeatLayout(current)
}

function applySeatTool(cell: SeatLayoutCell) {
  if (seatTool.value === 'INACTIVE') {
    cell.active = false
    return
  }
  const type = seatTypeByCode(seatTool.value)
  if (!type) return
  cell.active = true
  cell.typeId = type.id
  cell.typeCode = type.code
}

function selectSeatTool(tool: SeatTool) {
  seatTool.value = tool
}

function applyToolToRow(row: string) {
  seatLayout.value.filter((cell) => cell.row === row).forEach(applySeatTool)
}

function startPainting(cell: SeatLayoutCell, event: PointerEvent) {
  if (event.button !== 0) return
  event.preventDefault()
  isPainting.value = true
  paintStart.value = cell
  paintCurrent.value = cell
}

function extendPainting(cell: SeatLayoutCell) {
  if (isPainting.value) paintCurrent.value = cell
}

function finishPainting() {
  if (!isPainting.value) return
  const selectedKeys = paintedSeatKeys.value
  seatLayout.value
    .filter(cell => selectedKeys.has(`${cell.row}-${cell.number}`))
    .forEach(applySeatTool)
  isPainting.value = false
  paintStart.value = null
  paintCurrent.value = null
}

async function saveSeatLayout() {
  if (!seatForm.value.auditoriumId || !seatLayout.value.length) return
  seatLayoutSaving.value = true
  error.value = ''
  try {
    const result = await adminBackendService.saveSeatLayout(
      seatForm.value.auditoriumId,
      seatLayout.value.map((cell) => ({
        seat_row: cell.row,
        seat_number: cell.number,
        seat_type_id: cell.typeId,
        is_active: cell.active,
      })),
    )
    seats.value = result.seats
    auditoriums.value = await adminBackendService.getAuditoriums()
    alert('Sơ đồ ghế đã được lưu thành công!')
  } catch (e: any) {
    const message = e?.message || ''
    const seatMatch = message.match(/Seat ([A-Z0-9]+) has a ticket for an upcoming showtime/)
    error.value = seatMatch
      ? `Ghế ${seatMatch[1]} đã có người mua vé cho một suất sắp chiếu nên chưa thể thay đổi.`
      : message || 'Không thể lưu sơ đồ ghế.'
  } finally {
    seatLayoutSaving.value = false
  }
}

const activeSeatCount = computed(() => seatLayout.value.filter((cell) => cell.active).length)
const seatLayoutRowNames = computed(() => [...new Set(seatLayout.value.map((cell) => cell.row))])

onMounted(() => {
  loadData()
  window.addEventListener('pointerup', finishPainting)
})

onBeforeUnmount(() => window.removeEventListener('pointerup', finishPainting))
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-on-surface">Thiết kế Sơ đồ ghế</h2>
        <p class="text-sm text-on-surface-variant mt-1">Tuỳ chỉnh sơ đồ ghế, thiết lập lối đi và cấu hình ghế VIP, Couple cho từng phòng chiếu.</p>
      </div>
    </div>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-400">
      {{ error }}
    </p>

    <div class="panel p-6 shadow-xl relative overflow-hidden">
      <!-- Toolbar -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/10 pb-6 mb-6">
        <div class="grid gap-3 sm:grid-cols-3 max-w-2xl w-full">
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Chọn phòng chiếu</label>
            <select v-model="seatForm.auditoriumId" @change="loadSeatsByAuditorium" class="field-input font-medium bg-black/40">
              <option value="" disabled>-- Bấm để chọn phòng --</option>
              <option v-for="a in auditoriums" :key="a.id" :value="a.id">{{ a.branch_name }} - {{ a.name }}</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Số hàng dọc</label>
            <input v-model.number="seatLayoutRows" type="number" min="1" max="26" class="field-input text-center" @change="resizeSeatLayout" :disabled="!seatForm.auditoriumId" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Số cột ngang</label>
            <input v-model.number="seatLayoutColumns" type="number" min="1" max="30" class="field-input text-center" @change="resizeSeatLayout" :disabled="!seatForm.auditoriumId" />
          </div>
        </div>
        
        <div class="flex-shrink-0" v-if="seatForm.auditoriumId">
          <div class="bg-black/30 p-3 rounded-xl border border-white/5 flex flex-col items-center">
            <span class="text-[10px] uppercase text-on-surface-variant tracking-wider font-bold mb-1">Sức chứa</span>
            <div class="text-3xl font-black text-primary leading-none">{{ activeSeatCount }} <span class="text-sm font-medium text-on-surface-variant">ghế</span></div>
          </div>
        </div>
      </div>

      <!-- Editor Workspace -->
      <div v-if="seatForm.auditoriumId" class="animate-fade-in">
        <!-- Tools Palette -->
        <div class="mb-6">
          <p class="text-sm font-semibold text-on-surface mb-3 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-[20px]">palette</span>
            Công cụ vẽ (chọn công cụ, bấm một ghế hoặc kéo để tô cả vùng)
          </p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tool in seatTools"
              :key="tool.code"
              type="button"
              class="rounded-xl px-5 py-2 text-sm font-bold border-2 transition-all flex items-center gap-2"
              :class="[
                tool.cls, 
                seatTool === tool.code 
                  ? 'ring-2 ring-white/50 ring-offset-2 ring-offset-[#1a1c1c] scale-105 shadow-lg' 
                  : 'opacity-70 hover:opacity-100'
              ]"
              @click="selectSeatTool(tool.code)"
            >
              <span class="w-3 h-3 rounded-full bg-white/30" v-if="seatTool === tool.code"></span>
              {{ tool.label }}
            </button>
          </div>
        </div>

        <!-- Canvas -->
        <div class="overflow-auto rounded-2xl border border-white/5 bg-black/40 p-8 shadow-inner relative">
          <!-- Screen Curved Line -->
          <div class="mx-auto mb-16 max-w-4xl relative">
            <div class="h-2 rounded-[100%] bg-gradient-to-r from-transparent via-primary to-transparent shadow-[0_12px_32px_rgba(229,9,20,.6)] opacity-80"></div>
            <p class="mt-4 text-center text-sm font-black tracking-[0.5em] text-white/30 uppercase">Màn hình chính</p>
          </div>
          
          <div class="mx-auto w-max space-y-3 pb-8">
            <div v-for="row in seatLayoutRowNames" :key="row" class="flex items-center gap-3">
              <!-- Row Label Left -->
              <button
                type="button"
                class="w-10 h-10 rounded-xl bg-white/5 text-sm font-bold text-on-surface-variant hover:text-primary hover:bg-white/10 transition-colors flex items-center justify-center border border-white/5"
                title="Áp dụng công cụ cho cả hàng này"
                @click="applyToolToRow(row)"
              >{{ row }}</button>
              
              <!-- Seats -->
              <div class="flex gap-2 mx-4">
                <button
                  v-for="cell in seatLayout.filter((item) => item.row === row)"
                  :key="`${cell.row}-${cell.number}`"
                  type="button"
                  class="relative h-10 w-11 touch-none rounded-t-lg rounded-b-sm border-b-4 text-[11px] font-bold transition-all hover:scale-110 shadow-sm flex items-center justify-center select-none"
                  :class="
                    [
                    !cell.active ? 'border-dashed border-white/10 border-b border-t border-l border-r bg-transparent text-white/10 hover:border-white/30 hover:bg-white/5'
                    : cell.typeCode === 'VIP' ? 'border-red-800 bg-red-500 text-white shadow-red-500/20 hover:shadow-red-500/40'
                    : cell.typeCode === 'COUPLE' ? 'border-pink-800 bg-pink-500 text-white shadow-pink-500/20 hover:shadow-pink-500/40 w-[60px]'
                    : 'border-slate-800 bg-slate-600 text-white shadow-slate-900/40 hover:bg-slate-500',
                    paintedSeatKeys.has(`${cell.row}-${cell.number}`) ? 'ring-2 ring-cyan-300 scale-105 brightness-125' : ''
                    ]
                  "
                  @pointerdown="startPainting(cell, $event)"
                  @pointerenter="extendPainting(cell)"
                >
                  <span class="z-10">{{ cell.active ? `${cell.row}${cell.number}` : '+' }}</span>
                  <div v-if="cell.active" class="absolute top-0 left-0 w-full h-2/5 bg-white/10 rounded-t-lg"></div>
                </button>
              </div>

              <!-- Row Label Right -->
              <button
                type="button"
                class="w-10 h-10 rounded-xl bg-white/5 text-sm font-bold text-on-surface-variant hover:text-primary hover:bg-white/10 transition-colors flex items-center justify-center border border-white/5"
                title="Áp dụng công cụ cho cả hàng này"
                @click="applyToolToRow(row)"
              >{{ row }}</button>
            </div>
          </div>
        </div>

        <div class="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-white/10 pt-6">
          <p class="text-sm text-on-surface-variant flex items-center gap-2">
            <span class="material-symbols-outlined text-[20px]">info</span>
            Hãy nhớ lưu lại sau khi thực hiện thay đổi trên sơ đồ.
          </p>
          <button class="action-primary !w-auto px-10 py-3 text-base flex items-center gap-2" :disabled="seatLayoutSaving" @click="saveSeatLayout">
            <span class="material-symbols-outlined">{{ seatLayoutSaving ? 'hourglass_empty' : 'save' }}</span>
            {{ seatLayoutSaving ? 'Đang lưu sơ đồ...' : 'Lưu toàn bộ sơ đồ ghế' }}
          </button>
        </div>
      </div>

      <div v-else class="rounded-2xl border-2 border-dashed border-white/10 p-16 text-center text-sm text-on-surface-variant bg-black/20 flex flex-col items-center">
        <span class="material-symbols-outlined text-[64px] mb-4 opacity-20">widgets</span>
        <p class="text-lg">Chọn một phòng chiếu ở trên để bắt đầu thiết kế sơ đồ.</p>
        <p class="mt-2 text-on-surface-variant/70">Nếu chưa có phòng, hãy quay lại mục Phòng chiếu để tạo.</p>
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

.field-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.action-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px -16px rgba(229, 9, 20, 0.95);
}

.animate-fade-in {
  animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

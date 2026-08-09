<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import { adminBackendService, adminService, type AdminAuditorium, type AdminSeat, type AdminSeatType } from '~/services/api'
import { useUserStore } from '~/store/user'

const userStore = useUserStore()
const route = useRoute()
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
const savedSignature = ref('')
const undoStack = ref<SeatLayoutCell[][]>([])
const lastAuditoriumId = ref('')
const previousRows = ref(8)
const previousColumns = ref(12)
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
  savedSignature.value = layoutSignature()
  undoStack.value = []
  lastAuditoriumId.value = seatForm.value.auditoriumId
  previousRows.value = seatLayoutRows.value
  previousColumns.value = seatLayoutColumns.value
}

function resizeSeatLayout() {
  const removed = seatLayout.value.filter(cell =>
    cell.active && (cell.row.charCodeAt(0) - 64 > seatLayoutRows.value || cell.number > seatLayoutColumns.value),
  ).length
  if (removed && !window.confirm(`Thu nhỏ sơ đồ sẽ loại ${removed} ghế khỏi vùng hiển thị. Bạn có muốn tiếp tục?`)) {
    seatLayoutRows.value = previousRows.value
    seatLayoutColumns.value = previousColumns.value
    return
  }
  pushUndo()
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
  previousRows.value = seatLayoutRows.value
  previousColumns.value = seatLayoutColumns.value
}

function cloneLayout() {
  return seatLayout.value.map(cell => ({ ...cell }))
}

function layoutSignature() {
  return JSON.stringify(seatLayout.value.map(cell => [cell.row, cell.number, cell.typeId, cell.typeCode, cell.active]))
}

function pushUndo() {
  undoStack.value.push(cloneLayout())
  if (undoStack.value.length > 30) undoStack.value.shift()
}

function undo() {
  const previous = undoStack.value.pop()
  if (previous) {
    seatLayout.value = previous
    const rows = [...new Set(previous.map(cell => cell.row))]
    seatLayoutRows.value = Math.max(rows.length, 1)
    seatLayoutColumns.value = Math.max(...previous.map(cell => cell.number), 1)
    previousRows.value = seatLayoutRows.value
    previousColumns.value = seatLayoutColumns.value
  }
}

function restoreSaved() {
  if (!isDirty.value || window.confirm('Bỏ toàn bộ thay đổi chưa lưu và khôi phục sơ đồ gần nhất?')) {
    const rows = [...new Set(seats.value.map(seat => seat.seat_row))]
    seatLayoutRows.value = Math.max(rows.length, 1)
    seatLayoutColumns.value = seats.value.length ? Math.max(...seats.value.map(seat => seat.seat_number), 1) : 12
    previousRows.value = seatLayoutRows.value
    previousColumns.value = seatLayoutColumns.value
    rebuildSeatLayout(seats.value)
    undoStack.value = []
  }
}

async function changeAuditorium(event: Event) {
  const nextId = (event.target as HTMLSelectElement).value
  if (isDirty.value && !window.confirm('Sơ đồ hiện tại có thay đổi chưa lưu. Bạn có muốn chuyển phòng và bỏ các thay đổi này?')) {
    seatForm.value.auditoriumId = lastAuditoriumId.value
    return
  }
  seatForm.value.auditoriumId = nextId
  await loadSeatsByAuditorium()
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
  pushUndo()
  seatLayout.value.filter((cell) => cell.row === row).forEach(applySeatTool)
}

function startPainting(cell: SeatLayoutCell, event: PointerEvent) {
  if (event.button !== 0) return
  event.preventDefault()
  pushUndo()
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
    savedSignature.value = layoutSignature()
    undoStack.value = []
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
function coupleVisualPosition(cell: SeatLayoutCell) {
  if (!cell.active || cell.typeCode !== 'COUPLE') return ''
  const rowCouples = seatLayout.value
    .filter(item => item.row === cell.row && item.active && item.typeCode === 'COUPLE')
    .sort((a, b) => a.number - b.number)
  const index = rowCouples.findIndex(item => item.number === cell.number)
  let runStart = index
  while (runStart > 0 && rowCouples[runStart - 1].number === rowCouples[runStart].number - 1) runStart -= 1
  const offset = index - runStart
  const previous = rowCouples[index - 1]
  const next = rowCouples[index + 1]
  if (offset % 2 === 0 && next?.number === cell.number + 1) return 'couple-left'
  if (offset % 2 === 1 && previous?.number === cell.number - 1) return 'couple-right'
  return 'couple-single'
}
const selectedRoom = computed(() => auditoriums.value.find(item => item.id === seatForm.value.auditoriumId))
const isDirty = computed(() => Boolean(seatForm.value.auditoriumId) && layoutSignature() !== savedSignature.value)
const seatCounts = computed(() => ({
  standard: seatLayout.value.filter(cell => cell.active && cell.typeCode === 'STANDARD').length,
  vip: seatLayout.value.filter(cell => cell.active && cell.typeCode === 'VIP').length,
  couple: seatLayout.value.filter(cell => cell.active && cell.typeCode === 'COUPLE').length,
  inactive: seatLayout.value.filter(cell => !cell.active).length,
}))
const roomSize = computed(() => {
  if (activeSeatCount.value <= 80) return { label: 'Phòng nhỏ', description: 'Tối đa 80 ghế' }
  if (activeSeatCount.value <= 150) return { label: 'Phòng tiêu chuẩn', description: '81–150 ghế' }
  return { label: 'Phòng lớn', description: 'Trên 150 ghế' }
})

const formatPresets: Record<string, { rows: number; columns: number; label: string }> = {
  '2D': { rows: 8, columns: 12, label: 'Phòng tiêu chuẩn' },
  '3D': { rows: 9, columns: 14, label: 'Phòng 3D mở rộng' },
  'IMAX': { rows: 10, columns: 16, label: 'Phòng màn hình lớn' },
  '4DX': { rows: 8, columns: 12, label: 'Phòng hiệu ứng chuyển động' },
}

function applyFormatPreset(format: string) {
  const preset = formatPresets[format] || formatPresets['2D']
  const capacity = preset.rows * preset.columns
  if (!window.confirm(`Áp dụng sơ đồ gợi ý ${format}: ${preset.rows} hàng × ${preset.columns} vị trí (tối đa ${capacity})?\n\nĐây là mẫu bố trí, không tự đổi công nghệ màn hình của phòng. Sơ đồ đang chỉnh sẽ được thay thế.`)) return
  pushUndo()
  seatLayoutRows.value = preset.rows
  seatLayoutColumns.value = preset.columns
  previousRows.value = preset.rows
  previousColumns.value = preset.columns
  const standard = seatTypeByCode('STANDARD')
  const vip = seatTypeByCode('VIP') || standard
  const couple = seatTypeByCode('COUPLE') || vip
  seatLayout.value = []
  for (let rowIndex = 0; rowIndex < preset.rows; rowIndex += 1) {
    for (let number = 1; number <= preset.columns; number += 1) {
      const isLastRow = rowIndex === preset.rows - 1
      const isVipZone = rowIndex >= Math.ceil(preset.rows * 0.55)
      const isAisle = preset.columns >= 14 && (number === 3 || number === preset.columns - 2)
      const type = isLastRow ? couple : isVipZone ? vip : standard
      seatLayout.value.push({ row: String.fromCharCode(65 + rowIndex), number, typeId: type?.id || 1, typeCode: type?.code || 'STANDARD', active: !isAisle })
    }
  }
}

function beforeUnload(event: BeforeUnloadEvent) {
  if (!isDirty.value) return
  event.preventDefault()
  event.returnValue = ''
}

function confirmNavigation() {
  return !isDirty.value || window.confirm('Sơ đồ ghế có thay đổi chưa lưu. Bạn có chắc muốn rời trang?')
}

onBeforeRouteLeave(() => confirmNavigation())
onBeforeRouteUpdate(() => confirmNavigation())

onMounted(async () => {
  await loadData()
  const requestedAuditorium = String(route.query.auditorium || '')
  if (requestedAuditorium && auditoriums.value.some(item => item.id === requestedAuditorium)) {
    seatForm.value.auditoriumId = requestedAuditorium
    await loadSeatsByAuditorium()
  }
  window.addEventListener('pointerup', finishPainting)
  window.addEventListener('beforeunload', beforeUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('pointerup', finishPainting)
  window.removeEventListener('beforeunload', beforeUnload)
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-xs font-black uppercase tracking-[0.2em] text-primary">Cấu hình phòng chiếu</p>
        <h2 class="mt-1 text-2xl font-black text-on-surface">Thiết kế sơ đồ ghế</h2>
        <p class="text-sm text-on-surface-variant mt-1">Định dạng phòng và loại ghế được quản lý riêng, tương tự luồng chọn suất và ghế trên các nền tảng bán vé.</p>
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
            <select :value="seatForm.auditoriumId" @change="changeAuditorium" class="field-input font-medium bg-black/40">
              <option value="" disabled>-- Bấm để chọn phòng --</option>
              <option v-for="a in auditoriums" :key="a.id" :value="a.id">{{ a.branch_name }} - {{ a.name }}</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Số hàng ghế</label>
            <input v-model.number="seatLayoutRows" type="number" min="1" max="26" class="field-input text-center" @change="resizeSeatLayout" :disabled="!seatForm.auditoriumId" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-on-surface-variant uppercase">Số ghế mỗi hàng</label>
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
        <div class="mb-5 grid gap-3">
          <div class="rounded-xl border border-sky-500/20 bg-sky-500/5 p-4">
            <div class="flex flex-wrap items-center gap-2">
              <strong class="text-lg text-on-surface">{{ selectedRoom?.name }}</strong>
              <span class="format-badge">{{ selectedRoom?.screen_type || '2D' }}</span>
              <span class="rounded-full px-2 py-1 text-[10px] font-black" :class="selectedRoom?.is_active ? 'bg-emerald-500/10 text-emerald-300' : 'bg-slate-500/10 text-slate-300'">{{ selectedRoom?.is_active ? 'ĐANG HOẠT ĐỘNG' : 'TẠM NGƯNG' }}</span>
              <span class="rounded-full bg-violet-500/10 px-2 py-1 text-[10px] font-black text-violet-300">{{ roomSize.label }} · {{ roomSize.description }}</span>
              <span class="ml-auto text-xs font-bold" :class="isDirty ? 'text-amber-300' : 'text-emerald-300'">{{ isDirty ? '● Có thay đổi chưa lưu' : '✓ Đã đồng bộ' }}</span>
            </div>
            <p class="mt-2 text-xs text-on-surface-variant">Mã phòng {{ selectedRoom?.code }}. <b>Định dạng {{ selectedRoom?.screen_type || '2D' }}</b> mô tả công nghệ trình chiếu; <b>{{ activeSeatCount }} ghế</b> quyết định quy mô phòng, không quyết định phòng là 2D hay 3D.</p>
          </div>
          <div class="preset-panel">
            <div>
              <p class="text-sm font-black text-on-surface">Mẫu sơ đồ nhanh</p>
              <p class="text-xs text-on-surface-variant">Các con số là mẫu đề xuất cho đồ án, không phải tiêu chuẩn bắt buộc ngoài đời.</p>
            </div>
            <div class="grid grid-cols-2 gap-2 md:grid-cols-4">
              <button v-for="(preset, format) in formatPresets" :key="format" type="button" class="preset-choice" :class="{ active: selectedRoom?.screen_type === format }" @click="applyFormatPreset(String(format))">
                <span class="material-symbols-outlined">{{ format === '4DX' ? 'motion_mode' : format === 'IMAX' ? 'aspect_ratio' : 'movie' }}</span>
                <span><b>Mẫu {{ format }}</b><small>{{ preset.rows }} hàng × {{ preset.columns }} vị trí</small></span>
                <em v-if="selectedRoom?.screen_type === format">Định dạng hiện tại</em>
              </button>
            </div>
          </div>
        </div>

        <div v-if="selectedRoom?.future_showtimes_count" class="mb-5 flex gap-3 rounded-xl border border-amber-500/25 bg-amber-500/10 p-4 text-sm text-amber-100">
          <span class="material-symbols-outlined">warning</span>
          <p>Phòng đang có <b>{{ selectedRoom.future_showtimes_count }} suất chiếu tương lai</b>. Bạn vẫn có thể thiết kế, nhưng hệ thống sẽ không cho đổi hoặc ẩn ghế đã bán vé.</p>
        </div>

        <div class="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-5">
          <div class="seat-metric"><span>Tổng hoạt động</span><b>{{ activeSeatCount }}</b></div>
          <div class="seat-metric standard"><span>Ghế thường</span><b>{{ seatCounts.standard }}</b></div>
          <div class="seat-metric vip"><span>Ghế VIP</span><b>{{ seatCounts.vip }}</b></div>
          <div class="seat-metric couple"><span>Ghế đôi</span><b>{{ seatCounts.couple }}</b></div>
          <div class="seat-metric inactive"><span>Lối đi / Ẩn</span><b>{{ seatCounts.inactive }}</b></div>
        </div>

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
            <span class="mx-1 hidden h-10 w-px bg-white/10 sm:block"></span>
            <button type="button" class="utility-button" :disabled="undoStack.length === 0" @click="undo"><span class="material-symbols-outlined">undo</span>Hoàn tác</button>
            <button type="button" class="utility-button" :disabled="!isDirty" @click="restoreSaved"><span class="material-symbols-outlined">history</span>Khôi phục</button>
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
                    : cell.typeCode === 'COUPLE' ? `couple-seat border-pink-800 bg-pink-500 text-white shadow-pink-500/20 hover:shadow-pink-500/40 ${coupleVisualPosition(cell)}`
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
            {{ isDirty ? 'Sơ đồ có thay đổi chưa được lưu.' : 'Sơ đồ hiện đã đồng bộ với hệ thống.' }}
          </p>
          <button class="action-primary !w-auto px-10 py-3 text-base flex items-center gap-2" :disabled="seatLayoutSaving || !isDirty || activeSeatCount === 0" @click="saveSeatLayout">
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

.format-badge {
  border: 1px solid rgba(56, 189, 248, 0.32);
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.12);
  padding: 0.25rem 0.6rem;
  color: #7dd3fc;
  font-size: 0.72rem;
  font-weight: 900;
}

.preset-button, .utility-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.04);
  padding: 0.65rem 0.9rem;
  color: #ddd;
  font-size: 0.78rem;
  font-weight: 800;
  transition: 0.18s ease;
}

.preset-button:hover, .utility-button:hover:not(:disabled) {
  border-color: rgba(229, 9, 20, 0.4);
  background: rgba(229, 9, 20, 0.08);
  color: #fff;
}

.preset-panel {
  display: grid;
  gap: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.9rem;
  background: rgba(0, 0, 0, 0.18);
  padding: 1rem;
}

.preset-choice {
  position: relative;
  display: flex;
  min-height: 70px;
  align-items: center;
  gap: 0.6rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.035);
  padding: 0.7rem;
  color: #d4d4d4;
  text-align: left;
  transition: 0.18s ease;
}
.preset-choice:hover { transform: translateY(-1px); border-color: rgba(229, 9, 20, 0.45); background: rgba(229, 9, 20, 0.07); }
.preset-choice.active { border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.08); }
.preset-choice > .material-symbols-outlined { color: #fb7185; font-size: 1.45rem; }
.preset-choice b, .preset-choice small { display: block; }
.preset-choice b { color: #f4f4f5; font-size: 0.8rem; }
.preset-choice small { margin-top: 0.15rem; color: #999; font-size: 0.65rem; }
.preset-choice em { position: absolute; right: 0.4rem; top: 0.35rem; color: #7dd3fc; font-size: 0.52rem; font-style: normal; font-weight: 900; text-transform: uppercase; }

.utility-button:disabled { cursor: not-allowed; opacity: 0.35; }
.utility-button .material-symbols-outlined, .preset-button .material-symbols-outlined { font-size: 1.1rem; }

.seat-metric {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.8rem;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.8rem 1rem;
}
.seat-metric span { display: block; color: #929292; font-size: 0.65rem; font-weight: 800; text-transform: uppercase; }
.seat-metric b { color: #f5f5f5; font-size: 1.2rem; }
.seat-metric.standard b { color: #cbd5e1; }
.seat-metric.vip b { color: #fb7185; }
.seat-metric.couple b { color: #f472b6; }
.seat-metric.inactive b { color: #a1a1aa; }

.couple-seat {
  width: 44px !important;
  min-width: 44px !important;
  background: linear-gradient(180deg, #e84b9a 0%, #d52c82 78%, #a91761 100%) !important;
  border-color: #9d174d !important;
  border-bottom-color: #831843 !important;
  box-shadow: inset 0 5px 0 rgba(255,255,255,.1), 0 5px 10px rgba(219,39,119,.12);
}
.couple-seat.couple-left {
  z-index: 2;
  border-right-width: 0;
  border-radius: 11px 2px 2px 5px;
}
.couple-seat.couple-right {
  border-left-color: rgba(255,255,255,.18) !important;
  border-radius: 2px 11px 5px 2px;
}
.couple-seat.couple-left::after {
  content: '';
  position: absolute;
  right: -9px;
  top: -1px;
  bottom: -4px;
  width: 10px;
  background: linear-gradient(180deg, #e84b9a 0%, #d52c82 78%, #831843 100%);
  border-top: 1px solid #9d174d;
  border-bottom: 4px solid #831843;
}
.couple-seat.couple-single { border-radius: 11px 11px 5px 5px; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

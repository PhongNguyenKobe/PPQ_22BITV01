export type SeatGapInput = {
  id: string
  row: string
  number: number
  status: 'available' | 'selected' | 'occupied'
}

function singleAvailableSeatIds(seats: SeatGapInput[], unavailableIds: Set<string>): Set<string> {
  const rows = new Map<string, SeatGapInput[]>()
  for (const seat of seats) {
    const row = rows.get(seat.row) || []
    row.push(seat)
    rows.set(seat.row, row)
  }

  const singles = new Set<string>()
  const collectSegment = (segment: SeatGapInput[]) => {
    let availableRun: string[] = []
    for (const seat of segment) {
      if (unavailableIds.has(seat.id)) {
        if (availableRun.length === 1) singles.add(availableRun[0])
        availableRun = []
      } else {
        availableRun.push(seat.id)
      }
    }
    if (availableRun.length === 1) singles.add(availableRun[0])
  }

  for (const rowSeats of rows.values()) {
    const ordered = [...rowSeats].sort((a, b) => a.number - b.number)
    let segment: SeatGapInput[] = []
    for (const seat of ordered) {
      if (segment.length && seat.number !== segment[segment.length - 1].number + 1) {
        collectSegment(segment)
        segment = []
      }
      segment.push(seat)
    }
    collectSegment(segment)
  }
  return singles
}

export function leavesNewSingleSeatGap(seats: SeatGapInput[], selectedIds: Set<string>): boolean {
  const occupiedIds = new Set(seats.filter(seat => seat.status === 'occupied').map(seat => seat.id))
  const before = singleAvailableSeatIds(seats, occupiedIds)
  const after = singleAvailableSeatIds(seats, new Set([...occupiedIds, ...selectedIds]))
  return [...after].some(id => !before.has(id))
}

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { checkoutService, movieService, type Showtime, type Seat, type UserTicket } from '~/services/api'
import { isShowtimeExpired } from '~/utils/showtime'

export const useTicketsStore = defineStore('tickets', () => {
  const selectedMovie = ref<any>(null) // Product/Movie to book
  const selectedCinema = ref<string>('') // Cinema branch name
  const selectedShowtime = ref<Showtime | null>(null)
  const selectedSeats = ref<Seat[]>([])
  const ticketHistory = ref<UserTicket[]>([])
  const loading = ref(false)
  const purchaseError = ref('')
  const holdExpiresAt = ref<string | null>(null)
  const holdError = ref('')

  // Initialize from client-side localStorage if available
  if (process.client) {
    const savedHistory = localStorage.getItem('cineai_ticket_history')
    if (savedHistory) {
      try {
        ticketHistory.value = JSON.parse(savedHistory)
      } catch (e) {
        localStorage.removeItem('cineai_ticket_history')
      }
    }
  }

  const totalAmount = computed(() => {
    return selectedSeats.value.reduce((sum, seat) => sum + seat.price, 0)
  })

  function selectShowtime(showtime: Showtime) {
    selectedShowtime.value = showtime
    if (selectedMovie.value) {
      selectedMovie.value = {
        ...selectedMovie.value,
        price: showtime.price / 1000,
      }
    }
    selectedSeats.value = [] // Reset seats when showtime changes
    purchaseError.value = ''
    holdExpiresAt.value = null
    holdError.value = ''
  }

  async function toggleSeat(seat: Seat) {
    if (!selectedShowtime.value) return false
    const idx = selectedSeats.value.findIndex(s => s.id === seat.id)
    const nextSeats = [...selectedSeats.value]
    if (idx >= 0) {
      nextSeats.splice(idx, 1)
    } else {
      nextSeats.push(seat)
    }
    holdError.value = ''
    try {
      if (nextSeats.length) {
        const hold = await movieService.holdSeats(
          selectedShowtime.value.id,
          nextSeats.map((item) => item.id),
        )
        holdExpiresAt.value = hold.expires_at
      } else {
        await movieService.releaseSeatHolds(selectedShowtime.value.id)
        holdExpiresAt.value = null
      }
      selectedSeats.value = nextSeats
      return true
    } catch (e: any) {
      holdError.value = e?.message || 'Không thể giữ ghế. Ghế có thể vừa được khách khác chọn.'
      return false
    }
  }

  function selectMovie(movie: any) {
    selectedMovie.value = movie
    selectedCinema.value = ''
    selectedShowtime.value = null
    selectedSeats.value = []
  }

  function selectCinema(cinema: string) {
    selectedCinema.value = cinema
    selectedShowtime.value = null
    selectedSeats.value = []
  }

  function clearSelection() {
    const showtimeId = selectedShowtime.value?.id
    if (showtimeId) void movieService.releaseSeatHolds(showtimeId).catch(() => undefined)
    selectedMovie.value = null
    selectedCinema.value = ''
    selectedShowtime.value = null
    selectedSeats.value = []
    purchaseError.value = ''
    holdExpiresAt.value = null
    holdError.value = ''
  }

  async function purchaseTickets(paymentMethod: string): Promise<UserTicket | null> {
    if (!selectedShowtime.value || selectedSeats.value.length === 0) {
      return null
    }
    if (isShowtimeExpired(selectedShowtime.value)) {
      purchaseError.value = 'Đã hết thời gian mua vé cho suất chiếu này. Vui lòng chọn suất khác.'
      return null
    }

    loading.value = true
    purchaseError.value = ''
    try {
      const ticket = await checkoutService.processPayment({
        showtimeId: selectedShowtime.value.id,
        seats: selectedSeats.value.map(s => s.id),
        seatLabels: selectedSeats.value.map(s => `${s.row}${s.number}`),
        paymentMethod,
        totalAmount: totalAmount.value
      })

      // Prepend to history
      ticketHistory.value.unshift(ticket)
      
      if (process.client) {
        localStorage.setItem('cineai_ticket_history', JSON.stringify(ticketHistory.value))
      }

      // Clear the selections
      clearSelection()

      return ticket
    } catch (e: any) {
      purchaseError.value =
        e?.status === 404 || e?.status === 409
          ? 'Suất chiếu đã hết hạn hoặc ngừng bán vé. Vui lòng chọn suất khác.'
          : e?.message || 'Thanh toán không thành công. Vui lòng thử lại.'
      console.error('Payment failed:', e)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    selectedMovie,
    selectedCinema,
    selectedShowtime,
    selectedSeats,
    ticketHistory,
    loading,
    purchaseError,
    holdExpiresAt,
    holdError,
    totalAmount,
    selectMovie,
    selectCinema,
    selectShowtime,
    toggleSeat,
    clearSelection,
    purchaseTickets
  }
})

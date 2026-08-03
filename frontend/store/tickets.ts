import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { checkoutService, movieService, usersApi, type Showtime, type Seat, type UserTicket, type CinemaCombo } from '~/services/api'
import { isShowtimeExpired } from '~/utils/showtime'

export const useTicketsStore = defineStore('tickets', () => {
  const selectedMovie = ref<any>(null) // Product/Movie to book
  const selectedCinema = ref<string>('') // Cinema branch name
  const selectedShowtime = ref<Showtime | null>(null)
  const selectedSeats = ref<Seat[]>([])
  const selectedCombos = ref<Array<{ combo: CinemaCombo; quantity: number }>>([])
  const ticketHistory = ref<UserTicket[]>([])
  const loading = ref(false)
  const purchaseError = ref('')
  const holdExpiresAt = ref<string | null>(null)
  const holdError = ref('')
  const historyLoading = ref(false)
  const historyError = ref('')

  // Dữ liệu checkout cũng tách theo từng tab để hai tài khoản không dùng chung đơn.
  if (process.client) {
    localStorage.removeItem('cineai_checkout_selection')
    localStorage.removeItem('cineai_ticket_history')
    const savedSelection = sessionStorage.getItem('cineai_checkout_selection')
    if (savedSelection) {
      try {
        const parsed = JSON.parse(savedSelection)
        selectedMovie.value = parsed.selectedMovie || null
        selectedCinema.value = parsed.selectedCinema || ''
        selectedShowtime.value = parsed.selectedShowtime || null
        selectedSeats.value = Array.isArray(parsed.selectedSeats) ? parsed.selectedSeats : []
        selectedCombos.value = Array.isArray(parsed.selectedCombos) ? parsed.selectedCombos : []
        holdExpiresAt.value = parsed.holdExpiresAt || null
      } catch {
        sessionStorage.removeItem('cineai_checkout_selection')
      }
    }
    const savedHistory = sessionStorage.getItem('cineai_ticket_history')
    if (savedHistory) {
      try {
        ticketHistory.value = JSON.parse(savedHistory)
      } catch (e) {
        sessionStorage.removeItem('cineai_ticket_history')
      }
    }
    watch(
      [selectedMovie, selectedCinema, selectedShowtime, selectedSeats, selectedCombos, holdExpiresAt],
      () => sessionStorage.setItem('cineai_checkout_selection', JSON.stringify({
        selectedMovie: selectedMovie.value,
        selectedCinema: selectedCinema.value,
        selectedShowtime: selectedShowtime.value,
        selectedSeats: selectedSeats.value,
        selectedCombos: selectedCombos.value,
        holdExpiresAt: holdExpiresAt.value,
      })),
      { deep: true },
    )
  }

  const totalAmount = computed(() => {
    return selectedSeats.value.reduce((sum, seat) => sum + seat.price, 0)
      + selectedCombos.value.reduce((sum, item) => sum + Number(item.combo.price) * item.quantity, 0)
  })
  function setComboQuantity(combo: CinemaCombo, quantity: number) {
    selectedCombos.value = selectedCombos.value.filter(item => item.combo.id !== combo.id)
    if (quantity > 0) selectedCombos.value.push({ combo, quantity })
  }

  async function loadTicketHistory() {
    historyLoading.value = true
    historyError.value = ''
    try {
      ticketHistory.value = await usersApi.getMyTickets()
      if (process.client) {
        sessionStorage.setItem('cineai_ticket_history', JSON.stringify(ticketHistory.value))
      }
    } catch (e: any) {
      historyError.value = e?.message || 'Không thể tải lịch sử vé.'
    } finally {
      historyLoading.value = false
    }
  }

  async function requestCancellation(bookingId: string, reason: string) {
    await usersApi.requestTicketCancellation(bookingId, reason)
    await loadTicketHistory()
  }

  function selectShowtime(showtime: Showtime) {
    selectedShowtime.value = showtime
    if (selectedMovie.value) {
      selectedMovie.value = {
        ...selectedMovie.value,
        price: showtime.price / 1000,
      }
    }
    selectedSeats.value = [] // Reset seats when showtime changes
    selectedCombos.value = []
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

  async function releaseCurrentSeatHolds() {
    const showtimeId = selectedShowtime.value?.id
    if (showtimeId && (selectedSeats.value.length > 0 || holdExpiresAt.value)) {
      await movieService.releaseSeatHolds(showtimeId).catch(() => undefined)
    }
    selectedSeats.value = []
    holdExpiresAt.value = null
    holdError.value = ''
  }

  function selectMovie(movie: any) {
    selectedMovie.value = movie
    selectedCinema.value = ''
    selectedShowtime.value = null
    selectedSeats.value = []
    selectedCombos.value = []
  }

  function selectCinema(cinema: string) {
    selectedCinema.value = cinema
    selectedShowtime.value = null
    selectedSeats.value = []
    selectedCombos.value = []
  }

  function clearSelection() {
    const showtimeId = selectedShowtime.value?.id
    if (showtimeId) void movieService.releaseSeatHolds(showtimeId).catch(() => undefined)
    selectedMovie.value = null
    selectedCinema.value = ''
    selectedShowtime.value = null
    selectedSeats.value = []
    selectedCombos.value = []
    purchaseError.value = ''
    holdExpiresAt.value = null
    holdError.value = ''
  }

  async function purchaseTickets(paymentMethod: string, promotionCode?: string, payableAmount?: number): Promise<UserTicket | null> {
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
        movieTitle: selectedMovie.value?.title,
        poster: selectedMovie.value?.poster,
        branchName: selectedShowtime.value.branchName,
        screenName: selectedShowtime.value.screenName,
        date: selectedShowtime.value.date,
        time: selectedShowtime.value.time,
        paymentMethod,
        totalAmount: payableAmount ?? totalAmount.value,
        promotionCode,
      })

      // Prepend to history
      ticketHistory.value.unshift(ticket)
      
      if (process.client) {
        sessionStorage.setItem('cineai_ticket_history', JSON.stringify(ticketHistory.value))
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

  async function startVnpayPayment(
    promotionCode?: string,
    payableAmount?: number,
  ): Promise<{ paymentUrl: string; transactionRef: string } | null> {
    if (!selectedShowtime.value || selectedSeats.value.length === 0) {
      purchaseError.value = 'Vui lòng chọn suất chiếu và ghế trước khi thanh toán.'
      return null
    }
    if (isShowtimeExpired(selectedShowtime.value)) {
      purchaseError.value = 'Đã hết thời gian mua vé cho suất chiếu này. Vui lòng chọn suất khác.'
      return null
    }

    loading.value = true
    purchaseError.value = ''
    try {
      const payment = await checkoutService.createVnpayPayment({
        showtimeId: selectedShowtime.value.id,
        seats: selectedSeats.value.map((seat) => seat.id),
        totalAmount: payableAmount ?? totalAmount.value,
        promotionCode,
        comboItems: selectedCombos.value.map(item => ({ combo_id: item.combo.id, quantity: item.quantity })),
      })
      return payment
    } catch (e: any) {
      purchaseError.value =
        e?.status === 404 || e?.status === 409
          ? 'Suất chiếu đã hết hạn hoặc ngừng bán vé. Vui lòng chọn suất khác.'
          : e?.message || 'Không thể khởi tạo thanh toán VNPAY. Vui lòng thử lại.'
      console.error('VNPAY payment initialization failed:', e)
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
    selectedCombos,
    ticketHistory,
    loading,
    purchaseError,
    holdExpiresAt,
    holdError,
    historyLoading,
    historyError,
    totalAmount,
    setComboQuantity,
    selectMovie,
    selectCinema,
    selectShowtime,
    toggleSeat,
    releaseCurrentSeatHolds,
    clearSelection,
    purchaseTickets,
    startVnpayPayment,
    loadTicketHistory,
    requestCancellation,
  }
})

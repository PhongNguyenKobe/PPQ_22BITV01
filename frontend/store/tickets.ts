import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { checkoutService, mockTickets, type Showtime, type Seat, type UserTicket } from '~/services/api'

export const useTicketsStore = defineStore('tickets', () => {
  const selectedMovie = ref<any>(null) // Product/Movie to book
  const selectedCinema = ref<string>('') // Cinema branch name
  const selectedShowtime = ref<Showtime | null>(null)
  const selectedSeats = ref<Seat[]>([])
  const ticketHistory = ref<UserTicket[]>([...mockTickets])
  const loading = ref(false)

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
    selectedSeats.value = [] // Reset seats when showtime changes
  }

  function toggleSeat(seat: Seat) {
    const idx = selectedSeats.value.findIndex(s => s.id === seat.id)
    if (idx >= 0) {
      selectedSeats.value.splice(idx, 1)
    } else {
      selectedSeats.value.push(seat)
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
    selectedMovie.value = null
    selectedCinema.value = ''
    selectedShowtime.value = null
    selectedSeats.value = []
  }

  async function purchaseTickets(paymentMethod: string): Promise<UserTicket | null> {
    if (!selectedShowtime.value || selectedSeats.value.length === 0) {
      return null
    }

    loading.value = true
    try {
      const ticket = await checkoutService.processPayment({
        showtimeId: selectedShowtime.value.id,
        seats: selectedSeats.value.map(s => `${s.row}${s.number}`),
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
    } catch (e) {
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
    totalAmount,
    selectMovie,
    selectCinema,
    selectShowtime,
    toggleSeat,
    clearSelection,
    purchaseTickets
  }
})

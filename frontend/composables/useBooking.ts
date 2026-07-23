import { ref, computed } from 'vue'
import { useTicketsStore } from '~/store/tickets'
import type { Showtime, Seat } from '~/services/api'

export const useBooking = () => {
  const ticketsStore = useTicketsStore()
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const selectedMovie = computed(() => ticketsStore.selectedMovie)
  const selectedShowtime = computed(() => ticketsStore.selectedShowtime)
  const selectedSeats = computed(() => ticketsStore.selectedSeats)
  const totalAmount = computed(() => ticketsStore.totalAmount)

  const selectMovie = (movie: any) => {
    ticketsStore.selectedMovie = movie
  }

  const selectShowtime = (showtime: Showtime) => {
    ticketsStore.selectedShowtime = showtime
  }

  const selectSeats = (seats: Seat[]) => {
    if (seats.length > 10) {
      error.value = 'Maximum 10 seats per booking'
      return false
    }
    ticketsStore.selectedSeats = seats
    error.value = null
    return true
  }

  const toggleSeat = (seat: Seat) => {
    const index = selectedSeats.value.findIndex(s => s.id === seat.id)
    if (index >= 0) {
      selectedSeats.value.splice(index, 1)
    } else {
      if (selectedSeats.value.length >= 10) {
        error.value = 'Maximum 10 seats per booking'
        return false
      }
      selectedSeats.value.push(seat)
    }
    error.value = null
    return true
  }

  const isValidBooking = computed(() => {
    return selectedMovie.value && 
           selectedShowtime.value && 
           selectedSeats.value.length > 0
  })

  const resetBooking = () => {
    ticketsStore.selectedMovie = null
    ticketsStore.selectedShowtime = null
    ticketsStore.selectedSeats = []
    error.value = null
  }

  return {
    isLoading,
    error,
    selectedMovie,
    selectedShowtime,
    selectedSeats,
    totalAmount,
    isValidBooking,
    selectMovie,
    selectShowtime,
    selectSeats,
    toggleSeat,
    resetBooking
  }
}

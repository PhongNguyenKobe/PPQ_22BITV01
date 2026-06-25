import { d as defineStore } from './server.mjs';
import { ref, computed } from 'vue';
import { m as mockTickets, c as checkoutService } from './api-rwjTvGO1.mjs';

const useTicketsStore = defineStore("tickets", () => {
  const selectedShowtime = ref(null);
  const selectedSeats = ref([]);
  const ticketHistory = ref([...mockTickets]);
  const loading = ref(false);
  const totalAmount = computed(() => {
    return selectedSeats.value.reduce((sum, seat) => sum + seat.price, 0);
  });
  function selectShowtime(showtime) {
    selectedShowtime.value = showtime;
    selectedSeats.value = [];
  }
  function toggleSeat(seat) {
    const idx = selectedSeats.value.findIndex((s) => s.id === seat.id);
    if (idx >= 0) {
      selectedSeats.value.splice(idx, 1);
    } else {
      selectedSeats.value.push(seat);
    }
  }
  function clearSelection() {
    selectedShowtime.value = null;
    selectedSeats.value = [];
  }
  async function purchaseTickets(paymentMethod) {
    if (!selectedShowtime.value || selectedSeats.value.length === 0) {
      return null;
    }
    loading.value = true;
    try {
      const ticket = await checkoutService.processPayment({
        showtimeId: selectedShowtime.value.id,
        seats: selectedSeats.value.map((s) => `${s.row}${s.number}`),
        paymentMethod,
        totalAmount: totalAmount.value
      });
      ticketHistory.value.unshift(ticket);
      if (false) ;
      clearSelection();
      return ticket;
    } catch (e) {
      console.error("Payment failed:", e);
      return null;
    } finally {
      loading.value = false;
    }
  }
  return {
    selectedShowtime,
    selectedSeats,
    ticketHistory,
    loading,
    totalAmount,
    selectShowtime,
    toggleSeat,
    clearSelection,
    purchaseTickets
  };
});

export { useTicketsStore as u };
//# sourceMappingURL=tickets-DLGytZJQ.mjs.map

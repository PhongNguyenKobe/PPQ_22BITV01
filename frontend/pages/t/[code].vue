<script setup lang="ts">
const route = useRoute()
const apiBase = import.meta.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'
const { data: ticket, error } = await useFetch<any>(`${apiBase}/bookings/tickets/verify/${encodeURIComponent(String(route.params.code))}`, { server: false })
const labels: Record<string, string> = { VALID: 'Vé hợp lệ', TOO_EARLY: 'Chưa đến giờ soát vé', ALREADY_USED: 'Vé đã sử dụng', EXPIRED: 'Vé đã hết hạn', CANCELLED: 'Vé đã hủy', NOT_CONFIRMED: 'Vé chưa xác nhận' }
</script>

<template>
  <main class="mx-auto min-h-screen max-w-lg px-4 py-10">
    <section v-if="ticket" class="overflow-hidden rounded-3xl border border-white/10 bg-surface-container shadow-2xl">
      <img v-if="ticket.poster_url" :src="ticket.poster_url" :alt="ticket.movie_title" class="h-52 w-full object-cover">
      <div class="space-y-5 p-6">
        <div><p class="text-sm font-bold text-primary">{{ labels[ticket.state] || ticket.state }}</p><h1 class="mt-1 text-2xl font-black">{{ ticket.movie_title }}</h1><p class="mt-1 font-mono text-sm text-on-surface-variant">{{ ticket.ticket_code }}</p></div>
        <dl class="grid grid-cols-2 gap-4 text-sm">
          <div><dt class="text-on-surface-variant">Rạp</dt><dd class="font-bold">{{ ticket.branch_name }}</dd></div>
          <div><dt class="text-on-surface-variant">Phòng</dt><dd class="font-bold">{{ ticket.auditorium_name }}</dd></div>
          <div><dt class="text-on-surface-variant">Ghế</dt><dd class="text-xl font-black text-primary">{{ ticket.seats?.join(', ') }}</dd></div>
          <div><dt class="text-on-surface-variant">Suất chiếu</dt><dd class="font-bold">{{ new Date(ticket.starts_at).toLocaleString('vi-VN') }}</dd></div>
        </dl>
        <p class="text-xs text-on-surface-variant">Trang chỉ hiển thị thông tin vé, không chứa email hoặc số điện thoại khách hàng.</p>
      </div>
    </section>
    <section v-else class="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-center text-red-300">{{ error ? 'Không tìm thấy hoặc mã vé không hợp lệ.' : 'Đang tải thông tin vé...' }}</section>
  </main>
</template>

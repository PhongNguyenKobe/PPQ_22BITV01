<script setup lang="ts">
definePageMeta({ layout: 'default' })
useSeoMeta({ title: 'Trung tâm hỗ trợ - CineAI', description: 'Hướng dẫn đặt vé, thanh toán, sử dụng vé QR và xử lý sự cố trên CineAI.' })

const faqs = [
  ['Tôi đặt vé như thế nào?', 'Chọn phim, rạp, suất chiếu và ghế; đăng nhập, kiểm tra đơn hàng rồi hoàn tất thanh toán. Vé điện tử sẽ xuất hiện trong mục Vé của tôi sau khi thanh toán thành công.'],
  ['Tôi chưa nhận được vé?', 'Hãy kiểm tra trạng thái giao dịch và tải lại mục Vé của tôi. Nếu tiền đã trừ nhưng vé chưa được phát hành, vui lòng gửi mã giao dịch cho bộ phận hỗ trợ.'],
  ['Có thể hủy vé không?', 'Đơn đủ điều kiện có thể yêu cầu hủy trước giờ chiếu tối thiểu 120 phút, miễn là vé chưa được check-in. Khả năng hoàn tiền còn phụ thuộc trạng thái thanh toán.'],
  ['Dùng vé QR tại rạp ra sao?', 'Mở Vé của tôi và đưa mã QR cho nhân viên soát vé. Không đăng công khai ảnh QR vì mỗi vé chỉ được sử dụng theo trạng thái hợp lệ của hệ thống.'],
  ['Mã khuyến mãi không áp dụng được?', 'Kiểm tra thời hạn, giá trị đơn tối thiểu, rạp/phim áp dụng, phương thức thanh toán và giới hạn lượt dùng của chương trình.'],
]
</script>

<template>
  <InfoPageShell eyebrow="CineAI Care" title="Trung tâm hỗ trợ" description="Tìm câu trả lời nhanh cho những vấn đề thường gặp trong quá trình chọn phim, đặt ghế, thanh toán và sử dụng vé." icon="support_agent">
    <div class="info-grid">
      <NuxtLink to="/phim" class="info-card transition hover:-translate-y-1 hover:border-red-500/40"><span class="material-symbols-outlined text-3xl text-red-400">confirmation_number</span><h2 class="mt-4">Đặt vé</h2><p class="mt-2">Chọn phim và bắt đầu lại quy trình đặt vé.</p></NuxtLink>
      <NuxtLink to="/profile/tickets" class="info-card transition hover:-translate-y-1 hover:border-red-500/40"><span class="material-symbols-outlined text-3xl text-amber-300">qr_code_2</span><h2 class="mt-4">Vé của tôi</h2><p class="mt-2">Xem mã vé, trạng thái và lịch sử đặt chỗ.</p></NuxtLink>
      <NuxtLink to="/contact" class="info-card transition hover:-translate-y-1 hover:border-red-500/40"><span class="material-symbols-outlined text-3xl text-sky-300">forum</span><h2 class="mt-4">Liên hệ hỗ trợ</h2><p class="mt-2">Gửi thông tin để được hỗ trợ trực tiếp.</p></NuxtLink>
    </div>
    <section class="mt-14 max-w-4xl">
      <p class="text-xs font-black uppercase tracking-[.2em] text-red-400">Câu hỏi thường gặp</p>
      <div class="mt-5 space-y-3">
        <details v-for="item in faqs" :key="item[0]" class="group rounded-2xl border border-white/10 bg-[#181a1b] p-5 open:border-red-500/30">
          <summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-black"><span>{{ item[0] }}</span><span class="material-symbols-outlined transition group-open:rotate-180">expand_more</span></summary>
          <p class="mt-4 border-t border-white/5 pt-4 leading-7 text-white/55">{{ item[1] }}</p>
        </details>
      </div>
    </section>
  </InfoPageShell>
</template>

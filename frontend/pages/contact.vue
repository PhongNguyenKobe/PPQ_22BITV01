<script setup lang="ts">
definePageMeta({ layout: 'default' })
useSeoMeta({ title: 'Liên hệ - CineAI', description: 'Thông tin liên hệ và hướng dẫn gửi yêu cầu hỗ trợ đến CineAI.' })

const subject = ref('Hỗ trợ đơn hàng CineAI')
const message = ref('')
const mailLink = computed(() => `mailto:support@cineai.vn?subject=${encodeURIComponent(subject.value)}&body=${encodeURIComponent(message.value)}`)
</script>

<template>
  <InfoPageShell eyebrow="Kết nối với chúng tôi" title="Liên hệ CineAI" description="Cho chúng tôi biết vấn đề bạn gặp phải. Với yêu cầu về giao dịch, hãy chuẩn bị mã đơn hàng hoặc mã thanh toán để được kiểm tra nhanh hơn." icon="contact_support">
    <div class="info-grid">
      <a href="tel:19001234" class="info-card transition hover:border-red-500/40"><span class="material-symbols-outlined text-3xl text-red-400">call</span><h2 class="mt-4">Hotline</h2><p class="mt-2 text-lg font-black text-white">1900 1234</p><p class="mt-1 text-sm">Hỗ trợ các vấn đề đặt vé và thanh toán.</p></a>
      <a href="mailto:support@cineai.vn" class="info-card transition hover:border-red-500/40"><span class="material-symbols-outlined text-3xl text-sky-300">mail</span><h2 class="mt-4">Email</h2><p class="mt-2 break-all text-lg font-black text-white">support@cineai.vn</p><p class="mt-1 text-sm">Phù hợp khi cần gửi ảnh hoặc mã giao dịch.</p></a>
      <div class="info-card"><span class="material-symbols-outlined text-3xl text-amber-300">location_on</span><h2 class="mt-4">Khu vực vận hành</h2><p class="mt-2 text-lg font-black text-white">TP. Hồ Chí Minh</p><p class="mt-1 text-sm">Việt Nam</p></div>
    </div>
    <section class="mt-12 grid gap-8 rounded-3xl border border-white/10 bg-[#181a1b] p-6 md:grid-cols-[.8fr_1.2fr] md:p-10">
      <div><p class="text-xs font-black uppercase tracking-[.2em] text-red-400">Gửi yêu cầu</p><h2 class="mt-3 text-3xl font-black">Chuẩn bị email hỗ trợ</h2><p class="mt-4 leading-7 text-white/55">Không gửi mật khẩu, mã OTP hoặc thông tin thẻ. Với đơn hàng, chỉ cần mã đơn, thời gian giao dịch và mô tả vấn đề.</p></div>
      <div class="space-y-4"><label class="block"><span class="mb-2 block text-sm font-bold">Tiêu đề</span><input v-model="subject" class="w-full rounded-xl border border-white/10 bg-black/25 px-4 py-3 outline-none focus:border-red-500" /></label><label class="block"><span class="mb-2 block text-sm font-bold">Nội dung</span><textarea v-model="message" rows="5" placeholder="Ví dụ: Mã đơn hàng, thời gian thanh toán và vấn đề cần hỗ trợ..." class="w-full rounded-xl border border-white/10 bg-black/25 px-4 py-3 outline-none focus:border-red-500" /></label><a :href="mailLink" class="inline-flex items-center gap-2 rounded-xl bg-red-600 px-6 py-3 font-black transition hover:bg-red-500"><span class="material-symbols-outlined">send</span>Mở ứng dụng email</a></div>
    </section>
  </InfoPageShell>
</template>

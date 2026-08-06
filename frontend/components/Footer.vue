<script setup lang="ts">
const currentYear = new Date().getFullYear()

const navigationLinks = [
  { name: 'Sản phẩm', to: '/products' },
  { name: 'Lịch chiếu', to: '/showtimes' },
  { name: 'Rạp chiếu', to: '/cinemas' },
  { name: 'AI Discovery', to: '/ai-discovery' }
]

const supportLinks = [
  { name: 'Trung tâm hỗ trợ', to: '/support' },
  { name: 'Điều khoản dịch vụ', to: '/terms' },
  { name: 'Chính sách bảo mật', to: '/privacy' },
  { name: 'Liên hệ', to: '/contact' }
]

const socialLinks = [
  {
    name: 'Facebook',
    icon: 'facebook',
    href: 'https://facebook.com'
  },
  {
    name: 'Instagram',
    icon: 'photo_camera',
    href: 'https://instagram.com'
  },
  {
    name: 'YouTube',
    icon: 'play_circle',
    href: 'https://youtube.com'
  },
  {
    name: 'TikTok',
    icon: 'music_note',
    href: 'https://tiktok.com'
  }
]
</script>

<template>
  <footer
    class="mt-24 border-t border-glass-stroke bg-surface-container-lowest/90 backdrop-blur-xl"
  >
    <div
      class="mx-auto grid max-w-container-max gap-12 px-6 py-16 md:grid-cols-2 lg:grid-cols-4"
    >
      <!-- Brand -->
      <section>
        <NuxtLink
          to="/"
          class="text-3xl font-bold text-primary-container hover:opacity-90"
        >
          CineAI
        </NuxtLink>

        <p class="mt-5 text-sm leading-7 text-on-surface-variant">
          CineAI là nền tảng đặt vé xem phim thông minh ứng dụng Trí Tuệ Nhân Tạo,
          giúp người dùng khám phá phim phù hợp, đặt vé nhanh chóng và trải nghiệm
          điện ảnh hiện đại.
        </p>
      </section>

      <!-- Navigation -->
      <nav>
        <h3
          class="mb-5 text-sm font-bold uppercase tracking-wider text-on-surface"
        >
          Khám phá
        </h3>

        <ul class="space-y-3">
          <li
            v-for="item in navigationLinks"
            :key="item.to"
          >
            <NuxtLink
              :to="item.to"
              class="text-sm text-on-surface-variant transition hover:text-primary-container"
            >
              {{ item.name }}
            </NuxtLink>
          </li>
        </ul>
      </nav>

      <!-- Support -->
      <nav>
        <h3
          class="mb-5 text-sm font-bold uppercase tracking-wider text-on-surface"
        >
          Hỗ trợ
        </h3>

        <ul class="space-y-3">
          <li
            v-for="item in supportLinks"
            :key="item.to"
          >
            <NuxtLink
              :to="item.to"
              class="text-sm text-on-surface-variant transition hover:text-primary-container"
            >
              {{ item.name }}
            </NuxtLink>
          </li>
        </ul>
      </nav>

      <!-- Contact -->
      <section>
        <h3
          class="mb-5 text-sm font-bold uppercase tracking-wider text-on-surface"
        >
          Liên hệ
        </h3>

        <ul class="space-y-4 text-sm text-on-surface-variant">
          <li class="flex items-center gap-3">
            <span class="material-symbols-outlined text-lg">
              call
            </span>

            1900 1234
          </li>

          <li class="flex items-center gap-3">
            <span class="material-symbols-outlined text-lg">
              mail
            </span>

            support@cineai.vn
          </li>

          <li class="flex items-start gap-3">
            <span class="material-symbols-outlined text-lg">
              location_on
            </span>

            TP. Hồ Chí Minh, Việt Nam
          </li>
        </ul>

        <!-- Social -->

        <div class="mt-8 flex gap-4">
          <a
            v-for="social in socialLinks"
            :key="social.name"
            :href="social.href"
            target="_blank"
            rel="noopener noreferrer"
            class="flex h-11 w-11 items-center justify-center rounded-full border border-glass-stroke bg-surface-container hover:bg-primary-container hover:text-on-primary-container transition-all duration-300 hover:scale-110"
          >
            <span class="material-symbols-outlined">
              {{ social.icon }}
            </span>
          </a>
        </div>
      </section>
    </div>

    <!-- SEO Text block to improve Text/HTML ratio -->
    <div class="mx-auto max-w-6xl px-6 pt-4 pb-8 border-t border-glass-stroke/30 text-[10px] leading-relaxed text-on-surface-variant/40 space-y-3">
      <h4 class="font-bold text-on-surface-variant/60 uppercase tracking-wider">CineAI - Hệ thống Rạp Chiếu Phim Đỉnh Cao Tích Hợp Trí Tuệ Nhân Tạo</h4>
      <p>
        Chào mừng bạn đến với <strong>CineAI</strong>, cụm rạp chiếu phim hiện đại hàng đầu Việt Nam. Chúng tôi tự hào mang đến trải nghiệm điện ảnh đột phá nhờ tích hợp công nghệ trí tuệ nhân tạo (AI) giúp cá nhân hóa gợi ý phim, phân tích tâm trạng để chọn phim thích hợp (AI Mood Matcher), cùng tính năng đặt vé xem phim trực tuyến siêu tốc qua trợ lý ảo thông minh. Với hệ thống rạp chiếu đạt chuẩn quốc tế, phòng chiếu IMAX hiện đại, âm thanh Dolby Atmos sống động và ghế ngồi da cao cấp, CineAI cam kết là điểm đến giải trí lý tưởng cho gia đình và bạn bè.
      </p>
      <p>
        Mua vé xem phim trực tuyến tại CineAI vô cùng đơn giản và an toàn với nhiều phương thức thanh toán đa dạng như VNPAY, PayPal và các ví điện tử phổ biến. Đừng bỏ lỡ danh sách phim bom tấn hot nhất, lịch chiếu phim chi tiết của các chi nhánh rạp trên toàn quốc và các chương trình khuyến mãi, voucher giảm giá combo bắp nước độc quyền được cập nhật liên tục mỗi ngày. CineAI - Điện ảnh đỉnh cao trong tầm tay bạn.
      </p>
      <p>
        CineAI luôn tuân thủ nghiêm ngặt các quy định về phân loại độ tuổi người xem phim (P, K, T13, T16, T18) theo tiêu chuẩn của Bộ Văn hóa, Thể thao và Du lịch để đảm bảo môi trường giải trí lành mạnh, an toàn và văn minh. Khách hàng vui lòng xuất trình giấy tờ tùy thân hợp lệ khi đến rạp để nhân viên kiểm tra đối với các phim giới hạn độ tuổi. Về chính sách hoàn trả vé và đổi giờ chiếu, quý khách có thể dễ dàng thực hiện trực tiếp trên hệ thống tối thiểu 60 phút trước giờ phim khởi chiếu.
      </p>
    </div>

    <!-- Bottom -->

    <div
      class="border-t border-glass-stroke py-6 text-center text-sm text-on-surface-variant"
    >
      © {{ currentYear }}

      <span class="font-semibold text-primary-container">
        CineAI
      </span>

      • All Rights Reserved.

      <div class="mt-2 text-xs opacity-70">
        Designed & Developed with Nuxt 3 · Vue 3 · TailwindCSS
      </div>
    </div>
  </footer>
</template>
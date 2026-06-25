<template>
  <footer class="border-t border-glass-stroke bg-surface-container-lowest/80 backdrop-blur-md py-12 mt-auto">
    <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop flex flex-col md:flex-row justify-between items-center gap-6">
      <div>
        <h3 class="font-headline-md text-headline-md font-bold text-primary-container">CineAI</h3>
        <p class="text-sm text-on-surface-variant mt-2 max-w-sm">
          Trải nghiệm đặt vé xem phim thế hệ mới hỗ trợ bởi Trí Tuệ Nhân Tạo. Nhanh chóng, tiện lợi, và tối ưu hóa cho bạn.
        </p>
      </div>
      <div class="flex gap-8 text-sm text-on-surface-variant font-medium">
        <NuxtLink to="/movies" class="hover:text-primary transition-colors">Danh sách phim</NuxtLink>
        <a href="#" class="hover:text-primary transition-colors">Điều khoản dịch vụ</a>
        <a href="#" class="hover:text-primary transition-colors">Chính sách bảo mật</a>
        <a href="#" class="hover:text-primary transition-colors">Hỗ trợ khách hàng</a>
      </div>
    </div>
    <div class="max-w-container-max mx-auto px-6 md:px-margin-desktop text-center text-xs text-on-surface-variant mt-8 border-t border-glass-stroke/50 pt-6">
      &copy; 2026 CineAI System. Designed for Software Engineering Project. All rights reserved.
    </div>
  </footer>
</template>

<template>
  <footer class="w-full px-6 md:px-margin-desktop py-12 flex flex-col md:flex-row justify-between items-center gap-6 bg-surface-container-lowest border-t border-outline-variant/30">
    <div class="flex flex-col items-center md:items-start gap-4">
      <NuxtLink to="/" class="font-headline-md text-headline-md font-bold text-primary-container">CineAI</NuxtLink>
      <p class="font-body-md text-body-md text-on-surface-variant text-center md:text-left max-w-sm">
        &copy; 2026 CineAI Studios. Powered by Cinema Intelligence. Hệ thống rạp chiếu phim thông minh hàng đầu Việt Nam.
      </p>
    </div>
    <div class="flex flex-wrap justify-center gap-6">
      <a href="#" class="font-label-sm text-label-sm text-on-surface-variant hover:text-primary-container transition-colors">Chính sách bảo mật</a>
      <a href="#" class="font-label-sm text-label-sm text-on-surface-variant hover:text-primary-container transition-colors">Điều khoản dịch vụ</a>
      <a href="#" class="font-label-sm text-label-sm text-on-surface-variant hover:text-primary-container transition-colors">Cài đặt Cookie</a>
      <a href="#" class="font-label-sm text-label-sm text-on-surface-variant hover:text-primary-container transition-colors">Trung tâm hỗ trợ</a>
    </div>
    <div class="flex gap-4">
      <a href="#" class="w-10 h-10 rounded-full bg-surface-container border border-white/10 flex items-center justify-center hover:bg-primary-container group transition-all">
        <span class="material-symbols-outlined text-on-surface-variant group-hover:text-white text-xl">language</span>
      </a>
      <a href="#" class="w-10 h-10 rounded-full bg-surface-container border border-white/10 flex items-center justify-center hover:bg-primary-container group transition-all">
        <span class="material-symbols-outlined text-on-surface-variant group-hover:text-white text-xl">smart_toy</span>
      </a>
    </div>
  </footer>
</template>
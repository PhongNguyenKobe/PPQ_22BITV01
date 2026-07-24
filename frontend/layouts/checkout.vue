<template>
  <div class="min-h-screen bg-background flex flex-col">
    <!-- Header -->
    <header class="sticky top-0 z-40 h-20 bg-surface border-b border-glass-stroke flex items-center px-6">
      <NuxtLink to="/products" class="flex items-center gap-2">
        <span class="material-symbols-outlined text-2xl text-primary-container">local_movies</span>
        <h1 class="font-bold text-xl text-on-surface">CineAI - Đặt Vé</h1>
      </NuxtLink>
    </header>

    <!-- Main Content -->
    <main class="flex-1 max-w-6xl mx-auto w-full px-6 py-8">
      <div class="grid grid-cols-3 gap-6">
        <!-- Left: Checkout Steps -->
        <div class="col-span-2">
          <slot />
        </div>

        <!-- Right: Order Summary -->
        <div class="col-span-1">
          <div class="sticky top-32 bg-surface-container-high/80 backdrop-blur-sm border border-glass-stroke rounded-2xl p-6 space-y-4">
            <h3 class="font-bold text-lg text-on-surface">Tóm Tắt Đơn Hàng</h3>
            <slot name="summary" />
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="h-16 bg-surface-container-low border-t border-glass-stroke flex items-center justify-center text-xs text-on-surface-variant">
      © 2026 CineAI. Hỗ trợ: support@cineai.vn | 1800 1800
    </footer>
  </div>
</template>

<style scoped>
/* Checkout layout specific styles */
</style>

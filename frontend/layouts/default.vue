<template>
  <div class="flex flex-col min-h-screen bg-background text-on-surface">
    <!-- Main Header -->
    <Header />

    <!-- Main Content Slot -->
    <main class="flex-grow pt-[80px]">
      <slot />
    </main>

    <!-- Main Footer -->
    <Footer />

    <!-- AI Widgets (Only run on client browser) -->
    <ClientOnly>
      <FloatingAiChat />
    </ClientOnly>
  </div>
</template>

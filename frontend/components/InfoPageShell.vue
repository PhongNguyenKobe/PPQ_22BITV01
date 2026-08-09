<script setup lang="ts">
defineProps<{ eyebrow: string; title: string; description: string; icon: string }>()
</script>

<template>
  <main class="min-h-screen bg-[#0d0f10] text-white">
    <section class="relative overflow-hidden border-b border-white/5 px-5 py-20 md:py-28">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(229,9,20,.2),transparent_34%),radial-gradient(circle_at_85%_30%,rgba(245,158,11,.08),transparent_28%)]" />
      <div class="relative mx-auto max-w-6xl">
        <NuxtLink to="/" class="inline-flex items-center gap-2 text-sm font-bold text-white/50 transition hover:text-red-400">
          <span class="material-symbols-outlined text-base">arrow_back</span> Trang chủ
        </NuxtLink>
        <div class="mt-10 max-w-3xl">
          <span class="inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-red-500/25 bg-red-500/10 text-red-400">
            <span class="material-symbols-outlined text-3xl">{{ icon }}</span>
          </span>
          <p class="mt-6 text-xs font-black uppercase tracking-[.24em] text-red-400">{{ eyebrow }}</p>
          <h1 class="mt-3 text-4xl font-black tracking-tight md:text-6xl">{{ title }}</h1>
          <p class="mt-6 text-base leading-8 text-white/60 md:text-lg">{{ description }}</p>
        </div>
      </div>
    </section>
    <section class="mx-auto max-w-6xl px-5 py-14 md:py-20">
      <slot />
    </section>
  </main>
</template>

<style scoped>
:deep(.info-grid){display:grid;gap:1rem}@media(min-width:768px){:deep(.info-grid){grid-template-columns:repeat(3,minmax(0,1fr))}}
:deep(.info-card){border:1px solid rgba(255,255,255,.09);border-radius:1.25rem;background:#181a1b;padding:1.5rem}
:deep(.info-card h2),:deep(.info-card h3){font-weight:900;color:#fff}
:deep(.info-card p),:deep(.info-card li){color:rgba(255,255,255,.58);line-height:1.8}
:deep(.legal){max-width:900px;margin:auto}
:deep(.legal section){margin-bottom:1rem;border:1px solid rgba(255,255,255,.08);border-radius:1.1rem;background:#17191a;padding:1.5rem}
:deep(.legal h2){font-size:1.15rem;font-weight:900;margin-bottom:.7rem}
:deep(.legal p),:deep(.legal li){color:rgba(255,255,255,.62);line-height:1.85}
:deep(.legal ul){list-style:disc;padding-left:1.25rem;margin-top:.5rem}
</style>

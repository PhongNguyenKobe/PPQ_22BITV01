<script setup lang="ts">
type Toast = { id: number; message: string; type: 'success' | 'error' }
const toasts = ref<Toast[]>([])

function receive(event: Event) {
  const detail = (event as CustomEvent).detail as Omit<Toast, 'id'>
  const toast = { id: Date.now() + Math.random(), ...detail }
  toasts.value.push(toast)
  window.setTimeout(() => {
    toasts.value = toasts.value.filter(item => item.id !== toast.id)
  }, 3500)
}

onMounted(() => window.addEventListener('cineai:toast', receive))
onUnmounted(() => window.removeEventListener('cineai:toast', receive))
</script>

<template>
  <div class="fixed right-5 top-24 z-[100] flex w-[min(380px,calc(100vw-2.5rem))] flex-col gap-3">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="rounded-xl border px-4 py-3 font-semibold shadow-2xl backdrop-blur-xl"
        :class="toast.type === 'success'
          ? 'border-emerald-400/30 bg-emerald-950/90 text-emerald-100'
          : 'border-red-400/30 bg-red-950/90 text-red-100'"
      >
        {{ toast.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,.toast-leave-active{transition:all .2s ease}.toast-enter-from,.toast-leave-to{opacity:0;transform:translateX(24px)}
</style>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  id: number
  name: string
  price: number
  category: string
  imageUrl: string
  description: string
  rating?: number
}>()

const shortDescription = computed(() =>
  props.description.length > 100
    ? props.description.slice(0, 100) + '...'
    : props.description
)

const formattedPrice = computed(() =>
  new Intl.NumberFormat('vi-VN').format(props.price * 1000)
)
</script>

<template>
  <div
    class="group relative bg-surface-container-low border border-glass-stroke rounded-2xl overflow-hidden shadow-lg hover:border-primary-container/30 transition-all duration-300 flex flex-col h-full"
  >
    <!-- Image -->
    <div class="relative overflow-hidden aspect-[2/3] w-full bg-surface-container-high">
      <img
        :src="imageUrl"
        :alt="name"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />

      <!-- Hover overlay -->
      <div
        class="absolute inset-0 bg-black/80 p-4 opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col justify-between"
      >
        <p class="text-xs text-on-surface-variant line-clamp-6 leading-relaxed">
          {{ shortDescription }}
        </p>
        <NuxtLink
          :to="`/products/${id}`"
          class="w-full bg-primary-container text-on-primary-container py-2.5 rounded-xl font-bold text-center block text-sm transition-all hover:scale-105 active:scale-95 red-glow"
        >
          Đặt ngay
        </NuxtLink>
      </div>

      <!-- Category badge -->
      <div class="absolute top-3 left-3 flex flex-col gap-1 z-10">
        <span
          class="bg-black/60 border border-white/20 text-[10px] font-bold px-2.5 py-0.5 rounded text-white tracking-wide uppercase backdrop-blur-sm"
        >
          {{ category }}
        </span>
      </div>

      <!-- Rating badge -->
      <div
        v-if="rating"
        class="absolute top-3 right-3 bg-yellow-500/90 text-black font-bold text-xs px-2.5 py-1 rounded-lg flex items-center gap-1 z-10 backdrop-blur-sm"
      >
        <span
          class="material-symbols-outlined text-xs text-black"
          style="font-variation-settings: 'FILL' 1;"
        >
          star
        </span>
        {{ rating.toFixed(1) }}
      </div>
    </div>

    <!-- Metadata -->
    <div class="p-4 flex-1 flex flex-col justify-between bg-surface-container/30">
      <div>
        <h3
          class="font-bold text-base text-on-surface line-clamp-1 mb-1 group-hover:text-primary-container transition-colors"
        >
          {{ name }}
        </h3>
        <p class="text-xs text-on-surface-variant line-clamp-1">
          Giá: {{ formattedPrice }}₫
        </p>
      </div>
    </div>
  </div>
</template>

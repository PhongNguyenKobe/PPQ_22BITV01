<script setup lang="ts">
import QRCode from 'qrcode'

const props = withDefaults(defineProps<{
  value: string
  size?: number
}>(), {
  size: 250,
})

const src = ref('')

watch(
  () => [props.value, props.size] as const,
  async ([value, size]) => {
    src.value = await QRCode.toDataURL(value, {
      width: size,
      margin: 1,
      errorCorrectionLevel: 'M',
    })
  },
  { immediate: true },
)
</script>

<template>
  <img v-if="src" :src="src" alt="Mã QR vé điện tử" class="w-full h-full object-contain" />
</template>

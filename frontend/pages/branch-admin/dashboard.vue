<script setup lang="ts">
import SystemDashboard from '~/pages/admin/dashboard.vue'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})
</script>

<template>
  <SystemDashboard />
</template>

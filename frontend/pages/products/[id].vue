<script setup lang="ts">
const route = useRoute()
</script>

<template>
  <div>
    Product ID: {{ route.params.id }}
  </div>
</template>
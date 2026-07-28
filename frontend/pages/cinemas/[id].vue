<script setup lang="ts">
import { branchesService, mapBackendShowtimeToFrontend, type BranchDetail } from '~/services/api'

const route = useRoute()
const branch = ref<BranchDetail | null>(null)
const loading = ref(true)
const error = ref('')
const showtimes = computed(() => (branch.value?.showtimes || []).map(mapBackendShowtimeToFrontend))
const mapUrl = computed(() => {
  if (!branch.value) return ''
  const query = branch.value.latitude && branch.value.longitude
    ? `${branch.value.latitude},${branch.value.longitude}`
    : `${branch.value.address_line}, ${branch.value.city}`
  return `https://www.google.com/maps?q=${encodeURIComponent(query)}&output=embed`
})

onMounted(async () => {
  try {
    branch.value = await branchesService.getById(String(route.params.id))
  } catch {
    error.value = 'Không tìm thấy thông tin rạp chiếu.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="mx-auto max-w-7xl px-6 py-10 text-white">
    <p v-if="loading" class="py-20 text-center">Đang tải thông tin rạp...</p>
    <p v-else-if="error" class="py-20 text-center text-red-400">{{ error }}</p>
    <template v-else-if="branch">
      <section class="mb-8 rounded-3xl border border-white/10 bg-white/5 p-7">
        <p class="text-sm uppercase tracking-widest text-orange-300">CineAI Cinema</p>
        <h1 class="mt-2 text-4xl font-black">{{ branch.name }}</h1>
        <p class="mt-3 text-gray-300">{{ branch.address_line }}, {{ branch.district }}, {{ branch.city }}</p>
        <p v-if="branch.phone" class="mt-1 text-gray-400">Hotline: {{ branch.phone }}</p>
      </section>
      <iframe :src="mapUrl" class="mb-10 h-80 w-full rounded-3xl border-0" loading="lazy" title="Bản đồ rạp"></iframe>
      <h2 class="mb-5 text-2xl font-bold">Phim đang chiếu tại rạp</h2>
      <div class="mb-10 grid grid-cols-2 gap-5 md:grid-cols-4 lg:grid-cols-5">
        <NuxtLink v-for="movie in branch.movies" :key="movie.id" :to="`/movies/${movie.id}`" class="overflow-hidden rounded-2xl bg-white/5">
          <img :src="movie.poster" :alt="movie.title" class="aspect-[2/3] w-full object-cover">
          <h3 class="p-3 font-bold">{{ movie.title }}</h3>
        </NuxtLink>
      </div>
      <h2 class="mb-5 text-2xl font-bold">Toàn bộ lịch chiếu</h2>
      <div class="space-y-3">
        <div v-for="item in showtimes" :key="item.id" class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
          <span>{{ branch.movies.find(movie => movie.id === item.movieId)?.title }}</span>
          <span>{{ item.date }} · {{ item.time }} · {{ item.screenName }}</span>
          <NuxtLink :to="`/movies/${item.movieId}`" class="rounded-lg bg-orange-500 px-4 py-2 font-bold">Đặt vé</NuxtLink>
        </div>
        <p v-if="!showtimes.length" class="text-gray-400">Rạp chưa có suất chiếu đang mở bán.</p>
      </div>
    </template>
  </main>
</template>

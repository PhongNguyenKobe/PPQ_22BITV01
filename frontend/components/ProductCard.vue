<script setup lang="ts">
import { computed } from 'vue';
import { getProductSlugUrl } from '~/utils/slug';
import { useRouter } from 'vue-router'
import { useTicketsStore } from '~/store/tickets'
import { useUserStore } from '~/store/user'
import { youtubeTrailerLink } from '~/services/api'

const props = defineProps<{
  id: string | number
  backendMovieId?: string
  name: string
  price: number
  category: string
  imageUrl: string
  description: string
  rating?: number
  trailerUrl?: string
  genres?: string[]
  status?: 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'
  adminPreview?: boolean
  branchNames?: string[]
  selectedBranchName?: string
  selectedBranchId?: string
}>()

const router = useRouter()
const ticketsStore = useTicketsStore()
const userStore = useUserStore()

const shortDescription = computed(() =>
  props.description.length > 100
    ? props.description.slice(0, 100) + '...'
    : props.description
)

const formattedPrice = computed(() =>
  new Intl.NumberFormat('vi-VN').format(props.price * 1000)
)

const trailerHref = computed(() =>
  youtubeTrailerLink(props.trailerUrl, props.name)
)

const genreLabel = computed(() =>
  props.genres?.length ? props.genres.slice(0, 2).join(' · ') : props.category
)
const detailQuery = computed(() => ({
  ...(props.adminPreview ? { preview: 'admin' } : {}),
  ...(props.selectedBranchId ? { branch_id: props.selectedBranchId } : {}),
}))

function startBooking() {
  ticketsStore.selectMovie({
    id: props.id,
    name: props.name,
    backendMovieId: props.backendMovieId || null,
    imageUrl: props.imageUrl,
    category: props.category,
    price: props.price,
    rating: props.rating || null,
    description: props.description,
    trailerUrl: props.trailerUrl || null,
  })
  if (props.selectedBranchName) ticketsStore.selectCinema(props.selectedBranchName)

  if (!userStore.isAuthenticated) {
    router.push({
      path: '/login',
      query: { redirect: '/checkout/cinema' },
    })
    return
  }

  router.push(props.selectedBranchName ? '/checkout/showtime' : '/checkout/cinema')
}
</script>

<template>
  <div
    class="group relative movie-card bg-surface-container-low border border-glass-stroke rounded-2xl overflow-hidden shadow-lg transition-all duration-300 flex flex-col h-full"
  >
    <!-- Image -->
    <div class="relative overflow-hidden aspect-[2/3] w-full bg-surface-container-high">
      <img
        :src="imageUrl"
        :alt="name"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        @error="($event.target as HTMLImageElement).src = '/images/movie-placeholder.svg'"
      />

      <!-- Hover overlay -->
      <div class="absolute inset-0 movie-overlay p-4 flex flex-col justify-between">
        <div class="movie-overlay-top">
          <p class="text-xs text-white/85 line-clamp-5 leading-relaxed">
            {{ shortDescription }}
          </p>
        </div>

        <div class="movie-overlay-bottom space-y-3">
          <p class="text-xs text-white/70 font-semibold">{{ category }} • {{ formattedPrice }}₫</p>
          <div class="grid grid-cols-1 gap-2">
            <NuxtLink
              v-if="status !== 'UPCOMING' && !adminPreview"
              to="/checkout/cinema"
              class="overlay-btn overlay-btn-primary"
              @click.prevent="startBooking"
            >
              Mua vé
            </NuxtLink>
            <NuxtLink
              v-else-if="status === 'UPCOMING'"
              :to="{ path: getProductSlugUrl({ id, name }), query: detailQuery }"
              class="overlay-btn overlay-btn-primary"
            >
              Xem thông tin
            </NuxtLink>
            <span v-else class="overlay-btn overlay-btn-primary cursor-default">
              Chế độ chỉ xem
            </span>

            <div class="grid grid-cols-2 gap-2">
              <NuxtLink
                :to="{ path: getProductSlugUrl({ id, name }), query: detailQuery }"
                class="overlay-btn overlay-btn-secondary"
              >
                Xem chi tiết
              </NuxtLink>

              <a
                :href="trailerHref"
                target="_blank"
                rel="noopener noreferrer"
                class="overlay-btn overlay-btn-secondary"
              >
                Trailer
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Category badge -->
      <div class="absolute top-3 left-3 flex flex-col gap-1 z-10">
        <span
          v-if="status === 'UPCOMING'"
          class="w-fit bg-red-600 text-[10px] font-bold px-2.5 py-0.5 rounded text-white tracking-wide uppercase"
        >
          Sắp chiếu
        </span>
        <span
          class="bg-black/60 border border-white/20 text-[10px] font-bold px-2.5 py-0.5 rounded text-white tracking-wide uppercase backdrop-blur-sm"
        >
          {{ genreLabel }}
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
          {{ status === 'UPCOMING' ? 'Ngày phát hành sẽ được cập nhật' : `Giá: ${formattedPrice}₫` }}
        </p>
        <p v-if="branchNames?.length" class="mt-2 line-clamp-2 text-[11px] font-semibold text-sky-300">
          <span class="material-symbols-outlined mr-1 align-middle text-[13px]">location_on</span>
          {{ selectedBranchName || (branchNames.length === 1 ? branchNames[0] : `Đang chiếu tại ${branchNames.length} chi nhánh`) }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-card:hover {
  transform: translateY(-4px);
  border-color: rgba(229, 9, 20, 0.35);
  box-shadow: 0 20px 40px -28px rgba(0, 0, 0, 0.8);
}

.movie-overlay {
  background: linear-gradient(180deg, rgba(8, 10, 14, 0.05) 0%, rgba(8, 10, 14, 0.82) 52%, rgba(8, 10, 14, 0.96) 100%);
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.group:hover .movie-overlay,
.group:focus-within .movie-overlay {
  opacity: 1;
  transform: translateY(0);
}

.overlay-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  border-radius: 0.85rem;
  font-size: 0.84rem;
  font-weight: 800;
  transition: all 0.2s ease;
}

.overlay-btn-primary {
  background: #e50914;
  color: #fff;
}

.overlay-btn-primary:hover {
  filter: brightness(1.06);
}

.overlay-btn-secondary {
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f8fafc;
  background: rgba(255, 255, 255, 0.04);
}

.overlay-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.34);
}
</style>

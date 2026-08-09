<script setup lang="ts">
import { useTicketsStore } from '~/store/tickets'
import { useUserStore } from '~/store/user'
import { youtubeTrailerLink } from '~/services/api'
import { getProductSlugUrl } from '~/utils/slug'

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
  duration?: number
  releaseDate?: string
  status?: 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'
  adminPreview?: boolean
  branchNames?: string[]
  selectedBranchName?: string
  selectedBranchId?: string
}>()

const router = useRouter()
const ticketsStore = useTicketsStore()
const userStore = useUserStore()
const formattedPrice = computed(() => new Intl.NumberFormat('vi-VN').format(props.price * 1000))
const trailerHref = computed(() => youtubeTrailerLink(props.trailerUrl, props.name))
const genreLabel = computed(() => props.genres?.length ? props.genres.slice(0, 2).join(' · ') : props.category)
const detailQuery = computed(() => ({ ...(props.adminPreview ? { preview: 'admin' } : {}), ...(props.selectedBranchId ? { branch_id: props.selectedBranchId } : {}) }))
const detailPath = computed(() => getProductSlugUrl({ id: props.id, name: props.name }))
const releaseLabel = computed(() => {
  if (!props.releaseDate) return 'Ngày phát hành đang cập nhật'
  const date = new Date(props.releaseDate)
  return Number.isNaN(date.getTime()) ? 'Ngày phát hành đang cập nhật' : `Khởi chiếu ${date.toLocaleDateString('vi-VN')}`
})

function startBooking() {
  ticketsStore.selectMovie({ id: props.id, name: props.name, backendMovieId: props.backendMovieId || null, imageUrl: props.imageUrl, category: props.category, price: props.price, rating: props.rating || null, description: props.description, trailerUrl: props.trailerUrl || null })
  if (props.selectedBranchName) ticketsStore.selectCinema(props.selectedBranchName)
  if (!userStore.isAuthenticated) {
    router.push({ path: '/login', query: { redirect: '/checkout/cinema' } })
    return
  }
  router.push(props.selectedBranchName ? '/checkout/showtime' : '/checkout/cinema')
}
</script>

<template>
  <article class="movie-card group">
    <NuxtLink :to="{ path: detailPath, query: detailQuery }" class="poster-wrap" :aria-label="`Xem thông tin phim ${name}`">
      <img :src="imageUrl" :alt="name" class="poster" loading="lazy" @error="($event.target as HTMLImageElement).src = '/images/movie-placeholder.svg'">
      <div class="poster-shade" />
      <div class="absolute left-3 top-3 z-10 flex max-w-[75%] flex-wrap gap-1.5">
        <span v-if="status === 'UPCOMING'" class="badge badge-red">Sắp chiếu</span>
        <span class="badge">{{ genreLabel }}</span>
      </div>
      <span v-if="rating" class="rating"><span class="material-symbols-outlined text-sm" style="font-variation-settings:'FILL' 1">star</span>{{ rating.toFixed(1) }}</span>
      <span class="detail-reveal"><span class="material-symbols-outlined">info</span>Xem chi tiết</span>
    </NuxtLink>

    <div class="flex flex-1 flex-col p-4 sm:p-5">
      <NuxtLink :to="{ path: detailPath, query: detailQuery }"><h3 class="line-clamp-2 min-h-[48px] text-base font-black leading-6 text-white transition group-hover:text-red-400 sm:text-lg">{{ name }}</h3></NuxtLink>
      <div class="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-white/45">
        <span v-if="duration">{{ duration }} phút</span><span v-if="duration && genreLabel">•</span><span class="line-clamp-1">{{ genreLabel }}</span>
      </div>
      <p v-if="branchNames?.length" class="mt-3 line-clamp-1 text-xs font-semibold text-sky-300"><span class="material-symbols-outlined mr-1 align-middle text-sm">location_on</span>{{ selectedBranchName || (branchNames.length === 1 ? branchNames[0] : `${branchNames.length} cụm rạp`) }}</p>
      <p v-else-if="status === 'UPCOMING'" class="mt-3 text-xs text-white/45">{{ releaseLabel }}</p>

      <div class="mt-auto pt-5">
        <p v-if="status !== 'UPCOMING'" class="mb-3 text-xs text-white/45">Giá vé từ <strong class="ml-1 text-base text-amber-300">{{ formattedPrice }}đ</strong></p>
        <div class="flex gap-2">
          <NuxtLink v-if="status === 'UPCOMING' || adminPreview" :to="{ path: detailPath, query: detailQuery }" class="card-cta flex-1"><span class="material-symbols-outlined text-lg">{{ adminPreview ? 'visibility' : 'info' }}</span>{{ adminPreview ? 'Xem luồng bán vé' : 'Xem thông tin' }}</NuxtLink>
          <button v-else type="button" class="card-cta flex-1" @click="startBooking"><span class="material-symbols-outlined text-lg">confirmation_number</span>Chọn suất chiếu</button>
          <a :href="trailerHref" target="_blank" rel="noopener noreferrer" class="trailer-button" :aria-label="`Xem trailer ${name}`"><span class="material-symbols-outlined">play_arrow</span></a>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
.movie-card{display:flex;height:100%;flex-direction:column;overflow:hidden;border:1px solid rgba(255,255,255,.09);border-radius:20px;background:#191b1d;box-shadow:0 20px 45px -38px #000;transition:.25s}.movie-card:hover{transform:translateY(-6px);border-color:rgba(229,9,20,.38);box-shadow:0 30px 60px -38px rgba(229,9,20,.5)}
.poster-wrap{position:relative;display:block;overflow:hidden;aspect-ratio:2/3;background:#242629}.poster{height:100%;width:100%;object-fit:cover;transition:transform .55s}.group:hover .poster{transform:scale(1.045)}.poster-shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.1),transparent 55%,rgba(0,0,0,.7));opacity:.72}
.badge{display:inline-flex;border:1px solid rgba(255,255,255,.16);border-radius:7px;background:rgba(8,9,11,.75);padding:5px 7px;font-size:9px;font-weight:900;text-transform:uppercase;letter-spacing:.05em;color:white;backdrop-filter:blur(8px)}.badge-red{border-color:rgba(239,68,68,.5);background:rgba(220,38,38,.85)}
.rating{position:absolute;right:12px;top:12px;z-index:10;display:flex;align-items:center;gap:3px;border-radius:8px;background:rgba(245,190,40,.94);padding:5px 8px;font-size:11px;font-weight:900;color:#151515}
.detail-reveal{position:absolute;bottom:15px;left:50%;display:flex;transform:translate(-50%,12px);align-items:center;gap:5px;white-space:nowrap;border:1px solid rgba(255,255,255,.18);border-radius:10px;background:rgba(10,11,13,.75);padding:8px 12px;font-size:11px;font-weight:800;color:white;opacity:0;backdrop-filter:blur(9px);transition:.22s}.group:hover .detail-reveal,.group:focus-within .detail-reveal{transform:translate(-50%,0);opacity:1}
.card-cta{display:flex;min-height:44px;align-items:center;justify-content:center;gap:7px;border-radius:12px;background:#e50914;padding:0 12px;font-size:12px;font-weight:900;color:white;transition:.2s}.card-cta:hover{background:#f01924;box-shadow:0 12px 25px -14px #e50914}.trailer-button{display:flex;height:44px;width:44px;flex:none;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.13);border-radius:12px;background:rgba(255,255,255,.05);color:white;transition:.2s}.trailer-button:hover{background:rgba(255,255,255,.12)}
@media(max-width:520px){.movie-card{border-radius:15px}.detail-reveal{display:none}.card-cta{font-size:10px;padding:0 7px}.trailer-button{display:none}}
</style>

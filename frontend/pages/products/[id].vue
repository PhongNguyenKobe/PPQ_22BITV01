<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductsStore } from '~/store/products'
import { useTicketsStore } from '~/store/tickets'
import { useUserStore } from '~/store/user'
import { branchesService, youtubeTrailerLink, type BranchDetail } from '~/services/api'

definePageMeta({
  layout: 'default'
})

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()
const ticketsStore = useTicketsStore()
const userStore = useUserStore()

const { products } = storeToRefs(productsStore)
const { currentUser } = storeToRefs(userStore)
const loading = ref(true)
const selectedBranchCatalog = ref<BranchDetail | null>(null)
const selectedBranchId = computed(() => String(route.query.branch_id || ''))
const selectedBranchName = computed(() => selectedBranchCatalog.value?.name || '')
const isAdminPreview = computed(() =>
  route.query.preview === 'admin'
  && ['admin', 'branch-admin'].includes(currentUser.value?.role || '')
)
const adminReturnPath = computed(() =>
  currentUser.value?.role === 'branch-admin'
    ? '/branch-admin/dashboard'
    : '/admin/dashboard'
)
const listQuery = computed(() => ({
  ...(isAdminPreview.value ? { preview: 'admin' } : {}),
  ...(selectedBranchId.value ? { branch_id: selectedBranchId.value } : {}),
}))

// State bình luận
const newComment = ref('')
const userRating = ref(5)
const isSubmittingComment = ref(false)

// Danh sách bình luận mẫu (Mock comments)
const comments = ref([
  {
    id: 1,
    userName: 'Minh Tuấn',
    userAvatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80',
    rating: 5,
    date: '2 giờ trước',
    content: 'Phim đỉnh thực sự! Kỹ xảo hoành tráng, âm thanh sống động nghe cực sướng tai. Đã xem 2 lần rồi vẫn muốn xem lại!',
    likes: 12,
    isLiked: false
  },
  {
    id: 2,
    userName: 'Hoàng Yến',
    userAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80',
    rating: 4,
    date: '1 ngày trước',
    content: 'Cốt chuyện ổn, diễn xuất tròn vai. Đoạn kết hơi vội một chút nhưng nhìn chung rất đáng tiền vé.',
    likes: 5,
    isLiked: false
  },
  {
    id: 3,
    userName: 'Trần Khoa',
    userAvatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&auto=format&fit=crop&q=80',
    rating: 5,
    date: '3 ngày trước',
    content: '10/10 không nói nhiều! Bạn nào mê thể loại này thì nhất định phải đi xem ở phòng chiếu IMAX nhé.',
    likes: 19,
    isLiked: false
  }
])

// Fetch products
onMounted(async () => {
  try {
    if (products.value.length === 0) {
      await productsStore.fetchProducts()
    }
    if (selectedBranchId.value) {
      selectedBranchCatalog.value = await branchesService.getById(selectedBranchId.value)
    }
  } catch (error) {
    console.error('Lỗi tải sản phẩm:', error)
  } finally {
    loading.value = false
  }
})

// Current Product
const currentProduct = computed(() => {
  const id = String(route.params.id as string)
  return products.value.find((p) => String(p.id) === id)
})

const trailerHref = computed(() => {
  if (!currentProduct.value) return '#'
  return youtubeTrailerLink(currentProduct.value.trailerUrl, currentProduct.value.name)
})

const formattedPrice = computed(() => {
  if (!currentProduct.value) return '0đ'
  return new Intl.NumberFormat('vi-VN').format(currentProduct.value.price * 1000) + 'đ'
})

const genreLabel = computed(() =>
  currentProduct.value?.genres.length
    ? currentProduct.value.genres.join(' · ')
    : 'Chưa phân loại'
)

// Start Booking
function startBooking() {
  if (!currentProduct.value) return
  if (isAdminPreview.value) return
  if (currentProduct.value.status === 'UPCOMING') return

  ticketsStore.selectMovie({
    id: currentProduct.value.id,
    name: currentProduct.value.name,
    backendMovieId: currentProduct.value.backendMovieId || null,
    imageUrl: currentProduct.value.imageUrl,
    category: currentProduct.value.category,
    price: currentProduct.value.price,
    rating: currentProduct.value.rating || null,
    description: currentProduct.value.description,
    trailerUrl: currentProduct.value.trailerUrl || null,
  })
  if (selectedBranchName.value) {
    ticketsStore.selectCinema(selectedBranchName.value)
  }

  if (!userStore.isAuthenticated) {
    return router.push({
      path: '/login',
      query: { redirect: selectedBranchName.value ? '/checkout/showtime' : '/checkout/cinema' },
    })
  }

  router.push(selectedBranchName.value ? '/checkout/showtime' : '/checkout/cinema')
}

// Thêm bình luận
function submitComment() {
  if (!newComment.value.trim()) return
  if (!userStore.isAuthenticated) {
    alert('Vui lòng đăng nhập để gửi bình luận!')
    return router.push('/login')
  }

  isSubmittingComment.value = true

  setTimeout(() => {
    comments.value.unshift({
      id: Date.now(),
      userName: currentUser.value?.name || 'Khán giả CineAI',
      userAvatar: (currentUser.value as any)?.avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80',
      rating: userRating.value,
      date: 'Vừa xong',
      content: newComment.value,
      likes: 0,
      isLiked: false
    })

    newComment.value = ''
    userRating.value = 5
    isSubmittingComment.value = false
  }, 400)
}

function toggleLike(comment: typeof comments.value[0]) {
  if (comment.isLiked) {
    comment.likes--
    comment.isLiked = false
  } else {
    comment.likes++
    comment.isLiked = true
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#0b0c10] text-gray-100 selection:bg-red-600 selection:text-white">
    <div v-if="isAdminPreview" class="sticky top-0 z-50 border-b border-amber-400/30 bg-[#241d0b]/95 px-4 py-3 backdrop-blur-xl">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
        <div>
          <p class="text-sm font-bold text-amber-200">Đang xem trước trang chi tiết phim</p>
          <p class="text-xs text-amber-100/70">
            {{ selectedBranchName ? `Phạm vi: ${selectedBranchName}. ` : '' }}Đây là nội dung khách hàng nhìn thấy; thao tác đặt vé đã được khóa.
          </p>
        </div>
        <NuxtLink :to="adminReturnPath" class="rounded-lg bg-amber-300 px-4 py-2 text-xs font-bold text-black">
          Quay lại quản trị
        </NuxtLink>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="min-h-[80vh] flex flex-col items-center justify-center gap-4">
      <div class="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-400 font-medium animate-pulse">Đang tải trải nghiệm điện ảnh...</p>
    </div>

    <!-- Not Found -->
    <div v-else-if="!currentProduct" class="min-h-[80vh] flex flex-col items-center justify-center text-center px-4">
      <span class="material-symbols-outlined text-6xl text-gray-600 mb-4">movie_off</span>
      <h2 class="text-2xl font-bold text-white mb-2">Không tìm thấy tác phẩm</h2>
      <p class="text-gray-400 text-sm mb-6">Bộ phim bạn tìm kiếm không tồn tại hoặc đã ngừng chiếu.</p>
      <NuxtLink :to="{ path: '/products', query: listQuery }"
        class="inline-flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold px-6 py-3 rounded-xl transition-all shadow-lg hover:shadow-red-600/30">
        <span class="material-symbols-outlined text-sm">arrow_back</span>
        Quay lại danh sách phim
      </NuxtLink>
    </div>

    <!-- Main Content -->
    <main v-else class="relative w-full overflow-hidden">

      <!-- ================================================================= -->
      <!-- GLOBAL BACKGROUND IMAGE (NỀN PHIM PHỦ XUỐNG TỚI HẾT BÌNH LUẬN) -->
      <!-- ================================================================= -->
      <div class="absolute inset-0 z-0 pointer-events-none">
        <img :src="currentProduct.imageUrl"
          class="w-full h-full object-cover object-center filter blur-2xl scale-110 opacity-25" />
        <!-- Phủ gradient giúp mượt nền từ trên xuống dưới -->
        <div class="absolute inset-0 bg-gradient-to-b from-[#0b0c10]/40 via-[#0b0c10]/80 to-[#0b0c10]"></div>
        <div class="absolute inset-0 bg-gradient-to-r from-[#0b0c10] via-transparent to-[#0b0c10]"></div>
      </div>

      <!-- ================================================================= -->
      <!-- 1. FULL-WIDTH HERO BANNER -->
      <!-- ================================================================= -->
      <section class="relative z-10 w-full min-h-[80vh] flex items-center justify-center pt-16 pb-12">

        <!-- Hero Inner Content -->
        <div class="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-12 py-8">

          <!-- Back Button -->
          <div class="mb-8">
            <NuxtLink :to="{ path: '/products', query: listQuery }"
              class="inline-flex items-center gap-2 text-xs font-bold text-gray-300 hover:text-red-400 transition-colors uppercase tracking-wider bg-black/50 backdrop-blur-md px-4 py-2.5 rounded-xl border border-white/10 shadow-lg">
              <span class="material-symbols-outlined text-sm">arrow_back</span>
              Quay lại danh sách phim
            </NuxtLink>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">

            <!-- Poster Card (Trái) -->
            <div class="lg:col-span-4 flex justify-center lg:justify-start">
              <div class="relative group w-full max-w-[340px]">
                <img :src="currentProduct.imageUrl" :alt="currentProduct.name"
                  class="w-full aspect-[2/3] object-cover rounded-3xl shadow-[0_25px_60px_rgba(0,0,0,0.9)] border border-white/15 group-hover:scale-[1.02] transition-transform duration-300" />
                <span
                  class="absolute top-4 left-4 bg-red-600 text-white font-black text-[10px] tracking-widest px-3 py-1.5 rounded-lg uppercase shadow-lg border border-red-400/30">
                  {{ genreLabel }}
                </span>
              </div>
            </div>

            <!-- Movie Details (Phải) -->
            <div class="lg:col-span-8 flex flex-col justify-center">

              <div class="flex items-center gap-3 mb-3">
                <span
                  class="px-3 py-1 bg-red-600/20 text-red-400 border border-red-500/30 rounded-lg text-xs font-black uppercase tracking-widest">
                  Đang Chiếu
                </span>
                <span
                  class="text-xs text-gray-300 font-medium flex items-center gap-1 bg-black/40 backdrop-blur-md px-3 py-1 rounded-lg border border-white/10">
                  <span class="material-symbols-outlined text-sm text-gray-400">schedule</span>
                  {{ currentProduct.duration }} Phút
                </span>
                <span v-if="selectedBranchName"
                  class="text-xs text-sky-200 font-bold flex items-center gap-1 bg-sky-500/10 px-3 py-1 rounded-lg border border-sky-400/25">
                  <span class="material-symbols-outlined text-sm">location_on</span>
                  {{ selectedBranchName }}
                </span>
              </div>

              <!-- Movie Title -->
              <h1
                class="text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight uppercase leading-tight mb-4 drop-shadow-md">
                {{ currentProduct.name }}
              </h1>

              <!-- Rating & Price Tags -->
              <div class="flex flex-wrap items-center gap-4 mb-6">
                <div v-if="currentProduct.rating"
                  class="flex items-center gap-1.5 bg-yellow-500/10 border border-yellow-500/20 px-3.5 py-2 rounded-xl backdrop-blur-md">
                  <span class="material-symbols-outlined text-yellow-400 text-base">star</span>
                  <span class="text-yellow-400 font-black text-sm">{{ currentProduct.rating.toFixed(1) }}</span>
                  <span class="text-gray-400 text-xs font-normal">/ 5.0</span>
                </div>

                <div
                  class="flex items-center gap-1.5 bg-black/50 border border-white/10 px-3.5 py-2 rounded-xl backdrop-blur-md">
                  <span class="material-symbols-outlined text-red-500 text-base">confirmation_number</span>
                  <span class="text-gray-300 font-bold text-sm">Giá vé từ:</span>
                  <span class="text-red-400 font-black text-sm">{{ formattedPrice }}</span>
                </div>
              </div>

              <!-- Description -->
              <p class="text-gray-300 text-sm sm:text-base leading-relaxed font-light mb-8 max-w-3xl drop-shadow-sm">
                {{ currentProduct.description || 'Chưa có thông tin mô tả chi tiết cho phim này.' }}
              </p>

              <!-- Action Buttons -->
              <div class="flex flex-wrap items-center gap-4 mb-8">
                <button v-if="currentProduct.status !== 'UPCOMING' && !isAdminPreview" @click="startBooking"
                  class="flex-1 sm:flex-none px-10 py-4 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white font-black text-sm rounded-2xl shadow-[0_10px_30px_rgba(229,9,20,0.5)] hover:shadow-[0_15px_35px_rgba(229,9,20,0.7)] transition-all duration-300 flex items-center justify-center gap-2 transform hover:-translate-y-0.5">
                  <span class="material-symbols-outlined text-xl">confirmation_number</span>
                  ĐẶT VÉ NGAY
                </button>
                <span v-else-if="isAdminPreview"
                  class="flex-1 sm:flex-none px-8 py-4 bg-amber-400/10 text-amber-200 border border-amber-400/30 font-bold text-sm rounded-2xl text-center">
                  CHẾ ĐỘ CHỈ XEM — KHÔNG ĐẶT VÉ
                </span>
                <span v-else
                  class="flex-1 sm:flex-none px-8 py-4 bg-white/5 text-gray-300 border border-white/15 font-bold text-sm rounded-2xl text-center">
                  SẮP RA MẮT — CHƯA MỞ BÁN VÉ
                </span>

                <a :href="trailerHref" target="_blank" rel="noopener noreferrer"
                  class="flex-1 sm:flex-none px-8 py-4 bg-black/50 hover:bg-white/10 text-white border border-white/15 hover:border-white/30 font-bold text-sm rounded-2xl transition-all duration-300 flex items-center justify-center gap-2 backdrop-blur-md">
                  <span class="material-symbols-outlined text-xl text-red-500">play_circle</span>
                  XEM TRAILER
                </a>
              </div>

              <!-- Facts Grid -->
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 border-t border-white/10 pt-6">
                <div>
                  <span class="block text-[11px] text-gray-400 font-bold uppercase tracking-wider mb-1">Thể loại</span>
                  <span class="text-sm font-semibold text-white">{{ genreLabel }}</span>
                </div>
                <div>
                  <span class="block text-[11px] text-gray-400 font-bold uppercase tracking-wider mb-1">Đạo diễn</span>
                  <span class="text-sm font-semibold text-white">{{ currentProduct.director || 'Chưa cập nhật' }}</span>
                </div>
                <div>
                  <span class="block text-[11px] text-gray-400 font-bold uppercase tracking-wider mb-1">Khởi chiếu</span>
                  <span class="text-sm font-semibold text-white">{{ currentProduct.releaseDate || 'Chưa công bố' }}</span>
                </div>
                <div class="col-span-2 sm:col-span-3">
                  <span class="block text-[11px] text-gray-400 font-bold uppercase tracking-wider mb-1">Diễn viên</span>
                  <span class="text-sm font-semibold text-white">{{ currentProduct.cast.length ? currentProduct.cast.join(', ') : 'Chưa cập nhật' }}</span>
                </div>
              </div>

            </div>

          </div>

        </div>
      </section>

      <!-- ================================================================= -->
      <!-- 2. REVIEWS & COMMENTS SECTION (NẰM TRÊN CÙNG HÌNH NỀN) -->
      <!-- ================================================================= -->
      <section class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-t border-white/10">

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">

          <!-- Rating Summary Box -->
          <div class="lg:col-span-5 space-y-6">
            <div class="bg-[#14161d]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-6 sm:p-8 shadow-2xl">
              <h2 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <span class="material-symbols-outlined text-yellow-400">star</span>
                Đánh Giá Khán Giả
              </h2>

              <div class="flex items-center gap-6 mb-6 pb-6 border-b border-white/10">
                <div class="text-center">
                  <span class="text-5xl font-black text-white block">4.8</span>
                  <div class="flex items-center text-yellow-400 text-sm justify-center my-1">
                    <span v-for="i in 5" :key="i" class="material-symbols-outlined text-sm">star</span>
                  </div>
                  <span class="text-xs text-gray-400 font-medium">128 đánh giá</span>
                </div>

                <!-- Rating Bars -->
                <div class="flex-1 space-y-2 text-xs">
                  <div class="flex items-center gap-2">
                    <span class="w-3 text-gray-400 font-bold">5</span>
                    <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div class="h-full bg-yellow-400 w-[85%] rounded-full"></div>
                    </div>
                    <span class="w-8 text-right text-gray-400">85%</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-3 text-gray-400 font-bold">4</span>
                    <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div class="h-full bg-yellow-400 w-[10%] rounded-full"></div>
                    </div>
                    <span class="w-8 text-right text-gray-400">10%</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-3 text-gray-400 font-bold">3</span>
                    <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div class="h-full bg-yellow-400 w-[5%] rounded-full"></div>
                    </div>
                    <span class="w-8 text-right text-gray-400">5%</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-3 text-gray-400 font-bold">2</span>
                    <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div class="h-full bg-yellow-400 w-[0%] rounded-full"></div>
                    </div>
                    <span class="w-8 text-right text-gray-400">0%</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-3 text-gray-400 font-bold">1</span>
                    <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div class="h-full bg-yellow-400 w-[0%] rounded-full"></div>
                    </div>
                    <span class="w-8 text-right text-gray-400">0%</span>
                  </div>
                </div>
              </div>

              <!-- Form Bình Luận -->
              <form @submit.prevent="submitComment" class="space-y-4">
                <h3 class="text-sm font-bold text-white uppercase tracking-wider">Viết bình luận của bạn</h3>

                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-400">Số sao:</span>
                  <div class="flex gap-1">
                    <button v-for="star in 5" :key="star" type="button" @click="userRating = star"
                      class="text-yellow-400 hover:scale-125 transition-transform">
                      <span class="material-symbols-outlined text-xl">
                        {{ star <= userRating ? 'star' : 'star_border' }} </span>
                    </button>
                  </div>
                </div>

                <div>
                  <textarea v-model="newComment" rows="3" placeholder="Chia sẻ cảm nhận của bạn về bộ phim này..."
                    class="w-full bg-black/40 border border-white/10 rounded-2xl p-4 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500 transition-colors resize-none"
                    required></textarea>
                </div>

                <button type="submit" :disabled="isSubmittingComment"
                  class="w-full py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 text-white font-bold text-xs rounded-xl transition-all shadow-md flex items-center justify-center gap-2">
                  <span v-if="isSubmittingComment"
                    class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  <span v-else class="material-symbols-outlined text-sm">send</span>
                  Gửi Bình Luận
                </button>
              </form>

            </div>
          </div>

          <!-- Comments List -->
          <div class="lg:col-span-7 space-y-4">
            <div class="flex items-center justify-between mb-2">
              <h2 class="text-xl font-bold text-white flex items-center gap-2">
                <span class="material-symbols-outlined text-red-500">forum</span>
                Bình Luận Từ Khán Giả ({{ comments.length }})
              </h2>
            </div>

            <div v-for="c in comments" :key="c.id"
              class="bg-[#14161d]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-all space-y-3 shadow-lg">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <img :src="c.userAvatar" :alt="c.userName"
                    class="w-10 h-10 rounded-full object-cover border border-white/10" />
                  <div>
                    <h4 class="text-sm font-bold text-white">{{ c.userName }}</h4>
                    <span class="text-[10px] text-gray-500">{{ c.date }}</span>
                  </div>
                </div>

                <div
                  class="flex items-center gap-0.5 text-yellow-400 bg-yellow-400/10 border border-yellow-400/20 px-2 py-0.5 rounded-lg text-xs font-bold">
                  <span class="material-symbols-outlined text-xs">star</span>
                  <span>{{ c.rating }}.0</span>
                </div>
              </div>

              <p class="text-xs text-gray-300 leading-relaxed font-light">
                {{ c.content }}
              </p>

              <div class="flex items-center justify-between pt-2 border-t border-white/5">
                <button @click="toggleLike(c)" class="flex items-center gap-1.5 text-xs font-semibold transition-colors"
                  :class="c.isLiked ? 'text-red-500' : 'text-gray-400 hover:text-white'">
                  <span class="material-symbols-outlined text-sm">{{ c.isLiked ? 'favorite' : 'favorite_border'
                    }}</span>
                  <span>{{ c.likes }} Hữu ích</span>
                </button>
              </div>
            </div>

          </div>

        </div>

      </section>

    </main>

  </div>
</template>

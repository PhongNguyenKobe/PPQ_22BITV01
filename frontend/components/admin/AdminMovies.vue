<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { adminBackendService, movieService, tmdbService, type Movie, type TmdbPopularMovie, CANONICAL_MOVIE_GENRES } from '~/services/api'

const movies = ref<Movie[]>([])
const tmdbMovies = ref<TmdbPopularMovie[]>([])
const movieUsage = ref<Record<string, number>>({})
const loading = ref(false)
const error = ref('')
const success = ref('')
const catalogQuery = ref('')
const catalogStatus = ref<'ALL' | 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'>('ALL')
const currentPage = ref(1)
const pageSize = 10

const showManualCreate = ref(false)

const movieForm = ref({
  title: '',
  description: '',
  duration: 120,
  releaseDate: '',
  poster: '',
  trailer: '',
  status: 'UPCOMING' as 'UPCOMING' | 'NOW_SHOWING' | 'ENDED',
  genres: [] as string[],
  originalTitle: '',
  ageRating: '',
  language: '',
  director: '',
  castText: '',
})

const tmdbMovieQuery = ref('')
const selectedTmdbMovieId = ref('')
const tmdbImporting = ref(false)
const tmdbSearching = ref(false)
const duplicateImportConfirmed = ref(false)
let tmdbSearchTimer: ReturnType<typeof setTimeout> | undefined

const editingMovieId = ref('')
const movieEditForm = ref({
  title: '',
  originalTitle: '',
  description: '',
  duration: 120,
  releaseDate: '',
  poster: '',
  trailer: '',
  status: 'UPCOMING' as 'UPCOMING' | 'NOW_SHOWING' | 'ENDED',
  genres: [] as string[],
  director: '',
  castText: '',
  ageRating: '',
  language: '',
})

const filteredTmdbMovies = computed(() => {
  const query = tmdbMovieQuery.value.trim().toLocaleLowerCase('vi')
  if (!query) return tmdbMovies.value
  return tmdbMovies.value.filter((movie) =>
    movie.title.toLocaleLowerCase('vi').includes(query)
    || (movie.original_title || '').toLocaleLowerCase('vi').includes(query)
  )
})

const selectedTmdbMovie = computed(() =>
  tmdbMovies.value.find((movie) => String(movie.tmdb_id) === selectedTmdbMovieId.value),
)
const existingCatalogMovie = computed(() => {
  const selected = selectedTmdbMovie.value
  if (!selected) return null
  const normalize = (value?: string | null) => String(value || '').trim().toLocaleLowerCase('vi')
  const selectedTitles = new Set([normalize(selected.title), normalize(selected.original_title)].filter(Boolean))
  return movies.value.find(movie =>
    movie.tmdbId === selected.tmdb_id
    || selectedTitles.has(normalize(movie.title))
    || selectedTitles.has(normalize(movie.originalTitle)),
  ) || null
})

const filteredMovies = computed(() => {
  const query = catalogQuery.value.trim().toLocaleLowerCase('vi')
  return movies.value.filter(movie =>
    (catalogStatus.value === 'ALL' || movie.status === catalogStatus.value)
    && (!query || movie.title.toLocaleLowerCase('vi').includes(query)
      || movie.genre.some(genre => genre.toLocaleLowerCase('vi').includes(query)))
  )
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredMovies.value.length / pageSize)))
const paginatedMovies = computed(() => filteredMovies.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))
const statusCounts = computed(() => ({
  ALL: movies.value.length,
  NOW_SHOWING: movies.value.filter(movie => movie.status === 'NOW_SHOWING').length,
  UPCOMING: movies.value.filter(movie => movie.status === 'UPCOMING').length,
  ENDED: movies.value.filter(movie => movie.status === 'ENDED').length,
}))

watch([catalogQuery, catalogStatus], () => { currentPage.value = 1 })
watch(selectedTmdbMovieId, () => { duplicateImportConfirmed.value = false })
watch(tmdbMovieQuery, (query) => {
  if (tmdbSearchTimer) clearTimeout(tmdbSearchTimer)
  selectedTmdbMovieId.value = ''
  const normalized = query.trim()
  if (!normalized) {
    loadPopularTmdb()
    return
  }
  if (normalized.length < 2) return
  tmdbSearchTimer = setTimeout(async () => {
    tmdbSearching.value = true
    try {
      tmdbMovies.value = await tmdbService.searchMovies(normalized)
    } catch (e: any) {
      error.value = e?.data?.statusMessage || e?.message || 'Không thể tìm kiếm TMDB.'
    } finally {
      tmdbSearching.value = false
    }
  }, 450)
})

async function loadPopularTmdb() {
  tmdbSearching.value = true
  try { tmdbMovies.value = await movieService.getPopularFromTmdb() }
  finally { tmdbSearching.value = false }
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [movieData, tmdbMovieData, usageData] = await Promise.all([
      movieService.getAll(),
      movieService.getPopularFromTmdb(),
      adminBackendService.getMovieUsage(),
    ])
    movies.value = movieData
    tmdbMovies.value = tmdbMovieData
    movieUsage.value = usageData
  } catch (e: any) {
    error.value = e?.message || 'Không thể tải dữ liệu phim.'
  } finally {
    loading.value = false
  }
}

async function createMovie() {
  error.value = ''
  success.value = ''
  if (!movieForm.value.genres.length) {
    error.value = 'Vui lòng chọn ít nhất một thể loại.'
    return
  }
  try {
    await adminBackendService.createMovie({
      title: movieForm.value.title,
      original_title: movieForm.value.originalTitle || undefined,
      description: movieForm.value.description || undefined,
      duration_min: Number(movieForm.value.duration),
      release_date: movieForm.value.releaseDate || null,
      poster_url: movieForm.value.poster || undefined,
      trailer_url: movieForm.value.trailer || undefined,
      age_rating: movieForm.value.ageRating || undefined,
      language: movieForm.value.language || undefined,
      director: movieForm.value.director || undefined,
      cast_names: movieForm.value.castText.split(',').map(value => value.trim()).filter(Boolean),
      status: movieForm.value.status,
      genres: movieForm.value.genres,
    })
    movies.value = await movieService.getAll()
    movieForm.value = { title: '', description: '', duration: 120, releaseDate: '', poster: '', trailer: '', status: 'UPCOMING', genres: [], originalTitle: '', ageRating: '', language: '', director: '', castText: '' }
    showManualCreate.value = false
    success.value = 'Đã thêm phim thủ công vào kho.'
  } catch (e: any) {
    error.value = e?.message || 'Không thể tạo phim thủ công.'
  }
}

async function importTmdbMovieToCatalog() {
  const movie = selectedTmdbMovie.value
  if (!movie) {
    error.value = 'Vui lòng chọn một phim TMDB.'
    return
  }
  if (existingCatalogMovie.value && !duplicateImportConfirmed.value) {
    duplicateImportConfirmed.value = true
    error.value = `Phim “${existingCatalogMovie.value.title}” đã tồn tại trong kho với trạng thái ${existingCatalogMovie.value.status === 'NOW_SHOWING' ? 'Đang chiếu' : existingCatalogMovie.value.status === 'UPCOMING' ? 'Chờ mở bán' : 'Đã kết thúc'}. Nếu muốn cập nhật lại thông tin TMDB, hãy nhấn “Xác nhận đồng bộ” lần nữa.`
    success.value = ''
    return
  }
  error.value = ''
  success.value = ''
  tmdbImporting.value = true
  try {
    const detail = await tmdbService.getMovieDetail(movie.tmdb_id)
    const result = await adminBackendService.importTmdbMovie({
      tmdb_id: movie.tmdb_id,
      title: detail.title || movie.title,
      overview: detail.description || movie.overview || null,
      poster_path: movie.poster_path || null,
      release_date: detail.releaseDate || movie.release_date || null,
      original_title: movie.original_title || null,
      language: null,
      duration_min: detail.duration || 120,
      trailer_url: detail.trailerUrl || null,
      genres: detail.genre || [],
      director: detail.director || null,
      cast_names: detail.cast || [],
      status: 'UPCOMING',
    })
    movies.value = await movieService.getAll()
    selectedTmdbMovieId.value = ''
    tmdbMovieQuery.value = ''
    duplicateImportConfirmed.value = false
    success.value = result.imported ? 'Đã thêm phim từ TMDB vào kho.' : 'Đã đồng bộ lại thông tin TMDB. Trạng thái vận hành của phim được giữ nguyên.'
  } catch (e: any) {
    error.value = e?.message || 'Không thể import phim từ TMDB.'
  } finally {
    tmdbImporting.value = false
  }
}

function openEditModal(movie: Movie) {
  editingMovieId.value = movie.id
  movieEditForm.value = {
    title: movie.title,
    originalTitle: movie.originalTitle || '',
    description: movie.description,
    duration: movie.duration,
    releaseDate: movie.releaseDate,
    poster: movie.poster === '/images/movie-placeholder.svg' ? '' : movie.poster,
    trailer: movie.trailer,
    status: movie.status || 'UPCOMING',
    genres: [...movie.genre],
    director: movie.director,
    castText: movie.cast.join(', '),
    ageRating: movie.ageRating || '',
    language: movie.language || '',
  }
}

function closeEditModal() {
  editingMovieId.value = ''
}

async function saveMovieEdit() {
  const form = movieEditForm.value
  if (!editingMovieId.value || !form.title.trim()) return
  error.value = ''
  success.value = ''
  try {
    const updated = await adminBackendService.updateMovie(editingMovieId.value, {
      title: form.title.trim(),
      original_title: form.originalTitle.trim() || null,
      description: form.description.trim() || null,
      duration_min: form.duration,
      release_date: form.releaseDate || null,
      poster_url: form.poster || null,
      trailer_url: form.trailer || null,
      age_rating: form.ageRating.trim() || null,
      language: form.language.trim() || null,
      status: form.status,
      genres: form.genres,
      director: form.director.trim() || null,
      cast_names: form.castText.split(',').map(value => value.trim()).filter(Boolean),
    })
    movies.value = movies.value.map((item) => item.id === updated.id ? updated : item)
    closeEditModal()
    success.value = 'Đã lưu thông tin phim.'
  } catch (e: any) {
    error.value = e?.message || 'Không thể lưu thay đổi.'
  }
}

const actionConfirmType = ref<'delete' | 'end' | null>(null)
const actionConfirmMovie = ref<Movie | null>(null)

function promptDelete(movie: Movie) {
  if ((movieUsage.value[movie.id] || 0) > 0) {
    error.value = `Không thể xóa “${movie.title}” vì phim đã có lịch chiếu. Hãy dùng “Ngừng phát hành”.`
    return
  }
  actionConfirmType.value = 'delete'
  actionConfirmMovie.value = movie
}

function promptEnd(movie: Movie) {
  actionConfirmType.value = 'end'
  actionConfirmMovie.value = movie
}

function closeConfirmModal() {
  actionConfirmType.value = null
  actionConfirmMovie.value = null
}

async function executeAction() {
  if (!actionConfirmMovie.value || !actionConfirmType.value) return
  error.value = ''
  const movie = actionConfirmMovie.value
  
  if (actionConfirmType.value === 'delete') {
    try {
      await adminBackendService.deleteMovie(movie.id)
      movies.value = movies.value.filter((item) => item.id !== movie.id)
      delete movieUsage.value[movie.id]
      closeConfirmModal()
      success.value = 'Đã xóa phim chưa sử dụng khỏi kho.'
    } catch (e: any) {
      error.value = e?.message || 'Không thể xóa phim vì đang có dữ liệu lịch chiếu liên quan.'
    }
  } else if (actionConfirmType.value === 'end') {
    try {
      const updated = await adminBackendService.updateMovie(movie.id, {
        title: movie.title,
        original_title: movie.originalTitle || movie.title,
        description: movie.description || null,
        duration_min: movie.duration,
        release_date: movie.releaseDate || null,
        poster_url: movie.poster === '/images/movie-placeholder.svg' ? null : movie.poster,
        trailer_url: movie.trailer || null,
        age_rating: movie.ageRating || null,
        language: movie.language || null,
        status: 'ENDED',
        genres: movie.genre,
        director: movie.director || null,
        cast_names: movie.cast,
      })
      movies.value = movies.value.map((item) => item.id === updated.id ? updated : item)
      closeConfirmModal()
      success.value = 'Đã chuyển phim sang trạng thái kết thúc.'
    } catch (e: any) {
      error.value = e?.message
        ? `${e.message} Hãy xử lý tại Giám sát lịch chiếu.`
        : 'Không thể ngừng phát hành phim.'
    }
  }
}

function openScheduleMonitor(movie: Movie) {
  navigateTo({ path: '/admin/dashboard', query: { tab: 'schedule-monitor', movie_id: movie.id } })
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="space-y-6">
    <div class="panel flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between">
      <div>
        <h2 class="text-xl font-bold text-on-surface">Kho phim toàn hệ thống</h2>
        <p class="text-sm text-on-surface-variant mt-1">Nội dung phim dùng chung; lịch chiếu được vận hành riêng tại từng chi nhánh.</p>
      </div>
      <div class="flex flex-wrap gap-2 text-xs font-bold">
        <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1.5">Tất cả {{ statusCounts.ALL }}</span>
        <span class="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-emerald-300">Đang chiếu {{ statusCounts.NOW_SHOWING }}</span>
        <span class="rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1.5 text-blue-300">Chờ mở bán {{ statusCounts.UPCOMING }}</span>
        <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-on-surface-variant">Kết thúc {{ statusCounts.ENDED }}</span>
      </div>
    </div>

    <p v-if="error" class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm font-medium text-rose-400">
      {{ error }}
    </p>
    <p v-if="success" class="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm font-medium text-emerald-300">{{ success }}</p>

    <!-- Import Tool -->
    <div class="panel p-6 shadow-[0_0_30px_rgba(30,136,229,0.1)] border-blue-500/20 relative overflow-hidden">
      <!-- Decoration -->
      <div class="absolute -right-12 -top-12 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div class="relative z-10">
        <h3 class="text-lg font-bold text-on-surface flex items-center gap-2 mb-1">
          <span class="material-symbols-outlined text-blue-400">cloud_download</span>
          Import phim từ TMDB
        </h3>
        <p class="text-sm text-on-surface-variant mb-5">Poster, mô tả, ngày phát hành, trailer và thể loại sẽ được đồng bộ tự động.</p>
        
        <form class="grid gap-3 md:grid-cols-[1.5fr_2fr_auto]" @submit.prevent="importTmdbMovieToCatalog">
          <div class="relative">
            <label for="tmdb-movie-filter" class="sr-only">Tìm nhanh trong danh sách phim TMDB</label>
            <span
              class="material-symbols-outlined pointer-events-none absolute left-3 top-1/2 z-10 -translate-y-1/2 text-[18px] text-blue-300">
              search
            </span>
            <input
              id="tmdb-movie-filter"
              v-model="tmdbMovieQuery"
              placeholder="Tìm trực tiếp trên TMDB..."
              class="field-input tmdb-search-input"
            />
          </div>
          <select v-model="selectedTmdbMovieId" class="field-input font-medium" required>
            <option value="">-- Chọn phim từ TMDB --</option>
            <option v-for="movie in filteredTmdbMovies" :key="movie.tmdb_id" :value="String(movie.tmdb_id)">
              {{ movie.title }}{{ movie.release_date ? ` (${movie.release_date.slice(0, 4)})` : '' }}
            </option>
          </select>
          <button class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold px-6 py-2 rounded-xl transition hover:shadow-lg hover:shadow-blue-500/20 active:scale-[0.98] disabled:opacity-50" :class="existingCatalogMovie ? '!from-amber-600 !to-orange-600' : ''" :disabled="tmdbImporting">
            {{ tmdbImporting ? 'Đang xử lý...' : duplicateImportConfirmed ? 'Xác nhận đồng bộ' : existingCatalogMovie ? 'Phim đã tồn tại' : 'Import phim' }}
          </button>
        </form>
        <p class="mt-2 text-xs text-on-surface-variant">
          {{ tmdbSearching ? 'Đang tìm trên TMDB...' : 'Import chỉ thêm phim vào kho ở trạng thái Chờ mở bán. Khi Branch Admin công bố suất chiếu đầu tiên, phim tự chuyển thành Đang chiếu. Import lại không làm thay đổi trạng thái đang bán.' }}
        </p>

        <div v-if="selectedTmdbMovie" class="mt-4 flex gap-4 bg-black/30 p-4 rounded-xl border border-white/5 animate-fade-in">
          <img
            :src="selectedTmdbMovie.poster_path ? `/api/tmdb-image/w185${selectedTmdbMovie.poster_path}` : '/images/movie-placeholder.svg'"
            :alt="selectedTmdbMovie.title"
            class="h-28 w-20 rounded-lg object-cover shadow-lg"
          />
          <div class="flex-1 min-w-0">
            <p class="font-bold text-on-surface text-lg truncate">{{ selectedTmdbMovie.title }}</p>
            <p class="text-xs text-on-surface-variant mt-0.5">Khởi chiếu: {{ selectedTmdbMovie.release_date || 'Chưa công bố' }}</p>
            <p class="mt-2 text-sm text-on-surface-variant line-clamp-3 leading-relaxed">{{ selectedTmdbMovie.overview || 'TMDB chưa có mô tả tiếng Việt.' }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Manual Create Toggle -->
    <div class="text-right">
      <button @click="showManualCreate = !showManualCreate" class="text-sm font-semibold text-primary hover:underline flex items-center justify-end gap-1 ml-auto">
        <span>Nhập thủ công (nếu phim không có trên TMDB)</span>
        <span class="material-symbols-outlined text-[18px] transition-transform" :class="showManualCreate ? 'rotate-180' : ''">expand_more</span>
      </button>
    </div>
    
    <!-- Manual Create Form -->
    <div v-if="showManualCreate" class="panel p-6 animate-fade-in border border-primary/20">
      <h3 class="font-bold text-lg mb-4 text-on-surface">Thêm phim thủ công</h3>
      <form class="grid gap-4 md:grid-cols-3" @submit.prevent="createMovie">
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên phim</label>
          <input v-model="movieForm.title" class="field-input" required />
        </div>
        <div v-if="existingCatalogMovie" class="mt-3 flex items-start gap-3 rounded-xl border border-amber-400/30 bg-amber-400/10 px-4 py-3 text-sm text-amber-200">
          <span class="material-symbols-outlined mt-0.5">warning</span>
          <div><p class="font-bold">Phim này đã có trong kho CineAI</p><p class="mt-0.5 text-xs text-amber-100/70">{{ existingCatalogMovie.title }} · {{ existingCatalogMovie.status === 'NOW_SHOWING' ? 'Đang chiếu' : existingCatalogMovie.status === 'UPCOMING' ? 'Chờ mở bán' : 'Đã kết thúc' }}. Đồng bộ lại chỉ cập nhật nội dung TMDB, không đổi trạng thái vận hành.</p></div>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên gốc</label>
          <input v-model="movieForm.originalTitle" class="field-input" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Thời lượng (phút)</label>
          <input v-model.number="movieForm.duration" type="number" min="1" class="field-input" required />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Ngày phát hành</label>
          <input v-model="movieForm.releaseDate" type="date" class="field-input" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Trạng thái ban đầu</label>
          <div class="field-input flex items-center text-blue-300">Chờ mở bán</div>
        </div>
        <div class="space-y-1 md:col-span-2">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Poster URL</label>
          <input v-model="movieForm.poster" type="url" class="field-input" placeholder="https://..." />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Phân loại tuổi</label>
          <input v-model="movieForm.ageRating" class="field-input" placeholder="P, K, T13, T16, T18" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Ngôn ngữ</label>
          <input v-model="movieForm.language" class="field-input" placeholder="Tiếng Việt" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Đạo diễn</label>
          <input v-model="movieForm.director" class="field-input" />
        </div>
        <div class="space-y-1 md:col-span-2">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Diễn viên</label>
          <input v-model="movieForm.castText" class="field-input" placeholder="Ngăn cách bằng dấu phẩy" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Trailer URL</label>
          <input v-model="movieForm.trailer" type="url" class="field-input" placeholder="https://youtube.com/..." />
        </div>
        <fieldset class="space-y-2 md:col-span-3">
          <legend class="text-xs font-semibold text-on-surface-variant uppercase">Thể loại *</legend>
          <div class="grid grid-cols-2 gap-2 rounded-xl border border-white/10 bg-black/20 p-3 md:grid-cols-4">
            <label v-for="genre in CANONICAL_MOVIE_GENRES" :key="genre" class="flex items-center gap-2 text-sm text-on-surface-variant">
              <input v-model="movieForm.genres" type="checkbox" :value="genre" class="accent-primary" />
              {{ genre }}
            </label>
          </div>
        </fieldset>
        <div class="space-y-1 md:col-span-3">
          <label class="text-xs font-semibold text-on-surface-variant uppercase">Mô tả</label>
          <textarea v-model="movieForm.description" class="field-input" rows="2"></textarea>
        </div>
        <div class="flex justify-end gap-3 md:col-span-3 pt-2">
          <button type="button" @click="showManualCreate = false" class="px-5 py-2 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Đóng</button>
          <button class="action-primary px-8">Tạo phim thủ công</button>
        </div>
      </form>
    </div>

    <div class="panel grid gap-3 p-4 md:grid-cols-[1fr_220px]">
      <div class="relative">
        <span class="material-symbols-outlined pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
        <input v-model="catalogQuery" class="field-input pl-11" placeholder="Tìm theo tên phim hoặc thể loại..." />
      </div>
      <select v-model="catalogStatus" class="field-input">
        <option value="ALL">Tất cả trạng thái</option>
        <option value="NOW_SHOWING">Đang chiếu</option>
        <option value="UPCOMING">Chờ mở bán</option>
        <option value="ENDED">Đã kết thúc</option>
      </select>
    </div>

    <!-- Movies List -->
    <div class="panel overflow-hidden">
      <div v-if="loading" class="py-12 flex justify-center">
        <div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm min-w-[900px]">
          <thead class="bg-white/5 border-b border-white/10">
            <tr class="text-left text-on-surface-variant">
              <th class="px-5 py-4 font-semibold w-96">Phim</th>
              <th class="px-5 py-4 font-semibold">Trạng thái</th>
              <th class="px-5 py-4 font-semibold">Thời lượng</th>
              <th class="px-5 py-4 font-semibold text-center">Lịch chiếu</th>
              <th class="px-5 py-4 font-semibold text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr v-for="movie in paginatedMovies" :key="movie.id" class="group hover:bg-white/[0.02] transition-colors">
              <td class="px-5 py-3">
                <div class="flex gap-3 items-center">
                  <img :src="movie.poster" :alt="movie.title" class="w-10 h-14 rounded object-cover shadow border border-white/10" />
                  <div>
                    <div class="font-bold text-on-surface text-base">{{ movie.title }}</div>
                    <div class="text-[11px] text-on-surface-variant line-clamp-1 mt-0.5" :title="movie.genre.join(', ')">{{ movie.genre.join(', ') || 'Chưa cập nhật thể loại' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-5 py-3">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border"
                  :class="
                    movie.status === 'NOW_SHOWING' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                    movie.status === 'UPCOMING' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                    'bg-white/5 text-on-surface-variant border-white/10'
                  "
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="
                    movie.status === 'NOW_SHOWING' ? 'bg-emerald-400' :
                    movie.status === 'UPCOMING' ? 'bg-blue-400' :
                    'bg-on-surface-variant'
                  "></span>
                  {{ movie.status === 'NOW_SHOWING' ? 'Đang chiếu' : movie.status === 'UPCOMING' ? 'Chờ mở bán' : 'Đã kết thúc' }}
                </span>
              </td>
              <td class="px-5 py-3 text-on-surface-variant">{{ movie.duration }} phút</td>
              <td class="px-5 py-3 text-center">
                <button @click="openScheduleMonitor(movie)" class="inline-flex items-center justify-center min-w-[2rem] h-6 px-2 rounded-lg text-xs font-bold bg-black/40 border border-white/10 hover:border-primary/50 hover:text-primary transition" title="Mở giám sát lịch chiếu của phim">
                  {{ movieUsage[movie.id] || 0 }}
                </button>
              </td>
              <td class="px-5 py-3">
                <div class="flex items-center justify-end gap-2 opacity-70 group-hover:opacity-100 transition-opacity">
                  <button @click="openEditModal(movie)" class="p-2 rounded-lg bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 transition tooltip" title="Chỉnh sửa">
                    <span class="material-symbols-outlined text-[18px]">edit</span>
                  </button>
                  <button v-if="movie.status !== 'ENDED'" @click="promptEnd(movie)" class="p-2 rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition tooltip" title="Ngừng phát hành">
                    <span class="material-symbols-outlined text-[18px]">stop_circle</span>
                  </button>
                  <button 
                    @click="promptDelete(movie)" 
                    class="p-2 rounded-lg transition tooltip"
                    :class="(movieUsage[movie.id] || 0) > 0 ? 'bg-white/5 text-white/20 cursor-not-allowed' : 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20'" 
                    :title="(movieUsage[movie.id] || 0) > 0 ? 'Không thể xoá: Đang có lịch chiếu' : 'Xoá khỏi kho'"
                  >
                    <span class="material-symbols-outlined text-[18px]">delete</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!paginatedMovies.length" class="py-12 text-center text-sm text-on-surface-variant">Không tìm thấy phim phù hợp.</div>
      </div>
      <div v-if="totalPages > 1" class="flex items-center justify-between border-t border-white/10 px-5 py-3 text-sm">
        <span class="text-on-surface-variant">Trang {{ currentPage }}/{{ totalPages }} · {{ filteredMovies.length }} phim</span>
        <div class="flex gap-2">
          <button class="rounded-lg border border-white/10 px-3 py-1.5 disabled:opacity-30" :disabled="currentPage === 1" @click="currentPage--">Trước</button>
          <button class="rounded-lg border border-white/10 px-3 py-1.5 disabled:opacity-30" :disabled="currentPage === totalPages" @click="currentPage++">Sau</button>
        </div>
      </div>
    </div>

    <!-- Edit Movie Drawer/Modal -->
    <div v-if="editingMovieId" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border border-white/10 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col" @click.stop>
        <div class="p-5 border-b border-white/10 flex items-center justify-between shrink-0 bg-black/20">
          <h3 class="text-lg font-bold text-on-surface">Chỉnh sửa phim</h3>
          <button @click="closeEditModal" class="text-on-surface-variant hover:text-white transition">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-5">
          <div class="grid md:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên phim</label>
              <input v-model="movieEditForm.title" class="field-input" required />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Tên gốc</label>
              <input v-model="movieEditForm.originalTitle" class="field-input" />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Thời lượng (phút)</label>
              <input v-model.number="movieEditForm.duration" type="number" class="field-input" required />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Khởi chiếu</label>
              <input v-model="movieEditForm.releaseDate" type="date" class="field-input" />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Trạng thái vận hành</label>
              <div class="field-input flex items-center font-medium" :class="movieEditForm.status === 'NOW_SHOWING' ? 'text-emerald-300' : movieEditForm.status === 'UPCOMING' ? 'text-blue-300' : 'text-on-surface-variant'">
                {{ movieEditForm.status === 'NOW_SHOWING' ? 'Đang chiếu' : movieEditForm.status === 'UPCOMING' ? 'Chờ mở bán' : 'Đã kết thúc' }}
              </div>
              <p class="mt-1 text-[11px] text-on-surface-variant">Trạng thái được cập nhật theo việc công bố suất chiếu, không chỉnh tay tại đây.</p>
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Đạo diễn</label>
              <input v-model="movieEditForm.director" class="field-input" />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Phân loại tuổi</label>
              <input v-model="movieEditForm.ageRating" class="field-input" placeholder="P, K, T13, T16, T18" />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Ngôn ngữ</label>
              <input v-model="movieEditForm.language" class="field-input" />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Poster URL</label>
              <input v-model="movieEditForm.poster" type="url" class="field-input" />
            </div>
            <div class="space-y-1 md:col-span-2">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Diễn viên (cách nhau bởi dấu phẩy)</label>
              <input v-model="movieEditForm.castText" class="field-input" />
            </div>
            <div class="space-y-1 md:col-span-2">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Trailer URL</label>
              <input v-model="movieEditForm.trailer" type="url" class="field-input" />
            </div>
            <div class="space-y-1 md:col-span-2">
              <label class="text-xs font-semibold text-on-surface-variant uppercase block mb-2">Thể loại</label>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                <label v-for="genre in CANONICAL_MOVIE_GENRES" :key="genre" class="flex items-center gap-2 bg-black/20 px-3 py-2 rounded-lg border border-white/5 hover:bg-white/5 cursor-pointer transition">
                  <input v-model="movieEditForm.genres" type="checkbox" :value="genre" class="accent-primary" />
                  <span class="text-sm select-none">{{ genre }}</span>
                </label>
              </div>
            </div>
            <div class="space-y-1 md:col-span-2">
              <label class="text-xs font-semibold text-on-surface-variant uppercase">Mô tả phim</label>
              <textarea v-model="movieEditForm.description" class="field-input custom-scrollbar" rows="4"></textarea>
            </div>
          </div>
        </div>
        <div class="p-4 border-t border-white/10 bg-black/40 flex justify-end gap-3 shrink-0">
          <button @click="closeEditModal" class="px-5 py-2.5 rounded-xl font-bold text-on-surface-variant hover:bg-white/5 transition">Hủy</button>
          <button @click="saveMovieEdit" class="action-primary px-8">Lưu thay đổi</button>
        </div>
      </div>
    </div>
    
    <!-- Delete / End Action Confirm Modal -->
    <div v-if="actionConfirmType" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-[#1a1c1c] border rounded-2xl shadow-2xl w-full max-w-md overflow-hidden text-center p-6"
        :class="actionConfirmType === 'delete' ? 'border-rose-500/30' : 'border-amber-500/30'"
      >
        <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
          :class="actionConfirmType === 'delete' ? 'bg-rose-500/20 text-rose-500' : 'bg-amber-500/20 text-amber-500'"
        >
          <span class="material-symbols-outlined text-[32px]">{{ actionConfirmType === 'delete' ? 'delete_forever' : 'stop_circle' }}</span>
        </div>
        <h3 class="text-xl font-bold text-on-surface mb-2">
          {{ actionConfirmType === 'delete' ? 'Xoá vĩnh viễn phim?' : 'Ngừng phát hành?' }}
        </h3>
        <p class="text-sm text-on-surface-variant mb-6 leading-relaxed">
          <template v-if="actionConfirmType === 'delete'">
            Bạn sắp xoá vĩnh viễn phim <strong class="text-white">"{{ actionConfirmMovie?.title }}"</strong> khỏi kho dữ liệu.
            Hành động này chỉ thực hiện được khi phim chưa từng có suất chiếu nào.
          </template>
          <template v-else>
            Bạn sắp ngừng phát hành phim <strong class="text-white">"{{ actionConfirmMovie?.title }}"</strong>.
            Phim sẽ bị ẩn khỏi trang của khách hàng, nhưng lịch sử suất chiếu và doanh thu vẫn được giữ lại.
          </template>
        </p>
        
        <div class="flex gap-3">
          <button @click="closeConfirmModal" class="flex-1 py-2.5 rounded-xl font-bold border border-white/10 text-on-surface hover:bg-white/5 transition">Hủy bỏ</button>
          <button @click="executeAction" class="flex-1 py-2.5 rounded-xl font-bold transition text-white"
            :class="actionConfirmType === 'delete' ? 'bg-rose-600 hover:bg-rose-500 shadow-[0_0_20px_rgba(225,29,72,0.3)]' : 'bg-amber-600 hover:bg-amber-500 shadow-[0_0_20px_rgba(217,119,6,0.3)]'"
          >
            {{ actionConfirmType === 'delete' ? 'Xác nhận xoá' : 'Xác nhận ngừng' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.panel {
  background: var(--card, #1a1c1c);
  border: 1px solid var(--line, rgba(255, 255, 255, 0.08));
  border-radius: 1rem;
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.24);
}

.field-input {
  background: rgba(30, 32, 32, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.75rem;
  padding: 0.6rem 0.75rem;
  font-size: 0.875rem;
  color: #f5f5f5;
  transition: all 0.2s ease;
  width: 100%;
}

.field-input:focus {
  outline: none;
  border-color: rgba(229, 9, 20, 0.65);
  box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.15);
}

.field-input.tmdb-search-input {
  padding-left: 2.6rem;
}

.action-primary {
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #e50914 0%, #be0812 100%);
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: #fff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.action-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px -16px rgba(229, 9, 20, 0.95);
}

.animate-fade-in {
  animation: fadeIn 0.2s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>

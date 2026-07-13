import { defineStore } from 'pinia'
import { ref } from 'vue'
import { movieService, type Movie, type Showtime } from '~/services/api'

export const useMoviesStore = defineStore('movies', () => {
  const movies = ref<Movie[]>([])
  const recommendations = ref<Movie[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)   // thêm error
  const activeMovie = ref<Movie | null>(null)
  const activeShowtimes = ref<Showtime[]>([])

  async function fetchMovies() {
    loading.value = true
    error.value = null
    try {
      movies.value = await movieService.getAll()
    } catch (e) {
      console.error('Failed to load movies:', e)
      error.value = 'Không thể tải danh sách phim'
    } finally {
      loading.value = false
    }
  }

  async function fetchRecommendations() {
    error.value = null
    try {
      recommendations.value = await movieService.getRecommendations()
    } catch (e) {
      console.error('Failed to load recommendations:', e)
      error.value = 'Không thể tải gợi ý phim'
    }
  }

  async function fetchMovieDetails(id: string) {
    loading.value = true
    error.value = null
    try {
      activeMovie.value = await movieService.getById(id)
      activeShowtimes.value = await movieService.getShowtimes(id)
    } catch (e) {
      console.error(`Failed to load details for movie ${id}:`, e)
      error.value = `Không thể tải chi tiết phim ${id}`
      activeMovie.value = null
      activeShowtimes.value = []
    } finally {
      loading.value = false
    }
  }

  async function searchMovies(query: string) {
    if (!query.trim()) {
      await fetchMovies()
      return
    }
    loading.value = true
    error.value = null
    try {
      movies.value = await movieService.searchSemantically(query)
    } catch (e) {
      console.error('Failed search:', e)
      error.value = 'Không thể tìm kiếm phim'
    } finally {
      loading.value = false
    }
  }

  return {
    movies,
    recommendations,
    loading,
    error,              // expose error
    activeMovie,
    activeShowtimes,
    fetchMovies,
    fetchRecommendations,
    fetchMovieDetails,
    searchMovies
  }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { movieService, type Movie, type Showtime } from '~/services/api'

export const useMoviesStore = defineStore('movies', () => {
  const movies = ref<Movie[]>([])
  const recommendations = ref<Movie[]>([])
  const loading = ref(false)
  const activeMovie = ref<Movie | null>(null)
  const activeShowtimes = ref<Showtime[]>([])

  async function fetchMovies() {
    loading.value = true
    try {
      movies.value = await movieService.getAll()
    } catch (e) {
      console.error('Failed to load movies:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchRecommendations() {
    try {
      recommendations.value = await movieService.getRecommendations()
    } catch (e) {
      console.error('Failed to load recommendations:', e)
    }
  }

  async function fetchMovieDetails(id: string) {
    loading.value = true
    try {
      activeMovie.value = await movieService.getById(id)
      activeShowtimes.value = await movieService.getShowtimes(id)
    } catch (e) {
      console.error(`Failed to load details for movie ${id}:`, e)
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
    try {
      movies.value = await movieService.searchSemantically(query)
    } catch (e) {
      console.error('Failed search:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    movies,
    recommendations,
    loading,
    activeMovie,
    activeShowtimes,
    fetchMovies,
    fetchRecommendations,
    fetchMovieDetails,
    searchMovies
  }
})

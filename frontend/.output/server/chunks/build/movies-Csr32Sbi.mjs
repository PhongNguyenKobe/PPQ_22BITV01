import { d as defineStore } from './server.mjs';
import { ref } from 'vue';
import { b as movieService } from './api-rwjTvGO1.mjs';

const useMoviesStore = defineStore("movies", () => {
  const movies = ref([]);
  const recommendations = ref([]);
  const loading = ref(false);
  const activeMovie = ref(null);
  const activeShowtimes = ref([]);
  async function fetchMovies() {
    loading.value = true;
    try {
      movies.value = await movieService.getAll();
    } catch (e) {
      console.error("Failed to load movies:", e);
    } finally {
      loading.value = false;
    }
  }
  async function fetchRecommendations() {
    try {
      recommendations.value = await movieService.getRecommendations();
    } catch (e) {
      console.error("Failed to load recommendations:", e);
    }
  }
  async function fetchMovieDetails(id) {
    loading.value = true;
    try {
      activeMovie.value = await movieService.getById(id);
      activeShowtimes.value = await movieService.getShowtimes(id);
    } catch (e) {
      console.error(`Failed to load details for movie ${id}:`, e);
      activeMovie.value = null;
      activeShowtimes.value = [];
    } finally {
      loading.value = false;
    }
  }
  async function searchMovies(query) {
    if (!query.trim()) {
      await fetchMovies();
      return;
    }
    loading.value = true;
    try {
      movies.value = await movieService.searchSemantically(query);
    } catch (e) {
      console.error("Failed search:", e);
    } finally {
      loading.value = false;
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
  };
});

export { useMoviesStore as u };
//# sourceMappingURL=movies-Csr32Sbi.mjs.map

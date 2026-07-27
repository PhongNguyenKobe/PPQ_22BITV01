import { defineStore } from 'pinia'
import { movieService } from '~/services/api'

interface Product {
  id: string | number
  backendMovieId?: string
  name: string
  price: number
  category: string
  imageUrl: string
  description: string
  rating?: number
  trailerUrl?: string
}

const TICKET_TYPES = ['2D', 'IMAX', '4DX', 'VIP']

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [] as Product[],
    loading: false,
    error: ''
  }),
  actions: {
    async fetchProducts(force = false) {
      const normalize = (value: string) =>
        value
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .toLowerCase()
          .trim()

      const extractTmdbId = (value?: string | null) => {
        if (!value) return null
        const match = value.match(/themoviedb\.org\/movie\/(\d+)/i)
        return match ? match[1] : null
      }

      // Cache: chi tao price/category 1 lan, khong random lai moi lan vao trang.
      // Tuy nhien, van can rehydrate backendMovieId neu truoc do phim chua duoc import.
      if (this.products.length && !force) {
        try {
          const backendMovies = await movieService.getAll()
          const backendByTitle = new Map<string, string>()
          const backendByTmdbId = new Map<string, string>()
          backendMovies.forEach((movie) => {
            backendByTitle.set(normalize(movie.title), movie.id)
            const tmdbId = extractTmdbId(movie.trailer)
            if (tmdbId) {
              backendByTmdbId.set(tmdbId, movie.id)
            }
          })

          this.products = this.products.map((product) => {
            if (product.backendMovieId) return product
            const byTmdb = backendByTmdbId.get(String(product.id))
            if (byTmdb) {
              return { ...product, backendMovieId: byTmdb }
            }
            const byTitle = backendByTitle.get(normalize(product.name))
            return byTitle ? { ...product, backendMovieId: byTitle } : product
          })
        } catch {
          // Keep existing cached data if rehydrate fails.
        }
        return
      }

      this.loading = true
      this.error = ''
      try {
        const [tmdbData, backendMovies] = await Promise.all([
          $fetch<any>('/api/movies'),
          movieService.getAll(),
        ])

        const backendByTitle = new Map<string, string>()
        const backendByTmdbId = new Map<string, string>()
        backendMovies.forEach((movie) => {
          backendByTitle.set(normalize(movie.title), movie.id)
          const tmdbId = extractTmdbId(movie.trailer)
          if (tmdbId) {
            backendByTmdbId.set(tmdbId, movie.id)
          }
        })

        const results = Array.isArray(tmdbData?.results) ? tmdbData.results : []

        this.products = results.map((movie: any) => {
          const normalizedTitle = normalize(String(movie.title || ''))
          const tmdbId = String(movie.id)
          return {
            id: movie.id,
            backendMovieId: backendByTmdbId.get(tmdbId) || backendByTitle.get(normalizedTitle),
            name: movie.title,
            price: Number(movie.suggested_ticket_price || 90000) / 1000,
            category: TICKET_TYPES[Math.floor(Math.random() * TICKET_TYPES.length)],
            imageUrl: movie.poster_url
              ? movie.poster_url
              : movie.poster_path
              ? `/api/tmdb-image/w500${movie.poster_path}`
              : '/images/movie-placeholder.svg',
            description: movie.overview,
            rating: movie.vote_average,
            trailerUrl: `https://www.youtube.com/results?search_query=${encodeURIComponent(`${movie.title} trailer`)}`,
          }
        })
      } catch (err) {
        console.error(err)
        this.error = 'Khong the tai danh sach phim.'
      } finally {
        this.loading = false
      }
    }
  }
})

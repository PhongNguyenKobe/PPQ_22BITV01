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
  status: 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'
  genres: string[]
  duration: number
  releaseDate: string
  director: string
  cast: string[]
}

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [] as Product[],
    loading: false,
    error: ''
  }),
  actions: {
    async fetchProducts(force = false) {
      if (this.products.length && !force) return

      this.loading = true
      this.error = ''
      try {
        const backendMovies = await movieService.getPublic()
        this.products = backendMovies.map((movie) => {
          return {
            id: movie.id,
            backendMovieId: movie.id,
            name: movie.title,
            price: 90,
            category: movie.genre[0] || 'Khác',
            genres: movie.genre,
            status: movie.status || 'UPCOMING',
            imageUrl: movie.poster,
            description: movie.description,
            rating: movie.rating,
            trailerUrl: movie.trailer,
            duration: movie.duration,
            releaseDate: movie.releaseDate,
            director: movie.director,
            cast: movie.cast,
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

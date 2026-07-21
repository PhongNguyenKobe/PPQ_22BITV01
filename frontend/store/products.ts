import { defineStore } from 'pinia'

interface Product {
  id: number
  name: string
  price: number
  category: string
  imageUrl: string
  description: string
  rating?: number
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
      // Cache: chỉ generate price/category 1 lần, không random lại mỗi lần vào trang
      if (this.products.length && !force) return

      this.loading = true
      this.error = ''
      try {
        const data: any = await $fetch('/api/movies')

        this.products = data.results.map((movie: any) => ({
          id: movie.id,
          name: movie.title,
          price: (Math.floor(Math.random() * 16) + 7) * 10,
          category: TICKET_TYPES[Math.floor(Math.random() * TICKET_TYPES.length)],
          imageUrl: movie.poster_path
            ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
            : 'https://placehold.co/500x750?text=No+Image',
          description: movie.overview,
          rating: movie.vote_average
        }))
      } catch (err) {
        console.error(err)
        this.error = 'Không thể tải danh sách sản phẩm.'
      } finally {
        this.loading = false
      }
    }
  }
})
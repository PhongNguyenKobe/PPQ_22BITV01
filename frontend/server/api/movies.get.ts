// frontend/server/api/movies.get.ts
import { tmdbFetch } from '~/server/utils/tmdb'

interface TMDBMovie {
  id: number
  title: string
  overview: string
  poster_path: string | null
  poster_url?: string | null
  vote_average?: number
  genre_ids?: number[]
  release_date?: string
  original_title?: string
}

interface TMDBResponse {
  page: number
  results: TMDBMovie[]
  total_pages: number
  total_results: number
}

interface BackendMovie {
  id: string
  title: string
  description?: string | null
  poster_url?: string | null
  trailer_url?: string | null
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const requestedList = String(getQuery(event).list || 'popular')
  const list = ['popular', 'now_playing', 'upcoming'].includes(requestedList)
    ? requestedList
    : 'popular'

  const fallback: TMDBResponse & {
    source: string
    reason: string
  } = {
    source: 'fallback',
    reason: 'unknown',
    page: 1,
    total_pages: 1,
    total_results: 3,
    results: [
      {
        id: 910001,
        title: 'Avengers: Demo War',
        overview: 'Biệt đội siêu anh hùng tái hợp.',
        poster_path: null,
      },
      {
        id: 910002,
        title: 'Love In Saigon',
        overview: 'Chuyện tình nơi đô thị hiện đại.',
        poster_path: null,
      },
      {
        id: 910003,
        title: 'Ghost Apartment',
        overview: 'Bí ẩn trong khu chung cư cũ.',
        poster_path: null,
      },
    ],
  }

  if (!config.tmdbToken) {
    return {
      ...fallback,
      reason: 'missing_tmdb_token',
    }
  }

  try {
    const data = await tmdbFetch<TMDBResponse>(
      `/3/movie/${list}`,
      config.tmdbToken,
      { language: 'vi-VN', page: 1 },
    )

    return {
      ...data,
      source: 'tmdb',
      results: data.results.map((movie) => ({
        ...movie,
        suggested_ticket_price: getSuggestedTicketPrice(movie),
      })),
    }
  } catch (error) {
    const reason =
      error instanceof Error
        ? error.message
        : 'tmdb_request_failed'

    try {
      const backendMovies = await $fetch<BackendMovie[]>(
        `${config.public.apiBase}/movies`,
      )
      if (backendMovies.length > 0) {
        return {
          source: 'backend',
          reason,
          page: 1,
          total_pages: 1,
          total_results: backendMovies.length,
          results: backendMovies.map((movie, index) => ({
            id: 920000 + index,
            backend_id: movie.id,
            title: movie.title,
            overview: movie.description || '',
            poster_path: null,
            poster_url: movie.poster_url || null,
            trailer_url: movie.trailer_url || null,
          })),
        }
      }
    } catch {
      // The frontend still remains usable when both external and backend APIs are unavailable.
    }

    return {
      ...fallback,
      reason,
    }
  }
})

// frontend/server/api/movies.get.ts

interface TMDBMovie {
  id: number
  title: string
  overview: string
  poster_path: string | null
}

interface TMDBResponse {
  page: number
  results: TMDBMovie[]
  total_pages: number
  total_results: number
}

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()

  const fallback: TMDBResponse & { source: string; reason: string } = {
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
    const data = await $fetch<TMDBResponse>(
      "https://api.tmdb.org/3/movie/popular",
      {
        headers: {
          Authorization: `Bearer ${config.tmdbToken}`,
          Accept: "application/json",
        },
        query: {
          language: "vi-VN",
          page: 1,
        },
      }
    )

    return {
      ...data,
      source: 'tmdb',
    }
  } catch (error) {
    console.error(error)
    const reason = error instanceof Error ? error.message : 'tmdb_request_failed'
    return {
      ...fallback,
      reason,
    }
  }
})

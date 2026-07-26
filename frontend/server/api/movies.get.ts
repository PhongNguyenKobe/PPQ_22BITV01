export default defineEventHandler(async () => {
  const config = useRuntimeConfig()

  const fallback = {
    source: 'fallback',
    reason: 'unknown',
    results: [
      {
        id: 910001,
        title: 'Avengers: Demo War',
        overview: 'Biet doi sieu anh hung tai hop.',
        poster_path: null,
      },
      {
        id: 910002,
        title: 'Love In Saigon',
        overview: 'Chuyen tinh noi do thi hien dai.',
        poster_path: null,
      },
      {
        id: 910003,
        title: 'Ghost Apartment',
        overview: 'Bi an trong khu chung cu cu.',
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
    const data = await $fetch(
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
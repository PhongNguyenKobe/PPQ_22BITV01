interface TmdbMovie {
  id: number
  title: string
  overview: string
  poster_path: string | null
  backdrop_path: string | null
  release_date: string
  runtime: number
  vote_average: number
  genres: { id: number; name: string }[]
}

interface TmdbVideo {
  key: string
  site: string
  type: string
  official: boolean
  name: string
}

interface TmdbPerson {
  name: string
  job?: string
  known_for_department?: string
}

interface TmdbCredits {
  cast: TmdbPerson[]
  crew: TmdbPerson[]
}

interface TmdbVideosResponse {
  results: TmdbVideo[]
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const id = getRouterParam(event, 'id')

  if (!config.tmdbToken) {
    return {
      id: String(id || ''),
      title: `Movie #${id}`,
      description: 'Dữ liệu chi tiết tạm thời do TMDB chưa cấu hình token.',
      poster: 'https://placehold.co/500x750?text=No+Image',
      rating: 0,
      duration: 120,
      releaseDate: '',
      genre: ['General'],
      director: '',
      cast: [],
      trailerUrl: '',
    }
  }

  try {
    // Fetch movie details, credits (cast/director), and videos (trailer) in parallel
    const [movie, credits, videos] = await Promise.all([
      $fetch<TmdbMovie>(`https://api.tmdb.org/3/movie/${id}`, {
        headers: {
          Authorization: `Bearer ${config.tmdbToken}`,
          Accept: 'application/json',
        },
        query: { language: 'vi-VN' },
      }),
      $fetch<TmdbCredits>(`https://api.tmdb.org/3/movie/${id}/credits`, {
        headers: {
          Authorization: `Bearer ${config.tmdbToken}`,
          Accept: 'application/json',
        },
        query: { language: 'vi-VN' },
      }),
      $fetch<TmdbVideosResponse>(`https://api.tmdb.org/3/movie/${id}/videos`, {
        headers: {
          Authorization: `Bearer ${config.tmdbToken}`,
          Accept: 'application/json',
        },
        query: { language: 'vi-VN' },
      }),
    ])

    // Extract trailer from videos (prefer YouTube, official trailer)
    let trailerKey = ''
    const trailers = videos.results || []
    const officialTrailer = trailers.find(
      (v) => v.site === 'YouTube' && v.type === 'Trailer' && v.official === true
    )
    const anyTrailer = trailers.find((v) => v.site === 'YouTube' && v.type === 'Trailer')
    
    if (officialTrailer) {
      trailerKey = officialTrailer.key
    } else if (anyTrailer) {
      trailerKey = anyTrailer.key
    } else {
      // Fallback: any YouTube video
      const anyYoutube = trailers.find((v) => v.site === 'YouTube')
      if (anyYoutube) trailerKey = anyYoutube.key
    }

    // Extract director from crew
    const crew = credits.crew || []
    const director = crew.find((c) => c.job === 'Director')?.name || ''

    // Extract top cast (max 5)
    const castList = (credits.cast || []).slice(0, 5).map((c) => c.name)

    // Format poster URL
    const posterUrl = movie.poster_path
      ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
      : 'https://placehold.co/500x750?text=No+Image'

    return {
      id: String(movie.id),
      title: movie.title,
      description: movie.overview,
      poster: posterUrl,
      rating: movie.vote_average,
      duration: movie.runtime,
      releaseDate: movie.release_date,
      genre: movie.genres.map((g) => g.name),
      director,
      cast: castList,
      trailerUrl: trailerKey ? `https://www.youtube.com/embed/${trailerKey}` : '',
    }
  } catch (error) {
    console.error(`TMDB movie detail fetch failed for id=${id}:`, error)
    return {
      id: String(id || ''),
      title: `Movie #${id}`,
      description: 'Không thể lấy chi tiết TMDB, đang hiển thị dữ liệu tạm thời.',
      poster: 'https://placehold.co/500x750?text=No+Image',
      rating: 0,
      duration: 120,
      releaseDate: '',
      genre: ['General'],
      director: '',
      cast: [],
      trailerUrl: '',
    }
  }
})


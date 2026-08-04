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

// TMDB movie genre IDs are stable. Keep one Vietnamese taxonomy in the
// internal catalog even when TMDB returns an untranslated English name.
const TMDB_GENRES_VI: Record<number, string> = {
  28: 'Hành động',
  12: 'Phiêu lưu',
  16: 'Hoạt hình',
  35: 'Hài',
  80: 'Tội phạm',
  99: 'Tài liệu',
  18: 'Chính kịch',
  10751: 'Gia đình',
  14: 'Kỳ ảo',
  36: 'Lịch sử',
  27: 'Kinh dị',
  10402: 'Âm nhạc',
  9648: 'Bí ẩn',
  10749: 'Lãng mạn',
  878: 'Khoa học viễn tưởng',
  10770: 'Phim truyền hình',
  53: 'Giật gân',
  10752: 'Chiến tranh',
  37: 'Miền Tây',
}

export default defineEventHandler(async (event): Promise<any> => {
  const config = useRuntimeConfig()
  const id = getRouterParam(event, 'id')
  const uuidLike = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(String(id || ''))

  if (uuidLike) {
    const movie = await $fetch<any>(`${config.public.apiBase}/movies/${id}`)
    return {
      id: String(movie.id),
      title: movie.title,
      description: movie.description || '',
      poster: movie.poster_url || '/images/movie-placeholder.svg',
      rating: 0,
      duration: Number(movie.duration_min || 0),
      releaseDate: movie.release_date || '',
      genre: Array.isArray(movie.genres) ? movie.genres.map((genre: any) => genre.name) : [],
      director: '',
      cast: [],
      trailerUrl: movie.trailer_url || '',
    }
  }

  if (!config.tmdbToken) {
    return {
      id: String(id || ''),
      title: `Movie #${id}`,
      description: 'Dữ liệu chi tiết tạm thời do TMDB chưa cấu hình token.',
      poster: '/images/movie-placeholder.svg',
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
      tmdbFetch<TmdbMovie>(`/3/movie/${id}`, config.tmdbToken, { language: 'vi-VN' }),
      tmdbFetch<TmdbCredits>(`/3/movie/${id}/credits`, config.tmdbToken, { language: 'vi-VN' }),
      tmdbFetch<TmdbVideosResponse>(`/3/movie/${id}/videos`, config.tmdbToken, { language: 'vi-VN' }),
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
      : '/images/movie-placeholder.svg'

    return {
      id: String(movie.id),
      title: movie.title,
      description: movie.overview,
      poster: movie.poster_path
        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
        : movie.backdrop_path
          ? `https://image.tmdb.org/t/p/w500${movie.backdrop_path}`
          : '/images/movie-placeholder.svg',
      rating: movie.vote_average || 0,
      duration: movie.runtime || 0,
      releaseDate: movie.release_date || '',
      genre: movie.genres?.map((genre) => TMDB_GENRES_VI[genre.id] || genre.name) || [],
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
      poster: '/images/movie-placeholder.svg',
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


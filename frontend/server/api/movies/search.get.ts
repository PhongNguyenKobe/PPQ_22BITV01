import { tmdbFetch } from '~/server/utils/tmdb'

interface TmdbSearchResponse {
  page: number
  total_pages: number
  total_results: number
  results: Array<{
    id: number
    title?: string
    original_title?: string
    overview?: string
    poster_path?: string | null
    release_date?: string
  }>
}

export default defineEventHandler(async (event) => {
  const query = String(getQuery(event).query || '').trim()
  if (query.length < 2) {
    return { source: 'tmdb', page: 1, total_pages: 0, total_results: 0, results: [] }
  }

  const config = useRuntimeConfig()
  if (!config.tmdbToken) {
    throw createError({ statusCode: 503, statusMessage: 'TMDB chưa được cấu hình' })
  }

  try {
    const data = await tmdbFetch<TmdbSearchResponse>('/3/search/movie', config.tmdbToken, {
      query,
      language: 'vi-VN',
      include_adult: 'false',
      page: 1,
    })
    return { ...data, source: 'tmdb' }
  } catch {
    throw createError({ statusCode: 502, statusMessage: 'Không thể tìm kiếm TMDB lúc này' })
  }
})

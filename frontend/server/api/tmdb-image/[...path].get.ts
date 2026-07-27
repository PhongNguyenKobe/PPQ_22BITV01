export default defineEventHandler(async (event) => {
  const path = getRouterParam(event, 'path')
  if (!path || path.includes('..')) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid image path' })
  }
  return proxyRequest(event, `https://image.tmdb.org/t/p/${path}`)
})

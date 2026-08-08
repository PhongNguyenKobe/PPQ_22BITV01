export function slugify(text: string): string {
  if (!text) return ''
  return text
    .toString()
    .toLowerCase()
    .normalize('NFD') // separate characters from their accents
    .replace(/[\u0300-\u036f]/g, '') // remove accents
    .replace(/[đĐ]/g, 'd') // replace đ/Đ with d
    .replace(/[^a-z0-9\s-]/g, '') // remove non-alphanumeric except space and hyphen
    .replace(/\s+/g, '-') // convert spaces to hyphens
    .replace(/-+/g, '-') // remove duplicate hyphens
    .trim()
}

export function getProductSlugUrl(product: { id: string | number; name?: string; title?: string }): string {
  const name = product.name || product.title || ''
  const slug = slugify(name)
  return `/products/${product.id}${slug ? '-' + slug : ''}`
}

export function getMovieSlugUrl(movie: { id: string | number; title?: string; name?: string }): string {
  const name = movie.title || movie.name || ''
  const slug = slugify(name)
  return `/movies/${movie.id}${slug ? '-' + slug : ''}`
}

export function extractIdFromSlug(slug: string): string {
  if (!slug) return ''
  
  // Check if it starts with a UUID (8-4-4-4-12 hex characters)
  const uuidRegex = /^([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})/i
  const uuidMatch = slug.match(uuidRegex)
  if (uuidMatch) {
    return uuidMatch[1]
  }
  
  // Check if it starts with a numeric ID followed by a hyphen or is just digits
  const numericRegex = /^(\d+)/
  const numericMatch = slug.match(numericRegex)
  if (numericMatch) {
    return numericMatch[1]
  }
  
  return slug
}

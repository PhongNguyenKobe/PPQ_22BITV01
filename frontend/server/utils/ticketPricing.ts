type TmdbPricingMovie = {
  id?: number
  vote_average?: number
  genre_ids?: number[]
}

/**
 * TMDB does not publish ticket prices. Convert stable TMDB metadata into a
 * suggested local price so the UI never generates a different random price.
 */
export function getSuggestedTicketPrice(movie: TmdbPricingMovie): number {
  const premiumGenres = new Set([12, 14, 28, 878])
  const hasPremiumGenre = (movie.genre_ids || []).some((id) => premiumGenres.has(id))
  const rating = Number(movie.vote_average || 0)

  let price = 90_000
  if (hasPremiumGenre) price += 20_000
  if (rating >= 7) price += 10_000
  return price
}

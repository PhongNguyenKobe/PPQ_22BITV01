import type { Showtime } from '~/services/api'

export function getShowtimeDate(showtime: Showtime): Date {
  return new Date(`${showtime.date}T${showtime.time}:00`)
}

export function isShowtimeExpired(showtime: Showtime | null | undefined): boolean {
  if (!showtime) return true
  const closesAt = showtime.bookingClosesAt
    ? new Date(showtime.bookingClosesAt)
    : getShowtimeDate(showtime)
  return closesAt.getTime() <= Date.now()
}

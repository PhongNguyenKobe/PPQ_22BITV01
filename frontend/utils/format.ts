/**
 * Format price to Vietnamese Dong with proper formatting
 * @param price - Price in VND
 * @returns Formatted price string (e.g., "100,000 đ")
 */
export const formatPrice = (price: number | string): string => {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(numPrice)
}

/**
 * Format date to Vietnamese format
 * @param date - Date string or Date object
 * @returns Formatted date string (e.g., "23/07/2026")
 */
export const formatDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(dateObj)
}

/**
 * Format time to HH:mm format
 * @param date - Date string or Date object
 * @returns Formatted time string (e.g., "19:30")
 */
export const formatTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(dateObj)
}

/**
 * Format datetime to full format
 * @param date - Date string or Date object
 * @returns Formatted datetime string (e.g., "23/07/2026 19:30")
 */
export const formatDateTime = (date: string | Date): string => {
  return `${formatDate(date)} ${formatTime(date)}`
}

/**
 * Format duration in minutes to readable format
 * @param minutes - Duration in minutes
 * @returns Formatted duration (e.g., "2 giờ 20 phút")
 */
export const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours === 0) return `${mins} phút`
  if (mins === 0) return `${hours} giờ`
  return `${hours} giờ ${mins} phút`
}

/**
 * Generate seat label from row and number
 * @param row - Seat row (e.g., "A")
 * @param number - Seat number (e.g., 1)
 * @returns Formatted seat label (e.g., "A1")
 */
export const formatSeatLabel = (row: string, number: number): string => {
  return `${row}${number}`
}

/**
 * Format order/booking ID to readable confirmation number
 * @param id - UUID or numeric ID
 * @returns Formatted confirmation number (e.g., "CineAI-2026072319-12345")
 */
export const formatConfirmationNumber = (id: string): string => {
  return `CineAI-${id.slice(0, 8).toUpperCase()}`
}

/**
 * Truncate long text with ellipsis
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns Truncated text with ellipsis
 */
export const truncate = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return `${text.slice(0, maxLength)}...`
}

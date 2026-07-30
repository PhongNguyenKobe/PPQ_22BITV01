/**
 * Formats a date string (e.g. yyyy-mm-dd or ISO string) to dd/mm/yyyy
 */
export function formatDate(dateVal: string | Date | undefined | null): string {
  if (!dateVal) return ''
  let d: Date
  if (typeof dateVal === 'string') {
    // If it's yyyy-mm-dd, parse it carefully to avoid time zone shifts
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateVal)) {
      const parts = dateVal.split('-')
      d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
    } else {
      d = new Date(dateVal)
    }
  } else {
    d = dateVal
  }
  if (isNaN(d.getTime())) return String(dateVal)
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}/${month}/${year}`
}

/**
 * Formats a date/datetime to dd/mm/yyyy hh:mm
 */
export function formatDateTime(dateVal: string | Date | undefined | null): string {
  if (!dateVal) return ''
  let d: Date
  if (typeof dateVal === 'string') {
    // Replace space with T to ensure valid parsing in ISO-like strings
    const normalized = dateVal.includes(' ') && !dateVal.includes('T') ? dateVal.replace(' ', 'T') : dateVal
    d = new Date(normalized)
  } else {
    d = dateVal
  }
  if (isNaN(d.getTime())) return String(dateVal)
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${day}/${month}/${year} ${hours}:${minutes}`
}

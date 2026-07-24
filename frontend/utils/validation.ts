/**
 * Validate email format
 * @param email - Email address to validate
 * @returns true if valid email
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number format (Vietnam)
 * @param phone - Phone number to validate
 * @returns true if valid phone number
 */
export const isValidPhoneVN = (phone: string): boolean => {
  const phoneRegex = /^(0|\+84)[0-9]{9,10}$/
  return phoneRegex.test(phone.replace(/\s/g, ''))
}

/**
 * Validate password strength
 * @param password - Password to validate
 * @returns { isValid, feedback } validation result with feedback
 */
export const validatePassword = (password: string): { isValid: boolean; feedback: string[] } => {
  const feedback: string[] = []
  let isValid = true

  if (password.length < 8) {
    feedback.push('Password must be at least 8 characters')
    isValid = false
  }

  if (!/[A-Z]/.test(password)) {
    feedback.push('Password must contain at least one uppercase letter')
    isValid = false
  }

  if (!/[a-z]/.test(password)) {
    feedback.push('Password must contain at least one lowercase letter')
    isValid = false
  }

  if (!/[0-9]/.test(password)) {
    feedback.push('Password must contain at least one number')
    isValid = false
  }

  return { isValid, feedback }
}

/**
 * Validate full name
 * @param name - Full name to validate
 * @returns true if valid full name
 */
export const isValidFullName = (name: string): boolean => {
  return name.trim().length >= 2 && name.trim().length <= 100
}

/**
 * Validate payment amount
 * @param amount - Amount to validate
 * @returns true if valid payment amount
 */
export const isValidPaymentAmount = (amount: number): boolean => {
  return amount > 0 && amount <= 1000000000 // Max 1 billion VND
}

/**
 * Validate seat selection
 * @param seatCount - Number of seats selected
 * @returns { isValid, message }
 */
export const validateSeatSelection = (seatCount: number): { isValid: boolean; message: string } => {
  if (seatCount === 0) {
    return { isValid: false, message: 'Please select at least one seat' }
  }
  if (seatCount > 10) {
    return { isValid: false, message: 'Maximum 10 seats per booking' }
  }
  return { isValid: true, message: '' }
}

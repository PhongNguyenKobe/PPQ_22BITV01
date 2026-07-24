/**
 * Custom error handler for API errors
 */
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public originalError?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Format error message for display
 * @param error - Error object or string
 * @returns User-friendly error message
 */
export const formatErrorMessage = (error: any): string => {
  if (typeof error === 'string') {
    return error
  }

  if (error instanceof ApiError) {
    switch (error.statusCode) {
      case 400:
        return 'Invalid request. Please check your input.'
      case 401:
        return 'Session expired. Please login again.'
      case 403:
        return 'You do not have permission to perform this action.'
      case 404:
        return 'The requested resource was not found.'
      case 409:
        return 'This resource already exists.'
      case 422:
        return 'Invalid data format. Please check your input.'
      case 500:
        return 'Server error. Please try again later.'
      default:
        return error.message || 'An unexpected error occurred.'
    }
  }

  if (error instanceof Error) {
    return error.message
  }

  if (error?.response?.data?.detail) {
    return error.response.data.detail
  }

  if (error?.message) {
    return error.message
  }

  return 'An unexpected error occurred.'
}

/**
 * Log error with context
 * @param error - Error to log
 * @param context - Additional context information
 */
export const logError = (error: any, context?: string): void => {
  if (process.client) {
    console.error(
      `[${context || 'Error'}]`,
      error instanceof Error ? error.message : error
    )
  }
}

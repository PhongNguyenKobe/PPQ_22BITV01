import axios from 'axios'

// Set this to false when backend (FastAPI) is running
const USE_MOCK = false
const API_BASE_URL = import.meta.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

function notify(message: string, type: 'success' | 'error') {
  if (import.meta.client) window.dispatchEvent(new CustomEvent('cineai:toast', { detail: { message, type } }))
}

export interface BulkShowtimeDraft {
  movie_id: string
  movie_title: string
  auditorium_id: string
  auditorium_name: string
  starts_at: string // Khóa cứng kiểu string để không bị lỗi 'string | Date'
  ends_at: string // Khóa cứng kiểu string
  base_price: number
  status?: 'DRAFT' | 'OPEN' | 'CANCELLED'
  date?: string
  time?: string
  [key: string]: any
}

// ----------------------------------------------------
// Xử lý lỗi tập trung cho toàn bộ API module
// ----------------------------------------------------
export interface ApiError {
  message: string
  status?: number
}

export function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    return {
      message:
        (error.response?.data as any)?.detail ||
        (error.response?.data as any)?.message ||
        error.message ||
        'Đã có lỗi xảy ra, vui lòng thử lại.',
      status: error.response?.status,
    }
  }
  if (error instanceof Error) {
    return { message: error.message }
  }
  return { message: 'Lỗi không xác định' }
}

// Interceptor: mọi lỗi đi qua apiClient đều được chuẩn hóa thành ApiError
apiClient.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toUpperCase()
    if (method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
      notify(response.data?.message || 'Thao tác thành công.', 'success')
    }
    return response
  },
  (error) => {
    const normalized = handleApiError(error)
    if (error.config?.headers?.['X-Suppress-Error-Toast'] !== 'true') {
      notify(normalized.message, 'error')
    }
    return Promise.reject(normalized)
  }
)

export function setAuthToken(token: string | null) {
  if (token) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${token}`
    return
  }

  delete apiClient.defaults.headers.common.Authorization
}

// TypeScript interfaces
export interface Movie {
  id: string
  title: string
  originalTitle?: string
  rating: number
  genre: string[]
  format: string[]
  poster: string
  trailer: string
  description: string
  duration: number
  releaseDate: string
  director: string
  cast: string[]
  isFeatured?: boolean
  aiMatchReason?: string
  status?: 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'
}

export interface TmdbPopularMovie {
  tmdb_id: number
  title: string
  overview: string
  poster_path: string | null
  release_date: string | null
  original_title: string | null
  suggested_ticket_price: number
}

export interface Showtime {
  id: string
  movieId: string
  branchName: string
  screenName: string
  date: string
  time: string
  price: number
  bookingClosesAt?: string
}

export interface Seat {
  id: string
  row: string
  number: number
  type: 'standard' | 'vip' | 'couple'
  status: 'available' | 'selected' | 'occupied'
  price: number
}

export interface UserTicket {
  id: string
  movieTitle: string
  poster: string
  branchName: string
  screenName: string
  date: string
  time: string
  seats: string[]
  totalAmount: number
  paymentMethod: string
  qrCode: string
  bookingDate: string
  status: string
  cancellationReason?: string | null
}

interface BackendUserTicket {
  id: string
  movie_title: string
  poster_url?: string | null
  branch_name: string
  auditorium_name: string
  starts_at: string
  seats?: Array<{ row: string; number: number }>
  total_price: number | string
  payment_method?: string | null
  booking_date: string
  status: string
  cancellation_reason?: string | null
}

export interface UserProfile {
  id: string
  name: string
  email: string
  role: 'customer' | 'admin' | 'branch-admin' | 'staff'
  isActive: boolean
  branchId?: string
  phone?: string | null
  dateOfBirth?: string | null
  gender?: string | null
  token?: string
}

export interface BackendAdminUser {
  id: string
  email: string
  phone: string | null
  full_name: string
  date_of_birth: string | null
  gender: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  roles: BackendRole[]
  branch_id: string | null
}

export interface BackendBranch {
  id: string
  code: string
  name: string
  city: string
}

export const CANONICAL_MOVIE_GENRES = [
  'Hành động',
  'Phiêu lưu',
  'Hoạt hình',
  'Hài',
  'Tội phạm',
  'Tài liệu',
  'Chính kịch',
  'Gia đình',
  'Kỳ ảo',
  'Lịch sử',
  'Kinh dị',
  'Âm nhạc',
  'Bí ẩn',
  'Lãng mạn',
  'Khoa học viễn tưởng',
  'Phim truyền hình',
  'Giật gân',
  'Chiến tranh',
  'Miền Tây',
] as const

const canonicalGenreLookup = new Map(
  CANONICAL_MOVIE_GENRES.map((genre) => [genre.toLocaleLowerCase('vi'), genre]),
)

export function normalizeMovieGenres(genres: string[]): string[] {
  return [...new Set(
    genres
      .map((genre) => canonicalGenreLookup.get(String(genre).trim().toLocaleLowerCase('vi')))
      .filter((genre): genre is typeof CANONICAL_MOVIE_GENRES[number] => Boolean(genre)),
  )]
}

export type TmdbMovieList = 'popular' | 'now_playing' | 'upcoming'

export function youtubeEmbedUrl(value?: string | null): string {
  if (!value) return ''
  try {
    const url = new URL(value)
    if (url.hostname === 'youtu.be') {
      const id = url.pathname.slice(1).split('/')[0]
      return id ? `https://www.youtube.com/embed/${id}` : ''
    }
    if (url.hostname.endsWith('youtube.com')) {
      if (url.pathname.startsWith('/embed/')) return value
      const id = url.searchParams.get('v') || (url.pathname.startsWith('/shorts/') ? url.pathname.split('/')[2] : '')
      return id ? `https://www.youtube.com/embed/${id}` : ''
    }
  } catch {
    return ''
  }
  return ''
}

export function youtubeTrailerLink(value: string | null | undefined, title: string): string {
  const embed = youtubeEmbedUrl(value)
  if (embed) return `https://www.youtube.com/watch?v=${embed.split('/').pop()}`
  return `https://www.youtube.com/results?search_query=${encodeURIComponent(`${title} official trailer`)}`
}

export interface BranchDetail extends BackendBranch {
  address_line: string
  district: string | null
  phone: string | null
  latitude: number | null
  longitude: number | null
  movies: Movie[]
  showtimes: BackendShowtime[]
}

export interface AdminBranchManage {
  id: string
  vendor_id: string
  code: string
  name: string
  address_line: string
  city: string
  district: string | null
  phone: string | null
  is_active: boolean
  auditoriums_count: number
}

export interface AdminAuditorium {
  id: string
  branch_id: string
  branch_name: string
  code: string
  name: string
  total_seats: number
  screen_type: string | null
  is_active: boolean
}

export interface AdminSeatType {
  id: number
  code: string
  name: string
}

export interface AdminSeat {
  id: string
  auditorium_id: string
  auditorium_name: string
  branch_name: string
  seat_row: string
  seat_number: number
  seat_type_id: number
  seat_type_code: string
  is_active: boolean
}

export interface AdminSeatLayoutCell {
  seat_row: string
  seat_number: number
  seat_type_id: number
  is_active: boolean
}

export interface AdminShowtime {
  id: string
  movie_id: string
  movie_title: string
  auditorium_id: string
  auditorium_name: string
  branch_name: string
  starts_at: string
  ends_at: string
  status: string
  stored_status: 'DRAFT' | 'OPEN' | 'CANCELLED'
  booking_closes_at: string | null
  cancellation_reason: string | null
  base_price: number
  booking_count: number
  sold_seats: number
  revenue: number
}

export interface AdminBooking {
  id: string
  movie_title: string
  branch_name: string
  auditorium_name: string
  starts_at: string
  seats: Array<{ id: string; row: string; number: number }>
  quantity: number
  total_price: number
  status: string
  cancellation_reason: string | null
  cancellation_requested_at: string | null
  cancellation_review_note: string | null
  cancellation_reviewed_at: string | null
  created_at: string
}

export interface AdminPayment {
  id: string
  booking_id: string
  user_id: string
  amount: number
  payment_method: string
  status: string
  transaction_id: string | null
  provider_ref: string | null
  provider_transaction_no: string | null
  bank_transaction_no: string | null
  bank_code: string | null
  card_type: string | null
  response_code: string | null
  provider_status: string | null
  signature_valid: boolean | null
  provider_paid_at: string | null
  last_verified_at: string | null
  refund_transaction_no: string | null
  refund_response_code: string | null
  refund_provider_status: string | null
  refund_error: string | null
  refund_attempts: number
  refund_requested_at: string | null
  refunded_at: string | null
  paid_at: string | null
  created_at: string
}

export interface BranchAdminSalesPoint {
  label: string
  tickets: number
}

export interface BranchAdminPromo {
  code: string
  discount: number
  desc: string
  active: boolean
}

export interface BranchAdminStats {
  branchId: string
  branchName: string
  ticketsSold: number
  activeShowtimes: number
  activePromos: number
  branchRevenue: number
  orders: number
  seatsSold: number
  occupancyRate: number
  movieCount: number
  showtimeCount: number
  salesChartData: BranchAdminSalesPoint[]
  showtimesList: AdminShowtime[]
  promotionsList: BranchAdminPromo[]
}

export interface SuperAdminStats {
  totalBranches: number
  totalMovies: number
  totalUsers: number
  totalRevenue: number
  todayRevenue: number
  monthRevenue: number
  ticketsSold: number
  successfulBookings: number
  cancelledBookings: number
  pendingBookings: number
  revenueChartData: { label: string; value: number }[]
  branchPerformance: { label: string; revenue: number; tickets: number }[]
  topMovies: { label: string; revenue: number; tickets: number }[]
  moviesList?: Movie[]
  usersList?: UserProfile[]
}

export interface MovieRequestPayload {
  title: string
  original_title?: string | null
  description?: string | null
  duration_min: number
  release_date?: string | null
  age_rating?: string | null
  language?: string | null
  trailer_url?: string | null
  poster_url?: string | null
  status: 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'
  genres: string[]
}

export interface MovieRequestCreatePayload {
  request_type: 'CREATE' | 'UPDATE' | 'DELETE'
  target_movie_id?: string | null
  payload: MovieRequestPayload
}

export interface MovieRequest {
  id: string
  requested_by_id: string
  target_movie_id: string | null
  request_type: 'CREATE' | 'UPDATE' | 'DELETE'
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  payload: MovieRequestPayload
  review_note: string | null
  created_at: string
}

export interface AdminCreateUserPayload {
  email: string
  full_name: string
  password: string
  phone?: string | null
  date_of_birth?: string | null
  gender?: string | null
  role_code: 'CUSTOMER' | 'BRANCH_ADMIN' | 'STAFF' | 'SUPER_ADMIN'
  branch_id?: string | null
}

export interface AdminUpdateUserPayload {
  full_name?: string
  phone?: string | null
  date_of_birth?: string | null
  gender?: string | null
  is_active?: boolean
}

export interface AdminCreateBranchPayload {
  vendor_id?: string | null
  code: string
  name: string
  address_line: string
  city: string
  district?: string | null
  phone?: string | null
  is_active?: boolean
}

export interface AdminUpdateBranchPayload {
  code?: string
  name?: string
  address_line?: string
  city?: string
  district?: string | null
  phone?: string | null
  is_active?: boolean
}

export interface AdminCreateAuditoriumPayload {
  branch_id: string
  code: string
  name: string
  total_seats: number
  screen_type?: string | null
  is_active?: boolean
}

export interface AdminUpdateAuditoriumPayload {
  code?: string
  name?: string
  total_seats?: number
  screen_type?: string | null
  is_active?: boolean
}

export interface AdminCreateSeatPayload {
  auditorium_id: string
  seat_row: string
  seat_number: number
  seat_type_id: number
  is_active?: boolean
}

export interface AdminUpdateSeatPayload {
  seat_row?: string
  seat_number?: number
  seat_type_id?: number
  is_active?: boolean
}

export interface AdminCreateShowtimePayload {
  movie_id: string
  auditorium_id: string
  starts_at: string
  ends_at: string
  status?: 'DRAFT' | 'OPEN' | 'CANCELLED'
  booking_closes_at?: string
  base_price: number
}

export interface AdminImportTmdbMoviePayload {
  tmdb_id: number
  title: string
  overview?: string | null
  poster_path?: string | null
  release_date?: string | null
  original_title?: string | null
  language?: string | null
  duration_min?: number
  trailer_url?: string | null
  genres?: string[]
  director?: string | null
  cast_names?: string[]
  status?: 'UPCOMING' | 'NOW_SHOWING'
}

export interface AdminImportTmdbMovieResult {
  id: string
  title: string
  imported: boolean
}

export interface AdminUpdateShowtimePayload {
  auditorium_id?: string
  starts_at?: string
  ends_at?: string
  status?: 'DRAFT' | 'OPEN' | 'CANCELLED'
  booking_closes_at?: string
  cancellation_reason?: string
  base_price?: number
}

export interface BackendRole {
  id: number
  code: string
  name: string
}

export interface BackendUser {
  id: string
  email: string
  phone: string | null
  full_name: string
  date_of_birth: string | null
  gender: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  roles: BackendRole[]
}

export interface AuthCredentials {
  identifier: string
  password: string
}

export interface RegisterPayload {
  email: string
  phone: string
  full_name: string
  date_of_birth?: string | null
  gender?: string | null
  address?: string | null
  receive_marketing_emails?: boolean
  password: string
}

export interface RegisterResponse {
  message: string
  email: string
}

export interface CheckIdentifierResponse {
  exists: boolean
  type?: 'email' | 'phone'
}

export interface VerifyOtpRequest {
  identifier: string
  code: string
}

export interface ResendOtpRequest {
  identifier: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: BackendUser
}

function mapBackendRoleToFrontend(roleCodes: string[]): UserProfile['role'] {

  const roles = roleCodes.map(r => r.toUpperCase())

  if (
    roles.includes('SUPER_ADMIN') ||
    roles.includes('ADMIN')
  ) {
    return 'admin'
  }


  if (
    roles.includes('BRANCH_ADMIN')
  ) {
    return 'branch-admin'
  }


  if (
    roles.includes('STAFF')
  ) {
    return 'staff'
  }


  return 'customer'
}

export function mapBackendUserToProfile(user: BackendUser, token?: string): UserProfile {
  return {
    id: user.id,
    name: user.full_name,
    email: user.email,
    role: mapBackendRoleToFrontend(user.roles.map(role => role.code)),
    isActive: user.is_active,
    phone: user.phone,
    dateOfBirth: user.date_of_birth,
    gender: user.gender,
    token,
  }
}

export function mapBackendAdminUserToProfile(user: BackendAdminUser): UserProfile {
  return {
    id: user.id,
    name: user.full_name,
    email: user.email,
    role: mapBackendRoleToFrontend(user.roles.map(role => role.code)),
    isActive: user.is_active,
    phone: user.phone,
    dateOfBirth: user.date_of_birth,
    gender: user.gender,
    branchId: user.branch_id || undefined,
  }
}

export const authService = {
  async login(credentials: AuthCredentials): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/auth/login', credentials)
    return res.data
  },

  async register(payload: RegisterPayload): Promise<RegisterResponse> {
    const res = await apiClient.post<RegisterResponse>('/auth/register', payload)
    return res.data
  },

  async checkIdentifier(identifier: string): Promise<CheckIdentifierResponse> {
    const res = await apiClient.post<CheckIdentifierResponse>('/auth/check-identifier', { identifier })
    return res.data
  },

  async verifyOtp(payload: VerifyOtpRequest): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/auth/verify-otp', payload)
    return res.data
  },

  async resendOtp(identifier: string): Promise<{ message: string }> {
    const res = await apiClient.post<{ message: string }>('/auth/resend-otp', { identifier })
    return res.data
  },

  async forgotPassword(identifier: string): Promise<{ message: string }> {
    const res = await apiClient.post<{ message: string }>('/auth/forgot-password', { identifier })
    return res.data
  },

  async resetPassword(payload: { identifier: string; code: string; new_password: string }): Promise<{ message: string }> {
    const res = await apiClient.post<{ message: string }>('/auth/reset-password', payload)
    return res.data
  },

  async me(): Promise<BackendUser> {
    const res = await apiClient.get<BackendUser>('/auth/me')
    return res.data
  }
}
// ----------------------------------------------------
// usersApi: các thao tác liên quan tới người dùng (khách hàng)
// dùng cho các tính năng tương lai: xem/sửa hồ sơ, lịch sử vé...
// ----------------------------------------------------
export interface UpdateProfilePayload {
  full_name?: string
  phone?: string | null
  date_of_birth?: string | null
  gender?: string | null
}

export const usersApi = {
  async getProfile(): Promise<UserProfile> {
    const res = await apiClient.get<BackendUser>('/users/me')
    return mapBackendUserToProfile(res.data)
  },

  async updateProfile(payload: UpdateProfilePayload): Promise<UserProfile> {
    const res = await apiClient.patch<BackendUser>('/users/me', payload)
    return mapBackendUserToProfile(res.data)
  },

  async changePassword(payload: { current_password: string; new_password: string }): Promise<void> {
    await apiClient.patch('/users/me/password', payload)
  },

  async getMyTickets(): Promise<UserTicket[]> {
    const res = await apiClient.get<BackendUserTicket[]>('/users/me/tickets')
    const invalidTicket = res.data.find(ticket =>
      !ticket.movie_title ||
      !ticket.branch_name ||
      !ticket.auditorium_name ||
      !ticket.starts_at
    )
    if (invalidTicket) {
      throw new Error('Backend đang chạy phiên bản cũ. Hãy khởi động lại backend để tải đầy đủ thông tin vé.')
    }
    return res.data
      .filter(ticket => ['CONFIRMED', 'CANCEL_REQUESTED', 'CANCELLED'].includes(ticket.status))
      .map(ticket => ({
        id: ticket.id,
        movieTitle: ticket.movie_title,
        poster: ticket.poster_url || '/images/movie-placeholder.svg',
        branchName: ticket.branch_name,
        screenName: ticket.auditorium_name,
        date: ticket.starts_at.slice(0, 10),
        time: ticket.starts_at.slice(11, 16),
        seats: (ticket.seats || []).map(seat => `${seat.row}${seat.number}`),
        totalAmount: Number(ticket.total_price),
        paymentMethod: ticket.payment_method || 'Không xác định',
        qrCode: `CINEAI_E_TICKET_${ticket.id}`,
        bookingDate: ticket.booking_date,
        status: ticket.status,
        cancellationReason: ticket.cancellation_reason,
      }))
  },

  async requestTicketCancellation(bookingId: string, reason: string): Promise<void> {
    await apiClient.put(`/bookings/${bookingId}/cancel-request`, null, { params: { reason } })
  },

}

export const branchesService = {
  /** Lấy danh sách rạp (public, không cần auth) */
  async getAll(): Promise<BackendBranch[]> {
    if (USE_MOCK) {
      return [
        { id: 'b1', code: 'CGV_HCM_Q1', name: 'CGV Quận 1', city: 'HCM' },
        { id: 'b2', code: 'CGV_HCM_Q7', name: 'CGV Quận 7', city: 'HCM' },
        { id: 'b3', code: 'BETA_HN_CG', name: 'Beta Cầu Giấy', city: 'Hà Nội' },
      ]
    }
    const res = await apiClient.get<BackendBranch[]>('/branches')
    return res.data
  },
  async getById(id: string, suppressErrorToast = false): Promise<BranchDetail> {
    const res = await apiClient.get<any>(`/branches/${id}`, {
      headers: suppressErrorToast ? { 'X-Suppress-Error-Toast': 'true' } : undefined,
    })
    return {
      ...res.data,
      movies: (res.data.movies || []).map(mapBackendMovieToFrontend),
      showtimes: res.data.showtimes || [],
    }
  },
}

export interface Promotion {
  id: string
  code: string
  name: string
  discount_type: 'PERCENT' | 'FIXED'
  discount_value: number
  max_discount: number | null
  min_order_amount: number
  starts_at: string
  ends_at: string
  usage_limit: number | null
  used_count: number
  is_active: boolean
}

export const adminBackendService = {
  async getPromotions(): Promise<Promotion[]> {
    const res = await apiClient.get<Promotion[]>('/promotions')
    return res.data
  },

  async createPromotion(payload: Omit<Promotion, 'id' | 'used_count'>): Promise<Promotion> {
    const res = await apiClient.post<Promotion>('/promotions', payload)
    return res.data
  },

  async updatePromotion(id: string, payload: Partial<Promotion>): Promise<Promotion> {
    const res = await apiClient.patch<Promotion>(`/promotions/${id}`, payload)
    return res.data
  },

  async disablePromotion(id: string): Promise<void> {
    await apiClient.delete(`/promotions/${id}`)
  },

  async createMovie(payload: {
    title: string
    description?: string
    duration_min: number
    release_date?: string | null
    poster_url?: string
    trailer_url?: string
    status: 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'
    genres?: string[]
  }): Promise<Movie> {
    const res = await apiClient.post<BackendMovie>('/admin/movies', payload)
    return mapBackendMovieToFrontend(res.data)
  },

  async updateMovie(movieId: string, payload: Record<string, unknown>): Promise<Movie> {
    const res = await apiClient.put<BackendMovie>(`/admin/movies/${movieId}`, payload)
    return mapBackendMovieToFrontend(res.data)
  },

  async deleteMovie(movieId: string): Promise<void> {
    await apiClient.delete(`/admin/movies/${movieId}`)
  },

  async getMovieUsage(): Promise<Record<string, number>> {
    const res = await apiClient.get<Record<string, number>>('/admin/movies/usage')
    return res.data
  },

  async getBranches(): Promise<BackendBranch[]> {
    const res = await apiClient.get<BackendBranch[]>('/admin/branches')
    return res.data
  },

  async getUsers(): Promise<UserProfile[]> {
    const res = await apiClient.get<BackendAdminUser[]>('/admin/users')
    return res.data.map(mapBackendAdminUserToProfile)
  },

  async updateUserRole(userId: string, roleCode: 'CUSTOMER' | 'BRANCH_ADMIN' | 'STAFF' | 'SUPER_ADMIN', branchId?: string | null): Promise<UserProfile> {
    const res = await apiClient.patch<BackendAdminUser>(`/admin/users/${userId}/role`, {
      role_code: roleCode,
      branch_id: branchId || null,
    })
    return mapBackendAdminUserToProfile(res.data)
  },

  async createUser(payload: AdminCreateUserPayload): Promise<UserProfile> {
    const res = await apiClient.post<BackendAdminUser>('/admin/users', payload)
    return mapBackendAdminUserToProfile(res.data)
  },

  async updateUser(userId: string, payload: AdminUpdateUserPayload): Promise<UserProfile> {
    const res = await apiClient.patch<BackendAdminUser>(`/admin/users/${userId}`, payload)
    return mapBackendAdminUserToProfile(res.data)
  },

  async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/admin/users/${userId}`)
  },

  async getBranchesManage(): Promise<AdminBranchManage[]> {
    const res = await apiClient.get<AdminBranchManage[]>('/admin/branches/manage')
    return res.data
  },

  async createBranch(payload: AdminCreateBranchPayload): Promise<AdminBranchManage> {
    const res = await apiClient.post<AdminBranchManage>('/admin/branches/manage', payload)
    return res.data
  },

  async updateBranch(branchId: string, payload: AdminUpdateBranchPayload): Promise<AdminBranchManage> {
    const res = await apiClient.patch<AdminBranchManage>(`/admin/branches/manage/${branchId}`, payload)
    return res.data
  },

  async deleteBranch(branchId: string): Promise<void> {
    await apiClient.delete(`/admin/branches/manage/${branchId}`)
  },

  async getAuditoriums(branchId?: string): Promise<AdminAuditorium[]> {
    const res = await apiClient.get<AdminAuditorium[]>('/admin/auditoriums', {
      params: branchId ? { branch_id: branchId } : undefined,
    })
    return res.data
  },

  async createAuditorium(payload: AdminCreateAuditoriumPayload): Promise<AdminAuditorium> {
    const res = await apiClient.post<AdminAuditorium>('/admin/auditoriums', payload)
    return res.data
  },

  async updateAuditorium(auditoriumId: string, payload: AdminUpdateAuditoriumPayload): Promise<AdminAuditorium> {
    const res = await apiClient.patch<AdminAuditorium>(`/admin/auditoriums/${auditoriumId}`, payload)
    return res.data
  },

  async deleteAuditorium(auditoriumId: string): Promise<void> {
    await apiClient.delete(`/admin/auditoriums/${auditoriumId}`)
  },

  async getSeatTypes(): Promise<AdminSeatType[]> {
    const res = await apiClient.get<AdminSeatType[]>('/admin/seat-types')
    return res.data
  },

  async getSeats(auditoriumId?: string): Promise<AdminSeat[]> {
    const res = await apiClient.get<AdminSeat[]>('/admin/seats', {
      params: auditoriumId ? { auditorium_id: auditoriumId } : undefined,
    })
    return res.data
  },

  async createSeat(payload: AdminCreateSeatPayload): Promise<AdminSeat> {
    const res = await apiClient.post<AdminSeat>('/admin/seats', payload)
    return res.data
  },

  async updateSeat(seatId: string, payload: AdminUpdateSeatPayload): Promise<AdminSeat> {
    const res = await apiClient.patch<AdminSeat>(`/admin/seats/${seatId}`, payload)
    return res.data
  },

  async deleteSeat(seatId: string): Promise<void> {
    await apiClient.delete(`/admin/seats/${seatId}`)
  },

  async saveSeatLayout(
    auditoriumId: string,
    seats: AdminSeatLayoutCell[],
  ): Promise<{ auditorium_id: string; active_seats: number; seats: AdminSeat[] }> {
    const res = await apiClient.put<{ auditorium_id: string; active_seats: number; seats: AdminSeat[] }>(
      `/admin/auditoriums/${auditoriumId}/seat-layout`,
      { seats },
    )
    return res.data
  },

  async getShowtimes(branchId?: string): Promise<AdminShowtime[]> {
    const res = await apiClient.get<AdminShowtime[]>('/admin/showtimes', {
      params: branchId ? { branch_id: branchId } : undefined,
    })
    return res.data
  },

  async createShowtime(payload: AdminCreateShowtimePayload): Promise<AdminShowtime> {
    const res = await apiClient.post<AdminShowtime>('/admin/showtimes', payload)
    return res.data
  },

  async createShowtimesBulk(payload: AdminCreateShowtimePayload[]): Promise<AdminShowtime[]> {
    const res = await apiClient.post<AdminShowtime[]>('/admin/showtimes/bulk', { showtimes: payload })
    return res.data
  },

  async publishShowtimes(showtimeIds: string[]): Promise<AdminShowtime[]> {
    const res = await apiClient.post<AdminShowtime[]>('/admin/showtimes/publish', {
      showtime_ids: showtimeIds,
    })
    return res.data
  },

  async updateShowtime(showtimeId: string, payload: AdminUpdateShowtimePayload): Promise<AdminShowtime> {
    const res = await apiClient.patch<AdminShowtime>(`/admin/showtimes/${showtimeId}`, payload)
    return res.data
  },

  async deleteShowtime(showtimeId: string): Promise<void> {
    await apiClient.delete(`/admin/showtimes/${showtimeId}`)
  },

  async getBookings(params: Record<string, string | number | undefined> = {}): Promise<{ total: number; bookings: AdminBooking[] }> {
    const res = await apiClient.get('/admin/bookings', { params })
    return res.data
  },

  async cancelBooking(bookingId: string, reason: string): Promise<AdminBooking> {
    const res = await apiClient.put(`/admin/bookings/${bookingId}/cancel`, null, { params: { reason } })
    return res.data
  },

  async rejectBookingCancellation(bookingId: string, reason: string): Promise<AdminBooking> {
    const res = await apiClient.put(`/admin/bookings/${bookingId}/reject-cancellation`, null, { params: { reason } })
    return res.data
  },

  async getPayments(params: Record<string, string | number | undefined> = {}): Promise<{ total: number; payments: AdminPayment[] }> {
    const res = await apiClient.get('/admin/payments', { params })
    return res.data
  },

  async refundPayment(paymentId: string, reason: string): Promise<void> {
    await apiClient.post(`/admin/payments/${paymentId}/refund`, null, { params: { reason } })
  },

  async reconcilePayment(paymentId: string): Promise<any> {
    return (await apiClient.post(`/admin/payments/${paymentId}/reconcile`)).data
  },

  async getPaymentHistory(paymentId: string): Promise<any[]> {
    return (await apiClient.get(`/admin/payments/${paymentId}/history`)).data
  },

  async getRevenueReport(start_date: string, end_date: string, group_by = 'day', branch_id?: string) {
    return (await apiClient.get('/admin/reports/revenue', { params: { start_date, end_date, group_by, branch_id } })).data
  },

  async getOccupancyReport(start_date: string, end_date: string, branch_id?: string) {
    return (await apiClient.get('/admin/reports/occupancy', { params: { start_date, end_date, branch_id } })).data
  },

  async getTopMoviesReport(start_date: string, end_date: string, branch_id?: string) {
    return (await apiClient.get('/admin/reports/top-movies', { params: { start_date, end_date, branch_id } })).data
  },

  async importTmdbMovie(payload: AdminImportTmdbMoviePayload): Promise<AdminImportTmdbMovieResult> {
    const res = await apiClient.post<AdminImportTmdbMovieResult>('/admin/movies/import-tmdb', payload)
    return res.data
  },

  async getMyMovieRequests(): Promise<MovieRequest[]> {
    const res = await apiClient.get<MovieRequest[]>('/branch-admin/movie-requests')
    return res.data
  },

  async submitMovieRequest(payload: MovieRequestCreatePayload): Promise<MovieRequest> {
    const res = await apiClient.post<MovieRequest>('/branch-admin/movie-requests', payload)
    return res.data
  },
}

// ----------------------------------------------------
// Mock Data Layer
// ----------------------------------------------------

export const mockMovies: Movie[] = [
  {
    id: '1',
    title: 'Thành Phố Vô Hình: 2050',
    rating: 4.8,
    genre: ['Cyberpunk', 'Viễn Tưởng', 'Kịch Tính'],
    format: ['IMAX', '2D', '4DX'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCy_q8U1fieQE3DjTaCLWjqCQwXrCZsXiBLHjmnmmQdpc2TKR3LyPghhABCJehjXUTnjJhNCXW204MFqaYE2F6SAkFM6Vcp0vNHexNphDczN1DfA7c4fQ83Pv_jeLe2omU0PmLCKdHJdLx_iKpnLYBNbgTbwQQMYq98mFTfrmA3tvGk4-TJWgr1DWg5lN4LBp0CtwANVnKNuRgWi-Dq5oCu-DNTlS1L5qxfTFgfiLAypE-U8kW4wGO2g-SRAcKQaGW6MHIKMPq5G1dl',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Trong một thế giới nơi thực tại ảo thay thế cuộc sống thật, một lập trình viên phát hiện ra lỗ hổng có thể thay đổi nhân loại mãi mãi.',
    duration: 120,
    releaseDate: '2026-03-01',
    director: 'Denis Villeneuve',
    cast: ['Timothée Chalamet', 'Zendaya'],
    isFeatured: true,
    aiMatchReason: 'Được gợi ý dựa trên sở thích xem phim sử thi viễn tưởng của bạn.'
  },
  {
    id: '2',
    title: 'Trí Tuệ Nhân Tạo: Khởi Nguyên',
    rating: 4.9,
    genre: ['Viễn Tưởng', 'Tâm Lý', 'Hành Động'],
    format: ['2D', 'IMAX'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC5YIBPGdjmKme0u144QgxhV8kFAUzB1QpOuRZIMzt8bMyzaU8hQ5DjgSFoTUmM3f04pqnUAPat8sFJslT3l9Mk392K-C10eXrEz04WIwE9EWxd8XaKP9U26ATs1zj7tdZ2UESEna1GM0Kjh71Y2obVEe5h50Aq_u8rjZ42vBtcE8OnuHEGuYp7VFfcR-Xwly_ZqfFgungKXhbizP94owkAIWGm0hU8hJ_CWKer9U-8VR9pyK5XTkG1na7YoUIIdSUbrXO3BKipdHbV',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Sự trỗi dậy của một ý thức nhân tạo vượt trội trong cơ thể sinh học lai, buộc con người phải định nghĩa lại ý nghĩa của sự sống.',
    duration: 135,
    releaseDate: '2026-04-15',
    director: 'Chad Stahelski',
    cast: ['Keanu Reeves', 'Donnie Yen'],
    isFeatured: true,
    aiMatchReason: 'Bạn đã xem các phần trước của Trí Tuệ Nhân Tạo. AI đề xuất suất chiếu lúc 20:15 có tỷ lệ ghế đẹp cao.'
  },
  {
    id: '3',
    title: 'Vũ Trụ Vô Tận',
    rating: 4.9,
    genre: ['Khoa học viễn tưởng'],
    format: ['IMAX', '2D'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAsXsmNAsVQJkGnBMFt8hVCOL3StF6Rpvk3zVnk32ITcyyDxsNGnR7UtMmJAhGIFYvawOokSkMOTMYIp2CwMUaiFN9tLkWhOCmnnIAWk-sxhiUj1WelW_trFZGAOEqI9YAYiXWITCmprEIqzsP7UOqcs4aB4EBCyzYc2nW-Nrr4FpdO-_u0ItPOzjjxSua2eKTU2QlwqaWuNNFxatNAXcpYXpjLXqDLaKX1h3aYS6WFGj5baKwnkYh_CFBZj7APY2TvvZGl6XZGfo6r',
    trailer: 'https://www.youtube.com/embed/zSWdZVtXT7E',
    description: 'Hành trình vượt qua các hố đen và ranh giới không gian để cứu rỗi nhân loại.',
    duration: 145,
    releaseDate: '2026-05-10',
    director: 'Christopher Nolan',
    cast: ['Matthew McConaughey', 'Anne Hathaway'],
    isFeatured: false,
    aiMatchReason: 'Trùng khớp 98% với gu điện ảnh triết lý, du hành vũ trụ của bạn.'
  },
  {
    id: '4',
    title: 'Đường Đua Rực Lửa',
    rating: 4.7,
    genre: ['Hành động'],
    format: ['4DX', '2D'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCVJ0pF6H6Q6x8A11elmfSY5U7fHjvGgD8ie8NQiRJCfHOIWBQ34Y23J-KVL9r-jo8jhHcPWtPXOkGa99bo7a39ROR_JccyD1JVn3VY-YDelSKiqKHeqY3Hnpt0CYoPjgm8LB2_-YpajUqjPoDaseOsneaBKf9F6vfwW-5ewbeouS52Y9PvlX0X3TqDJEExTkwLiDyIHMgXBtIAb_ql1S7-wO7cOk58V6X_caFWDygy3Hf-NW59nnBb6yW9Wkrl_v-lK_Uesw087ruB',
    trailer: 'https://www.youtube.com/embed/qEVUtrk8_B4',
    description: 'Cuộc đua sinh tử của những tay lái kiệt xuất trong thành phố Tokyo tương lai rực rỡ sắc màu neon.',
    duration: 110,
    releaseDate: '2026-06-01',
    director: 'Justin Lin',
    cast: ['Vin Diesel', 'Paul Walker'],
    isFeatured: false,
    aiMatchReason: 'Bộ phim khoa học viễn tưởng mới ra mắt, phù hợp với sở thích phim đen tối tương lai.'
  },
  {
    id: '5',
    title: 'Bóng Đêm Thành Phố',
    rating: 4.5,
    genre: ['Trinh thám'],
    format: ['2D'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCrvOfBYGCh68jDrlUdA7mR9ysFqNwPqXy8FfHZDzq5IDhu1LaAKCnpZP_6r2RAuaf8U0pA2DwNq6n7-MecZPLYhOSpf4ChD3W1zkUYnn54td6jsxTo5mKTxEwHQH6lN5miOIQVr4UEz4CrvJNQyDm0vHtLxC5fC9X3sDVl80ssQ0th2KyjUgr3mJVU_PhROH7v7G_1MLeNRvdeq72eGHyz-7gFY-f2Y0-uKqqRGMgc_ZeItXtN-o45w6ufWbQfF-hzWLkYPXbjrkRa',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Một thám tử tư đơn độc trong hành trình vạch trần âm mưu đen tối của thế lực ngầm núp bóng chính quyền.',
    duration: 125,
    releaseDate: '2026-06-15',
    director: 'David Fincher',
    cast: ['Brad Pitt', 'Morgan Freeman'],
    isFeatured: false,
    aiMatchReason: 'Có lượng đánh giá tích cực rất cao từ những người dùng có gu giống bạn.'
  },
  {
    id: '6',
    title: 'Vùng Đất Kỳ Diệu',
    rating: 4.8,
    genre: ['Hoạt hình'],
    format: ['2D', '3D'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDtf1Bo44PrFX22Kw9z86OmCD2kSMzYvn9FIBJNyiynU9kzhCUpjS2GrJAS471OpoZbKAdwO09wRpJEYOR1hnFxQZDHbjyzpq1Xqc_a5B4j96Jpkuw8cpDXaeawTNeKvQB7QAFWiQHMCxbUNEDjCedW8_sCwXuqiEmQ51RStuuqli-Edw1FCQoAdMcLsh0NYr_rhcZw6SXoQcSn1bGffo71EUG5coAtD66fcIQ8ZFXqy6DFUytSG6-HPjA7yzx6lllCPH8zHUvbjtRJ',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Chuyến phiêu lưu của những sinh vật kỳ lạ và đầy màu sắc nhằm bảo vệ nguồn sáng của thế giới thần tiên.',
    duration: 95,
    releaseDate: '2026-07-01',
    director: 'Hayao Miyazaki',
    cast: ['Chiyo', 'Haku'],
    isFeatured: false,
    aiMatchReason: 'Hoạt hình ấm lòng, được AI bình chọn phù hợp cho gia đình.'
  },
  {
    id: '7',
    title: 'Vương Triều Sụp Đổ',
    rating: 4.9,
    genre: ['Sử thi', 'Hành động'],
    format: ['2D', 'IMAX'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBEuXmT3DJgVIS-S5qYDVSEwlpd6AJEdTm4FNE6P_hDsDeIeHw12h3cqL8KUP_ZzJ1NPplkQMXFaDixf1SpqppnIEWvdntszhk32Wxotx-kSzP_-uH2pz6Rsn7jxg6zffbpTFuB8n14uS5xBA3L5LFb69siWHFi2XJCrSxvWL0oEaEXIcib0f9KtUzo32nAlJ9elce75zDdsYybXcDVEI0hAkhEhsAraeg2jRdMadn3UYG3CPCiZSKCREGmO9jCRIiKUfZIOL67qBIA',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Trận chiến sinh tử hào hùng thời trung cổ giữa hai đế quốc hùng mạnh tranh giành ngai vàng.',
    duration: 150,
    releaseDate: '2026-07-05',
    director: 'Ridley Scott',
    cast: ['Russell Crowe', 'Joaquin Phoenix'],
    isFeatured: false,
    aiMatchReason: 'Sử thi chiến tranh hoành tráng, trùng khớp gu phim hành động lịch sử của bạn.'
  },
  {
    id: '8',
    title: 'Lời Nguyền Của Búp Bê',
    rating: 4.1,
    genre: ['Kinh dị'],
    format: ['2D'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBZ-h6Nj0XbbSoeaY_kdXixgd94egb9YxZivSSas-cii0Z8O85It7_UYos6EHZN4akDfzdgmU9rIsXeUS3v3Y1L0fOlBF-YR8wEEHGHge0VJ1OiVcJCsLaZLKgrWGEGzWMPO_mY-WTnCsONl3wOCknvRhxC1sFPrPbwmX8G56lH6tdGRHdO3RyPEbt6B-DqCFvCtHlCaBTMOHHX2BdNzHDuWmiQhRIyKf2mXOZD_vIsrJnm6lvQNe-ZA7N71Z7fzpuYRnSEQrf82mb4',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Con búp bê cổ mang lời nguyền oán hận gieo rắc kinh hoàng cho gia đình nhỏ chuyển đến ngôi nhà cổ.',
    duration: 102,
    releaseDate: '2026-07-08',
    director: 'James Wan',
    cast: ['Patrick Wilson', 'Vera Farmiga'],
    isFeatured: false,
    aiMatchReason: 'Kinh dị rùng rợn từ James Wan, được AI đề xuất cho các đêm cuối tuần.'
  },
  {
    id: '9',
    title: 'Mùa Hè Ở Venice',
    rating: 4.4,
    genre: ['Lãng mạn', 'Hài hước'],
    format: ['2D'],
    poster: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAMSFtwCei8ZDrs4lICf_3j_TUSGR-62_yVaCzI_F_xPsPZBM8TfEzam-5eorL2CmtoinRaoyarRd9uNLCz4ZYNU83VGHY5A93LOV1bvjguYRd22aLBBDlIoF5b_Xl_MXmXYefjIbEG3KO9mQliQElFKVb91zfE67bSVea4S2vKMg8LGX5dEMhBayMvBYaoaC8mLeCcvSMKE6zLya3kaRyFrfRxnAoL_3keCFEa3QSXmEsRGGgv64V8he0mUxz4B5C6hl5kDL5p79ls',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Mối tình mùa hè lãng mạn đầy tiếng cười của cặp đôi trẻ vô tình gặp nhau tại thành phố Venice xinh đẹp.',
    duration: 108,
    releaseDate: '2026-07-09',
    director: 'Richard Linklater',
    cast: ['Ethan Hawke', 'Julie Delpy'],
    isFeatured: false,
    aiMatchReason: 'Mối tình ngọt ngào lãng mạn kết hợp hài hước nhẹ nhàng.'
  }
]

export const mockShowtimes: Showtime[] = [
  // Thành Phố Vô Hình
  { id: 's1', movieId: '1', branchName: 'CineAI Hùng Vương', screenName: 'IMAX Phòng 1', date: '2026-07-11', time: '18:00', price: 150000 },
  { id: 's2', movieId: '1', branchName: 'CineAI Hùng Vương', screenName: 'Phòng 3 (2D)', date: '2026-07-11', time: '20:30', price: 90000 },
  { id: 's3', movieId: '1', branchName: 'CineAI Sala Q2', screenName: 'IMAX Phòng A', date: '2026-07-11', time: '19:00', price: 160000 },
  { id: 's4', movieId: '1', branchName: 'CineAI Sala Q2', screenName: 'Phòng B (4DX)', date: '2026-07-12', time: '21:15', price: 180000 },
  // Trí Tuệ Nhân Tạo
  { id: 's5', movieId: '2', branchName: 'CineAI Hùng Vương', screenName: 'Phòng 2 (2D)', date: '2026-07-11', time: '19:30', price: 90000 },
  { id: 's6', movieId: '2', branchName: 'CineAI Nguyễn Du', screenName: 'Phòng 1 (4DX)', date: '2026-07-11', time: '20:15', price: 170000 },
  { id: 's7', movieId: '2', branchName: 'CineAI Sala Q2', screenName: 'Phòng C (2D)', date: '2026-07-12', time: '18:00', price: 100000 },
  // Vũ Trụ Vô Tận
  { id: 's8', movieId: '3', branchName: 'CineAI Sala Q2', screenName: 'IMAX Phòng A', date: '2026-07-11', time: '15:30', price: 160000 },
  { id: 's9', movieId: '3', branchName: 'CineAI Nguyễn Du', screenName: 'Phòng 2 (2D)', date: '2026-07-12', time: '19:45', price: 95000 },
  // Đường Đua Rực Lửa
  { id: 's10', movieId: '4', branchName: 'CineAI Sala Q2', screenName: 'Phòng D (2D)', date: '2026-07-11', time: '21:00', price: 120000 },
  // Bóng Đêm Thành Phố
  { id: 's11', movieId: '5', branchName: 'CineAI Hùng Vương', screenName: 'Phòng 4 (2D)', date: '2026-07-11', time: '22:00', price: 90000 },
  // Vùng Đất Kỳ Diệu
  { id: 's12', movieId: '6', branchName: 'CineAI Sala Q2', screenName: 'Phòng B (2D)', date: '2026-07-11', time: '14:00', price: 100000 },
  // Vương Triều Sụp Đổ
  { id: 's13', movieId: '7', branchName: 'CineAI Nguyễn Du', screenName: 'Phòng 1 (IMAX)', date: '2026-07-11', time: '17:00', price: 150000 },
  // Lời Nguyền Của Búp Bê
  { id: 's14', movieId: '8', branchName: 'CineAI Hùng Vương', screenName: 'Phòng 2 (2D)', date: '2026-07-11', time: '23:00', price: 95000 },
  // Mùa Hè Ở Venice
  { id: 's15', movieId: '9', branchName: 'CineAI Sala Q2', screenName: 'Phòng C (2D)', date: '2026-07-11', time: '16:30', price: 100000 }
]

export const generateSeats = (showtimeId: string): Seat[] => {
  const seats: Seat[] = []
  const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J']

  rows.forEach((row, rowIndex) => {
    for (let i = 1; i <= 10; i++) {
      const id = `${showtimeId}_${row}${i}`
      let type: 'standard' | 'vip' | 'couple' = 'standard'
      let priceMultiplier = 1.0

      if (row === 'E' || row === 'F' || row === 'G') {
        type = 'vip'
        priceMultiplier = 1.3
      } else if (row === 'J') {
        type = 'couple'
        priceMultiplier = 1.5
      }

      // Hardcode some occupied seats randomly for visualization
      const statusSeed = Math.random()
      let status: 'available' | 'occupied' = 'available'
      if (statusSeed < 0.25) {
        status = 'occupied'
      }

      seats.push({
        id,
        row,
        number: i,
        type,
        status,
        price: Math.round(90000 * priceMultiplier / 1000) * 1000
      })
    }
  })

  return seats
}

export const mockTickets: UserTicket[] = [
  {
    id: 't-9831',
    movieTitle: 'Interstellar (Re-release)',
    poster: 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=2070&auto=format&fit=crop',
    branchName: 'CineAI Sala Q2',
    screenName: 'IMAX Phòng A',
    date: '2026-06-20',
    time: '15:30',
    seats: ['F5', 'F6'],
    totalAmount: 416000,
    paymentMethod: 'Ví Momo',
    qrCode: 'CineAI_E_TICKET_MOCK_QR_CODE_1',
    bookingDate: '2026-06-19 12:44',
    status: 'CONFIRMED'
  }
]

// ----------------------------------------------------
// Backend Schema types (matching FastAPI response)
// ----------------------------------------------------
export interface BackendMovie {
  id: string
  tmdb_id: number | null
  title: string
  original_title: string | null
  description: string | null
  duration_min: number
  release_date: string | null
  age_rating: string | null
  language: string | null
  trailer_url: string | null
  poster_url: string | null
  director: string | null
  cast_names: string[]
  status: string
  created_at: string
  updated_at: string
  genres: { id: number; code: string; name: string }[]
}

export interface BackendShowtime {
  id: string
  movie_id: string
  auditorium_id: string
  starts_at: string
  ends_at: string
  status: string
  booking_closes_at: string
  base_price: number
  branch_name: string
  screen_name: string
}

export interface BackendSeat {
  id: string
  seat_row: string
  seat_number: number
  seat_type: string
  is_active: boolean
  status: string
  price: number
}

// ----------------------------------------------------
// Mapping functions: Backend → Frontend
// ----------------------------------------------------
export function mapBackendMovieToFrontend(bm: BackendMovie): Movie {
  return {
    id: bm.id,
    title: bm.title,
    originalTitle: bm.original_title || '',
    rating: 0, // backend không có rating, để 0
    genre: normalizeMovieGenres(bm.genres.map(g => g.name)),
    format: [], // backend không có format, để trống
    poster: bm.poster_url || '/images/movie-placeholder.svg',
    trailer: bm.trailer_url || '',
    description: bm.description || '',
    duration: bm.duration_min,
    releaseDate: bm.release_date || '',
    director: bm.director || '',
    cast: bm.cast_names || [],
    isFeatured: bm.status === 'NOW_SHOWING',
    aiMatchReason: undefined,
    status: bm.status as NonNullable<Movie['status']>,
  }
}

export function mapBackendShowtimeToFrontend(bs: BackendShowtime): Showtime {
  // starts_at: "2026-07-11T18:00:00+07:00"
  const startDate = new Date(bs.starts_at)
  // Keep the calendar date and time in the user's local cinema timezone.
  // toISOString() converts to UTC and can leave the date one day behind
  // while the time below is formatted locally.
  const dateStr = [
    startDate.getFullYear(),
    String(startDate.getMonth() + 1).padStart(2, '0'),
    String(startDate.getDate()).padStart(2, '0'),
  ].join('-')
  const timeStr = startDate.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false }) // "18:00"

  return {
    id: bs.id,
    movieId: bs.movie_id,
    branchName: bs.branch_name,
    screenName: bs.screen_name,
    date: dateStr,
    time: timeStr,
    price: Number(bs.base_price),
    bookingClosesAt: bs.booking_closes_at,
  }
}

export function mapBackendSeatToFrontend(seat: BackendSeat): Seat {
  let type: 'standard' | 'vip' | 'couple' = 'standard'
  if (seat.seat_type === 'VIP') type = 'vip'
  else if (seat.seat_type === 'COUPLE') type = 'couple'

  return {
    id: seat.id,
    row: seat.seat_row,
    number: seat.seat_number,
    type,
    status:
      seat.status === 'BOOKED' || seat.status === 'HOLD'
        ? 'occupied'
        : seat.status === 'HELD_BY_ME'
          ? 'selected'
          : 'available',
    price: Number(seat.price),
  }
}

// ----------------------------------------------------
// TMDB Detail Service (Nuxt server proxy)
// ----------------------------------------------------
export interface TmdbMovieDetail {
  id: string
  title: string
  description: string
  poster: string
  rating: number
  duration: number
  releaseDate: string
  genre: string[]
  director: string
  cast: string[]
  trailerUrl: string
}

export const tmdbService = {
  /**
   * Fetch movie details from TMDB via Nuxt server proxy.
   * Includes: poster, trailer YouTube URL, director, cast, genres, rating, duration.
   */
  async getMovieDetail(id: string | number): Promise<TmdbMovieDetail> {
    const data = await $fetch<TmdbMovieDetail>(`/api/movies/${id}`)
    return data
  }
}

// ----------------------------------------------------
// API Client Functions
// ----------------------------------------------------

export const movieService = {
  async getAll(status?: 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'): Promise<Movie[]> {
    if (USE_MOCK) return mockMovies
    const res = await apiClient.get<BackendMovie[]>('/movies', { params: status ? { status } : undefined })
    return res.data.map(mapBackendMovieToFrontend)
  },

  async getPublic(status?: 'UPCOMING' | 'NOW_SHOWING'): Promise<Movie[]> {
    if (USE_MOCK) return mockMovies
    const res = await apiClient.get<BackendMovie[]>('/movies', {
      params: { public_only: true, ...(status ? { status } : {}) },
    })
    return res.data.map(mapBackendMovieToFrontend)
  },

  async getById(id: string): Promise<Movie> {
    if (USE_MOCK) {
      const m = mockMovies.find(item => item.id === id)
      if (!m) throw new Error('Không tìm thấy phim')
      return m
    }
    const res = await apiClient.get<BackendMovie>(`/movies/${id}`)
    return mapBackendMovieToFrontend(res.data)
  },

  async getShowtimes(movieId: string): Promise<Showtime[]> {
    if (USE_MOCK) {
      return mockShowtimes.filter(s => s.movieId === movieId)
    }
    // Internal showtimes endpoint expects backend UUID movie IDs.
    // TMDB numeric IDs should not be sent to this API.
    const uuidLike = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(movieId)
    if (!uuidLike) {
      return []
    }
    const res = await apiClient.get<BackendShowtime[]>(`/movies/${movieId}/showtimes`)
    return res.data.map(mapBackendShowtimeToFrontend)
  },

  async getSeats(showtimeId: string): Promise<Seat[]> {
    if (USE_MOCK) {
      return generateSeats(showtimeId)
    }
    const res = await apiClient.get<BackendSeat[]>(`/showtimes/${showtimeId}/seats`)
    return res.data.map(mapBackendSeatToFrontend)
  },

  async holdSeats(showtimeId: string, seatIds: string[]): Promise<{ expires_at: string; hold_seconds: number }> {
    const res = await apiClient.post<{ expires_at: string; hold_seconds: number }>(
      `/showtimes/${showtimeId}/holds`,
      { seat_ids: seatIds },
    )
    return res.data
  },

  async releaseSeatHolds(showtimeId: string): Promise<void> {
    await apiClient.delete(`/showtimes/${showtimeId}/holds`)
  },

  watchSeats(showtimeId: string, onUpdate: () => void): WebSocket {
    const apiUrl = new URL(API_BASE_URL)
    const protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
    const token = process.client ? sessionStorage.getItem('cineai_token') || '' : ''
    const socket = new WebSocket(`${protocol}//${apiUrl.host}${apiUrl.pathname}/showtimes/${showtimeId}/ws?token=${encodeURIComponent(token)}`)
    socket.onmessage = () => onUpdate()
    return socket
  },

  async searchSemantically(query: string): Promise<Movie[]> {
    if (USE_MOCK) {
      const q = query.toLowerCase()
      // Fallback keyword matching for mock
      if (q.includes('viễn tưởng') || q.includes('vũ trụ') || q.includes('dune') || q.includes('interstellar')) {
        return mockMovies.filter(m => m.genre.includes('Viễn Tưởng') || m.genre.includes('Cyberpunk'))
      }
      if (q.includes('hành động') || q.includes('john wick')) {
        return mockMovies.filter(m => m.genre.includes('Hành Động'))
      }
      if (q.includes('mới') || q.includes('neon') || q.includes('cyber') || q.includes('neuro')) {
        return mockMovies.filter(m => m.genre.includes('Cyberpunk') || m.genre.includes('Neon-Noir'))
      }
      return mockMovies
    }
    const res = await apiClient.post<BackendMovie[]>('/movies/semantic-search', { query })
    return res.data.map(mapBackendMovieToFrontend)
  },

  async getRecommendations(): Promise<Movie[]> {
    if (USE_MOCK) {
      // Return 3 suggested movies
      return mockMovies.filter(m => m.isFeatured || m.rating >= 4.8)
    }
    const res = await apiClient.get<BackendMovie[]>('/movies/recommendations')
    return res.data.map(mapBackendMovieToFrontend)
  },

  async getFromTmdb(list: TmdbMovieList = 'popular'): Promise<TmdbPopularMovie[]> {
    const data = await $fetch<{ source?: string; results?: any[] }>('/api/movies', {
      query: { list },
    })
    if (data?.source === 'backend') return []
    const results = Array.isArray(data?.results) ? data.results : []
    return results.map((item: any) => ({
      tmdb_id: Number(item.id),
      title: String(item.title || item.name || ''),
      overview: String(item.overview || ''),
      poster_path: item.poster_path ? String(item.poster_path) : null,
      release_date: item.release_date ? String(item.release_date) : null,
      original_title: item.original_title ? String(item.original_title) : null,
      suggested_ticket_price: Number(item.suggested_ticket_price || 90000),
    }))
  },

  async getPopularFromTmdb(): Promise<TmdbPopularMovie[]> {
    return this.getFromTmdb('popular')
  }
}

export const checkoutService = {
  async validatePromotion(code: string, subtotal: number): Promise<{
    promotion_id: string
    code: string
    subtotal: number
    discount_amount: number
    total_amount: number
    message: string
  }> {
    const response = await apiClient.post('/promotions/validate', { code, subtotal })
    return response.data
  },

  async createVnpayPayment(bookingDetails: {
    showtimeId: string
    seats: string[]
    totalAmount: number
    promotionCode?: string
  }): Promise<{ paymentUrl: string; transactionRef: string }> {
    const bookingRes = await apiClient.post<any>('/bookings', {
      showtime_id: bookingDetails.showtimeId,
      seat_ids: bookingDetails.seats,
      quantity: bookingDetails.seats.length,
      total_price: bookingDetails.totalAmount,
    })
    const response = await apiClient.post<any>('/payments/checkout', {
      booking_id: bookingRes.data.id,
      amount: bookingDetails.totalAmount,
      payment_method: 'VNPAY',
      promotion_code: bookingDetails.promotionCode || null,
    })
    return {
      paymentUrl: response.data.payment_url,
      transactionRef: response.data.payment_id,
    }
  },

  async createPaypalPayment(bookingDetails: {
    showtimeId: string
    seats: string[]
    totalAmount: number
    promotionCode?: string
  }): Promise<{ paymentUrl: string; transactionRef: string }> {
    const bookingRes = await apiClient.post<any>('/bookings', {
      showtime_id: bookingDetails.showtimeId,
      seat_ids: bookingDetails.seats,
      quantity: bookingDetails.seats.length,
      total_price: bookingDetails.totalAmount,
    })
    const response = await apiClient.post<any>('/payments/checkout', {
      booking_id: bookingRes.data.id,
      amount: bookingDetails.totalAmount,
      payment_method: 'PAYPAL',
      promotion_code: bookingDetails.promotionCode || null,
    })
    return {
      paymentUrl: response.data.payment_url,
      transactionRef: response.data.payment_id,
    }
  },

  async cancelPendingPayment(paymentId: string): Promise<void> {
    await apiClient.post(`/payments/${paymentId}/cancel`)
  },

  async verifyVnpayCallback(params: Record<string, string | string[]>): Promise<{
    success: boolean
    message: string
    payment_id?: string
    transaction_ref?: string
    payment_status?: string
  }> {
    const response = await apiClient.get('/payments/vnpay/callback', { params })
    return response.data
  },

  async processPayment(bookingDetails: {
    showtimeId: string
    seats: string[]
    seatLabels?: string[]
    movieTitle?: string
    poster?: string
    branchName?: string
    screenName?: string
    date?: string
    time?: string
    paymentMethod: string
    totalAmount: number
    promotionCode?: string
  }): Promise<UserTicket> {
    if (USE_MOCK) {
      const showtime = mockShowtimes.find(s => s.id === bookingDetails.showtimeId)
      const movie = mockMovies.find(m => m.id === showtime?.movieId)

      const newTicket: UserTicket = {
        id: `t-${Math.floor(1000 + Math.random() * 9000)}`,
        movieTitle: movie?.title || 'Phim đã đặt',
        poster: movie?.poster || 'https://images.unsplash.com/photo-1536440136628-849c177e76a1',
        branchName: showtime?.branchName || 'CineAI Hùng Vương',
        screenName: showtime?.screenName || 'Phòng 1',
        date: showtime?.date || '2026-06-25',
        time: showtime?.time || '20:00',
        seats: bookingDetails.seats,
        totalAmount: bookingDetails.totalAmount,
        paymentMethod: bookingDetails.paymentMethod,
        qrCode: `CineAI_E_TICKET_${Date.now()}`,
        bookingDate: new Date().toISOString(),
        status: 'CONFIRMED'
      }

      return newTicket
    }

    const bookingRes = await apiClient.post<any>('/bookings', {
      showtime_id: bookingDetails.showtimeId,
      seat_ids: bookingDetails.seats,
      quantity: bookingDetails.seats.length,
      total_price: bookingDetails.totalAmount,
    })
    const booking = bookingRes.data
    const paymentRes = await apiClient.post<any>('/payments/checkout', {
      booking_id: booking.id,
      amount: bookingDetails.totalAmount,
      payment_method: bookingDetails.paymentMethod,
      promotion_code: bookingDetails.promotionCode || null,
    })
    const payment = paymentRes.data
    if (payment.payment_url && process.client) {
      window.location.assign(payment.payment_url)
      return await new Promise<UserTicket>(() => {})
    }
    return {
      id: booking.id,
      movieTitle: bookingDetails.movieTitle || selectedMovieTitle(booking.movie_id),
      poster: bookingDetails.poster || '/images/movie-placeholder.svg',
      branchName: bookingDetails.branchName || 'CineAI',
      screenName: bookingDetails.screenName || 'Phòng chiếu',
      date: bookingDetails.date || String(booking.booking_date).slice(0, 10),
      time: bookingDetails.time || String(booking.booking_date).slice(11, 16),
      seats: bookingDetails.seatLabels || booking.seats.map((seat: any) => `${seat.row}${seat.number}`),
      totalAmount: Number(payment.total_amount),
      paymentMethod: bookingDetails.paymentMethod,
      qrCode: payment.qr_code || payment.confirmation_number,
      bookingDate: String(booking.booking_date),
      status: booking.status || 'CONFIRMED',
    }
  }
}

function selectedMovieTitle(movieId: string): string {
  return `Vé xem phim ${movieId.slice(0, 8)}`
}

export const aiService = {
  async askChatbot(message: string, context: any = {}): Promise<{ response: string; action?: string; data?: any }> {
    if (USE_MOCK) {
      await new Promise(resolve => setTimeout(resolve, 800)) // simulate latency
      const m = message.toLowerCase()

      if (m.includes('đặt vé') || m.includes('mua vé') || m.includes('chọn ghế')) {
        return {
          response: 'Để đặt vé, bạn hãy truy cập mục **Khám phá AI**, chọn phim yêu thích, chọn suất chiếu, sau đó sơ đồ phòng chiếu thông minh sẽ xuất hiện để bạn chọn ghế ngồi và tiến hành thanh toán nhé!',
          action: 'NAVIGATE_TO_MOVIES'
        }
      }
      if (m.includes('gợi ý') || m.includes('phim nào hay') || m.includes('recommend')) {
        return {
          response: 'Dựa trên sở thích của bạn, tôi đề xuất xem **Thành Phố Vô Hình: 2050** (Cyberpunk viễn tưởng hoành tráng) hoặc **Trí Tuệ Nhân Tạo: Khởi Nguyên** (Viễn tưởng, tâm lý). Bạn có muốn xem lịch chiếu của bộ phim nào không?',
          action: 'SHOW_RECOMMENDATIONS'
        }
      }
      if (m.includes('giá vé') || m.includes('bao nhiêu')) {
        return {
          response: 'Giá vé tại hệ thống rạp CineAI dao động từ **90.000 VNĐ** cho ghế Standard đến **120.000 - 150.000 VNĐ** cho ghế VIP và ghế Couple. Thành viên CineAI cũng được hưởng ưu đãi giảm giá lên tới 20%!'
        }
      }
      if (m.includes('lịch chiếu') || m.includes('hôm nay')) {
        return {
          response: 'Hôm nay chúng tôi có các suất chiếu từ chiều tới tối muộn cho các phim hot như **Thành Phố Vô Hình: 2050**, **Trí Tuệ Nhân Tạo: Khởi Nguyên**, **Vũ Trụ Vô Tận**... Bạn muốn kiểm tra suất chiếu ở chi nhánh Hùng Vương hay Sala Q2?',
          action: 'NAVIGATE_TO_MOVIES'
        }
      }
      return {
        response: 'Xin chào! Tôi là CineAI Assistant 🤖. Tôi có thể giúp bạn gợi ý phim, tra cứu lịch chiếu, hướng dẫn chọn ghế hoặc giải đáp các thắc mắc về dịch vụ. Bạn có câu hỏi nào khác không?'
      }
    }

    const res = await apiClient.post('/chatbot', { message, context })
    return res.data
  },

  async parseVoiceCommand(audioBlob: Blob | string): Promise<{ text: string; parsedAction: string; data?: any }> {
    if (USE_MOCK) {
      await new Promise(resolve => setTimeout(resolve, 1500))
      // Simulating a parsed action from speech-to-text
      const transcripts = [
        "Cho tôi đặt vé phim Thành Phố Vô Hình tối nay ở Sala",
        "Tìm kiếm phim hành động hay nhất",
        "Tôi muốn xem lịch chiếu Trí Tuệ Nhân Tạo",
        "Đặt ghế VIP hàng F"
      ]
      const randomText = transcripts[Math.floor(Math.random() * transcripts.length)]
      let parsedAction = 'UNKNOWN'
      let data: any = {}

      if (randomText.includes('Hình') || randomText.includes('Vô Hình')) {
        parsedAction = 'BOOK_MOVIE'
        data = { movieId: '1', date: '2026-07-11', branchName: 'CineAI Sala Q2' }
      } else if (randomText.includes('hành động')) {
        parsedAction = 'SEARCH_GENRE'
        data = { genre: 'Hành Động' }
      } else if (randomText.includes('Trí Tuệ') || randomText.includes('Nhân Tạo')) {
        parsedAction = 'VIEW_SHOWTIMES'
        data = { movieId: '2' }
      }

      return {
        text: randomText,
        parsedAction,
        data
      }
    }

    const formData = new FormData()
    if (typeof audioBlob === 'string') {
      formData.append('transcript', audioBlob)
    } else {
      formData.append('file', audioBlob)
    }
    const res = await apiClient.post('/voice-booking', formData)
    return res.data
  }
}

export const adminService = {
  async getSuperAdminStats(): Promise<SuperAdminStats> {
    if (USE_MOCK) {
      return {
        totalBranches: 5,
        totalMovies: mockMovies.length,
        totalUsers: 1420,
        totalRevenue: 285900000,
        todayRevenue: 12000000,
        monthRevenue: 285900000,
        ticketsSold: 1200,
        successfulBookings: 900,
        cancelledBookings: 12,
        pendingBookings: 8,
        revenueChartData: [
          { label: 'T12', value: 45000000 },
          { label: 'T01', value: 68000000 },
          { label: 'T02', value: 92000000 },
          { label: 'T03', value: 75000000 },
          { label: 'T04', value: 55000000 },
          { label: 'T05', value: 89000000 },
          { label: 'T06 (Dự kiến)', value: 120000000 }
        ],
        branchPerformance: [],
        topMovies: [],
        moviesList: mockMovies,
        usersList: [
          { id: 'u1', name: 'Nguyễn Văn A', email: 'vana@gmail.com', role: 'customer', isActive: true },
          { id: 'u2', name: 'Trần Thị B', email: 'thib@gmail.com', role: 'customer', isActive: true },
          { id: 'u3', name: 'Đặng Thanh Phong', email: 'phongnd@cineai.vn', role: 'admin', isActive: true },
          { id: 'u4', name: 'Võ Toàn Phú', email: 'phuvt@cineai.vn', role: 'branch-admin', branchId: 'b1', isActive: true }
        ]
      }
    }
    const res = await apiClient.get('/admin/stats')
    return res.data
  },

  async getBranchAdminStats(branchId?: string): Promise<BranchAdminStats> {
    if (USE_MOCK) {
      return {
        branchId: 'b1',
        branchName: 'CineAI Sala Q2',
        ticketsSold: 345,
        activeShowtimes: 8,
        activePromos: 3,
        branchRevenue: 34500000,
        orders: 210,
        seatsSold: 345,
        occupancyRate: 68.5,
        movieCount: 12,
        showtimeCount: 24,
        salesChartData: [
          { label: 'Thứ Hai', tickets: 35 },
          { label: 'Thứ Ba', tickets: 42 },
          { label: 'Thứ Tư', tickets: 55 },
          { label: 'Thứ Năm', tickets: 48 },
          { label: 'Thứ Sáu', tickets: 75 },
          { label: 'Thứ Bảy', tickets: 110 },
          { label: 'Chủ Nhật', tickets: 120 }
        ],
        showtimesList: mockShowtimes
          .filter(s => s.branchName.includes('Sala'))
          .map((showtime, index) => {
            const matchedMovie = mockMovies.find(movie => movie.id === showtime.movieId)
            const startTimeStr = `${showtime.date}T${showtime.time}:00+07:00`

            // Giả lập giờ kết thúc = giờ bắt đầu + 2 tiếng (120 phút)
            const startDate = new Date(startTimeStr)
            const endDate = new Date(startDate.getTime() + 120 * 60 * 1000)
            const endTimeStr = endDate.toISOString()

            return {
              id: String(showtime.id),
              movie_id: String(showtime.movieId),
              movie_title: matchedMovie?.title || 'Phim đã ẩn',
              auditorium_id: `aud-${index + 1}`,
              auditorium_name: showtime.screenName,
              branch_name: showtime.branchName,
              starts_at: startTimeStr,
              ends_at: endTimeStr,
              status: 'OPEN',
              base_price: showtime.price,

              //  BỔ SUNG ĐỦ DỮ LIỆU CHUẨN KHIÊN TYPE AdminShowtime KHÔNG BỊ LỖI
              stored_status: 'OPEN' as const,
              booking_closes_at: startTimeStr,
              cancellation_reason: null,
              booking_count: 15,
              sold_seats: 15,
              revenue: showtime.price * 15,
            }
          }),
        promotionsList: [
          { code: 'AISELECTION', discount: 15, desc: 'Giảm 15% cho phim do AI gợi ý', active: true },
          { code: 'WEEKEND30', discount: 10, desc: 'Giảm 10k/vé dịp cuối tuần', active: true },
          { code: 'STUDENTIMAX', discount: 20, desc: 'Giảm 20% vé IMAX cho học sinh sinh viên', active: false }
        ]
      }
    }

    // Gọi API thật từ Server
    const res = await apiClient.get<any>('/branch-admin/stats', {
      params: branchId ? { branchId } : undefined,
    })

    const rawData = res.data

    return {
      branchId: rawData.branch_id || rawData.branchId || '',
      branchName: rawData.branch_name || rawData.branchName || '',
      ticketsSold: rawData.ticketsSold || 0,
      activeShowtimes: rawData.activeShowtimes || 0,
      activePromos: rawData.activePromos || 0,
      branchRevenue: rawData.branchRevenue || 0,
      orders: rawData.orders || 0,
      seatsSold: rawData.seatsSold || 0,
      occupancyRate: rawData.occupancyRate || 0,
      movieCount: rawData.movieCount || 0,
      showtimeCount: rawData.showtimeCount || 0,
      salesChartData: rawData.salesChartData || [],
      showtimesList: (rawData.showtimesList || []).map((item: any): AdminShowtime => ({
        id: String(item.id),
        movie_id: String(item.movie_id || item.movieId),
        movie_title: item.movie_title || item.movieTitle || 'Phim chưa xác định',
        auditorium_id: String(item.auditorium_id || item.auditoriumId),
        auditorium_name: item.auditorium_name || item.screenName || 'Phòng chiếu',
        branch_name: item.branch_name || item.branchName || '',
        starts_at: item.starts_at || item.startsAt,
        ends_at: item.ends_at || item.endsAt,
        status: item.status || 'OPEN',
        base_price: item.base_price || item.price || 0,

        // Chuẩn hóa dữ liệu fallback phòng trường hợp API thiếu trường
        stored_status: item.stored_status || 'OPEN',
        booking_closes_at: item.booking_closes_at || null,
        cancellation_reason: item.cancellation_reason || null,
        booking_count: item.booking_count || 0,
        sold_seats: item.sold_seats || 0,
        revenue: item.revenue || 0,
      })),
      promotionsList: rawData.promotionsList || [],
    }
  }
}

export interface AiQueryResponse {
  reply: string
  movies: Movie[]
  branches: BackendBranch[]
  showtimes: Showtime[]
}

export const aiDiscoveryService = {
  async query(prompt: string, history: Array<{ role: string; parts: Array<{ text: string }> }>): Promise<AiQueryResponse> {
    const res = await apiClient.post<any>('/ai-discovery/query', { prompt, history })
    const raw = res.data
    return {
      reply: raw.reply || '',
      movies: (raw.movies || []).map(mapBackendMovieToFrontend),
      branches: raw.branches || [],
      showtimes: (raw.showtimes || []).map(mapBackendShowtimeToFrontend),
    }
  }
}


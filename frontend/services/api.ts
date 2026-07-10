import axios from 'axios'

// Set this to false when backend (FastAPI) is running
const USE_MOCK = true
const API_BASE_URL = import.meta.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
}

export interface Showtime {
  id: string
  movieId: string
  branchName: string
  screenName: string
  date: string
  time: string
  price: number
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
}

export interface UserProfile {
  id: string
  name: string
  email: string
  role: 'customer' | 'admin' | 'branch-admin' | 'staff'
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

export interface MovieDraftPayload {
  title: string
  original_title?: string | null
  description?: string | null
  duration_min: number
  release_date?: string | null
  age_rating?: string | null
  language?: string | null
  trailer_url?: string | null
  poster_url?: string | null
  status?: 'UPCOMING' | 'NOW_SHOWING' | 'ENDED'
  genres: string[]
}

export interface MovieRequest {
  id: string
  requested_by_id: string
  target_movie_id: string | null
  request_type: 'CREATE' | 'UPDATE' | 'DELETE'
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  payload: MovieDraftPayload
  review_note: string | null
  reviewed_by_id: string | null
  reviewed_at: string | null
  created_at: string
  requested_by?: UserProfile | null
}

export interface MovieRequestInput {
  request_type: 'CREATE' | 'UPDATE' | 'DELETE'
  target_movie_id?: string | null
  payload: MovieDraftPayload
}

export interface MovieRequestReview {
  review_note?: string | null
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
  phone?: string | null
  full_name: string
  date_of_birth?: string | null
  gender?: string | null
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: BackendUser
}

function mapBackendRoleToFrontend(roleCodes: string[]): UserProfile['role'] {
  if (roleCodes.includes('SUPER_ADMIN')) return 'admin'
  if (roleCodes.includes('BRANCH_ADMIN') || roleCodes.includes('STAFF')) return 'branch-admin'
  return 'customer'
}

export function mapBackendUserToProfile(user: BackendUser, token?: string): UserProfile {
  return {
    id: user.id,
    name: user.full_name,
    email: user.email,
    role: mapBackendRoleToFrontend(user.roles.map(role => role.code)),
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

  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/auth/register', payload)
    return res.data
  },

  async me(): Promise<BackendUser> {
    const res = await apiClient.get<BackendUser>('/auth/me')
    return res.data
  }
}

export const adminBackendService = {
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

  async getMovieRequests(): Promise<MovieRequest[]> {
    const res = await apiClient.get<MovieRequest[]>('/movie-requests/admin')
    return res.data
  },

  async getMyMovieRequests(): Promise<MovieRequest[]> {
    const res = await apiClient.get<MovieRequest[]>('/movie-requests/mine')
    return res.data
  },

  async submitMovieRequest(payload: MovieRequestInput): Promise<MovieRequest> {
    const res = await apiClient.post<MovieRequest>('/movie-requests', payload)
    return res.data
  },

  async approveMovieRequest(requestId: string, review_note?: string | null): Promise<MovieRequest> {
    const res = await apiClient.post<MovieRequest>(`/movie-requests/admin/${requestId}/approve`, {
      review_note: review_note || null,
    })
    return res.data
  },

  async rejectMovieRequest(requestId: string, review_note?: string | null): Promise<MovieRequest> {
    const res = await apiClient.post<MovieRequest>(`/movie-requests/admin/${requestId}/reject`, {
      review_note: review_note || null,
    })
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
    bookingDate: '2026-06-19 12:44'
  }
]

// ----------------------------------------------------
// API Client Functions
// ----------------------------------------------------

export const movieService = {
  async getAll(): Promise<Movie[]> {
    if (USE_MOCK) return mockMovies
    const res = await apiClient.get<Movie[]>('/movies')
    return res.data
  },

  async getById(id: string): Promise<Movie> {
    if (USE_MOCK) {
      const m = mockMovies.find(item => item.id === id)
      if (!m) throw new Error('Không tìm thấy phim')
      return m
    }
    const res = await apiClient.get<Movie>(`/movies/${id}`)
    return res.data
  },

  async getShowtimes(movieId: string): Promise<Showtime[]> {
    if (USE_MOCK) {
      return mockShowtimes.filter(s => s.movieId === movieId)
    }
    const res = await apiClient.get<Showtime[]>(`/movies/${movieId}/showtimes`)
    return res.data
  },

  async getSeats(showtimeId: string): Promise<Seat[]> {
    if (USE_MOCK) {
      return generateSeats(showtimeId)
    }
    const res = await apiClient.get<Seat[]>(`/showtimes/${showtimeId}/seats`)
    return res.data
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
    const res = await apiClient.post<Movie[]>('/movies/semantic-search', { query })
    return res.data
  },

  async getRecommendations(): Promise<Movie[]> {
    if (USE_MOCK) {
      // Return 3 suggested movies
      return mockMovies.filter(m => m.isFeatured || m.rating >= 4.8)
    }
    const res = await apiClient.get<Movie[]>('/movies/recommendations')
    return res.data
  }
}

export const checkoutService = {
  async processPayment(bookingDetails: {
    showtimeId: string
    seats: string[]
    paymentMethod: string
    totalAmount: number
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
        bookingDate: new Date().toISOString().replace('T', ' ').substring(0, 16)
      }
      
      return newTicket
    }
    
    const res = await apiClient.post<UserTicket>('/checkout/booking', bookingDetails)
    return res.data
  }
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
  async getSuperAdminStats(): Promise<{
    totalBranches: number
    totalMovies: number
    totalUsers: number
    totalRevenue: number
    revenueChartData: { label: string; value: number }[]
    moviesList: Movie[]
    usersList: UserProfile[]
  }> {
    if (USE_MOCK) {
      return {
        totalBranches: 5,
        totalMovies: mockMovies.length,
        totalUsers: 1420,
        totalRevenue: 285900000,
        revenueChartData: [
          { label: 'T12', value: 45000000 },
          { label: 'T01', value: 68000000 },
          { label: 'T02', value: 92000000 },
          { label: 'T03', value: 75000000 },
          { label: 'T04', value: 55000000 },
          { label: 'T05', value: 89000000 },
          { label: 'T06 (Dự kiến)', value: 120000000 }
        ],
        moviesList: mockMovies,
        usersList: [
          { id: 'u1', name: 'Nguyễn Văn A', email: 'vana@gmail.com', role: 'customer' },
          { id: 'u2', name: 'Trần Thị B', email: 'thib@gmail.com', role: 'customer' },
          { id: 'u3', name: 'Đặng Thanh Phong', email: 'phongnd@cineai.vn', role: 'admin' },
          { id: 'u4', name: 'Võ Toàn Phú', email: 'phuvt@cineai.vn', role: 'branch-admin', branchId: 'b1' }
        ]
      }
    }
    const res = await apiClient.get('/admin/stats')
    return res.data
  },

  async getBranchAdminStats(branchId: string): Promise<{
    ticketsSold: number
    activeShowtimes: number
    activePromos: number
    branchRevenue: number
    salesChartData: { label: string; tickets: number }[]
    showtimesList: Showtime[]
    promotionsList: { code: string; discount: number; desc: string; active: boolean }[]
  }> {
    if (USE_MOCK) {
      return {
        ticketsSold: 345,
        activeShowtimes: 8,
        activePromos: 3,
        branchRevenue: 34500000,
        salesChartData: [
          { label: 'Thứ Hai', tickets: 35 },
          { label: 'Thứ Ba', tickets: 42 },
          { label: 'Thứ Tư', tickets: 55 },
          { label: 'Thứ Năm', tickets: 48 },
          { label: 'Thứ Sáu', tickets: 75 },
          { label: 'Thứ Bảy', tickets: 110 },
          { label: 'Chủ Nhật', tickets: 120 }
        ],
        showtimesList: mockShowtimes.filter(s => s.branchName.includes('Sala')),
        promotionsList: [
          { code: 'AISELECTION', discount: 15, desc: 'Giảm 15% cho phim do AI gợi ý', active: true },
          { code: 'WEEKEND30', discount: 10, desc: 'Giảm 10k/vé dịp cuối tuần', active: true },
          { code: 'STUDENTIMAX', discount: 20, desc: 'Giảm 20% vé IMAX cho học sinh sinh viên', active: false }
        ]
      }
    }
    const res = await apiClient.get(`/branch-admin/stats?branchId=${branchId}`)
    return res.data
  }
}

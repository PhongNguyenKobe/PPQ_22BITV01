import axios from 'axios'

// Set this to false when backend (FastAPI) is running
const USE_MOCK = true
const API_BASE_URL = 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
  role: 'customer' | 'admin' | 'branch-admin'
  branchId?: string
}

// ----------------------------------------------------
// Mock Data Layer
// ----------------------------------------------------

export const mockMovies: Movie[] = [
  {
    id: '1',
    title: 'Dune: Part Two',
    rating: 4.9,
    genre: ['Viễn Tưởng', 'Hành Động', 'Kịch Tính'],
    format: ['IMAX', '2D', '4DX'],
    poster: 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1925&auto=format&fit=crop',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Paul Atreides hợp lực với Chani và người Fremen khi đang tìm cách trả thù những kẻ âm mưu hủy hoại gia đình mình. Đối mặt với sự lựa chọn giữa tình yêu của đời mình và số phận của vũ trụ được biết đến, anh cố gắng ngăn chặn một tương lai khủng khiếp mà chỉ anh mới có thể thấy trước.',
    duration: 166,
    releaseDate: '2024-03-01',
    director: 'Denis Villeneuve',
    cast: ['Timothée Chalamet', 'Zendaya', 'Rebecca Ferguson', 'Austin Butler'],
    isFeatured: true,
    aiMatchReason: 'Được gợi ý dựa trên sở thích xem phim sử thi viễn tưởng của bạn.'
  },
  {
    id: '2',
    title: 'John Wick: Chapter 4',
    rating: 4.8,
    genre: ['Hành Động', 'Kịch Tính'],
    format: ['2D', '4DX', 'IMAX'],
    poster: 'https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070&auto=format&fit=crop',
    trailer: 'https://www.youtube.com/embed/qEVUtrk8_B4',
    description: 'John Wick tìm ra con đường để đánh bại High Table. Nhưng trước khi giành lại tự do, Wick phải đối mặt với một kẻ thù mới sở hữu liên minh hùng mạnh trên toàn cầu và những thế lực biến những người bạn cũ thành kẻ thù.',
    duration: 169,
    releaseDate: '2023-03-24',
    director: 'Chad Stahelski',
    cast: ['Keanu Reeves', 'Donnie Yen', 'Bill Skarsgård', 'Laurence Fishburne'],
    isFeatured: true,
    aiMatchReason: 'Bạn đã xem các phần trước của John Wick. AI đề xuất suất chiếu lúc 20:15 có tỷ lệ ghế đẹp cao.'
  },
  {
    id: '3',
    title: 'Interstellar (Re-release)',
    rating: 5.0,
    genre: ['Viễn Tưởng', 'Tâm Lý'],
    format: ['IMAX', '2D'],
    poster: 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=2070&auto=format&fit=crop',
    trailer: 'https://www.youtube.com/embed/zSWdZVtXT7E',
    description: 'Trong tương lai, Trái Đất dần trở nên không thể sinh sống được. Một nhóm nhà thám hiểm không gian du hành qua một hố đen vũ trụ để tìm kiếm một hành tinh mới có thể duy trì sự sống cho nhân loại.',
    duration: 169,
    releaseDate: '2014-11-07',
    director: 'Christopher Nolan',
    cast: ['Matthew McConaughey', 'Anne Hathaway', 'Jessica Chastain', 'Michael Caine'],
    isFeatured: false,
    aiMatchReason: 'Trùng khớp 98% với gu điện ảnh triết lý, du hành vũ trụ của bạn.'
  },
  {
    id: '4',
    title: 'Techno-Dystopia: Final Signal',
    rating: 4.7,
    genre: ['Cyberpunk', 'Viễn Tưởng', 'Neon-Noir'],
    format: ['2D', '3D'],
    poster: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=2000&auto=format&fit=crop',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Trong một siêu đô thị Neon bị tàn phá bởi sự kiểm soát của siêu AI Cyberdyne, một thám tử tư phát hiện ra tín hiệu radio cuối cùng từ quá khứ có thể lật đổ toàn bộ trật tự thế giới ảo.',
    duration: 124,
    releaseDate: '2026-02-15',
    director: 'Kenji Sato',
    cast: ['René Takahashi', 'Marcus Vance', 'Sofia Chen'],
    isFeatured: false,
    aiMatchReason: 'Bộ phim khoa học viễn tưởng mới ra mắt, phù hợp với sở thích phim đen tối tương lai.'
  },
  {
    id: '5',
    title: 'Mạng Lưới Thần Kinh (Neural Net)',
    rating: 4.5,
    genre: ['Cyberpunk', 'Kịch Tính'],
    format: ['2D'],
    poster: 'https://images.unsplash.com/photo-1544256718-3bcf237f3974?q=80&w=2071&auto=format&fit=crop',
    trailer: 'https://www.youtube.com/embed/Way9Dexny3w',
    description: 'Một kỹ sư phần mềm trẻ vô tình kết nối bộ não của mình với mạng thần kinh AI toàn cầu và phát hiện ra một sự thật kinh hoàng về ý thức ảo ẩn sâu dưới các máy chủ đám mây.',
    duration: 118,
    releaseDate: '2026-05-10',
    director: 'Sarah Lin',
    cast: ['Andy Wu', 'Clara Smith', 'David Miller'],
    isFeatured: false,
    aiMatchReason: 'Có lượng đánh giá tích cực rất cao từ những người dùng có gu giống bạn.'
  }
]

export const mockShowtimes: Showtime[] = [
  // Dune
  { id: 's1', movieId: '1', branchName: 'CineAI Hùng Vương', screenName: 'IMAX Phòng 1', date: '2026-06-25', time: '18:00', price: 150000 },
  { id: 's2', movieId: '1', branchName: 'CineAI Hùng Vương', screenName: 'Phòng 3 (2D)', date: '2026-06-25', time: '20:30', price: 90000 },
  { id: 's3', movieId: '1', branchName: 'CineAI Sala Q2', screenName: 'IMAX Phòng A', date: '2026-06-25', time: '19:00', price: 160000 },
  { id: 's4', movieId: '1', branchName: 'CineAI Sala Q2', screenName: 'Phòng B (4DX)', date: '2026-06-26', time: '21:15', price: 180000 },
  // John Wick
  { id: 's5', movieId: '2', branchName: 'CineAI Hùng Vương', screenName: 'Phòng 2 (2D)', date: '2026-06-25', time: '19:30', price: 90000 },
  { id: 's6', movieId: '2', branchName: 'CineAI Nguyễn Du', screenName: 'Phòng 1 (4DX)', date: '2026-06-25', time: '20:15', price: 170000 },
  { id: 's7', movieId: '2', branchName: 'CineAI Sala Q2', screenName: 'Phòng C (2D)', date: '2026-06-26', time: '18:00', price: 100000 },
  // Interstellar
  { id: 's8', movieId: '3', branchName: 'CineAI Sala Q2', screenName: 'IMAX Phòng A', date: '2026-06-25', time: '15:30', price: 160000 },
  { id: 's9', movieId: '3', branchName: 'CineAI Nguyễn Du', screenName: 'Phòng 2 (2D)', date: '2026-06-26', time: '19:45', price: 95000 },
  // Techno-Dystopia
  { id: 's10', movieId: '4', branchName: 'CineAI Sala Q2', screenName: 'Phòng D (3D)', date: '2026-06-25', time: '21:00', price: 120000 },
  // Neural Net
  { id: 's11', movieId: '5', branchName: 'CineAI Hùng Vương', screenName: 'Phòng 4 (2D)', date: '2026-06-25', time: '22:00', price: 90000 }
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
          response: 'Để đặt vé, bạn hãy truy cập mục **Phim**, chọn phim yêu thích, chọn suất chiếu, sau đó sơ đồ phòng chiếu thông minh sẽ xuất hiện để bạn chọn ghế ngồi và tiến hành thanh toán nhé!',
          action: 'NAVIGATE_TO_MOVIES'
        }
      }
      if (m.includes('gợi ý') || m.includes('phim nào hay') || m.includes('recommend')) {
        return {
          response: 'Dựa trên sở thích của bạn, tôi đề xuất xem **Dune: Part Two** (Khoa học viễn tưởng hoành tráng) hoặc **John Wick: Chapter 4** (Hành động kịch tính nghẹt thở). Bạn có muốn xem lịch chiếu của bộ phim nào không?',
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
          response: 'Hôm nay chúng tôi có các suất chiếu từ chiều tới tối muộn cho các phim hot như **Dune: Part Two**, **John Wick 4**, **Interstellar**... Bạn muốn kiểm tra suất chiếu ở chi nhánh Hùng Vương hay Sala Q2?',
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
        "Cho tôi đặt vé phim Dune tối nay ở Sala",
        "Tìm kiếm phim hành động hay nhất",
        "Tôi muốn xem lịch chiếu John Wick",
        "Đặt ghế VIP hàng F"
      ]
      const randomText = transcripts[Math.floor(Math.random() * transcripts.length)]
      let parsedAction = 'UNKNOWN'
      let data: any = {}

      if (randomText.includes('Dune')) {
        parsedAction = 'BOOK_MOVIE'
        data = { movieId: '1', date: '2026-06-25', branchName: 'CineAI Sala Q2' }
      } else if (randomText.includes('hành động')) {
        parsedAction = 'SEARCH_GENRE'
        data = { genre: 'Hành Động' }
      } else if (randomText.includes('John Wick')) {
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

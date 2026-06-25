import axios from 'axios';

const API_BASE_URL = "http://localhost:8000/api";
axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
});
const mockMovies = [
  {
    id: "1",
    title: "Dune: Part Two",
    rating: 4.9,
    genre: ["Vi\u1EC5n T\u01B0\u1EDFng", "H\xE0nh \u0110\u1ED9ng", "K\u1ECBch T\xEDnh"],
    format: ["IMAX", "2D", "4DX"],
    poster: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1925&auto=format&fit=crop",
    trailer: "https://www.youtube.com/embed/Way9Dexny3w",
    description: "Paul Atreides h\u1EE3p l\u1EF1c v\u1EDBi Chani v\xE0 ng\u01B0\u1EDDi Fremen khi \u0111ang t\xECm c\xE1ch tr\u1EA3 th\xF9 nh\u1EEFng k\u1EBB \xE2m m\u01B0u h\u1EE7y ho\u1EA1i gia \u0111\xECnh m\xECnh. \u0110\u1ED1i m\u1EB7t v\u1EDBi s\u1EF1 l\u1EF1a ch\u1ECDn gi\u1EEFa t\xECnh y\xEAu c\u1EE7a \u0111\u1EDDi m\xECnh v\xE0 s\u1ED1 ph\u1EADn c\u1EE7a v\u0169 tr\u1EE5 \u0111\u01B0\u1EE3c bi\u1EBFt \u0111\u1EBFn, anh c\u1ED1 g\u1EAFng ng\u0103n ch\u1EB7n m\u1ED9t t\u01B0\u01A1ng lai kh\u1EE7ng khi\u1EBFp m\xE0 ch\u1EC9 anh m\u1EDBi c\xF3 th\u1EC3 th\u1EA5y tr\u01B0\u1EDBc.",
    duration: 166,
    releaseDate: "2024-03-01",
    director: "Denis Villeneuve",
    cast: ["Timoth\xE9e Chalamet", "Zendaya", "Rebecca Ferguson", "Austin Butler"],
    isFeatured: true,
    aiMatchReason: "\u0110\u01B0\u1EE3c g\u1EE3i \xFD d\u1EF1a tr\xEAn s\u1EDF th\xEDch xem phim s\u1EED thi vi\u1EC5n t\u01B0\u1EDFng c\u1EE7a b\u1EA1n."
  },
  {
    id: "2",
    title: "John Wick: Chapter 4",
    rating: 4.8,
    genre: ["H\xE0nh \u0110\u1ED9ng", "K\u1ECBch T\xEDnh"],
    format: ["2D", "4DX", "IMAX"],
    poster: "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070&auto=format&fit=crop",
    trailer: "https://www.youtube.com/embed/qEVUtrk8_B4",
    description: "John Wick t\xECm ra con \u0111\u01B0\u1EDDng \u0111\u1EC3 \u0111\xE1nh b\u1EA1i High Table. Nh\u01B0ng tr\u01B0\u1EDBc khi gi\xE0nh l\u1EA1i t\u1EF1 do, Wick ph\u1EA3i \u0111\u1ED1i m\u1EB7t v\u1EDBi m\u1ED9t k\u1EBB th\xF9 m\u1EDBi s\u1EDF h\u1EEFu li\xEAn minh h\xF9ng m\u1EA1nh tr\xEAn to\xE0n c\u1EA7u v\xE0 nh\u1EEFng th\u1EBF l\u1EF1c bi\u1EBFn nh\u1EEFng ng\u01B0\u1EDDi b\u1EA1n c\u0169 th\xE0nh k\u1EBB th\xF9.",
    duration: 169,
    releaseDate: "2023-03-24",
    director: "Chad Stahelski",
    cast: ["Keanu Reeves", "Donnie Yen", "Bill Skarsg\xE5rd", "Laurence Fishburne"],
    isFeatured: true,
    aiMatchReason: "B\u1EA1n \u0111\xE3 xem c\xE1c ph\u1EA7n tr\u01B0\u1EDBc c\u1EE7a John Wick. AI \u0111\u1EC1 xu\u1EA5t su\u1EA5t chi\u1EBFu l\xFAc 20:15 c\xF3 t\u1EF7 l\u1EC7 gh\u1EBF \u0111\u1EB9p cao."
  },
  {
    id: "3",
    title: "Interstellar (Re-release)",
    rating: 5,
    genre: ["Vi\u1EC5n T\u01B0\u1EDFng", "T\xE2m L\xFD"],
    format: ["IMAX", "2D"],
    poster: "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=2070&auto=format&fit=crop",
    trailer: "https://www.youtube.com/embed/zSWdZVtXT7E",
    description: "Trong t\u01B0\u01A1ng lai, Tr\xE1i \u0110\u1EA5t d\u1EA7n tr\u1EDF n\xEAn kh\xF4ng th\u1EC3 sinh s\u1ED1ng \u0111\u01B0\u1EE3c. M\u1ED9t nh\xF3m nh\xE0 th\xE1m hi\u1EC3m kh\xF4ng gian du h\xE0nh qua m\u1ED9t h\u1ED1 \u0111en v\u0169 tr\u1EE5 \u0111\u1EC3 t\xECm ki\u1EBFm m\u1ED9t h\xE0nh tinh m\u1EDBi c\xF3 th\u1EC3 duy tr\xEC s\u1EF1 s\u1ED1ng cho nh\xE2n lo\u1EA1i.",
    duration: 169,
    releaseDate: "2014-11-07",
    director: "Christopher Nolan",
    cast: ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine"],
    isFeatured: false,
    aiMatchReason: "Tr\xF9ng kh\u1EDBp 98% v\u1EDBi gu \u0111i\u1EC7n \u1EA3nh tri\u1EBFt l\xFD, du h\xE0nh v\u0169 tr\u1EE5 c\u1EE7a b\u1EA1n."
  },
  {
    id: "4",
    title: "Techno-Dystopia: Final Signal",
    rating: 4.7,
    genre: ["Cyberpunk", "Vi\u1EC5n T\u01B0\u1EDFng", "Neon-Noir"],
    format: ["2D", "3D"],
    poster: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=2000&auto=format&fit=crop",
    trailer: "https://www.youtube.com/embed/Way9Dexny3w",
    description: "Trong m\u1ED9t si\xEAu \u0111\xF4 th\u1ECB Neon b\u1ECB t\xE0n ph\xE1 b\u1EDFi s\u1EF1 ki\u1EC3m so\xE1t c\u1EE7a si\xEAu AI Cyberdyne, m\u1ED9t th\xE1m t\u1EED t\u01B0 ph\xE1t hi\u1EC7n ra t\xEDn hi\u1EC7u radio cu\u1ED1i c\xF9ng t\u1EEB qu\xE1 kh\u1EE9 c\xF3 th\u1EC3 l\u1EADt \u0111\u1ED5 to\xE0n b\u1ED9 tr\u1EADt t\u1EF1 th\u1EBF gi\u1EDBi \u1EA3o.",
    duration: 124,
    releaseDate: "2026-02-15",
    director: "Kenji Sato",
    cast: ["Ren\xE9 Takahashi", "Marcus Vance", "Sofia Chen"],
    isFeatured: false,
    aiMatchReason: "B\u1ED9 phim khoa h\u1ECDc vi\u1EC5n t\u01B0\u1EDFng m\u1EDBi ra m\u1EAFt, ph\xF9 h\u1EE3p v\u1EDBi s\u1EDF th\xEDch phim \u0111en t\u1ED1i t\u01B0\u01A1ng lai."
  },
  {
    id: "5",
    title: "M\u1EA1ng L\u01B0\u1EDBi Th\u1EA7n Kinh (Neural Net)",
    rating: 4.5,
    genre: ["Cyberpunk", "K\u1ECBch T\xEDnh"],
    format: ["2D"],
    poster: "https://images.unsplash.com/photo-1544256718-3bcf237f3974?q=80&w=2071&auto=format&fit=crop",
    trailer: "https://www.youtube.com/embed/Way9Dexny3w",
    description: "M\u1ED9t k\u1EF9 s\u01B0 ph\u1EA7n m\u1EC1m tr\u1EBB v\xF4 t\xECnh k\u1EBFt n\u1ED1i b\u1ED9 n\xE3o c\u1EE7a m\xECnh v\u1EDBi m\u1EA1ng th\u1EA7n kinh AI to\xE0n c\u1EA7u v\xE0 ph\xE1t hi\u1EC7n ra m\u1ED9t s\u1EF1 th\u1EADt kinh ho\xE0ng v\u1EC1 \xFD th\u1EE9c \u1EA3o \u1EA9n s\xE2u d\u01B0\u1EDBi c\xE1c m\xE1y ch\u1EE7 \u0111\xE1m m\xE2y.",
    duration: 118,
    releaseDate: "2026-05-10",
    director: "Sarah Lin",
    cast: ["Andy Wu", "Clara Smith", "David Miller"],
    isFeatured: false,
    aiMatchReason: "C\xF3 l\u01B0\u1EE3ng \u0111\xE1nh gi\xE1 t\xEDch c\u1EF1c r\u1EA5t cao t\u1EEB nh\u1EEFng ng\u01B0\u1EDDi d\xF9ng c\xF3 gu gi\u1ED1ng b\u1EA1n."
  }
];
const mockShowtimes = [
  // Dune
  { id: "s1", movieId: "1", branchName: "CineAI H\xF9ng V\u01B0\u01A1ng", screenName: "IMAX Ph\xF2ng 1", date: "2026-06-25", time: "18:00", price: 15e4 },
  { id: "s2", movieId: "1", branchName: "CineAI H\xF9ng V\u01B0\u01A1ng", screenName: "Ph\xF2ng 3 (2D)", date: "2026-06-25", time: "20:30", price: 9e4 },
  { id: "s3", movieId: "1", branchName: "CineAI Sala Q2", screenName: "IMAX Ph\xF2ng A", date: "2026-06-25", time: "19:00", price: 16e4 },
  { id: "s4", movieId: "1", branchName: "CineAI Sala Q2", screenName: "Ph\xF2ng B (4DX)", date: "2026-06-26", time: "21:15", price: 18e4 },
  // John Wick
  { id: "s5", movieId: "2", branchName: "CineAI H\xF9ng V\u01B0\u01A1ng", screenName: "Ph\xF2ng 2 (2D)", date: "2026-06-25", time: "19:30", price: 9e4 },
  { id: "s6", movieId: "2", branchName: "CineAI Nguy\u1EC5n Du", screenName: "Ph\xF2ng 1 (4DX)", date: "2026-06-25", time: "20:15", price: 17e4 },
  { id: "s7", movieId: "2", branchName: "CineAI Sala Q2", screenName: "Ph\xF2ng C (2D)", date: "2026-06-26", time: "18:00", price: 1e5 },
  // Interstellar
  { id: "s8", movieId: "3", branchName: "CineAI Sala Q2", screenName: "IMAX Ph\xF2ng A", date: "2026-06-25", time: "15:30", price: 16e4 },
  { id: "s9", movieId: "3", branchName: "CineAI Nguy\u1EC5n Du", screenName: "Ph\xF2ng 2 (2D)", date: "2026-06-26", time: "19:45", price: 95e3 },
  // Techno-Dystopia
  { id: "s10", movieId: "4", branchName: "CineAI Sala Q2", screenName: "Ph\xF2ng D (3D)", date: "2026-06-25", time: "21:00", price: 12e4 },
  // Neural Net
  { id: "s11", movieId: "5", branchName: "CineAI H\xF9ng V\u01B0\u01A1ng", screenName: "Ph\xF2ng 4 (2D)", date: "2026-06-25", time: "22:00", price: 9e4 }
];
const generateSeats = (showtimeId) => {
  const seats = [];
  const rows = ["A", "B", "C", "D", "E", "F", "G", "H", "J"];
  rows.forEach((row, rowIndex) => {
    for (let i = 1; i <= 10; i++) {
      const id = `${showtimeId}_${row}${i}`;
      let type = "standard";
      let priceMultiplier = 1;
      if (row === "E" || row === "F" || row === "G") {
        type = "vip";
        priceMultiplier = 1.3;
      } else if (row === "J") {
        type = "couple";
        priceMultiplier = 1.5;
      }
      const statusSeed = Math.random();
      let status = "available";
      if (statusSeed < 0.25) {
        status = "occupied";
      }
      seats.push({
        id,
        row,
        number: i,
        type,
        status,
        price: Math.round(9e4 * priceMultiplier / 1e3) * 1e3
      });
    }
  });
  return seats;
};
const mockTickets = [
  {
    id: "t-9831",
    movieTitle: "Interstellar (Re-release)",
    poster: "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=2070&auto=format&fit=crop",
    branchName: "CineAI Sala Q2",
    screenName: "IMAX Ph\xF2ng A",
    date: "2026-06-20",
    time: "15:30",
    seats: ["F5", "F6"],
    totalAmount: 416e3,
    paymentMethod: "V\xED Momo",
    qrCode: "CineAI_E_TICKET_MOCK_QR_CODE_1",
    bookingDate: "2026-06-19 12:44"
  }
];
const movieService = {
  async getAll() {
    return mockMovies;
  },
  async getById(id) {
    {
      const m = mockMovies.find((item) => item.id === id);
      if (!m) throw new Error("Kh\xF4ng t\xECm th\u1EA5y phim");
      return m;
    }
  },
  async getShowtimes(movieId) {
    {
      return mockShowtimes.filter((s) => s.movieId === movieId);
    }
  },
  async getSeats(showtimeId) {
    {
      return generateSeats(showtimeId);
    }
  },
  async searchSemantically(query) {
    {
      const q = query.toLowerCase();
      if (q.includes("vi\u1EC5n t\u01B0\u1EDFng") || q.includes("v\u0169 tr\u1EE5") || q.includes("dune") || q.includes("interstellar")) {
        return mockMovies.filter((m) => m.genre.includes("Vi\u1EC5n T\u01B0\u1EDFng") || m.genre.includes("Cyberpunk"));
      }
      if (q.includes("h\xE0nh \u0111\u1ED9ng") || q.includes("john wick")) {
        return mockMovies.filter((m) => m.genre.includes("H\xE0nh \u0110\u1ED9ng"));
      }
      if (q.includes("m\u1EDBi") || q.includes("neon") || q.includes("cyber") || q.includes("neuro")) {
        return mockMovies.filter((m) => m.genre.includes("Cyberpunk") || m.genre.includes("Neon-Noir"));
      }
      return mockMovies;
    }
  },
  async getRecommendations() {
    {
      return mockMovies.filter((m) => m.isFeatured || m.rating >= 4.8);
    }
  }
};
const checkoutService = {
  async processPayment(bookingDetails) {
    {
      const showtime = mockShowtimes.find((s) => s.id === bookingDetails.showtimeId);
      const movie = mockMovies.find((m) => m.id === (showtime == null ? void 0 : showtime.movieId));
      const newTicket = {
        id: `t-${Math.floor(1e3 + Math.random() * 9e3)}`,
        movieTitle: (movie == null ? void 0 : movie.title) || "Phim \u0111\xE3 \u0111\u1EB7t",
        poster: (movie == null ? void 0 : movie.poster) || "https://images.unsplash.com/photo-1536440136628-849c177e76a1",
        branchName: (showtime == null ? void 0 : showtime.branchName) || "CineAI H\xF9ng V\u01B0\u01A1ng",
        screenName: (showtime == null ? void 0 : showtime.screenName) || "Ph\xF2ng 1",
        date: (showtime == null ? void 0 : showtime.date) || "2026-06-25",
        time: (showtime == null ? void 0 : showtime.time) || "20:00",
        seats: bookingDetails.seats,
        totalAmount: bookingDetails.totalAmount,
        paymentMethod: bookingDetails.paymentMethod,
        qrCode: `CineAI_E_TICKET_${Date.now()}`,
        bookingDate: (/* @__PURE__ */ new Date()).toISOString().replace("T", " ").substring(0, 16)
      };
      return newTicket;
    }
  }
};

export { mockMovies as a, movieService as b, checkoutService as c, mockTickets as m };
//# sourceMappingURL=api-rwjTvGO1.mjs.map

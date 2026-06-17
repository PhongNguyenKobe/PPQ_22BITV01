<script setup lang="ts">
import ProductList from './components/ProductList.vue'

type MovieCard = {
  title: string
  rating: string
  format: string
  image: string
  label: string
  featured?: boolean
}

type FeatureCard = {
  icon: string
  title: string
  description: string
  accent?: boolean
}

const movieCards: MovieCard[] = [
  {
    title: 'Dune: Part Two',
    rating: '4.8',
    format: 'IMAX',
    label: 'Đặt chỗ',
    image: 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1925&auto=format&fit=crop',
  },
  {
    title: 'John Wick: Chapter 4',
    rating: '4.9',
    format: '4DX',
    label: 'Đặt chỗ',
    image: 'https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070&auto=format&fit=crop',
  },
  {
    title: 'The Batman',
    rating: '4.5',
    format: '2D',
    label: 'Đặt chỗ',
    image: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=1980&auto=format&fit=crop',
  },
  {
    title: 'Interstellar Re-release',
    rating: '5.0',
    format: 'AI Choice',
    label: 'Đặt chỗ',
    featured: true,
    image: 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=2070&auto=format&fit=crop',
  },
]

const featureCards: FeatureCard[] = [
  {
    icon: 'chair',
    title: 'Đặt vé trực tuyến',
    description: 'Chọn chỗ ngồi theo thời gian thực tại mọi cụm rạp trên toàn quốc với độ chính xác tuyệt đối.',
  },
  {
    icon: 'smart_toy',
    title: 'Trợ lý AI Chatbot',
    description: 'Tìm phim bằng ngôn ngữ tự nhiên, nhận đề xuất cá nhân hóa dựa trên sở thích của bạn.',
    accent: true,
  },
  {
    icon: 'payments',
    title: 'Thanh toán đa kênh',
    description: 'Hỗ trợ thanh toán nhanh chóng qua Momo, VNPAY, thẻ tín dụng hoặc quét mã QR an toàn.',
  },
  {
    icon: 'qr_code',
    title: 'Quản lý vé điện tử',
    description: 'Lưu trữ vé thông minh, quét mã QR tại rạp không cần in giấy, thân thiện với môi trường.',
  },
]

const chatQuickReplies = ['19:30', '20:15', '21:00']
</script>

<template>
  <div class="page-shell">
    <nav class="topbar">
      <div class="topbar__brand-wrap">
        <a class="brand" href="#hero">CineAI</a>
        <div class="topbar__links">
          <a class="topbar__link topbar__link--active" href="#movies">Phim nổi bật</a>
          <a class="topbar__link" href="#ai">AI Discovery</a>
          <a class="topbar__link" href="#showtimes">Showtimes</a>
          <a class="topbar__link" href="#theaters">Theaters</a>
        </div>
      </div>

      <div class="topbar__actions">
        <button class="icon-button" aria-label="Search">
          <span class="material-symbols-outlined">search</span>
        </button>
        <button class="button button--solid">Sign In</button>
      </div>
    </nav>

    <header id="hero" class="hero">
      <div class="hero__backdrop">
        <div class="hero__image"></div>
        <div class="hero__overlay"></div>
        <div class="hero__fade"></div>
        <div class="hero__rays"></div>
        <div class="hero__orbs">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <div class="container hero__content">
        <div class="hero__copy">
          <p class="eyebrow">Đặt vé xem phim thông minh với AI</p>
          <h1>
            Trải nghiệm tương lai của điện ảnh với
            <span>AI</span>
          </h1>
          <p class="lead">
            Tìm kiếm, khám phá và đặt vé chỉ trong vài giây với trợ lý AI thông minh của CineAI.
          </p>
          <div class="hero__actions">
            <button class="button button--primary">
              Đặt vé ngay
              <span class="material-symbols-outlined">arrow_forward</span>
            </button>
            <button class="button button--ghost">
              <span class="material-symbols-outlined">smart_toy</span>
              Trải nghiệm trợ lý AI
            </button>
          </div>

          <div class="hero__stats">
            <div>
              <strong>120+</strong>
              <span>suất chiếu AI gợi ý mỗi ngày</span>
            </div>
            <div>
              <strong>30s</strong>
              <span>từ tìm phim đến đặt vé</span>
            </div>
            <div>
              <strong>4.9/5</strong>
              <span>trải nghiệm cá nhân hóa</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main>
      <section id="movies" class="section section--movies container">
        <div class="section__heading">
          <h2>Phim đang chiếu</h2>
          <a class="section__more" href="#movies">
            Xem tất cả <span class="material-symbols-outlined">chevron_right</span>
          </a>
        </div>

        <div class="movie-grid">
          <article
            v-for="movie in movieCards"
            :key="movie.title"
            class="movie-card"
            :class="{ 'movie-card--featured': movie.featured }"
          >
            <div class="movie-card__poster">
              <img :src="movie.image" :alt="movie.title" />
              <div class="movie-card__fade"></div>
              <span class="movie-card__badge">
                <span v-if="movie.featured" class="material-symbols-outlined">auto_awesome</span>
                {{ movie.format }}
              </span>
            </div>

            <div class="movie-card__content">
              <div class="movie-card__rating">
                <span class="material-symbols-outlined">star</span>
                <span>{{ movie.rating }}</span>
              </div>
              <h3>{{ movie.title }}</h3>
              <div class="movie-card__actions">
                <button class="button button--primary button--block">{{ movie.label }}</button>
                <button class="button button--ghost button--block">Xem trailer</button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Vé & Combo từ products.json -->
      <ProductList />

      <section id="ai" class="section section--muted">
        <div class="container">
          <div class="section__center">
            <h2>Công nghệ dẫn đầu trải nghiệm</h2>
            <p>
              Hệ sinh thái thông minh giúp hành trình xem phim của bạn liền mạch từ lúc chọn ghế
              đến khi vào rạp.
            </p>
          </div>

          <div class="feature-grid">
            <article
              v-for="feature in featureCards"
              :key="feature.title"
              class="feature-card"
              :class="{ 'feature-card--accent': feature.accent }"
            >
              <div class="feature-card__icon">
                <span class="material-symbols-outlined">{{ feature.icon }}</span>
              </div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="section container" id="showtimes">
        <div class="chat-grid">
          <div class="chat-copy">
            <h2>Nói điều bạn muốn, vé phim trong tay ngay</h2>
            <p>
              Không cần duyệt qua hàng tá lịch chiếu phức tạp. Chỉ cần nói cho AI của chúng tôi
              biết bạn muốn xem gì, ở đâu và mức giá mong muốn. Hệ thống sẽ xử lý phần còn lại.
            </p>

            <ul class="checklist">
              <li>
                <span class="material-symbols-outlined">check_circle</span>
                Xử lý ngôn ngữ tự nhiên tiếng Việt chính xác
              </li>
              <li>
                <span class="material-symbols-outlined">check_circle</span>
                So sánh giá và suất chiếu đa rạp theo thời gian thực
              </li>
              <li>
                <span class="material-symbols-outlined">check_circle</span>
                Tự động đề xuất combo bắp nước tối ưu
              </li>
            </ul>

            <button class="button button--ghost button--wide">Khám phá tính năng AI</button>
          </div>

          <div class="chat-panel">
            <div class="chat-panel__glow"></div>
            <div class="chat-panel__window">
              <div class="chat-panel__header">
                <div class="chat-panel__avatar">
                  <span class="material-symbols-outlined">smart_toy</span>
                </div>
                <div>
                  <strong>CineAI Assistant</strong>
                  <span class="chat-panel__status"><span></span> Online</span>
                </div>
              </div>

              <div class="chat-panel__body">
                <div class="message message--user">Tìm phim hành động tối nay ở Quận 7 giá dưới 150k</div>
                <div class="message message--assistant">
                  Chào bạn! Tôi tìm thấy 3 suất chiếu phim <strong>'John Wick 4'</strong> tại
                  <strong>CGV SC VivoCity</strong>:
                  <div class="chips">
                    <span
                      v-for="reply in chatQuickReplies"
                      :key="reply"
                      class="chip"
                      :class="{ 'chip--active': reply === '19:30' }"
                    >{{ reply }}</span>
                  </div>
                  Giá vé đang ưu đãi chỉ từ <strong>120k</strong>. Bạn có muốn đặt vé ngay không?
                </div>
              </div>

              <div class="chat-panel__input">
                <div class="chat-panel__field">
                  <span class="material-symbols-outlined">mic</span>
                  <input value="Đặt vé suất 19:30" readonly />
                </div>
                <button class="icon-button icon-button--primary" aria-label="Send message">
                  <span class="material-symbols-outlined">send</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="section section--promo container">
        <div class="promo-card">
          <div>
            <h2>Ưu đãi độc quyền cho thành viên CineAI</h2>
            <p>Đăng ký ngay để nhận những đặc quyền dành riêng cho bạn.</p>
          </div>

          <div class="promo-grid">
            <article class="promo-item">
              <div class="promo-item__icon"><span class="material-symbols-outlined">loyalty</span></div>
              <div>
                <p>Tặng ngay</p>
                <strong>Mã giảm giá 20% lần đầu</strong>
              </div>
            </article>

            <article class="promo-item">
              <div class="promo-item__icon"><span class="material-symbols-outlined">local_dining</span></div>
              <div>
                <p>Đồng giá</p>
                <strong>Combo bắp nước 99k</strong>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="section section--cta" id="theaters">
        <div class="cta-overlay"></div>
        <div class="container cta-block">
          <h2>Khám phá trải nghiệm đặt vé thông minh ngay hôm nay!</h2>
          <button class="button button--primary button--large">
            Đăng ký ngay
            <span class="material-symbols-outlined">arrow_forward</span>
          </button>
        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="container footer__inner">
        <div>
          <span class="brand brand--footer">CineAI</span>
          <p>© 2026 CineAI Studios. Powered by Cinema Intelligence.</p>
        </div>

        <div class="footer__links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Cookie Settings</a>
          <a href="#">Help Center</a>
        </div>
      </div>
    </footer>
  </div>
</template>
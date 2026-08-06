# Thông tin thành viên trong nhóm, nội dung các buổi học trong file ABOUT.md
# CineAI - Hệ thống Đặt Vé Xem Phim Thông Minh Tích Hợp AI

**CineAI** là một nền tảng đặt vé xem phim Full-stack Multi-vendor hiện đại. Dự án được tích hợp các mô hình trí tuệ nhân tạo (AI) giúp tối ưu hóa trải nghiệm khách hàng. Hỗ trợ quản trị viên quản lý doanh thu, suất chiếu thông minh theo thời gian thực.

---

## 🚀 Các Tính Năng Nổi Bật

### 🤖 1. Cổng Trí Tuệ Nhân Tạo (AI Discovery Hub)
Tích hợp AI cao cấp mang lại trải nghiệm tương tác tự nhiên và cá nhân hóa cho người dùng tại cổng `/ai-discovery`:
- **CineAI Assistant (Chatbot đặt vé):** Trò chuyện bằng ngôn ngữ tự nhiên để tìm kiếm phim, rạp chiếu và suất chiếu thực tế. Trợ lý AI tự động trích xuất thực thể, thời gian và đề xuất suất chiếu trực quan để người dùng đặt vé siêu tốc.
- **AI Mood Matcher (Chọn phim theo tâm trạng):** Người dùng nhập tâm trạng hoặc hoàn cảnh hiện tại (ví dụ: *"Tôi muốn tìm phim hài giải tỏa stress sau giờ làm"*). AI phân tích danh sách phim đang chiếu tại hệ thống và đề xuất **Top 3 bộ phim phù hợp nhất** kèm lời khuyên lý giải cụ thể, thấu hiểu tâm lý.

### 📊 2. Admin Dashboard Cao Cấp (Overview & Transactions)
Giao diện quản trị được thiết kế theo phong cách hiện đại, trực quan, hỗ trợ quản trị viên nắm bắt nhanh hiệu quả kinh doanh:
- **Bục Vinh Quang Phim:** Tôn vinh Top 3 phim có doanh thu cao nhất theo chu kỳ thời gian (Tháng này / Năm nay / Tất cả) với hiệu ứng phát sáng viền neon vàng/bạc/đồng và poster thực tế.
- **Modal Phân Tích Suất Chiếu:** Khi click vào poster phim trên bục vinh quang, mở ra popup phân tích chi tiết: doanh thu, lượng vé bán ra và tỷ lệ lấp đầy ghế thực tế của các suất chiếu tiếp theo.
- **Bảng Xếp Hạng & Sparkline:** Bảng xếp hạng phim động hỗ trợ bộ lọc nhanh kèm biểu đồ mini (sparkline) dạng SVG động đổi màu theo tỷ lệ tăng trưởng.
- **Bộ Lọc Giao Dịch Đa Cổng:** Quản lý giao dịch tích hợp cổng **VNPAY** và **PayPal**, cho phép lọc danh sách thanh toán chính xác theo từng cổng và hiển thị mã Order ID/Capture ID chi tiết.

### 💳 3. Đặt Vé & Thanh Toán Đa Cổng
- **Đa cổng thanh toán:** Hỗ trợ thanh toán nội địa qua **VNPAY** và thanh toán quốc tế qua **PayPal**.
- **Vé & Email tự động:** Sau khi đặt vé thành công, hệ thống tự động gửi email xác nhận cho khách hàng chứa thông tin chi tiết vé, mã vé và hình ảnh vé điện tử thiết kế trực quan.
- **Nút chọn lại combo:** Cho phép người dùng dễ dàng quay lại bước chọn combo từ trang thanh toán nếu đổi ý.

### 🔍 4. Tối Ưu Hóa SEO Toàn Diện (Seoquake Certified)
Trang web được thiết kế tuân thủ nghiêm ngặt các quy tắc tối ưu hóa công cụ tìm kiếm:
- **Canonical & Language Tags:** Khai báo ngôn ngữ Việt Nam (`lang="vi"`) và thẻ canonical động.
- **Thẻ Meta & Open Graph:** Cấu hình đầy đủ thẻ meta description tối ưu (270 ký tự), Open Graph và Twitter Cards hỗ trợ hiển thị hình ảnh preview đẹp mắt khi chia sẻ lên MXH.
- **Schema.org & Google Analytics:** Nhúng dữ liệu có cấu trúc JSON-LD và tag đo lường GA4 giúp tăng thứ hạng tìm kiếm.
- **XML Sitemap tự động:** Hệ thống tự động sinh sơ đồ trang web thời gian thực tại `/sitemap.xml`.
- **Text/HTML Ratio:** Bổ sung các khối văn bản SEO tinh tế ở trang chủ và chân trang giúp tỷ lệ văn bản vượt mốc **15%** an toàn.

## 👥 Phân Quyền & Vai Trò Hệ Thống (Roles & Permissions)

Hệ thống được thiết kế theo mô hình phân quyền chặt chẽ phục vụ 3 đối tượng người dùng chính:

### 1. Khách Hàng (User)
- Tìm kiếm phim, suất chiếu thông minh qua AI Discovery Hub (CineAI Assistant & AI Mood Matcher).
- Chọn rạp chiếu, lịch chiếu, phòng chiếu và đặt giữ ghế trực tuyến theo thời gian thực.
- Đặt combo bắp nước đi kèm với nhiều voucher khuyến mãi giảm giá.
- Thanh toán tiện lợi qua cổng nội địa VNPAY hoặc cổng quốc tế PayPal.
- Nhận email vé điện tử tự động và quản lý lịch sử đặt vé trong trang cá nhân.

### 2. Quản Trị Viên Toàn Hệ Thống (Super Admin)
- **Tổng quan hệ thống:** Theo dõi biểu đồ doanh thu, vé bán ra, và hiệu suất kinh doanh của tất cả các chi nhánh rạp trên toàn quốc thông qua Dashboard trực quan.
- **Quản lý danh mục rạp:** Thêm, sửa, xóa các Chi nhánh rạp (Branches) và Phòng chiếu (Auditoriums) trong hệ thống.
- **Quản lý phim:** CRUD Phim (kết nối TMDB API) và phê duyệt danh mục phim chiếu trên toàn hệ thống.
- **Quản lý người dùng:** Quản lý tài khoản, theo dõi hoạt động và phân quyền quản trị chi nhánh cho các nhân viên.
- **Quản lý tài chính:** Giám sát tất cả các giao dịch thanh toán từ VNPAY và PayPal của hệ thống.
- **Quản lý Khuyến mãi:** Tạo mã giảm giá, voucher cho các chiến dịch toàn cụm rạp.

### 3. Quản Trị Viên Chi Nhánh (Branch Admin)
- **Vận hành chi nhánh:** Quản lý hoạt động riêng biệt của chi nhánh rạp được chỉ định (bảo mật độc lập dữ liệu giữa các rạp).
- **Lập lịch suất chiếu (Showtimes):** CRUD và phân bổ giờ chiếu cho phim tại các phòng chiếu của chi nhánh mình quản lý.
- **Quản lý phòng chiếu & ghế ngồi:** Thiết lập cấu hình phòng chiếu, sơ đồ ghế ngồi (Seat Layout), phân loại ghế (Thường, VIP, đôi Sweetbox) và giá vé nền tương ứng.
- **Thống kê chi nhánh:** Xem báo cáo doanh thu, sản lượng vé bán ra chi tiết của riêng chi nhánh được giao quản lý để tự động tối ưu hóa suất chiếu.

---

## 🛠️ Công Nghệ Sử Dụng

- **Frontend:** Nuxt 3 (Vue 3, TypeScript, TailwindCSS, Pinia, Axios).
- **Backend:** FastAPI (Python, Uvicorn, SQLAlchemy async, Alembic, PostgreSQL).
- **AI integration:** Gemini API (Model `gemini-3.5-flash` nhận diện và phân tích ngôn ngữ tự nhiên).

---

## 💻 Hướng Dẫn Cài Đặt & Chạy Dự Án

### Cách 1: Chạy Bằng Docker Compose (Khuyên Dùng)

1. Tạo tệp `.env` tại thư mục gốc của dự án (cùng cấp với `docker-compose.yml`):
   ```env
   POSTGRES_USER=ppq_user
   POSTGRES_PASSWORD=change-me
   POSTGRES_DB=movie_db
   POSTGRES_PORT=5432
   JWT_SECRET_KEY=change-this-secret
   TMDB_API_TOKEN=your_tmdb_token
   GEMINI_API_KEY=your_gemini_api_key
   RUN_SEED=1
   ```

2. Khởi động hệ thống:
   ```bash
   docker compose up --build
   ```

3. Truy cập:
   - **Frontend:** `http://localhost:3000`
   - **Backend API Docs:** `http://localhost:8000/docs`

---

### Cách 2: Chạy Thủ Công (Manual)

#### 1. Backend (FastAPI)
1. Di chuyển vào thư mục backend và cài đặt thư viện:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. Khởi tạo cơ sở dữ liệu và seed dữ liệu mẫu:
   ```bash
   alembic upgrade head
   python scripts/seed_demo_auth.py
   ```
3. Chạy API Server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### 2. Frontend (Nuxt 3)
1. Di chuyển vào thư mục frontend và cài đặt dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Khởi động Dev Server:
   ```bash
   npm run dev
   ```
3. Mở trình duyệt tại `http://localhost:3000`.

---

*Thông tin chi tiết về quá trình học tập và phân công thành viên được lưu trữ trong file [ABOUT.md](file:///c:/SE%20Special%20Project%202/PPQ/ABOUT.md).*

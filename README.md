# Thông tin thành viên trong nhóm, nội dung các buổi học trong file ABOUT.MD

# Hệ thống đặt vé xem phim Full Stack với AI, 
# Vue 3 + TypeScript + Vite + Nuxtjs + Axios

## Backend FastAPI
- Backend dùng FastAPI + async SQLAlchemy + PostgreSQL.
- Database connection local hiện tại nằm trong `backend/.env`.
- Migration/Alembic: `backend/alembic/`
- Script tạo bảng nhanh: `backend/scripts/create_tables.py`
- Script seed demo auth: `backend/scripts/seed_demo_auth.py`

### Chạy backend
1. Cài dependency trong `backend/requirements.txt`.
2. Chạy migration: `alembic upgrade head` trong thư mục `backend/`.
3. Nếu cần dữ liệu đăng nhập demo, chạy `python scripts/seed_demo_auth.py`.
4. Khởi động API: `uvicorn app.main:app --reload`.

### Chạy full stack bằng Docker
1. Tạo file `.env` ở thư mục gốc (cùng cấp `docker-compose.yml`) với nội dung tối thiểu:

```env
POSTGRES_USER=ppq_user
POSTGRES_PASSWORD=change-me
POSTGRES_DB=movie_db
POSTGRES_PORT=5432
JWT_SECRET_KEY=change-this-secret
TMDB_API_TOKEN=your_tmdb_token
RUN_SEED=1
```

2. Build và chạy:

```bash
docker compose up --build
```

3. Truy cập:
- Frontend: `http://localhost:3000`
- Backend API docs: `http://localhost:8000/docs`

4. Dừng:

```bash
docker compose down
```

## 👤 User (Khách hàng)
- **Đăng ký/Đăng nhập**: tạo tài khoản, lưu thông tin cá nhân.  
- **Xem phim & lịch chiếu**: duyệt danh sách phim, trailer, suất chiếu.  
- **Đặt vé**: chọn phim, suất chiếu, ghế ngồi, số lượng vé.  
- **Thanh toán**: tích hợp ví điện tử, thẻ ngân hàng.  
- **Quản lý vé**: lưu vé điện tử, QR code, lịch sử đặt vé.  
- **AI gợi ý**: đề xuất phim/suất chiếu phù hợp sở thích.  

---

## 🛠️ Admin (Quản trị tổng)
- **Quản lý phim**: thêm/sửa/xóa phim, duyệt nội dung.  
- **Quản lý suất chiếu**: tạo lịch chiếu, cấu hình phòng chiếu, số ghế.  
- **Quản lý người dùng**: theo dõi hoạt động, phân quyền, hỗ trợ khách hàng.  
- **Thống kê**: doanh thu, báo cáo vé bán ra.  
- **Khuyến mãi**: tạo mã giảm giá toàn hệ thống.  
- **Quản lý AI**: tinh chỉnh thuật toán gợi ý, chatbot.
- 
## 🛠️ Admin (Quản chi nhánh)
- **Quản lý phim**: thêm/sửa/xóa phim, duyệt nội dung.  
- **Quản lý suất chiếu**: tạo lịch chiếu, cấu hình phòng chiếu, số ghế.  
- **Quản lý phòng chiếu**: CRUD phim, thông tin của phòng chiếu.
- **Thống kê**: doanh thu, báo cáo vé bán ra.  
- **Quản lý AI**: tinh chỉnh thuật toán gợi ý, chatbot.
- **Quản lý ghế ngồi**: setup ghế ngồi, các loại ghế trong rạp.  


---

## 🤖 Chức năng AI

### AI cho User
- **Gợi ý phim cá nhân hóa**: dựa trên lịch sử đặt vé, thể loại yêu thích.  
- **Chatbot hỗ trợ**: trả lời câu hỏi về phim, lịch chiếu, hướng dẫn đặt vé.  
- **Tìm kiếm ngữ nghĩa**: ví dụ: “phim tình cảm tối nay”.  
- **Đặt vé bằng giọng nói**: hỗ trợ voice command.  
- **Phân tích cảm xúc**: gợi ý phim phù hợp tâm trạng.  

### AI cho Admin
- **Phân tích xu hướng**: dự đoán phim hot, thể loại được ưa chuộng.  
- **Tối ưu lịch chiếu**: gợi ý suất chiếu hợp lý.  
- **Phát hiện gian lận**: kiểm tra giao dịch bất thường.  
- **Phân tích dữ liệu lớn**: hành vi người dùng toàn hệ thống.  


Mình dùng TMDB API để lấy poster, trailer, mô tả phim, diễn viên, giúp giao diện đặt vé nhìn cho hấp dẫn và chuẩn dữ liệu. Từ đó, user sẽ thấy thông tin phim đầy đủ, giống các nền tảng quốc tế.
Nhưng mà TMDB không cung cấp suất chiếu, ghế, giá vé, nên là phải tự xây dựng và quản lý trong database của mình.

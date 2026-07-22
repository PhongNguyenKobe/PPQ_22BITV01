# Hệ thống đặt vé xem phim Full Stack với AI
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

### API user đã nối frontend
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/users/me`

## 👤 User (Khách hàng)
- **Đăng ký/Đăng nhập**: tạo tài khoản, lưu thông tin cá nhân.  
- **Xem phim & lịch chiếu**: duyệt danh sách phim, trailer, suất chiếu.  
- **Đặt vé**: chọn phim, suất chiếu, ghế ngồi, số lượng vé.  
- **Thanh toán**: tích hợp ví điện tử, thẻ ngân hàng.  
- **Quản lý vé**: lưu vé điện tử, QR code, lịch sử đặt vé.  
- **AI gợi ý**: đề xuất phim/suất chiếu phù hợp sở thích.  

---

## 🛠️ Admin Website (Quản trị tổng)
- **Quản lý hệ thống**: tạo/sửa/xóa chi nhánh rạp.  
- **Quản lý phim**: duyệt phim của admin thêm mới, có thể xóa,sửa.  
- **Quản lý người dùng**: theo dõi hoạt động, có thể phân quyền tài khoản, hỗ trợ khách hàng.  
- **Thống kê tổng**: doanh thu toàn hệ thống, báo cáo chi nhánh.  
- **Quản lý AI**: tinh chỉnh thuật toán gợi ý, chatbot.  

---

## 🎬 Admin Chi nhánh Rạp
- **Quản lý thông tin cá nhân của rạp**: thêm, xóa, sửa thông tin rạp như vị trí,...  
- **Quản lý suất chiếu**: lên lịch chiếu phim cho rạp của mình.  
- **Quản lý phim**: thêm phim mới, có thể xóa, sửa thông tin phim cũ, khi thêm mới thì đợi admin website duyệt.  
- **Quản lý phòng chiếu**: cấu hình số ghế, sơ đồ phòng.  
- **Theo dõi vé bán**: thống kê vé bán ra theo suất chiếu.  
- **Khuyến mãi tại rạp**: tạo mã giảm giá riêng cho chi nhánh.  
- **Quản lý nhân viên**: phân quyền nhân viên hỗ trợ tại rạp.  

---

# 🤖 Chức năng AI

## AI cho User (Khách hàng)
- **Gợi ý phim cá nhân hóa**: dựa trên lịch sử đặt vé, thể loại yêu thích, xu hướng.  
- **Chatbot hỗ trợ**: trả lời câu hỏi về phim, lịch chiếu, hướng dẫn đặt vé.  
- **Tìm kiếm ngữ nghĩa**: ví dụ: “phim tình cảm tối nay” → AI lọc suất chiếu phù hợp.  
- **Đặt vé bằng giọng nói**: hỗ trợ voice command để đặt vé nhanh.  
- **Phân tích cảm xúc**: dựa trên review, AI gợi ý phim phù hợp tâm trạng.  

---

## AI cho Admin Website (Quản trị tổng)
- **Phân tích xu hướng**: dự đoán phim hot, thể loại được ưa chuộng.  
- **Tối ưu lịch chiếu**: gợi ý suất chiếu hợp lý để tăng doanh thu.  
- **Phát hiện gian lận**: kiểm tra giao dịch bất thường, bảo mật hệ thống.  
- **Quản lý dữ liệu lớn**: phân tích hành vi người dùng toàn hệ thống.  

---

## AI cho Admin Chi nhánh Rạp
- **Dự đoán lượng vé bán**: giúp rạp chuẩn bị nhân sự, dịch vụ.  
- **Quản lý khuyến mãi thông minh**: AI gợi ý chương trình giảm giá phù hợp từng chi nhánh.  
- **Phân tích hiệu suất suất chiếu**: đánh giá suất nào bán chạy, suất nào cần cải thiện.  
- **Quản lý trải nghiệm khách hàng**: phân tích feedback để nâng cao dịch vụ.  

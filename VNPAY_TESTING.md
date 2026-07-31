# Kiểm tra luồng thanh toán VNPAY

## Cấu hình

Điền thông tin Sandbox thật vào `.env` ở thư mục gốc:

```env
VNPAY_TMN_CODE=...
VNPAY_HASH_SECRET=...
VNPAY_PAYMENT_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:3000/checkout/vnpay-return
```

Nếu chạy backend trực tiếp thay vì Docker, điền các biến tương tự vào `backend/.env`.
Không commit hai giá trị bí mật vào Git.

## Chạy và thanh toán thử

```powershell
docker compose up --build
```

1. Đăng nhập bằng tài khoản khách hàng.
2. Chọn phim, suất chiếu và ghế.
3. Ở bước thanh toán, chọn `Ví VNPAY`.
4. Nhấn `Xác Nhận Thanh Toán`.
5. Hoàn tất giao dịch bằng tài khoản/thẻ thử nghiệm do VNPAY Sandbox cung cấp.
6. Chờ VNPAY chuyển về trang `/checkout/vnpay-return`.
7. Trang kết quả phải hiện `Thanh toán thành công`, mã tham chiếu, mã thanh toán và trạng thái `SUCCESS`.
8. Nhấn `Xem vé của tôi`; vé phải xuất hiện trong `/profile/tickets`.

## Dấu hiệu giao dịch hợp lệ

Trong trang Admin Payments hoặc cơ sở dữ liệu, giao dịch phải có:

- Payment: `status = SUCCESS`.
- Booking: `status = CONFIRMED`.
- `response_code = 00`.
- `provider_status = 00`.
- `signature_valid = true`.
- `provider_transaction_no` và `paid_at` có giá trị.
- Lịch sử payment có nguồn `CALLBACK`, `RETURN` hoặc `IPN`.

Nếu hệ thống báo thành công nhưng Merchant Sandbox không thấy giao dịch, kiểm tra tài khoản đang đăng nhập có cùng `TmnCode`, khoảng ngày tìm kiếm và múi giờ Việt Nam.

## IPN khi triển khai

VNPAY không gọi được `localhost`. Khi triển khai thật hoặc kiểm tra IPN từ Internet, cấu hình URL HTTPS công khai:

```text
https://<backend-domain>/api/v1/payments/vnpay/ipn
```

Return URL của người dùng vẫn là:

```text
https://<frontend-domain>/checkout/vnpay-return
```

## Kiểm tra tự động

```powershell
cd backend
python -m unittest discover -s tests -p "test_*.py"
python -m compileall -q app
```

## Kiểm tra hủy vé và hoàn tiền

1. Thanh toán thành công một vé VNPAY có suất chiếu còn ít nhất 120 phút.
2. Tại `Vé của tôi`, mở vé và chọn `Yêu cầu hủy vé`.
3. Vé chuyển sang `CANCEL_REQUESTED`; ghế chưa được giải phóng cho tới khi quản trị viên duyệt.
4. Đăng nhập Branch Admin, mở `Đặt vé`, chọn:
   - `Từ chối`: vé trở lại `CONFIRMED`.
   - `Duyệt hủy & hoàn tiền`: vé thành `CANCELLED`, ghế được giải phóng và hệ thống gửi yêu cầu hoàn toàn phần tới VNPAY.
5. Trong `Thanh toán`, kiểm tra trạng thái:
   - `REFUND_PENDING`: VNPAY đang xử lý; dùng `Đối soát`.
   - `REFUNDED`: hoàn tiền thành công.
   - `REFUND_FAILED`: xem lỗi rồi chọn `Thử hoàn lại`.
6. Nếu Admin hủy cả suất chiếu, tất cả vé `CONFIRMED` và `CANCEL_REQUESTED` của suất đó được hủy, giải phóng ghế và đưa vào cùng luồng hoàn tiền.

Không bấm gửi hoàn lại lần nữa khi giao dịch đang `REFUND_PENDING`; hãy đối soát trạng thái trước để tránh yêu cầu trùng.

# Gian Hàng Thương Hiệu

Trang tĩnh trên GitHub Pages: trang chủ liệt kê các gian hàng; mỗi cơ sở một gian hàng (`/<slug>/`); mã QR trên bao bì trỏ về trang sản phẩm `/01/<GTIN-13>/` (cấu trúc GS1 Digital Link), trang này có nút vào gian hàng.

## Thêm một cơ sở
1. Chép `co_so/_mau` thành `co_so/<slug>` (slug: chữ thường không dấu, số, gạch ngang).
2. Điền `co_so.json` (chép từ bao bì, không bịa). Ảnh để trong `co_so/<slug>/anh/` (JPG, khoảng 200 KB, tên không dấu): logo, ảnh bìa, ảnh từng dòng sản phẩm.
3. `python tao_trang.py` (kiểm số kiểm tra GTIN, GTIN không trùng giữa các cơ sở, đủ ảnh).
4. `python tao_qr.py <slug> <thư mục ra>` tạo file QR.
5. `git add -A`, `git commit`, `git push`; chờ khoảng 1 phút rồi quét thử.

## Video
Điền link YouTube hoặc .mp4 vào `video_gioi_thieu` (gian hàng) hoặc `video` của từng sản phẩm, chạy lại `tao_trang.py`.

## Đổi địa chỉ gốc (tên miền riêng)
Sửa `dia_chi_goc` trong `nen_tang.json`, chạy lại `tao_trang.py` rồi `tao_qr.py`. Phải chốt trước khi in QR lên bao bì.

## Gian hàng mẫu
Gian hàng đầu tiên (một cơ sở cà phê, 6 sản phẩm, video, giao diện quán cà phê) đã gỡ khỏi trang ngày 20/11/2026 vì cơ sở có website riêng. Dữ liệu và ảnh vẫn nằm trong lịch sử kho, dùng làm ví dụ: `git show e5f8cee:co_so/hita/co_so.json`; khôi phục cả thư mục: `git checkout e5f8cee -- co_so/hita`.

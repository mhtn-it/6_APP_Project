# Đồ án môn Lập trình song song ứng dụng
**Giảng viên: Thầy Trần Trung Kiên**

## Thông tin nhóm
### STT: Nhóm 6

### Thành viên:
1. 1712258 - Nguyễn Văn Hậu - [kenneth-nguyenn](https://github.com/kenneth-nguyenn)
2. 18120181 - Nguyễn Thị Cẩm Hồng - [chnhgr](https://github.com/chnhgr)
3. 18120216 - Mai Huỳnh Trung Nguyên - [mhtn-it](https://github.com/mhtn-it)

### Tài liệu của nhóm
- Kế hoạch nhóm, phân chia công việc: [Google Sheet](https://docs.google.com/spreadsheets/d/1lNRWbRRnsN0L1bEBLm2tHkauJC2jS9DPZiZfhLQ9Av8/edit?usp=sharing)
- Link Colab thực thi: [Google Colab](https://colab.research.google.com/github/mhtn-it/6_APP_Project/blob/main/Report.ipynb)
- Drive làm việc chung: [Google Drive](https://drive.google.com/drive/folders/1bDjdUTDdbr1EV_9VxSVIOGB60OutJlZi?usp=sharing)

## Bài toán:
**Đề tài**: Thay đổi background ảnh dựa vào phương pháp Poisson Matting

**Input**: 
- Một bức ảnh chân dung
- Trimap của ảnh (được tạo từ một bài toán khác)
- Ảnh nền mới mong muốn

**Output**: 
- Ảnh đã được thay đổi nền

**Ý nghĩa thực tế của ứng dụng**:
- Thay đổi background của ảnh khi cần thiết, ví dụ trong các trường hợp như ảnh kỷ niệm, ảnh thẻ, trang trí...
- Áp dụng trên các phần mềm chỉnh sửa ảnh, trang web chỉnh sửa ảnh online

**Lý do cần tăng tốc**: 
- Toàn bộ quá trình xử lý để cho ra một bức ảnh đúng và chính xác có thể mất đến vài phút (giảm trải nghiệm người dùng)
- Khi xử lý hàng loạt, số lượng lớn thì thời gian sẽ rất lâu

## Tài liệu tham khảo

# Đồ án môn Lập trình song song ứng dụng
**Giảng viên hướng dẫn: Thầy Trần Trung Kiên**

## Thông tin nhóm
### STT: Nhóm 6

### Thành viên:
1. 1712258 - Nguyễn Văn Hậu - [kenneth-nguyenn](https://github.com/kenneth-nguyenn)
2. 18120181 - Nguyễn Thị Cẩm Hồng - [chnhgr](https://github.com/chnhgr)
3. 18120216 - Mai Huỳnh Trung Nguyên - [mhtn-it](https://github.com/mhtn-it)

### Tài liệu của nhóm
- Link thùng chứa Github của nhóm: [Github](https://github.com/mhtn-it/6_APP_Project)
- Kế hoạch nhóm, phân chia công việc: [Google Sheet](https://docs.google.com/spreadsheets/d/1lNRWbRRnsN0L1bEBLm2tHkauJC2jS9DPZiZfhLQ9Av8/edit?usp=sharing)
- Link Colab thực thi: [Google Colab](https://colab.research.google.com/github/mhtn-it/6_APP_Project/blob/main/Report.ipynb)

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
- Là một phần xử lý của quy trình đổi nền của video

**Lý do cần tăng tốc**: 
- Toàn bộ quá trình xử lý để cho ra một bức ảnh đúng và chính xác có thể mất đến vài phút (giảm trải nghiệm người dùng)
- Khi xử lý hàng loạt, số lượng lớn thì thời gian sẽ rất lâu
- Nếu áp dụng cho đổi nền video thì cần có tốc độ nhanh

## Tài liệu tham khảo
- Project: Poisson Matting, [github](https://github.com/avani17101/Poisson-Matting).
- Paper: Poisson Matting của Juan Sun, Jiaya Jia, Chi-Keung Tang, Heung-Yeung Shum, [paper](http://www.cse.cuhk.edu.hk/~leojia/all_final_papers/matting_siggraph04.pdf)
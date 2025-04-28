# PassGPTv2
Hệ thống sinh mật khẩu phục vụ các cuộc tấn công Brute Force hoàn toàn dựa trên mô hình ngôn ngữ lớn. Một ý tưởng mới về cải tiến của mô hình PassGPT (https://github.com/javirandor/passgpt.git). Ở đây tôi xử lý thêm phần cấu trúc để đảm bảo tính chính xác của đầu ra mật khẩu hơn và xây dựng hệ thống sinh mật khẩu đáp ứng tất cả yêu cầu cho người sử dụng.

![image](https://github.com/user-attachments/assets/078589fe-d9ed-46d1-bc44-4ec9a7d893a8)

Quá trình training (left) và quá trình sinh (right) của PassGPTv2. Các số trong hình tương ứng với các chỉ mục sau khi mã hóa. Các trường hợp, trong đó số bị che khuất, biểu thị các dự đoán không chính xác, trong khi các số được tô sáng màu đỏ biểu thị các chỉ mục dự đoán của mật khẩu mới.
## Yêu cầu cài đặt:

Sử dụng: Python 3.8 được cài đặt ở https://www.python.org/downloads/release/python-380/ (Lưu ý không nên sử dụng phiên bản cao hơn vì chưa tương thích)
Tải bộ cuda về máy tính để mô hình có thể hoạt động dựa trên gpu. Có thể tham khảo link https://schoolforengineering.com/tutorial/install-tensorflow-cuda-gpu-windows-10/

## Khởi chạy chương trình
Vào terminal của folder

Tải các thư viện cần thiết

  pip install -r requirements.txt
  
Khởi chạy file app.py

  python app.py
  
Nếu thoát không sử dụng thì Ctrl + C

Vì dung lượng cho phép hệ thống sẽ tự động tải model về cho PassGPT và PassGPTv2, bạn sẽ phải đợi khi thông báo có thể vào link

Vào link http://127.0.0.1:5000 để sử dụng hệ thống

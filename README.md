# PassGPTv2
Hệ thống sinh mật khẩu phục vụ các cuộc tấn công Brute Force hoàn toàn dựa trên mô hình ngôn ngữ lớn. Một ý tưởng mới về cải tiến của mô hình PassGPT (https://github.com/javirandor/passgpt.git). Ở đây ngoài được huấn luyện bởi các chuỗi mật khẩu từ tập dữ liệu bị rò rỉ, tôi đã huấn luyện cả phần cấu trúc cho mỗi mật khẩu đảm bảo xác suất khi sinh ra mật khẩu phổ biến được tốt hơn được tùy chọn điều chỉnh thêm phần cấu trúc để đảm bảo tính cố định cho đầu ra mật khẩu và xây dựng hệ thống sinh mật khẩu đáp ứng yêu cầu cho người sử dụng. Ngoài ra để nâng cao hiệu quả của tấn công Brute force tôi đề xuất phương pháp chọn ra các những mật khẩu có xác suất phổ biến nhất dựa trên thuật toán PCFG (https://github.com/lakiw/pcfg_cracker.git).

![image](https://github.com/user-attachments/assets/078589fe-d9ed-46d1-bc44-4ec9a7d893a8)

Quá trình training (left) và quá trình sinh (right) của PassGPTv2. Các số trong hình tương ứng với các chỉ mục sau khi mã hóa. Các trường hợp, trong đó số bị che khuất, biểu thị các dự đoán không chính xác, trong khi các số được tô sáng màu đỏ biểu thị các chỉ mục dự đoán của mật khẩu mới.

## Khởi chạy chương trình
Vào terminal của folder

Build docker:

    sudo systemctl restart docker
    sudo docker build -t passgptv2 .
  
Khởi chạy file app.py:

    sudo docker run -it -p 5000:5000 passgptv2 /bin/bash
    python3.8 app.py
  
Nếu thoát không sử dụng ấn tổ hợp phím Ctrl + C để thoát.

Vì dung lượng không cho phép hệ thống sẽ tự động tải model về cho PassGPT và PassGPTv2, bạn sẽ phải đợi khi thông báo có thể vào link.

Vào link http://127.0.0.1:5000 để sử dụng hệ thống.

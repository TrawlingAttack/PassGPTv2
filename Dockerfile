# Sử dụng image Python 3.8 chính thức
FROM python:3.8-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy toàn bộ project vào container
COPY . /app


# Nâng cấp pip và cài đặt các thư viện từ requirements.txt
RUN pip3.8 install --upgrade pip
RUN pip3.8 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip3.8 install -r requirements.txt
RUN python3.8 check_run.py
# Expose port 5000 để Flask có thể truy cập từ bên ngoài
EXPOSE 5000

# Chạy Flask app bằng Python 3.8
CMD ["python3.8", "app.py"]

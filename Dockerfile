# Sử dụng image Python 3.8 chính thức (nhẹ)
FROM python:3.8-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy toàn bộ project vào container
COPY . /app

# Cập nhật và cài đặt john + hashcat + các thư viện cần thiết
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        john \
        hashcat \
        build-essential \
        gcc \
        libffi-dev \
        libssl-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Nâng cấp pip và cài torch (CUDA 11.8)
RUN pip3.8 install --upgrade pip && \
    pip3.8 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Cài các thư viện Python trong requirements.txt
RUN pip3.8 install -r requirements.txt

# (Tùy chọn) Tải model sẵn trong quá trình build nếu cần
RUN python3.8 check_run.py

# Mở cổng Flask
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["python3.8", "app.py"]

import torch
import sys
import os
import gdown
import zipfile

# Danh sách model cần tải
models = [
    {
        "name": "PassGPT",
        "url": "https://drive.google.com/uc?id=1tukK05TPl-1Qt7s33JTZ6F_JwqUvmh6m",
        "zip_path": "PassGPT/model_passgpt.zip",
        "extract_path": "PassGPT/model_passgpt",
        "required_files": ["model_passgpt"]
    },
    {
        "name": "PassGPTv2",
        "url": "https://drive.google.com/uc?id=1ZL7R0Ujf7jn_e_IUeViFpKhYYhfX3uBx",
        "zip_path": "PassGPTv2/model_passgptv2.zip",
        "extract_path": "PassGPTv2/model_passgptv2",
        "required_files": ["model_passgptv2"]
    }
]

def download_file(url, filename):
    print(f"🚀 Downloading {filename} from Google Drive...")
    gdown.download(url, filename, quiet=False)

def extract_zip(zip_path, extract_to):
    print(f"📦 Extracting {zip_path} to {extract_to}...")
    # Dùng với ZipFile để giải nén
    with zipfile.ZipFile(zip_path, 'r') as zObject:
        zObject.extractall(path=extract_to)
    print(f"✅ Extracted to {extract_to}")

def check_required_files(base_path, required_files):
    for req in required_files:
        if not os.path.exists(os.path.join(base_path, req)):
            return False
    return True

def download_model():
    for model in models:
        # Kiểm tra nếu thư mục model đã tồn tại và có đủ file yêu cầu
        if os.path.exists(model['extract_path']) and check_required_files(model['extract_path'], model['required_files']):
            print(f"✅ Model '{model['name']}' already exists and is complete. Skipping download.\n")
            continue
        
        # Nếu chưa có thư mục hoặc thiếu file yêu cầu
        print(f"🚀 Downloading model: {model['name']}")
        
        # Nếu chưa có file zip, tải về
        if not os.path.exists(model['zip_path']):
            download_file(model['url'], model['zip_path'])
        
        # Giải nén nếu thư mục chưa có
        if not os.path.exists(model['extract_path']):
            extract_zip(model['zip_path'], model['extract_path'])
        
        # Không xóa file zip, vì chúng ta không cần xóa nó nữa
        print(f"📦 File zip '{model['zip_path']}' remains in place.\n")


# Kiểm tra GPU
if not torch.cuda.is_available():
    print("CUDA (GPU) không khả dụng. Vui lòng kiểm tra lại cài đặt.")
    print("Thoát chương trình ...")
    sys.exit(1)  # Thoát chương trình với mã lỗi 1
else:
    print("CUDA (GPU) đã được kích hoạt.")
    if torch.cuda.is_available():
        print("Tên GPU:", torch.cuda.get_device_name(0))
    download_model()


import torch
import sys
import os
import gdown
import zipfile

# Danh sách model cần tải
models = [
    {
        "name": "PassGPT_VietNam",  
        "url": "https://drive.google.com/uc?id=1Q1_CJODP0TphB1w1Xk_tjE0La5XrpegH",
        "zip_path": "PassGPT/model_passgpt_vn.zip",
        "extract_path": "PassGPT/model/model_passgpt_vn",
        "required_files": ["model_passgpt_vn"]
    },
    {
        "name": "PassGPT_China",  
        "url": "https://drive.google.com/uc?id=1flygKMOfIESCT5rUXIsSjujCGXPhHrzy",
        "zip_path": "PassGPT/model_passgpt_china.zip",
        "extract_path": "PassGPT/model/model_passgpt_china",
        "required_files": ["model_passgpt_china"]
    },
    {
        "name": "PassGPT_UnitedState",  
        "url": "https://drive.google.com/uc?id=1Fq5sGajoBmJGxu4pH8caY6FV5oHegA0i",
        "zip_path": "PassGPT/model_passgpt_us.zip",
        "extract_path": "PassGPT/model/model_passgpt_us",
        "required_files": ["model_passgpt_us"]
    },
    {
        "name": "PassGPT_Malaysia", 
        "url": "https://drive.google.com/uc?id=1s8qoLlzrmSUDjSvr65acdWfH88huRQYP",
        "zip_path": "PassGPT/model_passgpt_malaysia.zip",
        "extract_path": "PassGPT/model/model_passgpt_malaysia",
        "required_files": ["model_passgpt_malaysia"]
    },
    {
        "name": "PassGPT_Indonesia", 
        "url": "https://drive.google.com/uc?id=1Howa-atwAPDO3Wgz9vQz-COZGnOo9oWy",
        "zip_path": "PassGPT/model_passgpt_indo.zip",
        "extract_path": "PassGPT/model/model_passgpt_indo",
        "required_files": ["model_passgpt_indo"]
    },
    {
        "name": "PassGPTv2_VietNam", 
        "url": "https://drive.google.com/uc?id=1aRjvBlJDH43Gbb2DXOdR9YRc-_dmCQ-K",
        "zip_path": "PassGPTv2/model_passgptv2_vn.zip",
        "extract_path": "PassGPTv2/model/model_passgptv2_vn",
        "required_files": ["model_passgptv2_vn"]
    },
    {
        "name": "PassGPTv2_China",   
        "url": "https://drive.google.com/uc?id=1wkLgkQz_IlVhEfumT5oeYfcKcyUCBWro",
        "zip_path": "PassGPTv2/model_passgptv2_china.zip",
        "extract_path": "PassGPTv2/model/model_passgptv2_china",
        "required_files": ["model_passgptv2_china"]
    },
    {
        "name": "PassGPTv2_UnitedState", 
        "url": "https://drive.google.com/uc?id=193QCuWUW6C6Plo8D4Fq3Ucvgl882l-t0",
        "zip_path": "PassGPTv2/model_passgptv2_us.zip",
        "extract_path": "PassGPTv2/model/model_passgptv2_us",
        "required_files": ["model_passgptv2_us"]
    },
    {
        "name": "PassGPTv2_Malaysia",
        "url": "https://drive.google.com/uc?id=1OgVHnRrU5B1S-rzJZvMqily5w3MEqLkD",
        "zip_path": "PassGPTv2/model_passgptv2_malaysia.zip",
        "extract_path": "PassGPTv2/model/model_passgptv2_malaysia",
        "required_files": ["model_passgptv2_malaysia"]
    },
        {
        "name": "PassGPTv2_Indonesia", 
        "url": "https://drive.google.com/uc?id=1MSzqaxrc26XuxpzsdjkBtK48YVVJGe_l",
        "zip_path": "PassGPTv2/model_passgptv2_indo.zip",
        "extract_path": "PassGPTv2/model/model_passgptv2_indo",
        "required_files": ["model_passgptv2_indo"]
    }
]

def download_file(url, filename):
    print(f"🚀 Downloading {filename} from Google Drive...")
    gdown.download(url, filename, quiet=False, fuzzy=True)

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
#if not torch.cuda.is_available():
 #   print("CUDA (GPU) không khả dụng. Vui lòng kiểm tra lại cài đặt.")
  #  print("Thoát chương trình ...")
   # sys.exit(1)  # Thoát chương trình với mã lỗi 1
#else:
 #   print("CUDA (GPU) đã được kích hoạt.")
  #  if torch.cuda.is_available():
   #     print("Tên GPU:", torch.cuda.get_device_name(0))
download_model()


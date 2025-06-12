import os

input_path = "configs/rockyou.txt"  # Thay bằng args.train_data_path nếu dùng tham số
output_path = "configs/clean_rockyou.txt"

# Đọc bằng encoding 'latin-1' để tránh lỗi ký tự, sau đó ghi lại bằng 'utf-8'
with open(input_path, 'r', encoding='latin-1') as infile:
    lines = [line.strip() for line in infile if line.strip()]

# Kiểm tra số dòng hợp lệ
print(f"✅ Số dòng mật khẩu hợp lệ: {len(lines)}")

if not lines:
    raise ValueError("❌ File không chứa dòng hợp lệ.")

# Ghi ra file mới dưới dạng utf-8
with open(output_path, 'w', encoding='utf-8') as outfile:
    for line in lines:
        outfile.write(line + '\n')

print(f"✅ Đã ghi {len(lines)} dòng sang file: {output_path}")

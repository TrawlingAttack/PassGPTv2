# Đọc tệp với mã hóa hiện tại (ví dụ ISO-8859-1)
with open('./configs/rockyou.txt', 'r', encoding='ISO-8859-1') as file:
    content = file.read()

# Ghi lại nội dung tệp dưới dạng UTF-8
with open('./configs/rockyou_utf8.txt', 'w', encoding='utf-8') as file:
    file.write(content)

print("Tệp đã được chuyển đổi sang UTF-8 thành công!")
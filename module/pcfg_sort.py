import os
import string
from PCFG.password_scorer import list_password_scorer

def is_printable_ascii(s):
    return all(c in string.printable and not c in '\x0b\x0c' for c in s)

def analyze_password_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]

        if not passwords:
            print("File không chứa dòng nào hoặc không phải danh sách mật khẩu.")
            return

        name = os.path.splitext(os.path.basename(filepath))[0]
        size = os.path.getsize(filepath)
        num_passwords = len(passwords)
        num_unique = len(set(passwords))
        num_printable = sum(1 for pwd in passwords if is_printable_ascii(pwd))
        # Lấy đường dẫn tuyệt đối
        return {
            "name": name,
            "size": size,
            "num_passwords": num_passwords,
            "num_unique": num_unique,
            "num_printable": num_printable,
            "list_pass_data": passwords  # hoặc path tương đối như: f"/uploads/{filename}"
        }
    except FileNotFoundError:
        print("Không tìm thấy file.")
    except Exception as e:
        print(f"Lỗi: {e}")
def choose_top_password(list_password_file,value_top,socketio):
    # Gọi hàm lấy danh sách mật khẩu đã được sắp xếp theo score giảm dần
    list_password,list_scorer = list_password_scorer(list_password_file,socketio)

    # Tính số lượng tương ứng với value_top %
    num_top = int(len(list_password) * (value_top / 100.0))

    # Cắt danh sách để lấy value_top %
    top_passwords = list_password[:num_top]

    return top_passwords,list_scorer




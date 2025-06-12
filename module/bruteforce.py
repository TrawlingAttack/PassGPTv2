import subprocess
import tempfile
import os
import time
from module.guessfuse import guessfuse
from datetime import datetime

def print_john():  
    print(r"""     _       _             _   _                 _                    """)
    print(r"""    | | ___ | |__  _ __   | |_| |__   ___   _ __(_)_ __  _ __   ___ _ __ """)
    print(r""" _  | |/ _ \| '_ \| '_ \  | __| '_ \ / _ \ | '__| | '_ \| '_ \ / _ \ '__|""")
    print(r"""| |_| | (_) | | | | | | | | |_| | | |  __/ | |  | | |_) | |_) |  __/ |   """)
    print(r""" \___/ \___/|_| |_|_| |_|  \__|_| |_|\___| |_|  |_| .__/| .__/ \___|_|   """)
    print(r"""                                                  |_|   |_|              """)
def print_hash():
    print(" _   _           _               _   ")
    print("| | | | __ _ ___| |__   ___ __ _| |_ ")
    print("| |_| |/ _` / __| '_ \ / __/ _` | __|")
    print("|  _  | (_| \__ \ | | | (_| (_| | |_ ")
    print("|_| |_|\__,_|___/_| |_|\___\__,_|\__|")
class John_the_ripper():
    def __init__(self,list_hash,list_pass_file,algorithm, mask=None):
        self.list_pass_file = list_pass_file
        self.list_hash = list_hash
        self.algorithm = algorithm
        self.mask = mask



    def main(self):
        print_john()
        if len(self.list_pass_file) > 1:
            list_pass = guessfuse(self.list_pass_file)
        else:
            list_pass = self.list_pass_file[0] if self.list_pass_file else []

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as hash_file, \
            tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as wordlist_file:

            hash_file_path = hash_file.name
            wordlist_file_path = wordlist_file.name

            for h in self.list_hash:
                hash_file.write(h.strip() + '\n')
            hash_file.flush()

            for p in list_pass:
                wordlist_file.write(p.strip() + '\n')
            wordlist_file.flush()

        try:
            if self.mask:
                command = [
                    "john",
                    hash_file_path,
                    f"--mask={self.mask}",
                    f"--format=Raw-{self.algorithm}"
                ]
            else:
                command = [
                    "john",
                    hash_file_path,
                    f"--wordlist={wordlist_file_path}",
                    f"--format=Raw-{self.algorithm}"
                ]

            print(f"[+] Running: {' '.join(command)}", flush=True)

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8'  # <- thêm dòng này
            )

            for line in process.stdout:
                print(line.strip(), flush=True)

            process.stdout.close()
            process.wait()

            print("[+] The hashes have been decoded:", flush=True)

            result = subprocess.run(
                ["john", "--show", hash_file_path, f"--format=Raw-{self.algorithm}"],
                capture_output=True,
                text=True,
                encoding='utf-8'  # <- thêm dòng này
            )

            cracked = result.stdout.strip().splitlines()
            total_hash = len([h for h in self.list_hash if h.strip()])
            cracked_count = 0

            for line in cracked:
                if ':' in line:
                    parts = line.split(':')
                    password = parts[1].strip()
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cracked_count += 1
                    remaining = total_hash - cracked_count

                    print(f"- {password} | {timestamp}", flush=True)
                    print(f"[CRACKED] {password} | {timestamp}", flush=True)
                    print(f"[INFO] Remaining: {remaining}", flush=True)

        except Exception as e:
            print(f"[ERROR] Error: {e}", flush=True)

        finally:
            os.remove(hash_file_path)
            os.remove(wordlist_file_path)
            print("[DONE]", flush=True)

        return list_pass

class Hashcat():
    def __init__(self,list_hash,list_pass_file,algorithm, mask=None):
        self.list_pass_file = list_pass_file
        self.list_hash = list_hash
        self.algorithm = algorithm
        self.mask = mask
    
    def main(self):
        print_hash()
        if len(self.list_pass_file) > 1:
            list_pass = guessfuse(self.list_pass_file)
        else:
            list_pass = self.list_pass_file[0] if self.list_pass_file else []

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as hash_file, \
            tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as wordlist_file:

            hash_file_path = hash_file.name
            wordlist_file_path = wordlist_file.name

            for h in self.list_hash:
                hash_file.write(h.strip() + '\n')
            hash_file.flush()

            for p in list_pass:
                wordlist_file.write(p.strip() + '\n')
            wordlist_file.flush()

        try:
            # Bản đồ đơn giản hashcat mode
            hashcat_modes = {
                "MD5": "0",
                "SHA1": "100",
                "SHA256": "1400",
                "SHA512": "1700"
                # có thể mở rộng thêm
            }

            mode = hashcat_modes.get(self.algorithm.upper())
            if not mode:
                raise ValueError(f"Unsupported algorithm: {self.algorithm}")

            command = [
                "hashcat",
                "-m", mode,
                "-a", "0",  # attack mode 0 = wordlist
                hash_file_path,
                wordlist_file_path,
                "--quiet",  # tránh log quá nhiều
                "--force"   # tắt một số cảnh báo nếu cần (không khuyến khích production)
            ]

            print(f"[+] Running: {' '.join(command)}", flush=True)

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                text=True,
                encoding='utf-8'
            )

            for line in process.stdout:
                print(line.strip(), flush=True)

            process.stdout.close()
            process.wait()

            print("[+] The hashes have been processed by Hashcat", flush=True)

            # Giải mã: chạy lại với --show để lấy kết quả
            show_command = [
                "hashcat",
                "-m", mode,
                "--show",
                hash_file_path
            ]

            result = subprocess.run(
                show_command,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            cracked = result.stdout.strip().splitlines()
            total_hash = len([h for h in self.list_hash if h.strip()])
            cracked_count = 0

            for line in cracked:
                if ':' in line:
                    parts = line.split(':')
                    password = parts[1].strip()
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cracked_count += 1
                    remaining = total_hash - cracked_count

                    print(f"- {password} | {timestamp}", flush=True)
                    print(f"[CRACKED] {password} | {timestamp}", flush=True)
                    print(f"[INFO] Remaining: {remaining}", flush=True)

        except Exception as e:
            print(f"[ERROR] Error: {e}", flush=True)

        finally:
            os.remove(hash_file_path)
            os.remove(wordlist_file_path)
            print("[DONE]", flush=True)

        return list_pass



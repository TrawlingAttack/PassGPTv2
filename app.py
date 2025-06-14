import os
from flask import Flask, json, render_template, request, Response, send_file, jsonify
from flask_socketio import SocketIO
import traceback
import threading
import queue
import sys
import psutil
import cpuinfo
import GPUtil
from check_run import *
from datetime import datetime
from module.generate_file import Generate_Model
from werkzeug.utils import secure_filename 
from module.pcfg_sort import *
from module.bruteforce import *

# Configure
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép kết nối từ mọi nguồn
log_queue = queue.Queue()
# Redirect stdout để đưa log vào Queue
class StreamToQueue:
    def __init__(self, queue):
        self.queue = queue

    def write(self, message):
        if message.strip():  # Bỏ qua dòng trống
            self.queue.put(message)

    def flush(self):
        pass  # Không làm gì cả
# Streaming response generator
def generate_log_stream():
    while True:
        try:
            message = log_queue.get(timeout=1)
            yield f"data: {message}\n\n"
            if "[DONE]" in message:
                break
        except queue.Empty:
            continue

#sys.stderr = StreamToQueue(log_queue)  # Thêm dòng này
sys.stderr = StreamToQueue(log_queue)
# Fake task để ghi log
@app.route('/stream')
def stream():
    return Response(generate_log_stream(), content_type='text/event-stream')



# #########                                             DASHBOARD                                           ############################
@app.route("/")
def main():
    # Lấy thông tin CPU, RAM, GPU
    # Get CPU model name using cpuinfo
    info = cpuinfo.get_cpu_info()
    cpu_name = info.get('brand_raw', 'Unknown CPU')

    # Get total RAM in GB
    ram = psutil.virtual_memory()
    ram_gb = ram.total / (1024 ** 3)  # Convert bytes to GB
    ram_name = f"{ram_gb:.2f} GB RAM"

    # Get GPU names using GPUtil
    gpus = GPUtil.getGPUs()
    if gpus:
        # Join all GPU names if multiple
        gpu_name = ', '.join(gpu.name for gpu in gpus)
    else:
        gpu_name = 'No GPU detected'
    return render_template('index.html', cpu_name=cpu_name, ram_name=ram_name, gpu_name=gpu_name)




# #########                                             GENERATION PASSWORD                                 ############################
# Queue để lưu log

list_pass = []

# Generate_password
@app.route("/index1.html")
def index1():
    return render_template('index1.html')


# ==== Thread Wrapper ====
def run_generation_thread(instance):
    global list_pass
    list_pass = instance.main()

stop_flag = threading.Event()

def run_generation(model_generate):
    global stop_flag
    stop_flag.clear()  # Reset cờ khi bắt đầu
    model_generate.generate(stop_flag)  # Truyền cờ vào quá trình generate


@app.route('/input', methods=['POST'])
def input():
    global model
    lenght_pass = request.form.get('maxlength')
    number_pass = request.form.get('maxnum')
    option_model = request.form.get('option')
    list_prefix = request.form.get('list_prefix')
    country = request.form.get('country')  # Lấy giá trị country mới

    if not lenght_pass or not number_pass:
        return json.dumps({"error": "Missing length password or number password"}), 400
    if list_prefix:
        list_prefix = json.loads(list_prefix)
        # Kiểm tra nếu chọn PassGPTv2 thì cần struction
        if option_model == "4" or option_model == "3":
            list_prefix = list([{"prefix":item["prefix"], "struction":item["struction"]} for item in list_prefix])
        else:
            list_prefix = list([item["prefix"] for item in list_prefix])
        sys.stdout = StreamToQueue(log_queue)  # Chuyển stdout vào Queue
        model = int(option_model)
        model_generate = Generate_Model(country,lenght_pass, number_pass, socketio, model, list_prefix)
        threading.Thread(target=run_generation_thread, args=(model_generate,)).start()
        return json.dumps({"status": "success", "logs": ''}), 200

    return json.dumps({"message": "Data received", "data": list_prefix}), 200

@app.route('/download',methods=['GET'])
def download():
    if model == 0:
        file_path = 'PCFG_list_password.txt'
    elif model ==1:
        file_path = 'Omen_list_password.txt'
    elif model ==2:
        file_path = 'PassGAN_list_password.txt'
    elif model ==3:
        file_path = 'PassGPT_list_password.txt'
    elif model ==4:
        file_path = 'PassGPTv2_list_password.txt'
    # Ghi mảng vào tệp văn bản
    with open(file_path, 'w') as file:
        for item in list_pass:
            file.write(f"{item}\n")
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})




# #########                                             SORT COMMON PASSWORD                                 ############################

@app.route("/index2.html")
def index2():
    return render_template('index2.html')


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
@app.route("/analyze", methods=["POST"])
def analyze():
    results = []
    uploaded_files = request.files.getlist("files")
    
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        result = analyze_password_file(save_path)
        results.append(result)

        # Optional: xóa file sau khi xử lý nếu không muốn lưu
        os.remove(save_path)

    return jsonify(results)


@app.route("/start", methods=["POST"])
def start_process():
    try:
        data = request.get_json(force=True)  # ép Flask đọc JSON
        if not data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400

        files = data.get("files", [])
        percent = data.get("percent", None)

        if not isinstance(files, list) or not isinstance(percent, int):
            return jsonify({"status": "error", "message": "Invalid input format"}), 400

        # Gọi hàm xử lý chính
        list_sort_pass, list_score = choose_top_password(files, percent, socketio)

        global list_pass
        list_pass = list_sort_pass

        return jsonify({
            "status": "success",
            "passwords": list_sort_pass[:50],
            "scores": list_score[:50]
        })

    except Exception as e:
        traceback.print_exc()  # in lỗi đầy đủ vào terminal
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/download2',methods=['GET'])
def download_sorted():  # Đổi tên tránh trùng
    file_path = "list_sorted_pass_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".txt"
    # Ghi mảng vào tệp văn bản
    with open(file_path, 'w') as file:
        for item in list_pass:
            file.write(f"{item}\n")
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})


#list_prefix = [{"ducminh","L7N6"}]
# Run(10,100,socketio,list_prefix)
# run_generate = Generate_Model(22,100,socketio, int('4'), [{"prefix":"ducminh", "struction": "L7 N6"}])
# list_new_password = run_generate.main()
# #########                                             ATTACK PASSWORD                                 ############################

@app.route('/index3/index3_off.html')
def index3_off():
    return render_template('index3/index3_off.html')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

###           JOHN THE RIPPER
@app.route("/submit", methods=["POST"])
def handle_submit():
    hash_text = request.form.get("hash_text", "").strip()
    mask = request.form.get("mask", "")
    algorithm = request.form.get("algorithm", "")
    list_file = []
    index = 0
    while True:
        content = request.form.get(f"list_file_{index}")
        if content is None:
            break
        list_file.append(content.strip().splitlines())
        index += 1

    hash_file = request.files.get("hash_file")
    list_hashs = ""

    if (not hash_text and not hash_file) or not list_file:
        return Response(json.dumps({"status": "error", "message": "Không hợp lệ, vui lòng nhập đầy đủ thông tin"}), status=400, content_type='application/json')

    if hash_text:
        sys.stdout = StreamToQueue(log_queue)
        list_hashs = [hash_text]
        if not list_hashs:
            return Response(json.dumps({"status": "error", "message": "File không chứa mật khẩu hợp lệ"}), status=400, content_type='application/json')
        sys.stdout = StreamToQueue(log_queue)
        progress_attack = John_the_ripper(list_hashs,list_file,algorithm,mask)
        threading.Thread(target=run_generation_thread, args=(progress_attack,)).start()
        return Response(json.dumps({"status": "success", "logs": ""}), status=200, content_type='application/json')

    if hash_file and hash_file.filename.endswith(".txt"):
        save_path = os.path.join(UPLOAD_FOLDER, hash_file.filename)
        hash_file.save(save_path)
        try:
            with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
                list_hashs = [line.strip() for line in f if line.strip()]
            if not list_hashs:
                return Response(json.dumps({"status": "error", "message": "File không chứa mật khẩu hợp lệ"}), status=400, content_type='application/json')
        except FileNotFoundError:
            return Response(json.dumps({"status": "error", "message": "Không tìm thấy file đã upload"}), status=400, content_type='application/json')
        os.remove(save_path)
        sys.stdout = StreamToQueue(log_queue)
        progress_attack = John_the_ripper(list_hashs,list_file,algorithm,mask)
        threading.Thread(target=run_generation_thread, args=(progress_attack,)).start()
        return Response(json.dumps({"status": "success", "logs": ""}), status=200, content_type='application/json')

    elif hash_file:
        return Response(json.dumps({"status": "error", "message": "File không đúng định dạng .txt"}), status=400, content_type='application/json')

    return Response(json.dumps({"status": "error", "message": "Dữ liệu không hợp lệ"}), status=400, content_type='application/json')

###         HASHCAT

@app.route("/submit_hashcat", methods=["POST"])
def handle_submit_hashcat():
    hash_text = request.form.get("hash_text", "").strip()
    mask = request.form.get("mask", "")
    algorithm = request.form.get("algorithm", "")
    list_file = []
    index = 0
    while True:
        content = request.form.get(f"list_file_{index}")
        if content is None:
            break
        list_file.append(content.strip().splitlines())
        index += 1

    hash_file = request.files.get("hash_file")
    list_hashs = ""

    if (not hash_text and not hash_file) or not list_file:
        return Response(json.dumps({"status": "error", "message": "Không hợp lệ, vui lòng nhập đầy đủ thông tin"}), status=400, content_type='application/json')

    if hash_text:
        sys.stdout = StreamToQueue(log_queue)
        list_hashs = [hash_text]
        if not list_hashs:
            return Response(json.dumps({"status": "error", "message": "File không chứa mật khẩu hợp lệ"}), status=400, content_type='application/json')
        sys.stdout = StreamToQueue(log_queue)
        progress_attack = Hashcat(list_hashs,list_file,algorithm,mask)
        threading.Thread(target=run_generation_thread, args=(progress_attack,)).start()
        return Response(json.dumps({"status": "success", "logs": ""}), status=200, content_type='application/json')

    if hash_file and hash_file.filename.endswith(".txt"):
        save_path = os.path.join(UPLOAD_FOLDER, hash_file.filename)
        hash_file.save(save_path)
        try:
            with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
                list_hashs = [line.strip() for line in f if line.strip()]
            if not list_hashs:
                return Response(json.dumps({"status": "error", "message": "File không chứa mật khẩu hợp lệ"}), status=400, content_type='application/json')
        except FileNotFoundError:
            return Response(json.dumps({"status": "error", "message": "Không tìm thấy file đã upload"}), status=400, content_type='application/json')
        os.remove(save_path)
        sys.stdout = StreamToQueue(log_queue)
        progress_attack = Hashcat(list_hashs,list_file,algorithm,mask)
        threading.Thread(target=run_generation_thread, args=(progress_attack,)).start()
        return Response(json.dumps({"status": "success", "logs": ""}), status=200, content_type='application/json')

    elif hash_file:
        return Response(json.dumps({"status": "error", "message": "File không đúng định dạng .txt"}), status=400, content_type='application/json')

    return Response(json.dumps({"status": "error", "message": "Dữ liệu không hợp lệ"}), status=400, content_type='application/json')

@app.route('/index3/index3_on.html')
def index3_on():
    return render_template('index3/index3_on.html')



if __name__ == "__main__":
    print("Please run localhost: http://127.0.0.1:5000")
    socketio.run(app, host='0.0.0.0', port=5000)

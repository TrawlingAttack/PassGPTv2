import os
from flask import Flask, json, render_template, request, Response, send_file, jsonify
from flask_socketio import SocketIO
import threading
import queue
import sys
from datetime import datetime
from check_run import *
from module.generate_file import Generate_Model
from werkzeug.utils import secure_filename
from module.pcfg_sort import *

# Configure
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép kết nối từ mọi nguồn

# #########                                             GENERATION PASSWORD                                 ############################
# Queue để lưu log
log_queue = queue.Queue()
list_pass = []


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
            yield f"data: {message}\n\n"  # Định dạng cho EventSource
        except queue.Empty:
            pass

#sys.stderr = StreamToQueue(log_queue)  # Thêm dòng này
sys.stderr = StreamToQueue(log_queue)
# Fake task để ghi log
@app.route('/stream')
def stream():
    return Response(generate_log_stream(), content_type='text/event-stream')

# Generate_password
@app.route("/")
def main():
    return render_template('index.html')


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

    if not lenght_pass or not number_pass:
        return json.dumps({"error": "Missing length password or number password"}), 400
    if list_prefix:
        list_prefix = json.loads(list_prefix)
        # Kiểm tra nếu chọn PassGPTv2 thì cần struction
        if option_model == "4":
            list_prefix = list([{"prefix":item["prefix"], "struction":item["struction"]} for item in list_prefix])
        else:
            list_prefix = list([item["prefix"] for item in list_prefix])
        sys.stdout = StreamToQueue(log_queue)  # Chuyển stdout vào Queue
        model = int(option_model)
        model_generate = Generate_Model(lenght_pass, number_pass, socketio, model, list_prefix)
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
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    files = data.get("files", [])
    percent = data.get("percent", None)

    list_sort_pass, list_score = choose_top_password(files, percent, socketio)
    global list_pass
    list_pass = list_sort_pass
    return jsonify({
        "status": "success",
        "passwords": list_sort_pass[:50],
        "scores": list_score[:50]
    })

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
print("Please run localhost: http://127.0.0.1:5000")
socketio.run(app, debug=True)
#list_prefix = [{"ducminh","L7N6"}]
# Run(10,100,socketio,list_prefix)
# run_generate = Generate_Model(22,100,socketio, int('4'), [{"prefix":"ducminh", "struction": "L7 N6"}])
# list_new_password = run_generate.main()
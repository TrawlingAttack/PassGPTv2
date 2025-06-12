const analyzedFiles = []; // Mảng lưu kết quả các file
let currentPage = 1;
const itemsPerPage = 4;
const btn_start = document.getElementById("startBtn");
updateStartButtonState();
function renderTable(page) {
    console.log(analyzedFiles);
    const tableBody = document.querySelector("table tbody");
    tableBody.innerHTML = "";
  
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageItems = analyzedFiles.slice(start, end);
  
    pageItems.forEach((fileInfo, index) => {
      const actualIndex = start + index; // Vị trí thật trong mảng chính
      const row = `
        <tr>
          <td class="text-center">${actualIndex + 1}</td>
          <td class="text-center">${fileInfo.name}</td>
          <td class="text-center">${fileInfo.size}</td>
          <td class="text-center">${fileInfo.num_passwords}</td>
          <td class="text-center">${fileInfo.num_unique}</td>
          <td class="text-center">${fileInfo.num_printable}</td>
          <td>
            <button type="button" class="btn btn-block btn-danger" data-index="${actualIndex}">Delete</button>
          </td>
        </tr>
      `;
      tableBody.innerHTML += row;
    });
  
    renderPagination();
  
    // Gắn sự kiện Delete sau khi bảng đã được render xong
    const deleteButtons = document.querySelectorAll(".btn-danger");
    deleteButtons.forEach(btn => {
      btn.addEventListener("click", function () {
        const indexToDelete = parseInt(this.getAttribute("data-index"));
        analyzedFiles.splice(indexToDelete, 1); // Xóa khỏi mảng
  
        // Cập nhật trang hiện tại nếu cần (nếu đang ở trang cuối mà xóa hết thì lui lại)
        const totalPages = Math.ceil(analyzedFiles.length / itemsPerPage);
        if (currentPage > totalPages) {
          currentPage = totalPages;
        }
  
        renderTable(currentPage);
        updateStartButtonState();
      });
    });
  }
  

function renderPagination() {
    const totalPages = Math.ceil(analyzedFiles.length / itemsPerPage);
    const pagination = document.querySelector(".pagination");
    pagination.innerHTML = "";
  
    const prev = `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">&laquo;</a>
                  </li>`;
    pagination.innerHTML += prev;
  
    for (let i = 1; i <= totalPages; i++) {
      const active = i === currentPage ? 'active' : '';
      pagination.innerHTML += `
        <li class="page-item ${active}">
          <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
        </li>
      `;
    }
  
    const next = `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">&raquo;</a>
                  </li>`;
    pagination.innerHTML += next;
  }
  
  function changePage(page) {
    const totalPages = Math.ceil(analyzedFiles.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderTable(currentPage);
    updateStartButtonState();

}
function updateStartButtonState() {
  if (analyzedFiles.length === 0) {
    btn_start.className = "btn btn-block btn-success btn-lg";
    btn_start.innerText = "START";
    btn_start.disabled = true;
  } else {
    btn_start.className = "btn btn-block btn-success btn-lg";
    btn_start.innerText = "START";
    btn_start.disabled = false;
  }
}

const overlay = document.getElementById("overlay"); 

document.getElementById("chooseFilesBtn").addEventListener("click", function () {
    document.getElementById("customFile").click();
  });
  
  document.getElementById("customFile").addEventListener("change", function (event) {
    const files = event.target.files;
    const fileError = document.getElementById("fileError");
    const tableBody = document.querySelector("table tbody");
    overlay.style.display = "flex";
    fileError.textContent = ""; // Reset lỗi
  
    if (!files.length) {
      overlay.style.display = "none";
      fileError.textContent = "No file selected!";
      return;
    }
  
    // Kiểm tra tính hợp lệ
    for (let file of files) {
      if (!file.name.endsWith(".txt")) {
        overlay.style.display = "none";
        fileError.textContent = "Only .txt files are allowed!";
        return;
      }
    }
  
    // Tạo FormData và gửi qua Flask
    const formData = new FormData();
    for (let file of files) {
      formData.append("files", file);
    }
  
    fetch("/analyze", {
        method: "POST",
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          // Thêm kết quả mới vào danh sách
          analyzedFiles.push(...data);
      
          // Cập nhật trang hiện tại là trang cuối cùng
          currentPage = Math.ceil(analyzedFiles.length / itemsPerPage);
          overlay.style.display = "none";
          // Cập nhật bảng và phân trang
          renderTable(currentPage);
          updateStartButtonState();
        })
        .catch((err) => {
          overlay.style.display = "none";
          fileError.textContent = "Error uploading or analyzing files.";
          console.error(err);
        });
  });

const rangeInput = document.getElementById("customRange1");
const rangeValue = document.getElementById("rangeValue");

  // Cập nhật giá trị ban đầu
rangeValue.textContent = rangeInput.value + "%";

rangeInput.addEventListener("input", function () {
rangeValue.textContent = this.value + "%";
    // console.log("Giá trị phần trăm hiện tại:", this.value); // Nếu muốn debug
});



let passwords = [];  // mảng mật khẩu
let scores = [];     // mảng điểm số
let currentPasswordPage = 1;
const passwordsPerPage = 10;

function renderPasswordTable(page) {
  const scrollY = window.scrollY;  // ⬅️ lưu vị trí cuộn
  const tbody = document.getElementById("passwordTableBody");
  tbody.innerHTML = "";

  const start = (page - 1) * passwordsPerPage;
  const end = start + passwordsPerPage;

  for (let i = start; i < end && i < passwords.length; i++) {
    const row = `
      <tr>
        <td class="text-center">${i + 1}</td>
        <td class="text-center">${passwords[i]}</td>
        <td class="text-center">${scores[i]}</td>
      </tr>
    `;
    tbody.innerHTML += row;
  }

  renderPasswordPagination();

  // ✅ Chỉ scroll lại sau khi bảng và phân trang đã render xong
  window.scrollTo({ top: scrollY, behavior: "auto" });
}


function renderPasswordPagination() {
  const scrollY = window.scrollY;
  const totalPages = Math.ceil(passwords.length / passwordsPerPage);
  const pagination = document.getElementById("pagination_toppassword");
  pagination.innerHTML = "";

  const prev = `<li class="page-item ${currentPasswordPage === 1 ? 'disabled' : ''}">
                  <a class="page-link" href="#" data-page="${currentPasswordPage - 1}">&laquo;</a>
                </li>`;
  pagination.innerHTML += prev;

  for (let i = 1; i <= totalPages; i++) {
    const active = i === currentPasswordPage ? 'active' : '';
    pagination.innerHTML += `
      <li class="page-item ${active}">
        <a class="page-link" href="#" data-page="${i}">${i}</a>
      </li>
    `;
  }

  const next = `<li class="page-item ${currentPasswordPage === totalPages ? 'disabled' : ''}">
                  <a class="page-link" href="#" data-page="${currentPasswordPage + 1}">&raquo;</a>
                </li>`;
  pagination.innerHTML += next;

  // Thêm event listener sau khi render
  const pageLinks = pagination.querySelectorAll(".page-link");
  pageLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();  // ✅ Ngăn cuộn đầu trang
      const page = parseInt(link.dataset.page);
      if (!isNaN(page)) changePasswordPage(page);
    });
  });

  window.scrollTo({ top: scrollY, behavior: "auto" });
}


function changePasswordPage(page) {
  const totalPages = Math.ceil(passwords.length / passwordsPerPage);
  if (page < 1 || page > totalPages) return;
  currentPasswordPage = page;
  renderPasswordTable(page);
}

const socket = io();  // Kết nối mặc định
const progressContainer = document.querySelector(".progress");  // Thẻ chứa progress bar
const progressBar = document.getElementById("progress-bar");    // Thẻ progress-bar bên trong

// Khi kết nối thành công
socket.on("connect", () => {
    console.log("🟢 Connected to server via SocketIO");
});

// Nhận dữ liệu cập nhật tiến độ
socket.on("progress_update", (data) => {
  const progress = data.progress;
  const current = data.current;
  const total = data.total;

  progressContainer.style.display = "block";

  progressBar.style.width = `${progress}%`;
  progressBar.setAttribute("aria-valuenow", progress);

  // ✅ Cập nhật dạng: "45% - 23 / 50"
  progressBar.innerHTML = `${Math.floor(progress)}% - ${current} / ${total}`;

  if (progress >= 100) {
      setTimeout(() => {
          progressBar.innerHTML = `Completed`;
      }, 300);

      setTimeout(() => {
          progressContainer.style.display = "none";
          progressBar.style.width = "0%";
          progressBar.setAttribute("aria-valuenow", 0);
      }, 1500);

      btn_start.className = "btn btn-block btn-success btn-lg";
      btn_start.innerText = "START";
      btn_start.disabled = false;
  }
});


socket.on("disconnect", () => {
    console.log("🔴 Disconnected from server");
});


document.querySelector(".btn-success.btn-lg").addEventListener("click", function (event) {
  event.preventDefault(); // ⛔ Ngăn form bị submit gây reload trang
  // Ẩn progress & reset trước khi gửi request
  progressContainer.style.display = "none";
  progressBar.style.width = "0%";
  progressBar.setAttribute("aria-valuenow", 0);
  progressBar.innerHTML = "";
  btn_start.className = "btn btn-block btn-warning btn-lg";
  btn_start.innerText = "LOADING..";
  btn_start.disabled = true;
  const scrollY = window.scrollY;
  const percent = parseInt(document.getElementById("customRange1").value);
  const filePaths = analyzedFiles.map(f => f.list_pass_data);

  fetch("/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ files: filePaths, percent: percent })
  })
    .then(async (res) => {
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await res.text();
        console.error("❌ Không phải JSON:", text);
        throw new Error("Phản hồi không phải JSON!");
      }
      return res.json();
    })
    .then((data) => {
      console.log("✅ Dữ liệu trả về từ server:", data);
      passwords = data.passwords || [];
      scores = data.scores || [];
      currentPasswordPage = 1;
      renderPasswordTable(currentPasswordPage);

      window.scrollTo({ top: scrollY, behavior: "auto" });
    })
    .catch((err) => {
      console.error("Lỗi gửi dữ liệu START:", err);
    });
});

$('#downloadButton').click(function () {
  window.location.href = '/download2'; // chỉ cần gọi 1 lần
});


  

  
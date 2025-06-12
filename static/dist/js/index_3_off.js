const analyzedFiles = []; // Mảng lưu kết quả các file
let currentPage = 1;
const itemsPerPage = 4;
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
      });
    });
  }
  

function renderPagination() {
    const totalPages = Math.ceil(analyzedFiles.length / itemsPerPage);
    const pagination = document.querySelector(".pagination");
    pagination.innerHTML = "";
  
    const prev = `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${currentPage-1}">&laquo;</a>
                  </li>`;
    pagination.innerHTML += prev;
  
    for (let i = 1; i <= totalPages; i++) {
      const active = i === currentPage ? 'active' : '';
      pagination.innerHTML += `
        <li class="page-item ${active}">
          <a class="page-link" href="#" data-page="${i}">${i}</a>
        </li>
      `;
    }
  
    const next = `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${currentPage+1}">&raquo;</a>
                  </li>`;
    pagination.innerHTML += next;
    const pageLinks = document.querySelectorAll(".page-link");
    pageLinks.forEach(link => {
      link.addEventListener("click", function (e) {
        e.preventDefault(); // ❌ Ngăn chuyển trang cuộn lên đầu
        const targetPage = parseInt(this.getAttribute("data-page"));
        if (!isNaN(targetPage)) {
          changePage(targetPage);
        }
      });
    });
}
  
function changePage(page) {
    const totalPages = Math.ceil(analyzedFiles.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderTable(currentPage);
}

const overlay = document.getElementById("overlay_hashcat"); 
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
        })
        .catch((err) => {
          fileError.textContent = "Error uploading or analyzing files.";
          console.error(err);
        });
  });



document.getElementById("struction").addEventListener("focus", () => {
    document.getElementById("passwordOverlay").style.display = "flex";
});
  
  // Đóng khi click vào dấu X
document.getElementById("closeCard").addEventListener("click", () => {
    document.getElementById("passwordOverlay").style.display = "none";
});
  
  // Đóng khi click ra ngoài card
document.getElementById("passwordOverlay").addEventListener("click", (e) => {
    if (e.target === document.getElementById("passwordOverlay")) {
      document.getElementById("passwordOverlay").style.display = "none";
    }
});

let structure = [];

function addComponent() {
  const typeSelect = document.getElementById("typeSelect");
  const quantityInput = document.getElementById("quantityInput");

  if (!typeSelect || !quantityInput) return;

  const type = typeSelect.value;
  const quantity = parseInt(quantityInput.value);

  if (isNaN(quantity) || quantity <= 0) return;

  const last = structure[structure.length - 1];
  if (last && last.type === type) {
    last.quantity += quantity;
  } else {
    structure.push({ type, quantity });
  }

  renderStructure();
}

function removeComponent(index) {
  if (index >= 0 && index < structure.length) {
    structure.splice(index, 1);
    renderStructure();
  }
}

function renderStructure() {
  const box = document.getElementById("structureBox");
  if (!box) return;
  
  box.innerHTML = "";

  structure.forEach((item, index) => {
    const el = document.createElement("div");
    el.className = "badge-custom";
    el.innerHTML = `
      <span>${item.quantity} x ${mapLabel(item.type)}</span>
      <button class="btn-close-custom" onclick="removeComponent(${index})">&times;</button>
    `;
    box.appendChild(el);
  });
}

function mapLabel(type) {
    switch (type) {
      case "lower": return "Lowercase";
      case "upper": return "Uppercase";
      case "number": return "Number";
      case "special": return "Special"; // <-- chỉnh từ symbol -> special
      default: return type;
    }
  }
  

function confirmStructure() {
  const structionInput = document.getElementById("struction");
  if (!structionInput) return;

  const codeMap = {
    lower: "L",
    upper: "U",
    number: "N",
    special: "S"
  };

  const result = structure.map(item => {
    const code = codeMap[item.type] || "?";
    const qty = parseInt(item.quantity);
    return isNaN(qty) ? "" : `${code}${qty}`;
  }).join(" ");

  structionInput.value = result.trim();
}

// Phan input parameter vao va xu ly start
const hashInput = document.querySelector('input[placeholder="Enter the hash ..."]');
const fileInput = document.getElementById("exampleInputFile");
const fileLabel = document.getElementById("fileLabel");
const clearBtn = document.getElementById("clearFileBtn");

// Cập nhật label file khi người dùng chọn file
fileInput.addEventListener("change", function () {
    const fileName = this.files[0] ? this.files[0].name : "Choose file";
    fileLabel.textContent = fileName;
    updateInputStates();
});

// Nút Hủy bỏ
clearBtn.addEventListener("click", function () {
    fileInput.value = ""; // Reset file
    fileLabel.textContent = "Choose file";
    updateInputStates();
});

// Theo dõi người dùng nhập hash
hashInput.addEventListener('input', function () {
    updateInputStates();
});

// Hàm kiểm tra và cập nhật trạng thái disable/enable
function updateInputStates() {
    const hashValue = hashInput.value.trim();
    const fileSelected = fileInput.files.length > 0;

    if (hashValue === '' && !fileSelected) {
        // Nếu cả hai đều rỗng → bật cả hai
        hashInput.disabled = false;
        fileInput.disabled = false;
    } else if (hashValue !== '') {
        // Nếu có nhập hash → disable file
        fileInput.disabled = true;
        hashInput.disabled = false;
    } else if (fileSelected) {
        // Nếu đã chọn file → disable input hash
        hashInput.disabled = true;
        fileInput.disabled = false;
    }
}


const startButton = document.getElementById("submitBtn");


document.getElementById("submitBtn").addEventListener("click", async function () {
  const hashValue = hashInput.value.trim();
  const file = fileInput.files[0];
  const formData = new FormData();
  const maskValue = document.getElementById("struction").value.trim();
  const algorithm = document.getElementById("algorithm").value.trim();
  formData.append("mask", maskValue);
  formData.append("algorithm",algorithm)
  startButton.className = "btn btn-block btn-warning btn-lg";
  startButton.innerText = "LOADING..";
  startButton.disabled = true;
  logArea.innerHTML = "";
  resultArea.innerHTML = "";

  analyzedFiles.forEach((f, index) => {
    const fileData = f.list_pass_data.join("\n");
    formData.append(`list_file_${index}`, fileData);
  });

  if (hashValue !== "") {
    formData.append("hash_text", hashValue);
  } else if (file) {
    formData.append("hash_file", file);
  } else {
    startButton.className = "btn btn-block btn-primary btn-lg";
    startButton.innerText = "START";
    startButton.disabled = false;
    alert("Vui lòng nhập Hash hoặc chọn file hash!");

    return;
  }

  try {
    const response = await fetch("/submit", {
      method: "POST",
      body: formData
    });

    const result = await response.json();
    
    if (!response.ok) {
      startButton.className = "btn btn-block btn-primary btn-lg";
      startButton.innerText = "START";
      startButton.disabled = false;
      alert("Lỗi từ server: " + (result.message || result.error || "Không rõ lỗi"));
      return;
    }

    if (result.status === "success") {
    } else {
      startButton.className = "btn btn-block btn-primary btn-lg";
      startButton.innerText = "START";
      startButton.disabled = false;
      alert("Phản hồi không thành công: " + (result.message || "Không rõ lý do"));
    }

  } catch (error) {
    console.error("Lỗi gửi dữ liệu:", error);
    startButton.className = "btn btn-block btn-primary btn-lg";
    startButton.innerText = "START";
    startButton.disabled = false;
    alert("Đã xảy ra lỗi khi gửi dữ liệu!");
  }
});

// Hashcat

const analyzedFiles_hashcat = []; // Mảng lưu kết quả các file
let currentPage_hashcat = 1;
const itemsPerPage_hashcat = 4;


function renderTable_hashcat(page) {
    console.log(analyzedFiles_hashcat);
    const tableBody_hashcat = document.getElementById("table_hashcat").querySelector("table tbody");
    tableBody_hashcat.innerHTML = "";
  
    const start = (page - 1) * itemsPerPage_hashcat;
    const end = start + itemsPerPage_hashcat;
    const pageItems = analyzedFiles_hashcat.slice(start, end);
   
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
      tableBody_hashcat.innerHTML += row;
    });
  
    renderPagination_hashcat();
  
    // Gắn sự kiện Delete sau khi bảng đã được render xong
    const deleteButtons = document.querySelectorAll(".btn-danger");
    deleteButtons.forEach(btn => {
      btn.addEventListener("click", function () {
        const indexToDelete = parseInt(this.getAttribute("data-index"));
        analyzedFiles_hashcat.splice(indexToDelete, 1); // Xóa khỏi mảng
  
        // Cập nhật trang hiện tại nếu cần (nếu đang ở trang cuối mà xóa hết thì lui lại)
        const totalPages = Math.ceil(analyzedFiles_hashcat.length / itemsPerPage_hashcat);
        if (currentPage_hashcat > totalPages) {
          currentPage_hashcat = totalPages;
        }
  
        renderTable_hashcat(currentPage_hashcat);
      });
    });
  }
  

function renderPagination_hashcat() {
    const totalPages = Math.ceil(analyzedFiles_hashcat.length / itemsPerPage_hashcat);
    const pagination = document.getElementById("page_hashcat");
    pagination.innerHTML = "";
  
    const prev = `<li class="page-item ${currentPage_hashcat === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage_hashcat(${currentPage_hashcat - 1})">&laquo;</a>
                  </li>`;
    pagination.innerHTML += prev;
  
    for (let i = 1; i <= totalPages; i++) {
      const active = i === currentPage_hashcat ? 'active' : '';
      pagination.innerHTML += `
        <li class="page-item ${active}">
          <a class="page-link" href="#" onclick="changePage_hashcat(${i})">${i}</a>
        </li>
      `;
    }
  
    const next = `<li class="page-item ${currentPage_hashcat === totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage_hashcat(${currentPage_hashcat + 1})">&raquo;</a>
                  </li>`;
    pagination.innerHTML += next;
  }
  
  function changePage_hashcat(page) {
    const totalPages = Math.ceil(analyzedFiles_hashcat.length / itemsPerPage_hashcat);
    if (page < 1 || page > totalPages) return;
    currentPage_hashcat = page;
    renderTable_hashcat(currentPage_hashcat);
}

const overlay_hashcat = document.getElementById("overlay_hashcat"); 
document.getElementById("chooseFilesBtn_hashcat").addEventListener("click", function () {
    document.getElementById("customFile_hashcat").click();
  });
  
  document.getElementById("customFile_hashcat").addEventListener("change", function (event) {
    const files = event.target.files;
    const fileError = document.getElementById("fileError_hashcat");
    const tableBody = document.getElementById("table_hashcat");
    overlay_hashcat.style.display = "flex";
    fileError_hashcat.textContent = ""; // Reset lỗi
  
    if (!files.length) {
      overlay_hashcat.style.display = "none";
      fileError_hashcat.textContent = "No file selected!";
      return;
    }
  
    // Kiểm tra tính hợp lệ
    for (let file of files) {
      if (!file.name.endsWith(".txt")) {
        overlay_hashcat.style.display = "none";
        fileError_hashcat.textContent = "Only .txt files are allowed!";
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
          analyzedFiles_hashcat.push(...data);
      
          // Cập nhật trang hiện tại là trang cuối cùng
          currentPage_hashcat = Math.ceil(analyzedFiles_hashcat.length / itemsPerPage_hashcat);
          overlay_hashcat.style.display = "none";
          // Cập nhật bảng và phân trang
          renderTable_hashcat(currentPage_hashcat);
        })
        .catch((err) => {
          fileError_hashcat.textContent = "Error uploading or analyzing files.";
          console.error(err);
        });
  });



document.getElementById("struction_hashcat").addEventListener("focus", () => {
    document.getElementById("passwordOverlay_hashcat").style.display = "flex";
});
  
  // Đóng khi click vào dấu X
document.getElementById("closeCard_hashcat").addEventListener("click", () => {
    document.getElementById("passwordOverlay_hashcat").style.display = "none";
});
  
  // Đóng khi click ra ngoài card
document.getElementById("passwordOverlay_hashcat").addEventListener("click", (e) => {
    if (e.target === document.getElementById("passwordOverlay_hashcat")) {
      document.getElementById("passwordOverlay_hashcat").style.display = "none";
    }
});

let structure_hashcat = [];

function addComponent_hashcat() {
  const typeSelect = document.getElementById("typeSelect_hashcat");
  const quantityInput = document.getElementById("quantityInput_hashcat");

  if (!typeSelect || !quantityInput) return;

  const type = typeSelect.value;
  const quantity = parseInt(quantityInput.value);

  if (isNaN(quantity) || quantity <= 0) return;

  const last = structure_hashcat[structure_hashcat.length - 1];
  if (last && last.type === type) {
    last.quantity += quantity;
  } else {
    structure_hashcat.push({ type, quantity });
  }

  renderStructure_hashcat();
}

function removeComponent_hashcat(index) {
  if (index >= 0 && index < structure_hashcat.length) {
    structure_hashcat.splice(index, 1);
    renderStructure_hashcat();
  }
}

function renderStructure_hashcat() {
  const box = document.getElementById("structureBox_hashcat");
  if (!box) return;
  
  box.innerHTML = "";

  structure_hashcat.forEach((item, index) => {
    const el = document.createElement("div");
    el.className = "badge-custom";
    el.innerHTML = `
      <span>${item.quantity} x ${mapLabel(item.type)}</span>
      <button class="btn-close-custom" onclick="removeComponent_hashcat(${index})">&times;</button>
    `;
    box.appendChild(el);
  });
}

function mapLabel_hashcats(type) {
    switch (type) {
      case "lower": return "Lowercase";
      case "upper": return "Uppercase";
      case "number": return "Number";
      case "special": return "Special"; // <-- chỉnh từ symbol -> special
      default: return type;
    }
  }
  

function confirmStructure_hashcat() {
  const structionInput = document.getElementById("struction_hashcat");
  if (!structionInput) return;

  const codeMap = {
    lower: "L",
    upper: "U",
    number: "N",
    special: "S"
  };

  const result = structure_hashcat.map(item => {
    const code = codeMap[item.type] || "?";
    const qty = parseInt(item.quantity);
    return isNaN(qty) ? "" : `${code}${qty}`;
  }).join(" ");

  structionInput.value = result.trim();
}

// Phan input parameter vao va xu ly start
const hashInput_hashcat = document.getElementById("input_hash");
const fileInput_hashcat = document.getElementById("InputFile_hashcat");
const fileLabel_hashcat = document.getElementById("fileLabel_hashcat");
const clearBtn_hashcat = document.getElementById("clearFileBtn_hashcat");

// Cập nhật label file khi người dùng chọn file
fileInput_hashcat.addEventListener("change", function () {
    const fileName = this.files[0] ? this.files[0].name : "Choose file";
    fileLabel_hashcat.textContent = fileName;
    updateInputStates_hashcat();
});

// Nút Hủy bỏ
clearBtn_hashcat.addEventListener("click", function () {
    fileInput_hashcat.value = ""; // Reset file
    fileLabel_hashcat.textContent = "Choose file";
    updateInputStates_hashcat();
});

// Theo dõi người dùng nhập hash
hashInput_hashcat.addEventListener('input', function () {
    updateInputStates_hashcat();
});

// Hàm kiểm tra và cập nhật trạng thái disable/enable
function updateInputStates_hashcat() {
    const hashValue = hashInput_hashcat.value.trim();
    const fileSelected = fileInput_hashcat.files.length > 0;

    if (hashValue === '' && !fileSelected) {
        // Nếu cả hai đều rỗng → bật cả hai
        hashInput_hashcat.disabled = false;
        fileInput_hashcat.disabled = false;
    } else if (hashValue !== '') {
        // Nếu có nhập hash → disable file
        fileInput_hashcat.disabled = true;
        hashInput_hashcat.disabled = false;
    } else if (fileSelected) {
        // Nếu đã chọn file → disable input hash
        hashInput_hashcat.disabled = true;
        fileInput_hashcat.disabled = false;
    }
}


const startButton_hashcat = document.getElementById("submitBtn_hashcat");


document.getElementById("submitBtn_hashcat").addEventListener("click", async function () {
  const hashValue = hashInput_hashcat.value.trim();
  const file = fileInput_hashcat.files[0];
  const formData = new FormData();
  const maskValue = document.getElementById("struction_hashcat").value.trim();
  const algorithm = document.getElementById("algorithm_hashcat").value.trim();
  formData.append("mask", maskValue);
  formData.append("algorithm",algorithm)
  startButton_hashcat.className = "btn btn-block btn-warning btn-lg";
  startButton_hashcat.innerText = "LOADING..";
  startButton_hashcat.disabled = true;
  logArea.innerHTML = "";
  resultArea.innerHTML = "";

  analyzedFiles_hashcat.forEach((f, index) => {
    const fileData = f.list_pass_data.join("\n");
    formData.append(`list_file_${index}`, fileData);
  });

  if (hashValue !== "") {
    formData.append("hash_text", hashValue);
  } else if (file) {
    formData.append("hash_file", file);
  } else {
    startButton_hashcat.className = "btn btn-block btn-primary btn-lg";
    startButton_hashcat.innerText = "START";
    startButton_hashcat.disabled = false;
    alert("Vui lòng nhập Hash hoặc chọn file hash!");

    return;
  }

  try {
    const response = await fetch("/submit_hashcat", {
      method: "POST",
      body: formData
    });

    const result = await response.json();
    
    if (!response.ok) {
      startButton_hashcat.className = "btn btn-block btn-primary btn-lg";
      startButton_hashcat.innerText = "START";
      startButton_hashcat.disabled = false;
      alert("Lỗi từ server: " + (result.message || result.error || "Không rõ lỗi"));
      return;
    }

    if (result.status === "success") {
    } else {
      startButton_hashcat.className = "btn btn-block btn-primary btn-lg";
      startButton_hashcat.innerText = "START";
      startButton_hashcat.disabled = false;
      alert("Phản hồi không thành công: " + (result.message || "Không rõ lý do"));
    }

  } catch (error) {
    console.error("Lỗi gửi dữ liệu:", error);
    startButton_hashcat.className = "btn btn-block btn-primary btn-lg";
    startButton_hashcat.innerText = "START";
    startButton_hashcat.disabled = false;
    alert("Đã xảy ra lỗi khi gửi dữ liệu!");
  }
});

const logArea = document.getElementById('progress');
const resultArea = document.getElementById('output');
const eventSource = new EventSource('/stream');

eventSource.onmessage = function(event) {
    const data = event.data;

    // Bỏ qua các dòng không cần thiết
    if (
      data.includes('GET') ||
      data.includes('127.0.0.1 - -') ||
      data.includes('" 304 -') ||
      data.includes('404 -')
    ) {
      return;
    }

    // Khi kết thúc
    if (data.includes('[DONE]')) {
      startButton.className = "btn btn-block btn-primary btn-lg";
      startButton.innerText = "START";
      startButton.disabled = false;
      startButton_hashcat.className = "btn btn-block btn-primary btn-lg";
      startButton_hashcat.innerText = "START";
      startButton_hashcat.disabled = false;
      return;
    }

    // Nếu là dòng kết quả CRACKED → ghi vào #output
    if (data.includes("[CRACKED]") || data.includes("[INFO]")) {
      // Tách chuỗi: [CRACKED] password | time
      if(data.includes("[CRACKED]")){
        const match = data.match(/\[CRACKED\]\s+(.+?)\s+\|\s+(.+)/);
        if (match) {
          const password = match[1];
          const timestamp = match[2];

          const crackedLine = `<span style="color: black;">[CRACKED] </span>` +
                        `<span style="color: red;">${password}</span>` +
                        `<span style="color: black;"> | ${timestamp}</span>`;
          resultArea.innerHTML += crackedLine + "<br>";
          resultArea.scrollTop = resultArea.scrollHeight;
        }
      }
      else{
        resultArea.innerHTML += `<span style="color: black;"> ${data}</span>` + "<br>";
        resultArea.scrollTop = resultArea.scrollHeight;
      }
    } else {
      // Còn lại là log → ghi vào #progress
      const logLine = `<span style="color: limegreen;">${data}</span>`;
      logArea.innerHTML += logLine + "<br>";
      logArea.scrollTop = logArea.scrollHeight;
    }
};

   


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
      case "lower": return "chữ thường";
      case "upper": return "chữ hoa";
      case "number": return "số";
      case "special": return "ký tự đb"; // <-- chỉnh từ symbol -> special
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


let dataRows = [];
let list_prefix = [];
const rowsPerPage = 5;
let currentPage = 1;

function checkStruction(prefix, struction) {
  let structionError = document.getElementById('structionError');
  structionError.innerText = ''; // Clear lỗi cũ

  const result = [];
  let currentType = null;
  let currentLength = 0;

  // Tách prefix thành cấu trúc kiểu L5, N2, U3...
  if (prefix.length > 0) {
      for (let i = 0; i < prefix.length; i++) {
          const char = prefix[i];
          let type = null;
          if (/[a-z]/.test(char)) type = 'L';
          else if (/[A-Z]/.test(char)) type = 'U';
          else if (/[0-9]/.test(char)) type = 'N';
          else type = 'S';

          if (type === currentType) {
              currentLength++;
          } else {
              if (currentType !== null) {
                  result.push(currentType + currentLength);
              }
              currentType = type;
              currentLength = 1;
          }
      }

      if (currentType !== null) {
          result.push(currentType + currentLength);
      }
  }

  // Chuyển struction thành mảng tương tự
  const structionArr = struction.trim().split(/\s+/); // VD: ["L5", "N6"]

  // So sánh từng phần tử
  if (result.length > structionArr.length) {
      structionError.innerText = '❌ Không hợp lệ: cấu trúc vượt quá struction!';
      setTimeout(() => {
        structionError.innerText = '';
      }, 1500);
      return false;
  }

  for (let i = 0; i < result.length; i++) {
      const rType = result[i][0];
      const rLen = parseInt(result[i].slice(1));

      const sType = structionArr[i][0];
      const sLen = parseInt(structionArr[i].slice(1));

      if (rType !== sType || rLen > sLen) {
          structionError.innerText = '❌ Không hợp lệ: cấu trúc không khớp!';
          setTimeout(() => {
            structionError.innerText = '';
          }, 1500);
          return false;
      }
  }

  // Nếu hợp lệ
  structionError.innerText = '✅ Hợp lệ, đã thêm điều kiện vào bảng! ';
  setTimeout(() => {
    structionError.innerText = '';
  }, 1500);
  return true;
}

function appendRow() {
  const prefix = document.getElementById("prefix").value.trim();
  const struction = document.getElementById("struction").value.trim();

  if (!prefix && !struction) return;

  // Kiểm tra trùng lặp
  const exists = list_prefix.some(item => item.prefix === prefix && item.struction === struction);
  if (exists) {
    alert("Cặp prefix và struction đã tồn tại!");
    return;
  }

  const newItem = { prefix, struction };
  if (prefix && struction){
    if(!checkStruction(prefix,struction)){
      return;
    };
  }

  dataRows.push(newItem);
  list_prefix.push(newItem);

  // Reset input
  document.getElementById("prefix").value = "";
  document.getElementById("struction").value = "";

  // Chuyển đến trang cuối
  currentPage = Math.ceil(dataRows.length / rowsPerPage);

  renderTable();
  renderPagination();
}

function deleteRow(index) {
  const realIndex = (currentPage - 1) * rowsPerPage + index;

  const deletedItem = dataRows[realIndex];

  dataRows.splice(realIndex, 1);

  // Xóa đúng đối tượng trong list_prefix
  const prefixIndex = list_prefix.findIndex(
    item => item.prefix === deletedItem.prefix && item.struction === deletedItem.struction
  );
  if (prefixIndex !== -1) list_prefix.splice(prefixIndex, 1);

  const maxPage = Math.ceil(dataRows.length / rowsPerPage);
  if (currentPage > maxPage) currentPage = maxPage;

  renderTable();
  renderPagination();
}

function renderTable() {
  const tbody = document.getElementById("tableBody");
  tbody.innerHTML = "";

  const start = (currentPage - 1) * rowsPerPage;
  const end = Math.min(start + rowsPerPage, dataRows.length);

  // Kiểm tra xem option5 có đang được chọn không
  const selectedId = document.querySelector('input[name="options"]:checked')?.value;
  const showStruction = selectedId === '4';

  for (let i = start; i < end; i++) {
    const row = dataRows[i];
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${i + 1}</td>
      <td>${row.prefix}</td>
      ${showStruction ? `<td>${row.struction}</td>` : ""}
      <td>
        <button type="button" class="btn btn-danger btn-sm" onclick="deleteRow(${i - start})">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  }

  // Hiện/ẩn tiêu đề cột Struction trong thead
  const ths = document.querySelectorAll("table thead th");
  if (ths.length >= 3) {
    if (showStruction) {
      ths[2].style.display = "";
    } else {
      ths[2].style.display = "none";
    }
  }
}

function renderPagination() {
  const pagination = document.querySelector(".pagination");
  pagination.innerHTML = "";

  const totalPages = Math.ceil(dataRows.length / rowsPerPage);

  const createPageItem = (label, page, disabled = false) => {
    const li = document.createElement("li");
    li.className = `page-item ${disabled ? "disabled" : ""}`;
    li.innerHTML = `<a class="page-link" href="#">${label}</a>`;
    li.onclick = (e) => {
      e.preventDefault();
      if (!disabled) {
        currentPage = page;
        renderTable();
        renderPagination();
      }
    };
    return li;
  };

  // « Previous
  pagination.appendChild(createPageItem("«", currentPage - 1, currentPage === 1));

  for (let i = 1; i <= totalPages; i++) {
    const li = createPageItem(i, i);
    if (i === currentPage) li.classList.add("active");
    pagination.appendChild(li);
  }

  // » Next
  pagination.appendChild(createPageItem("»", currentPage + 1, currentPage === totalPages));
}

// Gắn sự kiện cho nút Append
document.querySelector(".btn-info.float-right").addEventListener("click", function (e) {
  e.preventDefault();
  appendRow();
});


// Bắt sự kiện radio và cập nhật giao diện
if (document.querySelector('input[name="options"]')) {
  document.querySelectorAll('input[name="options"]').forEach((elem) => {
    elem.addEventListener("change", function (event) {
      const selected = event.target;

      // Cập nhật trạng thái checked và active
      document.querySelectorAll('input[name="options"]').forEach(input => {
        input.checked = false;
        input.parentElement.classList.remove('active');
      });
      selected.checked = true;
      selected.parentElement.classList.add('active');

      const selectedId = selected.value;
      const isOption5 = selectedId === '4';

      const structionInputGroup = document.querySelector('#struction')?.closest('.form-group');
      if (structionInputGroup) {
        structionInputGroup.style.display = isOption5 ? 'flex' : 'none';
      }

      renderTable(); // Gọi lại bảng khi thay đổi radio
    });
  });
}

// Gọi lần đầu để khởi tạo đúng giao diện
document.addEventListener("DOMContentLoaded", () => {
  renderTable();
  renderPagination();
});

let isGenerating = false;
let currentSocket = null;
$(document).ready(function() {
  $('#maxlenght').on('input', function() {
    const value = parseInt($(this).val());
    if (value <= 5 || value >= 20) {
      $('#maxlenght-error').text("Max Lenght phải > 5 và < 20");
    } else {
      $('#maxlenght-error').text("");
    }
  });

  $('#maxnum').on('input', function() {
    const value = parseInt($(this).val());
    if (value <= 5) {
      $('#maxnum-error').text("Max Number phải > 5");
    } else {
      $('#maxnum-error').text("");
    }
  });
});
// Xử lý sự kiện Submit
// Xử lý sự kiện Submit
document.getElementById("submitButton").addEventListener("click", (e) => {
  e.preventDefault();

  const generateButton = document.getElementById("submitButton");
  const downloadButton = document.getElementById("downloadButton");
  const progressBar = document.getElementById("progress-bar");
  const bar = document.querySelector(".progress");
  // Danh sách các hàng cần làm mờ
  const rowsToBlur = document.querySelectorAll(".form-group.row");


  // Bắt đầu quá trình generate
  isGenerating = true;

  // Reset giao diện
  const logArea = document.getElementById("passwordArea");
  logArea.innerHTML = "";
  downloadButton.disabled = true;

  const selectedOption = document.querySelector('input[name="options"]:checked')?.value || "None";
  const maxlength = document.getElementById("maxlenght")?.value;
  const maxnum = document.getElementById("maxnum")?.value;
  // Kiểm tra hợp lệ
  const maxLenInt = parseInt(maxlength);
  const maxNumInt = parseInt(maxnum);

  if (!maxLenInt || !maxNumInt || maxLenInt <= 5 || maxLenInt >= 20 || maxNumInt <= 5) {
    alert("❗ Max Lenght phải > 5 và < 20\n❗ Max Number phải > 5");
    return;  // Không gửi request nếu điều kiện sai
  }

  const data = {
    list_prefix: JSON.stringify(list_prefix),
    option: selectedOption,
    maxlength: maxlength,
    maxnum: maxnum,
  };

  // Kết nối socket và giữ lại để sau này dừng
  const socket = io();
  currentSocket = socket;

  // Gửi dữ liệu đến server
  $.ajax({
    url: "/input",
    type: "POST",
    data: data,
    success: function (response) {
      console.log("📤 Dữ liệu đã gửi thành công:", response);
    },
    error: function (error) {
      console.log("❌ Lỗi khi gửi dữ liệu:", error);
    },
  });

  // Đổi nút thành STOP
  generateButton.className = "btn col-2 btn-warning btn-lg text-mid";
  generateButton.innerText = "LOADING..";
  rowsToBlur.forEach(row => row.classList.add("disabled-blur"));

  // Theo dõi tiến trình
  socket.on("progress_update", function (data) {
    bar.style.display = "block";
  
    const progress = parseFloat(data.progress).toFixed(2);
    progressBar.style.width = progress + "%";
    progressBar.innerText = progress + "%";
    progressBar.style.fontSize = "16px";
    progressBar.style.color = "white";
  
    // Đổi thành nút STOP
    generateButton.className = "btn col-2 btn-warning btn-lg text-mid";
    generateButton.innerText = "LOADING..";

    generateButton.disabled = true; 
    downloadButton.disabled = true;
    progressBar.className = "progress-bar bg-warning progress-bar-striped";
  
    if (progress >= 100 || progress === 0) {
      console.log("✅ Quá trình hoàn tất!");
      isGenerating = false;
      generateButton.className = "btn col-2 btn-success btn-lg text-mid";
      generateButton.innerText = "GENERATE";
      generateButton.disabled = false;
      generateButton.onclick = null; // Gỡ sự kiện STOP để quay lại chức năng submit
      rowsToBlur.forEach(row => row.classList.remove("disabled-blur"));
      downloadButton.disabled = false;
      progressBar.className = "progress-bar bg-primary progress-bar-striped";
      bar.style.display = "none";
    }
  });

  // Nhận batch mật khẩu từ server
  socket.on("new_password_batch", function (data) {
    const list = document.getElementById("passwordArea");
    data.guesses.forEach((password) => {
      const li = document.createElement("li");
      li.textContent = password;
      list.appendChild(li);

      if (list.children.length > 500) {
        list.removeChild(list.firstChild);
      }
    });
  });
});

// Hàm hoàn tất generate
function finishGeneration() {
  const generateButton = document.getElementById("submitButton");
  const downloadButton = document.getElementById("downloadButton");
  const progressBar = document.getElementById("progress-bar");
  const bar = document.querySelector(".progress");

  isGenerating = false;
  currentSocket?.disconnect();
  currentSocket = null;

  generateButton.className = "btn col-2 btn-success btn-lg text-mid";
  generateButton.innerText = "GENERATE";
  generateButton.disabled = false;

  downloadButton.disabled = false;
  progressBar.className = "progress-bar bg-primary progress-bar-striped";
  bar.style.display = "none";
}
jQuery(function($) {
  $('#downloadButton').click(function() {
      $.ajax({
          url: '/download',
          type: 'GET',
          success: function() {
              // Khi nhận phản hồi từ server, tự động tải file
              window.location.href = '/download';
          },
          error: function(error) { 
              console.log(error); 
          }
      });
  });
});

   // Khi có log mới từ server
const logArea = document.getElementById('passwordArea');
const eventSource = new EventSource('/stream');
           // Khi nhận được log từ server
   
eventSource.onmessage = function(event) {
// Lấy ra danh sách các chuỗi prefix để dễ xử lý
const list_prefix_obj = list_prefix.map(item => item.prefix);
if(event.data.includes('GET') ||  event.data.includes('127.0.0.1 - -') || event.data.includes('" 304 -') || event.data.includes('404 -')){
}
else{
  if(event.data.includes('-]')){
    logArea.textContent = ""
  }
  // Xử lý để tô màu cụm từ
  let formattedLine = event.data.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  list_prefix_obj.forEach(prefix => {
// Tô màu đỏ cho các cụm từ khớp
    const regex = new RegExp(`(${prefix})`, 'gi');
    formattedLine = formattedLine.replace(regex, `<span style="color: red;">$1</span>`);
  });
   
  logArea.innerHTML += formattedLine + '<br>';
  logArea.scrollTop = logArea.scrollHeight; // Cuộn xuống cuối  
  }
};
   





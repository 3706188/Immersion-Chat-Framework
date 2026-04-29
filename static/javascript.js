// --- 1. 全域變數定義 ---
let currentPersonaId = "tsundere"; // 預設角色 ID

// --- 2. 輔助函式：文字渲染 (動作渲染) ---
function formatAIResponse(text) {
  if (!text) return "";
  // 處理 *星號動作*
  text = text.replace(/\*(.*?)\*/g, '<span class="action-text">* $1 *</span>');
  // 處理 (括號動作)
  text = text.replace(/\((.*?)\)/g, '<span class="action-text">($1)</span>');
  // 處理 「」 標籤
  text = text.replace(
    /「(.*?)」/g,
    '<strong style="color:#075e54;">「$1」</strong>',
  );
  return text;
}

// --- 3. 被 HTML 呼叫的函式 ---

// 當 DOM (HTML) 載入完成後才執行綁定
document.addEventListener("DOMContentLoaded", () => {
  // 1. 角色卡片點擊
  const cards = document.querySelectorAll(".char-card");
  cards.forEach((card) => {
    card.addEventListener("click", () => {
      // 從 HTML 的 data- 屬性中抓取資料
      const id = card.dataset.id;
      const name = card.dataset.name;
      const avatarUrl = card.dataset.avatar;
      const box = document.getElementById("chat-box");
      selectPersona(id, name, avatarUrl);
    });
  });

  // 2. avatar 點擊（記憶）
  const avatar = document.getElementById("current-avatar");
  avatar.addEventListener("click", showMemory);

  // 3. 記憶按鈕
  const memoryBtn = document.querySelector(".memory-btn");
  memoryBtn.addEventListener("click", showMemory);

  //4. user id change
  const userInput = document.getElementById("user-id-input");
  userInput.addEventListener("change", handleUserChange);

  // 5. 發送訊息
  const sendBtn = document.querySelector(".send-btn");
  sendBtn.addEventListener("click", sendMsg);

  // 6. Enter 鍵發送訊息
  const msgInput = document.getElementById("msg-input");
  msgInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMsg();
    }
  });
});

//切換角色
function selectPersona(id, name, avatarUrl) {
  currentPersonaId = id;
  const displayName = document.getElementById("display-name");
  const currentAvatar = document.getElementById("current-avatar");
  const overlay = document.getElementById("selection-overlay");
  const chatBox = document.getElementById("chat-box");

  if (displayName) displayName.innerText = name;
  if (currentAvatar) {
    currentAvatar.title = `點擊查看${name}對你的記憶`;
    currentAvatar.src = avatarUrl;
  }
  if (chatBox) chatBox.innerHTML = ""; // 切換角色時清空對話框
  if (overlay) overlay.classList.add("hidden");

  // 提示通知
  Swal.fire({
    title: `與 ${name} 的對話開始`,
    timer: 1500,
    showConfirmButton: false,
    toast: true,
    position: "top-end",
    icon: "success",
    background: "#f0f0f0",
  });
}

// B. 查看記憶摘要
async function showMemory() {
  const userId = document.getElementById("user-id-input").value.trim();
  const personaName = document.getElementById("display-name").innerText;

  console.log(`[系統] 正在讀取 ${userId} 對於 ${personaName} 的記憶...`);

  try {
    const response = await fetch(`/memory/${userId}`);
    const data = await response.json();

    Swal.fire({
      title: `${personaName} 的筆記本`,
      html: `<div style="text-align: left; background: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd;">${data.summary || "她目前對你還沒什麼特別的印象..."}</div>`,
      icon: "info",
      confirmButtonColor: "#075e54",
    });
  } catch (error) {
    Swal.fire("錯誤", "目前尚無摘要內容，請多聊幾句後再試！", "error");
  }
}

// C. 修改 User ID 確認
function handleUserChange() {
  const newUserId = document.getElementById("user-id-input").value.trim();
  Swal.fire({
    title: "切換使用者？",
    text: `將以 ${newUserId} 的身份重新開始對話`,
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#075e54",
    confirmButtonText: "確定",
    cancelButtonText: "取消",
  }).then((result) => {
    if (result.isConfirmed) {
      document.getElementById("chat-box").innerHTML = "";
    }
  });
}

// D. 發送訊息功能
async function sendMsg() {
  const input = document.getElementById("msg-input");
  const userId = document.getElementById("user-id-input").value.trim();
  const box = document.getElementById("chat-box");

  if (!input.value.trim() || !userId) {
    Swal.fire("提示", "請輸入訊息與 User ID", "warning");
    return;
  }

  const text = input.value;
  box.innerHTML += `<div class="msg user">${text}</div>`;
  input.value = "";
  box.scrollTop = box.scrollHeight;

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        user_id: userId,
        persona_id: currentPersonaId,
      }),
    });

    const data = await response.json();
    const formattedReply = formatAIResponse(data.reply);
    box.innerHTML += `<div class="msg ai">${formattedReply}</div>`;
    box.scrollTop = box.scrollHeight;
  } catch (error) {
    box.innerHTML += `<div class="msg ai" style="color: red;">(連線失敗，請檢查後端是否開啟)</div>`;
  }
}

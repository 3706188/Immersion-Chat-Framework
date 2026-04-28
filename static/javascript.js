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

// --- 3. 被 HTML 呼叫的函式 (全部掛載到 window) ---

// A. 選擇角色功能
window.selectPersona = function (id, name, avatarUrl) {
  console.log(`[系統] 切換至角色: ${name} (ID: ${id})`);
  currentPersonaId = id;

  const displayName = document.getElementById("display-name");
  const currentAvatar = document.getElementById("current-avatar");
  const box = document.getElementById("chat-box");
  const overlay = document.getElementById("selection-overlay");

  // 更新 UI 文字與頭貼
  if (displayName) displayName.innerText = name;
  if (currentAvatar) {
    currentAvatar.src = avatarUrl;
    currentAvatar.title = `點擊查看 ${name} 對你的記憶`;
  }

  // 清空聊天室並隱藏選角層
  if (box) box.innerHTML = "";
  if (overlay) overlay.classList.add("hidden");

  // 提示通知
  Swal.fire({
    title: `與 ${name} 的對話開始`,
    timer: 1500,
    showConfirmButton: false,
    toast: true,
    position: "top-end",
    icon: "success",
  });
};

// B. 查看記憶摘要
window.showMemory = async function () {
  const userId = document.getElementById("user-id-input").value;
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
};

// C. 修改 User ID 確認
window.handleUserChange = function () {
  const newId = document.getElementById("user-id-input").value;
  Swal.fire({
    title: "切換使用者？",
    text: `將以 ${newId} 的身份重新開始對話`,
    icon: "info",
    confirmButtonColor: "#075e54",
    confirmButtonText: "確定",
  }).then(() => {
    document.getElementById("chat-box").innerHTML = "";
  });
};

// D. 發送訊息功能
window.sendMsg = async function () {
  const input = document.getElementById("msg-input");
  const userId = document.getElementById("user-id-input").value;
  const box = document.getElementById("chat-box");

  if (!input.value.trim() || !userId.trim()) {
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
};

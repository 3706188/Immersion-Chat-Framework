# 沉浸式 AI 聊天系統 🌸

這是一個基於 **FastAPI** 與 **Google Gemini 2.0** 打造的沉浸式 AI 陪伴對話系統。本專案特別強化了 AI 的長短期記憶處理與角色人格演繹。

## 🚀 技術亮點

- **沉浸式角色扮演**：透過 System Instruction 深度定制角色人格，並優化前端動作描述渲染。
- **自動記憶整合系統**：當對話累積至一定數量時，系統會自動呼叫 LLM 進行摘要，並將「長期記憶」存入資料庫，有效節省 Token 並維持背景連貫性。
- **輕量化架構**：後端採用 FastAPI 非同步框架，資料庫使用 SQLAlchemy 驅動的 SQLite。
- **動態 UI/UX**：具備 User ID 切換功能、SweetAlert2 互動式彈窗以及自動滾動聊天介面。

## 🛠️ 技術棧

- **Backend**: Python, FastAPI
- **Database**: SQLite, SQLAlchemy (ORM)
- **AI Model**: Google Gemini 2.0 Flash API
- **Frontend**: HTML5, CSS3, JavaScript (Fetch API)

## 📦 安裝與啟動

1. 複製專案：`git clone https://github.com/你的帳號/Immersion-Chat-Framework.git`
2. 安裝套件：`pip install -r requirements.txt`
3. 設定環境變數：建立 `.env` 並填入 `GEMINI_API_KEY=你的金鑰`
4. 啟動服務：`uvicorn app.main:app --reload`

## 🎨 預覽

- 瀏覽器開啟 `http://127.0.0.1:8000` 即可開始與你想對話的角色對話。

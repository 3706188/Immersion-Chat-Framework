import os
from fastapi import FastAPI, Request
from app.schemas import ChatRequest
from app.llm import get_ai_response, ERROR_REPLY
from app.persona import get_persona
from app.memory import add_message, get_history, get_summary
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 取得目前 main.py 的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
# 取得根目錄路徑 (app 的上一層)
base_dir = os.path.dirname(current_dir)
# 拼接出 static 資料夾的絕對路徑
static_path = os.path.join(base_dir, "static")
# 告訴 FastAPI 靜態檔案放在 static 資料夾
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
def index():
    # 確保讀取的是根目錄下的 static/index.html
    html_file = os.path.join(static_path, "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    return {"error": "找不到 index.html，請檢查 static 資料夾位置"}


@app.get("/memory/{user_id}/{persona_id}")
def read_memory(user_id: str, persona_id: str):
    from app.memory import get_summary
    summary = get_summary(user_id, persona_id)
    return {"summary": summary}


@app.post("/chat")

def chat(req: ChatRequest):
    persona = get_persona(req.persona_id)
    history = get_history(req.user_id, req.persona_id)
    summary = get_summary(req.user_id, req.persona_id)
    
    # 傳入 llm 前可以先在邏輯層做截斷，或者讓 llm.py 內部處理（如上方代碼）
    reply = get_ai_response(req.message, persona, history, summary=summary)
    
    # 存回記憶
    if reply != ERROR_REPLY:
        # 存入使用者的問題
        add_message(req.user_id, req.persona_id, "user", req.message)
        add_message(req.user_id, req.persona_id, "assistant", reply)
    else:
        # 如果失敗了，我們可以選擇不存，或只印出 Log 提醒開發者
        print(f"⚠️ AI 回覆失敗，未存入記憶。使用者 {req.user_id} 的訊息：{req.message}")
    return {
        "reply": reply
    }

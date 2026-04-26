import time
from google import genai
from google.genai import types
from app.config import settings

# 定義一個統一的錯誤回覆字串
ERROR_REPLY = "（角色現在有點累了，請稍等片刻再跟我說話...）"

# 初始化最新 SDK Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_ai_response(message: str, persona: str, history: list, retries=3, summary: str = ""):
    """
    使用 System Instruction 實作沉浸式對話
    """
    # 將你的 history 格式轉換成 Google API 要求的格式
    contents = []
    # 為了節省 Token，我們只取最近的 10 筆歷史紀錄
    recent_history = history[-10:]
    
    for msg in recent_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
    
    full_persona = persona
    if summary:
        full_persona += f"\n\n【關於使用者的重要記憶】：\n{summary}"
    # 加入當前的使用者訊息
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))

    # 自動重試邏輯
    for i in range(retries):
        try:
            response = client.models.generate_content(
                model=settings.MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=full_persona, # 這裡放入 Persona
                    temperature=0.8,            # 增加一點隨機性讓對話更自然
                    max_output_tokens=1024,      # 稍微調低以節省 Token 原本500
                ),
            )
            return response.text
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                wait_time = (i + 1) * 2 # 第一次等2秒，第二次等4秒...
                print(f"觸發頻率限制，{wait_time}秒後重試...")
                time.sleep(wait_time)
                continue
            print(f"Gemini API Error: {e}")
            break
            
    return ERROR_REPLY

    
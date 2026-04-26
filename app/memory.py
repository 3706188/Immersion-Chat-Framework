from app.database import SessionLocal, ChatLog, UserMemory
from sqlalchemy import func

def add_message(user_id: str, persona_id: str, role: str, content: str):
    db = SessionLocal()
    try:
        new_log = ChatLog(user_id=user_id, persona_id=persona_id, role=role, content=content)
        db.add(new_log)
        db.commit()

        # 每次存完訊息，檢查是否需要摘要
        count = db.query(ChatLog).filter(ChatLog.user_id == user_id).count()
        if count >= 15: 
            trigger_summarization(user_id)
    finally:
        db.close()

def trigger_summarization(user_id: str):
    from app.llm import client, settings # 避免循環導入
    db = SessionLocal()

    # 初始化，確保在任何情況下都有值
    history_text = ""
    
    try:
        # 1. 抓取最舊的 10 則對話
        old_logs = db.query(ChatLog).filter(ChatLog.user_id == user_id).order_by(ChatLog.id.asc()).limit(10).all()
        
        if not old_logs:
            print(f"使用者 {user_id} 沒有足夠的舊紀錄可以摘要。")
            return

        # 修正：原本你把這行寫在 return 後面，導致它永遠跑不到
        history_text = "\n".join([f"{log.role}: {log.content}" for log in old_logs])

        # 2. 取得現有的摘要
        existing_mem = db.query(UserMemory).filter(UserMemory.user_id == user_id).first()
        old_summary = existing_mem.summary if existing_mem and existing_mem.summary else "目前尚無舊記憶。"

        # 3. 呼叫 AI 進行「記憶整合」
        prompt = (
            f"你是一個記憶整理助手。請根據以下『舊記憶』與『新對話』，"
            f"更新成一段關於使用者的簡短筆記（約100字），保留使用者的喜好、習慣與目前的關係狀態。\n\n"
            f"【舊記憶】：{old_summary}\n\n"
            f"【新對話】：{history_text}"
        )
        
        # 修正拼字錯誤：generate_content (原本多了一個 g)
        response = client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=prompt
        )
        new_summary = response.text

        # 4. 更新 UserMemory 資料表
        if existing_mem:
            existing_mem.summary = new_summary
        else:
            db.add(UserMemory(user_id=user_id, summary=new_summary))

        # 5. 刪除已摘要的舊紀錄
        old_ids = [log.id for log in old_logs]
        db.query(ChatLog).filter(ChatLog.id.in_(old_ids)).delete(synchronize_session=False)

        db.commit()
        print(f"✅ 使用者 {user_id} 的記憶已自動完成摘要。")

    except Exception as e:
        db.rollback() # 出錯時回滾
        print(f"❌ 摘要失敗: {str(e)}")
    finally:
        db.close()

def get_history(user_id: str, limit=10):
    db = SessionLocal()
    try:
        logs = db.query(ChatLog).filter(ChatLog.user_id == user_id).order_by(ChatLog.id.desc()).limit(limit).all()
        return [{"role": log.role, "content": log.content} for log in reversed(logs)]
    finally:
        db.close()

def get_summary(user_id: str):
    db = SessionLocal()
    try:
        memory = db.query(UserMemory).filter(UserMemory.user_id == user_id).first()
        return memory.summary if memory else ""
    finally:
        db.close()
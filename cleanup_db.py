from app.database import SessionLocal, ChatLog
from app.llm import ERROR_REPLY

def cleanup():
    db = SessionLocal()
    try:
        # 尋找所有內容等於錯誤訊息的紀錄
        wrong_logs = db.query(ChatLog).filter(ChatLog.content == ERROR_REPLY).all()
        count = len(wrong_logs)

        if count > 0:
            # 執行刪除
            db.query(ChatLog).filter(ChatLog.content == ERROR_REPLY).delete(synchronize_session=False)
            db.commit
            print(f"✅ 成功清理！共刪除了 {count} 條錯誤紀錄。")
        else:
            print("查無錯誤紀錄，資料庫很乾淨！")
    except Exception as e:
        print(f"清理失敗: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
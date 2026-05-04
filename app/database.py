from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 建立 SQLite 資料庫檔案
DATABASE_URL = "sqlite:///./ai_chat.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 定義資料表：儲存對話與摘要
class ChatLog(Base):
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    persona_id = Column(String)
    role = Column(String)  # user / assistant
    content = Column(Text)

class UserMemory(Base):
    __tablename__ = "user_memory"
    id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(String, index=True)
    persona_id = Column(String, index=True) # <-- 新增角色 ID 欄位
    summary = Column(Text, default="") # 這裡存摘要

# 建立資料表
Base.metadata.create_all(bind=engine)
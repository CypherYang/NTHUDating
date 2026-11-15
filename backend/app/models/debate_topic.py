"""破冰辯論題目資料模型"""

from sqlalchemy import Boolean, Column, DateTime, Integer, Text
from sqlalchemy.sql import func

from app.core.database import Base


class DebateTopic(Base):
    """破冰辯論題目

    聊天室的「破冰題目」按鈕會從啟用中的題目隨機抽一題。
    """

    __tablename__ = "debate_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<DebateTopic {self.id} {self.content[:20]}>"

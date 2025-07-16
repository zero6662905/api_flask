from typing import Optional

import bcrypt
from flask_login import UserMixin
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from settings import Base, Session_db, cache


class Users(UserMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    sent_requests: Mapped[list["Friends"]] = relationship("Friends", foreign_keys="Friends.sender", back_populates="sender_user")
    received_requests: Mapped[list["Friends"]] = relationship("Friends", foreign_keys="Friends.recipient", back_populates="recipient_user")

    sent_messages: Mapped[list["Messages"]] = relationship("Messages", foreign_keys="Messages.sender", back_populates="sender_user")
    received_messages: Mapped[list["Messages"]] = relationship("Messages", foreign_keys="Messages.recipient", back_populates="recipient_user")

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Метод для перевірки пароля
    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def __repr__(self):
        return f"User: {self.username}"

    def to_json(self):
        return {"username": self.username, "email": self.email, 'id': self.id}

    @staticmethod
    @cache.memoize(timeout=30)
    def get(user_id):
        """ повинен бути методом классу, бо при пошуку ми оперуємо классами а не конкретними
        екземплярами."""        
        
        with Session_db() as conn:
            stmt = select(Users).where(Users.id == user_id)
            user = conn.scalar(stmt)
            return user if user else None

    @staticmethod
    @cache.memoize(timeout=30)
    def get_by_username(username):           
        with Session_db() as conn:
            stmt = select(Users).where(Users.username == username)
            user = conn.scalar(stmt)
            return user if user else None
    
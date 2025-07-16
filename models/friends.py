from typing import Optional

import bcrypt
from flask_login import UserMixin
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from settings import Base, Session_db
from .users import Users

class Friends(Base):
    __tablename__ = " friends"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    sender : Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipient : Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    status : Mapped[bool] = mapped_column( default=False)

    sender_user: Mapped["Users"] = relationship("Users", foreign_keys="Friends.sender", back_populates="sent_requests")
    recipient_user: Mapped["Users"] = relationship("Users", foreign_keys="Friends.recipient", back_populates="received_requests")
    
    @staticmethod
    def _check_friend(user_sender, user_recip) -> bool:
        with Session_db() as conn:
            stmt = select(Friends).filter_by(sender = user_sender, recipient=user_recip)
            request = conn.scalar(stmt)
        return False if request else True
    
    @classmethod
    def check_friends(cls, user_sender, user_recip):
        return cls._check_friend(user_sender, user_recip) and cls._check_friend(user_recip, user_sender)
    
    @classmethod
    def create_request(cls, user_sender, user_recip):
        with Session_db() as conn:
            new_friend_request = cls(sender = user_sender.id, recipient = user_recip.id, status = False)
            conn.add(new_friend_request)
            conn.commit()
        

class Messages(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipient: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message_text: Mapped[str] = mapped_column(Text)
    status_check : Mapped[bool] = mapped_column( default=False)

    sender_user: Mapped["Users"] = relationship("Users", foreign_keys="Messages.sender", back_populates="sent_messages")
    recipient_user: Mapped["Users"] = relationship("Users", foreign_keys="Messages.recipient",
                                                   back_populates="received_messages")

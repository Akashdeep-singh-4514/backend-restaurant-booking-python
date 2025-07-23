from sqlalchemy import Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.constants import AdminRole
from src.config._database_config import Base

class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[AdminRole] = mapped_column(Enum(AdminRole))
    is_active: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Admin(id={self.id}, username='{self.username}', email='{self.email} role='{self.role}')>"
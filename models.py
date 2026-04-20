from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# 1. Группы (например, ИСП-301)
class Group(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    
    # Связь: одна группа имеет много занятий
    lessons: List["Lesson"] = Relationship(back_populates="group")

# 2. Основное расписание
class Lesson(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str            # Предмет
    teacher: str            # Преподаватель
    room: str               # Кабинет
    lesson_number: int      # Номер пары (1-6)
    day_of_week: int        # День недели (1-7)
    
    group_id: int = Field(foreign_key="group.id")
    group: Group = Relationship(back_populates="lessons")

# 3. Таблица изменений (Для уведомлений при слабом сигнале)
class ScheduleChange(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(index=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    
    old_lesson_id: Optional[int] = None
    new_subject: Optional[str] = None
    new_room: Optional[str] = None
    is_canceled: bool = Field(default=False)
    
    # Метка времени для "умной" синхронизации
    updated_at: datetime = Field(default_factory=datetime.utcnow)

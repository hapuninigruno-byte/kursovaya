from sqlmodel import Session, create_engine, select, SQLModel
from models import Group, Lesson
import os

# Подключаемся к базе
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url)

def seed_data():
    # ШАГ 1: Принудительно создаем таблицы, если их нет
    print("Создаем таблицы...")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # ШАГ 2: Проверяем, есть ли уже данные
        existing_group = session.exec(select(Group)).first()
        if existing_group:
            print("База уже содержит данные!")
            return

        print("Добавляем тестовые данные...")
        # ШАГ 3: Создаем тестовую группу
        new_group = Group(name="ИСП-301")
        session.add(new_group)
        session.commit() 
        session.refresh(new_group)

        # ШАГ 4: Добавляем уроки
        lessons = [
            Lesson(subject="Моб. разработка", teacher="Иванов", room="402", lesson_number=1, day_of_week=1, group_id=new_group.id),
            Lesson(subject="Базы данных", teacher="Петрова", room="205", lesson_number=2, day_of_week=1, group_id=new_group.id)
        ]
        
        session.add_all(lessons)
        session.commit()
        print("Готово! Таблицы созданы, данные добавлены.")

if __name__ == "__main__":
    seed_data()

import os
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, select, SQLModel
from models import Group, Lesson, ScheduleChange
from typing import List
from datetime import datetime

ADMIN_PASS = "1234" 
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- API ---
@app.get("/groups")
def read_groups(session: Session = Depends(get_session)):
    return session.exec(select(Group)).all()

@app.post("/groups")
def create_group(group: Group, session: Session = Depends(get_session), x_password: str = Header(None)):
    if x_password != ADMIN_PASS: raise HTTPException(403)
    session.add(group); session.commit(); session.refresh(group)
    return group

@app.get("/schedule/{group_id}")
def read_schedule(group_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Lesson).where(Lesson.group_id == group_id)).all()

@app.post("/lessons")
def create_lesson(lesson: Lesson, session: Session = Depends(get_session), x_password: str = Header(None)):
    if x_password != ADMIN_PASS: raise HTTPException(403)
    session.add(lesson)
    change = ScheduleChange(group_id=lesson.group_id, new_subject=f"Добавлено: {lesson.subject}")
    session.add(change); session.commit()
    return {"ok": True}

@app.delete("/lessons/{id}")
def delete_lesson(id: int, session: Session = Depends(get_session), x_password: str = Header(None)):
    if x_password != ADMIN_PASS: raise HTTPException(403)
    item = session.get(Lesson, id)
    if item:
        change = ScheduleChange(group_id=item.group_id, new_subject=f"Удалено занятие")
        session.add(change); session.delete(item); session.commit()
    return {"ok": True}

@app.get("/sync/{group_id}")
def sync_updates(group_id: int, last_sync: str, session: Session = Depends(get_session)):
    dt_sync = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
    changes = session.exec(select(ScheduleChange).where(
        ScheduleChange.group_id == group_id, 
        ScheduleChange.updated_at > dt_sync
    )).all()
    return {"changes": [c.new_subject for c in changes], "server_time": datetime.utcnow().isoformat()}

@app.get("/")
def read_index(): return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

@app.get("/secret-admin")
def read_admin(): return FileResponse(os.path.join(os.path.dirname(__file__), "admin.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

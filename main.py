# run command: uvicorn main:app --reload 
import logging
import logstash
from fastapi import Depends, FastAPI, Body
from fastapi.responses import JSONResponse, FileResponse
from database import *
from sqlalchemy.orm import Session

# Initialize logger
test_logger = logging.getLogger('FASTAPI_APP')
test_logger.setLevel(logging.DEBUG)
test_logger.addHandler(logstash.TCPLogstashHandler('127.0.0.1', 6000 , version=1))

# Define extra context
extra = {'app_name': "FASTAPI_APP"}

# Initialize FastAPI app
app = FastAPI()

# Define database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define routes
@app.get("/")
def main():
    # Log request
    test_logger.info('Main endpoint accessed', extra=extra)
    return FileResponse("public/index-new.html")

@app.get("/api/users")
def get_people(db: Session = Depends(get_db)):
    # Log request
    test_logger.info('Get users endpoint accessed', extra=extra)
    return db.query(Person).all()

@app.get("/api/users/{id}")
def get_person(id, db: Session = Depends(get_db)):
    # Log request
    test_logger.info(f'Get user by ID {id} endpoint accessed', extra=extra)
    
    person = db.query(Person).filter(Person.id == id).first()
    if person is None:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    return person

@app.post("/api/users")
def create_person(data = Body(), db: Session = Depends(get_db)):
    # Log request
    test_logger.info('Create user endpoint accessed', extra=extra)

    person = Person(name=data["name"], age=data["age"])
    db.add(person)
    db.commit()
    db.refresh(person)
    return person

@app.put("/api/users")
def edit_person(data = Body(), db: Session = Depends(get_db)):
    # Log request
    test_logger.info('Edit user endpoint accessed', extra=extra)

    person = db.query(Person).filter(Person.id == data["id"]).first()
    if person is None:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    person.name = data["name"]
    person.age = data["age"]
    db.commit()
    db.refresh(person)
    return person

@app.delete("/api/users/{id}")
def delete_person(id, db: Session = Depends(get_db)):
    # Log request
    test_logger.info(f'Delete user by ID {id} endpoint accessed', extra=extra)

    person = db.query(Person).filter(Person.id == id).first()
    if person is None:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    db.delete(person)
    db.commit()
    return person

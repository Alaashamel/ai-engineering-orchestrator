from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserRead, UserLogin, Token
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register', response_model=UserRead, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=409, detail='username taken')
    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post('/login', response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='bad credentials')
    return Token(access_token=create_access_token(user.id), token_type='bearer')

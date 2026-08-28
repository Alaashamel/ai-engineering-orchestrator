import hashlib, hmac, os, secrets, time
import jwt
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import User

SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-change-me')
ALGORITHM = 'HS256'

def hash_password(password: str) -> str:
    salt = secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100_000).hex()
    return f'{salt}${digest}'

def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split('$')
    test = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100_000).hex()
    return hmac.compare_digest(test, digest)

def create_access_token(user_id: int) -> str:
    payload = {'sub': str(user_id), 'exp': int(time.time()) + 3600, 'iat': int(time.time())}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='missing token')
    token = authorization.split(' ', 1)[1]
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail='invalid token')
    user = db.get(User, int(data['sub']))
    if not user:
        raise HTTPException(status_code=401, detail='invalid token')
    return user

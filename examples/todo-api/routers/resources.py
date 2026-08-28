from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Todo
from schemas import TodoCreate, TodoRead, TodoUpdate
from auth import get_current_user

router = APIRouter(prefix='/' + 'todos', tags=['todos'])

@router.post('', response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: TodoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = Todo(title=payload.title, description=payload.description, owner_id=user.id)
    db.add(row); db.commit(); db.refresh(row)
    return row

@router.get('', response_model=list[TodoRead])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Todo).filter(Todo.owner_id == user.id).offset(skip).limit(limit).all()

@router.get('/{item_id}', response_model=TodoRead)
def get_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.get(Todo, item_id)
    if not row or row.owner_id != user.id:
        raise HTTPException(status_code=404, detail='not found')
    return row

@router.patch('/{item_id}', response_model=TodoRead)
def update_item(item_id: int, payload: TodoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.get(Todo, item_id)
    if not row or row.owner_id != user.id:
        raise HTTPException(status_code=404, detail='not found')
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit(); db.refresh(row)
    return row

@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.get(Todo, item_id)
    if not row or row.owner_id != user.id:
        raise HTTPException(status_code=404, detail='not found')
    db.delete(row); db.commit()
    return None

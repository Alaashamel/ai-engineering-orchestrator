from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Product
from schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix='/' + 'products', tags=['products'])

@router.post('', response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ProductCreate, db: Session = Depends(get_db)):
    row = Product(title=payload.title, description=payload.description)
    db.add(row); db.commit(); db.refresh(row)
    return row

@router.get('', response_model=list[ProductRead])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Product).offset(skip).limit(limit).all()

@router.get('/{item_id}', response_model=ProductRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = db.get(Product, item_id)
    if not row:
        raise HTTPException(status_code=404, detail='not found')
    return row

@router.patch('/{item_id}', response_model=ProductRead)
def update_item(item_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    row = db.get(Product, item_id)
    if not row:
        raise HTTPException(status_code=404, detail='not found')
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit(); db.refresh(row)
    return row

@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    row = db.get(Product, item_id)
    if not row:
        raise HTTPException(status_code=404, detail='not found')
    db.delete(row); db.commit()
    return None

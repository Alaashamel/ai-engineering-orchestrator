from fastapi import FastAPI

import routers.resources
from database import Base, engine

app = FastAPI(title='Todo Crud Service')
Base.metadata.create_all(bind=engine)
app.include_router(routers.resources.router)

@app.get('/health')
def health():
    return {'status': 'ok'}

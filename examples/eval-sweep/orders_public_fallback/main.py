from fastapi import FastAPI
from database import Base, engine
import routers.resources

app = FastAPI(title='Item Crud Service')
Base.metadata.create_all(bind=engine)
app.include_router(routers.resources.router)

@app.get('/health')
def health():
    return {'status': 'ok'}

from fastapi import FastAPI
from database import Base, engine
import routers.resources
import routers.auth

app = FastAPI(title='%(Name)s Service')
Base.metadata.create_all(bind=engine)
app.include_router(routers.resources.router)
app.include_router(routers.auth.router)

@app.get('/health')
def health():
    return {'status': 'ok'}

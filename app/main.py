from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import contact, admin as admin_api, get_data_from_database, categorymanager, adminproducts
from app.models import admin as admin_model
from app.database import Base, engine
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allowed origins
origins = [
    "http://localhost:5173",
    "http://192.168.0.179:5173",
    "http://172.20.10.4:5173",
    "https://elegant-global.vercel.app",
    "https://www.elegant.global",
    "https://elegant.global",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # <-- fixed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

print("Serving static files from:", STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Routers
app.include_router(adminproducts.router, prefix="/api/admin/products", tags=["admin_products"])
app.include_router(get_data_from_database.router, prefix="/api/products", tags=["public_products"])
app.include_router(categorymanager.router, prefix="/api/admin/categories", tags=["admin_categories"])
app.include_router(contact.router, prefix="/api", tags=["contact"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Backend is running"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import contact
from app.api import admin as admin_api
from app.models import admin as admin_model
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles

from app.api import get_data_from_database
from app.api import categorymanager
from app.api import adminproducts
import os






Base.metadata.create_all(bind=engine)

app = FastAPI()



# Allow your frontend's origin
origins = [
    "http://localhost:5173",
    "http://192.168.0.179:5173",
    "http://172.20.10.4:5173"  # optional, in case you open via IP
    "http://elegant-global.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for all origins during dev
    allow_credentials=True,
    allow_methods=["*"],    # allow all HTTP methods
    allow_headers=["*"],    # allow all headers
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Folder containing main.py
STATIC_DIR = os.path.join(BASE_DIR, "static")          # Absolute path to static folder

print("Serving static files from:", STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

print("STATIC_DIR mounted at:", STATIC_DIR)



# Admin product management (CRUD for dashboard)
app.include_router(adminproducts.router, prefix="/api/admin/products", tags=["admin_products"])

# Public-facing products (used by frontend website)
app.include_router(get_data_from_database.router, prefix="/api/products", tags=["public_products"])

# Categories manager (admin)
app.include_router(categorymanager.router, prefix="/api/admin/categories", tags=["admin_categories"])

# Other routers
app.include_router(contact.router, prefix="/api", tags=["contact"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["admin"])







@app.get("/")
def read_root():
    return {"message": "Backend is running"}

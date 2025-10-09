from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.admin import Product

# Map your product keys to image paths

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.admin import Product

image_map = {
    "hairFiller": "/static/products/hair.png",
    "lips": "/static/products/lips.png",
    "underEye": "/static/products/under-eye.png",
}

def update_images():
    db: Session = SessionLocal()
    try:
        for key, path in image_map.items():
            product = db.query(Product).filter(Product.key == key).first()
            if product:
                product.image_url = path  # store the static path
                print(f"Updated {key} -> {path}")
            else:
                print(f"Product with key '{key}' not found")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    update_images()



def update_images():
    db: Session = SessionLocal()
    try:
        for key, path in image_map.items():
            product = db.query(Product).filter(Product.key == key).first()
            if product:
                product.image_url = path
                print(f"Updated {key} -> {path}")
            else:
                print(f"Product with key '{key}' not found")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    update_images()

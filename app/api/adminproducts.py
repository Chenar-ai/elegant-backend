# app/routers/admin_products.py

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload
from typing import Optional
import shutil, os, json
from slugify import slugify
from uuid import uuid4
import uuid



from app.database import get_db
from app.models.admin import Product, ProductTranslation, Category

router = APIRouter()

# Absolute upload directory inside app/static/products
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # -> app/
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "products")
os.makedirs(UPLOAD_DIR, exist_ok=True)

print("✅ Upload directory set to:", UPLOAD_DIR)

# -------------------------
# List all products (full data)
# -------------------------
@router.get("/by-lang/{lang}")
def list_products(lang: str, db: Session = Depends(get_db)):
    products = db.query(Product).options(
        joinedload(Product.translations),
        joinedload(Product.category)
    ).all()

    result = []
    for product in products:
        t = next((tr for tr in product.translations if tr.language_code == lang), None)
        result.append({
            "id": product.id,
            "key": product.key,
            "category_id": product.category_id,
            "image_url": product.image_url,
            "translations": [
                {
                    "language_code": t.language_code,
                    "title": t.title,
                    "description": t.description,
                }
            ] if t else []
        })
    return result


@router.post("/")
def create_product(
    category_id: int = Form(...),
    translations: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    # Parse translations JSON
    try:
        translations_data = json.loads(translations)
        if not translations_data:
            raise ValueError("Translations cannot be empty")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid translations JSON: {e}")

    # Verify category exists
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    # Handle image upload
    image_url = None
    if image:
        filename = f"{uuid4().hex}{os.path.splitext(image.filename)[1]}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        print("📥 Incoming file:", image.filename)
        print("➡️ Saving to:", filepath)

        try:
            image.file.seek(0)  # rewind in case stream was read
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            print("❌ Error while saving file:", e)
            raise HTTPException(status_code=500, detail="Failed to save image")

        # Confirm file saved
        if os.path.exists(filepath):
            print("✅ File saved:", filepath, "Size:", os.path.getsize(filepath))
        else:
            print("❌ File not found after save:", filepath)

        # Store only relative path for frontend
        image_url = f"/static/products/{filename}"

    # Auto-generate unique key
    en_translation = next((t for t in translations_data if t.get("language_code") == "en"), None)
    if en_translation and en_translation.get("title"):
        base_key = slugify(en_translation["title"])
    else:
        base_key = uuid4().hex[:8]

    key = base_key
    i = 1
    while db.query(Product).filter(Product.key == key).first():
        key = f"{base_key}-{i}"
        i += 1

    # Create product
    product = Product(key=key, category_id=category_id, image_url=image_url)
    db.add(product)
    db.flush()

    # Add translations
    for tr in translations_data:
        db.add(ProductTranslation(
            product_id=product.id,
            language_code=tr["language_code"],
            title=tr.get("title", ""),
            description=tr.get("description", "")
        ))

    db.commit()
    db.refresh(product)

    return {
        "message": "Product created successfully",
        "id": product.id,
        "key": product.key,
        "category_id": product.category_id,
        "image_url": product.image_url
    }



@router.put("/{product_id}")
def update_product(
    product_id: int,
    category_id: int = Form(...),
    translations: str = Form(...),
    image: Optional[UploadFile] = File(None),
    existingImage: Optional[str] = Form(None),
    key: Optional[str] = Form(None),   # optional if frontend sends it
    db: Session = Depends(get_db),
):
    # Find product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate category
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    # Parse translations
    try:
        translations_data = json.loads(translations)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid translations JSON: {e}")

    # Handle image
    if image:
        filename = f"{uuid.uuid4().hex}{os.path.splitext(image.filename)[1]}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        product.image_url = f"/static/products/{filename}"
    elif existingImage:
        # keep the existing image
        product.image_url = existingImage

    # Update product fields
    product.category_id = category_id


    # Update translations
    db.query(ProductTranslation).filter(ProductTranslation.product_id == product.id).delete()
    for tr in translations_data:
        db.add(ProductTranslation(
            product_id=product.id,
            language_code=tr["language_code"],
            title=tr.get("title", ""),
            description=tr.get("description", "")
        ))

    db.commit()
    db.refresh(product)

    return {
        "id": product.id,
        "key": product.key,
        "category_id": product.category_id,
        "image_url": product.image_url,
    }



# -------------------------
# Delete product
# -------------------------
@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)  # mark for deletion
    db.commit()  # ✅ commit is required
    return {"message": "Product deleted"}

# -------------------------
# List products grouped by category
# -------------------------
@router.get("/grouped")
def list_products_grouped(db: Session = Depends(get_db)):
    categories = db.query(Category).options(
        joinedload(Category.products).joinedload(Product.translations)
    ).all()

    result = []
    for category in categories:
        result.append({
            "id": category.id,
            "key": category.key,
            "title": category.key,  # fallback
            "products": [
                {
                    "id": p.id,
                    "key": p.key,
                    "image_url": p.image_url,
                    "translations": [
                        {
                            "language_code": tr.language_code,
                            "title": tr.title,
                            "description": tr.description
                        }
                        for tr in p.translations
                    ]
                }
                for p in category.products
            ]
        })
    return {"categories": result}





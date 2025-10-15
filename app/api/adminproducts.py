from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload
from typing import Optional
import os, json, uuid
from slugify import slugify
from app.r2_client import r2
from app.database import get_db
from app.models.admin import Product, ProductTranslation, Category

router = APIRouter()

# -------------------------
# List all products
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


# -------------------------
# Create Product
# -------------------------
@router.post("/")
async def create_product(
    category_id: int = Form(...),
    translations: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    print("🧩 DEBUG incoming form fields:")
    print(f"category_id = {category_id}")
    print(f"translations = {translations}")
    print(f"image = {image}")
    if image is not None:
        print(f"image filename = {image.filename}")

    # Parse translations
    try:
        translations_data = json.loads(translations)
        if not translations_data:
            raise ValueError("Translations cannot be empty")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid translations JSON: {e}")

    # Verify category
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    # Upload image to R2
    image_url = None
    if image:
        file_ext = os.path.splitext(image.filename)[1]
        file_key = f"products/{uuid.uuid4().hex}{file_ext}"

        try:
            r2.put_object(
                Bucket=os.getenv("R2_BUCKET_NAME"),
                Key=file_key,
                Body=await image.read(),
                ContentType=image.content_type,
            )
            # build public url
            image_url = f"{os.getenv('R2_PUBLIC_URL')}/{file_key}"
        except Exception as e:
            print("❌ Upload to R2 failed:", e)
            raise HTTPException(status_code=500, detail="Failed to upload image")

    # Generate key
    en_translation = next((t for t in translations_data if t.get("language_code") == "en"), None)
    base_key = slugify(en_translation["title"]) if en_translation and en_translation.get("title") else uuid.uuid4().hex[:8]

    key = base_key
    i = 1
    while db.query(Product).filter(Product.key == key).first():
        key = f"{base_key}-{i}"
        i += 1

    # Create product
    product = Product(key=key, category_id=category_id, image_url=image_url)
    db.add(product)
    db.flush()

    # Translations
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


# -------------------------
# Update Product
# -------------------------
@router.put("/{product_id}")
async def update_product(
    product_id: int,
    category_id: int = Form(...),
    translations: str = Form(...),
    image: Optional[UploadFile] = File(None),
    existingImage: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    try:
        translations_data = json.loads(translations)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid translations JSON: {e}")

    if image:
        file_ext = os.path.splitext(image.filename)[1]
        file_key = f"products/{uuid.uuid4().hex}{file_ext}"
        try:
            r2.put_object(
                Bucket=os.getenv("R2_BUCKET_NAME"),
                Key=file_key,
                Body=await image.read(),
                ContentType=image.content_type,
            )
            product.image_url = f"{os.getenv('R2_PUBLIC_URL')}/{file_key}"
        except Exception as e:
            print("❌ R2 update failed:", e)
            raise HTTPException(status_code=500, detail="Failed to update image")
    elif existingImage:
        product.image_url = existingImage

    product.category_id = category_id

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
    return product


# -------------------------
# Delete Product
# -------------------------
@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

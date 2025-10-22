import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.admin import Category, Product
import json

router = APIRouter()

@router.get("/{language_code}")
def get_products(language_code: str, db: Session = Depends(get_db)):
    start_total = time.time()
    print("⚡ get_products called")

    # --- DB query timing ---
    start_query = time.time()
    categories = db.query(Category).options(
        joinedload(Category.products).joinedload(Product.translations),
        joinedload(Category.translations)
    ).all()
    end_query = time.time()

    # --- Processing timing ---
    start_process = time.time()
    result = []
    for category in categories:
        cat_translation = next(
            (t for t in category.translations if t.language_code == language_code),
            None
        )
        title = cat_translation.title if cat_translation else ""
        intro = cat_translation.intro if cat_translation else ""

        try:
            references = json.loads(category.references_json) if category.references_json else []
        except Exception:
            references = []

        products = []
        for product in category.products:
            prod_translation = next(
                (t for t in product.translations if t.language_code == language_code),
                None
            )
            if prod_translation:
                products.append({
                    "id": product.id,
                    "key": product.key,
                    "title": prod_translation.title,
                    "description": prod_translation.description,
                    "image_url": product.image_url
                })

        result.append({
            "id": category.id,
            "key": category.key,
            "title": title,
            "intro": intro,
            "references": references,
            "products": products
        })
    end_process = time.time()

    end_total = time.time()
    print(f"⏱️ Query: {end_query - start_query:.3f}s | Processing: {end_process - start_process:.3f}s | Total: {end_total - start_total:.3f}s")

    return {"categories": result or []}

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.admin import Category, Product
import json

router = APIRouter()

def get_translation(translations, language_code: str, fallback: str = "en"):
    """Return translation for requested language, fallback if missing."""
    # normalize (handle en-US → en)
    normalized = language_code.split("-")[0].lower()

    # try exact
    translation = next((t for t in translations if t.language_code == normalized), None)
    if translation:
        return translation

    # try fallback
    if fallback and fallback != normalized:
        return next((t for t in translations if t.language_code == fallback), None)

    return None


@router.get("/{language_code}")
def get_products(language_code: str, db: Session = Depends(get_db)):
    categories = db.query(Category).options(
        joinedload(Category.products).joinedload(Product.translations),
        joinedload(Category.translations)
    ).all()

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
            "id": category.id,   # ✅ fixed: use category.id, not product.id
            "key": category.key,
            "title": title,
            "intro": intro,
            "references": references,
            "products": products
        })

    return {"categories": result or []}  # ✅ always return list


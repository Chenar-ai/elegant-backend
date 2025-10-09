from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models.admin import Category, CategoryTranslation, Product, ProductTranslation
from app.schemas.categorymanager import CategoryOutSchema, CategoryCreateSchema, CategoryUpdateSchema
import json
import logging

router = APIRouter()

# 🛠️ UTF-8 safe JSON response helper
def safe_json_response(data):
    return Response(
        content=json.dumps(data, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )

# 📦 Helper to convert Category to dict
def category_to_dict(category: Category):
    return {
        "id": category.id,
        "key": category.key,
        "references_json": json.loads(category.references_json) if category.references_json else [],
        "translations": [
            {
                "id": t.id,
                "language_code": t.language_code,
                "title": t.title,
                "intro": t.intro
            }
            for t in category.translations
        ],
        "products": [
            {
                "id": p.id,
                "key": p.key,
                "image_url": p.image_url,
                "translations": [
                    {
                        "id": pt.id,
                        "language_code": pt.language_code,
                        "title": pt.title,
                        "description": pt.description
                    }
                    for pt in p.translations
                ]
            }
            for p in category.products
        ]
    }

# ✅ GET all categories (with products and translations)
@router.get("/", response_model=List[CategoryOutSchema])
def list_categories(db: Session = Depends(get_db)):
    try:
        categories = (
            db.query(Category)
            .options(
                joinedload(Category.translations),
                joinedload(Category.products).joinedload(Product.translations),
            )
            .all()
        )
        result = [category_to_dict(c) for c in categories]
        return safe_json_response(result)
    except SQLAlchemyError as e:
        logging.exception("Database error while fetching categories")
        raise HTTPException(status_code=500, detail="Database error")


# ✅ Create new category
@router.post("/", response_model=CategoryOutSchema)
def create_category(payload: CategoryCreateSchema, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.key == payload.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category key already exists")

    references = payload.references_json or "[]"

    category = Category(
        key=payload.key,
        references_json=json.dumps(references) if isinstance(references, list) else references,
    )
    db.add(category)
    db.flush()

    for t in payload.translations:
        db.add(CategoryTranslation(
            category_id=category.id,
            language_code=t.language_code,
            title=t.title,
            intro=t.intro
        ))

    db.commit()
    db.refresh(category)
    return safe_json_response(category_to_dict(category))


# ✅ Update existing category
@router.put("/{category_id}", response_model=CategoryOutSchema)
def update_category(category_id: int, payload: CategoryUpdateSchema, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if payload.key is not None:
        category.key = payload.key
    if payload.references_json is not None:
        category.references_json = json.dumps(payload.references_json) if isinstance(payload.references_json, list) else payload.references_json

    # Clear and re-add translations
    category.translations.clear()
    db.flush()
    for t in payload.translations:
        category.translations.append(CategoryTranslation(
            language_code=t.language_code,
            title=t.title,
            intro=t.intro
        ))

    db.commit()
    db.refresh(category)
    return safe_json_response(category_to_dict(category))


# ✅ Delete category
@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"success": True}


# ✅ Get products for a category
@router.get("/{category_id}/products")
def list_products_in_category(category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(Category)
        .options(joinedload(Category.products).joinedload(Product.translations))
        .filter(Category.id == category_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return safe_json_response([p for p in category_to_dict(category)["products"]])

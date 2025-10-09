import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.admin import Category, CategoryTranslation, Product, ProductTranslation

# --------------------
# Database setup
# --------------------
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:YourNewPassword@localhost/elegantdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --------------------
# Locale folder
# --------------------
LOCALE_PATH = r"C:\Users\Admin\elegant\public\locales"
LOCALES = ["en", "fr", "nl", "pt", "ar", "de", "es"]

# --------------------
# Import function
# --------------------
def import_data():
    db = SessionLocal()
    try:
        print(f"✅ Connected to DB: elegantdb\n🔍 Locales folder resolved to: {LOCALE_PATH}\n")

        # Load all locale JSONs
        locales = {}
        for lang in LOCALES:
            file_path = os.path.join(LOCALE_PATH, f"{lang}.json")
            if not os.path.isfile(file_path):
                print(f"⚠ Missing locale file: {file_path}")
                continue
            with open(file_path, encoding="utf-8") as f:
                locales[lang] = json.load(f)

        # --------------------
        # Import category (references)
        # --------------------
        for lang, data in locales.items():
            # Extract category references
            references = data.get("products", {}).get("references", [])
            cat_key = "haFillers"  # Using HA Fillers as the category key

            # Upsert category
            category = db.query(Category).filter_by(key=cat_key).first()
            if not category:
                category = Category(key=cat_key)
                db.add(category)
                db.flush()  # ensure category.id exists
            category.references_json = json.dumps(references, ensure_ascii=False)

            # Upsert category translation
            cat_trans = db.query(CategoryTranslation).filter_by(
                category_id=category.id, language_code=lang
            ).first()
            if not cat_trans:
                cat_trans = CategoryTranslation(category_id=category.id, language_code=lang)
                db.add(cat_trans)

            # Optional: add title/intro if present in JSON
            cat_data = data.get("products", {}).get("haFillers", {})
            cat_trans.title = cat_data.get("title", "HA Fillers")
            cat_trans.intro = cat_data.get("intro", "")

        db.commit()
        print("✅ Category upserted")

        # --------------------
        # Import products
        # --------------------
        for lang, data in locales.items():
            cat_key = "haFillers"
            category = db.query(Category).filter_by(key=cat_key).first()
            products_data = data.get("products", {}).get("haFillers", {}).get("items", {})

            for prod_key, prod_data in products_data.items():
                # Upsert product
                product = db.query(Product).filter_by(category_id=category.id, key=prod_key).first()
                if not product:
                    product = Product(category_id=category.id, key=prod_key)
                    db.add(product)
                    db.flush()  # ensure product.id exists

                # Upsert product translation
                prod_trans = db.query(ProductTranslation).filter_by(
                    product_id=product.id, language_code=lang
                ).first()
                if not prod_trans:
                    prod_trans = ProductTranslation(product_id=product.id, language_code=lang)
                    db.add(prod_trans)

                prod_trans.title = prod_data.get("title", "")
                prod_trans.description = prod_data.get("description", "")

        db.commit()
        print("✅ Products upserted")

    except Exception as e:
        db.rollback()
        print(f"❌ Database error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import_data()

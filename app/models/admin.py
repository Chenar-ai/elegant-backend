from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    references_json = Column(Text, nullable=True)  # store references as JSON string

    translations = relationship("CategoryTranslation", back_populates="category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class CategoryTranslation(Base):
    __tablename__ = "category_translations"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    language_code = Column(String, nullable=False)  # e.g., "en", "fr"
    title = Column(String, nullable=False)
    intro = Column(Text, nullable=True)

    category = relationship("Category", back_populates="translations")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    key = Column(String, nullable=False)  # NEW: stable key like "lips", "under-eye"
    image_url = Column(String, nullable=True)

    category = relationship("Category", back_populates="products")
    translations = relationship("ProductTranslation", back_populates="product", cascade="all, delete-orphan")


class ProductTranslation(Base):
    __tablename__ = "product_translations"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    language_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    product = relationship("Product", back_populates="translations")

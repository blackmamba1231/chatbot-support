from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class ProductImage(BaseModel):
    id: int
    src: str
    name: Optional[str] = None
    alt: Optional[str] = None

class ProductCategory(BaseModel):
    id: int
    name: str
    slug: str

class ProductAttributes(BaseModel):
    id: int
    name: str
    position: int
    visible: bool
    variation: bool
    options: List[str]

class Product(BaseModel):
    id: int
    name: str
    slug: str
    permalink: str
    date_created: str
    type: str
    status: str
    featured: bool
    description: str
    short_description: str
    price: str
    regular_price: str
    sale_price: Optional[str] = None
    on_sale: bool
    purchasable: bool
    total_sales: int
    virtual: bool
    downloadable: bool
    categories: List[ProductCategory]
    tags: List[Dict[str, Any]] = []
    images: List[ProductImage]
    attributes: List[ProductAttributes] = []
    stock_status: str
    
    # Custom fields from extraction
    location: Optional[str] = None
    mall: Optional[str] = None
    
    class Config:
        orm_mode = True

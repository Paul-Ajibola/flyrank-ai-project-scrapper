import re
from typing import Optional, Any
from pydantic import BaseModel, field_validator, model_validator

class NormalizedBook(BaseModel):
    title: str
    product_url: str
    price: float = 0.0
    stock_count: int = 0
    rating: int = 1
    description: Optional[str] = None
    source_page: str
    fetched_at: str

    @model_validator(mode="before")
    @classmethod
    def map_and_clean_fields(cls, values: Any) -> Any:
        """Flexible key mapping for extractor outputs."""
        if not isinstance(values, dict):
            return values
            
        # Handle aliases / alternative key names
        if "price_text" in values and "price" not in values:
            values["price"] = values.pop("price_text")
            
        for avail_key in ["availability_text", "availablity_text", "stock_raw"]:
            if avail_key in values and "stock_count" not in values:
                values["stock_count"] = values.pop(avail_key)
                
        if "rating_text" in values and "rating" not in values:
            values["rating"] = values.pop("rating_text")
            
        return values


    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v):
        """Converts currency string like '£20.66' into a float 20.66"""
        if isinstance(v, (int, float)):
            return float(v)
        if not v:
            return 0.0
        cleaned = re.sub(r"[^\d.]", "", str(v))
        return float(cleaned) if cleaned else 0.0


    @field_validator("stock_count", mode="before")
    @classmethod
    def parse_stock(cls, v):
        """Extracts available stock integer from availability text"""
        if isinstance(v, int):
            return v
        if not v:
            return 0
        match = re.search(r"\((\d+)\s+available\)", str(v))
        if match:
            return int(match.group(1))
        if "in stock" in str(v).lower():
            return 0
        return 0


    @field_validator("rating", mode="before")
    @classmethod
    def parse_rating(cls, v):
        """Converts word ratings like 'Four' into integer 4"""
        mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        if isinstance(v, int):
            return v
        return mapping.get(str(v).strip(), 1)


def validate_raw_record(raw_record: dict) -> Optional[NormalizedBook]:
    """Validates and normalizes a raw dictionary record into a Pydantic model."""
    try:
        return NormalizedBook.model_validate(raw_record)
    except Exception as e:
        print(f"Validation error for {raw_record.get('product_url')}: {e}")
        return None
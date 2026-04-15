from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

app = FastAPI(
    title="Inventory System API",
    description="Simple Inventory Management System — Cloud Computing Project",
    version="1.0.0"
)

# ── Models ─────────────────────────────────────────────────────────

class Item(BaseModel):
    name: str
    category: str
    quantity: int
    price: float
    description: Optional[str] = ""

class UpdateItem(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None

# ── In-memory DB (pre-loaded with sample data) ──────────────────────

inventory: dict[int, dict] = {
    1: {"id": 1, "name": "Laptop", "category": "Electronics", "quantity": 10, "price": 45000.00, "description": "14-inch laptop", "created_at": "2025-01-01T00:00:00"},
    2: {"id": 2, "name": "Office Chair", "category": "Furniture", "quantity": 25, "price": 3500.00, "description": "Ergonomic chair", "created_at": "2025-01-01T00:00:00"},
    3: {"id": 3, "name": "Notebook", "category": "Stationery", "quantity": 4, "price": 55.00, "description": "A4 ruled notebook", "created_at": "2025-01-01T00:00:00"},
    4: {"id": 4, "name": "USB Hub", "category": "Electronics", "quantity": 0, "price": 750.00, "description": "7-port USB 3.0 hub", "created_at": "2025-01-01T00:00:00"},
    5: {"id": 5, "name": "Whiteboard", "category": "Office Supplies", "quantity": 3, "price": 1200.00, "description": "Magnetic dry-erase board", "created_at": "2025-01-01T00:00:00"},
}
next_id = 6


# ── Frontend UI ─────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def dashboard():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(template_path) as f:
        return f.read()


# ── API Routes ──────────────────────────────────────────────────────

@app.get("/items")
def get_all_items(category: Optional[str] = None, search: Optional[str] = None):
    """Get all inventory items. Optional filter by category or search by name."""
    items = list(inventory.values())
    if category:
        items = [i for i in items if i["category"].lower() == category.lower()]
    if search:
        items = [i for i in items if search.lower() in i["name"].lower()]
    return {"total": len(items), "items": items}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Get a single item by ID."""
    if item_id not in inventory:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return inventory[item_id]

@app.post("/items", status_code=201)
def add_item(item: Item):
    """Add a new item to inventory."""
    global next_id
    new_item = {
        "id": next_id,
        **item.model_dump(),
        "created_at": datetime.utcnow().isoformat()
    }
    inventory[next_id] = new_item
    next_id += 1
    return {"message": "Item added successfully!", "item": new_item}

@app.put("/items/{item_id}")
def update_item(item_id: int, updates: UpdateItem):
    """Update an existing item (partial update)."""
    if item_id not in inventory:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    for field, value in updates.model_dump(exclude_none=True).items():
        inventory[item_id][field] = value
    return {"message": "Item updated!", "item": inventory[item_id]}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """Remove an item from inventory."""
    if item_id not in inventory:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    deleted = inventory.pop(item_id)
    return {"message": "Item deleted!", "item": deleted}

@app.get("/summary")
def get_summary():
    """Get inventory summary stats."""
    items = list(inventory.values())
    categories = {}
    for item in items:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1

    total_value = sum(i["quantity"] * i["price"] for i in items)
    low_stock = [i for i in items if i["quantity"] <= 5]

    return {
        "total_items": len(items),
        "total_stock_value": round(total_value, 2),
        "categories": categories,
        "low_stock_alerts": low_stock
    }

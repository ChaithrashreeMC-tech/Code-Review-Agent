# TC-009: Pagination and Data Retrieval (PERF10 violation)
# Expected: PERF10 finding, severity=high, confidence=high
# Technology: Python / FastAPI + SQLAlchemy

from fastapi import FastAPI, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Product, db_session

app = FastAPI()


# --- VIOLATION 1: No pagination — returns all rows ---
@app.get("/products")
def list_products_no_pagination(db: Session = db_session):
    """
    VIOLATION: Returns all Product records with no LIMIT or pagination.
    In a catalog with 500,000 products this will:
    - Transfer hundreds of MB of JSON
    - Exhaust memory in the application server
    - Time out the client connection
    """
    products = db.query(Product).all()  # VIOLATION: no .limit()
    return [p.to_dict() for p in products]


# --- VIOLATION 2: OFFSET pagination on large dataset ---
@app.get("/products/paged-offset")
def list_products_offset(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=1000),  # VIOLATION: allows 1,000
    db: Session = db_session,
):
    """
    VIOLATION 2a: OFFSET pagination performs a full scan up to the offset.
    At page 50,000 (offset 1,000,000) the database scans 1,000,000 rows
    before returning 20. Performance degrades linearly with page number.

    VIOLATION 2b: page_size allows up to 1,000 rows per page with no
    reasonable cap — a single request could return 1,000 full product rows.
    """
    offset = (page - 1) * page_size
    products = (
        db.query(Product)
        .offset(offset)      # VIOLATION: OFFSET degrades at scale
        .limit(page_size)
        .all()
    )
    return products


# --- SAFE 1: Cursor-based (keyset) pagination ---
@app.get("/products/paged-cursor")
def list_products_cursor(
    cursor: int | None = Query(default=None, description="Last seen product ID"),
    page_size: int = Query(default=20, ge=1, le=100),  # SAFE: hard cap at 100
    db: Session = db_session,
):
    """
    SAFE: Keyset pagination uses WHERE id > cursor to skip rows efficiently.
    O(1) regardless of how deep into the dataset the cursor is.
    page_size is capped at 100 to prevent oversized responses.
    """
    query = db.query(Product).order_by(Product.id)
    if cursor is not None:
        query = query.filter(Product.id > cursor)
    products = query.limit(page_size).all()

    next_cursor = products[-1].id if len(products) == page_size else None
    return {"items": [p.to_dict() for p in products], "next_cursor": next_cursor}


# --- SAFE 2: Simple limit-based with a hard cap ---
@app.get("/products/limited")
def list_products_limited(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = db_session,
):
    """
    SAFE: Always applies a LIMIT with a maximum of 100. Suitable for
    catalog browsing where deep pagination is not required.
    """
    products = db.query(Product).limit(limit).all()
    return [p.to_dict() for p in products]


# NOT APPLICABLE: Data export endpoint — intentionally returns all rows
@app.get("/products/export")
def export_all_products(db: Session = db_session):
    """
    NOT APPLICABLE (intentional full export):
    This endpoint is designed to export the full catalog for warehouse sync.
    It is called by an internal service, not end users.
    PERF10 should NOT flag the absence of pagination here.
    However, PERF03 streaming should still be considered for large datasets.
    """
    from fastapi.responses import StreamingResponse
    import csv, io

    def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "sku", "name", "price_cents"])
        for p in db.query(Product).yield_per(1000):
            writer.writerow([p.id, p.sku, p.name, p.price_cents])
            yield output.getvalue()
            output.truncate(0)
            output.seek(0)

    return StreamingResponse(generate(), media_type="text/csv")


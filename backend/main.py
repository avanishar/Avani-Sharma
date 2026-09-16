from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.models import BookingRequest
from backend.pricing_engine import PricingError, calculate_price
from backend.price_importer import import_price_list


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI(
    title="CineVerse Ticket Pricing Engine",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC FRONTEND
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
def root():
    return FileResponse(
        FRONTEND_DIR / "index.html",
        media_type="text/html",
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "CineVerse Pricing Engine",
    }


# ============================================================
# PRICE CALCULATION
# ============================================================

@app.post("/calculate-price")
def calculate_booking_price(
    booking: BookingRequest,
):
    try:
        return calculate_price(booking)

    except PricingError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected pricing error occurred.",
        ) from exc


# ============================================================
# MESSY PRICE LIST IMPORTER
# ============================================================

@app.post("/import-price-list")
def import_price_list_endpoint(
    records: list[dict],
):
    try:
        return import_price_list(records)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
import re
from decimal import Decimal, InvalidOperation


VALID_TIERS = {
    "SILVER",
    "GOLD",
    "RECLINER",
}


class ImportError(Exception):
    """Raised when a price list cannot be imported."""


def normalize_tier_name(name: object) -> str:
    """
    Normalize a seat-class name.

    Examples:
        ' Silver ' -> 'SILVER'
        'gold'     -> 'GOLD'
        ' RECLINER ' -> 'RECLINER'
    """

    if not isinstance(name, str):
        raise ValueError("Seat class name must be text.")

    normalized = " ".join(name.strip().split()).upper()

    if not normalized:
        raise ValueError("Seat class name cannot be blank.")

    return normalized


def parse_price_to_paise(price: object) -> int:
    """
    Convert a messy price value into integer paise.

    Accepted examples:
        150
        "150"
        "150.00"
        "₹150"
        "₹150.50"
        " 250.00 "

    Rejected:
        blank values
        negative values
        non-numeric values
    """

    if price is None:
        raise ValueError("Price cannot be blank.")

    if isinstance(price, bool):
        raise ValueError("Price must be numeric.")

    text = str(price).strip()

    if not text:
        raise ValueError("Price cannot be blank.")

    # Remove common currency symbols and separators.
    text = text.replace("₹", "")
    text = text.replace(",", "")
    text = text.strip()

    # Reject negative prices explicitly.
    if text.startswith("-"):
        raise ValueError("Price cannot be negative.")

    # Accept only a normal positive decimal representation.
    if not re.fullmatch(r"\+?\d+(\.\d{1,2})?", text):
        raise ValueError(
            f"Invalid price format: '{price}'."
        )

    try:
        amount = Decimal(text)

    except InvalidOperation as exc:
        raise ValueError(
            f"Invalid price format: '{price}'."
        ) from exc

    if amount <= 0:
        raise ValueError("Price must be greater than zero.")

    # Convert rupees to paise without floating-point arithmetic.
    paise = int(amount * 100)

    if paise <= 0:
        raise ValueError(
            "Price must be greater than zero."
        )

    return paise


def import_price_list(records: list[dict]) -> dict:
    """
    Clean and import a messy seat-class price list.

    Duplicate names are compared after normalization.

    The first valid occurrence of a normalized tier wins.
    Later occurrences are reported as duplicates.
    """

    cleaned_prices = {}

    imported_count = 0
    accepted_count = 0
    duplicate_count = 0
    rejected_count = 0

    duplicates = []
    rejected = []

    for index, record in enumerate(records, start=1):

        imported_count += 1

        if not isinstance(record, dict):
            rejected_count += 1

            rejected.append(
                {
                    "row": index,
                    "reason": "Record must be an object.",
                    "record": record,
                }
            )

            continue

        try:
            tier_name = normalize_tier_name(
                record.get("name")
            )

            if tier_name not in VALID_TIERS:
                raise ValueError(
                    f"Unknown seat class '{tier_name}'."
                )

            price_paise = parse_price_to_paise(
                record.get("price")
            )

        except (ValueError, TypeError) as exc:

            rejected_count += 1

            rejected.append(
                {
                    "row": index,
                    "reason": str(exc),
                    "record": record,
                }
            )

            continue

        # --------------------------------------------------------
        # DUPLICATE
        # --------------------------------------------------------

        if tier_name in cleaned_prices:

            duplicate_count += 1

            duplicates.append(
                {
                    "row": index,
                    "tier": tier_name,
                    "price_paise": price_paise,
                    "reason": (
                        "Duplicate seat class after "
                        "case/whitespace normalization."
                    ),
                }
            )

            continue

        # --------------------------------------------------------
        # ACCEPT
        # --------------------------------------------------------

        cleaned_prices[tier_name] = {
            "tier": tier_name,
            "price_paise": price_paise,
        }

        accepted_count += 1

    return {
        "cleaned_prices": list(
            cleaned_prices.values()
        ),
        "report": {
            "imported": imported_count,
            "accepted": accepted_count,
            "duplicates": duplicate_count,
            "rejected": rejected_count,
        },
        "duplicates": duplicates,
        "rejected": rejected,
    }
import json
from pathlib import Path

from backend.models import BookingRequest


CONFIG_PATH = Path(__file__).parent.parent / "data" / "pricing.json"


class PricingError(Exception):
    """Raised when a booking cannot be priced."""


def load_config() -> dict:
    """Load pricing configuration from JSON."""

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError as exc:
        raise PricingError(
            "Pricing configuration file was not found."
        ) from exc

    except json.JSONDecodeError as exc:
        raise PricingError(
            "Pricing configuration is invalid JSON."
        ) from exc


def calculate_percentage(
    amount_paise: int,
    percentage: int,
) -> int:
    """
    Calculate a percentage using integer paise.

    Any fractional paisa is truncated.
    This avoids floating-point money calculations.
    """

    return (amount_paise * percentage) // 100


def calculate_price(
    booking: BookingRequest,
    config: dict | None = None,
) -> dict:
    """
    Calculate the complete price for a cinema booking.

    Pricing order:

    1. Validate cinema.
    2. Validate show.
    3. Validate ticket tier.
    4. Validate tier availability.
    5. Calculate ticket subtotal.
    6. Apply festival discount.
    7. Apply member discount.
    8. Apply member discount cap.
    9. Add convenience fee.
    10. Calculate GST on discounted subtotal + convenience fee.
    11. Return itemized bill.

    All monetary calculations use integer paise.
    """

    if config is None:
        config = load_config()

    # ============================================================
    # VALIDATE CINEMA
    # ============================================================

    cinema = config.get("cinemas", {}).get(
        booking.cinema_id
    )

    if cinema is None:
        raise PricingError(
            f"Cinema '{booking.cinema_id}' does not exist."
        )

    # ============================================================
    # VALIDATE SHOW
    # ============================================================

    show = cinema.get("shows", {}).get(
        booking.show_id
    )

    if show is None:
        raise PricingError(
            f"Show '{booking.show_id}' does not exist."
        )

    # ============================================================
    # CALCULATE TICKET SUBTOTAL
    # ============================================================

    ticket_lines = []

    subtotal_paise = 0
    total_tickets = 0

    for ticket in booking.tickets:

        tier_name = ticket.tier.value

        tier = show.get("tiers", {}).get(
            tier_name
        )

        # --------------------------------------------------------
        # INVALID TIER
        # --------------------------------------------------------

        if tier is None:
            raise PricingError(
                f"Ticket tier '{tier_name}' does not exist."
            )

        # --------------------------------------------------------
        # SOLD-OUT TIER
        # --------------------------------------------------------

        if not tier.get("available", False):
            raise PricingError(
                f"Ticket tier '{tier_name}' is sold out."
            )

        # --------------------------------------------------------
        # AVAILABLE SEAT COUNT
        # --------------------------------------------------------

        available_seats = tier.get(
            "available_seats",
            0,
        )

        if available_seats <= 0:
            raise PricingError(
                f"Ticket tier '{tier_name}' is sold out."
            )

        # --------------------------------------------------------
        # QUANTITY CHECK
        # --------------------------------------------------------

        quantity = ticket.quantity

        if quantity > available_seats:
            raise PricingError(
                f"Only {available_seats} "
                f"{tier_name} seats are available."
            )

        # --------------------------------------------------------
        # PRICE CALCULATION
        # --------------------------------------------------------

        price_paise = tier["price_paise"]

        line_total_paise = (
            price_paise * quantity
        )

        ticket_lines.append(
            {
                "tier": tier_name,
                "quantity": quantity,
                "unit_price_paise": price_paise,
                "line_total_paise": line_total_paise,
                "available_seats": available_seats,
            }
        )

        subtotal_paise += line_total_paise
        total_tickets += quantity

    # ============================================================
    # FESTIVAL DISCOUNT
    # ============================================================

    festival_discount_paise = min(
        config["offers"]["festival_discount_paise"],
        subtotal_paise,
    )

    after_festival_paise = (
        subtotal_paise
        - festival_discount_paise
    )

    # ============================================================
    # MEMBER DISCOUNT
    # ============================================================

    member_discount_paise = 0

    if booking.is_member:

        discount_percent = config["offers"][
            "member_discount_percent"
        ]

        discount_cap_paise = config["offers"][
            "member_discount_cap_paise"
        ]

        member_discount_paise = calculate_percentage(
            after_festival_paise,
            discount_percent,
        )

        # Apply maximum discount cap
        member_discount_paise = min(
            member_discount_paise,
            discount_cap_paise,
        )

    # ============================================================
    # DISCOUNTED SUBTOTAL
    # ============================================================

    discounted_subtotal_paise = (
        after_festival_paise
        - member_discount_paise
    )

    # ============================================================
    # CONVENIENCE FEE
    # ============================================================

    convenience_fee_per_ticket_paise = config[
        "convenience_fee_per_ticket_paise"
    ]

    convenience_fee_paise = (
        total_tickets
        * convenience_fee_per_ticket_paise
    )

    # ============================================================
    # GST
    # ============================================================

    taxable_amount_paise = (
        discounted_subtotal_paise
        + convenience_fee_paise
    )

    gst_percent = config["gst_percent"]

    gst_paise = calculate_percentage(
        taxable_amount_paise,
        gst_percent,
    )

    # ============================================================
    # FINAL TOTAL
    # ============================================================

    final_total_paise = (
        discounted_subtotal_paise
        + convenience_fee_paise
        + gst_paise
    )

    # ============================================================
    # RESPONSE / ITEMIZED BILL
    # ============================================================

    return {
        "cinema_id": booking.cinema_id,
        "show_id": booking.show_id,

        "tickets": ticket_lines,

        "total_tickets": total_tickets,

        "subtotal_paise": subtotal_paise,

        "festival_discount_paise": (
            festival_discount_paise
        ),

        "member_discount_paise": (
            member_discount_paise
        ),

        "discounted_subtotal_paise": (
            discounted_subtotal_paise
        ),

        "convenience_fee_paise": (
            convenience_fee_paise
        ),

        "taxable_amount_paise": (
            taxable_amount_paise
        ),

        "gst_paise": gst_paise,

        "final_total_paise": final_total_paise,

        "currency": "INR",
    }
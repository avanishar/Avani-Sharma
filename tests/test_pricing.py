import pytest
from pydantic import ValidationError

from backend.models import BookingRequest
from backend.pricing_engine import PricingError, calculate_price


# ============================================================
# HELPER
# ============================================================

def make_booking(
    tickets,
    is_member=False,
    cinema_id="C001",
    show_id="S001",
):
    return BookingRequest(
        cinema_id=cinema_id,
        show_id=show_id,
        tickets=tickets,
        is_member=is_member,
    )


# ============================================================
# BASIC PRICING
# ============================================================

def test_single_silver_ticket():

    booking = make_booking(
        [
            {
                "tier": "SILVER",
                "quantity": 1,
            }
        ]
    )

    result = calculate_price(booking)

    assert result["subtotal_paise"] == 15000
    assert result["festival_discount_paise"] == 5000
    assert result["discounted_subtotal_paise"] == 10000
    assert result["convenience_fee_paise"] == 2000
    assert result["taxable_amount_paise"] == 12000
    assert result["gst_paise"] == 2160
    assert result["final_total_paise"] == 14160


def test_multiple_ticket_tiers():

    booking = make_booking(
        [
            {
                "tier": "SILVER",
                "quantity": 2,
            },
            {
                "tier": "GOLD",
                "quantity": 1,
            },
        ]
    )

    result = calculate_price(booking)

    assert result["subtotal_paise"] == 55000
    assert result["total_tickets"] == 3


# ============================================================
# FESTIVAL DISCOUNT
# ============================================================

def test_festival_discount_is_capped_by_subtotal():

    booking = make_booking(
        [
            {
                "tier": "SILVER",
                "quantity": 1,
            }
        ]
    )

    result = calculate_price(booking)

    assert result["festival_discount_paise"] == 5000


# ============================================================
# MEMBER DISCOUNT
# ============================================================

def test_non_member_does_not_get_member_discount():

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 2,
            }
        ],
        is_member=False,
    )

    result = calculate_price(booking)

    assert result["member_discount_paise"] == 0


def test_member_gets_discount():

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 2,
            }
        ],
        is_member=True,
    )

    result = calculate_price(booking)

    assert result["member_discount_paise"] == 4500


def test_member_discount_cap():

    # Custom configuration is used here because the purpose
    # of this test is to verify the discount cap, not the
    # production seat availability.

    config = {
        "cinemas": {
            "C001": {
                "name": "CineVerse",
                "shows": {
                    "S001": {
                        "name": "Friday Night Show",
                        "tiers": {
                            "GOLD": {
                                "price_paise": 25000,
                                "available": True,
                                "available_seats": 100,
                            }
                        },
                    }
                },
            }
        },
        "offers": {
            "festival_discount_paise": 5000,
            "member_discount_percent": 10,
            "member_discount_cap_paise": 10000,
        },
        "convenience_fee_per_ticket_paise": 2000,
        "gst_percent": 18,
    }

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 100,
            }
        ],
        is_member=True,
    )

    result = calculate_price(
        booking,
        config=config,
    )

    assert result["member_discount_paise"] == 10000


# ============================================================
# CONVENIENCE FEE
# ============================================================

def test_convenience_fee():

    booking = make_booking(
        [
            {
                "tier": "SILVER",
                "quantity": 3,
            }
        ]
    )

    result = calculate_price(booking)

    assert result["convenience_fee_paise"] == 6000


# ============================================================
# GST
# ============================================================

def test_gst_is_calculated():

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 2,
            }
        ]
    )

    result = calculate_price(booking)

    assert result["taxable_amount_paise"] == 49000
    assert result["gst_paise"] == 8820


# ============================================================
# COMPLETE CALCULATION
# ============================================================

def test_complete_member_booking():

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 2,
            }
        ],
        is_member=True,
    )

    result = calculate_price(booking)

    assert result["subtotal_paise"] == 50000
    assert result["festival_discount_paise"] == 5000
    assert result["member_discount_paise"] == 4500
    assert result["discounted_subtotal_paise"] == 40500
    assert result["convenience_fee_paise"] == 4000
    assert result["taxable_amount_paise"] == 44500
    assert result["gst_paise"] == 8010
    assert result["final_total_paise"] == 52510


# ============================================================
# INVALID CINEMA / SHOW
# ============================================================

def test_invalid_cinema():

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 1,
            }
        ],
        cinema_id="INVALID",
    )

    with pytest.raises(PricingError):
        calculate_price(booking)


def test_invalid_show():

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 1,
            }
        ],
        show_id="INVALID",
    )

    with pytest.raises(PricingError):
        calculate_price(booking)


# ============================================================
# VALIDATION
# ============================================================

def test_zero_quantity_rejected():

    with pytest.raises(ValidationError):

        BookingRequest(
            cinema_id="C001",
            show_id="S001",
            tickets=[
                {
                    "tier": "GOLD",
                    "quantity": 0,
                }
            ],
        )


def test_negative_quantity_rejected():

    with pytest.raises(ValidationError):

        BookingRequest(
            cinema_id="C001",
            show_id="S001",
            tickets=[
                {
                    "tier": "GOLD",
                    "quantity": -1,
                }
            ],
        )


def test_empty_ticket_list_rejected():

    with pytest.raises(ValidationError):

        BookingRequest(
            cinema_id="C001",
            show_id="S001",
            tickets=[],
        )


def test_non_integer_quantity_rejected():

    with pytest.raises(ValidationError):

        BookingRequest(
            cinema_id="C001",
            show_id="S001",
            tickets=[
                {
                    "tier": "GOLD",
                    "quantity": 2.5,
                }
            ],
        )


def test_string_quantity_rejected():

    with pytest.raises(ValidationError):

        BookingRequest(
            cinema_id="C001",
            show_id="S001",
            tickets=[
                {
                    "tier": "GOLD",
                    "quantity": "2",
                }
            ],
        )


def test_duplicate_tier_rejected():

    with pytest.raises(ValidationError):

        BookingRequest(
            cinema_id="C001",
            show_id="S001",
            tickets=[
                {
                    "tier": "GOLD",
                    "quantity": 1,
                },
                {
                    "tier": "GOLD",
                    "quantity": 2,
                },
            ],
        )


def test_huge_quantity_rejected():

    with pytest.raises(ValidationError):

        BookingRequest(
            cinema_id="C001",
            show_id="S001",
            tickets=[
                {
                    "tier": "GOLD",
                    "quantity": 101,
                }
            ],
        )


def test_invalid_member_value_rejected():

    with pytest.raises(ValidationError):

        BookingRequest(
            cinema_id="C001",
            show_id="S001",
            tickets=[
                {
                    "tier": "GOLD",
                    "quantity": 1,
                }
            ],
            is_member="yes",
        )


# ============================================================
# SOLD OUT
# ============================================================

def test_sold_out_tier():

    config = {
        "cinemas": {
            "C001": {
                "name": "CineVerse",
                "shows": {
                    "S001": {
                        "name": "Friday Night Show",
                        "tiers": {
                            "GOLD": {
                                "price_paise": 25000,
                                "available": False,
                                "available_seats": 0,
                            }
                        },
                    }
                },
            }
        },
        "offers": {
            "festival_discount_paise": 5000,
            "member_discount_percent": 10,
            "member_discount_cap_paise": 10000,
        },
        "convenience_fee_per_ticket_paise": 2000,
        "gst_percent": 18,
    }

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 1,
            }
        ]
    )

    with pytest.raises(
        PricingError,
        match="sold out",
    ):
        calculate_price(
            booking,
            config=config,
        )


# ============================================================
# AVAILABILITY
# ============================================================

def test_quantity_above_available_seats_rejected():

    config = {
        "cinemas": {
            "C001": {
                "name": "CineVerse",
                "shows": {
                    "S001": {
                        "name": "Friday Night Show",
                        "tiers": {
                            "GOLD": {
                                "price_paise": 25000,
                                "available": True,
                                "available_seats": 5,
                            }
                        },
                    }
                },
            }
        },
        "offers": {
            "festival_discount_paise": 5000,
            "member_discount_percent": 10,
            "member_discount_cap_paise": 10000,
        },
        "convenience_fee_per_ticket_paise": 2000,
        "gst_percent": 18,
    }

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 6,
            }
        ]
    )

    with pytest.raises(
        PricingError,
        match="Only 5 GOLD seats are available",
    ):
        calculate_price(
            booking,
            config=config,
        )


def test_available_seats_can_be_booked():

    config = {
        "cinemas": {
            "C001": {
                "name": "CineVerse",
                "shows": {
                    "S001": {
                        "name": "Friday Night Show",
                        "tiers": {
                            "GOLD": {
                                "price_paise": 25000,
                                "available": True,
                                "available_seats": 5,
                            }
                        },
                    }
                },
            }
        },
        "offers": {
            "festival_discount_paise": 5000,
            "member_discount_percent": 10,
            "member_discount_cap_paise": 10000,
        },
        "convenience_fee_per_ticket_paise": 2000,
        "gst_percent": 18,
    }

    booking = make_booking(
        [
            {
                "tier": "GOLD",
                "quantity": 5,
            }
        ]
    )

    result = calculate_price(
        booking,
        config=config,
    )

    assert result["total_tickets"] == 5
    assert result["subtotal_paise"] == 125000
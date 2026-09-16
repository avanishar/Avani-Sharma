from backend.price_importer import (
    import_price_list,
    normalize_tier_name,
    parse_price_to_paise,
)


def test_normalize_tier_name():

    assert normalize_tier_name(" Silver ") == "SILVER"
    assert normalize_tier_name("gold") == "GOLD"
    assert normalize_tier_name("  Recliner  ") == "RECLINER"


def test_price_parsing():

    assert parse_price_to_paise("₹150") == 15000
    assert parse_price_to_paise("250.00") == 25000
    assert parse_price_to_paise("₹400.50") == 40050


def test_negative_price_rejected():

    try:
        parse_price_to_paise("-200")
        assert False
    except ValueError:
        assert True


def test_blank_price_rejected():

    try:
        parse_price_to_paise("")
        assert False
    except ValueError:
        assert True


def test_messy_price_list_import():

    records = [
        {
            "name": "Silver",
            "price": "₹150",
        },
        {
            "name": " GOLD ",
            "price": "250.00",
        },
        {
            "name": "gold",
            "price": "₹250",
        },
        {
            "name": "Recliner",
            "price": "400",
        },
        {
            "name": "RECLINER",
            "price": "₹400.00",
        },
        {
            "name": "Silver",
            "price": "",
        },
        {
            "name": "Balcony",
            "price": "-200",
        },
        {
            "name": "",
            "price": "300",
        },
        {
            "name": "Premium",
            "price": "abc",
        },
    ]

    result = import_price_list(records)

    assert result["report"]["imported"] == 9
    assert result["report"]["accepted"] == 3
    assert result["report"]["duplicates"] == 2
    assert result["report"]["rejected"] == 4


def test_duplicate_names_are_case_insensitive():

    records = [
        {
            "name": "Silver",
            "price": "150",
        },
        {
            "name": "silver",
            "price": "160",
        },
    ]

    result = import_price_list(records)

    assert len(result["cleaned_prices"]) == 1
    assert result["cleaned_prices"][0]["price_paise"] == 15000
    assert result["report"]["duplicates"] == 1


def test_unknown_tier_rejected():

    records = [
        {
            "name": "Balcony",
            "price": "200",
        }
    ]

    result = import_price_list(records)

    assert result["report"]["accepted"] == 0
    assert result["report"]["rejected"] == 1
# CineVerse — Cinema Ticket Pricing Engine

A reusable cinema ticket pricing engine built around the problem of getting a booking total right down to the exact paisa.

The project handles different ticket tiers, seat availability, festival and membership discounts, convenience fees, GST, validation, and a clear itemized bill.

It also includes the additional price-list import challenge: messy seat-class names and prices are cleaned, normalized, de-duplicated, and rejected records are reported instead of silently being ignored.

---

## What this project does

The application has two main parts.

### 1. Cinema ticket pricing

A customer can:

- Select a cinema show
- Choose Silver, Gold, or Recliner tickets
- See the current number of available seats
- Select multiple tickets
- Apply CineVerse membership
- Get the festival discount
- Calculate the convenience fee
- Calculate GST
- See the complete line-by-line bill
- Get the final amount in exact paise

Sold-out tiers cannot be booked, and the backend checks availability again even if someone bypasses the frontend.

### 2. Messy price-list importer

The importer accepts a price list that may contain:

- Different capitalization
- Extra spaces
- Currency symbols
- Decimal prices
- Duplicate seat-class names
- Blank prices
- Negative prices
- Unknown seat classes
- Invalid price formats

The importer cleans the valid records and reports:

- How many records were imported
- How many were accepted
- How many were duplicates
- How many were rejected
- Why individual records were rejected

---

## Example

A messy input such as:

```json
[
  {"name": "Silver", "price": "₹150"},
  {"name": " GOLD ", "price": "250.00"},
  {"name": "gold", "price": "₹250"},
  {"name": "Recliner", "price": "400"},
  {"name": "RECLINER", "price": "₹400.00"},
  {"name": "Silver", "price": ""},
  {"name": "Balcony", "price": "-200"},
  {"name": "", "price": "300"},
  {"name": "Premium", "price": "abc"}
]
```

is cleaned into:

```text
SILVER      ₹150.00
GOLD        ₹250.00
RECLINER    ₹400.00
```

while duplicates and invalid records are reported separately.

---

## Pricing approach

Money is stored as integer paise instead of floating-point values.

For example:

```text
₹150.00 → 15000 paise
₹250.00 → 25000 paise
```

The pricing flow is:

```text
Ticket prices
     ↓
Ticket subtotal
     ↓
Festival discount
     ↓
Member discount
     ↓
Member discount cap
     ↓
Convenience fee
     ↓
GST
     ↓
Final total
```

This keeps the calculation deterministic and avoids floating-point money errors.

---

## Current configuration

The sample configuration used by the project contains:

| Ticket tier | Price | Availability |
|---|---:|---:|
| Silver | ₹150 | 42 seats |
| Gold | ₹250 | 18 seats |
| Recliner | ₹400 | Sold out |

Current offers:

- Festival discount: ₹50 flat discount
- Member discount: 10%
- Member discount cap: ₹100
- Convenience fee: ₹20 per ticket
- GST: 18%

These values are configuration values used for the demonstration and are not intended to represent a real cinema's pricing.

---

## Tech stack

- Python 3
- FastAPI
- Pydantic
- Pytest
- HTML
- CSS
- JavaScript
- JSON configuration

---

## Project structure

```text
Avani-Sharma/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── pricing_engine.py
│   └── price_importer.py
│
├── data/
│   └── pricing.json
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── tests/
│   ├── test_pricing.py
│   └── test_price_importer.py
│
├── README.md
├── REASONING.md
├── AI_LOGS.md
└── .gitignore
```

---

## Running the project

### 1. Create and activate the virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn pydantic pytest
```

### 3. Run the tests

```bash
python -m pytest -q
```

The current implementation has:

```text
29 passed
```

### 4. Start the application

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Then open the forwarded port in the browser.

---

## API endpoints

### Health check

```text
GET /health
```

Returns the current service status.

### Calculate booking price

```text
POST /calculate-price
```

Example:

```json
{
  "cinema_id": "C001",
  "show_id": "S001",
  "tickets": [
    {
      "tier": "SILVER",
      "quantity": 1
    }
  ],
  "is_member": false
}
```

### Import a messy price list

```text
POST /import-price-list
```

Accepts a JSON array of price records and returns the cleaned list and import report.

---

## Validation and edge cases

The backend validates:

- Missing cinema
- Missing show
- Invalid ticket tier
- Sold-out ticket tier
- Quantity of zero
- Negative quantity
- Non-integer quantity
- Excessive quantity
- Duplicate ticket tiers
- Invalid membership values
- Booking more seats than are available
- Empty ticket lists

The importer additionally validates:

- Blank seat-class names
- Unknown seat classes
- Blank prices
- Negative prices
- Invalid price formats
- Duplicate seat-class names

---

## Testing

The project uses Pytest for both the pricing engine and the price importer.

The test suite covers:

- Basic ticket pricing
- Multiple ticket tiers
- Festival discount
- Member discount
- Discount cap
- Convenience fee
- GST
- Complete booking calculations
- Invalid cinema/show
- Quantity validation
- Duplicate tiers
- Sold-out tiers
- Seat availability
- Price normalization
- Duplicate price-list records
- Invalid price records
- Blank values
- Negative prices
- Unknown seat classes

Current result:

```text
29 passed
```

---

## Design decisions

A few rules were not numerically specified in the problem statement, so the project treats them as explicit configuration/assumptions rather than hiding them inside the code.

The main assumptions are documented in `REASONING.md`.

The most important one is that the pricing engine is the single source of truth. The frontend sends the booking to the backend instead of reimplementing the pricing calculation in JavaScript.

---

## Frontend

The frontend is intentionally kept as a single booking page.

It provides:

- CineVerse branding
- Show information
- Seat-tier cards
- Availability information
- Quantity controls
- Membership toggle
- Booking summary
- Exact final total
- Messy price-list importer
- Import statistics
- Cleaned price list
- Rejected-record report

The UI is there to make the engine easy to demonstrate; the actual pricing logic stays in Python.

---

## Notes

This project was built as a reusable pricing engine rather than a hard-coded calculation for one particular cinema show.

Cinema, show, ticket prices, availability, offers, fees, and tax settings are kept in configuration so the pricing logic can be reused with different data.

---

## Author

Built as a Builder Round project demonstrating backend pricing logic, validation, testing, and a small working frontend.

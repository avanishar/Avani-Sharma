# AI Logs

## AI-Assisted Development Log

This file records the interaction with AI during the development of the cinema ticket pricing engine.

---

## 1. Understanding the Assignment

### User

I need to build the "Friday night at the multiplex" pricing engine assignment.

The multiplex booking counter has Silver, Gold and Recliner ticket tiers at different prices. Some tiers can sell out before the show and should not be bookable.

There is a flat festival discount and a percentage discount for members with a cap. Every booking also has a per-ticket convenience fee and GST.

The final bill needs to be accurate to the exact paisa and should show a clear line-by-line breakup.

The application should work for different cinemas and shows rather than being hard-coded for one show.

There is also an additional challenge: import a messy seat-class price list containing duplicate names in different cases, inconsistent price formats, blank values and negative prices. The application should clean the list and report imported, de-duplicated and rejected records.

### AI

The project should be separated into a pricing engine, validation layer, configuration/data, API and frontend.

A suitable structure is:

```text
backend/
    main.py
    models.py
    pricing_engine.py
    price_importer.py

data/
    pricing.json

frontend/
    index.html
    style.css
    script.js

tests/
    test_pricing.py
    test_price_importer.py
```

The pricing engine should remain the source of truth for all money calculations.

---

## 2. Technology and Architecture

### User

I want to build this in GitHub Codespaces. I want the backend in Python and a clean frontend.

### AI

A simple stack is appropriate:

* Python
* FastAPI
* Pydantic
* Pytest
* HTML/CSS/JavaScript
* JSON configuration

The request flow can be:

```text
Frontend
   ↓
FastAPI
   ↓
Pydantic validation
   ↓
Pricing engine
   ↓
Configuration
   ↓
Itemized response
   ↓
Frontend
```

Money should be represented internally as integer paise instead of floating-point values.

For example:

```text
₹150.00 = 15000 paise
```

This avoids floating-point precision problems.

---

## 3. Creating the Project Structure

### User

How do I create the files in the backend?

### AI

The backend can contain:

```text
backend/
├── __init__.py
├── main.py
├── models.py
├── pricing_engine.py
└── price_importer.py
```

The importer can be created with:

```bash
touch backend/price_importer.py
```

The tests can be placed under:

```text
tests/
```

---

## 4. Pricing Models

### User

I need the full models code.

### AI

The booking models should validate ticket tiers, quantities, duplicate tiers and membership values.

The ticket tiers are:

```text
SILVER
GOLD
RECLINER
```

Quantity should be a strict integer and should be greater than zero.

Duplicate ticket tiers should be rejected rather than silently merged.

Membership should also use strict boolean validation.

---

## 5. Pricing Engine

### User

I provided the pricing engine code and asked for the full new code.

### AI

The pricing engine should follow this order:

```text
1. Calculate ticket subtotal
2. Apply festival discount
3. Apply member discount
4. Apply member discount cap
5. Add convenience fee
6. Calculate GST
7. Return final total
```

All money calculations should use integer paise.

The engine should check:

* Cinema exists
* Show exists
* Ticket tier exists
* Ticket tier is available
* Requested quantity does not exceed available seats

The response should contain the ticket lines, subtotal, discounts, fee, GST and final total.

---

## 6. Initial Test Problems

### User

My tests initially gave:

```text
ModuleNotFoundError: No module named 'backend'
```

### AI

The backend directory needs to be recognized as a Python package.

Creating:

```text
backend/__init__.py
```

fixes the package import issue.

The test suite can then import:

```python
from backend.models import BookingRequest
from backend.pricing_engine import calculate_price
```

---

## 7. Validation Test Failures

### User

Some tests failed:

```text
test_duplicate_tier_rejected
test_huge_quantity_rejected
test_invalid_member_value_rejected
```

They were not raising `ValidationError`.

### AI

The Pydantic models need stricter validation.

Use strict integer and boolean types so values such as:

```text
"2"
2.5
"yes"
```

are not silently converted.

Also add validation for duplicate ticket tiers and a maximum quantity.

---

## 8. Sold-Out Tier Test Failure

### User

The multiple-tier tests failed because Recliner was sold out.

### AI

That is because the configuration correctly says Recliner is unavailable.

Tests that are checking normal multi-tier pricing should either use available tiers or provide a test configuration where Recliner is available.

The sold-out test should separately verify that attempting to book an unavailable tier raises a pricing error.

---

## 9. Availability Counts

### User

I want the frontend to show how many seats are available and make sure a customer cannot book more than that.

### AI

The configuration can contain:

```json
"SILVER": {
    "price_paise": 15000,
    "available": true,
    "available_seats": 42
}
```

and:

```json
"GOLD": {
    "price_paise": 25000,
    "available": true,
    "available_seats": 18
}
```

while Recliner can have:

```json
"RECLINER": {
    "price_paise": 40000,
    "available": false,
    "available_seats": 0
}
```

The backend must reject quantities above the available seat count.

The frontend can also disable the quantity control when the configured availability has been reached.

---

## 10. Cinema Name

### User

Change the cinema name. Don't use Auriga as the customer-facing cinema name.

### AI

The customer-facing cinema name was changed to:

```text
CineVerse
```

The sample show remains:

```text
Friday Night Show
```

with the movie:

```text
Friday Night at the Multiplex
```

---

## 11. Frontend

### User

I want the frontend to look like a real ticket-booking website.

It should show the offers, available seats, current show, different seat prices and allow booking.

### AI

The frontend was designed as a single cinema booking page containing:

* CineVerse branding
* Friday Night show information
* Screen and show time
* Festival offer
* Member offer
* Silver ticket card
* Gold ticket card
* Recliner sold-out card
* Quantity controls
* Membership toggle
* Booking summary
* Line-by-line price breakdown
* Final total

The frontend does not independently calculate discounts or GST.

Instead, it sends the booking to:

```text
POST /calculate-price
```

and displays the result returned by the Python pricing engine.

This prevents the frontend and backend from having two separate pricing implementations.

---

## 12. CSS and Static File Problem

### User

The CSS was not loading correctly.

I checked the server using curl and found that the CSS URL was returning HTML instead of CSS.

### AI

The static file configuration needed to be corrected.

The frontend files were configured to be served under:

```text
/static/
```

so:

```text
/static/style.css
/static/script.js
```

are separate from:

```text
/
```

which serves the main HTML page.

The frontend JavaScript was also changed to use the relative API path:

```javascript
const API_URL = "/calculate-price";
```

This avoids hard-coding the Codespaces URL.

---

## 13. Messy Price-List Importer

### User

The assignment now has an additional twist.

The system must import a messy seat-class price list with:

* Duplicate names in different cases
* Inconsistent price formats
* Blank values
* Negative prices

It should clean the list and report what was imported, de-duplicated and rejected.

### AI

A separate file was created:

```text
backend/price_importer.py
```

The importer performs:

```text
Input records
     ↓
Normalize names
     ↓
Validate seat class
     ↓
Parse price
     ↓
Reject invalid records
     ↓
Detect duplicates
     ↓
Return cleaned list
```

Names are normalized by trimming whitespace and converting them to uppercase.

For example:

```text
Silver
silver
 SILVER
```

all become:

```text
SILVER
```

The first valid occurrence is kept when a normalized duplicate is found.

---

## 14. Importer Price Handling

### User

The importer also needs to handle ₹ symbols, decimal values, blank prices and negative prices.

### AI

Prices are converted to integer paise.

Examples:

```text
₹150       → 15000
250.00     → 25000
₹400.50    → 40050
```

Negative prices are rejected.

Blank prices are rejected.

Invalid formats are rejected.

Unknown seat classes such as:

```text
BALCONY
PREMIUM
```

are also rejected because the supported classes are:

```text
SILVER
GOLD
RECLINER
```

---

## 15. Importer Tests

### User

I want tests for the importer.

### AI

Tests were added for:

* Seat-class normalization
* Price parsing
* Negative prices
* Blank prices
* Messy price lists
* Duplicate names
* Unknown seat classes

The importer also reports:

```text
Imported
Accepted
Duplicates
Rejected
```

and keeps rejected records with their row number and reason.

---

## 16. Frontend Importer

### User

I also want the messy price-list importer visible in the frontend.

### AI

A new section was added to the frontend where a JSON price list can be pasted.

The frontend sends the data to:

```text
POST /import-price-list
```

The result displays:

```text
Imported
Accepted
Duplicates
Rejected
```

along with:

* Cleaned price list
* Rejected records
* Rejection reasons

This makes the additional challenge visible during the project demonstration.

---

## 17. Testing the Application

### User

Everything worked now. I ran the tests.

### User

The final test result was:

```text
29 passed in 0.15s
```

### AI

The 29 passing tests confirm that the pricing and importer test suites are working.

The important manual tests were also checked:

* Silver booking
* Gold booking
* Member discount
* Festival discount
* Recliner sold-out behavior
* Seat availability
* Price-list importing
* Duplicate detection
* Rejected records
* Frontend booking summary

---

## 18. Port 8000 Problem

### User

When I started Uvicorn I got:

```text
ERROR: [Errno 98] error while attempting to bind on address
('0.0.0.0', 8000): [errno 98] address already in use
```

### AI

This means another process is already using port 8000.

It does not indicate a problem with the pricing engine.

The existing server can be checked using:

```bash
curl http://localhost:8000/health
```

If the existing server is not needed, it can be stopped with:

```bash
pkill -f uvicorn
```

and restarted with:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## 19. Git and Documentation

### User

I need README, REASONING.md and AI_LOGS.md.

### AI

The documentation should explain:

* What the project does
* How to run it
* Project structure
* Pricing approach
* Money handling
* Validation
* Availability
* Importer
* Testing
* Design decisions

`README.md` should be the main project documentation.

`REASONING.md` should explain the engineering decisions.

`AI_LOGS.md` should contain the AI conversation required by the assignment.

---

## 20. Git Commit and Push

### User

I committed the project with:

```text
Complete CineVerse pricing engine
```

and pushed it to GitHub.

### AI

The project should be checked with:

```bash
git status
```

and:

```bash
python -m pytest -q
```

The final test result was:

```text
29 passed
```

---

## 21. Git Rebase Conflict

### User

The documentation push was rejected with:

```text
! [rejected] main -> main (fetch first)
```

### AI

The remote branch had changed, so the local branch needed to be synchronized.

The suggested approach was:

```bash
git pull --rebase origin main
```

A conflict occurred in:

```text
README.md
```

The documentation files were then staged and the rebase was continued.

---

## 22. Final Git Result

### User

The rebase completed successfully:

```text
Successfully rebased and updated refs/heads/main.
```

The final push succeeded:

```text
main -> main
```

The repository was then up to date.

### User

The final automated test result was:

```text
29 passed
```

---

## 23. Final Project State

The final project contains:

```text
backend/
├── __init__.py
├── main.py
├── models.py
├── pricing_engine.py
└── price_importer.py

data/
└── pricing.json

frontend/
├── index.html
├── script.js
└── style.css

tests/
├── test_pricing.py
└── test_price_importer.py

README.md
REASONING.md
AI_LOGS.md
.gitignore
```

The application provides a reusable cinema pricing engine with:

* Configurable ticket tiers
* Seat availability
* Sold-out handling
* Festival discount
* Member discount
* Discount cap
* Convenience fee
* GST
* Exact-paise calculations
* Itemized billing
* Validation
* Automated tests
* Messy price-list importing
* Duplicate detection
* Invalid-data reporting
* Working frontend

Final automated test result:

```text
29 passed
```

---

## End of AI Development Log

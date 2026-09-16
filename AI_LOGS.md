# AI Logs

## How I used AI

I used AI mainly as a development assistant while building and debugging the project.

I did not use it as a replacement for testing the application. I ran the code myself, checked the errors, changed the implementation, and verified the final result with Pytest and the browser.

The conversation was especially useful for breaking the project into smaller pieces because there were several parts to handle: pricing, validation, availability, the messy price-list importer, API endpoints, and the frontend.

---

## 1. Understanding the problem

I first used AI to break the assignment into smaller requirements.

The main points identified were:

- Ticket tiers
- Seat availability
- Festival discount
- Member percentage discount
- Discount cap
- Convenience fee
- GST
- Exact-paisa calculation
- Itemized billing
- Validation
- Testing
- Configurable pricing

Later, the additional challenge about importing a messy seat-class price list was added.

---

## 2. Designing the project structure

AI helped me settle on a simple structure:

```text
backend/
data/
frontend/
tests/
```

The main backend responsibilities became:

```text
models.py
    ↓
Request validation

pricing_engine.py
    ↓
Business/pricing logic

price_importer.py
    ↓
Messy price-list cleaning

main.py
    ↓
FastAPI endpoints
```

This separation made debugging easier because pricing problems were not mixed with frontend code.

---

## 3. Money calculation

One of the important decisions was using integer paise instead of floating-point values.

AI suggested treating:

```text
₹150.00
```

as:

```text
15000 paise
```

I kept this approach because it makes the final calculation deterministic and fits the requirement for exact paisa-level totals.

---

## 4. Validation and testing

During testing, several issues appeared.

For example, some tests initially failed because:

- Sold-out Recliner tickets were being used in tests that expected them to be available.
- Pydantic was not rejecting some inputs in the way the tests expected.
- Duplicate ticket tiers were not being rejected.
- Large quantities were not being limited.
- String quantities were being converted instead of rejected.
- Boolean values needed stricter validation.

I used the test failures to identify these issues and then changed the models and tests accordingly.

The final result was:

```text
29 passed
```

---

## 5. Debugging the frontend

The frontend initially had problems loading correctly.

There were also issues with the API URL when running inside GitHub Codespaces.

The frontend was eventually changed to use:

```javascript
const API_URL = "/calculate-price";
```

instead of relying on a hard-coded Codespaces URL.

This made the frontend use the same origin as the FastAPI application.

---

## 6. Static file issue

At one point the browser displayed the HTML without the CSS being applied.

The problem turned out to be the way the static files were being served.

I checked the response from the server using `curl` and found that the CSS path was returning HTML instead of the stylesheet.

The frontend/server setup was then corrected so that the browser could load:

```text
/static/style.css
/static/script.js
```

separately from:

```text
/
```

for the main HTML page.

---

## 7. Adding the messy price-list importer

The additional challenge required handling deliberately messy data.

AI helped me design a separate importer rather than putting the cleaning logic inside the pricing engine.

The importer now handles:

```text
Case differences
Extra spaces
Currency symbols
Decimal prices
Blank values
Negative prices
Unknown seat classes
Duplicate names
Invalid price formats
```

It also reports what happened to every imported record.

For duplicates, the chosen rule is:

```text
First valid occurrence wins.
```

---

## 8. Frontend for the importer

After the backend importer was working and tested, AI helped me connect it to the frontend.

The page now has a section where a messy JSON price list can be pasted and imported.

The UI shows:

```text
Imported
Accepted
Duplicates
Rejected
```

It also displays the cleaned price list and the reasons for rejected records.

---

## 9. What I checked myself

I did not consider the project finished just because the code looked correct.

I checked:

- Pytest results
- FastAPI startup
- Frontend loading
- Ticket selection
- Sold-out Recliner behavior
- Member discount
- Booking total
- Price-list importer
- Duplicate detection
- Rejected records
- GitHub/Codespaces behavior

The final automated test result was:

```text
29 passed
```

The frontend was also tested manually in the browser.

---

## 10. Where AI was most useful

AI was most useful for:

- Breaking a large assignment into smaller tasks
- Explaining Python/FastAPI errors
- Suggesting test cases
- Debugging validation problems
- Structuring the importer
- Connecting the frontend to the backend
- Finding why static files were not loading
- Improving the frontend presentation

The actual implementation was repeatedly tested and adjusted based on what happened in the project rather than blindly copying generated code.

---

## 11. Final result

The final project contains:

- A reusable pricing engine
- Configurable cinema/show data
- Integer-paise calculations
- Ticket availability validation
- Discount handling
- Convenience fee and GST
- Itemized booking bills
- A messy price-list importer
- Duplicate and invalid-data reporting
- Automated tests
- A working frontend

Final test result:

```text
29 passed
```
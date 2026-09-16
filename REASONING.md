# Reasoning Behind the Solution

## 1. How I approached the problem

I treated the pricing calculation as the core of the application. The frontend is mainly there to make the system easy to use and demonstrate, while the backend is responsible for deciding whether a booking is valid and what it should cost.

My main goal was to make the pricing logic:

* Correct
* Reusable
* Configurable
* Easy to test
* Safe for money calculations
* Independent of the frontend

The overall flow is:

```text
Booking Request
      ↓
Input Validation
      ↓
Cinema / Show Validation
      ↓
Ticket Tier Validation
      ↓
Seat Availability Check
      ↓
Ticket Subtotal
      ↓
Festival Discount
      ↓
Member Discount + Cap
      ↓
Convenience Fee
      ↓
GST
      ↓
Itemized Bill
```

---

## 2. Why the pricing logic is in the backend

I decided not to calculate prices independently in JavaScript.

The frontend only collects the customer's choices and sends them to:

```text
POST /calculate-price
```

The Python pricing engine then performs the actual calculation.

This gives the application one source of truth.

If the frontend calculated GST or discounts separately, there would be a risk that the frontend and backend could produce different totals.

Keeping the business rules in the backend also means the same pricing engine could be used by another frontend or a cinema counter application later.

---

## 3. Why I used integer paise

Money calculations need to be exact.

Instead of using floating-point values such as:

```python
150.00
```

the application stores money as integer paise:

```text
₹150.00 → 15000 paise
₹250.00 → 25000 paise
₹400.50 → 40050 paise
```

This avoids floating-point precision issues and makes the final amount deterministic.

The final response still converts the value into rupees for display, but the actual calculation is performed using integer paise.

---

## 4. Pricing order

The pricing engine follows one explicit order:

```text
1. Calculate ticket subtotal
2. Apply festival discount
3. Calculate member discount
4. Apply member discount cap
5. Add convenience fee
6. Calculate GST
7. Calculate final total
```

I kept the order explicit because changing the order of discounts, fees and taxes can change the final price.

For example, the member discount is calculated after the festival discount.

GST is calculated on:

```text
discounted ticket subtotal + convenience fee
```

This rule is implemented consistently in the pricing engine.

---

## 5. Festival discount

The festival offer is a flat discount.

The discount cannot reduce the ticket subtotal below zero.

The calculation therefore uses the smaller value between:

```text
configured festival discount
subtotal
```

For example, if the festival discount is ₹50 but the ticket subtotal is only ₹30, the discount becomes ₹30 rather than producing a negative ticket value.

---

## 6. Member discount

The member offer is percentage based.

For a member booking, the configured percentage is applied after the festival discount.

The resulting member discount is then compared with the configured maximum cap.

The actual discount is therefore:

```text
minimum(
    calculated percentage discount,
    member discount cap
)
```

This keeps the cap enforced by the backend rather than relying on the frontend to display it correctly.

---

## 7. Ticket availability

Availability is part of the business logic, so it is checked by the backend.

Each tier can contain:

```json
{
    "price_paise": 25000,
    "available": true,
    "available_seats": 18
}
```

The engine checks both:

1. Whether the tier is available.
2. Whether the requested quantity is within the available seat count.

For the sample configuration:

```text
Silver     42 seats
Gold       18 seats
Recliner    0 seats
```

Recliner is therefore treated as sold out.

The frontend also disables unavailable options, but this is only a user-interface improvement. The backend performs the real validation so that a request cannot bypass the availability rules simply by avoiding the frontend.

---

## 8. Configuration-driven pricing

I kept cinema, show, ticket, offer, fee and tax information in:

```text
data/pricing.json
```

instead of hard-coding prices throughout the Python code.

This makes the pricing engine reusable.

For example, changing a Gold ticket from ₹250 to another price should only require changing the configuration rather than rewriting the pricing algorithm.

The same approach can be extended to additional cinemas and shows.

---

## 9. Request validation

I used Pydantic models for request validation.

The booking request checks things such as:

* A cinema ID is provided.
* A show ID is provided.
* At least one ticket is selected.
* Quantity is a positive integer.
* Quantity cannot exceed the configured request limit.
* Duplicate ticket tiers are rejected.
* Membership must be a boolean value.

Business-level checks are then handled by the pricing engine.

These include:

* Cinema exists.
* Show exists.
* Ticket tier exists.
* Ticket tier is available.
* Requested quantity does not exceed available seats.

This separates basic input validation from business rules.

---

## 10. Why duplicate ticket tiers are rejected

A request such as:

```text
GOLD × 2
GOLD × 3
```

could technically be merged into:

```text
GOLD × 5
```

but I decided not to do that automatically.

Instead, duplicate tiers are rejected.

This keeps the request structure predictable and prevents accidental merging of separate lines.

A valid request should simply use:

```text
GOLD × 5
```

when five Gold tickets are required.

---

# 11. Messy price-list importer

The additional challenge was handled as a separate module:

```text
backend/price_importer.py
```

I kept it separate from the pricing engine because importing and cleaning data is a different responsibility from calculating a booking.

The importer follows:

```text
Messy Input
     ↓
Normalize Name
     ↓
Validate Seat Class
     ↓
Parse Price
     ↓
Reject Invalid Records
     ↓
Detect Duplicates
     ↓
Create Clean Price List
     ↓
Generate Import Report
```

---

## 12. Normalizing seat-class names

The input can contain names such as:

```text
Silver
silver
 SILVER
  Silver
```

These should represent the same ticket tier.

The importer therefore:

1. Removes unnecessary whitespace.
2. Converts the name to uppercase.
3. Checks it against the supported ticket tiers.

The normalized result is:

```text
SILVER
```

The same process is used for Gold and Recliner.

---

## 13. Handling duplicates

Duplicates are detected after normalization.

For example:

```text
Silver → ₹150
silver → ₹160
```

are treated as duplicates because both normalize to:

```text
SILVER
```

I chose a simple rule:

> The first valid occurrence wins.

The later record is not silently discarded. It is reported as a duplicate so that the person importing the data knows what happened.

---

## 14. Handling inconsistent prices

The importer accepts reasonable variations such as:

```text
150
"150"
"150.00"
"₹150"
"₹150.50"
```

and converts them to integer paise.

For example:

```text
₹150.50
```

becomes:

```text
15050 paise
```

This allows the pricing system to work with one consistent internal representation even when the input data is messy.

---

## 15. Rejected prices and records

The importer rejects:

* Blank prices
* Negative prices
* Invalid price formats
* Blank seat-class names
* Unknown seat classes

Instead of simply throwing away bad records, the importer reports the row and the reason for rejection.

This makes the importer useful for cleaning real-world data rather than just accepting or rejecting the entire file.

---

## 16. Why the frontend does not duplicate importer logic

The frontend sends the raw imported records to:

```text
POST /import-price-list
```

The backend performs the cleaning and validation.

The frontend then displays:

```text
Imported
Accepted
Duplicates
Rejected
```

as well as the cleaned list and rejected-record reasons.

This follows the same principle as the pricing engine: business rules remain on the backend.

---

## 17. API design

The application uses FastAPI with a small number of focused endpoints.

### Health check

```text
GET /health
```

Used to confirm that the backend is running.

### Calculate booking price

```text
POST /calculate-price
```

Receives the booking and returns the complete itemized price calculation.

### Import price list

```text
POST /import-price-list
```

Receives the messy price list and returns the cleaned data and import report.

The frontend and backend can therefore be tested independently.

---

## 18. Testing strategy

I used Pytest to test the pricing engine and importer.

The pricing tests cover:

* Single-ticket pricing
* Multiple ticket tiers
* Festival discount
* Member discount
* Member discount cap
* Convenience fee
* GST
* Complete booking calculation
* Invalid cinema
* Invalid show
* Zero quantity
* Negative quantity
* Empty ticket list
* Non-integer quantity
* String quantity
* Duplicate ticket tiers
* Excessive quantity
* Invalid member value
* Sold-out tiers
* Available-seat limits

The importer tests cover:

* Name normalization
* Price conversion
* Negative prices
* Blank prices
* Messy input
* Duplicate names
* Unknown ticket tiers

The final test run was:

```text
29 passed
```

---

## 19. Frontend design decision

I kept the frontend as a single page instead of creating several pages.

The main booking page contains:

* Movie/show information
* Current screen and time
* Offer information
* Ticket tiers
* Seat availability
* Quantity controls
* Membership option
* Booking summary
* Exact final amount
* Price-list importer

The goal was to make the core functionality easy to demonstrate without adding unnecessary complexity.

---

## 20. Handling unspecified rules

Some numerical rules in the assignment were not explicitly provided.

Instead of pretending that those values came from the assignment, I kept the sample values in configuration and treated them as project assumptions.

For example:

```text
Silver     ₹150
Gold       ₹250
Recliner   ₹400
Festival   ₹50
Member     10%
Member cap ₹100
Fee        ₹20/ticket
GST        18%
```

These are demonstration values and can be changed through configuration.

This prevents assumptions from becoming hidden business logic.

---

## 21. What I would improve with more time

The current implementation focuses on the pricing engine and the required importer.

With more time, I would consider adding:

* Persistent seat inventory
* Actual seat-number selection
* Database-backed bookings
* Booking IDs
* Multiple cinemas and shows in the UI
* CSV file upload for price lists
* Authentication
* More integration tests
* More detailed API error status handling

I intentionally kept these outside the current implementation so that the core pricing and import requirements could be completed, tested and demonstrated reliably.

---

## 22. Final outcome

The final solution is designed around one main principle:

> The backend should be able to give the same correct price every time for the same valid booking.

The frontend makes the process easy to use, while the backend owns the pricing and validation rules.

The final project successfully combines:

```text
Configuration
      +
Validation
      +
Pricing Engine
      +
Availability
      +
Price Importer
      +
Automated Tests
      +
Frontend
```

with the final automated test result:

```text
29 passed
```

# Reasoning

## How I approached the problem

I started by treating the pricing engine as the most important part of the project.

The frontend is useful for demonstrating the application, but the actual price calculation should not depend on what the browser is doing. If the frontend and backend had separate pricing calculations, they could eventually disagree.

So I decided to keep the pricing rules in Python and make the frontend call the backend whenever a booking total is needed.

The basic flow became:

```text
Booking request
      ↓
Validation
      ↓
Check cinema/show
      ↓
Check ticket tiers
      ↓
Check availability
      ↓
Calculate subtotal
      ↓
Apply discounts
      ↓
Add convenience fee
      ↓
Calculate GST
      ↓
Return itemized bill
```

---

## Why I used integer paise

Money was one of the parts I wanted to be careful with.

Using normal Python floating-point numbers for money can introduce small precision problems. Since the problem specifically asks for the exact paisa, I decided to store all money internally as integers representing paise.

For example:

```text
₹150.00 = 15000 paise
₹250.00 = 25000 paise
```

This means the calculations remain predictable and there is no need to round floating-point values at different stages.

---

## Pricing order

I chose one explicit pricing order and kept it in the pricing engine:

```text
1. Calculate ticket subtotal
2. Apply festival discount
3. Apply member discount
4. Apply member discount cap
5. Add convenience fee
6. Calculate GST
7. Calculate final total
```

The important thing here is that the order is deliberate.

For example, the member discount is calculated after the festival discount. GST is calculated on the discounted ticket amount plus the convenience fee.

I documented this instead of leaving the order implicit.

---

## Discounts

There are two different discount types.

### Festival discount

The festival offer is a flat discount.

I also made sure that the discount cannot become larger than the subtotal.

For example, if the subtotal were lower than the festival discount, the customer should not end up with a negative ticket amount.

The calculation therefore uses the smaller of:

```text
festival discount
subtotal
```

### Member discount

The member discount is percentage based.

The percentage is calculated after the festival discount, and then the configured maximum cap is applied.

This makes the cap an actual limit rather than just displaying it in the frontend.

---

## Availability

I wanted availability to be checked by the backend, not just by the UI.

The frontend disables the controls when a tier is unavailable, but that is only a user-interface convenience.

The pricing engine checks again:

```text
Is the tier available?
Is the requested quantity within the available seat count?
```

This means a request cannot become valid simply because somebody bypasses the frontend.

For the sample configuration:

```text
Silver     42 seats
Gold       18 seats
Recliner    0 seats
```

Recliner therefore behaves as sold out.

---

## Configuration instead of hard-coding

I kept cinema/show information and pricing settings in:

```text
data/pricing.json
```

The goal was to avoid writing things like:

```python
if tier == "GOLD":
    price = 25000
```

throughout the pricing engine.

Instead, the engine reads the configuration.

That makes it easier to change the cinema, show, prices, availability, discounts, fees, or GST without rewriting the calculation logic.

---

## Validation

I wanted invalid input to fail early.

The request models therefore validate things such as:

- Quantity must be greater than zero
- Quantity cannot exceed the configured request limit
- Ticket list cannot be empty
- Ticket tiers cannot be duplicated
- Membership must be a boolean
- Ticket tiers must be valid values

The pricing engine then handles business-level validation such as:

- Cinema exists
- Show exists
- Tier exists in that show
- Tier is available
- Requested quantity does not exceed available seats

I kept these two types of validation separate because they solve different problems.

---

## Why duplicate ticket tiers are rejected

A booking request could technically contain:

```text
GOLD × 2
GOLD × 3
```

but I decided that this should be rejected instead of silently merging the two lines.

This keeps the request format predictable.

If a customer wants five Gold tickets, the request should simply say:

```text
GOLD × 5
```

---

# Messy price-list importer

The additional challenge required handling a price list that was not clean.

I treated the importer as a separate component rather than mixing it into the pricing calculation.

Its flow is:

```text
Messy records
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
Create clean price list
      ↓
Return import report
```

---

## Normalizing seat-class names

Names can arrive in different forms:

```text
Silver
 silver
 SILVER
  Silver
```

These should represent the same seat class.

I therefore trim whitespace and convert names to uppercase.

So all of the examples above become:

```text
SILVER
```

The same approach is used for Gold and Recliner.

---

## Handling duplicate names

After normalization, duplicate names are detected.

I chose:

> The first valid occurrence wins.

For example:

```text
Silver → ₹150
silver → ₹160
```

results in:

```text
SILVER → ₹150
```

and the second record is reported as a duplicate.

I chose this because silently replacing an earlier value could make the imported data change depending on the order in which records were processed.

---

## Handling prices

The importer accepts normal price representations such as:

```text
150
"150"
"150.00"
"₹150"
"₹150.50"
```

The value is converted into integer paise.

For example:

```text
₹150.50 → 15050
```

Negative prices are rejected.

Blank prices are rejected.

Values that do not look like valid monetary amounts are also rejected.

---

## Unknown seat classes

The application currently supports:

```text
SILVER
GOLD
RECLINER
```

If the imported file contains something such as:

```text
BALCONY
PREMIUM
VIP
```

it is reported as an unknown seat class rather than being silently added.

This keeps the cleaned list consistent with the pricing model.

---

## Reporting rejected records

I did not want the importer to simply return:

```text
Invalid data
```

Instead, every rejected record includes its row number and a reason.

For example:

```text
Row 6
Price cannot be blank.

Row 7
Unknown seat class 'BALCONY'.

Row 8
Seat class name cannot be blank.

Row 9
Unknown seat class 'PREMIUM'.
```

This makes the importer easier to debug and more useful to someone working with a real messy data file.

---

# Frontend decision

I deliberately kept the frontend separate from the pricing logic.

The browser handles:

- Displaying available tiers
- Selecting quantities
- Showing errors
- Sending the booking
- Displaying the returned bill
- Sending messy price-list data
- Displaying the import report

The backend handles:

- Validation
- Pricing
- Discounts
- Fees
- GST
- Availability
- Import cleaning

This avoids having the same business rules implemented twice.

---

# Testing approach

I wrote tests around the parts where mistakes are most likely.

For pricing, I tested:

- Normal bookings
- Multiple tiers
- Discounts
- Discount caps
- GST
- Fees
- Invalid inputs
- Sold-out tiers
- Available-seat limits

For the importer, I tested:

- Name normalization
- Price parsing
- Negative prices
- Blank prices
- Duplicate names
- Unknown tiers
- A complete messy input example

The final test run was:

```text
29 passed
```

---

# What I would improve with more time

The current version focuses on the pricing engine and the importer rather than building a complete commercial booking system.

With more time, I would consider adding:

- Persistent seat inventory
- Actual seat selection
- Booking IDs
- Database-backed bookings
- Multiple cinemas and shows through the UI
- Authentication
- Better API error status codes
- Importing CSV files directly
- More extensive integration tests

I intentionally did not add these features just for the sake of making the project larger. The main goal was to make the pricing calculation correct, testable, configurable, and easy to demonstrate.
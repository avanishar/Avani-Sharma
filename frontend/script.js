const API_URL = "/calculate-price";
const IMPORT_API_URL = "/import-price-list";


/* ============================================================
   ELEMENTS
============================================================ */

const ticketGrid =
    document.getElementById("ticket-grid");

const calculateButton =
    document.getElementById("calculate");

const memberCheckbox =
    document.getElementById("member");

const ticketCount =
    document.getElementById("ticket-count");

const emptySummary =
    document.getElementById("empty-summary");

const priceSummary =
    document.getElementById("price-summary");

const billLines =
    document.getElementById("bill-lines");

const festivalDiscount =
    document.getElementById("festival-discount");

const memberDiscount =
    document.getElementById("member-discount");

const convenienceFee =
    document.getElementById("convenience-fee");

const gst =
    document.getElementById("gst");

const finalTotal =
    document.getElementById("final-total");

const errorBox =
    document.getElementById("error-box");

const errorMessage =
    document.getElementById("error-message");

const importButton =
    document.getElementById("import-button");

const priceInput =
    document.getElementById("price-input");

const importResult =
    document.getElementById("import-result");

const importError =
    document.getElementById("import-error");

const importErrorMessage =
    document.getElementById("import-error-message");

const importedCount =
    document.getElementById("imported-count");

const acceptedCount =
    document.getElementById("accepted-count");

const duplicateCount =
    document.getElementById("duplicate-count");

const rejectedCount =
    document.getElementById("rejected-count");

const cleanPriceList =
    document.getElementById("clean-price-list");

const rejectedRecords =
    document.getElementById("rejected-records");


/* ============================================================
   BOOKING STATE
============================================================ */

const tickets = {
    SILVER: {
        name: "Silver",
        price: 150,
        seats: 42,
        quantity: 0,
        available: true,
        description: "Standard cinema seating"
    },

    GOLD: {
        name: "Gold",
        price: 250,
        seats: 18,
        quantity: 0,
        available: true,
        description: "Premium viewing position"
    },

    RECLINER: {
        name: "Recliner",
        price: 400,
        seats: 0,
        quantity: 0,
        available: false,
        description: "Fully reclining premium seat"
    }
};


/* ============================================================
   FORMAT MONEY
============================================================ */

function formatRupeesFromPaise(paise) {

    return (
        "₹" +
        (paise / 100).toFixed(2)
    );
}


/* ============================================================
   RENDER TICKET CARDS
============================================================ */

function renderTicketCards() {

    ticketGrid.innerHTML = "";

    Object.entries(tickets).forEach(
        ([tier, ticket]) => {

            const card =
                document.createElement("div");

            card.className =
                "ticket-card";

            if (!ticket.available) {
                card.classList.add("sold-out");
            }

            if (ticket.quantity > 0) {
                card.classList.add("selected");
            }


            const availabilityText =
                ticket.available
                    ? `${ticket.seats} seats available`
                    : "Sold out";


            card.innerHTML = `

                <div class="ticket-top">

                    <div>

                        <div class="ticket-code">
                            ${tier}
                        </div>

                        <h3>
                            ${ticket.name}
                        </h3>

                    </div>

                    <div class="ticket-price">
                        ₹${ticket.price}
                    </div>

                </div>


                <div class="ticket-details">

                    <div class="seat-status ${
                        ticket.available
                            ? "available"
                            : "unavailable"
                    }">

                        <span class="mini-dot"></span>

                        ${availabilityText}

                    </div>

                    <div class="seat-location">
                        ${ticket.description}
                    </div>

                </div>


                ${
                    ticket.available

                    ? `

                        <div class="quantity-row">

                            <span>
                                Quantity
                            </span>

                            <div class="quantity-control">

                                <button
                                    class="qty-btn"
                                    data-tier="${tier}"
                                    data-action="minus"
                                    ${ticket.quantity === 0 ? "disabled" : ""}
                                >
                                    −
                                </button>

                                <span class="quantity">
                                    ${ticket.quantity}
                                </span>

                                <button
                                    class="qty-btn"
                                    data-tier="${tier}"
                                    data-action="plus"
                                    ${ticket.quantity >= ticket.seats ? "disabled" : ""}
                                >
                                    +
                                </button>

                            </div>

                        </div>

                    `

                    : `

                        <div class="sold-out-label">
                            SOLD OUT
                        </div>

                    `
                }

            `;


            ticketGrid.appendChild(card);
        }
    );


    document
        .querySelectorAll(".qty-btn")
        .forEach(button => {

            button.addEventListener(
                "click",
                handleQuantityChange
            );

        });


    updateTicketCount();
}


/* ============================================================
   QUANTITY
============================================================ */

function handleQuantityChange(event) {

    const tier =
        event.currentTarget.dataset.tier;

    const action =
        event.currentTarget.dataset.action;

    const ticket =
        tickets[tier];


    if (!ticket) {
        return;
    }


    if (action === "plus") {

        if (
            ticket.quantity <
            ticket.seats
        ) {

            ticket.quantity += 1;
        }
    }


    if (action === "minus") {

        if (
            ticket.quantity > 0
        ) {

            ticket.quantity -= 1;
        }
    }


    clearPriceResult();

    renderTicketCards();
}


/* ============================================================
   TOTAL TICKET COUNT
============================================================ */

function getTotalTickets() {

    return Object.values(tickets)
        .reduce(
            (total, ticket) =>
                total + ticket.quantity,
            0
        );
}


function updateTicketCount() {

    ticketCount.textContent =
        getTotalTickets();
}


/* ============================================================
   BUILD BOOKING REQUEST
============================================================ */

function buildBookingRequest() {

    const selectedTickets =
        Object.entries(tickets)
            .filter(
                ([, ticket]) =>
                    ticket.quantity > 0
            )
            .map(
                ([tier, ticket]) => ({
                    tier: tier,
                    quantity: ticket.quantity
                })
            );


    return {
        cinema_id: "C001",

        show_id: "S001",

        tickets: selectedTickets,

        is_member:
            memberCheckbox.checked
    };
}


/* ============================================================
   CALCULATE PRICE
============================================================ */

calculateButton.addEventListener(
    "click",
    calculateBooking
);


async function calculateBooking() {

    clearError();


    const request =
        buildBookingRequest();


    if (
        request.tickets.length === 0
    ) {

        showError(
            "Please select at least one ticket."
        );

        return;
    }


    calculateButton.disabled = true;

    calculateButton.querySelector(
        "span"
    ).textContent = "CALCULATING...";


    try {

        const response =
            await fetch(
                API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(request)
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to calculate booking."
            );
        }


        displayPriceSummary(data);

    } catch (error) {

        showError(
            error.message
        );

    } finally {

        calculateButton.disabled = false;

        calculateButton.querySelector(
            "span"
        ).textContent = "REVIEW BOOKING";
    }
}


/* ============================================================
   DISPLAY PRICE
============================================================ */

function displayPriceSummary(data) {

    emptySummary.classList.add(
        "hidden"
    );

    priceSummary.classList.remove(
        "hidden"
    );


    billLines.innerHTML = "";


    data.tickets.forEach(ticket => {

        const line =
            document.createElement("div");

        line.className =
            "bill-line";


        const name =
            `${ticket.tier} × ${ticket.quantity}`;


        const amount =
            formatRupeesFromPaise(
                ticket.line_total_paise
            );


        line.innerHTML = `
            <span>${name}</span>
            <strong>${amount}</strong>
        `;


        billLines.appendChild(line);
    });


    festivalDiscount.textContent =
        "-" +
        formatRupeesFromPaise(
            data.festival_discount_paise
        );


    memberDiscount.textContent =
        "-" +
        formatRupeesFromPaise(
            data.member_discount_paise
        );


    convenienceFee.textContent =
        formatRupeesFromPaise(
            data.convenience_fee_paise
        );


    gst.textContent =
        formatRupeesFromPaise(
            data.gst_paise
        );


    finalTotal.textContent =
        formatRupeesFromPaise(
            data.final_total_paise
        );
}


/* ============================================================
   CLEAR PRICE
============================================================ */

function clearPriceResult() {

    emptySummary.classList.remove(
        "hidden"
    );

    priceSummary.classList.add(
        "hidden"
    );
}


/* ============================================================
   ERROR
============================================================ */

function showError(message) {

    errorMessage.textContent =
        message;

    errorBox.classList.remove(
        "hidden"
    );
}


function clearError() {

    errorBox.classList.add(
        "hidden"
    );

    errorMessage.textContent = "";
}


/* ============================================================
   MEMBER CHANGE
============================================================ */

memberCheckbox.addEventListener(
    "change",
    () => {

        clearPriceResult();

        clearError();

    }
);


/* ============================================================
   PRICE LIST IMPORT
============================================================ */

importButton.addEventListener(
    "click",
    importPriceList
);


async function importPriceList() {

    clearImportError();


    let records;


    try {

        records =
            JSON.parse(
                priceInput.value
            );

    } catch (error) {

        showImportError(
            "The price list is not valid JSON."
        );

        return;
    }


    if (!Array.isArray(records)) {

        showImportError(
            "Price list must be a JSON array."
        );

        return;
    }


    importButton.disabled = true;

    importButton.querySelector(
        "span"
    ).textContent = "IMPORTING...";


    try {

        const response =
            await fetch(
                IMPORT_API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(records)
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to import price list."
            );
        }


        displayImportResult(data);

    } catch (error) {

        showImportError(
            error.message
        );

    } finally {

        importButton.disabled = false;

        importButton.querySelector(
            "span"
        ).textContent =
            "IMPORT & CLEAN PRICE LIST";
    }
}


/* ============================================================
   DISPLAY IMPORT RESULT
============================================================ */

function displayImportResult(data) {

    importResult.classList.remove(
        "hidden"
    );


    const report =
        data.report;


    importedCount.textContent =
        report.imported;


    acceptedCount.textContent =
        report.accepted;


    duplicateCount.textContent =
        report.duplicates;


    rejectedCount.textContent =
        report.rejected;


    cleanPriceList.innerHTML = "";


    data.cleaned_prices.forEach(
        item => {

            const row =
                document.createElement("div");


            row.style.display = "flex";
            row.style.justifyContent =
                "space-between";
            row.style.padding = "9px 0";
            row.style.borderBottom =
                "1px solid rgba(255,255,255,.07)";


            row.innerHTML = `
                <span>
                    ${item.tier}
                </span>

                <strong>
                    ${formatRupeesFromPaise(
                        item.price_paise
                    )}
                </strong>
            `;


            cleanPriceList.appendChild(row);
        }
    );


    rejectedRecords.innerHTML = "";


    if (
        data.rejected.length === 0
    ) {

        rejectedRecords.innerHTML =
            "<p style='color:#4ed69a;'>No rejected records.</p>";

    } else {

        data.rejected.forEach(
            item => {

                const row =
                    document.createElement("div");


                row.style.padding = "8px 0";

                row.style.borderBottom =
                    "1px solid rgba(255,255,255,.07)";


                row.innerHTML = `
                    <strong>
                        Row ${item.row}
                    </strong>

                    <div
                        style="
                            color:#969baa;
                            margin-top:4px;
                        "
                    >
                        ${item.reason}
                    </div>
                `;


                rejectedRecords.appendChild(row);
            }
        );
    }
}


/* ============================================================
   IMPORT ERROR
============================================================ */

function showImportError(message) {

    importErrorMessage.textContent =
        message;

    importError.classList.remove(
        "hidden"
    );
}


function clearImportError() {

    importError.classList.add(
        "hidden"
    );

    importErrorMessage.textContent = "";
}


/* ============================================================
   INITIAL RENDER
============================================================ */

renderTicketCards();
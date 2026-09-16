from enum import Enum

from pydantic import BaseModel, Field, StrictBool, StrictInt, field_validator


class TicketTier(str, Enum):
    SILVER = "SILVER"
    GOLD = "GOLD"
    RECLINER = "RECLINER"


class TicketRequest(BaseModel):
    tier: TicketTier
    quantity: StrictInt = Field(gt=0)

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError(
                "Quantity must be greater than zero."
            )

        if value > 100:
            raise ValueError(
                "Quantity cannot exceed 100 tickets."
            )

        return value


class BookingRequest(BaseModel):
    cinema_id: str = Field(min_length=1)
    show_id: str = Field(min_length=1)

    tickets: list[TicketRequest] = Field(
        min_length=1
    )

    is_member: StrictBool = False

    @field_validator("tickets")
    @classmethod
    def validate_tickets(
        cls,
        tickets: list[TicketRequest],
    ) -> list[TicketRequest]:

        tiers = [
            ticket.tier
            for ticket in tickets
        ]

        if len(tiers) != len(set(tiers)):
            raise ValueError(
                "Duplicate ticket tiers are not allowed."
            )

        return tickets
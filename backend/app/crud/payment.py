from __future__ import annotations

from uuid import UUID
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession


async def validate_payment_amount(amount: Decimal, booking_total: Decimal) -> tuple[bool, str]:
    """
    Validate payment amount matches booking total.
    Returns: (is_valid, message)
    """
    if amount <= 0:
        return False, "Invalid payment amount"
    
    if abs(amount - booking_total) > Decimal('0.01'):
        return False, f"Payment amount {amount} does not match booking total {booking_total}"
    
    return True, "Payment amount is valid"


async def generate_confirmation_number() -> str:
    """
    Generate unique confirmation number for order.
    Format: CineAI-{timestamp}-{random_5_digits}
    """
    import random
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(10000, 99999)
    return f"CineAI-{timestamp}-{random_num}"


async def generate_qr_code_data(order_id: UUID, confirmation_number: str) -> str:
    """
    Generate QR code data for e-ticket.
    Format: CineAI_TICKET_{confirmation_number}_{order_id}
    """
    return f"CineAI_TICKET_{confirmation_number}_{order_id}"

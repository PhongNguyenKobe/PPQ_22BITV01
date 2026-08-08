from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
import unittest

from pydantic import ValidationError

from app.api.routes.promotions import promotion_discount
from app.schemas.promotion import PromotionCreate, PromotionUpdate, PromotionValidation


def valid_payload(**overrides):
    now = datetime.now(timezone.utc)
    data = {
        "code": " cine20 ", "name": "CineAI 20%", "discount_type": "PERCENT",
        "discount_value": 20, "starts_at": now, "ends_at": now + timedelta(days=7),
    }
    data.update(overrides)
    return data


class PromotionRulesTests(unittest.TestCase):
    def test_normalizes_code_and_rejects_zero_usage_limit(self):
        payload = PromotionCreate(**valid_payload())
        self.assertEqual(payload.code, "CINE20")
        with self.assertRaises(ValidationError):
            PromotionCreate(**valid_payload(usage_limit=0))

    def test_rejects_percentage_above_one_hundred(self):
        with self.assertRaises(ValidationError):
            PromotionCreate(**valid_payload(discount_value=101))

    def test_preview_requires_showtime_and_payment_method(self):
        with self.assertRaises(ValidationError):
            PromotionValidation(code="CINE20", subtotal=100_000)

    def test_percentage_discount_respects_cap(self):
        promotion = SimpleNamespace(discount_type="PERCENT", discount_value=Decimal("50"), max_discount=Decimal("30000"))
        self.assertEqual(promotion_discount(promotion, Decimal("100000")), Decimal("30000"))


if __name__ == "__main__":
    unittest.main()

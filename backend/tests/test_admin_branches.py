import unittest

from pydantic import ValidationError

from app.schemas.admin import BranchManageCreate, BranchManageRead


class AdminBranchSchemaTests(unittest.TestCase):
    def test_normalizes_branch_identity_and_contact(self):
        payload = BranchManageCreate(
            code="HCM-Q7",
            name="  CineAI Quận 7  ",
            address_line="  469 Nguyễn Hữu Thọ  ",
            city="  Hồ Chí Minh  ",
            phone="0901234567",
        )
        self.assertEqual(payload.name, "CineAI Quận 7")
        self.assertEqual(payload.city, "Hồ Chí Minh")

    def test_rejects_invalid_branch_phone(self):
        with self.assertRaises(ValidationError):
            BranchManageCreate(
                code="HCM-Q7",
                name="CineAI Quận 7",
                address_line="469 Nguyễn Hữu Thọ",
                city="Hồ Chí Minh",
                phone="123",
            )

    def test_operational_fields_are_safe_by_default(self):
        branch = BranchManageRead(
            id="caac40d5-6cc8-459b-828d-3e750ed5ba2e",
            vendor_id="b7f43660-edf8-438d-9888-bf7a1bb0171f",
            code="HCM-Q7",
            name="CineAI Quận 7",
            address_line="469 Nguyễn Hữu Thọ",
            city="Hồ Chí Minh",
            is_active=True,
        )
        self.assertFalse(branch.is_ready)
        self.assertFalse(branch.can_delete)


if __name__ == "__main__":
    unittest.main()

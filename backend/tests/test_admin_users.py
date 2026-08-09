import unittest

from pydantic import ValidationError

from app.schemas.admin import AdminUserCreate


class AdminUserSchemaTests(unittest.TestCase):
    def test_admin_screen_cannot_create_customer_accounts(self):
        with self.assertRaises(ValidationError):
            AdminUserCreate(
                email="customer@example.com",
                full_name="Customer",
                password="Customer123!",
                role_code="CUSTOMER",
            )

    def test_branch_admin_is_default_internal_role(self):
        payload = AdminUserCreate(
            email="manager@example.com",
            full_name="Manager",
            password="Manager123!",
        )
        self.assertEqual(payload.role_code, "BRANCH_ADMIN")


if __name__ == "__main__":
    unittest.main()

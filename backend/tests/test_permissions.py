import asyncio
from types import SimpleNamespace
from unittest import TestCase

from fastapi import HTTPException

from app.api.deps import require_roles


def user_with_roles(*codes: str):
    return SimpleNamespace(roles=[SimpleNamespace(code=code) for code in codes])


class RolePermissionTests(TestCase):
    def test_super_admin_dependency_rejects_customer(self):
        dependency = require_roles("SUPER_ADMIN")
        with self.assertRaises(HTTPException) as caught:
            asyncio.run(dependency(user_with_roles("CUSTOMER")))
        self.assertEqual(caught.exception.status_code, 403)

    def test_super_admin_dependency_accepts_super_admin(self):
        dependency = require_roles("SUPER_ADMIN")
        user = user_with_roles("SUPER_ADMIN")
        self.assertIs(asyncio.run(dependency(user)), user)

    def test_branch_admin_dependency_does_not_accept_super_admin(self):
        dependency = require_roles("BRANCH_ADMIN")
        with self.assertRaises(HTTPException) as caught:
            asyncio.run(dependency(user_with_roles("SUPER_ADMIN")))
        self.assertEqual(caught.exception.status_code, 403)


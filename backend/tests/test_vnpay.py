from datetime import datetime, timedelta, timezone
from unittest import TestCase
from urllib.parse import parse_qs, urlparse

from app.core.config import settings
from app.services.vnpay import (
    build_payment_url,
    refund_checksum,
    verify_refund_response,
    verify_signature,
)


class VnpaySignatureTests(TestCase):
    def setUp(self) -> None:
        self.original_tmn_code = settings.vnpay_tmn_code
        self.original_hash_secret = settings.vnpay_hash_secret
        settings.vnpay_tmn_code = "TESTCODE"
        settings.vnpay_hash_secret = "test-secret"

    def tearDown(self) -> None:
        settings.vnpay_tmn_code = self.original_tmn_code
        settings.vnpay_hash_secret = self.original_hash_secret

    def payment_params(self) -> dict[str, str]:
        url = build_payment_url(
            txn_ref="test-payment-id",
            amount=120_000,
            order_info="Test payment",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        return {key: values[0] for key, values in parse_qs(urlparse(url).query).items()}

    def test_generated_payment_url_has_valid_signature_and_amount(self) -> None:
        params = self.payment_params()

        self.assertTrue(verify_signature(params))
        self.assertEqual(params["vnp_Amount"], "12000000")
        self.assertEqual(params["vnp_TmnCode"], "TESTCODE")

    def test_signature_is_rejected_for_another_merchant(self) -> None:
        params = self.payment_params()
        params["vnp_TmnCode"] = "OTHER_MERCHANT"

        self.assertFalse(verify_signature(params))

    def test_signature_is_rejected_after_amount_is_modified(self) -> None:
        params = self.payment_params()
        params["vnp_Amount"] = "100"

        self.assertFalse(verify_signature(params))

    def test_refund_request_and_response_checksums(self) -> None:
        request = {
            "vnp_RequestId": "request1",
            "vnp_Version": "2.1.0",
            "vnp_Command": "refund",
            "vnp_TmnCode": "TESTCODE",
            "vnp_TransactionType": "02",
            "vnp_TxnRef": "payment1",
            "vnp_Amount": "12000000",
            "vnp_TransactionNo": "123456",
            "vnp_TransactionDate": "20260731100000",
            "vnp_CreateBy": "admin@example.com",
            "vnp_CreateDate": "20260731103000",
            "vnp_IpAddr": "127.0.0.1",
            "vnp_OrderInfo": "Refund ticket",
        }
        self.assertEqual(len(refund_checksum(request)), 128)

        response = {
            "vnp_ResponseId": "response1",
            "vnp_Command": "refund",
            "vnp_ResponseCode": "00",
            "vnp_Message": "Success",
            "vnp_TmnCode": "TESTCODE",
            "vnp_TxnRef": "payment1",
            "vnp_Amount": "12000000",
            "vnp_BankCode": "NCB",
            "vnp_PayDate": "20260731103100",
            "vnp_TransactionNo": "654321",
            "vnp_TransactionType": "02",
            "vnp_TransactionStatus": "00",
            "vnp_OrderInfo": "Refund ticket",
        }
        response["vnp_SecureHash"] = refund_checksum({
            "vnp_RequestId": response["vnp_ResponseId"],
            "vnp_Version": response["vnp_Command"],
            "vnp_Command": response["vnp_ResponseCode"],
            "vnp_TmnCode": response["vnp_Message"],
            "vnp_TransactionType": response["vnp_TmnCode"],
            "vnp_TxnRef": response["vnp_TxnRef"],
            "vnp_Amount": response["vnp_Amount"],
            "vnp_TransactionNo": response["vnp_BankCode"],
            "vnp_TransactionDate": response["vnp_PayDate"],
            "vnp_CreateBy": response["vnp_TransactionNo"],
            "vnp_CreateDate": response["vnp_TransactionType"],
            "vnp_IpAddr": response["vnp_TransactionStatus"],
            "vnp_OrderInfo": response["vnp_OrderInfo"],
        })
        self.assertTrue(verify_refund_response(response))
        response["vnp_Amount"] = "100"
        self.assertFalse(verify_refund_response(response))

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Mapping
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from app.core.config import settings


VIETNAM_TZ = timezone(timedelta(hours=7))


def _encoded_query(params: Mapping[str, object]) -> str:
    normalized = {
        key: str(value)
        for key, value in params.items()
        if value is not None and str(value) != "" and key not in {"vnp_SecureHash", "vnp_SecureHashType"}
    }
    return urlencode(sorted(normalized.items()), quote_via=quote_plus)


def sign_params(params: Mapping[str, object]) -> str:
    return hmac.new(
        settings.vnpay_hash_secret.encode("utf-8"),
        _encoded_query(params).encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()


def verify_signature(params: Mapping[str, object]) -> bool:
    received = str(params.get("vnp_SecureHash", "")).lower()
    received_tmn_code = str(params.get("vnp_TmnCode", ""))
    if (
        not settings.vnpay_hash_secret
        or not settings.vnpay_tmn_code
        or not received
        or not hmac.compare_digest(received_tmn_code, settings.vnpay_tmn_code)
    ):
        return False
    return hmac.compare_digest(received, sign_params(params))


def build_payment_url(
    *,
    txn_ref: str,
    amount: int,
    order_info: str,
    ip_address: str,
    expires_at: datetime,
) -> str:
    now = datetime.now(VIETNAM_TZ)
    expiry = expires_at.astimezone(VIETNAM_TZ)
    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": settings.vnpay_tmn_code,
        "vnp_Amount": amount * 100,
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": order_info,
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": settings.vnpay_return_url,
        "vnp_IpAddr": ip_address,
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": expiry.strftime("%Y%m%d%H%M%S"),
    }
    return f"{settings.vnpay_payment_url}?{_encoded_query(params)}&vnp_SecureHash={sign_params(params)}"


def query_checksum(params: Mapping[str, object]) -> str:
    ordered_keys = (
        "vnp_RequestId", "vnp_Version", "vnp_Command", "vnp_TmnCode",
        "vnp_TxnRef", "vnp_TransactionDate", "vnp_CreateDate",
        "vnp_IpAddr", "vnp_OrderInfo",
    )
    data = "|".join(str(params.get(key, "")) for key in ordered_keys)
    return hmac.new(
        settings.vnpay_hash_secret.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()


def refund_checksum(params: Mapping[str, object]) -> str:
    ordered_keys = (
        "vnp_RequestId", "vnp_Version", "vnp_Command", "vnp_TmnCode",
        "vnp_TransactionType", "vnp_TxnRef", "vnp_Amount",
        "vnp_TransactionNo", "vnp_TransactionDate", "vnp_CreateBy",
        "vnp_CreateDate", "vnp_IpAddr", "vnp_OrderInfo",
    )
    data = "|".join(str(params.get(key, "")) for key in ordered_keys)
    return hmac.new(
        settings.vnpay_hash_secret.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()


def verify_refund_response(params: Mapping[str, object]) -> bool:
    ordered_keys = (
        "vnp_ResponseId", "vnp_Command", "vnp_ResponseCode", "vnp_Message",
        "vnp_TmnCode", "vnp_TxnRef", "vnp_Amount", "vnp_BankCode",
        "vnp_PayDate", "vnp_TransactionNo", "vnp_TransactionType",
        "vnp_TransactionStatus", "vnp_OrderInfo",
    )
    data = "|".join(str(params.get(key, "")) for key in ordered_keys)
    expected = hmac.new(
        settings.vnpay_hash_secret.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()
    received = str(params.get("vnp_SecureHash", "")).lower()
    return bool(received) and hmac.compare_digest(received, expected)


async def refund_transaction(
    *,
    request_id: str,
    txn_ref: str,
    amount: int,
    transaction_no: str,
    transaction_date: datetime,
    created_by: str,
    ip_address: str,
    reason: str,
) -> dict:
    now = datetime.now(VIETNAM_TZ)
    safe_reason = "".join(
        character for character in reason
        if character.isascii() and (character.isalnum() or character == " ")
    ).strip() or "Refund CineAI transaction"
    params = {
        "vnp_RequestId": request_id,
        "vnp_Version": "2.1.0",
        "vnp_Command": "refund",
        "vnp_TmnCode": settings.vnpay_tmn_code,
        "vnp_TransactionType": "02",
        "vnp_TxnRef": txn_ref,
        "vnp_Amount": amount * 100,
        "vnp_TransactionNo": transaction_no,
        "vnp_TransactionDate": transaction_date.astimezone(VIETNAM_TZ).strftime("%Y%m%d%H%M%S"),
        "vnp_CreateBy": created_by[:245],
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr": ip_address,
        "vnp_OrderInfo": safe_reason[:255],
    }
    params["vnp_SecureHash"] = refund_checksum(params)

    def send() -> dict:
        request = Request(
            settings.vnpay_api_url,
            data=json.dumps(params).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    return await asyncio.to_thread(send)


async def query_transaction(
    *,
    request_id: str,
    txn_ref: str,
    transaction_date: datetime,
    ip_address: str,
) -> dict:
    now = datetime.now(VIETNAM_TZ)
    params = {
        "vnp_RequestId": request_id,
        "vnp_Version": "2.1.0",
        "vnp_Command": "querydr",
        "vnp_TmnCode": settings.vnpay_tmn_code,
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": f"Query transaction {txn_ref}",
        "vnp_TransactionDate": transaction_date.astimezone(VIETNAM_TZ).strftime("%Y%m%d%H%M%S"),
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr": ip_address,
    }
    params["vnp_SecureHash"] = query_checksum(params)

    def send() -> dict:
        request = Request(
            settings.vnpay_api_url,
            data=json.dumps(params).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    return await asyncio.to_thread(send)

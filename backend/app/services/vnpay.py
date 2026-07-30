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
    if not settings.vnpay_hash_secret or not received:
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

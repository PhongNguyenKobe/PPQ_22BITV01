import base64
import json
import logging
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from decimal import Decimal
from typing import Any, Dict

from app.core.config import settings

logger = logging.getLogger(__name__)

# Simple in-memory token cache
_token_cache: Dict[str, Any] = {
    "access_token": None,
    "expires_at": None
}

def _get_base_url() -> str:
    return "https://api-m.sandbox.paypal.com" if settings.paypal_mode == "sandbox" else "https://api-m.paypal.com"

async def get_access_token() -> str:
    now = datetime.now(timezone.utc)
    if _token_cache["access_token"] and _token_cache["expires_at"] > now + timedelta(seconds=60):
        return _token_cache["access_token"]

    base_url = _get_base_url()
    url = f"{base_url}/v1/oauth2/token"
    
    auth_str = f"{settings.paypal_client_id}:{settings.paypal_client_secret}"
    auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = b"grant_type=client_credentials"
    
    req = Request(url, data=data, headers=headers, method="POST")
    try:
        import asyncio
        loop = asyncio.get_running_loop()
        
        def _request():
            with urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
                
        res = await loop.run_in_executor(None, _request)
        
        _token_cache["access_token"] = res["access_token"]
        expires_in = int(res.get("expires_in", 3600))
        _token_cache["expires_at"] = now + timedelta(seconds=expires_in)
        return res["access_token"]
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        logger.error(f"PayPal oauth token error: {e.code} - {body}")
        raise Exception(f"PayPal authentication failed: {body}")
    except Exception as e:
        logger.error(f"PayPal oauth connection error: {str(e)}")
        raise Exception(f"PayPal oauth connection error: {str(e)}")

async def create_paypal_order(amount: Decimal, payment_id: Any, base_api_url: str) -> Dict[str, Any]:
    # Convert VND to USD (1 USD = 25000 VND)
    amount_usd = round(float(amount) / 25000.0, 2)
    if amount_usd <= 0:
        amount_usd = 0.01
        
    access_token = await get_access_token()
    base_url = _get_base_url()
    url = f"{base_url}/v2/checkout/orders"
    
    return_url = f"{base_api_url.rstrip('/')}/payments/paypal/return?payment_id={payment_id}"
    cancel_url = f"{base_api_url.rstrip('/')}/payments/paypal/cancel?payment_id={payment_id}"
    
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": str(payment_id),
                "amount": {
                    "currency_code": "USD",
                    "value": f"{amount_usd:.2f}"
                },
                "description": f"Thanh toan ve CineAI - Booking {payment_id}"
            }
        ],
        "application_context": {
            "brand_name": "CineAI",
            "landing_page": "NO_PREFERENCE",
            "user_action": "PAY_NOW",
            "return_url": return_url,
            "cancel_url": cancel_url
        }
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "PayPal-Request-Id": str(payment_id)
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=headers, method="POST")
    
    import asyncio
    loop = asyncio.get_running_loop()
    
    def _request():
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
            
    try:
        return await loop.run_in_executor(None, _request)
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        logger.error(f"PayPal create order error: {e.code} - {body}")
        raise Exception(f"PayPal order creation failed: {body}")
    except Exception as e:
        logger.error(f"PayPal create order connection error: {str(e)}")
        raise Exception(f"PayPal create order connection error: {str(e)}")

async def capture_paypal_order(order_id: str) -> Dict[str, Any]:
    access_token = await get_access_token()
    base_url = _get_base_url()
    url = f"{base_url}/v2/checkout/orders/{order_id}/capture"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = b"{}"
    req = Request(url, data=data, headers=headers, method="POST")
    
    import asyncio
    loop = asyncio.get_running_loop()
    
    def _request():
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
            
    try:
        return await loop.run_in_executor(None, _request)
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        logger.error(f"PayPal capture order error: {e.code} - {body}")
        raise Exception(f"PayPal capture failed: {body}")
    except Exception as e:
        logger.error(f"PayPal capture order connection error: {str(e)}")
        raise Exception(f"PayPal capture order connection error: {str(e)}")

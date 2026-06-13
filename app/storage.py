from app.db.database import supabase
import logging

logger = logging.getLogger(__name__)

BUCKET_NAME = "receipts"
SIGNED_URL_EXPIRY = 86400

def upload_receipt(user_id: str, filename: str, content: bytes, content_type: str = "image/jpeg") -> str | None:
    path = f"{user_id}/{filename}"
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path,
            content,
            {"content-type": content_type, "upsert": "true"},
        )
        logger.info(f"Receipt uploaded to storage: {path}")
        return path
    except Exception as e:
        logger.warning(f"Failed to upload receipt to storage: {e}")
        return None

def get_receipt_url(path: str) -> str | None:
    if not path:
        return None
    try:
        result = supabase.storage.from_(BUCKET_NAME).create_signed_url(path, SIGNED_URL_EXPIRY)
        if isinstance(result, dict):
            return result.get("signedURL") or result.get("signed_url")
        return str(result)
    except Exception as e:
        logger.warning(f"Failed to generate signed URL for {path}: {e}")
        return None

def delete_receipt(path: str) -> bool:
    if not path:
        return True
    try:
        supabase.storage.from_(BUCKET_NAME).remove([path])
        logger.info(f"Receipt deleted from storage: {path}")
        return True
    except Exception as e:
        logger.warning(f"Failed to delete receipt from storage: {e}")
        return False

def enrich_expense_with_receipt(expense: dict) -> dict:
    if expense.get("receipt_image"):
        expense["receipt_url"] = get_receipt_url(expense["receipt_image"])
    return expense

import random
import time
import logging
from datetime import datetime, timezone, timedelta

# Configure logging
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hong Kong timezone (UTC+8)
HK_TIMEZONE = timezone(timedelta(hours=8))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/"
    }

def human_delay(max_seconds=300):
    """Wait for a random amount of time to mimic human behavior."""
    delay = random.uniform(5, max_seconds)
    logger.info(f"Waiting for {delay:.2f} seconds to simulate human behavior...")
    time.sleep(delay)


def parse_iso_date(date_str):
    """
    Parse ISO 8601 date string to datetime object with UTC timezone.
    
    Args:
        date_str: ISO 8601 timestamp e.g. "2026-01-07T15:04:51.870Z" or "2026-01-07T15:04:51Z"
        
    Returns:
        datetime object with UTC timezone, or None if parsing fails
    """
    if not date_str:
        return None
    try:
        # Remove 'Z' suffix and parse
        clean_date = date_str.rstrip('Z')
        return datetime.fromisoformat(clean_date).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def format_hk_time(date_str):
    """
    Convert UTC to Hong Kong time (UTC+8) and format as string.
    
    Args:
        date_str: ISO 8601 timestamp string
        
    Returns:
        Formatted string like "2026-01-07 23:04:51 HKT" or "Unknown"
    """
    dt = parse_iso_date(date_str)
    if not dt:
        return "Unknown"
    hk_time = dt.astimezone(HK_TIMEZONE)
    return hk_time.strftime("%Y-%m-%d %H:%M:%S HKT")


def is_within_hours(date_str, hours):
    """
    Check if a date is within the last X hours (using Hong Kong time).
    
    Args:
        date_str: ISO 8601 timestamp string
        hours: Number of hours to look back
        
    Returns:
        True if date is within the time window, False otherwise (including parse failures)
    """
    if not hours:
        return True
    dt = parse_iso_date(date_str)
    if not dt:
        return False
    now_hk = datetime.now(HK_TIMEZONE)
    cutoff = now_hk - timedelta(hours=int(hours))
    return dt.astimezone(HK_TIMEZONE) >= cutoff

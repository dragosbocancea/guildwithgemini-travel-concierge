# Copyright 2026 Google LLC
# Budget calculation tool with live exchange rate lookup

import logging
import httpx

logger = logging.getLogger(__name__)


def calculate_trip_budget(
    destination_currency: str,
    num_days: int,
    daily_lodging_usd: float = 120.0,
    daily_food_usd: float = 50.0,
    daily_activities_usd: float = 40.0,
    base_currency: str = "USD",
) -> dict:
    """Calculates estimated trip budget breakdown and converts it to destination currency using live exchange rates.

    Args:
        destination_currency: 3-letter currency code for destination (e.g., 'JPY', 'EUR', 'GBP', 'MXN').
        num_days: Number of days for the trip.
        daily_lodging_usd: Estimated daily lodging cost in USD (default 120.0).
        daily_food_usd: Estimated daily food cost in USD (default 50.0).
        daily_activities_usd: Estimated daily activity/transit cost in USD (default 40.0).
        base_currency: Base currency code (default 'USD').

    Returns:
        Dictionary containing total USD cost, exchange rate, converted destination cost, and daily breakdown.
    """
    dest_curr = destination_currency.strip().upper()
    base_curr = base_currency.strip().upper()

    daily_total_usd = daily_lodging_usd + daily_food_usd + daily_activities_usd
    total_usd = daily_total_usd * num_days

    # Fetch live exchange rate from free API
    rate = 1.0
    try:
        url = f"https://open.er-api.com/v6/latest/{base_curr}"
        res = httpx.get(url, timeout=5.0)
        data = res.json()
        if res.status_code == 200 and "rates" in data:
            rate = float(data["rates"].get(dest_curr, 1.0))
    except Exception as e:
        logger.warning(f"Could not fetch exchange rate for {dest_curr}: {e}")

    converted_total = round(total_usd * rate, 2)

    return {
        "num_days": num_days,
        "base_currency": base_curr,
        "total_base_cost": round(total_usd, 2),
        "destination_currency": dest_curr,
        "exchange_rate": rate,
        "converted_total_cost": converted_total,
        "daily_breakdown_usd": {
            "lodging": daily_lodging_usd,
            "food": daily_food_usd,
            "activities": daily_activities_usd,
            "daily_total": daily_total_usd,
        },
    }

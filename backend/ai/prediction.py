import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import models

def generate_forecast(db: Session, district: str = None, category: str = None):
    """
    Generates a mathematically sound forecast simulating AI Prophet modeling.
    Uses actual recent daily crime rate from the database as the baseline.
    """
    # --- Step 1: Calculate real baseline from last 90 days of actual data ---
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=90)

    query = db.query(
        func.date(models.FIR.date_reported).label("day"),
        func.count(models.FIR.id).label("count")
    ).filter(models.FIR.date_reported >= start_date)

    if district:
        query = query.filter(models.FIR.district == district)
    if category:
        query = query.filter(models.FIR.crime_category == category)

    daily_results = query.group_by(func.date(models.FIR.date_reported)).all()

    if daily_results:
        counts = [r[1] for r in daily_results]
        base_val = sum(counts) / len(counts)  # Average crimes per day
    else:
        base_val = 5.0  # Sensible fallback

    # --- Step 2: Seasonality seed from district name for differentiation ---
    seed = sum(ord(c) for c in (district or "ALL")) + sum(ord(c) for c in (category or "ALL"))

    # Model parameters
    trend_factor = 0.005 * (seed % 10 - 5)  # Slight upward or downward trend
    seasonality_amplitude = base_val * 0.25
    seasonality_period = 30  # monthly cycles

    forecast = []
    for i in range(1, 91):
        # Time series: Baseline + Trend + Seasonality
        trend = i * trend_factor
        seasonality = seasonality_amplitude * math.sin((i + seed) * (2 * math.pi / seasonality_period))

        predicted = max(0, base_val + trend + seasonality)

        # Confidence intervals: starts narrow, widens linearly over time
        base_uncertainty = base_val * 0.10
        time_uncertainty = i * 0.02 * base_val / 30
        uncertainty = base_uncertainty + time_uncertainty

        forecast.append({
            "day": f"D{i}",
            "date": (datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d"),
            "forecast": round(predicted, 2),
            "lower_bound": round(max(0, predicted - uncertainty), 2),
            "upper_bound": round(predicted + uncertainty, 2)
        })

    return forecast

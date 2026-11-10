"""
AquaMitra Calculation Engine
Pure, reusable calculation functions for biomass, feeding, growth, mortality, and finance.
Never fabricates values when data is insufficient.
"""

from typing import Optional, Tuple, Dict, Any


def calculate_initial_biomass(number_of_fish: int, avg_initial_weight_grams: float) -> float:
    """
    Calculates initial stocked biomass in kilograms (kg).
    Formula: Biomass (kg) = (Number of Fish * Avg Initial Weight (g)) / 1000.0
    """
    if number_of_fish is None or avg_initial_weight_grams is None:
        return 0.0
    if number_of_fish <= 0 or avg_initial_weight_grams <= 0:
        return 0.0
    return round((number_of_fish * avg_initial_weight_grams) / 1000.0, 2)


def calculate_estimated_biomass(estimated_population: int, avg_weight_grams: float) -> Optional[float]:
    """
    Calculates current estimated biomass in kilograms (kg).
    Returns None if population or weight is not available, rather than fabricating.
    """
    if estimated_population is None or avg_weight_grams is None:
        return None
    if estimated_population <= 0 or avg_weight_grams <= 0:
        return 0.0
    return round((estimated_population * avg_weight_grams) / 1000.0, 2)


def calculate_daily_feed(biomass_kg: float, feeding_rate_percent: float) -> float:
    """
    Calculates recommended daily feed requirement in kilograms (kg).
    Formula: Daily Feed (kg) = Biomass (kg) * (Feeding Rate % / 100.0)
    """
    if biomass_kg is None or feeding_rate_percent is None:
        return 0.0
    if biomass_kg <= 0 or feeding_rate_percent <= 0:
        return 0.0
    return round(biomass_kg * (feeding_rate_percent / 100.0), 2)


def calculate_mortality_percentage(number_of_dead: int, total_population: Optional[int]) -> Optional[float]:
    """
    Calculates mortality percentage.
    If total population is unavailable or zero, returns None (does not fabricate percentage).
    Formula: Mortality % = (Dead Fish / Total Population) * 100.0
    """
    if number_of_dead is None or total_population is None:
        return None
    if total_population <= 0:
        return None
    if number_of_dead < 0:
        return 0.0
    return round((number_of_dead / float(total_population)) * 100.0, 2)


def calculate_total_revenue(quantity_sold_kg: float, price_per_kg: float) -> float:
    """
    Calculates total gross sales revenue.
    Formula: Total Revenue = Quantity Sold (kg) * Price/kg
    """
    if quantity_sold_kg is None or price_per_kg is None:
        return 0.0
    if quantity_sold_kg <= 0 or price_per_kg <= 0:
        return 0.0
    return round(quantity_sold_kg * price_per_kg, 2)


def calculate_net_difference(total_revenue: float, total_expenses: float) -> float:
    """
    Calculates Estimated Net Difference (Revenue - Expenses).
    Labeled as 'Estimated Net Difference' unless complete accounting is established.
    """
    rev = total_revenue if total_revenue is not None else 0.0
    exp = total_expenses if total_expenses is not None else 0.0
    return round(rev - exp, 2)


def calculate_average_daily_growth(
    initial_weight_grams: float,
    current_weight_grams: float,
    days_elapsed: int
) -> Optional[float]:
    """
    Calculates Average Daily Growth (ADG) in grams/day.
    Formula: ADG = (Current Weight - Initial Weight) / Days Elapsed
    """
    if initial_weight_grams is None or current_weight_grams is None or days_elapsed is None:
        return None
    if days_elapsed <= 0:
        return None
    weight_gain = current_weight_grams - initial_weight_grams
    return round(weight_gain / float(days_elapsed), 2)


def evaluate_parameter_status(
    param_name: str,
    value: Optional[float],
    lower_ref: Optional[float],
    upper_ref: Optional[float]
) -> Dict[str, Any]:
    """
    Evaluates a water quality reading against configured reference ranges.
    Returns:
        {
            'status': 'Good' | 'Needs Attention' | 'Potential Risk' | 'Not Evaluated',
            'severity': 'INFO' | 'WARNING' | 'HIGH',
            'color': 'green' | 'amber' | 'red' | 'gray',
            'message': descriptive text,
            'suggested_action': actionable recommendation
        }
    """
    if value is None:
        return {
            "status": "Not Evaluated",
            "severity": "INFO",
            "color": "gray",
            "message": "No observation recorded",
            "suggested_action": "Record parameter observation when available."
        }

    if lower_ref is None and upper_ref is None:
        return {
            "status": "Reference Range Not Configured",
            "severity": "INFO",
            "color": "gray",
            "message": "Reference threshold not configured in system",
            "suggested_action": "Configure reference limits in Settings if desired."
        }

    # Moderate deviation buffer (10% outside reference range)
    has_lower = lower_ref is not None
    has_upper = upper_ref is not None

    if has_lower and value < lower_ref:
        deviation = lower_ref - value
        # Substantial deviation
        if (lower_ref > 0 and (deviation / lower_ref) > 0.15) or (param_name == "DissolvedOxygen" and value < 3.0):
            return {
                "status": "Potential Risk",
                "severity": "HIGH",
                "color": "red",
                "message": f"{param_name} ({value}) is substantially below the reference range ({lower_ref} - {upper_ref}).",
                "suggested_action": "Recheck the reading immediately. Aerate or refresh pond water if feasible. Consult a fisheries specialist if condition persists."
            }
        else:
            return {
                "status": "Needs Attention",
                "severity": "WARNING",
                "color": "amber",
                "message": f"{param_name} ({value}) is slightly below the reference range ({lower_ref} - {upper_ref}).",
                "suggested_action": "Monitor the pond closely and consider verifying with a second reading."
            }

    if has_upper and value > upper_ref:
        deviation = value - upper_ref
        if (upper_ref > 0 and (deviation / upper_ref) > 0.15) or (param_name == "Ammonia" and value > 0.1):
            return {
                "status": "Potential Risk",
                "severity": "HIGH",
                "color": "red",
                "message": f"{param_name} ({value}) is substantially above the reference range ({lower_ref} - {upper_ref}).",
                "suggested_action": "Recheck the reading immediately. Inspect feeding rates and organic waste. Consult a fisheries specialist if condition persists."
            }
        else:
            return {
                "status": "Needs Attention",
                "severity": "WARNING",
                "color": "amber",
                "message": f"{param_name} ({value}) is slightly above the reference range ({lower_ref} - {upper_ref}).",
                "suggested_action": "Monitor pond conditions closely and verify with subsequent measurements."
            }

    return {
        "status": "Good",
        "severity": "INFO",
        "color": "green",
        "message": f"{param_name} ({value}) is within the configured reference range ({lower_ref} - {upper_ref}).",
        "suggested_action": "Maintain routine pond management and regular monitoring."
    }

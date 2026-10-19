from dataclasses import dataclass

@dataclass
class BusinessProfile:
    distributor_led: bool | None = None
    own_store_retail: bool | None = None
    diversified: bool | None = None
    reasons: dict[str, str] | None = None

def profile_business(facts: dict[str, object]) -> BusinessProfile:
    """Use caller-supplied public facts; absent facts remain unknown."""
    known = {key: bool(facts[key]) if key in facts and facts[key] is not None else None for key in ("distributor_led", "own_store_retail", "diversified")}
    reasons = {key: ("Classified from supplied public business-profile facts." if value is not None else "No verified public profile input was supplied.") for key, value in known.items()}
    return BusinessProfile(**known, reasons=reasons)

def applicable_angles(profile: BusinessProfile) -> dict[str, tuple[bool, str | None]]:
    angles = {"price_volume": (True, None), "working_capital": (True, None), "cash_conversion": (True, None)}
    if profile.own_store_retail is False:
        angles["store_economics"] = (False, "Business profile does not indicate own-store retail.")
    elif profile.own_store_retail is None:
        angles["store_economics"] = (False, "Own-store retail status is unverified.")
    else:
        angles["store_economics"] = (True, None)
    if profile.distributor_led is None:
        angles["distributor_metrics"] = (False, "Distributor-led status is unverified.")
    elif not profile.distributor_led:
        angles["distributor_metrics"] = (False, "Business profile does not indicate a distributor-led model.")
    return angles

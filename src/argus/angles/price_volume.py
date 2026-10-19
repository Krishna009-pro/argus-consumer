from ..metrics import price_mix_growth

def compute(revenue_growth: float | None, volume_growth: float | None) -> dict:
    result = price_mix_growth(revenue_growth, volume_growth)
    return {"status": "tested", "value": result} if result is not None else {"status": "abstained", "reason": "Revenue growth and disclosed volume growth are both required."}

from ..metrics import cash_conversion

def compute(operating_cash_flow, ebitda):
    value = cash_conversion(operating_cash_flow, ebitda)
    return {"status": "tested", "value": value} if value is not None else {"status": "abstained", "reason": "Operating cash flow and nonzero EBITDA for the same disclosed period are required."}

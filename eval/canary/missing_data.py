def evaluate() -> dict:
    from argus.angles.price_volume import compute
    from argus.angles.working_capital import compute_receivable_days
    from argus.angles.cash_conversion import compute as cash
    cases = [compute(None, .03), compute(.1, None), compute_receivable_days(None, 10, 180), cash(None, 10)]
    abstained = sum(case["status"] == "abstained" for case in cases)
    return {"count": len(cases), "abstained": abstained, "M06_abstain_correctness": 100 * abstained / len(cases)}

if __name__ == "__main__": print(evaluate())

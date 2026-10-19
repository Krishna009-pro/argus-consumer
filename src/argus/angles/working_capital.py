from ..metrics import receivable_days, inventory_days

def compute_receivable_days(receivables, revenue, days):
    value = receivable_days(receivables, revenue, days)
    return {"status": "tested", "value": value} if value is not None else {"status": "abstained", "reason": "Receivables and positive period revenue are required."}

def compute_inventory_days(inventory, denominator, days, denominator_name="cost_of_goods"):
    value = inventory_days(inventory, denominator, days)
    return {"status": "tested", "value": value, "denominator": denominator_name} if value is not None else {"status": "abstained", "reason": "Inventory and a positive disclosed denominator are required."}

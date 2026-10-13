# Maintainability violation: Excessive cyclomatic complexity and deep nesting (MAINT02)
def process_nested_orders(orders: list) -> list:
    results = []
    for order in orders:
        if order.get("active"):
            for item in order.get("items", []):
                if item.get("in_stock"):
                    if item.get("price", 0) > 100:
                        if order.get("user", {}).get("is_vip"):
                            if item.get("category") == "electronics":
                                for tag in item.get("tags", []):
                                    if tag == "promo":
                                        results.append(item["id"])
    return results


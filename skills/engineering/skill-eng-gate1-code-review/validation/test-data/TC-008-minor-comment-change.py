# Minor finding: Single low-severity naming ambiguity (MAINT03)
def format_item_label(product_name: str, sku_code: str) -> str:
    lbl = f"{product_name} ({sku_code})"  # Minor naming ambiguity 'lbl'
    return lbl.strip().upper()


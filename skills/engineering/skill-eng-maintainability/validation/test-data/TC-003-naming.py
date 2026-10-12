# TC-003: Naming and Intent Clarity (MAINT03)
# Demonstrates misleading names, single-letter variables, and descriptive domain identifiers

from typing import List, Dict, Any

# --- VIOLATION ---
def proc_usr_lst(d: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    VIOLATION:
    - Cryptic function name 'proc_usr_lst'
    - Single letter parameter 'd'
    - Misleading boolean 'not_unverified' (double negative)
    - Ambiguous variable 'x' and 'temp1'
    """
    res = []
    for x in d:
        temp1 = x.get("s", 0)
        not_unverified = not x.get("unv", False)
        if temp1 > 100 and not_unverified:
            res.append(x)
    return res


# --- SAFE IMPLEMENTATION ---
def filter_verified_high_value_accounts(accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    SAFE: Descriptive, domain-oriented identifiers that communicate business intent.
    """
    qualified_accounts = []
    minimum_balance_threshold = 100.0

    for account in accounts:
        balance = account.get("balance", 0.0)
        is_verified = account.get("is_verified", False)

        if balance > minimum_balance_threshold and is_verified:
            qualified_accounts.append(account)

    return qualified_accounts


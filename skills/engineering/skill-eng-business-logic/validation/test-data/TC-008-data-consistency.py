# TC-008: Business invariant or persistence consistency violation
# Spec: specs/wallet/business-spec.md Section 6.2
# Rule: Deducting wallet balance must atomically record a ledger entry and fail if balance < amount.

class WalletServiceViolation:
    def debit_balance(self, wallet_id: str, amount: float, db_session) -> None:
        """VIOLATION (BIZ06): Updates wallet balance without persisting corresponding ledger transaction."""
        db_session.execute("UPDATE wallets SET balance = balance - :amt WHERE id = :id", {"amt": amount, "id": wallet_id})
        # Missing atomic ledger insertion


class WalletServiceSafe:
    def debit_balance(self, wallet_id: str, amount: float, db_session) -> None:
        """SAFE: Atomically debits balance and records immutable ledger audit entry."""
        db_session.execute("UPDATE wallets SET balance = balance - :amt WHERE id = :id", {"amt": amount, "id": wallet_id})
        db_session.execute("INSERT INTO ledger_entries (wallet_id, amount, type) VALUES (:id, :amt, 'DEBIT')", {"id": wallet_id, "amt": amount})


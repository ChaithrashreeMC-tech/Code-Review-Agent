async def execute_transfer_unhandled_rollback(session, account_a: int, account_b: int, amount: float):
    # Violation: Exception handler re-raises without explicit transaction rollback
    try:
        session.add(DebitRecord(account=account_a, amount=amount))
        session.add(CreditRecord(account=account_b, amount=amount))
        await session.commit()
    except Exception as e:
        raise e # Missing await session.rollback()

async def execute_transfer_handled_rollback(session, account_a: int, account_b: int, amount: float):
    # Safe: Performs explicit session.rollback() before re-raising
    try:
        session.add(DebitRecord(account=account_a, amount=amount))
        session.add(CreditRecord(account=account_b, amount=amount))
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e


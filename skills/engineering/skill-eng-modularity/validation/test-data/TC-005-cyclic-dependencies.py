# TC-005: Cyclic Dependencies and Boundaries

# VIOLATION: Using local function import to workaround cyclic module import error
def process_order_violation(order_id: str):
    # Inline import to bypass circular dependency between order and user modules
    from user_service import notify_user_of_order
    notify_user_of_order(order_id)
    return True


# SAFE: Shared contracts extracted to lower-level interfaces/contracts module
class INotificationService:
    def notify(self, user_id: str, message: str):
        pass

def process_order_safe(order_id: str, notifier: INotificationService):
    notifier.notify("user_123", f"Order {order_id} processed")
    return True


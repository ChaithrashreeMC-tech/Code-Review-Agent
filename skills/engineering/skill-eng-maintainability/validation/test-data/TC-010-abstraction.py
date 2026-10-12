# TC-010: Abstraction and Design Consistency (MAINT10)
# Demonstrates over-engineered speculative layers vs. pragmatic direct design

from typing import Protocol, List

# --- VIOLATION ---
# VIOLATION: 4 layers of trivial passthrough abstractions for a basic string list fetcher
class IDataFetcherProtocol(Protocol):
    def fetch_items(self) -> List[str]: ...

class BaseDataFetcherProxy(IDataFetcherProtocol):
    def fetch_items(self) -> List[str]:
        raise NotImplementedError

class ConcreteDataFetcherDelegator(BaseDataFetcherProxy):
    def fetch_items(self) -> List[str]:
        return self._delegate_to_actual()
    def _delegate_to_actual(self) -> List[str]:
        return ["alpha", "beta", "gamma"]

class DataFetcherFactory:
    @staticmethod
    def get_instance() -> IDataFetcherProtocol:
        return ConcreteDataFetcherDelegator()

def fetch_data_violation() -> List[str]:
    """VIOLATION: Speculative layers of indirection with zero polymorphism or value."""
    factory = DataFetcherFactory()
    return factory.get_instance().fetch_items()


# --- SAFE IMPLEMENTATION ---
def fetch_system_tags_safe() -> List[str]:
    """SAFE: Simple, direct function providing clear maintainability without indirection overhead."""
    return ["alpha", "beta", "gamma"]


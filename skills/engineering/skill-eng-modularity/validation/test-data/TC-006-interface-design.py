# TC-006: Interface and Abstraction Design

from abc import ABC, abstractmethod

# VIOLATION: Fat interface forcing implementers to write unused stub methods (ISP violation)
class IWorkerFatInterface(ABC):
    @abstractmethod
    def code((self)): pass
    @abstractmethod
    def test(self): pass
    @abstractmethod
    def deploy(self): pass
    @abstractmethod
    def design_ui(self): pass

class BackendDeveloperViolation(IWorkerFatInterface):
    def code(self): print("Coding python")
    def test(self): print("Running pytest")
    def deploy(self): print("Deploying docker container")
    def design_ui(self): raise NotImplementedError("Backend devs don't design UI") # Stub


# SAFE: Segregated focused interfaces
class ICoder(ABC):
    @abstractmethod
    def code(self): pass

class ITester(ABC):
    @abstractmethod
    def test(self): pass

class BackendDeveloperSafe(ICoder, ITester):
    def code(self): print("Coding python")
    def test(self): print("Running pytest")


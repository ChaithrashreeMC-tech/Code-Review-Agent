# Model Provider Abstraction & Configuration

This reference documents the patterns for abstracting LLM providers, centralizing model client construction, managing configuration and credentials, and enabling deterministic test doubles.

---

## 1. Cloud-Agnostic LLM Architecture

The codebase remains cloud-agnostic and provider-independent. Agent nodes must depend on standard interface types rather than vendor-specific SDK classes:

```text
+------------------------------+
|   agents/graphs/[feature]/   |  <-- Nodes depend ONLY on BaseChatModel interface
+------------------------------+
               |
               v (requests model via factory)
+------------------------------+
|         agents/llm/          |  <-- Model factory interface & configuration contracts
+------------------------------+
               |
               v (concrete instantiation)
+------------------------------+
|       infrastructure/        |  <-- Concrete provider implementations
|   (OpenAI, Anthropic, Bedrock)|      configured via pydantic-settings
+------------------------------+
```

---

## 2. Core Implementation Patterns

### A. Model Factory & Provider Interface
Nodes never import `openai.OpenAI` or `anthropic.Anthropic`. They request models through `agents/llm/`:

```python
# agents/llm/factory.py
from langchain_core.language_models.chat_models import BaseChatModel
from infrastructure.llm_providers import get_configured_chat_model

def get_agent_llm(model_role: str = "default") -> BaseChatModel:
    """Return a configured BaseChatModel instance for the requested agent role."""
    return get_configured_chat_model(role=model_role)
```

### B. Concrete Provider Instantiation in Infrastructure
```python
# infrastructure/llm_providers.py
from langchain_core.language_models.chat_models import BaseChatModel
from infrastructure.config import settings

def get_configured_chat_model(role: str = "default") -> BaseChatModel:
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.OPENAI_MODEL_NAME,
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            temperature=settings.LLM_TEMPERATURE
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.ANTHROPIC_MODEL_NAME,
            api_key=settings.ANTHROPIC_API_KEY.get_secret_value(),
            temperature=settings.LLM_TEMPERATURE
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
```

---

## 3. Configuration & Credential Safety Rules

1. **No Hardcoded Keys**: API keys, tokens, and model endpoints must never appear in source code, graph state, prompts, or log statements.
2. **Pydantic Settings**: All LLM settings must be loaded through environment variables and `pydantic-settings` with `SecretStr` for credentials.
3. **No Direct Node Construction**: Node modules must never instantiate vendor clients directly (e.g. `client = OpenAI(api_key="...")`). Doing so introduces tight vendor lock-in and breaks automated unit testing.

---

## 4. Test Doubles for Deterministic Unit Testing

Unit tests for agent workflows must never call live external model APIs. Use LangChain's built-in fake models:

```python
# tests/agent_tests/helpers.py
from langchain_core.language_models.fake_chat_models import FakeListChatModel

def get_mock_llm(responses: list[str]) -> FakeListChatModel:
    """Return a deterministic FakeListChatModel yielding predetermined responses."""
    return FakeListChatModel(responses=responses)

# tests/agent_tests/graphs/triage/test_supervisor.py
import pytest
from tests.agent_tests.helpers import get_mock_llm
from agents.graphs.triage.nodes.supervisor import supervisor_node

@pytest.mark.asyncio
async def test_supervisor_routes_to_code_agent():
    mock_llm = get_mock_llm(['{"next_agent": "code_agent", "instructions": "Review PR"}'])
    state = {"task": "Review PR #123", "iteration_count": 0}
    
    result = await supervisor_node(state, llm=mock_llm)
    
    assert result["next_step"] == "code_agent"
    assert result["iteration_count"] == 1
```


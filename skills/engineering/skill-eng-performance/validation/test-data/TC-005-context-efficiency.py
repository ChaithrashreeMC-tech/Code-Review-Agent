# TC-005: LLM Context Efficiency (PERF06 violation)
# Expected: PERF06 finding, severity=high, confidence=high
# Technology: Python / LangChain / OpenAI SDK

from openai import AsyncOpenAI
import tiktoken

LARGE_SYSTEM_DOC = """
[Imagine this is a 3,000-token product specification document embedded
verbatim in every single system prompt regardless of the user's question.
This is injected unconditionally on every API call.]
""" * 50  # simulating ~3,000 tokens of static content

client = AsyncOpenAI()


# --- VIOLATION: Full history + large static doc on every call ---
async def chat_with_full_history(conversation_history: list[dict], user_msg: str) -> str:
    """
    VIOLATION: Injects the full conversation_history (unbounded growth) AND
    a 3,000-token static document into every prompt.
    After 20 turns the context window overflows; costs escalate linearly.
    """
    messages = [
        {
            "role": "system",
            # VIOLATION: 3,000 tokens of static content on every call
            "content": f"You are a helpful assistant.\n\n{LARGE_SYSTEM_DOC}",
        },
        # VIOLATION: Full unbounded history
        *conversation_history,
        {"role": "user", "content": user_msg},
    ]
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response.choices[0].message.content


# --- VIOLATION: Per-item LLM calls in a loop ---
async def classify_products_loop(products: list[dict]) -> list[dict]:
    """
    VIOLATION: Calls the LLM once per product. For 200 products this is
    200 API calls. A single structured batch prompt could handle all at once.
    """
    results = []
    for product in products:
        # VIOLATION: one LLM call per item
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Classify the product category."},
                {"role": "user", "content": str(product)},
            ],
        )
        results.append({
            "product_id": product["id"],
            "category": response.choices[0].message.content,
        })
    return results


# --- SAFE: Rolling-window history with token budget ---
ENCODING = tiktoken.encoding_for_model("gpt-4o")
MAX_HISTORY_TOKENS = 2000


def trim_history(history: list[dict], max_tokens: int = MAX_HISTORY_TOKENS) -> list[dict]:
    """Trims oldest messages to stay within token budget."""
    trimmed = list(history)
    while trimmed:
        total = sum(
            len(ENCODING.encode(m["content"])) for m in trimmed
        )
        if total <= max_tokens:
            break
        trimmed.pop(0)  # remove oldest message
    return trimmed


async def chat_with_trimmed_history(conversation_history: list[dict], user_msg: str) -> str:
    """
    SAFE: Trims history to a token budget before injecting.
    Static system prompt is concise (< 100 tokens).
    """
    trimmed = trim_history(conversation_history)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *trimmed,
        {"role": "user", "content": user_msg},
    ]
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response.choices[0].message.content


# NOT APPLICABLE: Short 3-turn conversation — full history is fine
async def short_chat_full_history(history: list[dict], user_msg: str) -> str:
    """
    NOT APPLICABLE: 3 messages in history, well within token budget.
    PERF06 should not be flagged for short conversations.
    """
    assert len(history) <= 6, "Use trim_history for longer conversations"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *history,
        {"role": "user", "content": user_msg},
    ]
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content


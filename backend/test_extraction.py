import asyncio

from app.models.schemas import ConversationRequest, Message
from app.services.extraction import ExtractionService

service = ExtractionService()


# ── Test 1: Multiple atomic facts in one message ────────────────────────────
multi_fact_request = ConversationRequest(
    user_id="test-user-1",
    messages=[
        Message(role="user", content="Hi, I'm Aryan. I love Japanese food and I'm moving to Gurgaon next month.")
    ]
)

# ── Test 2: Zero storable facts (filler / question) ─────────────────────────
filler_request = ConversationRequest(
    user_id="test-user-1",
    messages=[
        Message(role="user", content="lol that's funny"),
        Message(role="assistant", content="Glad you enjoyed it!"),
        Message(role="user", content="what time is it?"),
    ]
)

# ── Test 3: Multi-turn with assistant replies ────────────────────────────────
multi_turn_request = ConversationRequest(
    user_id="test-user-1",
    messages=[
        Message(role="user", content="I work as a software engineer at a startup."),
        Message(role="assistant", content="That sounds exciting! What kind of startup?"),
        Message(role="user", content="We're building an AI product. I also play guitar on weekends."),
        Message(role="assistant", content="Nice! How long have you been playing?"),
        Message(role="user", content="About 5 years now."),
    ]
)


async def main():
    print("=" * 60)
    print("TEST 1: Multiple atomic facts in one message")
    print("=" * 60)
    result = await service.extract_facts(multi_fact_request)
    print(f"  → {len(result.facts)} fact(s) extracted")
    for f in result.facts:
        print(f"    [{f.category}] {f.key} = {f.value!r}  (confidence={f.confidence:.2f})")

    print()
    print("=" * 60)
    print("TEST 2: Zero storable facts (filler/questions only)")
    print("=" * 60)
    result = await service.extract_facts(filler_request)
    print(f"  → {len(result.facts)} fact(s) extracted (expected: 0)")
    for f in result.facts:
        print(f"    [{f.category}] {f.key} = {f.value!r}  (confidence={f.confidence:.2f})")

    print()
    print("=" * 60)
    print("TEST 3: Multi-turn conversation (assistant replies should be ignored)")
    print("=" * 60)
    result = await service.extract_facts(multi_turn_request)
    print(f"  → {len(result.facts)} fact(s) extracted")
    for f in result.facts:
        print(f"    [{f.category}] {f.key} = {f.value!r}  (confidence={f.confidence:.2f})")


asyncio.run(main())
from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import TypeAdapter

from app.core.config import settings
from app.models.schemas import ConversationRequest, ExtractionResponse

client = genai.Client(api_key=settings.google_api_key)


class ExtractionService:

    async def extract_facts(self, request: ConversationRequest) -> ExtractionResponse:
        conversation = "\n".join(
            f"{message.role}: {message.content}"
            for message in request.messages
        )

        prompt = f"""<task>
Extract durable, atomic facts about the USER from the conversation below,
for long-term memory storage.
</task>

<categories>
preference: Things the user likes, dislikes, enjoys, or regularly does for enjoyment (hobbies, recreational habits, taste).
fact: Stable, durable information about the user (where they live, their job, physical traits).
relationship: Connections to a SPECIFIC named person, company, or group (e.g. "works at StarBoard AI", "married to Neha", "friends with Raj"). Do not use this category for general descriptive attributes about the user's job, lifestyle, or environment — those belong in `fact`.
plan: Future intentions expected to remain relevant for weeks or months.
event: Past occurrences worth remembering as context (not the user's permanent traits).
</categories>

<rules>
- Each fact must be atomic: one idea per fact.
- Do not extract: greetings, jokes, questions, temporary emotions, assistant replies, filler.
- confidence reflects how explicitly the conversation stated this fact, not how important it is.
</rules>

<examples>
Input: "Hi, I'm Priya, and I've been really into rock climbing lately."
Output:
- category: fact, text: "Name is Priya", confidence: 0.98
  (reason: stated as a direct, unambiguous self-introduction)
- category: preference, text: "Enjoys rock climbing", confidence: 0.85
  (reason: stated as a current interest, but "lately" softens permanence slightly)

Input: "I think I might want to switch careers into design at some point, not sure when."
Output:
- category: plan, text: "Considering a career switch to design", confidence: 0.55
  (reason: explicitly hedged with "I think," "might," and "not sure when" — low certainty about the plan itself)

Input: "My sister Riya just got into IIT Bombay."
Output:
- category: relationship, text: "Has a sister named Riya", confidence: 0.95
  (reason: stated as plain fact)
- category: event, text: "Sister got into IIT Bombay", confidence: 0.95
  (reason: stated as a clear, recent, unambiguous event)

Input: "I work at a fintech startup as a backend engineer."
Output:
- category: fact, text: "Works as a backend engineer", confidence: 0.95
  (reason: stable role information about the user — not a named connection)
- category: fact, text: "Works at a fintech startup", confidence: 0.9
  (reason: describes employer type/industry, not a specific named organization — stays in fact, not relationship)
</examples>

<conversation>
{conversation}
</conversation>"""

        response = await client.aio.models.generate_content(
            model=settings.model_name,
            contents=prompt,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResponse,
            ),
        )

        adapter = TypeAdapter(ExtractionResponse)
        facts = adapter.validate_json(response.text)
        return facts
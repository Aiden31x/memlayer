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

        prompt = f"""You are an information extraction system.

            Your job is to identify durable facts about the USER
            that are useful for long-term memory.

            Extract only facts that are likely to remain true
            or be useful in future conversations.

        Store:
                - personal information
                - preferences
                - relationships
                - long-term goals
                - recurring habits
                - skills
                - background
                - plans that span weeks or months


        Do NOT store:

            - greetings
            - jokes
            - temporary emotions
            - questions
            - assistant responses
            - obvious conversational filler

        Each extracted fact should be atomic.

        Good:
        "I like coffee."

        Bad:
        "I like coffee and tea and pizza."

        Category meanings:

        preference:
        Things the user likes or dislikes.

        fact:
        Stable information about the user.

        relationship:
        Connections to family, friends, coworkers,
        or organizations.

        plan:
        Future intentions that are expected
        to remain relevant.

        event:
        Past events worth remembering.

      Conversation:
        {conversation}"""

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
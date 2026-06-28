from app.models.schemas import ConversationRequest, ExtractionResponse

class ExtractionService:

    def extract_facts(self, request: ConversationRequest) -> ExtractionResponse:


        #TODO: Implement the extraction logic

        return ExtractionResponse(facts=[])
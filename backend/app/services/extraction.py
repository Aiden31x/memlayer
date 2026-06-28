from app.models.schemas import ConversationRequest, ExtractedFact, ExtractionResponse

class ExtractionService:

    def extract_facts(self, request: ConversationRequest) -> ExtractionResponse:


        #TODO: Implement the extraction logic

        return ExtractionResponse(facts=[ExtractedFact  (category="test", key="test", value="test", confidence=0.9, evidence="test")])
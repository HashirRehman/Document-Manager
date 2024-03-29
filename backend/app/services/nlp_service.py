from langchain import LangChain

class NLPService:

    def __init__(self):
        self.langchain = LangChain()

    async def search_and_get_answer(self, question: str) -> str:
        return await self.langchain.search_and_get_answer(question)

    async def analyze_sentiment(self, text: str) -> SentimentAnalysisResponse:
        sentiment_result = await self.langchain.analyze_sentiment(text)
        return sentiment_result

    async def extract_entities(self, text: str) -> List[EntityExtractionResponse]:
        entity_results = await self.langchain.extract_entities(text)
        return entity_results

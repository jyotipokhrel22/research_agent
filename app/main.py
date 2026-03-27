# app/main.py or wherever you wire things
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm import LLMClient
from app.services.extractor import PaperExtractor
from app.services.arxiv_client import ArxivClient
from app.config import OPENROUTER_API_KEY, MODEL_NAME

llm = LLMClient(api_key=OPENROUTER_API_KEY, model=MODEL_NAME)
extractor = PaperExtractor(llm)
arxiv_client = ArxivClient()


query = "transformer image classification"

raw_papers = arxiv_client.search(query, max_results=5)

papers = []

for i, raw in enumerate(raw_papers):
    print(f"\n===== PAPER {i+1} =====")
    print("TITLE:", raw["title"])

    content = raw["abstract"]

    extracted = extractor.extract(content)

    if extracted:
        # inject metadata (IMPORTANT)
        extracted.paper_id = raw["paper_id"]
        extracted.title = raw["title"]
        extracted.year = raw["year"]

        papers.append(extracted)

        print("\nEXTRACTED:")
        print(extracted)
    else:
        print("Extraction failed")

print(f"\nTotal extracted: {len(papers)}")
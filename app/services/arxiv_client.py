import arxiv


class ArxivClient:
    def search(self, query: str, max_results: int = 5):
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []

        for result in search.results():
            papers.append({
                "paper_id": result.entry_id,
                "title": result.title,
                "abstract": result.summary,
                "year": result.published.year
            })

        return papers
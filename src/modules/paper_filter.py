from dataclasses import asdict

from more_itertools import ichunked
from tqdm import tqdm

from modules.llm_interface import LLMInterface
from modules.paper import Paper
from utils.prompts import SYSTEM_PROMPT, USER_PROMPT


class PaperFilter:
    """
    A class to filter a list of papers using a Language Learning Model (LLM).

    Attributes:
        papers (list[Paper]): A list of `Paper` objects to filter.
        llm (LLMInterface): An interface to interact with the LLM.
        system_prompt (str): The system prompt to initialize the LLM.
        user_prompt (str): The user prompt template for the LLM.
    """

    def __init__(self, llm: LLMInterface):
        """
        Initializes the PaperFilter with a list of papers and an LLM interface.

        Args:
            llm (LLMInterface): An instance of `LLMInterface` to interact with the LLM.
        """
        self.llm = llm
        self.system_prompt = SYSTEM_PROMPT
        self.user_prompt = USER_PROMPT

    def filter(self, papers: list[Paper], query: str, mode: str = "matching") -> list[Paper]:
        """
        Filters a list of papers using a keyword or the LLM.

        Args:
            papers (list[Paper]): A list of `Paper` objects to filter.
            query (str): The keyword or query to filter the papers.
            mode (str): The filtering mode to use. Defaults to "matching".

        Returns:
            list[Paper]: A list of filtered `Paper` objects.
        """
        if mode == "matching":
            return self._filter_by_matching(papers=papers, query=query)
        elif mode == "llm":
            return self._filter_by_llm(papers=papers, query=query)
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def _filter_by_matching(self, papers: list[Paper], query: str) -> list[Paper]:
        """
        Filters the list of papers using a keyword.

        Args:
            papers (list[Paper]): A list of `Paper` objects to filter.
            keyword (str): The keyword to filter the papers.

        Returns:
            list[Paper]: A list of filtered `Paper` objects.
        """
        filtered_papers = []
        for paper in tqdm(papers):
            if query in paper.title or query in paper.abstract:
                filtered_papers.append(paper)
        return filtered_papers

    def _filter_by_llm(
        self, papers: list[Paper], query: str, chunk_size: int = 10
    ) -> list[Paper]:
        """
        Filters the list of papers using the LLM.

        Args:
            papers (list[Paper]): A list of `Paper` objects to filter.
            query (str): The query to filter the papers.
            chunk_size (int): The number of papers to process in a single batch. Defaults to 10.

        Returns:
            list[Paper]: A list of filtered `Paper` objects.

        Notes:
            - Currently, only the default filtering algorithm is implemented.
            - The method processes up to 15 papers, split into chunks of the specified size.
        """
        filtered_papers = []
        for chunk in ichunked(tqdm(papers), chunk_size):
            papers_str = "\n".join([str(asdict(paper)) for paper in chunk])
            results = self.llm.generate(
                system_prompt=self.system_prompt,
                user_prompt=self.user_prompt.format(query=query, papers=papers_str),
            )
            filtered_papers += results.papers
        return filtered_papers


if __name__ == "__main__":
    paper_filter = ""

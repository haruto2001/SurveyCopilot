from dataclasses import asdict

from modules.llm_interface import LLMInterface
from modules.paper import Paper


class PaperFilter:
    """Filters a list of papers using a language model interface.

    Args:
        papers (list[Paper]): A list of Paper objects to filter.
        llm (LLMInterface): An instance of a language model interface for filtering.
    """

    def __init__(self, papers: list[Paper], llm: LLMInterface):
        """Initializes the PaperFilter with papers and a language model interface.

        Args:
            papers (list[Paper]): A list of Paper objects to filter.
            llm (LLMInterface): An instance of a language model interface for filtering.
        """
        self.papers = papers
        self.llm = llm

    def filter(self) -> list[Paper]:  # TODO: 他のアルゴリズムを実装する
        """Filters the list of papers using the language model.

        The method takes the first 5 papers from the list, converts them to strings, and sends
        them to the language model to select 3 papers based on its internal logic.

        Returns:
            list[Paper]: A filtered list of 3 Paper objects selected by the language model.

        Note:
            If the number of papers exceeds 5, the filtering process should ideally be executed
            in multiple iterations (TODO: implement this in the future).
        """
        papers = "\n".join([str(asdict(paper)) for paper in self.papers[:5]])  # TODO: 数が多い場合は数回に分けて実行
        system_prompt = "You are a helpful assistant."
        user_prompt = f"choose 3 papers.\n\n{papers}"
        results = self.llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        filtered_papers = results.papers
        return filtered_papers


if __name__ == "__main__":
    paper_filter = ""

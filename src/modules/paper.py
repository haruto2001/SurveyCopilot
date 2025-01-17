from dataclasses import dataclass


@dataclass(frozen=True)
class Paper:
    """A class representing a research paper.

    Attributes:
        title (str): The title of the paper.
        authors (list[str]): A list of authors' names who contributed to the paper.
        abstract (str): A brief summary or abstract of the paper.
    """
    title: str
    authors: list[str]
    abstract: str
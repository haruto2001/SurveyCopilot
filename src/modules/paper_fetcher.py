import json
import os
import xml.etree.ElementTree as ET
from dataclasses import asdict
from urllib.parse import urlencode

import feedparser

from modules.paper import Paper
from modules.query_params import AclAnthologyQueryParams, ArxivQueryParams


class PaperFetcher:
    """Base class for fetching and handling research papers.

    Attributes:
        papers (list[Paper]): A list to store fetched `Paper` objects.
    """

    def __init__(self):
        """
        Initializes a PaperFetcher instance.

        Attributes:
            papers (list[Paper]): A list to store fetched `Paper` objects.
        """
        self.papers = []

    def __len__(self):
        """
        Returns the number of fetched papers.

        Returns:
            int: The number of papers stored in `self.papers`.
        """
        return self.papers

    def export(self, save_path: str) -> None:
        """
        Exports the stored papers to a JSON Lines file.

        Args:
            save_path (str): The path to save the exported JSON file.

        Note:
            This method creates the necessary directories if they do not exist.
        """
        exported_papers = [asdict(paper) for paper in self.papers]
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, mode="w") as f:
            f.writelines([json.dumps(paper) + "\n" for paper in exported_papers])


class AclAnthologyPaperFetcher(PaperFetcher):
    """A class for fetching research papers from the ACL Anthology dataset.

    Attributes:
        data_dir (str): The directory containing ACL Anthology XML files.
    """

    def __init__(self):
        """
        Initializes an AclAnthologyPaperFetcher instance.

        Attributes:
            data_dir (str): The directory containing ACL Anthology XML files.
        """
        super().__init__()
        self.data_dir = "/work/tools/acl-anthology/data/xml"

    def fetch(self, params: AclAnthologyQueryParams) -> list[Paper]:
        """
        Fetches papers from the ACL Anthology dataset.

        Args:
            year (int): The year of the conference.
            conference (str): The acronym of the conference.

        Returns:
            list[Paper]: A list of fetched `Paper` objects.
        """
        xml_path = os.path.join(self.data_dir, f"{params.year}.{params.conference}.xml")
        tree = ET.parse(xml_path)
        fetched_papers = self._parse_tree(tree)
        self.papers += fetched_papers
        return fetched_papers

    def _parse_tree(self, tree: ET.ElementTree) -> list[Paper]:
        """
        Parses an XML tree into a list of `Paper` objects.

        Args:
            tree (ET.ElementTree): The XML tree to parse.

        Returns:
            list[Paper]: A list of parsed `Paper` objects.
        """
        root = tree.getroot()
        fetched_papers = [
            Paper(
                title=element.findtext("title"),
                authors=[
                    " ".join(
                        [author.findtext("first"), author.findtext("last")]
                    )  # "first_name last_name"の形式
                    for author in element.findall("author")
                ],
                abstract=element.findtext("abstract"),
            )
            for element in root.findall(".//paper")
        ]
        return fetched_papers


class ArxivPaperFetcher(PaperFetcher):  # ?: Papersクラスも欲しいかも？
    """A class for fetching research papers from the arXiv API.

    Attributes:
        base_url (str): The base URL for the arXiv API.
    """

    def __init__(self):
        """
        Initializes an ArxivPaperFetcher instance.

        Attributes:
            base_url (str): The base URL for the arXiv API.
        """
        super().__init__()
        self.base_url = "https://export.arxiv.org/api/query"

    def fetch(self, params: ArxivQueryParams) -> list[Paper]:
        """
        Fetches papers from the arXiv API based on the specified criteria.

        Args:
            category (str, optional): The arXiv category. Defaults to "cs.CL".
            start (str, optional): The start date in the format YYYYMMDD. Defaults to "20240101".
            end (str, optional): The end date in the format YYYYMMDD. Defaults to "20240102".
            max_results (int, optional): The maximum number of results to fetch. Defaults to 10.

        Returns:
            list[Paper]: A list of fetched `Paper` objects.
        """
        query = self._build_query(
            category=params.category,
            start=params.start,
            end=params.end,
            max_results=params.max_results,
        )
        url = self.base_url + "?" + query
        feed = feedparser.parse(url)
        fetched_papers = self._parse_feed(feed)
        self.papers += fetched_papers
        return fetched_papers

    def _build_query(self, category: str, start: str, end: str, max_results: int):
        """
        Builds a query string for the arXiv API.

        Args:
            category (str): The arXiv category.
            start (str): The start date in the format YYYYMMDD.
            end (str): The end date in the format YYYYMMDD.
            max_results (int): The maximum number of results to fetch.

        Returns:
            str: The constructed query string.
        """
        params = {
            "search_query": f"cat:{category} AND submittedDate:[{start} TO {end}]",
            "max_results": max_results,
        }
        query = urlencode(params)
        return query

    def _parse_feed(self, feed: feedparser.FeedParserDict) -> list[Paper]:
        """
        Parses the fetched feed into a list of `Paper` objects.

        Args:
            feed (feedparser.FeedParserDict): The feed data fetched from the arXiv API.

        Returns:
            list[Paper]: A list of parsed `Paper` objects.
        """
        parsed_papers = [
            Paper(
                title=entry.title,
                authors=[author.name for author in entry.authors],
                abstract=entry.summary,
            )
            for entry in feed.entries
        ]
        return parsed_papers

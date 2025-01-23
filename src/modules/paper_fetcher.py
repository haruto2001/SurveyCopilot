import json
import os
import xml.etree.ElementTree as ET
from dataclasses import asdict
from urllib.parse import urlencode

import feedparser
import openreview

from paper import Paper
from query_params import ArxivQueryParams, ConferenceQueryParams


class PaperFetcher:
    """Base class for fetching and handling research papers.

    Attributes:
        papers (list[Paper]): A list to store fetched `Paper` objects.
    """

    def __init__(self) -> None:
        """
        Initializes a PaperFetcher instance.

        Attributes:
            papers (list[Paper]): A list to store fetched `Paper` objects.
        """
        self.papers = []

    def __len__(self) -> int:
        """
        Returns the number of fetched papers.

        Returns:
            int: The number of papers stored in `self.papers`.
        """
        return len(self.papers)

    def _update_papers(self, new_papers: list[Paper]) -> None:
        """
        Updates the list of fetched papers.

        Args:
            fetched_papers (list[Paper]): A list of fetched `Paper` objects.
        """
        self.papers += new_papers

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

    def __init__(self) -> None:
        """
        Initializes an AclAnthologyPaperFetcher instance.

        Attributes:
            data_dir (str): The directory containing ACL Anthology XML files.
        """
        super().__init__()
        self.data_dir = "/work/tools/acl-anthology/data/xml"

    def fetch(self, params: ConferenceQueryParams) -> list[Paper]:
        """
        Fetches papers from the ACL Anthology dataset.

        Args:
            params (ConferenceQueryParams): Query parameters including year and conference.

        Returns:
            list[Paper]: A list of fetched `Paper` objects.
        """
        xml_path = os.path.join(self.data_dir, f"{params.year}.{params.conference}.xml")
        tree = ET.parse(xml_path)
        fetched_papers = self._parse_tree(tree)
        self._update_papers(fetched_papers)
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

    def __init__(self) -> None:
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
            params (ArxivQueryParams): The query parameters including category, start date, end date, and max results.

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
        self._update_papers(fetched_papers)
        return fetched_papers

    def _build_query(self, params: ArxivQueryParams) -> str:
        """
        Builds a query string for the arXiv API.

        Args:
            params (ArxivQueryParams): The query parameters including category, start date, end date, and max results.

        Returns:
            str: The constructed query string.
        """
        query_params = {
            "search_query": f"cat:{params.category} AND submittedDate:[{params.start} TO {params.end}]",
            "max_results": params.max_results,
        }
        query = urlencode(query_params)
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


class OpenReviewPaperFetcher(PaperFetcher):
    """Fetches papers from OpenReview using provided credentials and query parameters.

    Attributes:
        client (openreview.Client): A client instance for interacting with the OpenReview API.
    """

    def __init__(self, username: str, password: str) -> None:
        """Initializes the OpenReviewPaperFetcher with the provided credentials.

        Args:
            username (str): The username for OpenReview authentication.
            password (str): The password for OpenReview authentication.
        """
        super().__init__()
        self.client = openreview.Client(
            baseurl="https://api.openreview.net",
            username=username,
            password=password,
        )

    def fetch(self, params: ConferenceQueryParams) -> list[Paper]:
        """Fetches papers based on the specified query parameters.

        Args:
            params (ConferenceQueryParams): The query parameters containing the conference name and year.

        Returns:
            list[Paper]: A list of `Paper` objects fetched from OpenReview.

        Example:
            params = ConferenceQueryParams(conference="ICLR", year=2024)
            papers = fetcher.fetch(params)
        """
        invitation = f"{params.conference}.cc/{params.year}/Conference/-/Blind_Submission"
        notes = openreview.tools.iterget_notes(self.client, invitation=invitation)
        fetched_papers = [
            Paper(
                title=note.content["title"],
                authors=note.content["authors"],
                abstract=note.content["abstract"],
            )
            for note in notes
        ]
        self._update_papers(fetched_papers)
        return fetched_papers

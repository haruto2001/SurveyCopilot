from typing import Optional, Union

from modules.paper import Paper
from modules.paper_fetcher import AclAnthologyPaperFetcher, ArxivPaperFetcher
from modules.paper_filter import PaperFilter
from modules.query_params import AclAnthologyQueryParams, ArxivQueryParams
from modules.slack_notifier import SlackPaperNotifier


class Pipeline:
    def __init__(
        self,
        paper_fetcher: Union[AclAnthologyPaperFetcher, ArxivPaperFetcher],
        paper_filter: PaperFilter,
        slack_notifier: Optional[SlackPaperNotifier] = None,
    ) -> None:
        self.paper_fetcher = paper_fetcher
        self.paper_filter = paper_filter
        self.slack_notifier = slack_notifier

    def run(  # TODO: exportに対応させる（フィルタ後のpaperを保存できるように）
        self,
        fetching_params: Union[AclAnthologyQueryParams, ArxivQueryParams],
        filtering_query: str,
        save_path: Optional[str] = None,
    ) -> list[Paper]:
        papers = self.paper_fetcher.fetch(params=fetching_params)
        filtered_papers = self.paper_filter.filter(query=filtering_query, papers=papers)
        if self.slack_notifier is not None:
            self.slack_notifier.send_message(message=f"Query: {filtering_query}")
            for paper in filtered_papers:
                self.slack_notifier.send_message(message=paper)
        return filtered_papers

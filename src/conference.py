import argparse
import os

from modules.llm_interface import LLMInterface
from modules.paper_fetcher import AclAnthologyPaperFetcher, OpenReviewPaperFetcher
from modules.paper_filter import PaperFilter
from modules.pipeline import Pipeline
from modules.query_params import ConferenceQueryParams
from modules.slack_notifier import SlackPaperNotifier
from utils.functions import is_in_acl_anthology, is_in_openreview, print_paper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter research papers using a Language Learning Model."
    )
    parser.add_argument(
        "-conference", type=str, default="acl", help="The conference to fetch."
    )
    parser.add_argument(
        "--year", type=int, default=2024, help="The year of the conference."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Choose papers related to 'Large Vision Language Models'.",
        help="The query to filter papers.",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    if is_in_acl_anthology(conference=args.conference):
        paper_fetcher = AclAnthologyPaperFetcher()
    elif is_in_openreview(conference=args.conference):
        paper_fetcher = OpenReviewPaperFetcher()
    else:
        raise ValueError(f"Conference '{args.conference}' is not supported.")

    paper_fetcher = AclAnthologyPaperFetcher()
    llm = LLMInterface(api_key=os.environ.get("OPENAI_API_KEY"))
    paper_filter = PaperFilter(llm=llm)
    slack_notifier = SlackPaperNotifier(bot_token=os.environ.get("SLACK_BOT_TOKEN"))

    pipeline = Pipeline(
        paper_fetcher=paper_fetcher,
        paper_filter=paper_filter,
        slack_notifier=slack_notifier,
    )
    params = ConferenceQueryParams(
        conference=args.conference,
        year=args.year,
    )
    papers = pipeline.run(fetching_params=params, filtering_query=args.prompt)

    for paper in papers:
        print_paper(paper)


if __name__ == "__main__":
    args = parse_args()
    main(args)

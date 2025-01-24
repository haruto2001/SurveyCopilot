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
        "-conference", type=str, default="ACL", help="The conference to fetch."
    )
    parser.add_argument(
        "--year", type=int, default=2024, help="The year of the conference."
    )
    parser.add_argument(
        "--filtering_mode",
        type=str,
        default="matching",
        choices=["matching", "llm"],
        help="The filtering mode to use.",
    )
    parser.add_argument(
        "--keyword", type=str, default="LVLM", help="The keyword to filter papers."
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
        params = ConferenceQueryParams(
            conference=args.conference.lower(),
            year=args.year,
        )
    elif is_in_openreview(conference=args.conference):
        paper_fetcher = OpenReviewPaperFetcher()
        params = ConferenceQueryParams(
            conference=args.conference,
            year=args.year,
        )
    else:
        raise ValueError(f"Conference '{args.conference}' is not supported.")

    llm = LLMInterface(api_key=os.environ.get("OPENAI_API_KEY"))
    paper_filter = PaperFilter(llm=llm)
    slack_notifier = SlackPaperNotifier(bot_token=os.environ.get("SLACK_BOT_TOKEN"))

    pipeline = Pipeline(
        paper_fetcher=paper_fetcher,
        paper_filter=paper_filter,
        slack_notifier=slack_notifier,
    )

    if args.filtering_mode == "matching":
        filtering_query = args.keyword
    elif args.filtering_mode == "llm":
        filtering_query = args.prompt
    else:
        raise ValueError(f"Invalid filtering mode: {args.filtering_mode}")
    papers = pipeline.run(
        fetching_params=params,
        filtering_query=filtering_query,
        filtering_mode=args.filtering_mode,
    )

    for paper in papers:
        print_paper(paper)


if __name__ == "__main__":
    args = parse_args()
    main(args)

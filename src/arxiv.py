import argparse
import os

from modules.llm_interface import LLMInterface
from modules.paper_fetcher import ArxivPaperFetcher
from modules.paper_filter import PaperFilter
from modules.pipeline import Pipeline
from modules.query_params import ArxivQueryParams
from modules.slack_notifier import SlackPaperNotifier
from utils.functions import print_paper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter research papers using a Language Learning Model."
    )
    parser.add_argument(
        "--category", type=str, default="cs.CL", help="The category of papers to fetch."
    )
    parser.add_argument(
        "--start",
        type=int,
        default="20240101",
        help="The start date of papers to fetch.",
    )
    parser.add_argument(
        "--end", type=int, default="20240102", help="The end date of papers to fetch."
    )
    parser.add_argument(
        "--max_results",
        type=int,
        default=100,
        help="The maximum number of papers to fetch.",
    )
    parser.add_argument(
        "--filtering_mode",
        type=str,
        default="matching",
        choices=["matching", "llm"],
        help="The filtering mode to use.",
    )
    parser.add_argument("--keyword", type=str, default="LVLM")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Choose papers related to 'Large Vision Language Models'.",
        help="The query to filter papers.",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    paper_fetcher = ArxivPaperFetcher()
    llm = LLMInterface(api_key=os.environ.get("OPENAI_API_KEY"))
    paper_filter = PaperFilter(llm=llm)
    slack_notifier = SlackPaperNotifier(bot_token=os.environ.get("SLACK_BOT_TOKEN"))

    pipeline = Pipeline(
        paper_fetcher=paper_fetcher,
        paper_filter=paper_filter,
        slack_notifier=slack_notifier,
    )
    params = ArxivQueryParams(
        category=args.category,
        start=args.start,
        end=args.end,
        max_results=args.max_results,
    )

    if args.filtering_mode == "matching":
        filtering_query = args.keyword
    elif args.filtering_mode == "llm":
        filtering_query = args.prompt
    else:
        raise ValueError(f"Invalid filtering mode: {args.filtering_mode}")
    papers = pipeline.run(fetching_params=params, filtering_query=filtering_query, filtering_mode=args.filtering_mode)

    for paper in papers:
        print_paper(paper)


if __name__ == "__main__":
    args = parse_args()
    main(args)

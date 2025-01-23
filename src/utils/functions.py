from modules.paper import Paper


def is_in_acl_anthology(conference: str) -> bool:
    return conference in [
        "AACL",
        "ACL",
        "ALTA",
        "AMTA",
        "ArabicNLP",
        "CCL",
        "CL",
        "COLING",
        "CoNLL",
        "EACL",
        "EAMT",
        "EMNLP",
        "HLT",
        "IJCLCLP",
        "IJCNLP",
        "IWSLT",
        "JLCL",
        "KONVENS",
        "LILT",
        "LREC",
        "NAACL",
        "NEJLT",
        "NoDaLiDa",
        "PACLIC",
        "RANLP",
        "ROCLING",
        "SemEval",
        "TACL",
        "TAL",
        "WMT",
    ]


def is_in_openreview() -> bool:
    return ["ICLR", "NeurIPS"]


def print_paper(paper: Paper) -> None:
    print("-" * 30)
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join(paper.authors)}")
    print(f"Abstract: {paper.abstract}")
    print("-" * 30)

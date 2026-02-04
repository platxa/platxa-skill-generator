#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "huggingface_hub",
#     "pyyaml",
#     "requests",
#     "python-dotenv",
# ]
# ///
"""Paper Manager for Hugging Face Hub.

Manages paper indexing, linking to repositories, authorship claims,
visibility settings, and research article creation.

Usage:
    python3 paper_manager.py index --arxiv-id "2301.12345"
    python3 paper_manager.py check --arxiv-id "2301.12345"
    python3 paper_manager.py link --repo-id "user/model" --arxiv-id "2301.12345"
    python3 paper_manager.py claim --arxiv-id "2301.12345" --email "user@edu"
    python3 paper_manager.py create --template standard --title "Title" --output paper.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
    from dotenv import load_dotenv
    from huggingface_hub import HfApi, HfFolder, hf_hub_download
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install: pip install huggingface_hub pyyaml requests python-dotenv")
    sys.exit(1)

load_dotenv()


def clean_arxiv_id(arxiv_id: str) -> str:
    """Normalize arXiv ID by removing common prefixes and URL patterns."""
    arxiv_id = arxiv_id.strip()
    arxiv_id = re.sub(r"^(arxiv:|arXiv:)", "", arxiv_id, flags=re.IGNORECASE)
    arxiv_id = re.sub(r"https?://arxiv\.org/(abs|pdf)/", "", arxiv_id)
    arxiv_id = arxiv_id.replace(".pdf", "")
    return arxiv_id


def index_paper(arxiv_id: str) -> dict[str, Any]:
    """Check if a paper is indexed on HF and provide indexing URL."""
    arxiv_id = clean_arxiv_id(arxiv_id)
    paper_url = f"https://huggingface.co/papers/{arxiv_id}"

    try:
        response = requests.get(paper_url, timeout=10)
        if response.status_code == 200:
            print(f"Paper already indexed: {paper_url}")
            return {"status": "exists", "url": paper_url}
        print(f"Not indexed. Visit {paper_url} to trigger indexing.")
        return {"status": "not_indexed", "url": paper_url, "action": "visit_url"}
    except requests.RequestException as e:
        print(f"Error checking paper: {e}")
        return {"status": "error", "message": str(e)}


def check_paper(arxiv_id: str) -> dict[str, Any]:
    """Check if a paper exists on Hugging Face."""
    arxiv_id = clean_arxiv_id(arxiv_id)
    paper_url = f"https://huggingface.co/papers/{arxiv_id}"

    try:
        response = requests.get(paper_url, timeout=10)
        if response.status_code == 200:
            return {
                "exists": True,
                "url": paper_url,
                "arxiv_id": arxiv_id,
                "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
            }
        return {
            "exists": False,
            "arxiv_id": arxiv_id,
            "index_url": paper_url,
            "message": f"Visit {paper_url} to index",
        }
    except requests.RequestException as e:
        return {"exists": False, "error": str(e)}


def link_paper(
    repo_id: str,
    arxiv_id: str,
    repo_type: str = "model",
    citation: str | None = None,
) -> dict[str, Any]:
    """Link a paper to a repository by adding arXiv URL to README."""
    arxiv_id = clean_arxiv_id(arxiv_id)
    token = os.getenv("HF_TOKEN") or HfFolder.get_token()

    if not token:
        return {"status": "error", "message": "HF_TOKEN not set"}

    api = HfApi(token=token)
    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
    hf_paper_url = f"https://huggingface.co/papers/{arxiv_id}"

    try:
        readme_path = hf_hub_download(
            repo_id=repo_id,
            filename="README.md",
            repo_type=repo_type,
            token=token,
        )

        with open(readme_path, encoding="utf-8") as f:
            content = f.read()

        if arxiv_id in content:
            print(f"Paper {arxiv_id} already referenced in {repo_id}")
            return {"status": "already_linked", "repo_id": repo_id}

        # Build paper section
        paper_section = "\n## Paper\n\n"
        paper_section += f"**[arXiv]({arxiv_url})** | "
        paper_section += f"**[Paper Page]({hf_paper_url})**\n\n"

        if citation:
            paper_section += f"### Citation\n\n```bibtex\n{citation}\n```\n\n"

        # Insert after YAML frontmatter
        yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if yaml_match:
            insert_pos = yaml_match.end()
            updated = content[:insert_pos] + paper_section + content[insert_pos:]
        else:
            updated = "---\n---\n\n" + paper_section + content

        api.upload_file(
            path_or_fileobj=updated.encode("utf-8"),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type=repo_type,
            commit_message=f"Add paper reference: arXiv:{arxiv_id}",
            token=token,
        )

        print(f"Linked {arxiv_id} to {repo_id}")
        return {"status": "success", "paper_url": hf_paper_url, "repo_id": repo_id}

    except Exception as e:
        print(f"Error linking paper: {e}")
        return {"status": "error", "message": str(e)}


def get_arxiv_info(arxiv_id: str) -> dict[str, Any]:
    """Fetch paper metadata from arXiv API."""
    arxiv_id = clean_arxiv_id(arxiv_id)
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        text = response.text

        title_match = re.search(r"<title>(.*?)</title>", text, re.DOTALL)
        authors = re.findall(r"<name>(.*?)</name>", text)
        summary_match = re.search(r"<summary>(.*?)</summary>", text, re.DOTALL)

        return {
            "arxiv_id": arxiv_id,
            "title": title_match.group(1).strip() if title_match else None,
            "authors": authors[1:] if len(authors) > 1 else [],
            "abstract": summary_match.group(1).strip() if summary_match else None,
            "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        }
    except Exception as e:
        return {"error": str(e)}


def generate_bibtex(arxiv_id: str) -> str:
    """Generate BibTeX citation from arXiv metadata."""
    info = get_arxiv_info(arxiv_id)
    if "error" in info:
        return f"Error: {info['error']}"

    key = f"arxiv{arxiv_id.replace('.', '_')}"
    authors_str = " and ".join(info.get("authors", ["Unknown"]))
    title = info.get("title", "Untitled")
    year_prefix = arxiv_id.split(".")[0][:2]
    year = f"20{year_prefix}" if int(year_prefix) < 50 else f"19{year_prefix}"

    return (
        f"@article{{{key},\n"
        f"  title={{{title}}},\n"
        f"  author={{{authors_str}}},\n"
        f"  journal={{arXiv preprint arXiv:{arxiv_id}}},\n"
        f"  year={{{year}}}\n"
        f"}}"
    )


def create_article(
    template: str,
    title: str,
    output: str,
    authors: str | None = None,
    abstract: str | None = None,
) -> dict[str, Any]:
    """Create a research article from a markdown template."""
    template_dir = Path(__file__).parent.parent / "templates"
    template_file = template_dir / f"{template}.md"

    if not template_file.exists():
        available = [f.stem for f in template_dir.glob("*.md")] if template_dir.exists() else []
        return {
            "status": "error",
            "message": f"Template '{template}' not found. Available: {available}",
        }

    content = template_file.read_text()
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    content = content.replace("{{TITLE}}", title)
    content = content.replace("{{DATE}}", now)
    content = content.replace("{{AUTHORS}}", authors or "Author Name")
    content = content.replace("{{ABSTRACT}}", abstract or "Abstract to be written.")

    Path(output).write_text(content)
    print(f"Article created: {output}")
    return {"status": "success", "output": output, "template": template}


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Paper Manager for Hugging Face Hub")
    sub = parser.add_subparsers(dest="command", help="Command to run")

    p_index = sub.add_parser("index", help="Index a paper from arXiv")
    p_index.add_argument("--arxiv-id", required=True, help="arXiv paper ID")

    p_check = sub.add_parser("check", help="Check if paper exists on HF")
    p_check.add_argument("--arxiv-id", required=True, help="arXiv paper ID")

    p_link = sub.add_parser("link", help="Link paper to a repository")
    p_link.add_argument("--repo-id", required=True, help="Repository ID (user/repo)")
    p_link.add_argument("--repo-type", default="model", choices=["model", "dataset", "space"])
    p_link.add_argument("--arxiv-id", help="Single arXiv ID")
    p_link.add_argument("--arxiv-ids", help="Comma-separated arXiv IDs")
    p_link.add_argument("--citation", help="BibTeX citation text")

    p_claim = sub.add_parser("claim", help="Claim authorship on a paper")
    p_claim.add_argument("--arxiv-id", required=True, help="arXiv paper ID")
    p_claim.add_argument("--email", required=True, help="Author email for verification")

    p_create = sub.add_parser("create", help="Create research article from template")
    p_create.add_argument("--template", required=True, help="Template name")
    p_create.add_argument("--title", required=True, help="Paper title")
    p_create.add_argument("--output", required=True, help="Output file path")
    p_create.add_argument("--authors", help="Comma-separated author names")
    p_create.add_argument("--abstract", help="Abstract text")

    p_info = sub.add_parser("info", help="Get paper metadata from arXiv")
    p_info.add_argument("--arxiv-id", required=True, help="arXiv paper ID")

    p_citation = sub.add_parser("citation", help="Generate BibTeX citation")
    p_citation.add_argument("--arxiv-id", required=True, help="arXiv paper ID")

    sub.add_parser("list-my-papers", help="List your claimed papers")

    p_toggle = sub.add_parser("toggle-visibility", help="Toggle paper profile visibility")
    p_toggle.add_argument("--arxiv-id", required=True, help="arXiv paper ID")
    p_toggle.add_argument("--show", required=True, choices=["true", "false"])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "index":
        result = index_paper(args.arxiv_id)
        print(json.dumps(result, indent=2))

    elif args.command == "check":
        result = check_paper(args.arxiv_id)
        print(json.dumps(result, indent=2))

    elif args.command == "link":
        arxiv_ids: list[str] = []
        if args.arxiv_id:
            arxiv_ids.append(args.arxiv_id)
        if args.arxiv_ids:
            arxiv_ids.extend(aid.strip() for aid in args.arxiv_ids.split(","))
        if not arxiv_ids:
            print("Provide --arxiv-id or --arxiv-ids", file=sys.stderr)
            return 1
        for aid in arxiv_ids:
            result = link_paper(
                repo_id=args.repo_id,
                arxiv_id=aid,
                repo_type=args.repo_type,
                citation=args.citation,
            )
            print(json.dumps(result, indent=2))

    elif args.command == "claim":
        paper_url = f"https://huggingface.co/papers/{clean_arxiv_id(args.arxiv_id)}"
        print("To claim authorship:")
        print(f"  1. Visit {paper_url}")
        print("  2. Find your name in the author list")
        print("  3. Click 'Claim authorship'")
        print(f"  4. Verification email: {args.email}")

    elif args.command == "create":
        result = create_article(
            template=args.template,
            title=args.title,
            output=args.output,
            authors=args.authors,
            abstract=args.abstract,
        )
        print(json.dumps(result, indent=2))

    elif args.command == "info":
        result = get_arxiv_info(args.arxiv_id)
        print(json.dumps(result, indent=2))

    elif args.command == "citation":
        print(generate_bibtex(args.arxiv_id))

    elif args.command == "list-my-papers":
        print("Visit https://huggingface.co/settings/papers to manage your papers.")

    elif args.command == "toggle-visibility":
        aid = clean_arxiv_id(args.arxiv_id)
        show = args.show == "true"
        action = "shown on" if show else "hidden from"
        print(f"Paper {aid} will be {action} your profile.")
        print("Manage visibility at https://huggingface.co/settings/papers")

    return 0


if __name__ == "__main__":
    sys.exit(main())

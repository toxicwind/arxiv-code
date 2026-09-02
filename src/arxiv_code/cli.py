"""
CLI Entry Point for arxiv-code.
"""

import sys
import re
import json
import argparse
from rich.console import Console
from .client import ArxivClient
from .extractor import TexExtractor
from .miner import CodeMiner
from .tui import TUI

console = Console()

def main():
    parser = argparse.ArgumentParser(
        prog="arxiv-code",
        description="Sovereign Emergent arXiv 2026 Code & LaTeX Extraction Engine"
    )
    parser.add_argument("target", help="Search topic query (e.g. 'KV cache compression') or specific arXiv ID (e.g. '2608.31105')")
    parser.add_argument("-m", "--months", type=int, default=3, help="Recency search window in months (default: 3)")
    parser.add_argument("-n", "--limit", type=int, default=4, help="Max paper search results (default: 4)")
    parser.add_argument("-j", "--json", action="store_true", help="Output raw JSON data")
    parser.add_argument("--deep", action="store_true", help="Perform deep TeX mining across all search matches")

    args = parser.parse_args()
    target = args.target.strip()

    client = ArxivClient()
    extractor = TexExtractor()

    # Check if target is an explicit arXiv ID
    id_match = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", target)

    if id_match:
        arxiv_id = id_match.group(1)
        if not args.json:
            console.print(f"[bold cyan]⚡ Decompiling arXiv TeX Package for:[/] [bold green]{arxiv_id}[/]")
        
        extracted = extractor.extract(arxiv_id)
        if "error" in extracted:
            if args.json:
                print(json.dumps({"error": extracted["error"]}))
            else:
                console.print(f"[bold red]Error:[/] {extracted['error']}")
            sys.exit(1)

        links = CodeMiner.mine_links(extracted["tex_sources"])

        if args.json:
            output_data = {
                "id": arxiv_id,
                "tex_files": extracted["tex_files"],
                "links": links,
                "algorithms": extracted["algorithms"],
                "pseudocode": extracted["pseudocode"],
                "equations": extracted["equations"]
            }
            print(json.dumps(output_data, indent=2))
        else:
            console.print(f"\n[bold magenta]Found {len(extracted['tex_files'])} TeX sources in author package.[/]")
            TUI.render_links_table(links)
            TUI.render_algorithms(extracted["algorithms"])
            if not extracted["algorithms"] and extracted["pseudocode"]:
                console.print("\n[bold yellow]Extracted Python Functions / Definitions:[/]")
                for p in extracted["pseudocode"][:3]:
                    console.print(p["code"])
            TUI.render_equations(extracted["equations"])
    else:
        # Query Search Mode
        if not args.json:
            console.print(f"[bold cyan]🔍 Querying arXiv API (Past {args.months} Months) for:[/] [bold green]{target}[/]")

        papers = client.search(f"all:{target}", months=args.months, max_results=args.limit)

        if not papers:
            if args.json:
                print(json.dumps([]))
            else:
                console.print(f"[bold red]No preprints found within the past {args.months} months matching query.[/]")
            sys.exit(0)

        results = []
        for paper in papers:
            if not args.json:
                TUI.render_paper_card(paper)
            
            # Extract code from the paper
            extracted = extractor.extract(paper["id"])
            links = {}
            if "tex_sources" in extracted:
                links = CodeMiner.mine_links(extracted["tex_sources"])

            if not args.json:
                if links.get("github"):
                    for gh in links["github"]:
                        console.print(f"    [bold green]★ Discovered GitHub:[/] {gh}")
                if extracted.get("algorithms"):
                    console.print(f"    [bold yellow]★ {len(extracted['algorithms'])} algorithmic block(s) detected in TeX.[/]")
                console.print()

            results.append({
                "paper": paper,
                "links": links,
                "algorithms_count": len(extracted.get("algorithms", [])),
                "tex_files_count": len(extracted.get("tex_files", []))
            })

        if args.json:
            print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()

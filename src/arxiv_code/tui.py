"""
TUI — Rich formatting and display routines for papers, code blocks, and metrics.
"""

from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

console = Console()

class TUI:
    @staticmethod
    def render_paper_card(paper: Dict[str, Any]):
        table = Table.grid(padding=1)
        table.add_column("Key", style="bold cyan", width=14)
        table.add_column("Value", style="white")

        table.add_row("arXiv ID", f"[bold yellow]{paper['id']}[/] (Published: [green]{paper['published']}[/])")
        table.add_row("Authors", ", ".join(paper["authors"][:4]) + (" et al." if len(paper["authors"]) > 4 else ""))
        table.add_row("Categories", ", ".join(paper.get("categories", [])))
        table.add_row("Abstract", paper["summary"][:320] + "...")

        console.print(Panel(table, title=f"[bold green]{paper['title']}[/]", border_style="cyan"))

    @staticmethod
    def render_links_table(links: Dict[str, List[str]]):
        has_any = any(len(v) > 0 for v in links.values())
        if not has_any:
            return

        table = Table(title="[bold green]★ Discovered Repositories & Implementation Links[/]", border_style="green")
        table.add_column("Resource Type", style="cyan", width=20)
        table.add_column("Direct URL", style="white")

        for url in links.get("github", []):
            table.add_row("GitHub Repository", url)
        for url in links.get("huggingface", []):
            table.add_row("HuggingFace Space", url)
        for url in links.get("models_and_datasets", []):
            table.add_row("Model Weights / Data", url)
        for url in links.get("project_pages", []):
            table.add_row("Project Website", url)

        console.print(table)

    @staticmethod
    def render_algorithms(algorithms: List[Dict[str, Any]], limit: int = 5):
        if not algorithms:
            return

        console.print(f"\n[bold yellow]Extracted {len(algorithms)} Algorithm / Implementation Block(s):[/]")
        for i, alg in enumerate(algorithms[:limit], 1):
            env_type = alg["type"]
            lexer = "latex" if env_type in ["algorithm", "algorithmic"] else "python"
            syntax = Syntax(alg["code"][:1800], lexer, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Algorithm Block #{i} ({env_type} in {alg['file']})", border_style="cyan"))

    @staticmethod
    def render_equations(equations: List[Dict[str, Any]], limit: int = 3):
        if not equations:
            return

        console.print(f"\n[bold magenta]Key Formulation & Loss Equations:[/]")
        for i, eq in enumerate(equations[:limit], 1):
            syntax = Syntax(eq["latex"][:500], "latex", theme="monokai")
            console.print(Panel(syntax, title=f"Equation #{i} ({eq['file']})", border_style="magenta"))

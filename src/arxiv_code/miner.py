"""
CodeMiner — Extracts code repository, weights, and dataset URLs from LaTeX sources.
"""

import re
from typing import Dict, List, Set

class CodeMiner:
    @staticmethod
    def mine_links(tex_sources: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Scan LaTeX source files for GitHub, Hugging Face, Weights & Biases, and Kaggle links.
        """
        github_repos: Set[str] = set()
        huggingface_repos: Set[str] = set()
        model_weights: Set[str] = set()
        project_pages: Set[str] = set()

        for filename, text in tex_sources.items():
            # GitHub links (strip trailing latex commands or punctuation)
            gh_matches = re.findall(r"https?://github\.com/([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\.]+)", text)
            for gh in gh_matches:
                clean_gh = gh.rstrip(".,;)}% \t\n")
                if clean_gh and not clean_gh.endswith(".git") and "/" in clean_gh:
                    github_repos.add(f"https://github.com/{clean_gh}")

            # Hugging Face links
            hf_matches = re.findall(r"https?://huggingface\.co/([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\.]+)", text)
            for hf in hf_matches:
                clean_hf = hf.rstrip(".,;)}% \t\n")
                if clean_hf and "/" in clean_hf:
                    if "models" in clean_hf or "datasets" in clean_hf or "spaces" in clean_hf:
                        model_weights.add(f"https://huggingface.co/{clean_hf}")
                    else:
                        huggingface_repos.add(f"https://huggingface.co/{clean_hf}")

            # Project Pages / GitHub.io
            io_matches = re.findall(r"https?://[a-zA-Z0-9_\-]+\.github\.io/[a-zA-Z0-9_\-/]+", text)
            for page in io_matches:
                project_pages.add(page.rstrip(".,;)}% \t\n"))

        return {
            "github": sorted(list(github_repos)),
            "huggingface": sorted(list(huggingface_repos)),
            "models_and_datasets": sorted(list(model_weights)),
            "project_pages": sorted(list(project_pages))
        }

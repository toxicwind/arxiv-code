"""
TexExtractor — Decompiles arXiv e-print source packages and extracts algorithms/code.
"""

import io
import re
import tarfile
import urllib.request
from typing import Dict, List, Any, Optional

ARXIV_EPRINT_BASE = "https://arxiv.org/e-print"

class TexExtractor:
    def __init__(self, user_agent: str = "Sovereign-arXiv-Harvester/2026.1", timeout: int = 30):
        self.user_agent = user_agent
        self.timeout = timeout

    def extract(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Download and unpack author TeX source for a given arXiv ID.
        """
        clean_id = re.sub(r"v\d+$", "", arxiv_id.strip())
        eprint_url = f"{ARXIV_EPRINT_BASE}/{clean_id}"
        req = urllib.request.Request(eprint_url, headers={"User-Agent": self.user_agent})

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                content = resp.read()
        except Exception as e:
            return {"error": f"Failed to download source package: {e}", "id": clean_id}

        tex_sources = self._unpack_sources(content)
        
        algorithms = []
        pseudocode = []
        equations = []

        for filename, source in tex_sources.items():
            # 1. LaTeX Algorithm Environments
            algo_matches = re.findall(
                r"\\begin\{(algorithm|algorithmic|lstlisting|minted|verbatim|python|code)\}(.*?)\\end\{\1\}",
                source,
                re.DOTALL
            )
            for env_type, block in algo_matches:
                cleaned = block.strip()
                if len(cleaned) > 30:
                    algorithms.append({
                        "type": env_type,
                        "file": filename,
                        "code": cleaned
                    })

            # 2. Python Def Blocks in comments or text
            py_matches = re.findall(r"(def\s+[a-zA-Z0-9_]+\s*\(.*?\):.*?(?=\n\n|\Z))", source, re.DOTALL)
            for pyd in py_matches:
                cleaned_py = pyd.strip()
                if len(cleaned_py) > 30:
                    pseudocode.append({
                        "file": filename,
                        "code": cleaned_py
                    })

            # 3. Key Loss / Metric Equations
            eq_matches = re.findall(r"\\begin\{(equation|align|gather)\*?\}(.*?)\\end\{\1\*?\}", source, re.DOTALL)
            for eq_type, eq_body in eq_matches:
                if any(kw in eq_body for kw in ["\\mathcal{L}", "loss", "arg\\,min", "arg\\,max", "\\mathrm{CrossEntropy}", "\\mathbb{E}"]):
                    equations.append({
                        "type": eq_type,
                        "file": filename,
                        "latex": eq_body.strip()
                    })

        return {
            "id": clean_id,
            "tex_sources": tex_sources,
            "tex_files": list(tex_sources.keys()),
            "algorithms": algorithms,
            "pseudocode": pseudocode,
            "equations": equations
        }

    def _unpack_sources(self, raw_bytes: bytes) -> Dict[str, str]:
        sources: Dict[str, str] = {}
        valid_exts = (".tex", ".sty", ".py", ".cu", ".triton", ".cpp", ".h", ".cuh", ".sh", ".json", ".yaml")

        try:
            tar = tarfile.open(fileobj=io.BytesIO(raw_bytes))
            for member in tar.getmembers():
                if any(member.name.endswith(ext) for ext in valid_exts):
                    f = tar.extractfile(member)
                    if f:
                        try:
                            sources[member.name] = f.read().decode("utf-8", errors="ignore")
                        except Exception:
                            pass
        except tarfile.ReadError:
            try:
                import gzip
                decomp = gzip.decompress(raw_bytes)
                sources["main.tex"] = decomp.decode("utf-8", errors="ignore")
            except Exception:
                sources["main.tex"] = raw_bytes.decode("utf-8", errors="ignore")

        return sources

"""
ArxivClient — Direct REST API query interface with recency filtering.
"""

import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

ARXIV_API_BASE = "http://export.arxiv.org/api/query"

class ArxivClient:
    def __init__(self, user_agent: str = "Sovereign-arXiv-Harvester/2026.1", timeout: int = 15):
        self.user_agent = user_agent
        self.timeout = timeout

    def search(
        self,
        query: str,
        months: Optional[int] = 3,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        max_results: int = 5,
        start: int = 0,
        sort_by: str = "submittedDate",
        sort_order: str = "descending"
    ) -> List[Dict[str, Any]]:
        """
        Execute search against arXiv API with date window constraints.
        """
        now = datetime.datetime.now()
        
        if months is not None and not start_date:
            start_date = (now - datetime.timedelta(days=months * 30)).date()
            end_date = now.date()

        date_clause = ""
        if start_date and end_date:
            date_clause = f"submittedDate:[{start_date.strftime('%Y%m%d')}0000 TO {end_date.strftime('%Y%m%d')}2359]"
        elif start_date:
            date_clause = f"submittedDate:[{start_date.strftime('%Y%m%d')}0000 TO {now.strftime('%Y%m%d')}2359]"

        if query and date_clause:
            full_query = f"({query}) AND {date_clause}"
        elif query:
            full_query = query
        else:
            full_query = date_clause or "all:ai"

        params = {
            "search_query": full_query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }

        url = f"{ARXIV_API_BASE}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            xml_data = resp.read()

        return self._parse_atom_feed(xml_data)

    def _parse_atom_feed(self, xml_bytes: bytes) -> List[Dict[str, Any]]:
        root = ET.fromstring(xml_bytes)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom"
        }

        entries = []
        for entry in root.findall("atom:entry", ns):
            arxiv_id_full = entry.find("atom:id", ns).text.strip()
            arxiv_id = arxiv_id_full.split("/abs/")[-1]
            title = " ".join(entry.find("atom:title", ns).text.strip().split())
            summary = " ".join(entry.find("atom:summary", ns).text.strip().split())
            published = entry.find("atom:published", ns).text.strip()[:10]
            updated = entry.find("atom:updated", ns).text.strip()[:10]
            authors = [a.find("atom:name", ns).text.strip() for a in entry.findall("atom:author", ns)]
            
            categories = [c.attrib.get("term") for c in entry.findall("atom:category", ns) if "term" in c.attrib]
            
            # Find PDF and source links
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href", "")

            entries.append({
                "id": arxiv_id,
                "title": title,
                "summary": summary,
                "published": published,
                "updated": updated,
                "authors": authors,
                "categories": categories,
                "pdf_url": pdf_url,
                "abs_url": arxiv_id_full
            })

        return entries

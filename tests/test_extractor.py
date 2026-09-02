import unittest
from arxiv_code.miner import CodeMiner
from arxiv_code.extractor import TexExtractor

class TestExtractor(unittest.TestCase):
    def test_code_miner(self):
        mock_tex = {
            "main.tex": r"""
            \section{Introduction}
            Our code is available at \url{https://github.com/toxicwind/sovereign}.
            Pretrained models can be downloaded from \url{https://huggingface.co/toxicwind/heretic-27b}.
            Visit the project page at \url{https://toxicwind.github.io/arxiv-code/}.
            """
        }
        
        links = CodeMiner.mine_links(mock_tex)
        self.assertIn("https://github.com/toxicwind/sovereign", links["github"])
        self.assertIn("https://huggingface.co/toxicwind/heretic-27b", links["huggingface"])
        self.assertIn("https://toxicwind.github.io/arxiv-code/", links["project_pages"])

    def test_unpack_single_source(self):
        extractor = TexExtractor()
        raw = b"\\begin{algorithm}\nstep 1\n\\end{algorithm}"
        res = extractor._unpack_sources(raw)
        self.assertIn("main.tex", res)
        self.assertIn("algorithm", res["main.tex"])

if __name__ == "__main__":
    unittest.main()

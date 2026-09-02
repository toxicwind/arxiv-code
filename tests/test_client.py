import unittest
from arxiv_code.client import ArxivClient

SAMPLE_ATOM_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2608.12345v1</id>
    <published>2026-08-30T10:00:00Z</published>
    <updated>2026-08-30T10:00:00Z</updated>
    <title>Emergent Speculative Decoding at Scale</title>
    <summary>We introduce a novel KV compression technique.</summary>
    <author><name>Alice Dev</name></author>
    <author><name>Bob Research</name></author>
    <category term="cs.AI"/>
    <link title="pdf" href="http://arxiv.org/pdf/2608.12345v1"/>
  </entry>
</feed>
"""

class TestClient(unittest.TestCase):
    def test_parse_atom_feed(self):
        client = ArxivClient()
        parsed = client._parse_atom_feed(SAMPLE_ATOM_FEED)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], "2608.12345v1")
        self.assertEqual(parsed[0]["title"], "Emergent Speculative Decoding at Scale")
        self.assertIn("Alice Dev", parsed[0]["authors"])
        self.assertIn("cs.AI", parsed[0]["categories"])

if __name__ == "__main__":
    unittest.main()

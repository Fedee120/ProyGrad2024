import unittest
from agent.llms.rag_response_generator import ContextItem, extract_year_from_creation_date

class TestAPACitations(unittest.TestCase):
    def test_extract_year_from_creation_date(self):
        """Test the function that extracts year from creation date string"""
        self.assertEqual(extract_year_from_creation_date("D:20240607114253+02'00'"), "2024")
        self.assertEqual(extract_year_from_creation_date("D:20220101000000"), "2022")
        self.assertEqual(extract_year_from_creation_date(""), None)
        self.assertEqual(extract_year_from_creation_date(None), None)
        self.assertEqual(extract_year_from_creation_date("Invalid format"), None)

    def test_apa_citation_formatting(self):
        """Test the APA citation formatting with various input combinations"""
        # Complete citation
        item = ContextItem(
            content="This is content",
            source="document.pdf",
            title="Research on AI",
            author="Smith, J.",
            year="2023"
        )
        self.assertEqual(item.format_apa_citation(), "Smith, J. (2023). Research on AI.")
        
        # Missing year
        item = ContextItem(
            content="This is content",
            source="document.pdf",
            title="Research on AI",
            author="Smith, J.",
            year=None
        )
        self.assertEqual(item.format_apa_citation(), "Smith, J. (s.f.). Research on AI.")
        
        # Missing author
        item = ContextItem(
            content="This is content",
            source="document.pdf",
            title="Research on AI",
            author=None,
            year="2023"
        )
        self.assertEqual(item.format_apa_citation(), "Autor desconocido (2023). Research on AI.")
        
        # Missing title
        item = ContextItem(
            content="This is content",
            source="document.pdf",
            title=None,
            author="Smith, J.",
            year="2023"
        )
        self.assertEqual(item.format_apa_citation(), "Smith, J. (2023). document.pdf.")
        
        # Missing multiple fields
        item = ContextItem(
            content="This is content",
            source="document.pdf",
            title=None,
            author=None,
            year=None
        )
        self.assertEqual(item.format_apa_citation(), "Autor desconocido (s.f.). document.pdf.")

if __name__ == "__main__":
    unittest.main() 
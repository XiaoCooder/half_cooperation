from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "style.css").read_text(encoding="utf-8")


class HomepageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.classes = []
        self.links = []
        self.images = []
        self.text_chunks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if "class" in attrs:
            self.classes.extend(attrs["class"].split())
        if tag == "a":
            self.links.append(attrs)
        if tag == "img":
            self.images.append(attrs)

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_chunks.append(text)


class StaticHomepageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = HomepageParser()
        cls.parser.feed(HTML)
        cls.text = "\n".join(cls.parser.text_chunks)

    def test_required_profile_and_content_sections_exist(self):
        for required_class in [
            "profile-panel",
            "social-links",
            "content-panel",
            "updates-list",
            "projects-grid",
            "site-footer",
        ]:
            self.assertIn(required_class, self.parser.classes)

    def test_recent_updates_and_featured_projects_have_expected_counts(self):
        self.assertEqual(HTML.count('class="update-card"'), 4)
        self.assertEqual(HTML.count('class="project-card"'), 2)

    def test_avatar_and_social_links_are_present(self):
        self.assertTrue(self.parser.images)
        avatar = self.parser.images[0]
        self.assertIn("src", avatar)
        self.assertIn("alt", avatar)
        self.assertGreaterEqual(len(self.parser.links), 3)
        hrefs = [link.get("href", "") for link in self.parser.links]
        self.assertTrue(any("github.com" in href for href in hrefs))
        self.assertTrue(any("zhihu.com" in href for href in hrefs))
        self.assertTrue(any(href.startswith("mailto:") for href in hrefs))

    def test_responsive_and_hover_styles_are_defined(self):
        self.assertIn("@media (max-width: 760px)", CSS)
        self.assertIn(":hover", CSS)
        self.assertIn("translateY", CSS)
        self.assertIn("grid-template-columns: 1fr;", CSS)


if __name__ == "__main__":
    unittest.main()

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "style.css").read_text(encoding="utf-8")


class HomepageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.ids = set()
        self.links = []
        self.article_count = 0
        self.current_article = None
        self.articles = []
        self.classes = set()
        self.text_chunks = []

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        classes = attr_map.get("class", "").split()
        self.classes.update(classes)
        if "id" in attr_map:
            self.ids.add(attr_map["id"])
        if tag == "a":
            self.links.append(attr_map.get("href", ""))
        if tag == "article" and "article-card" in classes:
            self.article_count += 1
            self.current_article = {"headings": 0, "paragraphs": 0, "read_time": False}
        if self.current_article is not None:
            if tag == "h3":
                self.current_article["headings"] += 1
            if tag == "p":
                self.current_article["paragraphs"] += 1
            if tag == "span" and "read-time" in classes:
                self.current_article["read_time"] = True
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "article" and self.current_article is not None:
            self.articles.append(self.current_article)
            self.current_article = None
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        stripped = data.strip()
        if stripped:
            self.text_chunks.append(stripped)


class HomepageImplementationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = HomepageParser()
        cls.parser.feed(HTML)
        cls.visible_text = "\n".join(cls.parser.text_chunks)

    def test_required_landmarks_and_sections_exist(self):
        for class_name in ["site-header", "hero-section", "article-section", "site-footer"]:
            self.assertIn(class_name, self.parser.classes)
        for section_id in ["home", "articles", "about", "projects"]:
            self.assertIn(section_id, self.parser.ids)

    def test_navigation_links_target_existing_sections(self):
        anchor_links = [href for href in self.parser.links if href.startswith("#") and href != "#"]
        for href in ["#home", "#about", "#projects", "#articles"]:
            self.assertIn(href, anchor_links)
        for href in anchor_links:
            self.assertIn(href[1:], self.parser.ids)

    def test_hero_content_matches_t1_direction(self):
        self.assertIn("智能无限，创作无间", self.visible_text)
        self.assertIn("Frontend Developer · AI Explorer", self.visible_text)
        self.assertIn("前端开发者 / AI 探索者", self.visible_text)
        self.assertNotIn("<img", HTML.lower())

    def test_article_cards_have_required_fields(self):
        self.assertGreaterEqual(self.parser.article_count, 3)
        self.assertLessEqual(self.parser.article_count, 5)
        for article in self.parser.articles:
            self.assertEqual(article["headings"], 1)
            self.assertGreaterEqual(article["paragraphs"], 1)
            self.assertTrue(article["read_time"])

    def test_css_supports_minimal_responsive_interactions(self):
        self.assertRegex(CSS, r"\.site-header\s*\{[^}]*backdrop-filter:\s*blur")
        self.assertRegex(CSS, r"\.article-card:hover\s*\{[^}]*translateY\(-2px\)")
        self.assertIn("@media (max-width: 760px)", CSS)
        self.assertRegex(CSS, r"grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)")
        self.assertRegex(CSS, r"grid-template-columns:\s*1fr")
        self.assertRegex(CSS, r"font-size:\s*clamp\(")


if __name__ == "__main__":
    unittest.main()

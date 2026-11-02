import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from build import render


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags, self.text, self.links = [], [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == "a":
            self.links.append(dict(attrs).get("href"))

    def handle_data(self, data):
        self.text.append(data)


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.article = json.loads(Path("content/article.json").read_text())

    def test_public_article_preserves_voice_and_structure(self):
        doc = Document(render(self.article))
        for paragraph in self.article["paragraphs"]:
            self.assertIn(paragraph, doc.text)
        self.assertIn(("main", {"id": "main"}), doc.tags)
        self.assertEqual(sum(tag == "h1" for tag, _ in doc.tags), 1)
        self.assertIn("#main", doc.links)
        self.assertFalse(any(tag == "script" for tag, _ in doc.tags))

    def test_draft_not_published(self):
        self.assertIsNone(render({**self.article, "published": False}))

    def test_markup_in_prose_is_text(self):
        content = '<script>alert("synthetic")</script>'
        doc = Document(render({**self.article, "paragraphs": [content]}))
        self.assertIn(content, doc.text)
        self.assertFalse(any(tag == "script" for tag, _ in doc.tags))

"""Synthetic static publishing fixture; returns output without publishing it."""
from html import escape


def render(article):
    if not article["published"]:
        return None
    title = escape(article["title"])
    paragraphs = "".join(f"<p>{escape(text)}</p>" for text in article["paragraphs"])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="site.css"></head><body>
<a href="#main">Skip to content</a><nav aria-label="Main"><a href="/">Home</a></nav>
<main id="main"><article><h1>{title}</h1>{paragraphs}</article></main></body></html>'''

import os
from bs4 import BeautifulSoup


def test_frontend_has_mecha_elements():
    index_path = os.path.join(os.path.dirname(__file__), "..", "docs", "index.html")
    assert os.path.exists(index_path), "Frontend index.html is missing"

    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # Check for mecha style classes
    assert soup.find(class_="scanlines") is not None
    assert soup.find(class_="mecha-nav") is not None
    assert soup.find(class_="mecha-panel") is not None

    # Check for internationalization support
    i18n_elements = soup.find_all(attrs={"data-i18n": True})
    assert len(i18n_elements) > 0, "No i18n data attributes found"

    # Check for theme toggle
    assert soup.find(id="themeToggle") is not None

    # Check for download links
    download_links = soup.find(class_="download-links")
    assert download_links is not None
    links = download_links.find_all("a")
    assert len(links) >= 3, "Missing OS download links"


def test_frontend_has_translations():
    index_path = os.path.join(os.path.dirname(__file__), "..", "docs", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Super simple text check for the JS dictionary
    assert "const i18n =" in html_content
    assert "ja:" in html_content
    assert "es:" in html_content
    assert "de:" in html_content

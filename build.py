#!/usr/bin/env python3
"""Assemble static pages from src/*.body.html plus the shared head and footer.

Each body file starts with a small header block of key: value lines, then a
blank line, then the page's <main> content. Run: python3 build.py
"""
import hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
SITE = "https://ovdcapital.com/"

# Stylesheet fingerprint, so a changed stylesheet is never served from cache.
CSS_VER = hashlib.sha1((ROOT / "css" / "site.css").read_bytes()).hexdigest()[:8]
HEAD = (ROOT / "_head.part").read_text()
FOOT = (ROOT / "_foot.part").read_text()

NAV = {
    "approach": "__A_APPROACH__", "where-we-focus": "__A_FOCUS__",
    "founders": "__A_FOUNDERS__", "investments": "__A_INVESTMENTS__",
    "who-we-are": "__A_WHO__", "advisory": "__A_ADVISORY__",
    "contact": "__A_CONTACT__",
}

def build(src: pathlib.Path) -> tuple[str, dict]:
    raw = src.read_text()
    meta_block, _, body = raw.partition("\n\n")
    meta = dict(
        (k.strip(), v.strip())
        for k, _, v in (l.partition(":") for l in meta_block.splitlines() if l.strip())
    )
    slug = src.name.replace(".body.html", "")
    depth = slug.count("/")
    root = "../" * depth or ""

    url = SITE + ("" if slug == "index" else f"{slug}.html")
    page = HEAD.replace("__TITLE__", meta["title"]).replace("__DESC__", meta["desc"])
    page = page.replace("__URL__", url)
    page = page.replace("__CSS__", root).replace("__ROOT__", root)
    page = page.replace("css/site.css\"", f"css/site.css?v={CSS_VER}\"")
    for key, token in NAV.items():
        page = page.replace(token, 'class="here"' if key == slug else "")
    page = re.sub(r"<a\s+href=", "<a href=", page)

    out = page + body.rstrip() + "\n\n" + FOOT.replace("__ROOT__", root)
    return out, meta

# Page order for sitemap and llms.txt: home first, then the nav order.
ORDER = ["index", "approach", "where-we-focus", "founders",
         "investments", "who-we-are", "advisory", "contact"]


def page_url(slug: str) -> str:
    return SITE + ("" if slug == "index" else f"{slug}.html")


def write_sitemap(pages: dict) -> None:
    rows = "\n".join(
        f"  <url><loc>{page_url(s)}</loc></url>"
        for s in sorted(pages, key=lambda s: ORDER.index(s) if s in ORDER else 99)
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{rows}\n</urlset>\n"
    )


def write_llms(pages: dict) -> None:
    """A plain-language index for language models that fetch the site."""
    lines = [
        "# OVD Capital",
        "",
        "> An operator-led investment firm in Chicago, Illinois. OVD Capital partners "
        "with founders and management teams of established, profitable businesses, "
        "bringing operating experience, flexible capital and the practical application "
        "of technology, including AI. Through OVD Advisory it delivers AI opportunity "
        "assessments and implementation to established businesses, private equity firms "
        "and family offices.",
        "",
        "Principals: Alan Warms, Jamie Crouthamel, Gary Leff.",
        "Contact: contact@ovdcapital.com",
        "",
        "## Pages",
        "",
    ]
    for s in sorted(pages, key=lambda s: ORDER.index(s) if s in ORDER else 99):
        lines.append(f"- [{pages[s]['title']}]({page_url(s)}): {pages[s]['desc']}")
    (ROOT / "llms.txt").write_text("\n".join(lines) + "\n")


def main():
    built, pages = [], {}
    for src in sorted((ROOT / "src").glob("*.body.html")):
        slug = src.name.replace(".body.html", "")
        dest = ROOT / f"{slug}.html"
        html, meta = build(src)
        dest.write_text(html)
        pages[slug] = meta
        built.append(dest.name)
    write_sitemap(pages)
    write_llms(pages)
    print("built:", ", ".join(built))
    print("also wrote: sitemap.xml, llms.txt")

if __name__ == "__main__":
    main()

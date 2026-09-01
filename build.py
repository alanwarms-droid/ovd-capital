#!/usr/bin/env python3
"""Assemble static pages from src/*.body.html plus the shared head and footer.

Each body file starts with a small header block of key: value lines, then a
blank line, then the page's <main> content. Run: python3 build.py
"""
import hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent

# Stylesheet fingerprint, so a changed stylesheet is never served from cache.
CSS_VER = hashlib.sha1((ROOT / "css" / "site.css").read_bytes()).hexdigest()[:8]
HEAD = (ROOT / "_head.part").read_text()
FOOT = (ROOT / "_foot.part").read_text()

NAV = {
    "approach": "__A_APPROACH__", "where-we-focus": "__A_FOCUS__",
    "founders": "__A_FOUNDERS__", "investments": "__A_INVESTMENTS__",
    "who-we-are": "__A_WHO__", "contact": "__A_CONTACT__",
}

def build(src: pathlib.Path) -> str:
    raw = src.read_text()
    meta_block, _, body = raw.partition("\n\n")
    meta = dict(
        (k.strip(), v.strip())
        for k, _, v in (l.partition(":") for l in meta_block.splitlines() if l.strip())
    )
    slug = src.name.replace(".body.html", "")
    depth = slug.count("/")
    root = "../" * depth or ""

    page = HEAD.replace("__TITLE__", meta["title"]).replace("__DESC__", meta["desc"])
    page = page.replace("__CSS__", root).replace("__ROOT__", root)
    page = page.replace("css/site.css\"", f"css/site.css?v={CSS_VER}\"")
    for key, token in NAV.items():
        page = page.replace(token, 'class="here"' if key == slug else "")
    page = re.sub(r"<a\s+href=", "<a href=", page)

    out = page + body.rstrip() + "\n\n" + FOOT.replace("__ROOT__", root)
    return out

def main():
    built = []
    for src in sorted((ROOT / "src").glob("*.body.html")):
        slug = src.name.replace(".body.html", "")
        dest = ROOT / f"{slug}.html"
        dest.write_text(build(src))
        built.append(dest.name)
    print("built:", ", ".join(built))

if __name__ == "__main__":
    main()

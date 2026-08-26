# OVD Capital — website

Static site. No framework, no build dependencies beyond Python 3.
Same structure as the OVD Advisory site so both are edited the same way.

## Editing

Page content lives in `src/*.body.html`. Each file starts with a `title:` and
`desc:` line, a blank line, then the page's `<main>` content.

Shared masthead and footer live in `_head.part` and `_foot.part`, so the
navigation is defined once.

After editing, rebuild:

    python3 build.py

Commit the generated `*.html` files too — GitHub Pages serves them directly.

## Local preview

    python3 -m http.server 4323

Then open http://localhost:4323

## Relationship to OVD Advisory

The two sites cross-link from their navigation bars and share one stylesheet.
When `css/site.css` changes in either repo, copy it to the other so the design
stays identical:

    cp ../ovd-site/css/site.css css/site.css && python3 build.py

## Before launch

- Remove the `noindex` meta tag from `_head.part` and rebuild.
- Point ovdcapital.com at GitHub Pages and add a `CNAME` file. Email rides on
  MX records and is unaffected by where the site is hosted.
- Confirm contact@ovdcapital.com is live.

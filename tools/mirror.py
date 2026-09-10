#!/usr/bin/env python3
"""Mirror the published Webflow portfolio into a self-contained static site."""

import os
import re
import sys
import urllib.request
import urllib.parse
from collections import OrderedDict

SRC = "https://www.irinacsapo.co.uk"
OUT = sys.argv[1] if len(sys.argv) > 1 else "site"

PAGES = [
    "/",
    "/about",
    "/contact",
    "/case-studies/omaze-mm-case-study",
    "/case-studies/e-on-buzz-case-study",
    "/case-studies/weglow",
    "/case-studies/paycada-case-study",
    "/case-studies/snapit-case-study",
    "/case-studies/argc-case-study",
    "/case-studies/strands-case-study",
    "/case-studies/aidaptus-case-study",
    "/case-studies/veva-case-study",
    "/product-design/strands-showcase",
    "/product-design/aidaptus-showcase",
    "/product-design/veva-showcase",
    "/webflow-projects",
    "/ai-applications",
    "/photography",
    "/photography/portraits",
    "/photography/headshots",
    "/photography/meanwhile-in-iran",
    # Older /portfolio/* pages. Not part of the current portfolio, but each one
    # is still published and still linked from a page above, so they are kept
    # to avoid introducing broken links. Safe to delete as a group.
    "/portfolio/astronauts",
    "/portfolio/e-on",
    "/portfolio/email-notifications",
    "/portfolio/fever-crush",
    "/portfolio/gridfabric",
    "/portfolio/spree-app",
    "/portfolio/travel-animation",
    "/404",
]

# Hosts whose assets we pull down and serve ourselves.
ASSET_HOSTS = (
    "cdn.prod.website-files.com",
    "uploads-ssl.webflow.com",
    "assets-global.website-files.com",
    "d3e54v103j8qbb.cloudfront.net",
)

# Internal page hosts that should be rewritten to local relative links.
SITE_HOSTS = ("www.irinacsapo.co.uk", "irinacsapo.co.uk", "irina-csapo.webflow.io")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

asset_map = OrderedDict()  # remote url -> site-root-relative local path
fetch_cache = {}


CACHE = ".httpcache"


def get(url, binary=False):
    if url in fetch_cache:
        return fetch_cache[url]
    import hashlib

    os.makedirs(CACHE, exist_ok=True)
    key = os.path.join(CACHE, hashlib.sha256(url.encode()).hexdigest())
    if os.path.exists(key) and os.path.getsize(key) > 0:
        with open(key, "rb") as f:
            data = f.read()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(key, "wb") as f:
            f.write(data)
    if not binary:
        data = data.decode("utf-8", "replace")
    fetch_cache[url] = data
    return data


def _slug(name):
    """Make a filename safe to serve from a plain static host."""
    base, ext = os.path.splitext(name)
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-.")
    return (base or "asset") + ext.lower()


def local_for(url):
    """Decide where a remote asset lives inside the repo."""
    if url in asset_map:
        return asset_map[url]
    p = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(p.path)
    host = p.netloc

    if host == "d3e54v103j8qbb.cloudfront.net":
        local = "assets/js/jquery.min.js"
    else:
        # Strip the Webflow site-id segment: /5e960886.../css/foo.css -> css/foo.css
        seg = [s for s in path.split("/") if s]
        if seg and re.fullmatch(r"[0-9a-f]{24}", seg[0]):
            seg = seg[1:]
        if not seg:
            seg = ["asset"]
        if seg[0] in ("css", "js"):
            local = "assets/" + "/".join(seg)
        elif seg[0] == "gsap":
            local = "assets/js/gsap/" + seg[-1]
        else:
            ext = os.path.splitext(seg[-1])[1].lower()
            if ext in (".woff", ".woff2", ".ttf", ".otf", ".eot"):
                bucket = "fonts"
            elif ext in (".mp4", ".webm", ".mov", ".m4v"):
                bucket = "media"
            elif ext in (".pdf", ".doc", ".docx"):
                bucket = "docs"
            elif ext in (".css",):
                bucket = "css"
            elif ext in (".js",):
                bucket = "js"
            else:
                bucket = "images"
            local = "assets/%s/%s" % (bucket, _slug(seg[-1]))

    # Avoid collisions between different URLs landing on the same filename.
    taken = set(asset_map.values())
    if local in taken:
        base, ext = os.path.splitext(local)
        n = 2
        while "%s-%d%s" % (base, n, ext) in taken:
            n += 1
        local = "%s-%d%s" % (base, n, ext)

    asset_map[url] = local
    return local


# Webflow filenames legitimately contain parentheses and encoded spaces, so
# parens are allowed here and balanced separately below.
ASSET_RE = re.compile(
    r"https://(?:%s)/[^\s\"'<>\\]+" % "|".join(h.replace(".", r"\.") for h in ASSET_HOSTS)
)

# Trailing junk that regularly rides along in HTML attributes and inline JS.
TRAILING = ("&quot;", "&quot", "&#39;", "&#x27;", "&amp;", '"', "'", "\\")


def _clean(u):
    changed = True
    while changed:
        changed = False
        for t in TRAILING:
            if u.endswith(t):
                u = u[: -len(t)]
                changed = True
        if u and u[-1] in ".,;":
            u, changed = u[:-1], True
        # Drop a closing paren only when it has no opener - i.e. it came from url(...).
        while u.endswith(")") and u.count(")") > u.count("("):
            u, changed = u[:-1], True
    return u


def find_assets(text):
    out = []
    for m in ASSET_RE.finditer(text):
        # data-video-urls packs several URLs into one comma-separated attribute.
        for part in m.group(0).split(","):
            part = _clean(part.strip())
            if part.startswith("https://"):
                out.append(part)
    return out


def relpath(root_rel, depth):
    return ("../" * depth) + root_rel if depth else root_rel


def page_target(path):
    """Published path -> (file path in repo, depth)."""
    if path == "/":
        return "index.html", 0
    if path == "/404":
        # GitHub Pages serves /404.html from the repo root for any missing URL.
        return "404.html", 0
    seg = [s for s in path.split("/") if s]
    return "/".join(seg) + "/index.html", len(seg)


def write(path, data):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(full, mode) as f:
        f.write(data)


# ---------------------------------------------------------------- fetch pages
print("Fetching %d pages..." % len(PAGES))
raw = {}
for p in PAGES:
    url = SRC + ("" if p == "/" else p)
    try:
        raw[p] = get(url)
        print("  ok   %s (%d KB)" % (p, len(raw[p]) // 1024))
    except Exception as e:
        print("  FAIL %s -> %s" % (p, e))

# --------------------------------------------------------------- collect css/js
pending = []
for html in raw.values():
    pending += find_assets(html)

seen = set()
queue = []
for u in pending:
    if u not in seen:
        seen.add(u)
        queue.append(u)

# Recursively pull assets referenced from inside CSS files.
css_bodies = {}
i = 0
while i < len(queue):
    u = queue[i]
    i += 1
    if not u.split("?")[0].endswith(".css"):
        continue
    try:
        body = get(u)
    except Exception as e:
        print("  css FAIL %s -> %s" % (u, e))
        continue
    css_bodies[u] = body
    for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", body):
        ref = m.group(1).strip()
        if ref.startswith("data:"):
            continue
        abs_u = urllib.parse.urljoin(u, ref)
        if any(h in abs_u for h in ASSET_HOSTS) and abs_u not in seen:
            seen.add(abs_u)
            queue.append(abs_u)

print("\nDownloading %d assets..." % len(queue))
ok = fail = 0
for u in queue:
    local = local_for(u)
    try:
        if u in css_bodies:
            body = css_bodies[u]
            # Rewrite url() refs inside the stylesheet to sit next to it.
            css_dir = os.path.dirname(local)

            def fix(m, _dir=css_dir, _base=u):
                ref = m.group(1).strip()
                if ref.startswith("data:"):
                    return m.group(0)
                abs_u = urllib.parse.urljoin(_base, ref)
                if not any(h in abs_u for h in ASSET_HOSTS):
                    return m.group(0)
                target = local_for(abs_u)
                return "url(%s)" % os.path.relpath(target, _dir)

            body = re.sub(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", fix, body)
            write(local, body)
        else:
            write(local, get(u, binary=True))
        ok += 1
    except Exception as e:
        fail += 1
        print("  FAIL %s -> %s" % (u, e))
print("  %d ok, %d failed" % (ok, fail))

# ------------------------------------------------------------- rewrite pages
# Longest-first so /case-studies/x is replaced before /case-studies.
page_paths = sorted([p for p in raw if p != "/"], key=len, reverse=True)

print("\nRewriting pages...")
for p, html in raw.items():
    target, depth = page_target(p)

    # 1. Drop Webflow's <base> tag - it would send every relative link back to Webflow.
    html = re.sub(r"<base\b[^>]*>", "", html, flags=re.I)

    # 2. Point every asset at our local copy.
    for u in sorted(seen, key=len, reverse=True):
        if u in asset_map:
            html = html.replace(u, relpath(asset_map[u], depth))

    # 3. Internal links -> relative.
    for host in SITE_HOSTS:
        for scheme in ("https://", "http://"):
            base = scheme + host
            for op in page_paths:
                html = html.replace(base + op, relpath(op.lstrip("/") + "/", depth))
            html = html.replace(base + "/", relpath("", depth) or "./")
            html = html.replace(base, relpath("", depth) or "./")

    # Root-relative hrefs written by Webflow, e.g. href="/about" or
    # href="/webflow-projects#intro". Everything must become relative, because
    # on GitHub Pages the site may be served from a sub-path.
    def fix_href(m):
        attr, quote, url = m.group(1), m.group(2), m.group(3)
        # Split off #fragment / ?query so they survive the rewrite untouched.
        mm = re.match(r"([^#?]*)([#?].*)?$", url)
        path, tail = mm.group(1), mm.group(2) or ""
        if path == "/":
            new = relpath("", depth) or "./"
        elif path.rstrip("/") in [p.rstrip("/") for p in page_paths]:
            key = next(p for p in page_paths if p.rstrip("/") == path.rstrip("/"))
            new = relpath(key.lstrip("/") + "/", depth)
        else:
            # Unknown page (e.g. a Webflow draft that was never published).
            # Keep it relative anyway so it lands on our own 404 rather than
            # escaping to the domain root.
            new = relpath(path.lstrip("/"), depth)
        return "%s=%s%s%s%s" % (attr, quote, new, tail, quote)

    # The (?!/) guard keeps protocol-relative //host URLs out of this.
    html = re.sub(r"\b(href|action)=([\"'])(/(?!/)[^\"']*)\2", fix_href, html)

    # 4. Localised stylesheets don't need SRI/CORS attributes.
    html = re.sub(r'\s+integrity="[^"]*"', "", html)
    html = re.sub(r'\s+crossorigin="anonymous"(?=[^>]*\brel="stylesheet")', "", html)

    # 5a. Webflow proxied Google Analytics through an obfuscated first-party
    #     path that only resolves on Webflow's own infrastructure, so it 404s
    #     everywhere else. Remove it rather than ship a broken request.
    #     The path is <random>/<base64 of the site id>/<token>, and the prefix
    #     differs per page, so anchor the match on the encoded site id.
    site_b64 = "NWU5NjA4ODZiM2E4ZTM3YTY1ODYyNDBi"  # base64("5e960886b3a8e37a6586240b")
    html = re.sub(
        r'<script[^>]*\bsrc="/[A-Za-z0-9]*%s/[^"]*"[^>]*>\s*</script>' % site_b64,
        "",
        html,
        flags=re.I,
    )
    # 5b. Dead rule: nothing ever adds .anti-flicker now that Optimize is gone,
    #     but leaving it invites a future edit that hides the whole page.
    html = html.replace(
        "<style>.anti-flicker, .anti-flicker * "
        "{visibility: hidden !important; opacity: 0 !important;}</style>",
        "",
    )

    # 5. Drop the now-pointless preconnect hint to Webflow's CDN.
    html = re.sub(
        r'<link[^>]*href="https://cdn\.prod\.website-files\.com"[^>]*>', "", html, flags=re.I
    )

    # 6. The form used to post to Webflow. Keep it pixel-identical but inert,
    #    and drop the Turnstile widget, which only works on Webflow's domain.
    if "<form" in html:
        html = re.sub(r'\s+data-turnstile-sitekey="[^"]*"', "", html)
        html = html.replace(
            "<form ",
            "<!-- TODO: form submission is disabled. To re-enable, sign up with a form\n"
            '     backend (e.g. Formspree) and set action="https://formspree.io/f/XXXX"\n'
            '     method="POST", then remove the onsubmit handler below. -->\n'
            '<form onsubmit="return false;" ',
            1,
        )

    write(target, html)
    print("  %-46s -> %s" % (p, target))

# Stop GitHub Pages running the files through Jekyll, which would silently
# drop any path beginning with an underscore.
write(".nojekyll", "")

print("\nDone. Assets: %d" % len(asset_map))

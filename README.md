# irinacsapo.co.uk — product design portfolio

Static site, migrated off Webflow. No build step, no dependencies, no subscription.
Every page is plain HTML with its assets committed alongside it, so it can be served
by any static host.

## Deploying to GitHub Pages

1. Create a repo on GitHub (e.g. `irina-csapo-product-portfolio`) — **public**, and
   do not let GitHub add a README, licence or `.gitignore`.
2. Push this folder:

   ```bash
   git remote add origin https://github.com/<your-username>/irina-csapo-product-portfolio.git
   git branch -M main
   git push -u origin main
   ```

3. On GitHub: **Settings → Pages → Build and deployment**. Set *Source* to
   **Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
4. Wait a minute or two, then open
   `https://<your-username>.github.io/irina-csapo-product-portfolio/`.

### Moving irinacsapo.co.uk across later

All internal links are **relative**, so the site works unchanged at a sub-path
(`user.github.io/repo/`), at a domain root, or opened from disk. Switching the
domain over needs no edits to the HTML:

1. Add a file called `CNAME` at the repo root containing one line:
   `www.irinacsapo.co.uk`
2. At your domain registrar, set:
   - `CNAME` record, host `www` → `<your-username>.github.io`
   - Four `A` records for the apex `@` → `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153`
3. **Settings → Pages → Custom domain**, enter `www.irinacsapo.co.uk`, then tick
   **Enforce HTTPS** once the certificate is issued (can take up to 24h).

Keep the Webflow site published until DNS has propagated and the new site is
confirmed working — the two can coexist, and only DNS decides which one answers.

## Layout

```
index.html              home
404.html                served by GitHub Pages for any unknown URL
about/  contact/        top-level pages
case-studies/           9 case studies
product-design/         3 project showcases
photography/            gallery + 3 sub-galleries
portfolio/              7 older project pages (see "Legacy pages" below)
webflow-projects/  ai-applications/
assets/
  css/ js/ fonts/       Webflow's compiled stylesheet, JS bundles, GSAP, jQuery
  images/ media/ docs/  all images, video, and CV PDFs
.nojekyll               stops GitHub Pages hiding files that start with "_"
tools/mirror.py         the script that generated this site from the live Webflow site
```

Editing is plain HTML: find the page, change the markup. The CSS in
`assets/css/` is Webflow's compiled output — it is minified and class names are
Webflow-generated, so prefer adding your own rules over editing it in place.

## Known issues carried over from the Webflow site

These were **already broken on the live Webflow site** and were mirrored as-is
rather than silently changed:

| Issue | Where | Notes |
|---|---|---|
| `/quote` links 404 | footer/CTA on most pages | The "Request a Quote" page is an unpublished draft in Webflow. Repoint these to `/contact` or remove them. |
| `/old-home`, `/old-home-2` links 404 | 404 page, photography pages | Unpublished drafts. |
| `/portfolio/creative-duo` links 404 | `ai-applications` | Unpublished draft. |
| 2 missing icons | `portfolio/spree-app` | `shield-check-1.svg`, `thunder-move-1.svg` are hosted under a *different* Webflow account and now return 403. Replace or delete them. |

## Things that changed in the migration

- **Contact form is inert.** It kept its exact markup and styling, but submission
  is disabled (`onsubmit="return false;"`) and the Cloudflare Turnstile widget was
  removed — both only worked on Webflow's servers. There is a `TODO` comment above
  the form in `contact/index.html` with wiring instructions. A form backend such as
  Formspree needs only an `action` URL and `method="POST"`.
- **Webflow's Google Analytics proxy was removed.** Webflow served GA through an
  obfuscated first-party path that exists only on its own infrastructure, so it
  404'd everywhere else. It carried a Universal Analytics ID (`UA-172745255-1`),
  which Google switched off in July 2023 and which was collecting nothing. Your
  self-hosted Umami analytics is untouched and still works.
- **Legacy pages.** `portfolio/` holds 7 older project pages. They are not part of
  the current portfolio, but each is still linked from a page you kept, so they were
  included to avoid creating broken links. To drop them, delete the `portfolio/`
  directory and remove the links that point into it.

## Still loaded from third parties

These are unchanged and keep working, but they are external dependencies:
Google Fonts, jQuery/GSAP were localised, but the cookie banner
(`flowbase.s3-ap-southeast-2.amazonaws.com`), Umami, Heap and Pendo analytics, and
some images on `dl.dropboxusercontent.com` still load remotely.

## Regenerating

`tools/mirror.py` rebuilds this site from the live Webflow site. It only works
while the Webflow site is still published, so keep a copy of this repo once you
cancel.

```bash
python3 tools/mirror.py <output-directory>
```
